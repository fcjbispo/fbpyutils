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

from fbpyutils import Env, Logger
from fbpyutils.file import creation_date
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
            return multiprocessing.cpu_count()
        except NotImplementedError:
            Logger.log(Logger.INFO, "CPU count not supported, falling back to single worker")
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
                Logger.log(Logger.INFO, "Multiprocessing parallelization available")
                return True
            except ImportError:
                Logger.log(Logger.ERROR, f"Multiprocessing not available: {__file__}:{inspect.currentframe().f_lineno}")
                return False
        elif parallel_type == 'threads':
            Logger.log(Logger.INFO, "Default multi-threads parallelization available")
            return True
        else:
            Logger.log(Logger.WARNING, f"Unknown parallel type: {parallel_type}. Assuming not parallelizable.")
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
        self._parallelize: bool = parallelize and Process.is_parallelizable(parallel_type=self._parallel_type)
        self._workers: int = workers or Process._MAX_WORKERS # Ensured _workers is always int
        self.sleeptime: float = 0 if sleeptime < 0 else sleeptime
        Logger.log(Logger.INFO, f"Process initialized: parallel={self._parallelize}, type={self._parallel_type}, workers={self._workers}")

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
        try:
            Logger.log(Logger.INFO, f"Starting execution with parameters: {params}")
            responses: List[Tuple[bool, Optional[str], Any]] = []
            if not self._parallelize:
                Logger.log(Logger.INFO, "Running in serial mode (parallelization disabled)")
                for param in params:
                    responses.append(self._process(*param))
                    if self.sleeptime > 0:
                        time.sleep(self.sleeptime)
                return responses

            max_workers = self._workers or Process.get_available_cpu_count()
            if (max_workers < 1 or max_workers > Process.get_available_cpu_count()):
                max_workers = Process.get_available_cpu_count()

            Logger.log(Logger.INFO, f"Starting parallel execution with {max_workers} workers using {self._parallel_type}")
            executor_class = concurrent.futures.ProcessPoolExecutor if self._parallel_type == 'processes' else concurrent.futures.ThreadPoolExecutor
            with executor_class(max_workers=max_workers) as executor:
                if self._parallel_type == 'processes':
                    responses = list(executor.map(Process._process_wrapper, [(self._process, p) for p in params]))
                else:
                    responses = list(executor.map(lambda x: self._process(*x), params))

            Logger.log(Logger.INFO, f"Processed {len(responses)} items successfully")
            return responses
        except Exception as e:
            Logger.log(Logger.ERROR, f"Error during process execution: {str(e)} at {__file__}:{inspect.currentframe().f_lineno}")
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
        try:
            if len(args) < 2:
                raise ValueError('Not enough arguments to run')

            process: Callable = args[0] # Added type hint
            process_file: str = args[1] # Added type hint

            if not os.path.exists(process_file):
                raise FileNotFoundError(f"Process file {process_file} does not exist")

            # Create control folder
            control_folder: str = os.path.sep.join([Env.USER_APP_FOLDER,
                                             f"p_{hash_string(Process.get_function_info(process)['full_ref'])}.control"])
            if not os.path.exists(control_folder):
                Logger.log(Logger.INFO, f"Creating control folder: {control_folder}")
                try:
                    os.makedirs(control_folder)
                except FileExistsError:
                    Logger.log(Logger.WARNING, f"{control_folder} already exists, probaly created by concurrent process. Skipping.")

            # Define control file path
            control_file: str = os.path.sep.join([control_folder, f"f_{hash_string(process_file)}.reg"])

            # Get current file timestamp
            current_timestamp: float = os.path.getmtime(process_file)

            # Check if control file exists and read last timestamp
            control_exists: bool = os.path.exists(control_file)
            Logger.log(Logger.INFO, f"Control file exists: {control_exists}")
            if control_exists:
                with open(control_file, 'rb') as cf:
                    last_timestamp: float = pickle.load(cf) # Added type hint

                # If file has not been modified since last processing, skip processing
                if last_timestamp >= current_timestamp:
                    Logger.log(Logger.DEBUG, f"Control file timestamp: {last_timestamp}, File timestamp: {current_timestamp}. Elapsed time: {round(abs(last_timestamp - current_timestamp), 4)}")
                    Logger.log(Logger.INFO, f"Skipping unmodified file: {process_file}.")
                    return (process_file, True, "Skipped", None)

            Logger.log(Logger.INFO, f"Processing file: {process_file}")
            # Execute processing function
            try:
                result = process(process_file)  # Call with file path for file processing functions
                
                # Handle various return value formats from the process function
                if len(result) < 3:
                    Logger.log(Logger.ERROR, f"Unexpected result length: {len(result)}. Result: {result}")
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
                Logger.log(Logger.ERROR, f"Error processing file: {str(e)}")
                return (process_file, False, str(e), None)

            # Update control file if processing was successful
            if success:  # success
                with open(control_file, 'wb') as cf:
                    pickle.dump(current_timestamp, cf)
                Logger.log(Logger.INFO, f"Updated control file: {control_file}")
            # Remove control file if it was created but an error occurred
            elif not control_exists and os.path.exists(control_file):
                os.remove(control_file)
                Logger.log(Logger.INFO, f"Removed control file due to error: {control_file}")

            # For ProcessingFilesFunction, return consistent format (file_path, success, message, result)
            return (process_file, success, message, proc_result)
        except Exception as e:
            Logger.log(Logger.ERROR, f"Error in controlled run: {str(e)} at {__file__}:{inspect.currentframe().f_lineno}")
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
        self._parallelize: bool = parallelize and Process.is_parallelizable()
        self._workers: int = workers or Process._MAX_WORKERS # Ensured _workers is always int
        self.sleeptime: float = 0 if sleeptime < 0 else sleeptime
        Logger.log(Logger.INFO, f"FileProcess initialized: parallel={self._parallelize}, workers={self._workers}")

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
        try:
            if controlled:
                Logger.log(Logger.INFO, "Starting controlled execution")
                # Save the original process function
                original_process: Callable = self._process # Added type hint
                # Temporarily replace with _controlled_run method
                self._process = self._controlled_run
                try:
                    # Execute using the modified infrastructure for execution control
                    _params: List[Tuple[Any, ...]] = [(original_process,) + p for p in params] # Added type hint
                    # Execute using the base class infrastructure
                    return super().run(_params)
                finally:
                    # Restore the original function
                    self._process = original_process
            else:
                Logger.log(Logger.INFO, "Starting normal execution")
                # If controlled=False, use the default behavior of the base class
                return super().run(params)
        except Exception as e:
            Logger.log(Logger.ERROR, f"Error in process execution: {str(e)} at {__file__}:{inspect.currentframe().f_lineno}")
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
                Logger.log(Logger.INFO, f"Creating session control folder: {session_control_folder}")
                try:
                    os.makedirs(session_control_folder)
                except FileExistsError:
                    Logger.log(Logger.WARNING, f"{session_control_folder} already exists, probably created by concurrent process. Skipping.")

            # Define task control file path
            task_control_file: str = os.path.sep.join([session_control_folder, f"t_{hash_string(task_id)}.reg"])

            # Check if task control file exists
            task_control_exists: bool = os.path.exists(task_control_file)
            Logger.log(Logger.INFO, f"Task control file exists: {task_control_exists} for task_id: {task_id}")
            if task_control_exists:
                Logger.log(Logger.INFO, f"Skipping already processed task: {task_id}")
                return (task_id, True, "Skipped", None)

            Logger.log(Logger.INFO, f"Processing task: {task_id} in session: {session_id}")
            # Execute processing function
            try:
                # For session process function, we pass the actual parameters
                result = process(*params)  # May return various formats

                # Handle various return value formats from the process function
                if len(result) < 2:
                    Logger.log(Logger.ERROR, f"Unexpected result length: {len(result)}. Result: {result}")
                    return (task_id, False, "Unexpected result length", None)
                
                # Extract components from result
                # For session process func, typically (success, message, result, data)
                success = result[0]
                message = result[1] if len(result) > 1 else None
                proc_result = result[2] if len(result) > 2 else None
            except Exception as e:
                Logger.log(Logger.ERROR, f"Error processing task: {str(e)}")
                return (task_id, False, str(e), None)

            # Update task control file if processing was successful
            if success:  # success
                with open(task_control_file, 'wb') as cf:
                    pickle.dump(True, cf) # just mark that the task was successfully executed
                Logger.log(Logger.INFO, f"Updated task control file: {task_control_file}")
            # Remove task control file if it was created but an error occurred
            elif not task_control_exists and os.path.exists(task_control_file):
                os.remove(task_control_file)
                Logger.log(Logger.INFO, f"Removed task control file due to error: {task_control_file}")

            # For the session process, return a standardized format
            # Return structure: (task_id, success, message, result)
            return (task_id, success, message, proc_result)
        except Exception as e:
            Logger.log(Logger.ERROR, f"Error in session controlled run: {str(e)} at {__file__}:{inspect.currentframe().f_lineno}")
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
        Logger.log(Logger.INFO, f"SessionProcess initialized: parallel={self._parallelize}, workers={self._workers}, type={self._parallel_type}")

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
                Logger.log(Logger.INFO, "Starting session controlled execution")
                _session_id: str = session_id or SessionProcess.generate_session_id() # Added type hint
                Logger.log(Logger.INFO, f"Session ID: {_session_id}")
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
                Logger.log(Logger.INFO, "Starting normal execution")
                # If controlled=False, use the default behavior of the base class
                return super().run(params)
        except Exception as e:
            Logger.log(Logger.ERROR, f"Error in session process execution: {str(e)} at {__file__}:{inspect.currentframe().f_lineno}")
            raise


Logger.log(Logger.INFO, f"Process Module initialized - Parallelizable: {Process.is_parallelizable()}, CPU Count: {Process.get_available_cpu_count()}")
