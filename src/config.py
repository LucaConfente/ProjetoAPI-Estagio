from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError, Field
import logging
import os
from dotenv import load_dotenv

# Importe sua exceção personalizada para erros de configuração
from src.exceptions import OpenAIConfigurationError

# Configuração básica de logging para o próprio módulo config.py
# O nível do logger root será ajustado dinamicamente por Config.get_instance()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carrega as variáveis de ambiente do arquivo .env, se existir
load_dotenv()

class Config(BaseSettings):
    LOG_LEVEL_STR: str = "INFO"  # Usado para compatibilidade com logconfig. Pode ser ajustado conforme necessário.
    """
    Classe de configuração do projeto OpenAI Integration Hub.
    Carrega as configurações a partir de variáveis de ambiente e/ou arquivo .env
    usando Pydantic Settings.
    """
    
    # Configuração do Pydantic Settings para carregar do .env
    # 'extra='ignore'' permite que variáveis não definidas na classe sejam ignoradas no .env
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # --- Configurações da API OpenAI ---
    OPENAI_API_KEY: str = Field(..., description="Chave da API OpenAI. Obrigatória.")
    OPENAI_BASE_URL: str = Field("https://api.openai.com/v1", description="URL base para a API OpenAI.")
    OPENAI_TIMEOUT: int = Field(10, description="Tempo limite em segundos para requisições à API OpenAI.")

    # --- Configurações de Retry e Backoff ---
    OPENAI_MAX_RETRIES: int = Field(3, description="Número máximo de tentativas para requisições à API OpenAI.")
    OPENAI_BACKOFF_FACTOR: float = Field(0.5, description="Fator de backoff exponencial para retries da API OpenAI.")

    # --- Configurações de Logging ---
    # Mapeamento de strings de nível de log para constantes de logging
    _LOG_LEVEL_MAPPING = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    # Nível de log geral para o logger root e console
    LOG_LEVEL: str = Field("INFO", description="Nível de log para a aplicação (DEBUG, INFO, WARNING, ERROR, CRITICAL).")
    
    # Configurações para o arquivo de log rotativo
    LOG_DIR: str = Field("logs", description="Diretório para os arquivos de log.")
    LOG_FILE_NAME: str = Field("app.log", description="Nome do arquivo de log principal.")
    LOG_FILE_LEVEL: str = Field("DEBUG", description="Nível mínimo de log para o arquivo de log.")
    LOG_FILE_MAX_BYTES: int = Field(10 * 1024 * 1024, description="Tamanho máximo de um arquivo de log antes da rotação (bytes).") # 10 MB
    LOG_FILE_BACKUP_COUNT: int = Field(5, description="Número de arquivos de log de backup a serem mantidos.")
    LOG_FORMAT: str = Field('%(asctime)s - %(name)s - %(levelname)s - %(message)s', description="String de formato para mensagens de log.")

    @property
    def parsed_log_level(self) -> int:
        """
        Retorna o nível de log geral (para console/root) configurado como um inteiro da biblioteca `logging`.
        Se a string for inválida, retorna `logging.INFO` como padrão.
        """
        return self._LOG_LEVEL_MAPPING.get(self.LOG_LEVEL.upper(), logging.INFO)

    @property
    def parsed_log_file_level(self) -> int:
        """
        Retorna o nível de log para o arquivo de log configurado como um inteiro da biblioteca `logging`.
        Se a string for inválida, retorna `logging.DEBUG` como padrão.
        """
        return self._LOG_LEVEL_MAPPING.get(self.LOG_FILE_LEVEL.upper(), logging.DEBUG)

    @classmethod
    @lru_cache
    def get_instance(cls) -> 'Config':
        """
        Retorna uma instância singleton da configuração.
        A configuração é carregada e validada na primeira chamada e cacheada para reuso.
        O nível de log do logger root também é configurado aqui.
        """
        try:
            instance = cls()
            # Configura o nível do logger root com base na configuração carregada
            # Isso afeta todos os loggers que não têm um nível específico definido
            logging.getLogger().setLevel(instance.parsed_log_level)
            logger.info(f"Nível de log do root configurado para: {instance.LOG_LEVEL.upper()} (numérico: {instance.parsed_log_level})")
            return instance
        except ValidationError as e:
            logger.error(f"Erro de validação na configuração: {e}")
            logger.error("Por favor, verifique se todas as variáveis de ambiente necessárias estão definidas.")
            logger.error("Certifique-se de que 'OPENAI_API_KEY' está presente no seu ambiente ou no arquivo .env.")
            # Levanta sua exceção personalizada para que o chamador possa tratá-la
            raise OpenAIConfigurationError(
                "Falha ao carregar configurações críticas. Verifique OPENAI_API_KEY e outras variáveis de ambiente.",
                details=str(e)
            ) from e # Adiciona a exceção original para rastreamento
        except Exception as e:
            logger.critical(f"Erro inesperado ao carregar configurações: {e}", exc_info=True)
            raise OpenAIConfigurationError(
                "Erro inesperado durante o carregamento das configurações.",
                details=str(e)
            ) from e

# Bloco para testar o carregamento das configurações quando o script é executado diretamente
if __name__ == "__main__":
    print("Iniciando teste de carregamento de configurações...")
    try:
        settings = Config.get_instance()
        print("\n--- Configurações Carregadas ---")
        print(f"OPENAI_API_KEY (primeiros 5 caracteres): {settings.OPENAI_API_KEY[:5]}...")
        print(f"OPENAI_BASE_URL: {settings.OPENAI_BASE_URL}")
        print(f"OPENAI_TIMEOUT: {settings.OPENAI_TIMEOUT}s")
        print(f"OPENAI_MAX_RETRIES: {settings.OPENAI_MAX_RETRIES}")
        print(f"OPENAI_BACKOFF_FACTOR: {settings.OPENAI_BACKOFF_FACTOR}")
        print(f"LOG_LEVEL (Console/Root): {settings.LOG_LEVEL} (parsed: {settings.parsed_log_level})")
        print(f"LOG_DIR: {settings.LOG_DIR}")
        print(f"LOG_FILE_NAME: {settings.LOG_FILE_NAME}")
        print(f"LOG_FILE_LEVEL: {settings.LOG_FILE_LEVEL} (parsed: {settings.parsed_log_file_level})")
        print(f"LOG_FILE_MAX_BYTES: {settings.LOG_FILE_MAX_BYTES} bytes")
        print(f"LOG_FILE_BACKUP_COUNT: {settings.LOG_FILE_BACKUP_COUNT}")
        print(f"LOG_FORMAT: {settings.LOG_FORMAT}")
        print("\nConfigurações carregadas com sucesso!")

        # Exemplo de uso do logger após configuração
        logger.debug("Esta é uma mensagem de debug (se o nível do root permitir).")
        logger.info("Esta é uma mensagem de informação.")
        logger.warning("Esta é uma mensagem de aviso.")

    except OpenAIConfigurationError as e:
        print(f"Erro de configuração: {e.message}")
        if e.details:
            print(f"Detalhes: {e.details}")
        exit(1) # Sai do programa se a configuração crítica falhar
    except Exception as e:
        print(f"Erro inesperado ao carregar as configurações: {e}")
        exit(1)
