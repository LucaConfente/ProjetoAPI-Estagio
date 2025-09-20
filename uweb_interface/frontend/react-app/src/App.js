
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Chat from './pages/Chat';
import Completions from './pages/Completions';

const Home = () => (
  <div style={{ maxWidth: 600, margin: '40px auto', background: '#fff', borderRadius: 14, boxShadow: '0 4px 24px #0002', padding: 32 }}>
    <h2 style={{ color: '#1976d2', marginBottom: 12 }}>Bem-vindo ao OpenAI Integration Hub</h2>
    <p style={{ fontSize: '1.1rem', marginBottom: 24 }}>
      Esta aplicação integra recursos de IA generativa via API da OpenAI.<br />
      Use o menu acima para acessar o Chat ou testar Completions.
    </p>
    <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
      <div style={{ background: '#e3f2fd', borderRadius: 10, padding: 16, boxShadow: '0 1px 4px #0001' }}>
        <b>💬 Chat:</b> Converse com o modelo GPT-3.5-turbo simulando um assistente virtual inteligente.
      </div>
      <div style={{ background: '#f1f8e9', borderRadius: 10, padding: 16, boxShadow: '0 1px 4px #0001' }}>
        <b>⚡ Completions:</b> Teste prompts de texto (se disponível para sua conta OpenAI).
      </div>
      <div style={{ background: '#fffde7', borderRadius: 10, padding: 16, boxShadow: '0 1px 4px #0001', color: '#795548' }}>
        <b>ℹ️ Dicas:</b>
        <ul style={{ margin: '8px 0 0 18px', fontSize: '1rem' }}>
          <li>Para usar, basta digitar sua mensagem e clicar em Enviar.</li>
          <li>O backend precisa estar rodando para o chat funcionar.</li>
          <li>Consulte a <a href="https://platform.openai.com/docs/api-reference" target="_blank" rel="noopener noreferrer">documentação da OpenAI</a> para exemplos de prompts.</li>
        </ul>
      </div>
    </div>
    <div style={{ marginTop: 32, textAlign: 'center', color: '#888', fontSize: '0.95rem' }}>
      Projeto de Estágio &copy; {new Date().getFullYear()}<br />
      Desenvolvido por LucaConfente
    </div>
  </div>
);

function App() {
  return (
    <Router>
      <nav style={{ display: 'flex', gap: 16, justifyContent: 'center', padding: 16, background: '#1976d2' }}>
        <Link to="/" style={{ color: '#fff', textDecoration: 'none', fontWeight: 'bold' }}>Home</Link>
        <Link to="/chat" style={{ color: '#fff', textDecoration: 'none', fontWeight: 'bold' }}>Chat</Link>
        <Link to="/completions" style={{ color: '#fff', textDecoration: 'none', fontWeight: 'bold' }}>Completions</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/completions" element={<Completions />} />
      </Routes>
    </Router>
  );
}

export default App;
