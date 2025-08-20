# cli/main.py
import sys
import os
from pathlib import Path # manipulação de caminhos mais robusta

# --- Funções de Configuração (idealmente em um módulo separado como cli/config.py) ---
# Para fins de demonstração, vamos mantê-las aqui por enquanto.
from dotenv import load_dotenv
import openai
from src.logconfig import configurar_logging

def configurar_ambiente_e_paths():
    """
    Configura o sys.path e carrega as variáveis de ambiente.
    Retorna o objeto logger configurado.
    """
    # Ajuste do sys.path
    current_script_dir = Path(__file__).parent.absolute()
    project_root_dir = current_script_dir.parent

    # Adiciona o diretório raiz do projeto ao sys.path
    if str(project_root_dir) not in sys.path:
        sys.path.insert(0, str(project_root_dir))
    
    # Carrega as variáveis do .env
    load_dotenv() 
    
    # Configura a chave da API da OpenAI 
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("ERRO: Variável de ambiente OPENAI_API_KEY não encontrada.")
        sys.exit(1) # Sai do programa com erro

    # Configura o logger
    logger = configurar_logging("aplicacao_principal")
    return logger





# main 
def main():
    """
    Função principal do programa OpenAI Integration Hub CLI.
    Gerencia a inicialização, configuração e execução de testes de logging.
    """
    logger = None # Inicializa logger como None

    try:
        # 1. Configurar ambiente e obter o logger
        logger = configurar_ambiente_e_paths()
        logger.info("Ambiente e logger configurados com sucesso.")

        # 2. Testando níveis de logging
        logger.debug("Mensagem de debug")
        logger.info("Aplicação iniciada com sucesso")
        logger.warning("Configuração padrão sendo usada")
        logger.error("Simulando um erro")
        logger.critical("Erro crítico simulado")

        print("✅ Verifique o console e o arquivo logs/app.log")
        logger.info("Testes de logging concluídos.")

        # 3. Aqui você adicionaria a lógica principal da sua CLI
        # Por exemplo:
        # from core_library.chat_module import ChatModule
        # chat_module = ChatModule(openai.api_key)
        # response = chat_module.send_message("Olá, como você está?")
        # print(f"Resposta da IA: {response}")

        # Retorna 0 para indicar sucesso na execução
        sys.exit(0)

    except Exception as e:
        # Tratamento de erros genérico para a função main
        if logger:
            logger.critical(f"Ocorreu um erro crítico na aplicação: {e}", exc_info=True)
        else:
            print(f" Erro crítico antes do logger ser configurado: {e}")
        sys.exit(1) # Retorna 1 para indicar falha na execução

# --- Ponto de Entrada do Script ---
if __name__ == "__main__":
    main() # Chama a função principal quando o script é executado diretamente