
import pytest
import logging
import os
import shutil

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

@pytest.fixture(scope="module", autouse=True)
def cleanup_logs_fixture():
    """
    Fixture para limpar o diretório de logs e resetar os handlers de log
    antes e depois da execução dos testes neste módulo.
    Isso garante que os testes de log sejam isolados e não interfiram uns nos outros.
    """
    log_dir = "logs"
    log_file = os.path.join(log_dir, "app.log")

    # Limpa handlers de todos os loggers para garantir um estado limpo
    # Crucial para testes de logging consistentes.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    for logger_name in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        logger.propagate = True # Reseta a propagação para o padrão (True)

    # Limpa o diretório de logs se existir
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    os.makedirs(log_dir, exist_ok=True) # Recria o diretório

    yield # Executa os testes

    # Opcional: Limpar o diretório de logs após todos os testes do módulo
    # if os.path.exists(log_dir):
    #     shutil.rmtree(log_dir)


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


def test_log_file_creation():
    """
    Verifica se o diretório e o arquivo de log são criados
    quando a função `configurar_logging` é chamada.
    """
    log_dir = "logs"
    log_file_path = os.path.join(log_dir, "app.log")

    # Garante que o diretório de logs está limpo antes deste teste específico
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)

    # Chama configurar_logging para um logger dummy para acionar a criação do arquivo
    dummy_logger = configurar_logging("logger_para_teste_arquivo")
    dummy_logger.info("Esta mensagem deve estar no arquivo de log.")

    assert os.path.exists(log_dir)
    assert os.path.isdir(log_dir)
    assert os.path.exists(log_file_path)
    assert os.path.isfile(log_file_path)

    # Verifica se a mensagem foi escrita no arquivo
    with open(log_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Esta mensagem deve estar no arquivo de log." in content




# # main.py
# from src.logconfig import configurar_logging

# def main():
#     # Configura o logger
#     logger = configurar_logging("aplicacao_principal")
    
#     # Testa diferentes níveis de log
#     logger.debug("Mensagem de debug")
#     logger.info("Aplicação iniciada com sucesso")
#     logger.warning("Configuração padrão sendo usada")
#     logger.error("Simulando um erro")
#     logger.critical("Erro crítico simulado")
    
#     print("Verifique o console e o arquivo logs/app.log")

# if __name__ == "__main__":
#     main()