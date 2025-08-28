import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import openai
import click 

# Importa o logger e módulos específicos
from src.logconfig import configurar_logging
from src.chat import ChatModule # Ou o módulo que você está usando
from src.exceptions import (
    OpenAIClientError, OpenAIAuthenticationError, OpenAIRateLimitError,
    OpenAIConfigurationError, OpenAIValidationError,
)

# Inicializa o logger como None globalmente para que possa ser acessado
# por diferentes partes do script após a configuração
logger = None

def configurar_ambiente_e_paths_e_logger():
    """
    Configura o sys.path, carrega as variáveis de ambiente e configura o logger.
    Retorna o objeto logger configurado.
    """
    global logger # Indica que estamos usando a variável global logger

    # Ajuste do sys.path
    current_script_dir = Path(__file__).parent.absolute()
    project_root_dir = current_script_dir.parent

    # Adiciona o diretório raiz do projeto ao sys.path
    if str(project_root_dir) not in sys.path:
        sys.sys.path.insert(0, str(project_root_dir))

    # Carrega as variáveis do .env
    load_dotenv()

    # Configura a chave da API da OpenAI
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("ERRO: Variável de ambiente OPENAI_API_KEY não encontrada. Por favor, defina-a.")
        sys.exit(1) # Sai do programa com erro

    # Configura o logger APÓS a checagem da API_KEY,
    # para que erros críticos iniciais sejam visíveis antes do logging completo
    logger = configurar_logging("aplicacao_principal")
    return logger

# A função principal da CLI será o ponto de entrada
@click.group()
def cli():
    """
    OpenAI Integration Hub CLI.
    Gerencia a inicialização, configuração e execução de comandos.
    """
    global logger # Garante que estamos usando o logger global

    # Esta lógica de inicialização será executada uma vez quando qualquer comando da CLI for chamado
    if logger is None: # Garante que a configuração ocorra apenas uma vez
        try:
            logger = configurar_ambiente_e_paths_e_logger()
            logger.info("Ambiente e logger configurados com sucesso para a CLI.")

            # Opcional: Você pode manter os testes de logging aqui se quiser que apareçam
            # sempre que a CLI for inicializada.
            logger.debug("Mensagem de debug CLI")
            logger.info("CLI iniciada com sucesso")
            # ... outros testes de logging
        except Exception as e:
            # Tratamento de erro se a configuração falhar antes do logger estar totalmente disponível
            if logger: # Se o logger foi parcialmente configurado
                logger.critical(f"Ocorreu um erro crítico durante a inicialização da CLI: {e}", exc_info=True)
            else: # Se o logger não pôde ser configurado de forma alguma
                print(f"ERRO CRÍTICO: Não foi possível configurar o ambiente ou o logger: {e}")
            sys.exit(1)


@cli.command()
@click.option("--message", required=True, help="A mensagem para enviar ao modelo.")
@click.option("--model", default="gpt-3.5-turbo", help="O modelo OpenAI a ser usado.")
def chat(message, model):
    """Envia uma mensagem para o modelo de chat da OpenAI."""
    global logger # Acessa o logger configurado globalmente
    try:
        # ChatModule não precisa da API key explicitamente se openai.api_key já foi definido globalmente
        chat_module = ChatModule()
        logger.info(f"Iniciando comando 'chat' com mensagem: '{message}' e modelo: '{model}'")
        response = chat_module.criar_conversa(mensagens=[{"role": "user", "content": message}], modelo=model)
        click.echo(f"Resposta: {response['choices'][0]['message']['content']}")
        logger.info("Comando 'chat' executado com sucesso.")

    except OpenAIConfigurationError as e:
        if logger: logger.error(f"Erro de Configuração: {e.message}", exc_info=True)
        click.echo(f"Erro de Configuração: {e.message}", err=True)
        if e.config_key:
            click.echo(f"Por favor, verifique a configuração de '{e.config_key}'.", err=True)
        sys.exit(1)
    except OpenAIAuthenticationError as e:
        if logger: logger.error(f"Erro de Autenticação: {e.message}", exc_info=True)
        click.echo(f"Erro de Autenticação: {e.message}", err=True)
        click.echo("Verifique sua chave da API OpenAI.", err=True)
        sys.exit(1)
    except OpenAIRateLimitError as e:
        if logger: logger.error(f"Erro de Limite de Requisições: {e.message}", exc_info=True)
        click.echo(f"Erro de Limite de Requisições: {e.message}", err=True)
        click.echo("Você excedeu o limite de requisições. Tente novamente mais tarde.", err=True)
        sys.exit(1)
    except OpenAIValidationError as e:
        if logger: logger.error(f"Erro de Validação: {e.message}", exc_info=True)
        click.echo(f"Erro de Validação: {e.message}", err=True)
        if e.field:
            click.echo(f"Campo inválido: '{e.field}'.", err=True)
        sys.exit(1)
    except OpenAIClientError as e: # Captura qualquer outra exceção base do cliente
        if logger: logger.error(f"Ocorreu um erro inesperado da OpenAI: {e.message}", exc_info=True)
        click.echo(f"Ocorreu um erro inesperado da OpenAI: {e.message}", err=True)
        sys.exit(1)
    except Exception as e: # Captura qualquer outra exceção não tratada
        if logger: logger.critical(f"Ocorreu um erro crítico e inesperado no comando 'chat': {e}", exc_info=True)
        else: click.echo(f"Ocorreu um erro crítico e inesperado: {e}", err=True) # Fallback se logger não estiver disponível
        sys.exit(1)


# Ponto de Entrada Único do Script
if __name__ == "__main__":
    cli() # Chama a função principal da CLI