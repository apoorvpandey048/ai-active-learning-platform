import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import LearnerProgress from './components/LearnerProgress';
import TranscriptSummary from './components/TranscriptSummary';
import AdaptiveQuiz from './components/AdaptiveQuiz';
import LecturePage from './components/LecturePage';
import MyLectures from './components/MyLectures';
import ModelsStatus from './components/ModelsStatus';

function Home() {
  return (
    <div style={{ padding: 24, fontFamily: 'Arial, Helvetica, sans-serif' }}>
      <h1>AI Active Learning Platform — Frontend Demo</h1>
      <ModelsStatus />
      <LearnerProgress />
      <TranscriptSummary />
      <AdaptiveQuiz />
      <MyLectures />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ padding: 12 }}>
        <nav>
          <Link to="/">Home</Link> | <Link to="/lecture">Lecture Page</Link>
        </nav>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/lecture" element={<LecturePage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
