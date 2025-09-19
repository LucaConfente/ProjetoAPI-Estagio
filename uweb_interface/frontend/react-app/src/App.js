
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Chat from './pages/Chat';
import Completions from './pages/Completions';

const Home = () => (
  <div style={{ maxWidth: 500, margin: '40px auto', background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px #0001', padding: 24 }}>
    <h2>Bem-vindo ao OpenAI Integration Hub</h2>
    <p>Escolha uma funcionalidade no menu acima.</p>
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
