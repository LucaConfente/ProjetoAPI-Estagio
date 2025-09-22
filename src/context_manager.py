class ContextManager:
    """
    Gerencia o histórico de mensagens para manter o contexto de conversação com o modelo.
    Permite adicionar, recuperar e limpar o contexto.
    """
    def __init__(self, max_length=20):
        self.mensagens = []
        self.max_length = max_length

    def adicionar_mensagem(self, role, content):
        self.mensagens.append({"role": role, "content": content})
        # Mantém apenas as últimas max_length mensagens
        if len(self.mensagens) > self.max_length:
            self.mensagens = self.mensagens[-self.max_length:]

    def get_contexto(self):
        return list(self.mensagens)

    def limpar(self):
        self.mensagens.clear()

if __name__ == "__main__":
    ctx = ContextManager(max_length=3)
    ctx.adicionar_mensagem("user", "Olá")
    ctx.adicionar_mensagem("assistant", "Oi! Como posso ajudar?")
    ctx.adicionar_mensagem("user", "Me conte uma piada.")
    print("Contexto atual:", ctx.get_contexto())
    ctx.limpar()
    print("Contexto após limpar:", ctx.get_contexto())

# -----------------------------------------------------------------------------
#
# Este módulo define a classe ContextManager, responsável por gerenciar o
# histórico de mensagens em uma conversa com o modelo de linguagem. Permite
# adicionar novas mensagens, recuperar o contexto atual (lista de mensagens)
# e limpar o histórico.
#
# Principais pontos:
# - Mantém o contexto de conversas para interações mais naturais com o modelo.
# - Limita o número de mensagens armazenadas (max_length) para evitar excesso de contexto.
# - Métodos simples para adicionar, recuperar e limpar mensagens.
# - Pode ser executado diretamente para testes rápidos do gerenciamento de contexto.
#
# Uso típico:
#   ctx = ContextManager(max_length=10)
#   ctx.adicionar_mensagem("user", "Olá!")
#   contexto = ctx.get_contexto()
#
# Este arquivo é útil para aplicações que precisam manter o histórico de
# interações do usuário com o assistente, garantindo que o modelo tenha
# acesso ao contexto recente da conversa.

