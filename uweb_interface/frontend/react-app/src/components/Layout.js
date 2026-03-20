import React, { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';

const navLinks = [
  { path: '/', label: 'Home' },
  { path: '/chat', label: 'Chat' },
  { path: '/completions', label: 'Completions' },
];

export default function Layout({ children }) {
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <div style={styles.root}>
      {/* Ambient blobs */}
      <div style={styles.blob1} />
      <div style={styles.blob2} />

      {/* Navbar */}
      <nav style={{ ...styles.nav, ...(scrolled ? styles.navScrolled : {}) }}>
        <Link to="/" style={styles.brand}>
          <span style={styles.brandDot} />
          <span style={styles.brandText}>AI<span style={styles.brandAccent}>Hub</span></span>
        </Link>

        <div style={styles.navLinks}>
          {navLinks.map(({ path, label }) => {
            const active = location.pathname === path;
            return (
              <Link
                key={path}
                to={path}
                style={{
                  ...styles.navLink,
                  ...(active ? styles.navLinkActive : {}),
                }}
              >
                {label}
                {active && <span style={styles.navLinkBar} />}
              </Link>
            );
          })}
        </div>

        <div style={styles.navBadge}>
          <span style={styles.statusDot} />
          <span style={styles.statusText}>OPENAI</span>
        </div>
      </nav>

      {/* Content */}
      <main style={styles.main}>
        {children}
      </main>
    </div>
  );
}

const styles = {
  root: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    position: 'relative',
    overflow: 'hidden',
  },

  blob1: {
    position: 'fixed',
    width: '700px',
    height: '700px',
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(110,86,255,0.07) 0%, transparent 70%)',
    top: '-300px',
    left: '-200px',
    filter: 'blur(60px)',
    pointerEvents: 'none',
    zIndex: 0,
    animation: 'drift1 18s ease-in-out infinite alternate',
  },

  blob2: {
    position: 'fixed',
    width: '600px',
    height: '600px',
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(86,207,255,0.05) 0%, transparent 70%)',
    bottom: '-250px',
    right: '-150px',
    filter: 'blur(80px)',
    pointerEvents: 'none',
    zIndex: 0,
  },

  nav: {
    position: 'sticky',
    top: 0,
    zIndex: 100,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 2rem',
    height: '58px',
    background: 'rgba(7, 7, 16, 0.7)',
    borderBottom: '1px solid rgba(255,255,255,0.05)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    transition: 'border-color 0.3s, background 0.3s',
    animation: 'slideDown 0.5s ease',
  },

  navScrolled: {
    background: 'rgba(7, 7, 16, 0.92)',
    borderBottomColor: 'rgba(255,255,255,0.08)',
  },

  brand: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.55rem',
    textDecoration: 'none',
    userSelect: 'none',
  },

  brandDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: 'var(--accent)',
    boxShadow: '0 0 12px var(--accent)',
    animation: 'blink 3s ease-in-out infinite',
    display: 'block',
  },

  brandText: {
    fontFamily: 'var(--font)',
    fontWeight: 700,
    fontSize: '1rem',
    letterSpacing: '-0.01em',
    color: 'var(--text)',
  },

  brandAccent: {
    color: 'var(--accent)',
  },

  navLinks: {
    display: 'flex',
    gap: '0.1rem',
    position: 'absolute',
    left: '50%',
    transform: 'translateX(-50%)',
  },

  navLink: {
    position: 'relative',
    padding: '0.4rem 0.85rem',
    borderRadius: '7px',
    fontSize: '0.82rem',
    fontWeight: 500,
    color: 'var(--text-secondary)',
    textDecoration: 'none',
    transition: 'color 0.2s, background 0.2s',
    letterSpacing: '0.01em',
  },

  navLinkActive: {
    color: 'var(--text)',
    background: 'rgba(255,255,255,0.05)',
  },

  navLinkBar: {
    position: 'absolute',
    bottom: '2px',
    left: '50%',
    transform: 'translateX(-50%)',
    width: '16px',
    height: '2px',
    borderRadius: '99px',
    background: 'var(--accent)',
    display: 'block',
  },

  navBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.4rem',
    padding: '0.25rem 0.7rem',
    borderRadius: '99px',
    background: 'rgba(0, 255, 145, 0.08)',
    border: '1px solid rgba(0, 0, 0, 0.15)',
  },

  statusDot: {
    width: '6px',
    height: '6px',
    borderRadius: '50%',
    background: 'var(--green)',
    boxShadow: '0 0 6px var(--green)',
    display: 'block',
    animation: 'blink 2s ease-in-out infinite',
  },

  statusText: {
    fontSize: '0.72rem',
    fontWeight: 500,
    color: 'var(--green)',
    fontFamily: 'var(--mono)',
    letterSpacing: '0.05em',
  },

  main: {
    flex: 1,
    position: 'relative',
    zIndex: 1,
  },
};
