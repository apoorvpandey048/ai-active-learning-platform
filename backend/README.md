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

## Safe defaults and demo mode (recommended)

By default this repo is configured for fast development and demos:

- HF model background loading is disabled by default. This avoids heavy downloads and memory usage on small machines or in CI.
- `/summarize` and `/generate-quiz` support a `force_mock` boolean in the request body. When `force_mock=true` the endpoints return instant mock responses suitable for UI demos.

Recommended local workflow for demos:

```bash
# start the backend (safe defaults)
nohup python3 app.py > backend.log 2>&1 & echo $! > backend.pid

# run the smoke tests (these use force_mock for ML endpoints)
python3 ../backend/run_smoke.py

# tail logs
tail -n 200 backend.log
```

## Enabling Hugging Face models (optional, resource-heavy)

If you want to enable real HF models and use them in the background loader:

1. Ensure you have sufficient memory and a suitable Python environment (PyTorch installed).
2. Set the environment variable `ENABLE_HF_BACKGROUND=1` before starting the server.

```bash
export ENABLE_HF_BACKGROUND=1
nohup python3 app.py > backend.log 2>&1 &
tail -f backend.log
```

The server will log when it starts loading models and when they're ready. While models are loading, endpoints without `force_mock` may return a 202 "Model loading" response. After models finish loading, requests will use the HF pipelines automatically.

## Deployment notes

For production use deploy behind a WSGI server (the included `render.yaml` uses `gunicorn`). Move database to a managed Postgres instance and use proper secrets (DATABASE_URL, HF_API_KEY) and background workers (RQ/Celery) for long-running tasks.
