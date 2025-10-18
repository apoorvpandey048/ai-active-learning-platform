# Backend - AI-Powered Active Learning Platform

Flask-based Python backend for the AI-Powered Active Learning Platform.

## Features

- **Text Summarization** (`/summarize`): Uses Hugging Face models to summarize video transcripts
- **Quiz Generation** (`/generate-quiz`): Produces multiple-choice questions from text content
- **Cognitive Load Management** (`/cognitive-load`): Chunks text for optimal learning

## Setup

This backend is a minimal Flask app. To set it up locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The app exposes a simple health endpoint:

GET /health — returns JSON { status: 'healthy', message: 'Flask API is running' }

## API Endpoints

The following endpoints are planned for the backend (to be implemented):

- `POST /summarize` — summarize text or transcript using an LLM/HF model
- `POST /generate-quiz` — generate multiple-choice questions from text
- `POST /cognitive-load` — chunk text for cognitive-load-aware delivery

These endpoints are currently placeholders in the project roadmap.
