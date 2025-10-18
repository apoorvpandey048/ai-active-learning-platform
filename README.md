# ai-active-learning-platform
Prototype for an AI-Powered Active Learning Platform that converts video lectures into interactive, retention-optimized learning through summarization, adaptive quizzes, and cognitive load management.

## Repository layout

- `backend/` - Flask-based backend (API endpoints, inference hooks)
- `frontend/` - React-based frontend and demo components
- `docs/` - project documentation and literature review

## Quickstart

Prerequisites: Python 3.11+, Node.js 18+ (or compatible), npm/yarn

Start the backend (from the `backend` folder):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Start the frontend (from the `frontend` folder):

```bash
npm install
npm start
```

This will open a small demo frontend (webpack dev server) with the `LearnerProgress` component wired in.

## Contributing

See `docs/` for design notes and the literature review. If you add features, please include tests and update the README with usage details.
