
import logging
import os
from logging.handlers import RotatingFileHandler
from functools import lru_cache

try:
    from src.config import Config
    logger = logging.getLogger(__name__)
except ImportError:
    # Fallback para ambientes de teste ou inicialização incompleta
    print("AVISO: Não foi possível importar 'Config' de 'src.config'. A configuração do logger raiz pode ser incompleta.")
    
    logger = logging.getLogger(__name__)
    # Cria uma classe Config dummy para que o código continue funcionando sem erros de importação
    class Config:
        def __init__(self):
            self.LOG_LEVEL_STR = "INFO"
            self.parsed_log_level = logging.INFO
        @classmethod
        def get_instance(cls):
            return cls()

class OpenAIConfigurationError(Exception):
    """
    Exceção levantada para erros de configuração relacionados à API OpenAI.
    """
    def __init__(self, message: str, details: str = None):
        super().__init__(message)
        self.details = details


def configurar_logging(logger_name: str, log_file_path: str = None) -> logging.Logger:
    """
    Configura um logger nomeado específico para o projeto.
    Cria um diretório 'logs' e um arquivo 'app.log' (ou o especificado) se não existirem.

    Args:
        logger_name (str): O nome do logger a ser configurado (e.g., __name__, 'my_app').
                           É uma boa prática usar `__name__` para loggers de módulos.
        log_file_path (str, optional): Caminho completo para o arquivo de log para este logger.
                                       Se None, usa 'logs/app.log' como padrão.

    Returns:
        logging.Logger: A instância do logger configurado.
    """
    logger_instance = logging.getLogger(logger_name)
    logger_instance.setLevel(logging.DEBUG) # O logger irá processar mensagens a partir do nível DEBUG.
                                          # Os handlers individuais podem filtrar ainda mais.

    # Evita adicionar handlers duplicados se a função for chamada múltiplas vezes para o mesmo logger.
    if not logger_instance.handlers:
        # 1. Handler para console (StreamHandler)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO) # Nível para console: Geralmente, mostra apenas mensagens mais importantes.
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger_instance.addHandler(console_handler)

        # 2. Handler para arquivo (RotatingFileHandler)
        file_log_full_path = log_file_path
        if not file_log_full_path:
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True) # Garante que o diretório 'logs' exista
            file_log_full_path = os.path.join(log_dir, "app.log")
        
        # Garante que o diretório para o arquivo de log especificado exista
        file_log_dir = os.path.dirname(file_log_full_path)
        if file_log_dir and not os.path.exists(file_log_dir):
            os.makedirs(file_log_dir, exist_ok=True)

        # RotatingFileHandler: 10 MB por arquivo, mantém 5 arquivos de backup
        file_handler = RotatingFileHandler(
            filename=file_log_full_path, 
            maxBytes=10 * 1024 * 1024, # 10 MB
            backupCount=5, 
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG) # Nível para arquivo: Captura todos os logs DEBUG ou superior.
        file_handler.setFormatter(formatter)
        logger_instance.addHandler(file_handler)

    return logger_instance

# --- Configuração do Logger Raiz  ---
# Esta função é executada UMA VEZ quando o módulo `logconfig.py` é importado pela primeira vez.

@lru_cache(maxsize=1) # Garante seja executada apenas uma vez
def _configure_root_logger_from_config():
    """
    Configura o logger raiz (root logger) com base nas configurações da classe Config.
    Isso afeta o nível mínimo de logs que o sistema inteiro de logging processará.
    """
    root_logger = logging.getLogger() # Obtém o logger raiz
    try:
        config = Config.get_instance()
        root_logger.setLevel(config.parsed_log_level)
        logger.info(f"Nível de log do root configurado para: {config.LOG_LEVEL_STR} (numérico: {config.parsed_log_level})")
        
    except Exception as e:

        root_logger.setLevel(logging.INFO) # Default para INFO se a config falhar
        logger.error(f"ERRO: Falha ao configurar o logger raiz a partir de Config. Usando INFO como padrão. Detalhes: {e}")
   

_configure_root_logger_from_config()
