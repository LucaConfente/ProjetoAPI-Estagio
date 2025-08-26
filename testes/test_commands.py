# main.py
from src.logconfig import configurar_logging

def main():
    # Configura o logger
    logger = configurar_logging("aplicacao_principal")
    
    # Testa diferentes níveis de log
    logger.debug("Mensagem de debug")
    logger.info("Aplicação iniciada com sucesso")
    logger.warning("Configuração padrão sendo usada")
    logger.error("Simulando um erro")
    logger.critical("Erro crítico simulado")
    
    print("Verifique o console e o arquivo logs/app.log")

if __name__ == "__main__":
    main()