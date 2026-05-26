import { useState, useEffect } from 'react';

export default function FailedRecords({ setView }) {
  const [failed, setFailed] = useState([]);
  const [suspicious, setSuspicious] = useState([]);
  const [failedNext, setFailedNext] = useState(null);
  const [failedPrev, setFailedPrev] = useState(null);
  const [suspiciousNext, setSuspiciousNext] = useState(null);
  const [suspiciousPrev, setSuspiciousPrev] = useState(null);
  const [status, setStatus] = useState('');

  const fetchFailed = (url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/raw_records/?parse_status=FAILED&latest=true`) => {
    fetch(url)
      .then(res => res.json())
      .then(data => {
        if (data.results) {
          setFailed(data.results);
          setFailedNext(data.next);
          setFailedPrev(data.previous);
        } else {
          setFailed(data);
          setFailedNext(null);
          setFailedPrev(null);
        }
      })
      .catch(() => setStatus('Error loading failed records.'));
  };

  const fetchSuspicious = (url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/raw_records/?parse_status=SUSPICIOUS&latest=true`) => {
    fetch(url)
      .then(res => res.json())
      .then(data => {
        if (data.results) {
          setSuspicious(data.results);
          setSuspiciousNext(data.next);
          setSuspiciousPrev(data.previous);
        } else {
          setSuspicious(data);
          setSuspiciousNext(null);
          setSuspiciousPrev(null);
        }
      })
      .catch(() => setStatus('Error loading suspicious records.'));
  };

  useEffect(() => {
    fetchFailed();
    fetchSuspicious();
  }, []);

  return (
    <div className="card border-danger">
      <div className="flex justify-between items-center mb-4">
        <h2>Failed & Suspicious Records</h2>
        <button onClick={() => setView('review')} style={{background: 'transparent', border: '1px solid var(--accent-primary)', color: 'var(--accent-primary)'}}>
          &larr; Back to Review
        </button>
      </div>

      {status && <div className="mb-4 text-warning">{status}</div>}
      
      <div className="mb-8">
        <h3 className="text-danger mb-4">Failed Rows</h3>
        <p className="text-secondary mb-4">These rows encountered fatal errors during parsing and were not normalized.</p>
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>Job ID</th>
                <th>Error Reason</th>
                <th>Raw Data Dump</th>
              </tr>
            </thead>
            <tbody>
              {failed.map(rec => (
                <tr key={rec.id}>
                  <td style={{fontFamily: 'monospace'}}>{rec.job.substring(0, 8)}</td>
                  <td className="text-danger font-bold">{rec.parse_error}</td>
                  <td style={{fontFamily: 'monospace', fontSize: '0.8rem', whiteSpace: 'pre-wrap', maxWidth: '300px'}}>
                    {JSON.stringify(rec.raw_data, null, 2)}
                  </td>
                </tr>
              ))}
              {failed.length === 0 && (
                <tr>
                  <td colSpan="3" className="text-center text-secondary py-4">No failed records.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="flex justify-between items-center mt-4">
          <div>
            <button disabled={!failedPrev} onClick={() => fetchFailed(failedPrev)} style={{marginRight: '0.5rem'}}>&larr; Previous</button>
            <button disabled={!failedNext} onClick={() => fetchFailed(failedNext)}>Next &rarr;</button>
          </div>
        </div>
      </div>
      
      <div>
        <h3 className="text-warning mb-4">Suspicious Rows</h3>
        <p className="text-secondary mb-4">These rows were parsed and normalized, but were auto-flagged for missing dimensions.</p>
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>Job ID</th>
                <th>Suspicious Reason</th>
                <th>Raw Data Dump</th>
              </tr>
            </thead>
            <tbody>
              {suspicious.map(rec => (
                <tr key={rec.id}>
                  <td style={{fontFamily: 'monospace'}}>{rec.job.substring(0, 8)}</td>
                  <td className="text-warning font-bold">{rec.parse_error}</td>
                  <td style={{fontFamily: 'monospace', fontSize: '0.8rem', whiteSpace: 'pre-wrap', maxWidth: '300px'}}>
                    {JSON.stringify(rec.raw_data, null, 2)}
                  </td>
                </tr>
              ))}
              {suspicious.length === 0 && (
                <tr>
                  <td colSpan="3" className="text-center text-secondary py-4">No suspicious records.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="flex justify-between items-center mt-4">
          <div>
            <button disabled={!suspiciousPrev} onClick={() => fetchSuspicious(suspiciousPrev)} style={{marginRight: '0.5rem'}}>&larr; Previous</button>
            <button disabled={!suspiciousNext} onClick={() => fetchSuspicious(suspiciousNext)}>Next &rarr;</button>
          </div>
        </div>
      </div>
    </div>
  );
}
