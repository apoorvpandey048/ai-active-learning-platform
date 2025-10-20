import React, { useState } from 'react';
import { fetchWith202Retry } from '../lib/api';

export default function TranscriptSummary() {
  const [text, setText] = useState('');
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [useMock, setUseMock] = useState(true);
  const [retryState, setRetryState] = useState({ attempt: 0, delay: 0 });

  const handleSummarize = async () => {
    setLoading(true);
    setError(null);
    try {
      const body = { text };
      if (useMock) body.force_mock = true;
      const res = await fetchWith202Retry('http://localhost:5000/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      }, { onRetry: (attempt, delay) => setRetryState({ attempt, delay }) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || data.message || 'Summarization failed');
      setSummary(data.summary || data.message || '');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setRetryState({ attempt: 0, delay: 0 });
    }
  };

  return (
    <div style={{ marginTop: 20 }}>
      <h3>Transcript Summarizer (demo)</h3>
      <textarea rows={6} style={{ width: '100%' }} value={text} onChange={(e) => setText(e.target.value)} />
      <div style={{ marginTop: 8 }}>
        <label style={{ marginRight: 12 }}>
          <input type="checkbox" checked={useMock} onChange={(e) => setUseMock(e.target.checked)} /> Use mock
        </label>
        <button onClick={handleSummarize} disabled={loading || !text}>
          {loading ? 'Summarizing...' : 'Summarize'}
        </button>
      </div>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {retryState.attempt > 0 && (
        <div style={{ marginTop: 8, color: 'orange' }}>
          Retrying (attempt {retryState.attempt})... waiting {Math.round(retryState.delay/1000)}s
        </div>
      )}
      {summary && (
        <div style={{ marginTop: 12 }}>
          <strong>Summary:</strong>
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
}
