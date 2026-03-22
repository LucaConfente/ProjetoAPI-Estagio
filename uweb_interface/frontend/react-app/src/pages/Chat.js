import React, { useState, useRef, useEffect } from 'react';

const INITIAL_MESSAGES = [
  {
    id: 0,
    role: 'assistant',
    content: 'Olá! Sou seu assistente virtual. Posso analisar imagens, PDFs e arquivos de texto. Como posso ajudar?',
    time: formatTime(new Date()),
  },
];

function formatTime(date) {
  return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

const ACCEPTED_FILES = '.jpg,.jpeg,.png,.gif,.webp,.pdf,.txt,.csv';
const IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

function getFileIcon(type) {
  if (IMAGE_TYPES.includes(type)) return '🖼';
  if (type === 'application/pdf') return '📄';
  return '📝';
}

function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

export default function Chat() {
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [input, setInput] = useState('');
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleFiles = (newFiles) => {
    const arr = Array.from(newFiles).map(f => ({
      file: f,
      name: f.name,
      type: f.type,
      size: f.size,
      id: Date.now() + Math.random(),
    }));
    setFiles(prev => [...prev, ...arr]);
  };

  const removeFile = (id) => setFiles(prev => prev.filter(f => f.id !== id));

  const toBase64 = (file) => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(',')[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });

  const toText = (file) => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsText(file);
  });

  const sendMessage = async () => {
    const text = input.trim();
    if ((!text && files.length === 0) || loading) return;

    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: text,
      files: files.map(f => ({
        name: f.name,
        type: f.type,
        size: f.size,
        preview: IMAGE_TYPES.includes(f.type) ? URL.createObjectURL(f.file) : null,
      })),
      time: formatTime(new Date()),
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setError(null);

    const processedFiles = await Promise.all(files.map(async (f) => {
      if (IMAGE_TYPES.includes(f.type)) {
        const b64 = await toBase64(f.file);
        return { type: 'image', name: f.name, mime: f.type, data: b64 };
      } else {
        const content = await toText(f.file);
        return { type: 'text', name: f.name, mime: f.type, data: content };
      }
    }));

    setFiles([]);

    const historyMessages = messages
      .filter(m => m.id !== 0)
      .map(m => ({ role: m.role, content: m.content }));

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer API_LUCA',
        },
        body: JSON.stringify({
          messages: [...historyMessages, { role: 'user', content: text || 'Analise os arquivos enviados.' }],
          model: 'gpt-4o',
          files: processedFiles,
        }),
      });

      if (!response.ok) throw new Error(`Erro ${response.status}`);

      const data = await response.json();
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.response || data.message || JSON.stringify(data),
        time: formatTime(new Date()),
      }]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  const clearChat = () => { setMessages(INITIAL_MESSAGES); setFiles([]); setError(null); };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Chat</h1>
          <p style={styles.subtitle}>
            <span style={styles.modelBadge}>GPT-4 Vision</span>
            {messages.length - 1} mensagem{messages.length !== 2 ? 's' : ''}
          </p>
        </div>
        <button style={styles.clearBtn} onClick={clearChat}>↺ Limpar</button>
      </div>

      <div
        style={{ ...styles.messagesWrap, ...(dragOver ? styles.messagesWrapDrag : {}) }}
        onDragOver={e => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        {dragOver && (
          <div style={styles.dropOverlay}>
            <span style={styles.dropIcon}>⬆</span>
            <span>Solte os arquivos aqui</span>
          </div>
        )}
        <div style={styles.messages}>
          {messages.map((msg, i) => <MessageBubble key={msg.id} msg={msg} index={i} />)}
          {loading && <TypingIndicator />}
          {error && (
            <div style={styles.error}>
              <span>⚠</span><span>Erro ao conectar: {error}</span>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </div>

      {files.length > 0 && (
        <div style={styles.filesPreview}>
          {files.map(f => (
            <div key={f.id} style={styles.fileChip}>
              <span>{getFileIcon(f.type)}</span>
              <div style={styles.fileChipInfo}>
                <span style={styles.fileChipName}>{f.name}</span>
                <span style={styles.fileChipSize}>{formatBytes(f.size)}</span>
              </div>
              <button style={styles.fileChipRemove} onClick={() => removeFile(f.id)}>✕</button>
            </div>
          ))}
        </div>
      )}

      <div style={styles.inputArea}>
        <div style={styles.inputWrap}>
          <button style={styles.attachBtn} onClick={() => fileInputRef.current?.click()} title="Anexar arquivo">
            📎
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept={ACCEPTED_FILES}
            style={{ display: 'none' }}
            onChange={e => handleFiles(e.target.files)}
          />
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Digite sua mensagem ou arraste arquivos..."
            style={styles.input}
            rows={1}
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={(!input.trim() && files.length === 0) || loading}
            style={{
              ...styles.sendBtn,
              ...((!input.trim() && files.length === 0) || loading ? styles.sendBtnDisabled : styles.sendBtnActive),
            }}
          >
            {loading ? <LoadingSpinner /> : '↑'}
          </button>
        </div>
        <p style={styles.hint}>Shift+Enter para nova linha · Arraste arquivos para o chat</p>
      </div>
    </div>
  );
}

function MessageBubble({ msg, index }) {
  const isUser = msg.role === 'user';
  return (
    <div style={{ ...styles.msgRow, ...(isUser ? styles.msgRowUser : styles.msgRowAssistant), animationDelay: `${Math.min(index * 0.05, 0.3)}s` }}>
      {!isUser && <div style={styles.avatar}>AI</div>}
      <div style={isUser ? styles.bubbleUser : styles.bubbleAssistant}>
        {msg.files && msg.files.length > 0 && (
          <div style={styles.msgFiles}>
            {msg.files.map((f, i) => (
              <div key={i}>
                {f.preview
                  ? <img src={f.preview} alt={f.name} style={styles.msgImage} />
                  : <div style={styles.msgFileIcon}><span>{getFileIcon(f.type)}</span><span style={styles.msgFileName}>{f.name}</span></div>
                }
              </div>
            ))}
          </div>
        )}
        {msg.content && <p style={styles.msgContent}>{msg.content}</p>}
        <span style={styles.msgTime}>{msg.time}</span>
      </div>
      {isUser && <div style={{ ...styles.avatar, ...styles.avatarUser }}>EU</div>}
    </div>
  );
}

function TypingIndicator() {
  return (
    <div style={{ ...styles.msgRow, ...styles.msgRowAssistant }}>
      <div style={styles.avatar}>AI</div>
      <div style={{ ...styles.bubbleAssistant, ...styles.typingBubble }}>
        <div style={styles.dots}>
          {[0, 1, 2].map(i => <span key={i} style={{ ...styles.dot, animationDelay: `${i * 0.18}s` }} />)}
        </div>
      </div>
    </div>
  );
}

function LoadingSpinner() {
  return <span style={styles.spinner} />;
}

const styles = {
  page: { maxWidth: '780px', margin: '0 auto', padding: '2rem 1.5rem', display: 'flex', flexDirection: 'column', height: 'calc(100vh - 58px)', animation: 'fadeUp 0.5s ease' },
  header: { display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1.5rem' },
  title: { fontSize: '1.4rem', fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--text)', marginBottom: '0.3rem' },
  subtitle: { fontSize: '0.78rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.5rem' },
  modelBadge: { fontFamily: 'var(--mono)', fontSize: '0.68rem', background: 'var(--accent-soft)', color: 'var(--accent)', padding: '0.15rem 0.5rem', borderRadius: '99px', border: '1px solid rgba(110,86,255,0.2)' },
  clearBtn: { padding: '0.4rem 0.8rem', borderRadius: '8px', background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-muted)', fontSize: '0.78rem', cursor: 'pointer', fontFamily: 'var(--font)' },
  messagesWrap: { flex: 1, overflow: 'hidden', borderRadius: '14px', background: 'var(--card)', border: '1px solid var(--border)', marginBottom: '0.75rem', position: 'relative', transition: 'border-color 0.2s' },
  messagesWrapDrag: { borderColor: 'var(--accent)', boxShadow: '0 0 0 3px var(--accent-glow)' },
  dropOverlay: { position: 'absolute', inset: 0, zIndex: 10, background: 'rgba(7,7,16,0.85)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', fontSize: '0.9rem', color: 'var(--accent)', fontWeight: 500, backdropFilter: 'blur(4px)', borderRadius: '14px' },
  dropIcon: { fontSize: '2rem' },
  messages: { height: '100%', overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' },
  msgRow: { display: 'flex', alignItems: 'flex-end', gap: '0.6rem', animation: 'fadeUp 0.3s ease both' },
  msgRowUser: { flexDirection: 'row-reverse' },
  msgRowAssistant: { flexDirection: 'row' },
  avatar: { width: '28px', height: '28px', borderRadius: '50%', background: 'var(--accent-soft)', border: '1px solid rgba(110,86,255,0.25)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.55rem', fontWeight: 700, fontFamily: 'var(--mono)', color: 'var(--accent)', flexShrink: 0 },
  avatarUser: { background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', color: 'var(--text-secondary)' },
  bubbleAssistant: { maxWidth: '72%', padding: '0.75rem 1rem', borderRadius: '14px 14px 14px 4px', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)' },
  bubbleUser: { maxWidth: '72%', padding: '0.75rem 1rem', borderRadius: '14px 14px 4px 14px', background: 'var(--accent-soft)', border: '1px solid rgba(110,86,255,0.2)' },
  msgFiles: { display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '0.5rem' },
  msgImage: { maxWidth: '100%', maxHeight: '200px', borderRadius: '8px', objectFit: 'cover', display: 'block' },
  msgFileIcon: { display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.4rem 0.7rem', borderRadius: '8px', background: 'rgba(255,255,255,0.06)', border: '1px solid var(--border)' },
  msgFileName: { fontSize: '0.78rem', color: 'var(--text-secondary)', fontFamily: 'var(--mono)' },
  msgContent: { fontSize: '0.88rem', lineHeight: 1.65, color: 'var(--text)', whiteSpace: 'pre-wrap', wordBreak: 'break-word' },
  msgTime: { display: 'block', fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '0.35rem', fontFamily: 'var(--mono)' },
  typingBubble: { padding: '0.85rem 1rem' },
  dots: { display: 'flex', gap: '0.35rem', alignItems: 'center' },
  dot: { display: 'block', width: '5px', height: '5px', borderRadius: '50%', background: 'var(--text-muted)', animation: 'blink 1.2s ease-in-out infinite' },
  error: { display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.7rem 1rem', borderRadius: '10px', background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', color: '#f87171', fontSize: '0.82rem' },
  filesPreview: { display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.5rem' },
  fileChip: { display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.4rem 0.6rem', borderRadius: '8px', background: 'var(--card)', border: '1px solid var(--border-active)', maxWidth: '220px' },
  fileChipInfo: { display: 'flex', flexDirection: 'column', overflow: 'hidden' },
  fileChipName: { fontSize: '0.75rem', color: 'var(--text)', fontFamily: 'var(--mono)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' },
  fileChipSize: { fontSize: '0.65rem', color: 'var(--text-muted)' },
  fileChipRemove: { background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.7rem', marginLeft: 'auto' },
  inputArea: {},
  inputWrap: { display: 'flex', gap: '0.5rem', alignItems: 'flex-end', padding: '0.75rem', borderRadius: '14px', background: 'var(--card)', border: '1px solid var(--border)' },
  attachBtn: { width: '36px', height: '36px', borderRadius: '9px', border: '1px solid var(--border)', background: 'transparent', fontSize: '1rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 },
  input: { flex: 1, background: 'transparent', border: 'none', outline: 'none', color: 'var(--text)', fontSize: '0.88rem', fontFamily: 'var(--font)', resize: 'none', lineHeight: 1.5, maxHeight: '120px', overflowY: 'auto', caretColor: 'var(--accent)' },
  sendBtn: { width: '36px', height: '36px', borderRadius: '9px', border: 'none', fontSize: '1.1rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontWeight: 700 },
  sendBtnActive: { background: 'var(--accent)', color: '#fff', boxShadow: '0 0 20px rgba(110,86,255,0.4)' },
  sendBtnDisabled: { background: 'rgba(255,255,255,0.04)', color: 'var(--text-muted)', cursor: 'not-allowed' },
  hint: { fontSize: '0.68rem', color: 'var(--text-muted)', textAlign: 'center', marginTop: '0.5rem', fontFamily: 'var(--mono)' },
  spinner: { display: 'block', width: '14px', height: '14px', border: '2px solid rgba(255,255,255,0.2)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin 0.7s linear infinite' },
};
