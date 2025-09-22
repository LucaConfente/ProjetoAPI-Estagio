import pytest
import logging
import os
import shutil
import requests
from requests.exceptions import HTTPError
import requests_mock


# Importa a função de configuração de log do módulo src.logconfig
# Assumimos que o diretório raiz do projeto está no sys.path quando o pytest é executado
# (ex: executando 'pytest' na raiz 'ProjetoAPI-Estagio/')
from src.logconfig import configurar_logging

# --- Módulo "Comando" Dummy para Teste ---
# Esta classe simula a lógica de um comando que faria uso do sistema de logging.
class CommandProcessor:
    def __init__(self, command_name: str):
        self.command_name = command_name
        # Obtém um logger configurado especificamente para este processador de comando
        self.logger = configurar_logging(f"command_processor.{command_name}")

    def execute(self, should_succeed: bool = True):
        """
        Simula a execução de um comando, logando seu status.
        """
        self.logger.info(f"Tentando executar comando: '{self.command_name}'")
        if should_succeed:
            self.logger.debug(f"Comando '{self.command_name}' executado com sucesso.")
            return True
        else:
            self.logger.warning(f"Comando '{self.command_name}' encontrou um aviso.")
            self.logger.error(f"Comando '{self.command_name}' falhou na execução.")
            return False

# --- Fixtures e Testes Pytest ---

@pytest.fixture
def algum_fixture(caplog):
    """
    Fixture de exemplo para capturar logs durante os testes.
    """
    caplog.set_level(logging.DEBUG)
    yield caplog


def test_command_execution_success(caplog):
    """
    Testa se a execução bem-sucedida de um comando loga as mensagens esperadas.
    """
    command_name = "comando_sucesso"
    processor = CommandProcessor(command_name)

    # Define o nível de captura do caplog para DEBUG para capturar todas as mensagens
    caplog.set_level(logging.DEBUG)

    result = processor.execute(should_succeed=True)

    assert result is True
    
    # Verifica se as mensagens esperadas estão nos logs capturados
    assert f"Tentando executar comando: '{command_name}'" in caplog.text
    assert f"Comando '{command_name}' executado com sucesso." in caplog.text

    # Verifica os detalhes dos registros de log
    info_found = False
    debug_found = False
    for record in caplog.records:
        assert record.name == f"command_processor.{command_name}" # Verifica o nome do logger
        if record.levelname == "INFO" and "Tentando executar comando" in record.message:
            info_found = True
        if record.levelname == "DEBUG" and "executado com sucesso" in record.message:
            debug_found = True
    
    assert info_found
    assert debug_found


def test_command_execution_failure(caplog):
    """
    Testa se a execução com falha de um comando loga mensagens de aviso e erro.
    """
    command_name = "comando_falha"
    processor = CommandProcessor(command_name)

    # Define o nível de captura do caplog para DEBUG
    caplog.set_level(logging.DEBUG)

    result = processor.execute(should_succeed=False)

    assert result is False
    
    # Verifica se as mensagens esperadas estão nos logs capturados
    assert f"Tentando executar comando: '{command_name}'" in caplog.text
    assert f"Comando '{command_name}' encontrou um aviso." in caplog.text
    assert f"Comando '{command_name}' falhou na execução." in caplog.text

    # Verifica os detalhes dos registros de log, incluindo níveis WARNING e ERROR
    warning_found = False
    error_found = False
    for record in caplog.records:
        assert record.name == f"command_processor.{command_name}"
        if record.levelname == "WARNING" and "encontrou um aviso" in record.message:
            warning_found = True
        if record.levelname == "ERROR" and "falhou na execução" in record.message:
            error_found = True
    
    assert warning_found
    assert error_found


# testes/test_commands.py
import os
import shutil
import logging
import pytest 
from src.logconfig import configurar_logging 

def test_log_file_creation(tmp_path): # Adicione tmp_path como argumento
    """
    Verifica se o diretório e o arquivo de log são criados
    quando a função `configurar_logging` é chamada, usando um diretório temporário.
    """
    # Define o caminho do arquivo de log dentro do diretório temporário
    log_file_path = tmp_path / "app.log"

    # Chama configurar_logging com o caminho temporário
    dummy_logger = configurar_logging("logger_para_teste_arquivo", log_file_path=str(log_file_path))

    # Verifica se o arquivo de log foi criado no caminho temporário
    assert log_file_path.exists()
    assert log_file_path.is_file()

    # Opcional: Verifica se algo foi escrito no log
    # dummy_logger.info("Mensagem de teste")
    # with open(log_file_path, 'r') as f:
    #     content = f.read()
    #     assert "Mensagem de teste" in content

    # Limpeza: Fecha os handlers do logger criado para este teste.
    # O tmp_path cuida da exclusão do diretório.
    for handler in dummy_logger.handlers[:]:
        dummy_logger.removeHandler(handler)
        handler.close()
    
    # Também é bom limpar handlers do logger root que possam ter sido adicionados
    # se configurar_logging afeta o logger root.
    for handler in logging.root.handlers[:]:
        if isinstance(handler, logging.FileHandler) and handler.baseFilename == str(log_file_path.resolve()):
            logging.root.removeHandler(handler)
            handler.close()


def test_mock_http_error_429(requests_mock):
    # Mocka resposta 429 levantando HTTPError
    response_429 = requests.Response()
    response_429.status_code = 429
    response_429._content = b'{"error": {"message": "Limite de taxa excedido", "type": "rate_limit_error"}}'
    response_429.reason = "Too Many Requests"

    ponto_final_teste = "endpoint_de_teste"
    url_base = "http://localhost/api"

    # Mocka a URL para levantar HTTPError
    requests_mock.get(f"{url_base}/{ponto_final_teste}", exc=HTTPError(response=response_429))

    # Exemplo de chamada que vai levantar o erro
    with pytest.raises(HTTPError) as excinfo:
        requests.get(f"{url_base}/{ponto_final_teste}")

    assert excinfo.value.response.status_code == 429
    assert excinfo.value.response.reason == "Too Many Requests"


from src.exceptions import OpenAIRetryError  # Adicione o import correto conforme o local da definição

# -----------------------------------------------------------------------------
#
# Este arquivo contém testes unitários para comandos e para o sistema de logging
# do projeto, utilizando pytest. Testa tanto a execução de comandos simulados
# quanto a criação e funcionamento de arquivos de log, além de cenários de erro
# HTTP mockados.
#
# Principais pontos:
# - Testa o fluxo de sucesso e falha de comandos, verificando logs gerados.
# - Garante que arquivos e diretórios de log são criados corretamente.
# - Usa mocks para simular erros HTTP (ex: 429 Too Many Requests).
# - Utiliza fixtures do pytest para capturar logs e isolar ambiente de teste.
#
# Uso típico:
#   pytest testes/test_commands.py
#
# Este arquivo é importante para garantir que comandos e logging funcionem
# corretamente, prevenindo regressões e facilitando a manutenção do sistema.


