import React, { useState } from 'react';

const PRESETS = [
  { label: 'Criativo', temp: 0.9, tokens: 300 },
  { label: 'Balanceado', temp: 0.5, tokens: 200 },
  { label: 'Preciso', temp: 0.1, tokens: 150 },
];

export default function Completions() {
  const [prompt, setPrompt] = useState('');
  const [temperature, setTemperature] = useState(0.5);
  const [maxTokens, setMaxTokens] = useState(200);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [meta, setMeta] = useState(null);

  const send = async () => {
    const text = prompt.trim();
    if (!text || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setMeta(null);

    const start = Date.now();

    try {
      const response = await fetch('http://localhost:8000/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer API_LUCA',
        },
        body: JSON.stringify({
          prompt: text,
          temperature,
          max_tokens: maxTokens,
        }),
      });

      if (!response.ok) throw new Error(`Erro ${response.status}`);

      const data = await response.json();
      const elapsed = ((Date.now() - start) / 1000).toFixed(2);

      setResult(data.response || data.completion || data.text || JSON.stringify(data, null, 2));
      setMeta({ elapsed, tokens: data.usage?.total_tokens });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const applyPreset = (preset) => {
    setTemperature(preset.temp);
    setMaxTokens(preset.tokens);
  };

  const clear = () => {
    setPrompt('');
    setResult(null);
    setMeta(null);
    setError(null);
  };

  const tempColor = temperature <= 0.3 ? '#56cfff' : temperature <= 0.6 ? '#6e56ff' : '#f5a623';

  return (
    <div style={styles.page}>
      {/* Header */}
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Completions</h1>
          <p style={styles.subtitle}>Teste prompts e ajuste os parâmetros do modelo</p>
        </div>
        <button style={styles.clearBtn} onClick={clear}>↺ Limpar</button>
      </div>

      <div style={styles.layout}>
        {/* Left: Prompt + Output */}
        <div style={styles.main}>
          <div style={styles.section}>
            <label style={styles.label}>Prompt</label>
            <textarea
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              placeholder="Digite o prompt aqui..."
              style={styles.textarea}
              rows={6}
              disabled={loading}
            />
          </div>

          <button
            onClick={send}
            disabled={!prompt.trim() || loading}
            style={{
              ...styles.sendBtn,
              ...(!prompt.trim() || loading ? styles.sendBtnDisabled : styles.sendBtnActive),
            }}
          >
            {loading ? (
              <><span style={styles.spinner} />Gerando...</>
            ) : (
              <>⚡ Enviar Prompt</>
            )}
          </button>

          {(result || error || loading) && (
            <div style={styles.outputSection}>
              <div style={styles.outputHeader}>
                <span style={styles.label}>Resultado</span>
                {meta && (
                  <div style={styles.metaRow}>
                    <span style={styles.metaItem}>
                      <span style={styles.metaDot} />
                      {meta.elapsed}s
                    </span>
                    {meta.tokens && (
                      <span style={styles.metaItem}>{meta.tokens} tokens</span>
                    )}
                  </div>
                )}
              </div>

              {loading && (
                <div style={styles.loadingOutput}>
                  <div style={styles.shimmer} />
                  <div style={{ ...styles.shimmer, width: '75%' }} />
                  <div style={{ ...styles.shimmer, width: '55%' }} />
                </div>
              )}

              {result && !loading && (
                <div style={styles.output}>
                  <pre style={styles.outputText}>{result}</pre>
                  <button
                    style={styles.copyBtn}
                    onClick={() => navigator.clipboard.writeText(result)}
                  >
                    ⎘ Copiar
                  </button>
                </div>
              )}

              {error && (
                <div style={styles.error}>
                  <span>⚠</span><span>Erro: {error}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right: Controls */}
        <aside style={styles.sidebar}>
          {/* Presets */}
          <div style={styles.sideSection}>
            <span style={styles.sideLabel}>Presets</span>
            <div style={styles.presets}>
              {PRESETS.map(p => (
                <button key={p.label} style={styles.presetBtn} onClick={() => applyPreset(p)}>
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Temperature */}
          <div style={styles.sideSection}>
            <div style={styles.paramHeader}>
              <span style={styles.sideLabel}>Temperature</span>
              <span style={{ ...styles.paramValue, color: tempColor }}>
                {temperature.toFixed(1)}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={temperature}
              onChange={e => setTemperature(parseFloat(e.target.value))}
              style={styles.slider}
            />
            <div style={styles.sliderLabels}>
              <span>Preciso</span>
              <span>Criativo</span>
            </div>
            <p style={styles.paramDesc}>
              {temperature <= 0.3
                ? 'Respostas determinísticas e focadas'
                : temperature <= 0.6
                ? 'Equilíbrio entre precisão e criatividade'
                : 'Saídas mais variadas e criativas'}
            </p>
          </div>

          {/* Max tokens */}
          <div style={styles.sideSection}>
            <div style={styles.paramHeader}>
              <span style={styles.sideLabel}>Max Tokens</span>
              <span style={{ ...styles.paramValue, color: 'var(--accent)' }}>{maxTokens}</span>
            </div>
            <input
              type="range"
              min="50"
              max="1000"
              step="10"
              value={maxTokens}
              onChange={e => setMaxTokens(parseInt(e.target.value))}
              style={styles.slider}
            />
            <div style={styles.sliderLabels}>
              <span>50</span>
              <span>500</span>
            </div>
            <p style={styles.paramDesc}>
              Mínimo de 50 tokens para evitar respostas cortadas no meio da frase.
            </p>
          </div>

          {/* Info */}
          <div style={styles.infoCard}>
            <p style={styles.infoTitle}>ℹ Sobre Tokens</p>
            <p style={styles.infoText}>
              ~1 token ≈ 4 caracteres. Use pelo menos 150 tokens para respostas completas.
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}

const styles = {
  page: { maxWidth: '1000px', margin: '0 auto', padding: '2rem 1.5rem 4rem', animation: 'fadeUp 0.5s ease' },
  header: { display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '2rem' },
  title: { fontSize: '1.4rem', fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--text)', marginBottom: '0.3rem' },
  subtitle: { fontSize: '0.82rem', color: 'var(--text-muted)' },
  clearBtn: { padding: '0.4rem 0.8rem', borderRadius: '8px', background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-muted)', fontSize: '0.78rem', cursor: 'pointer', fontFamily: 'var(--font)' },
  layout: { display: 'grid', gridTemplateColumns: '1fr 260px', gap: '1.5rem', alignItems: 'start' },
  main: { display: 'flex', flexDirection: 'column', gap: '1rem' },
  sidebar: { display: 'flex', flexDirection: 'column', gap: '0.75rem' },
  section: {},
  label: { display: 'block', fontSize: '0.72rem', fontFamily: 'var(--mono)', color: 'var(--text-muted)', letterSpacing: '0.07em', textTransform: 'uppercase', marginBottom: '0.6rem' },
  textarea: { width: '100%', padding: '1rem', borderRadius: '12px', background: 'var(--card)', border: '1px solid var(--border)', color: 'var(--text)', fontSize: '0.88rem', fontFamily: 'var(--font)', resize: 'vertical', outline: 'none', lineHeight: 1.65, caretColor: 'var(--accent)', minHeight: '140px' },
  sendBtn: { display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', width: '100%', padding: '0.8rem', borderRadius: '12px', border: 'none', fontSize: '0.88rem', fontWeight: 600, fontFamily: 'var(--font)', cursor: 'pointer', transition: 'all 0.2s' },
  sendBtnActive: { background: 'var(--accent)', color: '#fff', boxShadow: '0 4px 20px rgba(110,86,255,0.35)' },
  sendBtnDisabled: { background: 'rgba(255,255,255,0.04)', color: 'var(--text-muted)', cursor: 'not-allowed' },
  outputSection: { borderRadius: '12px', background: 'var(--card)', border: '1px solid var(--border)', overflow: 'hidden' },
  outputHeader: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 1rem', borderBottom: '1px solid var(--border)' },
  metaRow: { display: 'flex', gap: '0.75rem' },
  metaItem: { fontSize: '0.7rem', fontFamily: 'var(--mono)', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' },
  metaDot: { display: 'inline-block', width: '5px', height: '5px', borderRadius: '50%', background: 'var(--green)' },
  loadingOutput: { padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' },
  shimmer: { height: '14px', borderRadius: '4px', background: 'linear-gradient(90deg, rgba(255,255,255,0.04) 25%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.04) 75%)', backgroundSize: '200% 100%', animation: 'shimmer 1.5s infinite', width: '100%' },
  output: { position: 'relative', padding: '1rem' },
  outputText: { fontFamily: 'var(--mono)', fontSize: '0.82rem', color: 'var(--text)', whiteSpace: 'pre-wrap', wordBreak: 'break-word', lineHeight: 1.7 },
  copyBtn: { marginTop: '0.75rem', padding: '0.35rem 0.7rem', borderRadius: '6px', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', color: 'var(--text-secondary)', fontSize: '0.72rem', fontFamily: 'var(--font)', cursor: 'pointer' },
  error: { display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '1rem', color: '#f87171', fontSize: '0.82rem' },
  sideSection: { padding: '1rem', borderRadius: '12px', background: 'var(--card)', border: '1px solid var(--border)' },
  sideLabel: { display: 'block', fontSize: '0.68rem', fontFamily: 'var(--mono)', color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '0.6rem' },
  presets: { display: 'flex', gap: '0.4rem', flexWrap: 'wrap' },
  presetBtn: { padding: '0.3rem 0.7rem', borderRadius: '6px', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', color: 'var(--text-secondary)', fontSize: '0.75rem', fontFamily: 'var(--font)', cursor: 'pointer' },
  paramHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' },
  paramValue: { fontFamily: 'var(--mono)', fontSize: '0.9rem', fontWeight: 600 },
  slider: { width: '100%', appearance: 'none', WebkitAppearance: 'none', height: '3px', borderRadius: '99px', background: 'rgba(255,255,255,0.08)', outline: 'none', cursor: 'pointer', accentColor: 'var(--accent)' },
  sliderLabels: { display: 'flex', justifyContent: 'space-between', marginTop: '0.35rem', fontSize: '0.65rem', color: 'var(--text-muted)', fontFamily: 'var(--mono)' },
  paramDesc: { marginTop: '0.6rem', fontSize: '0.74rem', color: 'var(--text-muted)', lineHeight: 1.5 },
  infoCard: { padding: '0.9rem', borderRadius: '10px', background: 'rgba(86,207,255,0.04)', border: '1px solid rgba(86,207,255,0.1)' },
  infoTitle: { fontSize: '0.75rem', fontWeight: 600, color: 'var(--accent2)', marginBottom: '0.35rem' },
  infoText: { fontSize: '0.73rem', color: 'var(--text-muted)', lineHeight: 1.55 },
  spinner: { display: 'inline-block', width: '13px', height: '13px', border: '2px solid rgba(255,255,255,0.2)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin 0.7s linear infinite' },
};
