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
      // Detecta se o usuário quer uma imagem (exemplo: começa com /img ou "desenhe" ou "gere uma imagem")
      const isImagePrompt = /(^\/img\b|\bdesenhe\b|\bgere uma imagem\b|\bimagem de\b|\bdraw\b|\bimage of\b)/i.test(input);
      if (isImagePrompt) {
        // Chama o endpoint de imagem
        const imgRes = await fetch('http://localhost:8000/image', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer API_LUCA' },
          body: JSON.stringify({ prompt: input, n: 1, size: '512x512' })
        });
        const imgData = await imgRes.json();
        if (imgData.urls && imgData.urls.length > 0) {
          setMessages((msgs) => [...msgs, { sender: 'bot', text: '', image: imgData.urls[0] }]);
        } else {
          setMessages((msgs) => [...msgs, { sender: 'bot', text: 'Não foi possível gerar a imagem.' }]);
        }
      } else {
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
      }
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
            {msg.image ? (
              <img src={msg.image} alt="Imagem gerada pela IA" style={{ maxWidth: '100%', borderRadius: 12, margin: '8px 0' }} />
            ) : (
              msg.text
            )}
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
