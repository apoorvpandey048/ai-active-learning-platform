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

## API Endpoints (implemented)

This backend contains lightweight/demo implementations of the key endpoints. They are suitable for prototyping and demoing the frontend. For production use you should replace the mock/heuristic logic with robust model-backed implementations.

- `POST /summarize` — Accepts JSON { "text": "..." } and returns { "summary": "...", "source": "heuristic|huggingface" }. If `transformers` is installed, the server attempts to use a Hugging Face summarization pipeline (model download required on first run). Otherwise it falls back to a simple heuristic summary.

- `POST /generate-quiz` — Accepts JSON { "text": "..." } and returns { "questions": [...] , "source": "mock|huggingface" }. If `transformers` is available the server will attempt to generate MCQs using a text2text model and parse JSON output. Fallback returns placeholder MCQs.

- `POST /cognitive-load` — Accepts JSON { "text": "...", "max_chunk_chars": 300 } and returns { "chunks": [...], "readability_flesch": <score|null> }. The endpoint chunks text into segments and (optionally) computes a Flesch reading ease score if `textstat` is installed.

Note: Enabling Hugging Face models requires `transformers` and a model backend (e.g., `torch`). These are listed in `requirements.txt` but are optional; the Flask app will still run without them.
