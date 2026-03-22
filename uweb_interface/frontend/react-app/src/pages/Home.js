import React from 'react';
import { Link } from 'react-router-dom';

const cards = [
  {
    icon: '◈',
    title: 'Chat',
    badge: 'GPT-4o',
    badgeColor: 'accent',
    description: 'Converse com um assistente virtual inteligente em tempo real. Suporte a histórico de mensagens e contexto de conversa.',
    path: '/chat',
    cta: 'Abrir Chat',
    delay: '0.1s',
  },
  {
    icon: '⚡',
    title: 'Completions',
    badge: 'text-davinci',
    badgeColor: 'amber',
    description: 'Teste prompts de texto e ajuste parâmetros como temperatura e max tokens para explorar o comportamento do modelo.',
    path: '/completions',
    cta: 'Explorar',
    delay: '0.2s',
  },
];

const stats = [
  { label: 'Modelo', value: 'GPT-4o', mono: true },
  { label: 'Latência', value: '~800ms', mono: true },
  { label: 'Status', value: 'Online', green: true },
];

export default function Home() {
  return (
    <div style={styles.page}>
      {/* Hero */}
      <section style={styles.hero}>
        <div style={styles.heroInner}>
          <div style={styles.chip}>
            <span style={styles.chipDot} />
            Projeto de Estágio · 2026
          </div>

          <h1 style={styles.heroTitle}>
            OpenAI
            <br />
            <span style={styles.heroAccent}>Integration</span>
            <span style={styles.heroGhost}> Hub</span>
          </h1>

          <p style={styles.heroSubtitle}>
            Plataforma de integração com a API da OpenAI.
            Explore modelos generativos via interface web com backend Python.
          </p>

          {/* Stats row */}
          <div style={styles.statsRow}>
            {stats.map((s, i) => (
              <div key={i} style={styles.statItem}>
                <span style={styles.statLabel}>{s.label}</span>
                <span style={{
                  ...styles.statValue,
                  ...(s.mono ? { fontFamily: 'var(--mono)' } : {}),
                  ...(s.green ? { color: 'var(--green)' } : {}),
                }}>
                  {s.green && <span style={styles.greenDot} />}
                  {s.value}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Decorative grid lines */}
        <div style={styles.gridLines} aria-hidden>
          {[...Array(5)].map((_, i) => (
            <div key={i} style={{ ...styles.gridLine, top: `${15 + i * 18}%` }} />
          ))}
        </div>
      </section>

      {/* Cards */}
      <section style={styles.cardsSection}>
        <div style={styles.cardsGrid}>
          {cards.map((card) => (
            <FeatureCard key={card.title} {...card} />
          ))}
        </div>
      </section>

      {/* Info box */}
      <section style={styles.infoSection}>
        <div style={styles.infoBox}>
          <div style={styles.infoIcon}>ℹ</div>
          <div>
            <p style={styles.infoTitle}>Como usar</p>
            <ul style={styles.infoList}>
              <li>Digite sua mensagem e clique em <strong>Enviar</strong></li>
              <li>O backend Python precisa estar rodando na porta <code style={styles.code}>8000</code></li>
              <li>Consulte a{' '}
                <a href="https://platform.openai.com/docs" target="_blank" rel="noopener noreferrer" style={styles.link}>
                  documentação da OpenAI
                </a>
                {' '}para exemplos de prompts
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={styles.footer}>
        <span style={styles.footerText}>
          Desenvolvido por{' '}
          <a
            href="https://github.com/LucaConfente"
            target="_blank"
            rel="noopener noreferrer"
            style={styles.footerLink}
          >
            LucaConfente
          </a>
        </span>
        <span style={styles.footerDivider}>·</span>
        <span style={styles.footerText}>Projeto de Estágio © 2026</span>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, badge, badgeColor, description, path, cta, delay }) {
  const [hovered, setHovered] = React.useState(false);

  const badgeStyles = {
    accent: { background: 'var(--accent-soft)', color: 'var(--accent)' },
    amber: { background: 'var(--amber-soft)', color: 'var(--amber)' },
  };

  return (
    <div
      style={{
        ...styles.card,
        ...(hovered ? styles.cardHovered : {}),
        animationDelay: delay,
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Top row */}
      <div style={styles.cardTop}>
        <span style={styles.cardIcon}>{icon}</span>
        <span style={{ ...styles.badge, ...badgeStyles[badgeColor] }}>
          {badge}
        </span>
      </div>

      <h2 style={styles.cardTitle}>{title}</h2>
      <p style={styles.cardDesc}>{description}</p>

      <Link to={path} style={{ ...styles.cardBtn, ...(hovered ? styles.cardBtnHovered : {}) }}>
        {cta}
        <span style={styles.btnArrow}>→</span>
      </Link>

      {/* Accent line */}
      <div style={{ ...styles.cardLine, ...(hovered ? styles.cardLineHovered : {}) }} />
    </div>
  );
}

const styles = {
  page: {
    maxWidth: '860px',
    margin: '0 auto',
    padding: '0 1.5rem 4rem',
    animation: 'fadeUp 0.6s ease forwards',
  },

  // Hero
  hero: {
    position: 'relative',
    padding: '5rem 0 3rem',
    overflow: 'hidden',
  },
  heroInner: { position: 'relative', zIndex: 1 },

  chip: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.45rem',
    padding: '0.3rem 0.8rem',
    borderRadius: '99px',
    background: 'rgba(255,255,255,0.04)',
    border: '1px solid rgba(255,255,255,0.08)',
    fontSize: '0.72rem',
    color: 'var(--text-secondary)',
    fontFamily: 'var(--mono)',
    letterSpacing: '0.03em',
    marginBottom: '1.6rem',
    animation: 'fadeIn 0.4s ease',
  },
  chipDot: {
    display: 'inline-block',
    width: '5px', height: '5px',
    borderRadius: '50%',
    background: 'var(--accent)',
    boxShadow: '0 0 6px var(--accent)',
  },

  heroTitle: {
    fontSize: 'clamp(2.4rem, 6vw, 4rem)',
    fontWeight: 700,
    letterSpacing: '-0.03em',
    lineHeight: 1.05,
    marginBottom: '1.2rem',
    color: 'var(--text)',
    animation: 'fadeUp 0.5s ease 0.05s both',
  },
  heroAccent: {
    background: 'linear-gradient(135deg, var(--accent), var(--accent2))',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
  },
  heroGhost: {
    color: 'var(--text-muted)',
  },

  heroSubtitle: {
    fontSize: '1rem',
    color: 'var(--text-secondary)',
    lineHeight: 1.7,
    maxWidth: '480px',
    marginBottom: '2rem',
    fontWeight: 300,
    animation: 'fadeUp 0.5s ease 0.1s both',
  },

  statsRow: {
    display: 'flex',
    gap: '0',
    animation: 'fadeUp 0.5s ease 0.15s both',
  },
  statItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.2rem',
    padding: '0.8rem 1.4rem',
    borderRight: '1px solid var(--border)',
    '&:first-child': { paddingLeft: 0 },
  },
  statLabel: {
    fontSize: '0.7rem',
    color: 'var(--text-muted)',
    fontFamily: 'var(--mono)',
    letterSpacing: '0.06em',
    textTransform: 'uppercase',
  },
  statValue: {
    fontSize: '0.9rem',
    fontWeight: 600,
    color: 'var(--text)',
    display: 'flex',
    alignItems: 'center',
    gap: '0.4rem',
  },
  greenDot: {
    display: 'inline-block',
    width: '6px', height: '6px',
    borderRadius: '50%',
    background: 'var(--green)',
    boxShadow: '0 0 6px var(--green)',
  },

  // Grid lines decoration
  gridLines: {
    position: 'absolute',
    inset: 0,
    pointerEvents: 'none',
    zIndex: 0,
    overflow: 'hidden',
  },
  gridLine: {
    position: 'absolute',
    left: 0, right: 0,
    height: '1px',
    background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.025), transparent)',
  },

  // Cards
  cardsSection: { paddingBottom: '2rem' },
  cardsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '1rem',
  },

  card: {
    position: 'relative',
    padding: '1.8rem',
    borderRadius: '14px',
    background: 'var(--card)',
    border: '1px solid var(--border)',
    transition: 'transform 0.25s ease, border-color 0.25s, box-shadow 0.25s',
    overflow: 'hidden',
    animation: 'fadeUp 0.6s ease both',
    cursor: 'default',
  },
  cardHovered: {
    transform: 'translateY(-4px)',
    borderColor: 'rgba(110,86,255,0.3)',
    boxShadow: '0 20px 60px rgba(0,0,0,0.4), 0 0 40px rgba(110,86,255,0.08)',
  },

  cardTop: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '1rem',
  },
  cardIcon: {
    fontSize: '1.4rem',
    color: 'var(--accent)',
    lineHeight: 1,
  },
  badge: {
    fontSize: '0.68rem',
    fontFamily: 'var(--mono)',
    fontWeight: 500,
    padding: '0.2rem 0.55rem',
    borderRadius: '99px',
    letterSpacing: '0.03em',
  },
  cardTitle: {
    fontSize: '1.25rem',
    fontWeight: 700,
    letterSpacing: '-0.02em',
    marginBottom: '0.6rem',
    color: 'var(--text)',
  },
  cardDesc: {
    fontSize: '0.85rem',
    color: 'var(--text-secondary)',
    lineHeight: 1.65,
    marginBottom: '1.5rem',
    fontWeight: 300,
  },

  cardBtn: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.4rem',
    padding: '0.5rem 1rem',
    borderRadius: '8px',
    background: 'var(--accent-soft)',
    border: '1px solid rgba(110,86,255,0.2)',
    color: 'var(--accent)',
    fontSize: '0.82rem',
    fontWeight: 500,
    textDecoration: 'none',
    transition: 'background 0.2s, border-color 0.2s',
    letterSpacing: '0.01em',
  },
  cardBtnHovered: {
    background: 'rgba(110,86,255,0.2)',
    borderColor: 'rgba(110,86,255,0.4)',
  },
  btnArrow: {
    fontSize: '0.9rem',
    transition: 'transform 0.2s',
  },

  cardLine: {
    position: 'absolute',
    bottom: 0, left: 0,
    height: '2px',
    width: '0%',
    background: 'linear-gradient(90deg, var(--accent), var(--accent2))',
    transition: 'width 0.4s ease',
    borderRadius: '0 0 14px 14px',
  },
  cardLineHovered: { width: '100%' },

  // Info
  infoSection: { marginBottom: '2rem' },
  infoBox: {
    display: 'flex',
    gap: '1rem',
    padding: '1.2rem 1.5rem',
    borderRadius: '12px',
    background: 'rgba(86,207,255,0.04)',
    border: '1px solid rgba(86,207,255,0.1)',
    animation: 'fadeUp 0.6s ease 0.3s both',
  },
  infoIcon: {
    fontSize: '1rem',
    color: 'var(--accent2)',
    flexShrink: 0,
    marginTop: '1px',
  },
  infoTitle: {
    fontSize: '0.82rem',
    fontWeight: 600,
    color: 'var(--text)',
    marginBottom: '0.5rem',
  },
  infoList: {
    listStyle: 'none',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.3rem',
  },
  code: {
    fontFamily: 'var(--mono)',
    fontSize: '0.78rem',
    background: 'rgba(255,255,255,0.07)',
    padding: '0.1rem 0.35rem',
    borderRadius: '4px',
    color: 'var(--text)',
  },
  link: {
    color: 'var(--accent2)',
    textDecoration: 'none',
    borderBottom: '1px solid rgba(86,207,255,0.3)',
  },

  // Footer
  footer: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.6rem',
    paddingTop: '1rem',
    borderTop: '1px solid var(--border)',
  },
  footerText: {
    fontSize: '0.75rem',
    color: 'var(--text-muted)',
  },
  footerLink: {
    color: 'var(--text-secondary)',
    textDecoration: 'none',
    transition: 'color 0.2s',
  },
  footerDivider: {
    color: 'var(--text-muted)',
    fontSize: '0.75rem',
  },
};
