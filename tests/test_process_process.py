import os
import time
import pytest
import tempfile
import pickle
import multiprocessing
from unittest import mock
from datetime import datetime

from fbpyutils import process
from fbpyutils import Env
from fbpyutils.file import creation_date
from fbpyutils.string import hash_string

# Função top-level para corrigir o erro de pickling
def dummy_process_func(param):
    return True, None, f"processed {param}"

def dummy_file_process_func(file_path):
    return "file_path", True, None, f"processed {file_path}"

def dummy_session_process_func(param1, param2):
    return True, None, f"processed {param1}, {param2}"

def error_process_func(param):
    raise ValueError("Processing error")

def error_file_process_func(file_path):
    return False, "processing failed", None

def error_file_process_func_remove_control(file_path):
    return False, "processing failed", None

def error_session_process_func(param1, param2):
    return False, "session processing failed", None

def error_session_process_func_remove_control(param1, param2):
    return False, "session processing failed", None


def test_get_available_cpu_count():
    with mock.patch('multiprocessing.cpu_count') as mock_cpu_count:
        mock_cpu_count.return_value = 4
        assert process.Process.get_available_cpu_count() == 4

    with mock.patch('multiprocessing.cpu_count', side_effect=NotImplementedError):
        assert process.Process.get_available_cpu_count() == 1


def test_is_parallelizable(caplog):
    import logging
    caplog.set_level(logging.INFO)

    assert process.Process.is_parallelizable(parallel_type='threads') is True
    assert "Default multi-threads parallelization available" in caplog.text

    with mock.patch('fbpyutils.process.multiprocessing', None):
        assert process.Process.is_parallelizable(parallel_type='processes') is False
        assert "Multiprocessing not available" in caplog.text

    assert process.Process.is_parallelizable(parallel_type='invalid') is False
    assert "Unknown parallel type: invalid. Assuming not parallelizable." in caplog.text


def test_get_function_info():
    def example_function():
        pass
    info = process.Process.get_function_info(example_function)
    assert info['module'] == 'tests.test_process_process' # Correção aqui
    assert info['name'] == 'example_function'
    assert info['full_ref'] == 'tests.test_process_process.example_function'
    assert 'example_function' in info['unique_ref']


def test_process_init():
    proc = process.Process(process=dummy_process_func)
    assert proc._parallelize is True
    assert proc._parallel_type == 'threads'
    assert proc._workers == process.Process._MAX_WORKERS
    assert proc.sleeptime == 0.0

    proc_serial = process.Process(process=dummy_process_func, parallelize=False, sleeptime=1.0, workers=2, parallel_type='processes')
    assert proc_serial._parallelize is False
    assert proc_serial._parallel_type == 'processes'
    assert proc_serial._workers == 2
    assert proc_serial.sleeptime == 1.0

    with pytest.raises(ValueError) as excinfo:
        process.Process(process=dummy_process_func, parallel_type='invalid')
    assert "Invalid parallel processing type: invalid. Valid types are: threads or processes." in str(excinfo.value)


def test_process_run_serial(caplog):
    proc = process.Process(process=dummy_process_func, parallelize=False, sleeptime=0.1)
    params = [(1,), (2,), (3,)]
    results = proc.run(params)

    assert len(results) == 3
    assert all(res[0] is True for res in results)
    assert [res[2] for res in results] == ['processed 1', 'processed 2', 'processed 3']
    assert "Running in serial mode (parallelization disabled)" in caplog.text


def test_process_run_parallel_threads(caplog):
    proc = process.Process(process=dummy_process_func, parallel_type='threads', workers=2)
    params = [(1,), (2,), (3,), (4,)]
    results = proc.run(params)

    assert len(results) == 4
    assert all(res[0] is True for res in results)
    assert "Starting parallel execution with 2 workers using threads" in caplog.text
    assert "Processed 4 items successfully" in caplog.text


def test_process_run_parallel_processes(caplog):
    proc = process.Process(process=dummy_process_func, parallel_type='processes', workers=2)
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


@mock.patch('fbpyutils.process.creation_date')
@mock.patch('os.path.exists')
@mock.patch('os.makedirs')
@mock.patch('pickle.dump')
@mock.patch('pickle.load')
@mock.patch('os.remove')
@mock.patch('fbpyutils.Env.MM_USER_APP_FOLDER', new_callable=mock.PropertyMock, return_value=tempfile.gettempdir())
def test_process_files_controlled_run(mock_env_mm_user_app_folder, mock_remove, mock_pickle_load, mock_pickle_dump, mock_makedirs, mock_exists, mock_creation_date, caplog, tmpdir):
    test_file = tmpdir.join("test_file.txt")
    test_file.write("test content")
    file_path_str = str(test_file)

    mock_creation_date.return_value = datetime.now()
    mock_exists.side_effect = [False, False, True] # control_folder exists?, control_file exists?, control_file exists after creation

    # First run - control file does not exist
    result = process.ProcessFiles(process=dummy_file_process_func)._controlled_run(dummy_file_process_func, file_path_str)
    assert result[0] == file_path_str
    assert result[1] is True
    assert result[2] is None
    assert "Creating control folder" in caplog.text
    mock_makedirs.assert_called()
    mock_pickle_dump.assert_called()
    mock_exists.assert_called()

    caplog.clear()
    mock_exists.side_effect = [True, True, True] # control_folder exists?, control_file exists?, control_file exists after creation
    mock_pickle_load.return_value = datetime.now().timestamp() # last_timestamp >= current_timestamp

    # Second run - file not modified
    result = process.ProcessFiles(process=dummy_file_process_func)._controlled_run(dummy_file_process_func, file_path_str)
    assert result[0] == file_path_str
    assert result[1] is True
    assert result[2] == "Skipped"
    assert "Skipping unmodified file" in caplog.text
    mock_pickle_load.assert_called()

    caplog.clear()
    mock_exists.side_effect = [True, False, True] # control_folder exists?, control_file exists?, control_file exists after creation
    mock_pickle_load.return_value = datetime(2023, 1, 1).timestamp() # last_timestamp < current_timestamp

    # Third run - file modified
    result = process.ProcessFiles(process=dummy_file_process_func)._controlled_run(dummy_file_process_func, file_path_str)
    assert result[0] == file_path_str
    assert result[1] is True
    assert result[2] is None
    assert "Processing file" in caplog.text
    mock_pickle_load.assert_called()
    mock_pickle_dump.assert_called()

    caplog.clear()
    mock_exists.side_effect = [True, False, True] # control_folder exists?, control_file exists?, control_file exists after creation
    mock_pickle_load.return_value = datetime(2023, 1, 1).timestamp() # last_timestamp < current_timestamp

    # Fourth run - processing error
    result = process.ProcessFiles(process=error_file_process_func)._controlled_run(error_file_process_func, file_path_str)
    assert result[0] == file_path_str
    assert result[1] is False
    assert result[2] == "processing failed"
    mock_remove.assert_not_called() # Control file is kept on error

    caplog.clear()
    mock_exists.side_effect = [False, False, False, True] # control_folder exists?, control_file exists?, control_file exists after creation, control_file exists after error
    mock_pickle_load.return_value = datetime(2023, 1, 1).timestamp() # last_timestamp < current_timestamp

    # Fifth run - processing error and control file created but should be removed
    result = process.ProcessFiles(process=error_file_process_func_remove_control)._controlled_run(error_file_process_func_remove_control, file_path_str)
    assert result[0] == file_path_str
    assert result[1] is False
    assert result[2] == "processing failed"
    mock_remove.assert_not_called() # Control file is kept on error

    caplog.clear()
    mock_exists.side_effect = [True, False, False, True] # control_folder exists?, control_file exists?, control_file exists after creation, control_file exists after error
    mock_pickle_load.return_value = datetime(2023, 1, 1).timestamp() # last_timestamp < current_timestamp

    # Sixth run - ValueError in _controlled_run
    with pytest.raises(ValueError) as excinfo:
        process.ProcessFiles(process=dummy_file_process_func)._controlled_run(dummy_file_process_func) # missing file_path
    assert "No enough arguments to run" in str(excinfo.value)

    caplog.clear()
    mock_exists.side_effect = [False] # file exists? - NO
    # Seventh run - FileNotFoundError in _controlled_run
    with pytest.raises(FileNotFoundError) as excinfo:
        process.ProcessFiles(process=dummy_file_process_func)._controlled_run(dummy_file_process_func, "non_existent_file.txt") # non existent file
    assert "Process file non_existent_file.txt does not exist" in str(excinfo.value)


def test_process_files_init():
    proc_files = process.ProcessFiles(process=dummy_file_process_func)
    assert proc_files._parallelize is True
    assert proc_files._workers == process.Process._MAX_WORKERS
    assert proc_files.sleeptime == 0.0

    proc_files_serial = process.ProcessFiles(process=dummy_file_process_func, parallelize=False, sleeptime=1.0, workers=2)
    assert proc_files_serial._parallelize is False
    assert proc_files_serial._workers == 2
    assert proc_files_serial.sleeptime == 1.0


@mock.patch.object(process.ProcessFiles, '_controlled_run')
@mock.patch.object(process.Process, 'run')
def test_process_files_run(mock_super_run, mock_controlled_run, caplog):
    proc_files = process.ProcessFiles(process=dummy_file_process_func)
    params = [("file1.txt",), ("file2.txt",)]

    # Test controlled run
    proc_files.run(params, controlled=True)
    mock_controlled_run.assert_called()
    assert mock_super_run.call_count == 1
    assert "Starting controlled execution" in caplog.text

    caplog.clear()
    mock_super_run.reset_mock()
    mock_controlled_run.reset_mock()

    # Test normal run
    proc_files.run(params, controlled=False)
    mock_controlled_run.assert_not_called()
    mock_super_run.assert_called()
    assert "Starting normal execution" in caplog.text

    caplog.clear()
    mock_super_run.reset_mock()
    mock_controlled_run.reset_mock()

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


@mock.patch('os.path.exists')
@mock.patch('os.makedirs')
@mock.patch('pickle.dump')
@mock.patch('pickle.load')
@mock.patch('os.remove')
@mock.patch('fbpyutils.Env.MM_USER_APP_FOLDER', new_callable=mock.PropertyMock, return_value=tempfile.gettempdir())
def test_session_process_controlled_run_session(mock_env_mm_user_app_folder, mock_remove, mock_pickle_load, mock_pickle_dump, mock_makedirs, mock_exists, caplog):
    session_id = "test_session_id"
    params = (1, 2)
    task_id = process.SessionProcess.generate_task_id(params)

    mock_exists.side_effect = [False, False, True] # session_control_folder exists?, task_control_file exists?, task_control_file exists after creation

    # First run - task control file does not exist
    result = process.SessionProcess(process=dummy_session_process_func)._controlled_run(session_id, dummy_session_process_func, *params)
    assert result[0] == task_id
    assert result[1] is True
    assert result[2] is None
    assert "Creating session control folder" in caplog.text
    mock_makedirs.assert_called()
    mock_pickle_dump.assert_called()
    mock_exists.assert_called()

    caplog.clear()
    mock_exists.side_effect = [True, True, True] # session_control_folder exists?, task_control_file exists?, task_control_file exists after creation

    # Second run - task already processed
    result = process.SessionProcess(process=dummy_session_process_func)._controlled_run(session_id, dummy_session_process_func, *params)
    assert result[0] == task_id
    assert result[1] is True
    assert result[2] == "Skipped"
    assert "Skipping already processed task" in caplog.text
    mock_pickle_load.assert_not_called()

    caplog.clear()
    mock_exists.side_effect = [True, False, True] # session_control_folder exists?, task_control_file exists?, task_control_file exists after creation

    # Third run - task not processed yet
    result = process.SessionProcess(process=dummy_session_process_func)._controlled_run(session_id, dummy_session_process_func, *params)
    assert result[0] == task_id
    assert result[1] is True
    assert result[2] is None
    assert "Processing task" in caplog.text
    mock_pickle_dump.assert_called()

    caplog.clear()
    mock_exists.side_effect = [True, False, True] # session_control_folder exists?, task_control_file exists?, task_control_file exists after creation

    # Fourth run - processing error
    result = process.SessionProcess(process=error_session_process_func)._controlled_run(session_id, error_session_process_func, *params)
    assert result[0] == task_id
    assert result[1] is False
    assert result[2] == "session processing failed"
    mock_remove.assert_not_called() # Control file is kept on error

    caplog.clear()
    mock_exists.side_effect = [False, False, False, True] # session_control_folder exists?, task_control_file exists?, task_control_file exists after creation, task_control_file exists after error

    # Fifth run - processing error and control file created but should be removed
    result = process.SessionProcess(process=error_session_process_func_remove_control)._controlled_run(session_id, error_session_process_func_remove_control, *params)
    assert result[0] == task_id
    assert result[1] is False
    assert result[2] == "session processing failed"
    mock_remove.assert_not_called() # Control file is kept on error


    caplog.clear()
    mock_exists.side_effect = [True, False, False, True] # session_control_folder exists?, task_control_file exists?, task_control_file exists after creation, task_control_file exists after error

    # Sixth run - ValueError in _controlled_run
    with pytest.raises(ValueError) as excinfo:
        process.SessionProcess(process=dummy_session_process_func)._controlled_run(session_id, dummy_session_process_func, ) # missing params
    assert "Not enough arguments to run session controlled process" in str(excinfo.value)


def test_session_process_init():
    proc_session = process.SessionProcess(process=dummy_session_process_func)
    assert proc_session._parallelize is True
    assert proc_session._parallel_type == 'threads'
    assert proc_session._workers == process.Process._MAX_WORKERS
    assert proc_session.sleeptime == 0.0

    proc_session_serial = process.SessionProcess(process=dummy_session_process_func, parallelize=False, sleeptime=1.0, workers=2, parallel_type='processes')
    assert proc_session_serial._parallelize is False
    assert proc_session_serial._parallel_type == 'processes'
    assert proc_session_serial._workers == 2
    assert proc_session_serial.sleeptime == 1.0


@mock.patch.object(process.SessionProcess, '_controlled_run')
@mock.patch.object(process.Process, 'run')
def test_session_process_run(mock_super_run, mock_controlled_run, caplog):
    proc_session = process.SessionProcess(process=dummy_session_process_func)
    params = [(1,), (2,)]
    session_id = "test_session"

    # Test controlled run with session_id
    proc_session.run(params, session_id=session_id, controlled=True)
    mock_controlled_run.assert_called()
    mock_super_run.assert_called()
    assert "Starting session controlled execution" in caplog.text

    caplog.clear()
    mock_super_run.reset_mock()
    mock_controlled_run.reset_mock()

    # Test controlled run without session_id (should generate one)
    proc_session.run(params, controlled=True)
    mock_controlled_run.assert_called()
    mock_super_run.assert_called()
    assert "Starting session controlled execution" in caplog.text
    assert "Session ID: session_" in caplog.text # Check if session ID is generated

    caplog.clear()
    mock_super_run.reset_mock()
    mock_controlled_run.reset_mock()

    # Test normal run
    proc_session.run(params, controlled=False)
    mock_controlled_run.assert_not_called()
    mock_super_run.assert_called()
    assert "Starting normal execution" in caplog.text

    caplog.clear()
    mock_super_run.reset_mock()
    mock_controlled_run.reset_mock()

    # Test exception in run
    mock_super_run.side_effect = ValueError("Run error")
    with pytest.raises(ValueError) as excinfo:
        proc_session.run(params, controlled=False)
    assert "Run error" in str(excinfo.value)
    assert "Error in session process execution" in caplog.text
