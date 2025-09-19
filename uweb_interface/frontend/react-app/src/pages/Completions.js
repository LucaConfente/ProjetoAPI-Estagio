import React, { useState } from 'react';

const Completions = () => {
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [params, setParams] = useState({ temperature: 0.7, max_tokens: 100 });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult('');
    try {
      const res = await fetch('http://localhost:8000/completions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer API_LUCA' },
        body: JSON.stringify({ prompt, ...params })
      });
      const data = await res.json();
      setResult(data.message || data.completion || data.result || 'Sem resposta.');
    } catch (err) {
      setResult('Erro ao conectar ao backend.');
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 500, margin: '40px auto', background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px #0001', padding: 24 }}>
      <h2>Testar Completions</h2>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <textarea
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          placeholder="Digite o prompt..."
          rows={4}
          required
        />
        <div style={{ display: 'flex', gap: 8 }}>
          <label>Temperature:
            <input type="number" step="0.1" min="0" max="2" value={params.temperature}
              onChange={e => setParams(p => ({ ...p, temperature: parseFloat(e.target.value) }))} style={{ width: 60, marginLeft: 4 }} />
          </label>
          <label>Max tokens:
            <input type="number" min="1" max="2048" value={params.max_tokens}
              onChange={e => setParams(p => ({ ...p, max_tokens: parseInt(e.target.value) }))} style={{ width: 60, marginLeft: 4 }} />
          </label>
        </div>
        <button type="submit" disabled={loading || !prompt.trim()}>Enviar</button>
      </form>
      <div style={{ marginTop: 20, minHeight: 40 }}>
        {loading ? 'Carregando...' : result}
      </div>
    </div>
  );
};

export default Completions;
