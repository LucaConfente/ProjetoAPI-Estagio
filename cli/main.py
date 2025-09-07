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


# Comando para modo interativo de chat
@cli.command()
@click.option('--model', default='gpt-3.5-turbo', help='Modelo OpenAI a ser usado.')
@click.pass_obj
def interativo(app_config: Config, model: str):
    """Inicia um chat interativo com o modelo OpenAI."""
    from src.chat import ChatModule
    import json
    import datetime
    import colorama
    colorama.init(autoreset=True)
    click.echo(f"Modo interativo iniciado (modelo: {model}). Comandos: /sair, /limpar, /ajuda, /salvar, /carregar, /historico")
    chat_module = ChatModule()
    contexto = []
    historico = []
    def print_ajuda():
        click.echo("\nComandos disponíveis:")
        click.echo("  /sair      - Sair do modo interativo")
        click.echo("  /limpar    - Limpar a conversa atual")
        click.echo("  /ajuda     - Mostrar esta ajuda")
        click.echo("  /salvar    - Salvar conversa atual em arquivo")
        click.echo("  /carregar  - Carregar conversa de arquivo")
        click.echo("  /historico - Exibir histórico desta sessão\n")
    LIMITE_CONTEXTO = 10  # Enviar apenas as últimas 10 mensagens para o modelo
    while True:
        user_input = input("Você: ")
        if user_input.strip().startswith("/"):
            comando = user_input.strip().lower()
            if comando in ["/sair", "/exit", "/quit"]:
                click.echo("Encerrando modo interativo.")
                break
            elif comando == "/limpar":
                contexto.clear()
                click.echo("Conversa limpa.")
            elif comando == "/ajuda":
                print_ajuda()
            elif comando == "/salvar":
                nome = f"conversa_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(nome, "w", encoding="utf-8") as f:
                    json.dump(contexto, f, ensure_ascii=False, indent=2)
                click.echo(f"Conversa salva em {nome}.")
            elif comando == "/carregar":
                nome = input("Arquivo para carregar: ")
                try:
                    with open(nome, "r", encoding="utf-8") as f:
                        contexto.clear()
                        contexto.extend(json.load(f))
                    click.echo(f"Conversa carregada de {nome}.")
                except Exception as e:
                    click.echo(f"Erro ao carregar: {e}", err=True)
            elif comando == "/historico":
                if not historico:
                    click.echo("Nenhuma conversa registrada nesta sessão.")
                else:
                    click.echo("\nHistórico desta sessão:")
                    for i, conv in enumerate(historico, 1):
                        click.echo(f"[{i}] {conv}")
            else:
                click.echo("Comando não reconhecido. Use /ajuda para ver os comandos.")
            continue
        contexto.append({"role": "user", "content": user_input})
        # Limitar o contexto enviado para o modelo
        contexto_envio = contexto[-LIMITE_CONTEXTO:]
        click.echo(colorama.Fore.YELLOW + "Aguardando resposta..." + colorama.Style.RESET_ALL)
        try:
            resposta = chat_module.criar_conversa(mensagens=contexto_envio, modelo=model)
            resposta_texto = resposta['choices'][0]['message']['content']
            contexto.append({"role": "assistant", "content": resposta_texto})
            historico.append(f"Você: {user_input}\nOpenAI: {resposta_texto}")
            click.echo(colorama.Fore.GREEN + "OpenAI:" + colorama.Style.RESET_ALL)
            click.echo(colorama.Fore.CYAN + resposta_texto + colorama.Style.RESET_ALL)
        except Exception as e:
            click.echo(f"Erro: {e}", err=True)


# Comando para exibir configurações atuais
@cli.command()
@click.pass_obj
def config(app_config: Config):
    """Exibe as configurações atuais da aplicação."""
    click.echo("Configurações atuais:")
    for k, v in vars(app_config).items():
        click.echo(f"{k}: {v}")

# Comando para testar conexão com a API (valida a chave)
@cli.command()
@click.pass_obj
def test_connection(app_config: Config):
    """Testa se a chave da API está funcionando."""
    import requests
    try:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {app_config.OPENAI_API_KEY}"}
        )
        if response.status_code == 200:
            click.echo("Conexão bem-sucedida! Sua chave está válida.")
        else:
            click.echo(f"Falha na conexão. Código: {response.status_code} - {response.text}", err=True)
    except Exception as e:
        click.echo(f"Erro ao testar conexão: {e}", err=True)

# Comando para listar modelos disponíveis
@cli.command()
@click.pass_obj
def listar_modelos(app_config: Config):
    """Lista os modelos disponíveis na OpenAI para sua chave."""
    import requests
    try:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {app_config.OPENAI_API_KEY}"}
        )
        if response.status_code == 200:
            modelos = response.json().get("data", [])
            click.echo("Modelos disponíveis:")
            for modelo in modelos:
                click.echo(f"- {modelo.get('id')}")
        else:
            click.echo(f"Erro ao listar modelos. Código: {response.status_code} - {response.text}", err=True)
    except Exception as e:
        click.echo(f"Erro ao listar modelos: {e}", err=True)

if __name__ == "__main__":
    cli()
