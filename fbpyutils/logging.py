import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

# Define o diretório base para os logs na pasta HOME do usuário
LOG_DIR = Path.home() / ".fbpyutils"
LOG_FILE = LOG_DIR / "fbpyutils.log"

# Garante que o diretório de logs exista
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configura o logger global para a biblioteca fbpyutils
def setup_logging():
    """
    Configures a global file logging system for the fbpyutils library.

    Logs are rotated automatically, supporting concurrency, with a maximum of
    5 backup files and a maximum size of 256 KB per file.
    Logs are stored in a '.fbpyutils' folder within the user's HOME directory.
    """
    logger = logging.getLogger("fbpyutils")
    logger.setLevel(logging.DEBUG) # Define o nível mínimo para o logger

    # Impede a adição de múltiplos handlers se o logging já estiver configurado
    if not logger.handlers:
        # Handler para rotação de arquivos
        # maxBytes=256 * 1024 (256 KB), backupCount=5
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=256 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG) # Define o nível mínimo para o handler de arquivo

        # Formato do log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        # Opcional: Adicionar um StreamHandler para saída no console durante o desenvolvimento
        # console_handler = logging.StreamHandler()
        # console_handler.setLevel(logging.INFO)
        # console_handler.setFormatter(formatter)
        # logger.addHandler(console_handler)

    logger.info(f"Logging system initialized. Logs are being written to: {LOG_FILE}")
    logger.info(f"Log rotation configured: max size 256KB, 5 backup files.")

# Chama a função de configuração de logging quando o módulo é importado
setup_logging()

# Obtém o logger para ser usado em outros módulos
logger = logging.getLogger("fbpyutils")
