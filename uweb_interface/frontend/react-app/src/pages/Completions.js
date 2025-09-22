import React, { useState } from 'react';
import './Completions.css';

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
  setResult(data.response || data.message || data.completion || data.result || 'Sem resposta.');
    } catch (err) {
      setResult('Erro ao conectar ao backend.');
    }
    setLoading(false);
  };

  return (
    <div className="completions-container card">
      <h2 className="completions-title">Testar Completions</h2>
      <form className="completions-form" onSubmit={handleSubmit}>
        <textarea
          className="completions-textarea"
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          placeholder="Digite o prompt..."
          rows={4}
          required
        />
        <div className="completions-params">
          <label>Temperature:  
            { /* Input para o parâmetro 'temperature' do completions:
              - Permite ao usuário escolher um valor entre 0 e 2 (step 0.1), conforme limites da OpenAI.
              - Quanto menor o valor, mais determinística e repetitiva a resposta; quanto maior, mais criativa e variada.
              - O valor é controlado pelo estado React (params.temperature) e atualizado a cada mudança no input. */}
              
            <input type="number" step="0.1" min="0" max="2" value={params.temperature}
              onChange={e => setParams(p => ({ ...p, temperature: parseFloat(e.target.value) }))} />
          </label>
          <label>Max tokens:
            {/* Input para o parâmetro 'max_tokens' do completions:
             - Permite ao usuário definir o número máximo de tokens (palavras/frases curtas) que a resposta pode ter.
             - O valor mínimo é 1 e o máximo é 2048, conforme limites da OpenAI.
             - Valores maiores permitem respostas mais longas; valores menores limitam a resposta.
             - O valor é controlado pelo estado React (params.max_tokens) e atualizado a cada mudança no input. */}

            <input type="number" min="1" max="2048" value={params.max_tokens}
              onChange={e => setParams(p => ({ ...p, max_tokens: parseInt(e.target.value) }))} />
          </label>
        </div>
        <button className="completions-btn" type="submit" disabled={loading || !prompt.trim()}>Enviar</button>
      </form>
      <div className="completions-result">
        {loading ? 'Carregando...' : result}
      </div>
    </div>
  );
};

export default Completions;

