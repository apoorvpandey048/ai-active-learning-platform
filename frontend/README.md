# Frontend - AI-Powered Active Learning Platform

React-based frontend for the AI-Powered Active Learning Platform.

## Features

- **Video Transcript Summarization**: Displays summarized content from video lectures
- **Adaptive Quizzes**: Interactive quiz component with adaptive difficulty
- **Learner Progress**: Charts and visualizations showing learning progress

## Setup

This frontend is a React app. At minimum you'll need Node.js and npm/yarn.

Install dependencies (example using npm):

```bash
npm install
```

Install Recharts (used by some components):

```bash
npm install recharts
```

Run the development server:

```bash
npm install
npm start
```

Build for production:

```bash
npm run build
```

## Components

### LearnerProgress

A responsive chart component showing sample learner metrics (mastery, engagement, accuracy) using Recharts. It includes labels, tooltips, legends, and animations.

Location: `src/components/LearnerProgress.js`

Basic usage:

```jsx
import React from 'react';
import LearnerProgress from './src/components/LearnerProgress';

function App() {
	return (
		<div>
			<LearnerProgress />
		</div>
	);
}

export default App;
```

The component accepts an optional `data` prop to override the built-in sample dataset. Each data point should have the shape:

```js
{ week: 'Week 1', mastery: 20, engagement: 30, accuracy: 60 }
```
