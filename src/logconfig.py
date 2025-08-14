

import logging
import os
from .config import Configuracao # Importa a sua classe de configuração

def configurar_logging(nome_logger="app_logger"):
    """
    Configura e retorna um objeto logger.

    Args:
        nome_logger (str): O nome do logger a ser configurado.

    Returns:
        logging.Logger: A instância do logger configurado.
    """
    config = Configuracao.obter_instancia()

    # Obtém o nível de log da configuração
    nivel_log = config.NIVEL_LOG

    # Cria o logger
    logger = logging.getLogger(nome_logger)
    logger.setLevel(nivel_log)

    # Impede que handlers dupliquem mensagens se a função for chamada múltiplas vezes
    if not logger.handlers:
        # Formato das mensagens de log
        # Exemplo: 2023-10-27 10:30:00,123 - INFO - meu_modulo - Mensagem de log
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )

        # Handler para console (saída padrão)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(nivel_log) # Nível mínimo para o console
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Handler para arquivo (opcional, bom para produção)
        # Cria um diretório de logs se não existir
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "app.log")
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG) # Geralmente DEBUG para arquivo, para ter tudo
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
