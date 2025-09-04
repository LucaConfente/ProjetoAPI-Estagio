import sys
import os
from pathlib import Path
import click
import openai 


current_script_dir = Path(__file__).parent.absolute()
project_root_dir = current_script_dir.parent
if str(project_root_dir) not in sys.path:
    sys.path.insert(0, str(project_root_dir))

import src.logconfig


from src.config import Config
from src.chat import ChatModule
from src.exceptions import (
    OpenAIClientError, OpenAIAuthenticationError, OpenAIRateLimitError,
    OpenAIConfigurationError, OpenAIValidationError,
)


logger = src.logconfig.configurar_logging(__name__)


@click.group()
@click.pass_context # Permite passar um objeto de contexto para os subcomandos
def cli(ctx):
    """
    OpenAI Integration Hub CLI.
    Gerencia a inicialização, configuração e execução de comandos.
    """
    try:
        # Permite sobrescrever a chave via variável de ambiente no terminal
        api_key_env = os.environ.get("OPENAI_API_KEY")
        app_config = Config.get_instance()
        if api_key_env:
            app_config.OPENAI_API_KEY = api_key_env
        openai.api_key = app_config.OPENAI_API_KEY

        ctx.obj = app_config

        logger.info("CLI inicializada e configuração da aplicação carregada com sucesso.")
        logger.debug("Mensagem de debug da inicialização da CLI.")

    except OpenAIConfigurationError as e:
        logger.critical(f"Erro de Configuração Crítico durante a inicialização da CLI: {e.message}", exc_info=True)
        click.echo(f"ERRO CRÍTICO: Falha na configuração da aplicação. {e.message}", err=True)
        if e.config_key:
            click.echo(f"Por favor, verifique a configuração de '{e.config_key}'.", err=True)
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Ocorreu um erro crítico e inesperado durante a inicialização da CLI: {e}", exc_info=True)
        click.echo(f"ERRO CRÍTICO: Ocorreu um erro inesperado durante a inicialização: {e}", err=True)
        sys.exit(1)


## define o comando chat
@cli.command()
@click.option("--message", required=True, help="A mensagem para enviar ao modelo.")
@click.option("--model", default="gpt-3.5-turbo", help="O modelo OpenAI a ser usado.")
@click.pass_obj # Permite acessar o objeto passado pelo comando pai (ctx.obj)
def chat(app_config: Config, message: str, model: str): # Adiciona 'app_config' como parâmetro
    """Envia uma mensagem para o modelo de chat da OpenAI."""
    try:
        # O ChatModule deve ser capaz de usar a chave API que já foi definida globalmente
        # ou, idealmente, receber a app_config ou a chave diretamente.
        chat_module = ChatModule() 
        logger.info(f"Iniciando comando 'chat' com mensagem: '{message}' e modelo: '{model}'")
        
        response = chat_module.criar_conversa(mensagens=[{"role": "user", "content": message}], modelo=model)
        
        click.echo(f"Resposta: {response['choices'][0]['message']['content']}")
        logger.info("Comando 'chat' executado com sucesso.")

    # Tratamento de exceções específicas da OpenAI
    except OpenAIConfigurationError as e:
        logger.error(f"Erro de Configuração: {e.message}", exc_info=True)
        click.echo(f"Erro de Configuração: {e.message}", err=True)
        if e.config_key:
            click.echo(f"Por favor, verifique a configuração de '{e.config_key}'.", err=True)
        sys.exit(1)
    except OpenAIAuthenticationError as e:
        logger.error(f"Erro de Autenticação: {e.message}", exc_info=True)
        click.echo(f"Erro de Autenticação: {e.message}", err=True)
        click.echo("Verifique sua chave da API OpenAI.", err=True)
        sys.exit(1)
    except OpenAIRateLimitError as e:
        logger.error(f"Erro de Limite de Requisições: {e.message}", exc_info=True)
        click.echo(f"Erro de Limite de Requisições: {e.message}", err=True)
        click.echo("Você excedeu o limite de requisições. Tente novamente mais tarde.", err=True)
        sys.exit(1)
    except OpenAIValidationError as e:
        logger.error(f"Erro de Validação: {e.message}", exc_info=True)
        click.echo(f"Erro de Validação: {e.message}", err=True)
        if e.field:
            click.echo(f"Campo inválido: '{e.field}'.", err=True)
        sys.exit(1)
    except OpenAIClientError as e:
        logger.error(f"Ocorreu um erro inesperado da OpenAI: {e.message}", exc_info=True)
        click.echo(f"Ocorreu um erro inesperado da OpenAI: {e.message}", err=True)
        sys.exit(1)
    except Exception as e: # Captura qualquer outra exceção não tratada
        logger.critical(f"Ocorreu um erro crítico e inesperado no comando 'chat': {e}", exc_info=True)
        click.echo(f"Ocorreu um erro crítico e inesperado: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('endpoint')
@click.option('--params', default=None, help='Parâmetros de consulta em JSON (opcional).')
@click.pass_obj
def obter(app_config: Config, endpoint: str, params: str):
    """Realiza uma requisição GET para o endpoint informado."""
    from src.http_client import ClienteHttpOpenAI
    import json
    cliente = ClienteHttpOpenAI()
    try:
        params_dict = json.loads(params) if params else None
        resposta = cliente.obter(endpoint, params=params_dict)
        click.echo(f"Resposta: {resposta}")
    except Exception as e:
        click.echo(f"Erro ao executar GET: {e}", err=True)

@cli.command()
@click.argument('endpoint')
@click.option('--dados', default=None, help='Dados para POST em JSON.')
@click.pass_obj
def enviar(app_config: Config, endpoint: str, dados: str):
    """Realiza uma requisição POST para o endpoint informado."""
    from src.http_client import ClienteHttpOpenAI
    import json
    cliente = ClienteHttpOpenAI()
    try:
        dados_dict = json.loads(dados) if dados else None
        resposta = cliente.enviar(endpoint, dados=dados_dict)
        click.echo(f"Resposta: {resposta}")
    except Exception as e:
        click.echo(f"Erro ao executar POST: {e}", err=True)

if __name__ == "__main__":
    cli()