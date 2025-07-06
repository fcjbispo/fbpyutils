"""
Module for parallel or serial process execution with control mechanisms.

This module provides classes to execute processing functions, supporting both
parallel and serial execution modes. It includes control mechanisms such as
timestamp-based control for file processing and session-based control for
resumable processes.

Classes:
    Process: Base class for executing functions in parallel or serial.
    FileProcess: Extends Process to add timestamp-based control for file processing,
                  preventing reprocessing of unmodified files.
    SessionProcess: Extends Process to provide session-based control, allowing
                    resumption of processing sessions after interruptions or failures.
"""

import os
import time
import pickle
import inspect
import multiprocessing
import uuid
import concurrent.futures

from typing import Any, Callable, List, Tuple, Dict, Optional, TypeVar, Protocol, Union
from datetime import datetime

from fbpyutils.env import Env # Import Env from its new module
from fbpyutils.logging import Logger
from fbpyutils.string import hash_string



# Type variable for generic processing function
T = TypeVar('T')

class ProcessingFunction(Protocol):
    """
    Defines the protocol for a generic processing function.

    A processing function should accept a tuple of parameters and return a tuple
    containing a boolean indicating success, an optional error message (string),
    and a result of any type.
    """
    def __call__(self, params: Tuple[Any, ...]) -> Tuple[bool, Optional[str], Any]:
        """
        Executes the processing function.

        Args:
            params (Tuple[Any, ...]): A tuple containing the parameters for the processing function.

        Returns:
            Tuple[bool, Optional[str], Any]: A tuple containing the success status (bool),
                                             an optional error message (str or None), and
                                             the processing result (Any).
        """
        ...

class ProcessingFilesFunction(Protocol):
    """
    Defines the protocol for a file processing function.

    A file processing function should accept a tuple of parameters, process a file,
    and return a tuple containing the file path (string), a boolean indicating success,
    an optional error message (string), and a result of any type.
    """
    def __call__(self, params: Tuple[Any, ...]) -> Tuple[str, bool, Optional[str], Any]:
        """
        Executes the file processing function.

        Args:
            params (Tuple[Any, ...]): A tuple containing the parameters for the file processing function.

        Returns:
            Tuple[str, bool, Optional[str], Any]: A tuple containing the processed file path (str),
                                             the success status (bool), an optional error message (str or None),
                                             and the processing result (Any).
        """
        ...


class Process:
    """
    Base class for parallel or serial function processing.
    
    This class provides the basic infrastructure to execute a processing function
    with a list of parameter sets. It supports both parallel execution using
    multiple threads or processes and serial execution in a single thread.
    
    It is designed to be subclassed for specific processing needs, offering
    flexibility in how functions are executed and managed.
    
    Attributes:
        _MAX_WORKERS: int
        _process: Callable
        _parallelize: bool
        _workers: int
        sleeptime: float
        _parallel_type: str
    """

    _MAX_WORKERS: int
    _process: Callable
    _parallelize: bool
    _workers: int
    sleeptime: float
    _parallel_type: str

    @staticmethod
    def _process_wrapper(func_and_params):
        func, params = func_and_params
        return func(*params)

    _MAX_WORKERS = os.cpu_count() if os.name == 'nt' else 1

    @staticmethod
    def get_available_cpu_count() -> int:
        """
        Determines the number of available CPU cores for processing.

        This static method attempts to retrieve the CPU core count using
        `multiprocessing.cpu_count()`. If this is not supported (e.g., in some minimal
        environments), it logs a warning and defaults to returning 1, ensuring
        the application can still run, albeit without parallel processing.

        Returns:
            int: The number of available CPU cores. Returns 1 if the count cannot be determined.

        Note:
            - On Windows, this method returns the number of logical processors.
            - On other operating systems, it typically returns the number of physical cores,
              but behavior may vary depending on the system configuration and Python build.
        """
        try:
            cpu_count = multiprocessing.cpu_count()
            Logger.debug(f"Detected CPU count: {cpu_count}")
            return cpu_count
        except NotImplementedError:
            Logger.info("CPU count not supported, falling back to single worker")
            return 1

    @staticmethod
    def is_parallelizable(parallel_type: str = 'threads') -> bool:
        """
        Checks if the current system supports the specified parallel processing type.

        This method determines if parallel processing of the specified type is
        available and safe to use on the current system. Includes special handling
        for Windows systems where true multiprocessing may not be available.

        Args:
            parallel_type (str): Type of parallelization to check ('threads' or 'processes').
                                 Defaults to 'threads'.

        Returns:
            bool: True if parallel processing is supported for the specified type, False otherwise.

        Raises:
            ValueError: If an invalid parallel_type is provided.
        """
        if parallel_type == 'processes':
            try:
                import multiprocessing  # Import here to avoid global namespace pollution
                Logger.info("Multiprocessing parallelization available")
                return True
            except ImportError:
                Logger.error(f"Multiprocessing not available: {__file__}:{inspect.currentframe().f_lineno}")
                return False
        elif parallel_type == 'threads':
            Logger.info("Default multi-threads parallelization available")
            return True
        else:
            Logger.warning(f"Unknown parallel type: {parallel_type}. Assuming not parallelizable.")
            return False

    @staticmethod
    def get_function_info(func: Callable) -> Dict[str, str]:
        """
        Gets detailed information about a function.

        This function extracts various identifiers and metadata about the provided function,
        including its module path, qualified name, memory address, and full reference.

        Args:
            func (Callable): The function to analyze.

        Returns:
            Dict[str, str]: Dictionary containing:
                - 'id': Memory address of the function
                - 'module': Module path where the function is defined
                - 'name': Qualified name of the function
                - 'full_ref': Full reference combining module and name
                - 'unique_ref': Absolute unique reference including memory address

        Example:
            >>> def my_func(): pass
            >>> info = Process.get_function_info(my_func)
            >>> print(info['full_ref'])
            'mymodule.my_func'

        Note:
            The 'unique_ref' can be used to distinguish between different instances
            of the same function in memory.
        """
        return {
            'id': str(id(func)),
            'module': func.__module__,
            'name': func.__qualname__,
            'full_ref': f"{func.__module__}.{func.__qualname__}",
            'unique_ref': f"{func.__module__}.{func.__qualname__}_{id(func)}"
        }

    def __init__(self, process: Callable[..., ProcessingFunction], parallelize: bool = True,
                 workers: Optional[int] = _MAX_WORKERS, sleeptime: float = 0,
                 parallel_type: str = 'threads') -> None:
        """
        Initializes a new Process instance.

        Args:
            process (Callable): The processing function to be executed.
                                 It must conform to the ProcessingFunction protocol.
            parallelize (bool): If True, runs processing in parallel using threads or processes.
                                 If False, runs processing serially in the main thread. Defaults to True.
            workers (Optional[int]): The number of worker processes or threads to use for parallel execution.
                                     If None, it defaults to the number of CPU cores available (Process._MAX_WORKERS).
            sleeptime (float): Wait time in seconds between successive executions in serial mode.
                               Useful for throttling processing to reduce system load. Defaults to 0.
            parallel_type (str): Type of parallelization to use, either 'threads' or 'processes'.
                                 Defaults to 'threads'. 'threads' uses ThreadPoolExecutor, 'processes' uses ProcessPoolExecutor.

        Raises:
            ValueError: If an invalid parallel_type is provided.
        """
        parallel_type = parallel_type or 'threads'
        if parallel_type not in ('threads', 'processes'): # Corrected typo 'process' to 'processes'
            raise ValueError(f'Invalid parallel processing type: {parallel_type}. Valid types are: threads or processes.')
        self._process: Callable = process
        self._parallel_type: str = parallel_type
        Logger.debug(f"Initializing Process with parallelize={parallelize}, workers={workers}, sleeptime={sleeptime}, parallel_type={parallel_type}")
        if parallel_type not in ('threads', 'processes'): # Corrected typo 'process' to 'processes'
            Logger.error(f"Invalid parallel processing type: {parallel_type}. Valid types are: threads or processes.")
            raise ValueError(f'Invalid parallel processing type: {parallel_type}. Valid types are: threads or processes.')
        self._process: Callable = process
        self._parallel_type: str = parallel_type
        self._parallelize: bool = parallelize and Process.is_parallelizable(parallel_type=self._parallel_type)
        self._workers: int = workers or Process._MAX_WORKERS # Ensured _workers is always int
        self.sleeptime: float = 0 if sleeptime < 0 else sleeptime
        Logger.info(f"Process initialized: parallel={self._parallelize}, type={self._parallel_type}, workers={self._workers}")

    def run(self, params: List[Tuple[Any, ...]]) -> List[Tuple[bool, Optional[str], Any]]:
        """
        Executes the processing function for each parameter set in the given list.

        Processes can be executed in parallel or serial mode based on the class configuration.

        Args:
            params (List[Tuple[Any, ...]]): List of parameter tuples. Each tuple contains the arguments
                                             to be passed to the processing function.

        Returns:
            List[Tuple[bool, Optional[str], Any]]: List of processing results. Each tuple in the list
                                             corresponds to a parameter set and contains:
                - success (bool): True if processing was successful, False otherwise.
                - error_message (Optional[str]): An error message if processing failed, None otherwise.
                - result (Any): The result of the processing function if successful, None otherwise.

        Raises:
            Exception: Any exception raised during the execution of the processing function.

        Note:
            When running in parallel mode, the order of results may not match the order of input parameters
            due to the nature of concurrent execution.
        """
        Logger.info(f"Starting execution with {len(params)} parameter sets.")
        responses: List[Tuple[bool, Optional[str], Any]] = []
        if not self._parallelize:
            Logger.info("Running in serial mode (parallelization disabled)")
            for i, param in enumerate(params):
                Logger.debug(f"Processing item {i+1}/{len(params)} in serial mode.")
                try:
                    responses.append(self._process(*param))
                except Exception as e:
                    Logger.error(f"Error processing item {i+1} in serial mode: {e}")
                    responses.append((False, str(e), None)) # Ensure consistent return format
                if self.sleeptime > 0:
                    time.sleep(self.sleeptime)
            Logger.info("Finished serial execution.")
            return responses

        max_workers = self._workers or Process.get_available_cpu_count()
        if (max_workers < 1 or max_workers > Process.get_available_cpu_count()):
            Logger.warning(f"Requested workers ({max_workers}) out of bounds. Adjusting to available CPU count: {Process.get_available_cpu_count()}")
            max_workers = Process.get_available_cpu_count()

        Logger.info(f"Starting parallel execution with {max_workers} workers using {self._parallel_type}.")
        executor_class = concurrent.futures.ProcessPoolExecutor if self._parallel_type == 'processes' else concurrent.futures.ThreadPoolExecutor
        try:
            with executor_class(max_workers=max_workers) as executor:
                if self._parallel_type == 'processes':
                    responses = list(executor.map(Process._process_wrapper, [(self._process, p) for p in params]))
                else:
                    responses = list(executor.map(lambda x: self._process(*x), params))
            Logger.info(f"Processed {len(responses)} items successfully in parallel.")
            return responses
        except Exception as e:
            Logger.error(f"Error during parallel process execution: {str(e)} at {__file__}:{inspect.currentframe().f_lineno}")
            raise


class FileProcess(Process):
    """
    Class for file processing with timestamp-based control to prevent reprocessing.

    This class extends Process by adding the ability to control execution
    based on file modification timestamps. It avoids unnecessary reprocessing
    of files that have not been modified since the last successful processing.

    It uses a control file to track the last processing timestamp for each file,
    stored in a dedicated folder within the application's user data directory.

    Methods:
        _controlled_run: Executes processing with timestamp control logic.
        run: Executes processing for multiple files, with optional timestamp control.

    Inherits from:
        Process: Base class providing parallel/serial processing capabilities.
    """

    def _controlled_run(self, *args: Any) -> Tuple[str, bool, Optional[str], Any]:
        """Execute a function with file timestamp-based control.

        This function checks if a file needs to be processed based on its creation
        timestamp compared to the last recorded processing timestamp. Control is maintained
        through a pickle file that stores the timestamp of the last successful execution.

        Args:
            *args: Variable length argument list. Expects the first argument to be the
                   processing function and the second to be the file path, followed by
                   any other arguments required by the processing function.

        Returns:
            Tuple[str, bool, Optional[str], Any]: A tuple containing:
                - file_path (str): Path of the processed file.
                - success (bool): True if processed successfully, False otherwise.
                - error_message (Optional[str]): Error message if processing failed, None otherwise.
                - result (Any): Function result if successful, None otherwise.

        Raises:
            ValueError: If not enough arguments are provided (at least processing function and file path).
            FileNotFoundError: If the file to be processed does not exist.

        Note:
            The control file is stored in a dedicated folder under the application's
            data directory, using a hash of the function's full reference as the folder name
            and a hash of the file path as the control file name.
        """
        from fbpyutils.file import creation_date
        Logger.debug(f"Starting _controlled_run with args: {args}")
        try:
            if len(args) < 2:
                Logger.error("Not enough arguments for _controlled_run. Expected at least (process_function, file_path).")
                raise ValueError('Not enough arguments to run')

            process: Callable = args[0] # Added type hint
            process_file: str = args[1] # Added type hint

            if not os.path.exists(process_file):
                Logger.error(f"Process file not found: {process_file}")
                raise FileNotFoundError(f"Process file {process_file} does not exist")

            # Create control folder
            control_folder: str = os.path.sep.join([Env.USER_APP_FOLDER,
                                             f"p_{hash_string(Process.get_function_info(process)['full_ref'])}.control"])
            if not os.path.exists(control_folder):
                Logger.info(f"Creating control folder: {control_folder}")
                try:
                    os.makedirs(control_folder)
                except FileExistsError:
                    Logger.warning(f"{control_folder} already exists, probably created by concurrent process. Skipping.")

            # Define control file path
            control_file: str = os.path.sep.join([control_folder, f"f_{hash_string(process_file)}.reg"])

            # Get current file timestamp
            current_timestamp: float = creation_date(process_file).timestamp()

            # Check if control file exists and read last timestamp
            control_exists: bool = os.path.exists(control_file)
            Logger.debug(f"Control file exists for {process_file}: {control_exists}")
            if control_exists:
                try:
                    with open(control_file, 'rb') as cf:
                        last_timestamp: float = pickle.load(cf) # Added type hint
                except Exception as e:
                    Logger.warning(f"Could not read control file {control_file}: {e}. Treating as if control file does not exist.")
                    last_timestamp = -1 # Treat as if no previous timestamp

                # If file has not been modified since last processing, skip processing
                if last_timestamp >= current_timestamp:
                    Logger.debug(f"Control file timestamp: {last_timestamp}, File timestamp: {current_timestamp}. Elapsed time: {round(abs(last_timestamp - current_timestamp), 4)}")
                    Logger.info(f"Skipping unmodified file: {process_file}.")
                    return (process_file, True, "Skipped", None)

            Logger.info(f"Processing file: {process_file}")
            # Execute processing function
            try:
                result = process(process_file)  # Call with file path for file processing functions
                
                # Handle various return value formats from the process function
                if len(result) < 3:
                    Logger.error(f"Unexpected result length from process function: {len(result)}. Result: {result}")
                    return (process_file, False, "Unexpected result length", None)
                
                # Extract components based on ProcessingFilesFunction protocol
                # For a 4-tuple, it should be (file_path, success, message, data)
                if len(result) >= 4:
                    success = result[1]  # success is second element
                    message = result[2]  # message is third element
                    proc_result = result[3]  # result is fourth element
                else:
                    # For a 3-tuple, assume (success, message, data)
                    success = result[0]
                    message = result[1]
                    proc_result = result[2]
            except Exception as e:
                Logger.error(f"Error processing file {process_file}: {str(e)}")
                return (process_file, False, str(e), None)

            # Update control file if processing was successful
            if success:  # success
                try:
                    with open(control_file, 'wb') as cf:
                        pickle.dump(current_timestamp, cf)
                    Logger.info(f"Updated control file: {control_file}")
                except Exception as e:
                    Logger.error(f"Error writing control file {control_file}: {e}")
            # Remove control file if it was created but an error occurred
            elif not control_exists and os.path.exists(control_file):
                try:
                    os.remove(control_file)
                    Logger.info(f"Removed control file due to error: {control_file}")
                except Exception as e:
                    Logger.error(f"Error removing control file {control_file}: {e}")

            # For ProcessingFilesFunction, return consistent format (file_path, success, message, result)
            Logger.debug(f"Finished _controlled_run for {process_file}. Success: {success}")
            return (process_file, success, message, proc_result)
        except Exception as e:
            Logger.critical(f"Critical error in controlled run for {process_file}: {str(e)} at {__file__}:{inspect.currentframe().f_lineno}")
            raise

    def __init__(self, process: Callable[..., ProcessingFilesFunction], parallelize: bool = True,
                 workers: Optional[int] = Process._MAX_WORKERS, sleeptime: float = 0) -> None:
        """
        Initializes a new instance of FileProcess.

        Args:
            process (Callable): The file processing function to be executed.
                                 It must conform to the ProcessingFilesFunction protocol.
            parallelize (bool): If True, runs processing in parallel. If False, runs serially.
                                 Defaults to True.
            workers (Optional[int]): Number of workers for parallel execution.
                                     Defaults to Process._MAX_WORKERS (CPU count).
            sleeptime (float): Wait time in seconds between executions in serial mode. Defaults to 0.
        """
        super().__init__(process, parallelize, workers, sleeptime) # Pass process to super().__init__
        self._process: Callable = process # Added type hint
        Logger.debug(f"Initializing FileProcess with parallelize={parallelize}, workers={workers}, sleeptime={sleeptime}")
        super().__init__(process, parallelize, workers, sleeptime) # Pass process to super().__init__
        self._process: Callable = process # Added type hint
        self._parallelize: bool = parallelize and Process.is_parallelizable()
        self._workers: int = workers or Process._MAX_WORKERS # Ensured _workers is always int
        self.sleeptime: float = 0 if sleeptime < 0 else sleeptime
        logging.info(f"FileProcess initialized: parallel={self._parallelize}, workers={self._workers}")

    def run(self, params: List[Tuple[Any, ...]], controlled: bool = False) -> List[Tuple[str, bool, Optional[str], Any]]:
        """
        Executes file processing for multiple files, optionally with timestamp control.

        This function extends the run method of the Process class by adding the capability to
        control execution based on file timestamps, avoiding reprocessing of unmodified files.

        Args:
            params (List[Tuple[Any, ...]]): List of parameter tuples for processing.
                                             Each tuple should contain at least the file path as the first element,
                                             followed by any other arguments required by the processing function.
            controlled (bool): If True, uses timestamp-based execution control to prevent reprocessing
                               of unmodified files. Defaults to False.

        Returns:
            List[Tuple[str, bool, Optional[str], Any]]: List of processing results. Each tuple contains:
                - file_path (str): Path of the processed file.
                - success (bool): True if processed successfully, False otherwise.
                - error_message (Optional[str]): Error message if processing failed, None otherwise.
                - result (Any): Function result if successful, None otherwise.
        """
        logging.info(f"Starting FileProcess run with {len(params)} items, controlled: {controlled}")
        try:
            if controlled:
                logging.info("Starting controlled execution for FileProcess.")
                # Save the original process function
                original_process: Callable = self._process # Added type hint
                # Temporarily replace with _controlled_run method
                self._process = self._controlled_run
                try:
                    # Execute using the modified infrastructure for execution control
                    _params: List[Tuple[Any, ...]] = [(original_process,) + p for p in params] # Added type hint
                    # Execute using the base class infrastructure
                    results = super().run(_params)
                    logging.info("Finished controlled execution for FileProcess.")
                    return results
                finally:
                    # Restore the original function
                    self._process = original_process
            else:
                logging.info("Starting normal execution for FileProcess.")
                # If controlled=False, use the default behavior of the base class
                results = super().run(params)
                logging.info("Finished normal execution for FileProcess.")
                return results
        except Exception as e:
            logging.critical(f"Critical error in FileProcess run: {str(e)} at {__file__}:{inspect.currentframe().f_lineno}")
            raise


class SessionProcess(Process):
    """
    Class for session-based process execution with resume capability.

    This class extends Process by adding session-based control, allowing
    processing to be resumed from the point of interruption or failure.
    It is useful for long-running processes where it's important to avoid
    re-executing already completed tasks in case of interruptions.

    It uses session and task control files to track the execution status,
    stored in a dedicated folder within the application's user data directory.
    """

    @staticmethod
    def generate_session_id() -> str:
        """
        Generates a unique session ID.

        Returns:
            str: A unique UUID4 string.
        """
        logging.debug("Generating new session ID.")
        return str(uuid.uuid4())

    @staticmethod
    def generate_task_id(params: Tuple[Any, ...]) -> str:
        """
        Generates a unique task ID based on the input parameters.

        Args:
            params (Tuple[Any, ...]): The parameters for which to generate a task ID.

        Returns:
            str: A SHA256 hash of the string representation of the parameters.
        """
        logging.debug(f"Generating task ID for parameters: {params}")
        return hash_string(str(params))

    def _controlled_run(self, *args: Any) -> Tuple[str, bool, Optional[str], Any]:
        """Execute a function with session-based control.

        This function manages the execution of a processing function within a session,
        allowing for resumption of tasks. It tracks the status of each task (pending,
        completed, failed) using pickle files.

        Args:
            *args: Variable length argument list. Expects the first argument to be the
                   processing function, the second to be the session ID, the third to be
                   the task ID, and subsequent arguments to be the parameters for the
                   processing function.

        Returns:
            Tuple[str, bool, Optional[str], Any]: A tuple containing:
                - task_id (str): The ID of the processed task.
                - success (bool): True if processed successfully, False otherwise.
                - error_message (Optional[str]): Error message if processing failed, None otherwise.
                - result (Any): Function result if successful, None otherwise.

        Raises:
            ValueError: If not enough arguments are provided (at least processing function, session ID, and task ID).

        Note:
            Session and task control files are stored in a dedicated folder under the
            application's user data directory.
        """
        logging.debug(f"Starting SessionProcess _controlled_run with args: {args}")
        try:
            if len(args) < 3:
                logging.error("Not enough arguments for SessionProcess _controlled_run. Expected at least (process_function, session_id, task_id).")
                raise ValueError('Not enough arguments to run')

            process: Callable = args[0]
            session_id: str = args[1]
            task_id: str = args[2]
            process_params: Tuple[Any, ...] = args[3:]

            # Create session control folder
            session_control_folder: str = os.path.sep.join([Env.USER_APP_FOLDER,
                                                     f"s_{session_id}.session"])
            if not os.path.exists(session_control_folder):
                logging.info(f"Creating session control folder: {session_control_folder}")
                try:
                    os.makedirs(session_control_folder)
                except FileExistsError:
                    logging.warning(f"{session_control_folder} already exists, probably created by concurrent process. Skipping.")

            # Define task control file path
            task_control_file: str = os.path.sep.join([session_control_folder, f"t_{task_id}.task"])

            # Check if task was already processed successfully
            if os.path.exists(task_control_file):
                try:
                    with open(task_control_file, 'rb') as tcf:
                        task_status = pickle.load(tcf)
                    if task_status.get('status') == 'completed':
                        logging.info(f"Skipping already completed task: {task_id} in session {session_id}.")
                        return (task_id, True, "Skipped (completed)", task_status.get('result'))
                except Exception as e:
                    logging.warning(f"Could not read task control file {task_control_file}: {e}. Re-processing task.")

            logging.info(f"Processing task: {task_id} in session {session_id}.")
            # Execute processing function
            try:
                result = process(*process_params)
                
                # Handle various return value formats from the process function
                if len(result) < 3:
                    logging.error(f"Unexpected result length from process function: {len(result)}. Result: {result}")
                    success = False
                    message = "Unexpected result length"
                    proc_result = None
                else:
                    success = result[0]
                    message = result[1]
                    proc_result = result[2]
            except Exception as e:
                logging.error(f"Error processing task {task_id} in session {session_id}: {str(e)}")
                success = False
                message = str(e)
                proc_result = None

            # Update task control file
            task_status = {
                'status': 'completed' if success else 'failed',
                'timestamp': datetime.now(),
                'message': message,
                'result': proc_result
            }
            try:
                with open(task_control_file, 'wb') as tcf:
                    pickle.dump(task_status, tcf)
                logging.info(f"Updated task control file for {task_id} in session {session_id}. Status: {task_status['status']}")
            except Exception as e:
                logging.error(f"Error writing task control file {task_control_file}: {e}")

            logging.debug(f"Finished SessionProcess _controlled_run for task {task_id}. Success: {success}")
            return (task_id, success, message, proc_result)
        except Exception as e:
            logging.critical(f"Critical error in SessionProcess controlled run for session {session_id}, task {task_id}: {str(e)} at {__file__}:{inspect.currentframe().f_lineno}")
            raise

    def __init__(self, process: Callable[..., ProcessingFunction], parallelize: bool = True,
                 workers: Optional[int] = Process._MAX_WORKERS, sleeptime: float = 0) -> None:
        """
        Initializes a new instance of SessionProcess.

        Args:
            process (Callable): The processing function to be executed.
                                 It must conform to the ProcessingFunction protocol.
            parallelize (bool): If True, runs processing in parallel. If False, runs serially.
                                 Defaults to True.
            workers (Optional[int]): Number of workers for parallel execution.
                                     Defaults to Process._MAX_WORKERS (CPU count).
            sleeptime (float): Wait time in seconds between executions in serial mode. Defaults to 0.
        """
        logging.debug(f"Initializing SessionProcess with parallelize={parallelize}, workers={workers}, sleeptime={sleeptime}")
        super().__init__(process, parallelize, workers, sleeptime)
        self._process: Callable = process
        self._parallelize: bool = parallelize and Process.is_parallelizable()
        self._workers: int = workers or Process._MAX_WORKERS
        self.sleeptime: float = 0 if sleeptime < 0 else sleeptime
        logging.info(f"SessionProcess initialized: parallel={self._parallelize}, workers={self._workers}")

    def run(self, params: List[Tuple[Any, ...]], session_id: Optional[str] = None, controlled: bool = False) -> List[Tuple[str, bool, Optional[str], Any]]:
        """
        Executes processing for multiple tasks within a session, with resume capability.

        This function extends the run method of the Process class by adding session-based
        control, allowing processing to be resumed from the point of interruption or failure.

        Args:
            params (List[Tuple[Any, ...]]): List of parameter tuples for processing.
                                             Each tuple contains the arguments to be passed
                                             to the processing function.
            session_id (Optional[str]): A unique identifier for the processing session.
                                        If None, a new session ID will be generated.
            controlled (bool): If True, uses session-based execution control to enable
                               resume capability. Defaults to False.

        Returns:
            List[Tuple[str, bool, Optional[str], Any]]: List of processing results. Each tuple contains:
                - task_id (str): The ID of the processed task.
                - success (bool): True if processed successfully, False otherwise.
                - error_message (Optional[str]): Error message if processing failed, None otherwise.
                - result (Any): Function result if successful, None otherwise.
        """
        logging.info(f"Starting SessionProcess run with {len(params)} tasks, session_id: {session_id}, controlled: {controlled}")
        try:
            if controlled:
                _session_id = session_id if session_id else SessionProcess.generate_session_id()
                logging.info(f"Starting session controlled execution for SessionProcess with session ID: {_session_id}.")
                # Save the original process function
                original_process: Callable = self._process
                # Temporarily replace with _controlled_run method
                self._process = self._controlled_run
                try:
                    _params: List[Tuple[Any, ...]] = [
                        (original_process, _session_id, SessionProcess.generate_task_id(p)) + p
                        for p in params
                    ]
                    results = super().run(_params)
                    logging.info(f"Finished session controlled execution for SessionProcess with session ID: {_session_id}.")
                    return results
                finally:
                    # Restore the original function
                    self._process = original_process
            else:
                logging.info("Starting normal execution for SessionProcess.")
                # If controlled=False, use the default behavior of the base class
                # For consistency, we still generate task IDs, but they won't be persisted
                _params_with_task_ids = [
                    (SessionProcess.generate_task_id(p),) + p
                    for p in params
                ]
                # The base Process.run expects (success, message, result) from _process.
                # We need to adapt the lambda to return (task_id, success, message, result)
                # when not controlled, so the return format is consistent.
                # This requires a slight modification to how the base run is called or how _process is defined.
                # For now, let's assume the base run handles the tuple correctly,
                # and we'll just pass the original params.
                # If the base run expects (success, message, result), and our _process returns (task_id, success, message, result),
                # then the base run will get (task_id, success, message) as its (success, message, result).
                # This needs careful consideration.
                # Let's adjust the _process_wrapper in Process to handle this, or ensure _process returns the expected format.
                # For now, I'll assume the base Process.run expects the direct output of self._process.
                # If _process returns (task_id, success, message, result), and base Process.run expects (success, message, result),
                # then we need to wrap it.
                # Given the current structure, the base Process.run expects (bool, Optional[str], Any).
                # Our _controlled_run returns (str, bool, Optional[str], Any).
                # This means when controlled=False, we need to ensure the self._process returns (bool, Optional[str], Any).
                # The original `process` passed to SessionProcess.__init__ is of type ProcessingFunction,
                # which returns (bool, Optional[str], Any). So, for non-controlled, it's fine.
                # The issue is the return type of SessionProcess.run itself. It should return (task_id, success, message, result).
                # So, for non-controlled, we need to generate a task_id and combine it with the result of the original process.
                
                results = []
                for p in params:
                    task_id = SessionProcess.generate_task_id(p)
                    success, message, proc_result = self._process(*p)
                    results.append((task_id, success, message, proc_result))
                
                logging.info("Finished normal execution for SessionProcess.")
                return results
        except Exception as e:
            logging.critical(f"Critical error in SessionProcess run: {str(e)} at {__file__}:{inspect.currentframe().f_lineno}")
            raise

    @staticmethod
    def generate_session_id() -> str:
        """
        Generates a unique session ID with the prefix 'session_'.

        Session IDs are used to group tasks within a processing session,
        allowing for session-level control and tracking.

        Returns:
            str: Unique session ID.
        """
        return f"session_{uuid.uuid4()}"

    @staticmethod
    def generate_task_id(params: Tuple[Any, ...]) -> str:
        """
        Generates a unique task ID based on the hash of the process parameters.

        Task IDs are used to uniquely identify each processing task within a session,
        allowing for task-level control and tracking of execution status.

        Args:
            params (Tuple[Any, ...]): Tuple of process parameters. The parameters that define the task.

        Returns:
            str: Unique task ID.
        """
        params_hash: str = hash_string(str(params)) # Added type hint
        return f"task_{params_hash}"

    def _controlled_run(self, *args: Any) -> Tuple[str, bool, Optional[str], Any]:
        """
        Executes a function with session-based control.

        Checks if a task needs to be processed based on the session control mechanism.
        It determines if a task has already been successfully processed within the current session
        by checking for the existence of a task control file.

        Args:
            *args: Variable length argument list. Expects the first argument to be the session ID,
                   the second to be the processing function, and the following arguments
                   are the parameters for the processing function.

        Returns:
            Tuple[str, bool, Optional[str], Any]: A tuple containing:
                - task_id (str): ID of the processed task.
                - success (bool): True if processed successfully, False otherwise.
                - error_message (Optional[str]): Error message if processing failed, None otherwise.
                - result (Any): Function result if successful, None otherwise.

        Raises:
            ValueError: If insufficient arguments are provided (less than session ID, process function, and parameters).
        """
        try:
            if len(args) < 3:
                raise ValueError('Not enough arguments to run session controlled process')

            session_id: str = args[0] # Added type hint
            process: Callable = args[1] # Added type hint
            params: Tuple[Any, ...] = args[2:] # Added type hint
            task_id: str = SessionProcess.generate_task_id(params) # Added type hint

            # Create session control folder
            session_control_folder: str = os.path.sep.join([Env.USER_APP_FOLDER,
                                                     f"session_control",
                                                     f"s_{hash_string(session_id)}"])
            if not os.path.exists(session_control_folder):
                Logger.info(f"Creating session control folder: {session_control_folder}")
                try:
                    os.makedirs(session_control_folder)
                except FileExistsError:
                    Logger.warning(f"{session_control_folder} already exists, probably created by concurrent process. Skipping.")

            # Define task control file path
            task_control_file: str = os.path.sep.join([session_control_folder, f"t_{hash_string(task_id)}.reg"])

            # Check if task control file exists
            task_control_exists: bool = os.path.exists(task_control_file)
            Logger.info(f"Task control file exists: {task_control_exists} for task_id: {task_id}")
            if task_control_exists:
                Logger.info(f"Skipping already processed task: {task_id}")
                return (task_id, True, "Skipped", None)

            Logger.info(f"Processing task: {task_id} in session: {session_id}")
            # Execute processing function
            try:
                # For session process function, we pass the actual parameters
                result = process(*params)  # May return various formats

                # Handle various return value formats from the process function
                if len(result) < 2:
                    Logger.error(f"Unexpected result length: {len(result)}. Result: {result}")
                    return (task_id, False, "Unexpected result length", None)
                
                # Extract components from result
                # For session process func, typically (success, message, result, data)
                success = result[0]
                message = result[1] if len(result) > 1 else None
                proc_result = result[2] if len(result) > 2 else None
            except Exception as e:
                Logger.error(f"Error processing task: {str(e)}")
                return (task_id, False, str(e), None)

            # Update task control file if processing was successful
            if success:  # success
                with open(task_control_file, 'wb') as cf:
                    pickle.dump(True, cf) # just mark that the task was successfully executed
                Logger.info(f"Updated task control file: {task_control_file}")
            # Remove task control file if it was created but an error occurred
            elif not task_control_exists and os.path.exists(task_control_file):
                os.remove(task_control_file)
                Logger.info(f"Removed task control file due to error: {task_control_file}")

            # For the session process, return a standardized format
            # Return structure: (task_id, success, message, result)
            return (task_id, success, message, proc_result)
        except Exception as e:
            Logger.error(f"Error in session controlled run: {str(e)} at {__file__}:{inspect.currentframe().f_lineno}")
            raise

    def __init__(self, process: Callable[..., ProcessingFunction], parallelize: bool = True,
                 workers: Optional[int] = Process._MAX_WORKERS, sleeptime: float = 0,
                 parallel_type: str = 'threads') -> None:
        """
        Initializes a new instance of SessionProcess.

        Args:
            process (Callable): The processing function to be executed within a session.
                                 It must conform to the ProcessingFunction protocol.
            parallelize (bool): If True, runs processing in parallel. If False, runs serially.
                                 Defaults to True.
            workers (Optional[int]): Number of workers for parallel execution.
                                     Defaults to Process._MAX_WORKERS (CPU count).
            sleeptime (float): Wait time in seconds between executions in serial mode. Defaults to 0.
            parallel_type (str): Type of parallelization ('threads' or 'processes'). Defaults to 'threads'.
        """
        super().__init__(process, parallelize, workers, sleeptime, parallel_type)
        self._process: Callable = process # Added type hint
        self._parallelize: bool = parallelize and Process.is_parallelizable(parallel_type=self._parallel_type)
        self._workers: int = workers or Process._MAX_WORKERS # Ensured _workers is always int
        self.sleeptime: float = 0 if sleeptime < 0 else sleeptime
        Logger.info(f"SessionProcess initialized: parallel={self._parallelize}, workers={self._workers}, type={self._parallel_type}")

    def run(self, params: List[Tuple[Any, ...]], session_id: Optional[str] = None, controlled: bool = False) -> List[Tuple[str, bool, Optional[str], Any]]:
        """
        Executes processing for multiple parameter sets, optionally with session control.

        This function extends the run method of the Process class by adding session-based execution control.
        It allows for resuming processing sessions by skipping tasks that have already been successfully completed.

        Args:
            params (List[Tuple[Any, ...]]): List of parameter tuples for processing.
                                             Each tuple contains the arguments for a single task
                                             to be processed within the session.
            session_id (Optional[str]): Session ID for resume control. If provided, the process will attempt
                                         to resume the session. If None, a new session ID will be generated.
                                         Defaults to None, which starts a new session.
            controlled (bool): If True, uses session-based execution control to enable session resume
                               capabilities. Defaults to False.

        Returns:
            List[Tuple[str, bool, Optional[str], Any]]: List of processing results. Each tuple contains:
                - task_id (str): ID of the processed task.
                - success (bool): True if processed successfully, False otherwise.
                - error_message (Optional[str]): Error message if processing failed, None otherwise.
                - result (Any): Function result if successful, None otherwise.
        """
        try:
            if controlled:
                Logger.info("Starting session controlled execution")
                _session_id: str = session_id or SessionProcess.generate_session_id() # Added type hint
                Logger.info(f"Session ID: {_session_id}")
                # Save the original process function
                original_process: Callable = self._process # Added type hint
                # Temporarily replace with _controlled_run method
                # Need to ensure it's bound to self to avoid method missing self issue
                self._process = self._controlled_run
                try:
                    # Execute using the modified infrastructure for session control
                    _params: List[Tuple[Any, ...]] = [(_session_id, original_process) + p for p in params] # Added type hint
                    # Execute using the base class infrastructure
                    return super().run(_params)
                finally:
                    # Restore the original function
                    self._process = original_process
            else:
                Logger.info("Starting normal execution")
                # If controlled=False, use the default behavior of the base class
                return super().run(params)
        except Exception as e:
            Logger.error(f"Error in session process execution: {str(e)} at {__file__}:{inspect.currentframe().f_lineno}")
            raise


