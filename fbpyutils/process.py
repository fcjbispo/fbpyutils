"""
Module for parallel or serial file processing with execution control.

This module provides classes to execute processing functions on multiple files,
with support for parallel or serial execution, and optional timestamp-based control
to avoid unnecessary reprocessing.

Classes:
    Process: Base class for parallel/serial processing
    ProcessFiles: Class for file processing with timestamp control
    SessionProcess: Class for session-based processing with resume capability
"""

import os
import time
import pickle
import inspect
import multiprocessing
import uuid
import concurrent.futures

from typing import Any, Callable, List, Tuple, Dict, Optional, TypeVar, Protocol

from fbpyutils import Env, Logger
from fbpyutils.file import creation_date
from fbpyutils.string import hash_string


# Type variable para função de processamento genérica
T = TypeVar('T')

class ProcessingFunction(Protocol):
    def __call__(self, params: Tuple[Any, ...]) -> Tuple[bool, Optional[str], Any]:
        ...

class ProcessingFilesFunction(Protocol):
    def __call__(self, params: Tuple[Any, ...]) -> Tuple[str, bool, Optional[str], Any]:
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
        _MAX_WORKERS (int): Maximum number of worker processes or threads for parallel processing.
            Defaults to the number of CPU cores available if not explicitly defined,
            otherwise, it is set to 1 on systems where CPU count detection is not supported.
        _process (Callable): The processing function to be executed. This function should
            accept a tuple of parameters and return a tuple indicating success, an optional
            error message, and a result.
        _parallelize (bool): A flag that indicates whether to run the processing in parallel.
            Set to True for parallel execution, False for serial.
        _workers (Optional[int]): The number of worker processes or threads to use in parallel execution.
            If None, defaults to _MAX_WORKERS.
        sleeptime (float): The wait time in seconds between successive executions in serial mode.
            Useful to throttle processing and reduce system load.
        _parallel_type (str): Type of parallelization to use, either 'threads' (default) or 'processes'.

    Methods:
        get_available_cpu_count: Returns the number of available CPU cores.
        is_parallelizable: Checks if parallel processing is supported on the current system.
        run: Executes the processing function for each parameter set, either in parallel or serial.
        get_function_info: Provides detailed information about a given function, such as module and name.
    """

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
            parallel_type (str): Type of parallelization to check ('threads' or 'processes'). Default is 'threads'.

        Returns:
            bool: True if parallel processing is supported for the specified type, False otherwise.

        Raises:
            ValueError: If an invalid parallel_type is provided.
        """
        if parallel_type == 'processes':
            try:
                import multiprocessing
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
                - id: Memory address of the function
                - module: Module path where the function is defined
                - name: Qualified name of the function
                - full_ref: Full reference combining module and name
                - unique_ref: Absolute unique reference including memory address

        Example:
            >>> def my_func(): pass
            >>> info = Process.get_function_info(my_func)
            >>> print(info['full_ref'])
            'mymodule.my_func'

        Note:
            The unique_ref can be used to distinguish between different instances
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
                 parallel_type: str = 'threads'):
        """
        Initializes a new Process instance.

        Args:
            process (Callable): Function to be executed for each parameter set
            parallelize (bool): If True, runs in parallel. If False, runs serially
            workers (Optional[int]): Number of workers for parallel execution. Defaults to CPU count.
            sleeptime (float): Wait time between executions in serial mode
            parallel_type (str): Type of parallelization ('threads' or 'processes'). Default is 'threads'.

        Raises:
            ValueError: If an invalid parallel_type is provided.
        """
        parallel_type = parallel_type or 'threads'
        if parallel_type not in ('threads', 'process'):
            raise ValueError(f'Invalid parallel processing type: {parallel_type}. Valid types are: threads or process.')
        self._process = process
        self._parallel_type = parallel_type
        self._parallelize = parallelize and Process.is_parallelizable(parallel_type=self._parallel_type)
        self._workers = workers or Process._MAX_WORKERS
        self.sleeptime = 0 if sleeptime < 0 else sleeptime
        Logger.log(Logger.INFO, f"Process initialized: parallel={self._parallelize}, type={self._parallel_type}, workers={self._workers}")

    def run(self, params: List[Tuple[Any, ...]]) -> List[Tuple[bool, Optional[str], Any]]:
        """
        Executes processing for multiple parameter sets.

        Args:
            params (List[Tuple[Any, ...]]): List of parameter tuples for processing

        Returns:
            List[Tuple[bool, Optional[str], Any]]: List of processing results where each tuple contains:
                - success: True if processing succeeded, False otherwise
                - error_message: Error message if processing failed, None otherwise
                - result: Processing result if successful, None otherwise

        Raises:
            Exception: Any exception that may occur during processing

        Note:
            When running in parallel mode, the order of results may not match the order of input parameters.
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
            if self._parallel_type == 'processes':
                with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
                    responses = list(executor.map(lambda x: self._process(*x), params))
            else:  # Default to threads
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    responses = list(executor.map(lambda x: self._process(*x), params))

            Logger.log(Logger.INFO, f"Processed {len(responses)} items successfully")
            return responses
        except Exception as e:
            Logger.log(Logger.ERROR, f"Error during process execution: {str(e)} at {__file__}:{inspect.currentframe().f_lineno}")
            raise


class ProcessFiles(Process):
    """
    Class for file processing with timestamp-based control.

    This class extends Process by adding the ability to control execution
    based on file timestamps, avoiding unnecessary reprocessing
    of unmodified files.

    Methods:
        _controlled_run: Executes processing with timestamp control
        run: Executes processing for multiple files

    Inherits from:
        Process: Base class providing parallel/serial processing capabilities
    """

    def _controlled_run(self, *args: Any) -> Tuple[str, bool, Optional[str], Any]:
        """Execute a function with file timestamp-based control.

        This function checks if a file needs to be processed based on its creation
        timestamp compared to the last recorded processing. Control is maintained
        through a pickle file that stores the timestamp of the last execution.

        Args:
            *args: Unpacked arguments where the first is the file path

        Returns:
            Tuple[str, bool, Optional[str], Any]: A tuple containing:
                - file_path: Path of the processed file
                - success: True if processed successfully, False otherwise
                - error_message: Error message if processing failed, None otherwise
                - result: Function result if successful, None otherwise

        Raises:
            ValueError: If no arguments are provided
            FileNotFoundError: If the file to be processed does not exist

        Note:
            The control file is stored in a dedicated folder under the application's
            data directory, using a hash of the function reference as the folder name.
        """
        try:
            if len(args) < 2:
                raise ValueError('No enough arguments to run')
            
            process = args[0]

            process_file = args[1]
            if not os.path.exists(process_file):
                raise FileNotFoundError(f"Process file {process_file} does not exist")
            
            # Cria pasta de controle
            control_folder = os.path.sep.join([Env.MM_USER_APP_FOLDER, 
                                             f"p_{hash_string(Process.get_function_info(process)['full_ref'])}.control"])
            if not os.path.exists(control_folder):
                Logger.log(Logger.INFO, f"Creating control folder: {control_folder}")
                try:
                    os.makedirs(control_folder)
                except FileExistsError:
                    Logger.log(Logger.WARNING, f"{control_folder} already exists, probaly created by concurrent process. Skipping.")

            # Define arquivo de controle
            control_file = os.path.sep.join([control_folder, f"f_{hash_string(process_file)}.reg"])
            
            # Obtém timestamp atual do arquivo
            current_timestamp = creation_date(process_file).timestamp()
            
            # Verifica se arquivo de controle existe e lê timestamp
            control_exists = os.path.exists(control_file)
            Logger.log(Logger.INFO, f"Control file exists: {control_exists}")
            if control_exists:
                with open(control_file, 'rb') as cf:
                    last_timestamp = pickle.load(cf)
                    
                # Se arquivo não foi modificado, ignora processamento
                if last_timestamp >= current_timestamp:
                    Logger.log(Logger.INFO, f"Skipping unmodified file: {process_file}")
                    return (process_file, True, "Skipped", None)
            
            Logger.log(Logger.INFO, f"Processing file: {process_file}")
            # Executa função de processamento
            _args = args[1:]
            result = process(_args)

            if len(result) < 2:
                Logger.log(Logger.ERROR, f"Unexpected result length: {len(result)}. Result: {result}")
                return (process_file, False, "Unexpected result length", None)
            
            # Atualiza arquivo de controle se processamento teve sucesso
            if result[1]:  # sucesso
                with open(control_file, 'wb') as cf:
                    pickle.dump(current_timestamp, cf)
                Logger.log(Logger.INFO, f"Updated control file: {control_file}")
            # Remove arquivo de controle se foi criado mas houve erro
            elif not control_exists and os.path.exists(control_file):
                os.remove(control_file)
                Logger.log(Logger.INFO, f"Removed control file due to error: {control_file}")
            
            return result
        except Exception as e:
            Logger.log(Logger.ERROR, f"Error in controlled run: {str(e)} at {__file__}:{inspect.currentframe().f_lineno}")
            raise

    def __init__(self, process: Callable[..., ProcessingFilesFunction], parallelize: bool = True, 
                 workers: Optional[int] = Process._MAX_WORKERS, sleeptime: float = 0):
        """
        Inicializa uma nova instância de ProcessFiles.

        Args:
            process: Função a ser executada para cada conjunto de parâmetros
            parallelize: Se True, executa em paralelo. Se False, executa em série
            workers: Número de workers para execução paralela
            sleeptime: Tempo de espera entre execuções em modo serial
        """
        self._process = process
        self._parallelize = parallelize and Process.is_parallelizable()
        self._workers = workers or Process._MAX_WORKERS
        self.sleeptime = 0 if sleeptime < 0 else sleeptime
        Logger.log(Logger.INFO, f"ProcessFiles initialized: parallel={self._parallelize}, workers={self._workers}")
        
    def run(self, params: List[Tuple[Any, ...]], controlled: bool = False) -> List[Tuple[str, bool, Optional[str], Any]]:
        """
        Executa o processamento para múltiplos arquivos, opcionalmente com controle de timestamp.

        Esta função estende o método run da classe Process adicionando a capacidade de
        controlar a execução baseada em timestamps dos arquivos.

        Args:
            params: Lista de tuplas de parâmetros para processamento
            controlled: Se True, usa controle de execução baseado em timestamp

        Returns:
            Lista de tuplas contendo resultados do processamento:
                - caminho_arquivo: Caminho do arquivo processado
                - sucesso: True se processado com sucesso, False caso contrário
                - mensagem_erro: Mensagem de erro ou None se sucesso
                - resultado: Resultado da função ou None se erro
        """
        try:
            if controlled:
                Logger.log(Logger.INFO, "Starting controlled execution")
                # Guarda a função original
                original_process = self._process
                # Substitui temporariamente por _controlled_run
                self._process = self._controlled_run
                try:
                    # Executa usando a infraestrutura modificada para controle de execução
                    _params = [(original_process,) + p for p in params]
                    # Executa usando a infraestrutura da classe mãe
                    return super().run(_params)
                finally:
                    # Restaura a função original
                    self._process = original_process
            else:
                Logger.log(Logger.INFO, "Starting normal execution")
                # Se controlled=False, usa o comportamento padrão da classe mãe
                return super().run(params)
        except Exception as e:
            Logger.log(Logger.ERROR, f"Error in process execution: {str(e)} at {__file__}:{inspect.currentframe().f_lineno}")
            raise


class SessionProcess(Process):
    """
    Classe para processamento em sessão com controle de retomada baseado em sessão.

    Esta classe estende Process adicionando a capacidade de controlar a execução
    baseada em sessão, permitindo retomar processamentos a partir de falhas ou interrupções.
    """

    @staticmethod
    def generate_session_id() -> str:
        """
        Gera um ID de sessão único com o prefixo 'session_'.

        Returns:
            str: ID de sessão único.
        """
        return f"session_{uuid.uuid4()}"

    @staticmethod
    def generate_task_id(params: Tuple[Any, ...]) -> str:
        """
        Gera um ID de tarefa único com base no hash dos parâmetros do processo.

        Args:
            params: Tupla de parâmetros do processo.

        Returns:
            str: ID de tarefa único.
        """
        params_hash = hash_string(str(params))
        return f"task_{params_hash}"

    def _controlled_run(self, *args: Any) -> Tuple[str, bool, Optional[str], Any]:
        """
        Executa uma função com controle baseado em sessão.

        Verifica se uma tarefa precisa ser processada baseado no controle de sessão.

        Args:
            *args: Argumentos desempacotados onde o primeiro é o ID da sessão, o segundo é a função
                   de processamento e os seguintes são os parâmetros para a função.

        Returns:
            Tuple contendo:
                - task_id: ID da tarefa processada
                - sucesso: True se processado com sucesso, False caso contrário
                - mensagem_erro: Mensagem de erro ou None se sucesso
                - resultado: Resultado da função ou None se erro

        Raises:
            ValueError: Se argumentos insuficientes forem fornecidos.
        """
        try:
            if len(args) < 3:
                raise ValueError('Not enough arguments to run session controlled process')

            session_id = args[0]
            process = args[1]
            params = args[2:]
            task_id = SessionProcess.generate_task_id(params)

            # Cria pasta de controle da sessão
            session_control_folder = os.path.sep.join([Env.MM_USER_APP_FOLDER,
                                                     f"session_control",
                                                     f"s_{hash_string(session_id)}"])
            if not os.path.exists(session_control_folder):
                Logger.log(Logger.INFO, f"Creating session control folder: {session_control_folder}")
                try:
                    os.makedirs(session_control_folder)
                except FileExistsError:
                    Logger.log(Logger.WARNING, f"{session_control_folder} already exists, probably created by concurrent process. Skipping.")

            # Define arquivo de controle da tarefa
            task_control_file = os.path.sep.join([session_control_folder, f"t_{hash_string(task_id)}.reg"])

            # Verifica se arquivo de controle da tarefa existe
            task_control_exists = os.path.exists(task_control_file)
            Logger.log(Logger.INFO, f"Task control file exists: {task_control_exists} for task_id: {task_id}")
            if task_control_exists:
                Logger.log(Logger.INFO, f"Skipping already processed task: {task_id}")
                return (task_id, True, "Skipped", None)

            Logger.log(Logger.INFO, f"Processing task: {task_id} in session: {session_id}")
            # Executa função de processamento
            result = process(*params)

            if len(result) < 2:
                Logger.log(Logger.ERROR, f"Unexpected result length: {len(result)}. Result: {result}")
                return (task_id, False, "Unexpected result length", None)

            # Atualiza arquivo de controle se processamento teve sucesso
            if result[1]:  # sucesso
                with open(task_control_file, 'wb') as cf:
                    pickle.dump(True, cf) # apenas marca que a task foi executada com sucesso
                Logger.log(Logger.INFO, f"Updated task control file: {task_control_file}")
            # Remove arquivo de controle se foi criado mas houve erro
            elif not task_control_exists and os.path.exists(task_control_file):
                os.remove(task_control_file)
                Logger.log(Logger.INFO, f"Removed task control file due to error: {task_control_file}")

            return (task_id, result[1], result[2], result[3]) # task_id, success, message, result
        except Exception as e:
            Logger.log(Logger.ERROR, f"Error in session controlled run: {str(e)} at {__file__}:{inspect.currentframe().f_lineno}")
            raise

    def __init__(self, process: Callable[..., ProcessingFunction], parallelize: bool = True,
                 workers: Optional[int] = Process._MAX_WORKERS, sleeptime: float = 0,
                 parallel_type: str = 'threads'):
        """
        Inicializa uma nova instância de SessionProcess.

        Args:
            process: Função a ser executada para cada conjunto de parâmetros
            parallelize: Se True, executa em paralelo. Se False, executa em série
            workers: Número de workers para execução paralela
            sleeptime: Tempo de espera entre execuções em modo serial
            parallel_type (str): Tipo de paralelização ('threads' ou 'processes'). Padrão é 'threads'.
        """
        super().__init__(process, parallelize, workers, sleeptime, parallel_type)
        Logger.log(Logger.INFO, f"SessionProcess initialized: parallel={self._parallelize}, workers={self._workers}, type={self._parallel_type}")

    def run(self, params: List[Tuple[Any, ...]], session_id: str = None, controlled: bool = False) -> List[Tuple[str, bool, Optional[str], Any]]:
        """
        Executa o processamento para múltiplos conjuntos de parâmetros, opcionalmente com controle de sessão.

        Args:
            params: Lista de tuplas de parâmetros para processamento
            session_id: ID da sessão para controle de retomada. Se None, um novo ID será gerado.
            controlled: Se True, usa controle de execução baseado em sessão.

        Returns:
            Lista de tuplas contendo resultados do processamento:
                - task_id: ID da tarefa processada
                - sucesso: True se processado com sucesso, False caso contrário
                - mensagem_erro: Mensagem de erro ou None se sucesso
                - resultado: Resultado da função ou None se erro
        """
        try:
            if controlled:
                Logger.log(Logger.INFO, "Starting session controlled execution")
                _session_id = session_id or SessionProcess.generate_session_id()
                Logger.log(Logger.INFO, f"Session ID: {_session_id}")
                # Guarda a função original
                original_process = self._process
                # Substitui temporariamente por _controlled_run
                self._process = self._controlled_run
                try:
                    # Executa usando a infraestrutura modificada para controle de sessão
                    _params = [(_session_id, original_process) + p for p in params]
                    # Executa usando a infraestrutura da classe mãe
                    return super().run(_params)
                finally:
                    # Restaura a função original
                    self._process = original_process
            else:
                Logger.log(Logger.INFO, "Starting normal execution")
                # Se controlled=False, usa o comportamento padrão da classe mãe
                return super().run(params)
        except Exception as e:
            Logger.log(Logger.ERROR, f"Error in session process execution: {str(e)} at {__file__}:{inspect.currentframe().f_lineno}")
            raise


Logger.log(Logger.INFO, f"Process Module initialized - Parallelizable: {Process.is_parallelizable()}, CPU Count: {Process.get_available_cpu_count()}")
