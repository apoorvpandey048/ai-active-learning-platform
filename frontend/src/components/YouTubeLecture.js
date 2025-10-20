import React, { useState } from 'react';

export default function YouTubeLecture() {
  const [url, setUrl] = useState('');
  const [transcript, setTranscript] = useState('');
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchTranscript = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:5000/fetch-transcript', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      const data = await res.json();
      if (res.ok) {
        setTranscript(data.transcript || '');
      } else {
        setTranscript('Error fetching transcript');
      }
    } catch (err) {
      setTranscript('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:5000/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: transcript })
      });
      const data = await res.json();
      if (res.ok) setSummary(data.summary || '');
      else setSummary('Error summarizing');
    } catch (err) {
      setSummary('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const saveLecture = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:5000/save-lecture', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: url, video_url: url, transcript, summary })
      });
      const data = await res.json();
      alert(data.message || JSON.stringify(data));
    } catch (err) {
      alert('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginTop: 20 }}>
      <h3>YouTube Lecture</h3>
      <input style={{ width: '100%' }} placeholder="YouTube URL" value={url} onChange={(e) => setUrl(e.target.value)} />
      <div style={{ marginTop: 8 }}>
        <button onClick={fetchTranscript} disabled={!url || loading}>Fetch Transcript</button>
        <button onClick={handleSummarize} disabled={!transcript || loading} style={{ marginLeft: 8 }}>Summarize</button>
        <button onClick={saveLecture} disabled={!transcript || loading} style={{ marginLeft: 8 }}>Save Lecture</button>
      </div>
      <div style={{ marginTop: 12 }}>
        <h4>Transcript</h4>
        <pre style={{ maxHeight: 200, overflow: 'auto', background: '#f7f7f7', padding: 8 }}>{transcript}</pre>
      </div>
      <div style={{ marginTop: 12 }}>
        <h4>Summary</h4>
        <div style={{ background: '#f7f7f7', padding: 8 }}>{summary}</div>
      </div>
    </div>
  );
}
