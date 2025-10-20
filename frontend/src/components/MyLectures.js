import React, { useEffect, useState } from 'react';

export default function MyLectures() {
  const [lectures, setLectures] = useState([]);

  const fetchLectures = async () => {
    try {
      const res = await fetch('http://localhost:5000/my-lectures');
      const data = await res.json();
      if (res.ok) setLectures(data.lectures || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => { fetchLectures(); }, []);

  return (
    <div style={{ marginTop: 20 }}>
      <h3>My Lectures</h3>
      {lectures.length === 0 ? (
        <div>No lectures saved yet.</div>
      ) : (
        <ul>
          {lectures.map(l => (
            <li key={l.id}><strong>{l.title}</strong> — <a href={l.video_url} target="_blank" rel="noreferrer">Watch</a></li>
          ))}
        </ul>
      )}
    </div>
  );
}
