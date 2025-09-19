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
      // Chamada ao backend (ajuste a URL se necessário)
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
          <div key={idx} className={`chat-msg ${msg.sender}`}>{msg.text}</div>
        ))}
        {loading && <div className="chat-msg bot">Carregando...</div>}
      </div>
      <form className="chat-form" onSubmit={handleSend}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Digite sua mensagem..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>Enviar</button>
      </form>
    </div>
  );
};

export default Chat;
