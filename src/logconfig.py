import logging
import os
from logging.handlers import RotatingFileHandler # Importa para rotação de logs
from .config import Config # <-- CORRIGIDO: Importa a classe Config

def configurar_logging(nome_logger="app_logger"):
    """
    Configura e retorna um objeto logger.

    Args:
        nome_logger (str): O nome do logger a ser configurado.

    Returns:
        logging.Logger: A instância do logger configurado.
    """
    # CORRIGIDO: Obtém a instância singleton da configuração
    config = Config.get_instance() 

    # CORRIGIDO: Obtém os níveis de log e formato da configuração
    nivel_log_console = config.parsed_log_level # Nível para o console
    nivel_log_arquivo = config.parsed_log_file_level # Nível para o arquivo
    log_format = config.LOG_FORMAT
    log_dir = config.LOG_DIR
    log_file_name = config.LOG_FILE_NAME
    log_file_max_bytes = config.LOG_FILE_MAX_BYTES
    log_file_backup_count = config.LOG_FILE_BACKUP_COUNT

    # Cria o logger
    logger = logging.getLogger(nome_logger)
    # O nível do logger principal deve ser o mais baixo entre os handlers para garantir que todas as mensagens sejam processadas
    logger.setLevel(min(nivel_log_console, nivel_log_arquivo)) 

    # Impede a duplicação de mensagens pelos handlers se a função for chamada múltiplas vezes
    # para o mesmo nome de logger.
    if not logger.handlers:
        # Formato das mensagens de log
        formatter = logging.Formatter(log_format)

        # Handler para console (saída padrão)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(nivel_log_console) # Nível mínimo para o console
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Handler para arquivo (com rotação para produção)
        # Cria um diretório de logs se não existir
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, log_file_name)
        
        file_handler = RotatingFileHandler( # <-- CORRIGIDO: Usando RotatingFileHandler
            log_file_path,
            maxBytes=log_file_max_bytes, # <-- Da configuração
            backupCount=log_file_backup_count, # <-- Da configuração
            encoding='utf-8'
        )
        file_handler.setLevel(nivel_log_arquivo) # <-- Da configuração
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Opcional: Se você estiver usando loggers hierárquicos e quiser evitar
        # que as mensagens sejam passadas para o logger pai (e talvez duplicadas
        # pelo handler do logger pai), você pode definir propagate como False.
        # logger.propagate = False

    return logger