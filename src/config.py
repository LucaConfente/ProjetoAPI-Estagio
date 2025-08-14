

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError
import os
from dotenv import load_dotenv

class Config(BaseSettings):
    """
    Classe de configuração do projeto OpenAI Integration Hub.
    Carrega as configurações a partir de variáveis de ambiente e/ou arquivo .env.
    """
    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    OPENAI_API_KEY: str 
    OPENAI_BASE_URL: str = "https://api.openai.com/v1" 
    OPENAI_TIMEOUT: int = 10 # Tempo limite para requisiçoes


    @classmethod
    @lru_cache
    def get_instance(cls) -> 'Config':
        """
        Retorna uma instância singleton da configuração.
        A configuração é carregada e validada na primeira chamada e cacheada para reuso.
        """
        try:
            return cls() 
        except ValidationError as e:
            print(f"\nErro de validação na configuração: {e}")
            print("Por favor, verifique se todas as variáveis de ambiente necessárias estão definidas.")
            print("Certifique-se de que OPENAI_API_KEY está presente no seu ambiente ou no arquivo .env.")
            exit(1) 

if __name__ == "__main__":
    # apenas executado se você 'python src/config.py' diretamente ;; especificar caminho 
    print("Testando carregamento de configurações:")
    try:
        settings = Config.get_instance()
        print(f"API Key (primeiros 5 caracteres): {settings.OPENAI_API_KEY[:5]}...")
        print(f"Base URL: {settings.OPENAI_BASE_URL}")
        print(f"Timeout: {settings.OPENAI_TIMEOUT}s")
        print("\nConfigurações carregadas com sucesso!")
    except Exception as e:
        print(f"Não foi possível carregar as configurações. Erro: {e}")

        

###################################################################################################################################

class Configuracao:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Configuracao, cls).__new__(cls)
            cls._instance._carregar_configuracoes()
        return cls._instance

    def _carregar_configuracoes(self):
        load_dotenv() # Carrega variáveis do .env

        # Configurações da API OpenAI
        self.CHAVE_API_OPENAI = os.getenv("OPENAI_API_KEY") or "YOUR_OPENAI_API_KEY" # Valor padrão para desenvolvimento
        self.URL_BASE_OPENAI = os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
        self.TEMPO_LIMITE_OPENAI = int(os.getenv("OPENAI_TIMEOUT", 10))
        self.MAX_TENTATIVAS_OPENAI = int(os.getenv("OPENAI_MAX_RETRIES", 3)) # Adicionado
        self.FATOR_BACKOFF_OPENAI = float(os.getenv("OPENAI_BACKOFF_FACTOR", 0.1)) # Adicionado

        # --- Adicionar configuração de Log ---
        # Mapeia strings para níveis de log do módulo logging
        self.NIVEIS_LOG = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        # Obtém o nível de log do .env ou usa INFO como padrão
        # Garante que o valor padrão seja uma string válida para o mapeamento
        nivel_log_str = os.getenv("LOG_LEVEL", "INFO").upper() 
        self.NIVEL_LOG = self.NIVEIS_LOG.get(nivel_log_str, logging.INFO)


# Importar 'logging' para que o mapeamento de níveis funcione
import logging 