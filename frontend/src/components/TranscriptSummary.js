import React, { useState } from 'react';

export default function TranscriptSummary() {
  const [text, setText] = useState('');
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSummarize = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('http://localhost:5000/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Summarization failed');
      setSummary(data.summary);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginTop: 20 }}>
      <h3>Transcript Summarizer (demo)</h3>
      <textarea rows={6} style={{ width: '100%' }} value={text} onChange={(e) => setText(e.target.value)} />
      <div style={{ marginTop: 8 }}>
        <button onClick={handleSummarize} disabled={loading || !text}>
          {loading ? 'Summarizing...' : 'Summarize'}
        </button>
      </div>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {summary && (
        <div style={{ marginTop: 12 }}>
          <strong>Summary:</strong>
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
}
