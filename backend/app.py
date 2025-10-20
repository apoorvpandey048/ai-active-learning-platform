from flask import Flask, jsonify, request
from flask_cors import CORS

# SQLAlchemy imports are optional at import-time because some Python
# environments (e.g. very new Python versions) may not be compatible with
# the installed SQLAlchemy wheel. Import lazily and fall back gracefully.
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.sql import func
    DB_AVAILABLE = True
except Exception:
    create_engine = None
    sessionmaker = None
    func = None
    DB_AVAILABLE = False
import json
import threading
import time
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger('backend')

app = Flask(__name__)
CORS(app)

# Database setup (only if SQLAlchemy imported successfully)
DB_URL = 'sqlite:///ai_active_learning.db'
engine = None
SessionLocal = None
if DB_AVAILABLE and create_engine is not None and sessionmaker is not None:
    try:
        engine = create_engine(DB_URL, echo=False)
        SessionLocal = sessionmaker(bind=engine)
    except Exception:
        # If engine creation fails, treat DB as unavailable but keep app running
        engine = None
        SessionLocal = None
        DB_AVAILABLE = False

try:
    # Import models to ensure tables are registered
    from models import Base
    Base.metadata.create_all(bind=engine)
except Exception:
    # Models may not be available if SQLAlchemy isn't installed — we'll handle that later
    pass

# Optional imports for Hugging Face integrations. These are imported lazily so the app
# can still run without large ML dependencies during development.
_hf_summarizer = None
_hf_generator = None
# Flags to indicate whether a pipeline has finished loading
_hf_summarizer_ready = False
_hf_generator_ready = False

# Whether transformers is importable at all
_hf_available = False
try:
    from transformers import pipeline
    _hf_available = True
except Exception:
    _hf_available = False

# Configurable model names (small/lightweight defaults)
SUMMARIZER_MODEL = 'sshleifer/distilbart-cnn-12-6'
GENERATOR_MODEL = 'google/flan-t5-small'


def _background_load_models():
    """Load HF pipelines in a background thread so first-request latency
    doesn't block the server startup. Sets readiness flags when done.
    """
    global _hf_summarizer, _hf_generator
    global _hf_summarizer_ready, _hf_generator_ready

    if not _hf_available:
        logger.info('background_load: transformers not available; skipping model load')
        return

    # Load summarizer
    try:
        logger.info('background_load: starting to load summarizer model %s', SUMMARIZER_MODEL)
        _hf_summarizer = pipeline('summarization', model=SUMMARIZER_MODEL)
        _hf_summarizer_ready = True
        logger.info('background_load: summarizer ready')
    except Exception as e:
        _hf_summarizer = None
        _hf_summarizer_ready = False
        logger.exception('background_load: summarizer load failed: %s', e)

    # Load generator
    try:
        logger.info('background_load: starting to load generator model %s', GENERATOR_MODEL)
        _hf_generator = pipeline('text2text-generation', model=GENERATOR_MODEL)
        _hf_generator_ready = True
        logger.info('background_load: generator ready')
    except Exception as e:
        _hf_generator = None
        _hf_generator_ready = False
        logger.exception('background_load: generator load failed: %s', e)


# Start background loading thread (daemon) so it doesn't block process exit.
import os

# Only attempt background HF model loading if explicitly enabled via env var.
# This avoids crashing or consuming too much memory in limited CI/dev environments.
ENABLE_HF_BACKGROUND = os.environ.get('ENABLE_HF_BACKGROUND', '0') == '1'

if _hf_available and ENABLE_HF_BACKGROUND:
    try:
        t = threading.Thread(target=_background_load_models, daemon=True)
        t.start()
        logger.info('startup: background HF model loader started')
    except Exception as e:
        logger.exception('startup: failed to start background loader: %s', e)
else:
    logger.info('startup: HF background loading disabled (ENABLE_HF_BACKGROUND=%s, transformers_available=%s)', ENABLE_HF_BACKGROUND, _hf_available)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Flask API is running'
    })


@app.route('/models/status', methods=['GET'])
def models_status():
    """Return the HF model availability and readiness state."""
    return jsonify({
        'transformers_available': _hf_available,
        'summarizer_ready': _hf_summarizer_ready,
        'generator_ready': _hf_generator_ready,
        'background_loading_enabled': os.environ.get('ENABLE_HF_BACKGROUND', '0') == '1',
        'summarizer_model': SUMMARIZER_MODEL,
        'generator_model': GENERATOR_MODEL,
    })


@app.route('/test-db', methods=['GET'])
def test_db():
    try:
        if not DB_AVAILABLE or SessionLocal is None:
            return jsonify({'db': 'unavailable', 'error': 'Database not configured or unsupported in this environment'}), 503
        from models import User
        session = SessionLocal()
        user = session.query(User).first()
        session.close()
        return jsonify({'db': 'connected', 'user_exists': bool(user)})
    except Exception as e:
        return jsonify({'db': 'error', 'error': str(e)}), 500


@app.route('/init-db', methods=['POST'])
def init_db_route():
    try:
        # Initialize the database schema using db_init.init_db()
        from db_init import init_db
        if not DB_AVAILABLE:
            return jsonify({'error': 'Database not available in this environment'}), 503
        engine = init_db()
        # Log and return success
        print('init-db: database initialized using engine=%s' % (engine,))
        return jsonify({'message': 'DB initialized', 'db_url': DB_URL})
    except Exception as e:
        print('init-db: error -', str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/seed-db', methods=['POST'])
def seed_db_route():
    try:
        # Seed the database with Faker data. The db_init.seed_questions function
        # is idempotent in the sense that it will create new records each time
        # but will not fail if called multiple times (it uses SQLAlchemy sessions).
        from db_init import seed_questions
        if not DB_AVAILABLE:
            return jsonify({'error': 'Database not available in this environment'}), 503

        # Call the seeding logic and then report counts back to caller.
        seed_questions()

        # After seeding, compute counts for reporting
        try:
            from models import User, Lecture, Question
            session = SessionLocal()
            ucount = session.query(User).count()
            lcount = session.query(Lecture).count()
            qcount = session.query(Question).count()
            session.close()
        except Exception:
            ucount = lcount = qcount = None

        msg = {'message': 'DB seeded', 'users': ucount, 'lectures': lcount, 'questions': qcount}
        print('seed-db:', msg)
        return jsonify(msg)
    except Exception as e:
        print('seed-db: error -', str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/summarize', methods=['POST'])
def summarize():
    """Naive/mock summarization endpoint.

    Accepts JSON: { "text": "..." }
    Returns: { "summary": "..." }
    """
    payload = request.get_json(force=True, silent=True) or {}
    text = payload.get('text') or payload.get('transcript')
    force_mock = payload.get('force_mock') if isinstance(payload, dict) else False
    if not text:
        return jsonify({'error': 'Missing "text" in request body'}), 400

    # If forced mock is requested, always return a quick placeholder
    if force_mock:
        return jsonify({'summary': 'Mock summary (force_mock=True)', 'source': 'mock'})

    # If HF isn't available at all, fall back to heuristic immediately
    if not _hf_available:
        print('summarize: transformers not available, using heuristic')
    else:
        # If model is not yet ready, inform caller to retry or return mock
        if not _hf_summarizer_ready or _hf_summarizer is None:
            print('summarize: summarizer not ready yet')
            return jsonify({'message': 'Model loading, please try again later', 'source': 'loading'}), 202
        # Use the pre-loaded summarizer pipeline
        try:
            hf_input = text if len(text) < 1000 else text[:1000]
            result = _hf_summarizer(hf_input, max_length=120, min_length=30, do_sample=False)
            summary = result[0]['summary_text']
            return jsonify({'summary': summary, 'source': 'huggingface'})
        except Exception as ex:
            print('summarize: error during HF summarization -', str(ex))
            # Fall through to heuristic

    # Very simple heuristic summary as a fallback: first 2 sentences or first 200 chars
    sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if s.strip()]
    if len(sentences) >= 2:
        summary = '. '.join(sentences[:2]).strip() + '.'
    else:
        summary = (text[:200].strip() + '...') if len(text) > 200 else text

    return jsonify({'summary': summary, 'source': 'heuristic'})


@app.route('/generate-quiz', methods=['GET', 'POST'])
def generate_quiz():
    """Mock MCQ generator.

    Accepts JSON: { "text": "..." }
    Returns: { "questions": [ {question, options, answerIndex} ] }
    """
    # Support both DB-backed random quiz (GET) and text-based generation (POST)
    if request.method == 'GET':
        # Return 5 random questions from DB
        try:
            if not DB_AVAILABLE or SessionLocal is None:
                raise RuntimeError('DB unavailable')
            from models import Question
            session = SessionLocal()
            qs = session.query(Question).order_by(func.random()).limit(5).all()
            out = []
            for q in qs:
                # models may store options differently; best-effort extraction
                try:
                    opts = json.loads(getattr(q, 'options', '[]'))
                except Exception:
                    opts = []
                out.append({'id': getattr(q, 'id', None), 'topic': getattr(q, 'topic', None), 'question_text': getattr(q, 'question_text', None), 'options': opts})
            session.close()
            return jsonify({'questions': out})
        except Exception:
            # Fall back to mock if DB not available
            pass

    payload = request.get_json(force=True, silent=True) or {}
    text = payload.get('text')
    # For POST text-based generation ensure text present
    if request.method == 'POST' and not text:
        return jsonify({'error': 'Missing "text" in request body'}), 400

    # If forced mock is requested, return mock quickly
    force_mock = payload.get('force_mock') if isinstance(payload, dict) else False
    if force_mock:
        return jsonify({'questions': [
            {'question': 'Mock question 1', 'options': ['A', 'B', 'C', 'D'], 'answerIndex': 0},
            {'question': 'Mock question 2', 'options': ['A', 'B', 'C', 'D'], 'answerIndex': 1}
        ], 'source': 'mock'})

    # If HF not available, fall back to mock
    if not _hf_available:
        print('generate_quiz: transformers not available, returning mock')
    else:
        # If generator model hasn't finished loading yet, inform client
        if not _hf_generator_ready or _hf_generator is None:
            print('generate_quiz: generator not ready yet')
            return jsonify({'message': 'Model loading, please try again later', 'source': 'loading'}), 202
        # Use the pre-loaded generator
        try:
            prompt = f"Generate 2 multiple-choice questions (provide options and correct answer index) from the following text:\n\n{text}\n\nOutput as JSON array"
            res = _hf_generator(prompt, max_length=256, do_sample=False)
            out_text = res[0]['generated_text'] if isinstance(res, list) else str(res)
            # Best-effort JSON extraction
            start = out_text.find('[')
            end = out_text.rfind(']')
            if start != -1 and end != -1 and end > start:
                json_str = out_text[start:end+1]
                try:
                    questions = json.loads(json_str)
                    return jsonify({'questions': questions, 'source': 'huggingface'})
                except Exception:
                    print('generate_quiz: failed to parse HF output, falling back to mock')
        except Exception as ex:
            print('generate_quiz: error during HF generation -', str(ex))
            # Fall through to mock below

    # Fallback mock questions
    questions = [
        {
            'question': 'What is the main topic discussed in the text?',
            'options': [
                'An unrelated topic',
                'A core concept from the input text',
                'Random trivia',
                'None of the above'
            ],
            'answerIndex': 1
        },
        {
            'question': 'Which strategy was recommended?',
            'options': ['Strategy A', 'Strategy B', 'Strategy C', 'Strategy D'],
            'answerIndex': 2
        }
    ]

    return jsonify({'questions': questions, 'source': 'mock'})


@app.route('/seed-questions', methods=['GET'])
def seed_questions_route():
    try:
        from db_init import seed_questions
        seed_questions()
        return jsonify({'message': 'Questions seeded'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/save-progress', methods=['POST'])
def save_progress():
    payload = request.get_json(force=True, silent=True) or {}
    user_id = payload.get('user_id', 1)
    week = payload.get('week')
    mastery = int(payload.get('mastery', 0))
    engagement = int(payload.get('engagement', 0))
    accuracy = int(payload.get('accuracy', 0))
    try:
        if not DB_AVAILABLE or SessionLocal is None:
            return jsonify({'error': 'Database not available in this environment'}), 503
        from models import QuizResult
        session = SessionLocal()
        # Save as a QuizResult with score mapped from mastery (demo mapping)
        score = mastery
        qr = QuizResult(user_id=user_id, lecture_id=payload.get('lecture_id'), score=score)
        session.add(qr)
        session.commit()
        session.close()
        return jsonify({'message': 'Progress (quiz result) saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/save-lecture', methods=['POST'])
def save_lecture():
    payload = request.get_json(force=True, silent=True) or {}
    title = payload.get('title')
    # Accept either video_url or yt_url and normalize
    video_url = payload.get('video_url') or payload.get('yt_url')
    transcript = payload.get('transcript')
    summary = payload.get('summary')
    try:
        if not DB_AVAILABLE or SessionLocal is None:
            return jsonify({'error': 'Database not available in this environment'}), 503
        from models import Lecture
        session = SessionLocal()
        lec = Lecture(title=title, yt_url=video_url, transcript=transcript, summary=summary)
        session.add(lec)
        session.commit()
        lid = lec.id
        session.close()
        return jsonify({'message': 'Lecture saved', 'lecture_id': lid})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/my-lectures', methods=['GET'])
def my_lectures():
    try:
        if not DB_AVAILABLE or SessionLocal is None:
            return jsonify({'error': 'Database not available in this environment'}), 503
        from models import Lecture
        session = SessionLocal()
        qs = session.query(Lecture).all()
        out = []
        for l in qs:
            out.append({'id': l.id, 'title': l.title, 'video_url': l.yt_url, 'transcript': l.transcript, 'summary': l.summary})
        session.close()
        return jsonify({'lectures': out})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analyze-performance', methods=['GET'])
def analyze_performance():
    try:
        if not DB_AVAILABLE or SessionLocal is None:
            return jsonify({'error': 'Database not available in this environment'}), 503
        from models import QuizResult
        session = SessionLocal()
        qs = session.query(QuizResult).all()
        data = {}
        for q in qs:
            wk = q.date.date().isoformat() if q.date else 'unknown'
            if wk not in data:
                data[wk] = {'scores': []}
            data[wk]['scores'].append(q.score or 0)
        weeks = sorted(data.keys())
        mastery = [int(sum(data[w]['scores'])/len(data[w]['scores'])) if data[w]['scores'] else 0 for w in weeks]
        # For demo purposes use mastery for all three metrics
        engagement = mastery[:]
        accuracy = mastery[:]
        session.close()
        return jsonify({'weeks': weeks, 'mastery': mastery, 'engagement': engagement, 'accuracy': accuracy})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/fetch-transcript', methods=['POST'])
def fetch_transcript():
    payload = request.get_json(force=True, silent=True) or {}
    url = payload.get('url') or payload.get('video_url')
    if not url:
        return jsonify({'error': 'Missing "url" in request body'}), 400

    # Try to extract transcript using youtube_transcript_api if installed
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        # extract video id from URL
        import re
        m = re.search(r'(?:v=|youtu\.be/)([A-Za-z0-9_-]{6,})', url)
        vid = m.group(1) if m else url
        transcript_list = YouTubeTranscriptApi.get_transcript(vid)
        text = ' '.join([t['text'] for t in transcript_list])
        return jsonify({'transcript': text})
    except Exception:
        # Fallback: return mock transcript
        mock = 'This is a mocked transcript. Install youtube-transcript-api for real transcripts.'
        return jsonify({'transcript': mock})


@app.route('/cognitive-load', methods=['POST'])
def cognitive_load():
    """Simple text chunking endpoint.

    Accepts JSON: { "text": "...", "max_chunk_chars": 300 }
    Returns: { "chunks": [ ... ] }
    """
    payload = request.get_json(force=True, silent=True) or {}
    text = payload.get('text')
    if not text:
        return jsonify({'error': 'Missing "text" in request body'}), 400

    max_chars = int(payload.get('max_chunk_chars', 300))
    words = text.split()
    chunks = []
    cur = []
    cur_len = 0
    for w in words:
        if cur_len + len(w) + 1 > max_chars and cur:
            chunks.append(' '.join(cur))
            cur = [w]
            cur_len = len(w) + 1
        else:
            cur.append(w)
            cur_len += len(w) + 1
    if cur:
        chunks.append(' '.join(cur))

    # Optional readability score (Flesch reading ease) if textstat is available
    readability = None
    try:
        import textstat
        readability = textstat.flesch_reading_ease(text)
    except Exception:
        readability = None

    return jsonify({'chunks': chunks, 'readability_flesch': readability})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
