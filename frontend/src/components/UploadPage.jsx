import { useState, useEffect } from 'react';

const SOURCE_ICONS = {
  SAP:     '🏭',
  TRAVEL:  '✈️',
  UTILITY: '⚡',
};

const SOURCE_COLORS = {
  SAP:     { accent: '#3b82f6', bg: 'rgba(59,130,246,0.08)', border: 'rgba(59,130,246,0.4)' },
  TRAVEL:  { accent: '#a78bfa', bg: 'rgba(167,139,250,0.08)', border: 'rgba(167,139,250,0.4)' },
  UTILITY: { accent: '#34d399', bg: 'rgba(52,211,153,0.08)', border: 'rgba(52,211,153,0.4)' },
};

const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function UploadPage({ setView }) {
  const [clients, setClients]     = useState([]);
  const [clientId, setClientId]   = useState('');
  const [samples, setSamples]     = useState([]);
  const [selected, setSelected]   = useState(null);   // filename string
  const [status, setStatus]       = useState(null);   // { type: 'loading'|'success'|'error', message }
  const [loadingClients, setLoadingClients] = useState(true);
  const [loadingSamples, setLoadingSamples] = useState(true);

  // Load clients
  useEffect(() => {
    fetch(`${API}/api/clients/`)
      .then(r => r.json())
      .then(data => {
        const list = data.results ?? data;
        setClients(list);
        if (list.length > 0) setClientId(String(list[0].id));
      })
      .catch(() => setStatus({ type: 'error', message: 'Could not load clients — is the Django server running?' }))
      .finally(() => setLoadingClients(false));
  }, []);

  // Load sample catalogue
  useEffect(() => {
    fetch(`${API}/api/ingestion/jobs/samples/`)
      .then(r => r.json())
      .then(data => {
        setSamples(data);
        const firstAvailable = data.find(s => s.available);
        if (firstAvailable) setSelected(firstAvailable.filename);
      })
      .catch(() => setStatus({ type: 'error', message: 'Could not load sample catalogue from the server.' }))
      .finally(() => setLoadingSamples(false));
  }, []);

  const handleAnalyse = async () => {
    if (!selected || !clientId) return;
    setStatus({ type: 'loading', message: 'Running ingestion pipeline…' });

    try {
      const res = await fetch(`${API}/api/ingestion/jobs/ingest_sample/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client: clientId, filename: selected }),
      });
      const data = await res.json();
      if (res.ok) {
        setStatus({
          type: 'success',
          message: `✅ Done! Parsed ${data.row_count} rows — ${data.success_count} successful, ${data.error_count} errors.`,
          jobId: data.id,
        });
      } else {
        setStatus({ type: 'error', message: data.error ?? 'Ingestion failed.' });
      }
    } catch (err) {
      setStatus({ type: 'error', message: `Network error: ${err.message}` });
    }
  };

  const isLoading = loadingClients || loadingSamples;
  const selectedSample = samples.find(s => s.filename === selected);

  return (
    <div className="card" style={{ maxWidth: 780, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.4rem', marginBottom: '0.35rem' }}>Analyse a Dataset</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Choose a pre-loaded sample and a client, then run the ingestion pipeline instantly — no file upload needed.
        </p>
      </div>

      {/* Client selector */}
      <div style={{ marginBottom: '1.75rem' }}>
        <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>
          Client
        </label>
        <select
          id="client-select"
          value={clientId}
          onChange={e => setClientId(e.target.value)}
          disabled={loadingClients}
          style={{ marginBottom: 0, maxWidth: 320 }}
        >
          {loadingClients
            ? <option>Loading…</option>
            : clients.map(c => <option key={c.id} value={c.id}>{c.name}</option>)
          }
        </select>
      </div>

      {/* Dataset cards */}
      <div style={{ marginBottom: '1.75rem' }}>
        <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.75rem' }}>
          Select Dataset
        </label>

        {isLoading ? (
          <div style={{ color: 'var(--text-secondary)', padding: '1rem 0' }}>Loading datasets…</div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '0.875rem' }}>
            {samples.map(sample => {
              const isSelected  = selected === sample.filename;
              const colors      = SOURCE_COLORS[sample.source_type] ?? SOURCE_COLORS.SAP;
              const icon        = SOURCE_ICONS[sample.source_type] ?? '📄';
              return (
                <button
                  key={sample.filename}
                  id={`dataset-card-${sample.source_type.toLowerCase()}`}
                  type="button"
                  disabled={!sample.available}
                  onClick={() => setSelected(sample.filename)}
                  style={{
                    all: 'unset',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.6rem',
                    padding: '1.1rem 1.25rem',
                    borderRadius: '0.75rem',
                    cursor: sample.available ? 'pointer' : 'not-allowed',
                    background: isSelected ? colors.bg : 'rgba(255,255,255,0.03)',
                    border: `1.5px solid ${isSelected ? colors.accent : 'rgba(255,255,255,0.1)'}`,
                    boxShadow: isSelected ? `0 0 0 3px ${colors.border}` : 'none',
                    transition: 'all 0.2s ease',
                    opacity: sample.available ? 1 : 0.45,
                    textAlign: 'left',
                  }}
                  onMouseEnter={e => { if (!isSelected && sample.available) e.currentTarget.style.border = `1.5px solid ${colors.border}`; }}
                  onMouseLeave={e => { if (!isSelected) e.currentTarget.style.border = '1.5px solid rgba(255,255,255,0.1)'; }}
                >
                  <span style={{ fontSize: '1.6rem', lineHeight: 1 }}>{icon}</span>
                  <span style={{ fontWeight: 600, fontSize: '0.92rem', color: isSelected ? colors.accent : 'var(--text-primary)', lineHeight: 1.3 }}>
                    {sample.name}
                  </span>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    {sample.description}
                  </span>
                  {!sample.available && (
                    <span style={{ fontSize: '0.72rem', color: 'var(--danger)', fontWeight: 500 }}>
                      ⚠ File not found — run generate_samples.py
                    </span>
                  )}
                  {isSelected && (
                    <span style={{ fontSize: '0.72rem', color: colors.accent, fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      ✓ Selected
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Action row */}
      <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
        <button
          id="analyse-btn"
          type="button"
          onClick={handleAnalyse}
          disabled={!selected || !clientId || status?.type === 'loading' || !selectedSample?.available}
          style={{
            background: 'linear-gradient(135deg, #3b82f6, #6366f1)',
            border: 'none',
            padding: '0.75rem 1.75rem',
            fontWeight: 600,
            fontSize: '0.95rem',
            opacity: (!selected || status?.type === 'loading') ? 0.6 : 1,
            cursor: (!selected || status?.type === 'loading') ? 'not-allowed' : 'pointer',
          }}
        >
          {status?.type === 'loading' ? '⏳ Processing…' : 'Analyse Dataset →'}
        </button>

        <button
          type="button"
          onClick={() => setView('review')}
          style={{ background: 'var(--glass-bg)', border: '1px solid var(--border-color)', color: 'var(--text-primary)' }}
        >
          Go to Review Dashboard →
        </button>
      </div>

      {/* Status banner */}
      {status && status.type !== 'loading' && (
        <div style={{
          marginTop: '1.25rem',
          padding: '0.9rem 1.25rem',
          borderRadius: '0.6rem',
          background: status.type === 'success' ? 'rgba(16,185,129,0.12)' : 'rgba(239,68,68,0.12)',
          border: `1px solid ${status.type === 'success' ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`,
          color: status.type === 'success' ? 'var(--success)' : 'var(--danger)',
          fontSize: '0.9rem',
          fontWeight: 500,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem',
        }}>
          <span>{status.message}</span>
          {status.type === 'success' && (
            <button
              type="button"
              onClick={() => setView('review')}
              style={{ background: 'var(--success)', border: 'none', padding: '0.4rem 1rem', fontSize: '0.82rem', whiteSpace: 'nowrap', flexShrink: 0 }}
            >
              View Results →
            </button>
          )}
        </div>
      )}
    </div>
  );
}
