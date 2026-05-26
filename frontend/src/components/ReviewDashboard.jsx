import { useState, useEffect } from 'react';

export default function ReviewDashboard({ setView }) {
  const [records, setRecords] = useState([]);
  const [status, setStatus] = useState('');
  const [nextPage, setNextPage] = useState(null);
  const [prevPage, setPrevPage] = useState(null);

  const fetchRecords = (url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/records/?latest=true`) => {
    fetch(url)
      .then(res => res.json())
      .then(data => {
        if (data.results) {
          setRecords(data.results);
          setNextPage(data.next);
          setPrevPage(data.previous);
        } else {
          setRecords(data);
          setNextPage(null);
          setPrevPage(null);
        }
      })
      .catch(() => setStatus('Error loading records.'));
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  const handleAction = async (id, action) => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/records/${id}/${action}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(action === 'flag' ? { note: 'Flagged by reviewer' } : {})
      });
      if (res.ok) {
        fetchRecords();
      } else {
        const err = await res.json();
        setStatus(`Error: ${err.error}`);
      }
    } catch (err) {
      setStatus(`Network error: ${err.message}`);
    }
  };

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h2>Review & Approve</h2>
        <div className="flex gap-4">
          <button onClick={() => setView('failed')} className="danger" style={{padding: '0.5rem 1rem'}}>
            View Failed & Suspicious Rows
          </button>
          <button onClick={() => setView('upload')} style={{background: 'transparent', border: '1px solid var(--accent-primary)', color: 'var(--accent-primary)'}}>
            &larr; Back to Upload
          </button>
        </div>
      </div>

      {status && <div className="mb-4 text-warning">{status}</div>}

      <div style={{ overflowX: 'auto' }}>
        <table>
          <thead>
            <tr>
              <th>ID (Short)</th>
              <th>Scope</th>
              <th>Original</th>
              <th>Normalized (kWh)</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {records.map(rec => (
              <tr key={rec.id}>
                <td style={{fontFamily: 'monospace'}}>{rec.id.substring(0, 8)}</td>
                <td>{rec.scope}</td>
                <td>{parseFloat(rec.quantity_original).toFixed(2)} {rec.unit_original}</td>
                <td>{parseFloat(rec.quantity_normalized).toFixed(2)}</td>
                <td>
                  <span className={`status-badge ${rec.review_status.toLowerCase()}`}>
                    {rec.review_status}
                  </span>
                </td>
                <td className="flex gap-4">
                  {!rec.is_locked && (
                    <>
                      <button className="success" style={{padding: '0.25rem 0.75rem', fontSize: '0.875rem'}} onClick={() => handleAction(rec.id, 'approve')}>Approve</button>
                      <button className="danger" style={{padding: '0.25rem 0.75rem', fontSize: '0.875rem'}} onClick={() => handleAction(rec.id, 'flag')}>Flag</button>
                    </>
                  )}
                  {rec.is_locked && <span className="text-secondary">Locked</span>}
                </td>
              </tr>
            ))}
            {records.length === 0 && (
              <tr>
                <td colSpan="6" className="text-center text-secondary py-8">No records found. Upload some data first.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      
      <div className="flex justify-between items-center mt-4">
        <div>
          <button disabled={!prevPage} onClick={() => fetchRecords(prevPage)} style={{marginRight: '0.5rem'}}>&larr; Previous</button>
          <button disabled={!nextPage} onClick={() => fetchRecords(nextPage)}>Next &rarr;</button>
        </div>
      </div>
    </div>
  );
}
