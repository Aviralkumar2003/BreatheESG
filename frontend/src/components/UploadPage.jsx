import { useState, useEffect } from 'react';

export default function UploadPage({ setView }) {
  const [clients, setClients] = useState([]);
  const [clientId, setClientId] = useState('');
  const [sourceType, setSourceType] = useState('SAP');
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/clients/`)
      .then(res => res.json())
      .then(data => {
        const clientList = data.results ? data.results : data;
        setClients(clientList);
        if (clientList.length > 0) setClientId(clientList[0].id);
      })
      .catch(() => setStatus('Error loading clients. Ensure Django is running.'));
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || !clientId) return setStatus('Please select a client and file');

    const formData = new FormData();
    formData.append('client', clientId);
    formData.append('source_type', sourceType);
    formData.append('file', file);

    setStatus('Uploading...');
    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/ingestion/jobs/upload/`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        setStatus(`Upload complete! Parsed ${data.row_count} rows. ${data.error_count} errors.`);
      } else {
        setStatus(`Upload failed: ${data.error}`);
      }
    } catch (err) {
      setStatus(`Network error: ${err.message}`);
    }
  };

  return (
    <div className="card">
      <h2 className="mb-4">Upload Data Source</h2>
      
      <form onSubmit={handleUpload} className="flex-col gap-4">
        <div className="flex gap-4" style={{ width: '100%' }}>
          <div style={{ flex: 1 }}>
            <label className="text-secondary mb-2 block" style={{ fontSize: '0.875rem' }}>Select Client</label>
            <select value={clientId} onChange={(e) => setClientId(e.target.value)} style={{ marginBottom: 0 }}>
              {clients.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>

          <div style={{ flex: 1 }}>
            <label className="text-secondary mb-2 block" style={{ fontSize: '0.875rem' }}>Source Type</label>
            <select value={sourceType} onChange={(e) => setSourceType(e.target.value)} style={{ marginBottom: 0 }}>
              <option value="SAP">SAP Export (Fuel/Procurement)</option>
              <option value="UTILITY">Utility Portal (Electricity)</option>
              <option value="TRAVEL">Concur/Navan (Travel)</option>
            </select>
          </div>
        </div>

        <div className="upload-area" style={{ padding: '2rem 1rem', marginBottom: '1rem', marginTop: '1rem' }}>
          <input 
            type="file" 
            accept={sourceType === 'UTILITY' ? '.pdf' : '.csv'}
            onChange={(e) => setFile(e.target.files[0])}
            className="mb-0"
            style={{ marginBottom: 0 }}
          />
          <p className="text-secondary mt-2" style={{ fontSize: '0.875rem' }}>
            {sourceType === 'UTILITY' ? 'Please upload a PDF bill.' : 'Please upload a CSV file.'}
          </p>
        </div>

        <div className="flex justify-between items-center mt-2">
          <button type="submit">Upload & Process</button>
          <button type="button" onClick={() => setView('review')} style={{background: 'var(--glass-bg)', border: '1px solid var(--border-color)'}}>
            Go to Review Dashboard &rarr;
          </button>
        </div>
      </form>

      {status && <div className="mt-4 p-4 rounded" style={{background: 'rgba(255,255,255,0.1)'}}>{status}</div>}
    </div>
  );
}
