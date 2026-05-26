import { useState } from 'react';
import UploadPage from './components/UploadPage';
import ReviewDashboard from './components/ReviewDashboard';
import FailedRecords from './components/FailedRecords';

function App() {
  const [view, setView] = useState('upload'); // 'upload' | 'review' | 'failed'

  return (
    <div className="container py-8">
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h1>Breathe ESG</h1>
          <p className="text-secondary">Data Ingestion & Review Platform</p>
        </div>
        
        <nav className="flex gap-4">
          <button 
            style={{background: view === 'upload' ? 'var(--accent-primary)' : 'transparent', border: view === 'upload' ? 'none' : '1px solid var(--border-color)'}}
            onClick={() => setView('upload')}
          >
            Analyse Data
          </button>
          <button 
            style={{background: view === 'review' ? 'var(--accent-primary)' : 'transparent', border: view === 'review' ? 'none' : '1px solid var(--border-color)'}}
            onClick={() => setView('review')}
          >
            Review Data
          </button>
          <button 
            style={{background: view === 'failed' ? 'var(--accent-primary)' : 'transparent', border: view === 'failed' ? 'none' : '1px solid var(--border-color)'}}
            onClick={() => setView('failed')}
          >
            Failed Records
          </button>
        </nav>
        <button 
          className="danger"
          onClick={() => {
            if(window.confirm('Are you sure you want to delete all data?')) {
              fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/ingestion/jobs/reset/`, {method: 'POST'})
                .then(() => window.location.reload())
            }
          }}
        >
          Reset Data
        </button>
      </header>

      <main>
        {view === 'upload' && <UploadPage setView={setView} />}
        {view === 'review' && <ReviewDashboard setView={setView} />}
        {view === 'failed' && <FailedRecords setView={setView} />}
      </main>
    </div>
  );
}

export default App;
