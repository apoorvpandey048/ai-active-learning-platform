import React, { useState } from 'react';
import { fetchWith202Retry } from '../lib/api';
import Spinner from './Spinner';

export default function LecturePage() {
  const [url, setUrl] = useState('');
  const [transcript, setTranscript] = useState('');
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const fetchTranscript = async () => {
    setLoading(true);
    setMessage('');
    try {
      const res = await fetch('http://localhost:5000/fetch-transcript', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to fetch transcript');
      setTranscript(data.transcript || '');
    } catch (err) {
      setMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  const [retryState, setRetryState] = useState({ attempt: 0, delay: 0 });

  const summarize = async () => {
    setLoading(true);
    setMessage('');
    try {
      const body = { text: transcript };
      if (useMock) body.force_mock = true;
      const res = await fetchWith202Retry('http://localhost:5000/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      }, { onRetry: (attempt, delay) => setRetryState({ attempt, delay }) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Summarize failed');
      setSummary(data.summary || data.message || '');
    } catch (err) {
      setMessage(err.message);
    } finally {
      setLoading(false);
      setRetryState({ attempt: 0, delay: 0 });
    }
  };

  const [questions, setQuestions] = useState([]);
  const [useMock, setUseMock] = useState(true);

  const generateQuiz = async () => {
    setLoading(true);
    setMessage('');
    try {
      const body = { text: transcript };
      if (useMock) body.force_mock = true;
      const res = await fetchWith202Retry('http://localhost:5000/generate-quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      }, { onRetry: (attempt, delay) => setRetryState({ attempt, delay }) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || data.message || 'Quiz generation failed');
      setQuestions(data.questions || []);
    } catch (err) {
      setMessage(err.message);
    } finally {
      setLoading(false);
      setRetryState({ attempt: 0, delay: 0 });
    }
  };

  // Robust YouTube embed helper
  const getEmbedUrl = (u) => {
    if (!u) return '';
    try {
      const urlObj = new URL(u);
      if (urlObj.hostname.includes('youtube.com')) {
        const v = urlObj.searchParams.get('v');
        if (v) return `https://www.youtube.com/embed/${v}`;
      }
      if (urlObj.hostname.includes('youtu.be')) {
        const id = urlObj.pathname.split('/').filter(Boolean).pop();
        if (id) return `https://www.youtube.com/embed/${id}`;
      }
      return u; // fallback
    } catch (e) {
      return u;
    }
  };


  const saveLecture = async () => {
    setLoading(true);
    setMessage('');
    try {
      const res = await fetch('http://localhost:5000/save-lecture', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: 'Uploaded Lecture', video_url: url, transcript, summary })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Save failed');
      setMessage('Lecture saved: ' + (data.lecture_id || 'unknown'));
    } catch (err) {
      setMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginTop: 20 }}>
      <h3>Lecture Page (demo)</h3>
      <div>
        <input placeholder="YouTube URL" style={{ width: '70%' }} value={url} onChange={(e) => setUrl(e.target.value)} />
        <button onClick={fetchTranscript} disabled={loading || !url} style={{ marginLeft: 8 }}>Fetch Transcript</button>
      </div>
      {url && (
        <div style={{ marginTop: 12 }}>
          <strong>Video</strong>
          <div style={{ marginTop: 8 }}>
            <iframe title="video" width="560" height="315" src={getEmbedUrl(url)} frameBorder="0" allowFullScreen />
          </div>
        </div>
      )}
      {transcript && (
        <div style={{ marginTop: 12 }}>
          <strong>Transcript</strong>
          <p style={{ whiteSpace: 'pre-wrap' }}>{transcript}</p>
          <div style={{ marginTop: 8 }}>
            <label style={{ marginRight: 12 }}>
              <input type="checkbox" checked={useMock} onChange={(e) => setUseMock(e.target.checked)} /> Use mock
            </label>
            <button onClick={summarize} disabled={loading}>Summarize</button>
            <button onClick={generateQuiz} disabled={loading} style={{ marginLeft: 8 }}>Generate Quiz</button>
            <button onClick={saveLecture} disabled={loading} style={{ marginLeft: 8 }}>Save Lecture</button>
            {loading && <span style={{ marginLeft: 12 }}><Spinner size={14} /></span>}
            {retryState.attempt > 0 && <span style={{ marginLeft: 12, color: 'orange' }}>Retrying (attempt {retryState.attempt})...</span>}
          </div>
        </div>
      )}
      {summary && (
        <div style={{ marginTop: 12 }}>
          <strong>Summary</strong>
          <p>{summary}</p>
        </div>
      )}
      {questions.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <strong>Generated Quiz</strong>
          {questions.map((q, i) => (
            <div key={i} style={{ marginTop: 8 }}>
              <div><strong>{i+1}. {q.question || q.question_text}</strong></div>
              <ul>
                {(q.options || q.options || []).map((opt, j) => (
                  <li key={j}>{opt}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
      {message && <div style={{ color: 'red', marginTop: 8 }}>{message}</div>}
    </div>
  );
}
