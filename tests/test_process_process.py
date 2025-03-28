import os
import time
import pytest
import tempfile
import pickle
import multiprocessing
from unittest import mock
from datetime import datetime, timedelta

from fbpyutils import process
from fbpyutils import Env
from fbpyutils.file import creation_date # Re-added import
from fbpyutils.string import hash_string

#@mock.patch("fbpyutils.file.creation_date") # Mock creation_date globalmente # Removed global mock decorator
def dummy_process_func(param):
    return True, None, f"processed {param}"


def dummy_file_process_func(file_path):
    # Return signature: file_path, success, message, result
    return file_path, True, None, f"processed {file_path}"


def dummy_session_process_func(param1, param2):
    return (True, None, f"processed {param1}, {param2}", "result_data")


def error_process_func(param):
    raise ValueError("Processing error")


def error_file_process_func(file_path):
    # Return signature: file_path, success, message, result
    return file_path, False, "processing failed", None


def error_file_process_func_remove_control(file_path):
    # Return signature: file_path, success, message, result
    return file_path, False, "processing failed", None


def error_session_process_func(param1, param2):
    return False, "session processing failed", None


def error_session_process_func_remove_control(param1, param2):
    return False, "session processing failed", None


def test_get_available_cpu_count():
    with mock.patch("multiprocessing.cpu_count") as mock_cpu_count:
        mock_cpu_count.return_value = 4
        assert process.Process.get_available_cpu_count() == 4

    with mock.patch("multiprocessing.cpu_count", side_effect=NotImplementedError):
        assert process.Process.get_available_cpu_count() == 1


def test_is_parallelizable(caplog):
    import logging

    # Configure root logger to capture messages
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Set root logger level to DEBUG or INFO
    root_logger.addHandler(logging.StreamHandler())  # Add a basic handler

    import logging

    caplog.set_level(logging.INFO)

    assert process.Process.is_parallelizable(parallel_type="threads") is True
    assert "Default multi-threads parallelization available" in caplog.text

    with mock.patch("fbpyutils.process.Process.is_parallelizable", return_value=False):
        assert process.Process.is_parallelizable(parallel_type="processes") is False

    assert process.Process.is_parallelizable(parallel_type="invalid") is False
    assert "Unknown parallel type: invalid. Assuming not parallelizable." in caplog.text


def test_get_function_info():
    def example_function():
        pass

    info = process.Process.get_function_info(example_function)
    assert info["module"] == "test_process_process"  # Updated to match actual behavior
    assert info["name"].endswith("example_function")
    assert info["full_ref"].endswith("example_function")
    assert "example_function" in info["unique_ref"]


def test_process_init():
    proc = process.Process(process=dummy_process_func)
    assert proc._parallelize is True
    assert proc._parallel_type == "threads"
    assert proc._workers == process.Process._MAX_WORKERS
    assert proc.sleeptime == 0.0

    proc_serial = process.Process(
        process=dummy_process_func,
        parallelize=False,
        sleeptime=1.0,
        workers=2,
        parallel_type="processes",
    )
    assert proc_serial._parallelize is False
    assert proc_serial._parallel_type == "processes"
    assert proc_serial._workers == 2
    assert proc_serial.sleeptime == 1.0

    with pytest.raises(ValueError) as excinfo:
        process.Process(process=dummy_process_func, parallel_type="invalid")
    assert (
        "Invalid parallel processing type: invalid. Valid types are: threads or processes."
        in str(excinfo.value)
    )


def test_process_run_serial(caplog):
    proc = process.Process(process=dummy_process_func, parallelize=False, sleeptime=0.1)
    params = [(1,), (2,), (3,)]
    results = proc.run(params)

    assert len(results) == 3
    assert all(res[0] is True for res in results)
    assert [res[2] for res in results] == ["processed 1", "processed 2", "processed 3"]
    assert "Running in serial mode (parallelization disabled)" in caplog.text


def test_process_run_parallel_threads(caplog):
    proc = process.Process(
        process=dummy_process_func, parallel_type="threads", workers=2
    )
    params = [(1,), (2,), (3,), (4,)]
    results = proc.run(params)

    assert len(results) == 4
    assert all(res[0] is True for res in results)
    assert "Starting parallel execution with 2 workers using threads" in caplog.text
    assert "Processed 4 items successfully" in caplog.text


def test_process_run_parallel_processes(caplog):
    proc = process.Process(
        process=dummy_process_func, parallel_type="processes", workers=2
    )
    params = [(1,), (2,), (3,), (4,)]
    results = proc.run(params)

    assert len(results) == 4
    assert all(res[0] is True for res in results)
    assert "Starting parallel execution with 2 workers using processes" in caplog.text
    assert "Processed 4 items successfully" in caplog.text


def test_process_run_exception(caplog):
    proc = process.Process(process=error_process_func, parallelize=False)
    params = [(1,)]
    with pytest.raises(ValueError) as excinfo:
        proc.run(params)
    assert "Processing error" in str(excinfo.value)
    assert "Error during process execution" in caplog.text


@mock.patch("pickle.dump", wraps=pickle.dump)
@mock.patch("pickle.load", wraps=pickle.load)
@mock.patch(
    "fbpyutils.Env.USER_APP_FOLDER",
    new_callable=mock.PropertyMock,
)
def test_process_files_controlled_run(
    mock_env_mm_user_app_folder,
    mock_pickle_load,
    mock_pickle_dump,
    caplog,
    tmpdir,
):
    # Configure the USER_APP_FOLDER to use tmpdir
    mock_env_mm_user_app_folder.return_value = str(tmpdir)

    # Create a test file in the temporary directory
    test_file = tmpdir.join("test_file.txt")
    test_file.write("test content")
    file_path_str = str(test_file)

    # Ensure the file exists for the test
    assert os.path.exists(file_path_str), f"Test file {file_path_str} does not exist"

    # Get function info for our test function
    function_info = process.Process.get_function_info(dummy_file_process_func)

    # Calculate control folder and file paths - use os.path.join for platform independence
    control_folder = os.path.join(
        str(tmpdir), f"p_{hash_string(function_info['full_ref'])}.control"
    )
    control_file = os.path.join(control_folder, f"f_{hash_string(file_path_str)}.reg")

    # First run - control file does not exist
    # Set timestamp for unmodified file
    initial_timestamp = datetime.now()

    # Run the process
    result = process.ProcessFiles(process=dummy_file_process_func)._controlled_run(
        dummy_file_process_func, file_path_str
    )

    # Verify the result
    assert result[0] == file_path_str
    assert result[1] is True
    assert result[2] is None
    assert "Creating control folder" in caplog.text

    # Verify the control file was created
    assert os.path.exists(control_folder)
    assert os.path.exists(control_file)

    # Verify the timestamp was stored correctly
    with open(control_file, "rb") as cf:
        last_timestamp = pickle.load(cf)
    print(f"last_timestamp: {last_timestamp}, initial_timestamp: {initial_timestamp.timestamp()}") # Adicionado log
    assert round(abs(last_timestamp - initial_timestamp.timestamp()), 2) == 0

    # Second run - file not modified (same timestamp)
    caplog.clear()

    # Run the process
    result = process.ProcessFiles(process=dummy_file_process_func)._controlled_run(
        dummy_file_process_func, file_path_str
    )

    # Verify skipping due to unchanged timestamp
    assert result[0] == file_path_str
    assert result[1] is True
    assert result[2] == "Skipped"
    assert "Skipping unmodified file" in caplog.text

    # Third run - file modified (newer timestamp)
    caplog.clear()

    # Set newer timestamp to simulate file modification
    # Opens the file and write some text to force it updates

    print("Waiting a bit to force file update..")
    time.sleep(5)
    test_file.write("new content")
    modified_timestamp = datetime.now()

    # Run the process
    result = process.ProcessFiles(process=dummy_file_process_func)._controlled_run(
        dummy_file_process_func, file_path_str
    )

    # Verify processing occurred
    assert result[0] == file_path_str
    assert result[1] is True
    assert result[2] is None
    assert "Processing file" in caplog.text

    # Verify timestamp was updated
    with open(control_file, "rb") as cf:
        updated_timestamp = pickle.load(cf)
    assert round(abs(updated_timestamp - modified_timestamp.timestamp()), 2) == 0

    caplog.clear()

    # Fourth run - processing error
    result = process.ProcessFiles(process=error_file_process_func)._controlled_run(
        error_file_process_func, file_path_str
    )
    assert result[0] == file_path_str
    assert result[1] is False
    assert result[2] == "processing failed"

    caplog.clear()

    # Fifth run - processing error and control file created but should be removed
    result = process.ProcessFiles(
        process=error_file_process_func_remove_control
    )._controlled_run(error_file_process_func_remove_control, file_path_str)
    assert result[0] == file_path_str
    assert result[1] is False
    assert result[2] == "processing failed"

    caplog.clear()

    # Sixth run - ValueError in _controlled_run
    with pytest.raises(ValueError) as excinfo:
        process.ProcessFiles(process=dummy_file_process_func)._controlled_run(
            dummy_file_process_func
        )  # missing file_path
    assert "Not enough arguments to run" in str(excinfo.value)

    caplog.clear()
    # Seventh run - FileNotFoundError in _controlled_run
    with pytest.raises(FileNotFoundError) as excinfo:
        process.ProcessFiles(process=dummy_file_process_func)._controlled_run(
            dummy_file_process_func, "non_existent_file.txt"
        )  # non existent file
    assert "Process file non_existent_file.txt does not exist" in str(excinfo.value)


def test_process_files_init():
    proc_files = process.ProcessFiles(process=dummy_file_process_func)
    assert proc_files._parallelize is True
    assert proc_files._workers == process.Process._MAX_WORKERS
    assert proc_files.sleeptime == 0.0

    proc_files_serial = process.ProcessFiles(
        process=dummy_file_process_func, parallelize=False, sleeptime=1.0, workers=2
    )
    assert proc_files_serial._parallelize is False
    assert proc_files_serial._workers == 2
    assert proc_files_serial.sleeptime == 1.0


def test_process_files_run(caplog, tmpdir):
    # Patch Env.USER_APP_FOLDER to use tmpdir
    with mock.patch(
        "fbpyutils.Env.USER_APP_FOLDER",
        new_callable=mock.PropertyMock,
        return_value=str(tmpdir),
    ):
        # Create a concrete instance
        proc_files = process.ProcessFiles(process=dummy_file_process_func)

        # Create test files
        test_file1 = tmpdir.join("file1.txt")
        test_file1.write("test content 1")
        test_file2 = tmpdir.join("file2.txt")
        test_file2.write("test content 2")

        file_paths = [str(test_file1), str(test_file2)]
        params = [(path,) for path in file_paths]

        with mock.patch.object(process.Process, "run") as mock_super_run:
            # Test with normal execution (controlled=False)

            # Configure mock to return expected results
            mock_super_run.return_value = [
                (path, True, None, f"result for {path}") for path in file_paths
            ]

            # Run with controlled=False
            results = proc_files.run(params, controlled=False)

            # Verify results
            mock_super_run.assert_called_once()
            assert "Starting normal execution" in caplog.text
            assert len(results) == 2

            caplog.clear()
            mock_super_run.reset_mock()


            # Test normal run
            proc_files.run(params, controlled=False)
            mock_super_run.assert_called()
            assert "Starting normal execution" in caplog.text

            caplog.clear()
            mock_super_run.reset_mock()

            # Test exception in run
            mock_super_run.side_effect = ValueError("Run error")
            with pytest.raises(ValueError) as excinfo:
                proc_files.run(params, controlled=False)
            assert "Run error" in str(excinfo.value)
            assert "Error in process execution" in caplog.text


def test_session_process_generate_session_id():
    session_id = process.SessionProcess.generate_session_id()
    assert session_id.startswith("session_")
    assert len(session_id) > len("session_")


def test_session_process_generate_task_id():
    params = (1, "test", True)
    task_id = process.SessionProcess.generate_task_id(params)
    assert task_id.startswith("task_")
    assert len(task_id) > len("task_")


@mock.patch("pickle.dump", wraps=pickle.dump)
@mock.patch("pickle.load", wraps=pickle.load)
@mock.patch(
    "fbpyutils.Env.USER_APP_FOLDER",
    new_callable=mock.PropertyMock,
)
def test_session_process_controlled_run_session(
    mock_env_mm_user_app_folder,
    mock_pickle_load,
    mock_pickle_dump,
    caplog,
    tmpdir,
):
    # Configure USER_APP_FOLDER to use tmpdir
    mock_env_mm_user_app_folder.return_value = str(tmpdir)

    session_id = "test_session_id"
    params = (1, 2)
    task_id = process.SessionProcess.generate_task_id(params)

    # Calculate session control folder and file paths
    session_control_folder = os.path.join(
        str(tmpdir), "session_control", f"s_{hash_string(session_id)}"
    )
    task_control_file = os.path.join(
        session_control_folder, f"t_{hash_string(task_id)}.reg"
    )

    # First run - task control file does not exist
    result = process.SessionProcess(process=dummy_session_process_func)._controlled_run(
        session_id, dummy_session_process_func, *params
    )

    # Verify results
    assert result[0] == task_id
    assert result[1] is True
    assert result[2] is None
    assert "Creating session control folder" in caplog.text

    # Verify control files were created
    assert os.path.exists(session_control_folder)
    assert os.path.exists(task_control_file)

    # Second run - task already processed (file exists)
    caplog.clear()

    result = process.SessionProcess(process=dummy_session_process_func)._controlled_run(
        session_id, dummy_session_process_func, *params
    )

    assert result[0] == task_id
    assert result[1] is True
    assert result[2] == "Skipped"
    assert "Skipping already processed task" in caplog.text

    # Third run - with a different task/params
    caplog.clear()
    new_params = (3, 4)
    new_task_id = process.SessionProcess.generate_task_id(new_params)
    new_task_control_file = os.path.join(
        session_control_folder, f"t_{hash_string(new_task_id)}.reg"
    )

    # Should process this one since it's a new task
    result = process.SessionProcess(process=dummy_session_process_func)._controlled_run(
        session_id, dummy_session_process_func, *new_params
    )

    assert result[0] == new_task_id
    assert result[1] is True
    assert result[2] is None
    assert "Processing task" in caplog.text
    assert os.path.exists(new_task_control_file)

    # Fourth run - processing error scenario
    caplog.clear()
    error_params = (5, 6)
    error_task_id = process.SessionProcess.generate_task_id(error_params)

    result = process.SessionProcess(process=error_session_process_func)._controlled_run(
        session_id, error_session_process_func, *error_params
    )

    assert result[0] == error_task_id
    assert result[1] is False
    assert result[2] == "session processing failed"

    # Fifth run - testing ValueError with missing arguments
    caplog.clear()

    with pytest.raises(ValueError) as excinfo:
        process.SessionProcess(process=dummy_session_process_func)._controlled_run(
            session_id,
            dummy_session_process_func,
        )  # missing params
    assert "Not enough arguments to run session controlled process" in str(
        excinfo.value
    )


def test_session_process_init():
    proc_session = process.SessionProcess(process=dummy_session_process_func)
    assert proc_session._parallelize is True
    assert proc_session._parallel_type == "threads"
    assert proc_session._workers == process.Process._MAX_WORKERS
    assert proc_session.sleeptime == 0.0

    proc_session_serial = process.SessionProcess(
        process=dummy_session_process_func,
        parallelize=False,
        sleeptime=1.0,
        workers=2,
        parallel_type="processes",
    )
    assert proc_session_serial._parallelize is False
    assert proc_session_serial._parallel_type == "processes"
    assert proc_session_serial._workers == 2
    assert proc_session_serial.sleeptime == 1.0


def test_session_process_run(caplog, tmpdir):
    # Create instance and setup test environment
    with mock.patch(
        "fbpyutils.Env.USER_APP_FOLDER",
        new_callable=mock.PropertyMock,
        return_value=str(tmpdir),
    ):
        # Create a concrete instance
        proc_session = process.SessionProcess(process=dummy_session_process_func)

        # Test with mock_super_run and spy on _controlled_run
        with mock.patch.object(process.Process, "run") as mock_super_run:
            # Setup
            params = [(1,), (2,)]
            session_id = "test_session"

            # Create control folder to prevent file operation errors
            session_control_folder = os.path.join(
                str(tmpdir), "session_control", f"s_{hash_string(session_id)}"
            )
            os.makedirs(session_control_folder, exist_ok=True)

            # 1. Test controlled run with session_id
            # Using return_value instead of side_effect for simpler mocking
            proc_session.run(params, session_id=session_id, controlled=True)
            mock_super_run.assert_called()
            assert "Starting session controlled execution" in caplog.text

            # Reset for next test
            caplog.clear()
            mock_super_run.reset_mock()

            # 2. Test controlled run without session_id (auto-generated)
            mock_super_run.reset_mock()
            caplog.clear()

            proc_session.run(params, controlled=True)
            mock_super_run.assert_called()
            assert "Starting session controlled execution" in caplog.text
            assert "Session ID: session_" in caplog.text

            # Reset for next test
            caplog.clear()
            mock_super_run.reset_mock()

            # 3. Test normal run
            mock_super_run.reset_mock()
            caplog.clear()

            proc_session.run(params, controlled=False)
            mock_super_run.assert_called()
            assert "Starting normal execution" in caplog.text

            # Reset for next test
            caplog.clear()
            mock_super_run.reset_mock()

            # 4. Test exception in run
            mock_super_run.side_effect = ValueError("Run error")
            with pytest.raises(ValueError) as excinfo:
                proc_session.run(params, controlled=False)
            assert "Run error" in str(excinfo.value)
            assert "Error in session process execution" in caplog.text
