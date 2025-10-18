import React, { useState } from 'react';

export default function AdaptiveQuiz() {
  const [text, setText] = useState('');
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('http://localhost:5000/generate-quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Quiz generation failed');
      setQuestions(data.questions || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginTop: 20 }}>
      <h3>Adaptive Quiz (demo)</h3>
      <textarea rows={4} style={{ width: '100%' }} value={text} onChange={(e) => setText(e.target.value)} />
      <div style={{ marginTop: 8 }}>
        <button onClick={generate} disabled={loading || !text}>
          {loading ? 'Generating...' : 'Generate Quiz'}
        </button>
      </div>
      {error && <div style={{ color: 'red' }}>{error}</div>}
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
