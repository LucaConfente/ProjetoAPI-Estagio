import React, { useState } from 'react';
import './Chat.css';

const Chat = () => {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Olá! Como posso ajudar você hoje?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMessage = { sender: 'user', text: input };
    setMessages((msgs) => [...msgs, userMessage]);
    setInput('');
    setLoading(true);
    try {
      // Chamada ao backend para texto
      const body = {
        messages: [
          { role: 'user', content: input }
        ],
        model: 'gpt-3.5-turbo'
      };
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer API_LUCA' },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      setMessages((msgs) => [...msgs, { sender: 'bot', text: data.response || data.message || JSON.stringify(data) || 'Erro na resposta.' }]);
    } catch (err) {
      setMessages((msgs) => [...msgs, { sender: 'bot', text: 'Erro ao conectar ao backend.' }]);
    }
    setLoading(false);
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-msg ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
        {loading && <div className="chat-msg bot">Carregando...</div>}
      </div>
      <form className="chat-form" onSubmit={handleSend} autoComplete="off">
        <div className="input-wrapper">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Digite sua mensagem..."
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            title="Enviar"
            className="send-arrow-btn"
            tabIndex={-1}
          >
            <span className="arrow-icon">&#8594;</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default Chat;

// ----------------------------------------------------------------------------------------

// Este arquivo define o componente Chat do frontend React.
// Função principal:
// - Permite ao usuário conversar com o modelo de IA via backend FastAPI.
// - Usa useState para controlar mensagens, input do usuário e estado de carregamento.
// - handleSend envia a mensagem do usuário para o backend (endpoint /chat), recebe a resposta e atualiza o histórico de mensagens.
// - Exibe todas as mensagens (usuário e bot) em ordem, com estilização diferenciada.
// - O botão de envio é desabilitado enquanto carrega ou se o input estiver vazio.
// - apenas chat de texto. Tentativa de geração de imagens foi removida.
// - O componente é totalmente controlado por estado React, garantindo atualização automática da interface.
//
// Este arquivo faz parte da interface web do projeto e é responsável por toda a experiência de chat com IA no frontend.
