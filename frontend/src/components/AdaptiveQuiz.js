import React, { useState } from 'react';
import { fetchWith202Retry } from '../lib/api';

export default function AdaptiveQuiz() {
  const [text, setText] = useState('');
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [useMock, setUseMock] = useState(true);
  const [retryState, setRetryState] = useState({ attempt: 0, delay: 0 });

  const generate = async () => {
    setLoading(true);
    setError(null);
    try {
      const body = { text };
      if (useMock) body.force_mock = true;
      const res = await fetchWith202Retry('http://localhost:5000/generate-quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      }, { onRetry: (attempt, delay) => setRetryState({ attempt, delay }) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || data.message || 'Quiz generation failed');
      setQuestions(data.questions || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setRetryState({ attempt: 0, delay: 0 });
    }
  };

  return (
    <div style={{ marginTop: 20 }}>
      <h3>Adaptive Quiz (demo)</h3>
      <textarea rows={4} style={{ width: '100%' }} value={text} onChange={(e) => setText(e.target.value)} />
      <div style={{ marginTop: 8 }}>
        <label style={{ marginRight: 12 }}>
          <input type="checkbox" checked={useMock} onChange={(e) => setUseMock(e.target.checked)} /> Use mock
        </label>
        <button onClick={generate} disabled={loading || !text}>
          {loading ? 'Generating...' : 'Generate Quiz'}
        </button>
      </div>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {retryState.attempt > 0 && (
        <div style={{ marginTop: 8, color: 'orange' }}>
          Retrying (attempt {retryState.attempt})... waiting {Math.round(retryState.delay/1000)}s
        </div>
      )}
      {questions.length > 0 && (
        <div style={{ marginTop: 12 }}>
          {questions.map((q, i) => (
            <div key={i} style={{ marginBottom: 12 }}>
              <strong>{i + 1}. {q.question}</strong>
              <ul>
                {q.options.map((opt, j) => (
                  <li key={j}>{opt}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
