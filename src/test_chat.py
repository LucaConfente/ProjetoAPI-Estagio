
import pytest
from unittest.mock import MagicMock, patch

# Importe a classe que você quer testar
from src.chat import ChatModule

# Importe a exceção que você espera que seja levantada
from src.exceptions import OpenAIValidationError

# --- Testes para o método criar_conversa ---

def test_criar_conversa_sucesso():
    """
    Testa se criar_conversa chama corretamente o cliente_http.enviar com dados válidos.
    """
    # Mock do ClienteHttpOpenAI e seu método 'enviar'
    # Usamos patch para substituir ClienteHttpOpenAI globalmente durante o teste
    with patch('src.chat.ClienteHttpOpenAI') as MockClienteHttpOpenAI:
        # Configura o mock para retornar uma instância de ClienteHttpOpenAI
        mock_cliente_instance = MockClienteHttpOpenAI.return_value
        # Configura o retorno do método 'enviar' do mock
        mock_cliente_instance.enviar.return_value = {"choices": [{"message": {"content": "Resposta de teste."}}]}

        chat_module = ChatModule()
        
        mensagens_validas = [{"role": "user", "content": "Olá, como você está?"}]
        modelo_valido = "gpt-4"

        # Chama o método que queremos testar
        resposta = chat_module.criar_conversa(mensagens_validas, modelo_valido)

        # Verifica se o construtor de ClienteHttpOpenAI foi chamado
        MockClienteHttpOpenAI.assert_called_once()
        
        # Verifica se o método 'enviar' foi chamado com os argumentos corretos
        mock_cliente_instance.enviar.assert_called_once_with(
            "chat/completions",
            dados={"model": modelo_valido, "messages": mensagens_validas}
        )
        
        # Verifica se a resposta é a esperada
        assert resposta == {"choices": [{"message": {"content": "Resposta de teste."}}]}


def test_criar_conversa_mensagens_nao_lista():
    """
    Testa se OpenAIValidationError é levantada quando 'mensagens' não é uma lista.
    """
    chat_module = ChatModule()
    with pytest.raises(OpenAIValidationError, match="lista não vazia"):
        chat_module.criar_conversa("string invalida", "gpt-3.5-turbo")

def test_criar_conversa_mensagens_lista_vazia():
    """
    Testa se OpenAIValidationError é levantada quando 'mensagens' é uma lista vazia.
    """
    chat_module = ChatModule()
    with pytest.raises(OpenAIValidationError, match="lista não vazia"):
        chat_module.criar_conversa([], "gpt-3.5-turbo")

def test_criar_conversa_mensagens_formato_invalido():
    """
    Testa se OpenAIValidationError é levantada quando mensagens não têm 'role'/'content'.
    """
    chat_module = ChatModule()
 
    with pytest.raises(OpenAIValidationError, match="dicionário com 'role' e 'content'"):
        chat_module.criar_conversa([{"role": "user", "text": "Isso está errado"}], "gpt-3.5-turbo")
    

    with pytest.raises(OpenAIValidationError, match="dicionário com 'role' e 'content'"):
        chat_module.criar_conversa([{"content": "Isso também está errado"}], "gpt-3.5-turbo")

def test_criar_conversa_modelo_nao_string():
    """
    Testa se OpenAIValidationError é levantada quando 'modelo' não é uma string.
    """
    chat_module = ChatModule()
    with pytest.raises(OpenAIValidationError, match="string não vazia"):
        chat_module.criar_conversa([{"role": "user", "content": "Olá"}], 123)

def test_criar_conversa_modelo_string_vazia():
    """
    Testa se OpenAIValidationError é levantada quando 'modelo' é uma string vazia.
    """
    chat_module = ChatModule()
    with pytest.raises(OpenAIValidationError, match="string não vazia"):
        chat_module.criar_conversa([{"role": "user", "content": "Olá"}], "")

# --- Testes para o construtor (opcional, mas boa prática) ---


def test_chat_module_inicializacao():
    """
    Testa se o ChatModule é inicializado corretamente e se ClienteHttpOpenAI é instanciado.
    """
    with patch('src.chat.ClienteHttpOpenAI') as MockClienteHttpOpenAI:
        chat_module = ChatModule()
        MockClienteHttpOpenAI.assert_called_once() # Verifica se ClienteHttpOpenAI foi instanciado

        assert chat_module.cliente_http is MockClienteHttpOpenAI.return_value