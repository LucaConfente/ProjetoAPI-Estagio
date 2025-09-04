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
