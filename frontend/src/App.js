import React from 'react';
import LearnerProgress from './components/LearnerProgress';
import TranscriptSummary from './components/TranscriptSummary';
import AdaptiveQuiz from './components/AdaptiveQuiz';
import YouTubeLecture from './components/YouTubeLecture';
import MyLectures from './components/MyLectures';

export default function App() {
  return (
    <div style={{ padding: 24, fontFamily: 'Arial, Helvetica, sans-serif' }}>
      <h1>AI Active Learning Platform — Frontend Demo</h1>
  <LearnerProgress />
  <TranscriptSummary />
  <AdaptiveQuiz />
  <YouTubeLecture />
  <MyLectures />
    </div>
  );
}
