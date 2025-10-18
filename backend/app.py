from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Optional imports for Hugging Face integrations. These are imported lazily so the app
# can still run without large ML dependencies during development.
_hf_summarizer = None
_hf_generator = None
_hf_available = False
try:
    from transformers import pipeline
    _hf_available = True
except Exception:
    _hf_available = False


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Flask API is running'
    })


@app.route('/summarize', methods=['POST'])
def summarize():
    """Naive/mock summarization endpoint.

    Accepts JSON: { "text": "..." }
    Returns: { "summary": "..." }
    """
    payload = request.get_json(force=True, silent=True) or {}
    text = payload.get('text') or payload.get('transcript')
    if not text:
        return jsonify({'error': 'Missing "text" in request body'}), 400

    # If transformers is available, use an abstractive summarization pipeline.
    if _hf_available:
        global _hf_summarizer
        try:
            if _hf_summarizer is None:
                # Use a small summarization model by default. This will download model files on first run.
                _hf_summarizer = pipeline('summarization', model='sshleifer/distilbart-cnn-12-6')
            # Transformers summarizers usually accept long text; we truncate for quick response.
            hf_input = text if len(text) < 1000 else text[:1000]
            result = _hf_summarizer(hf_input, max_length=120, min_length=30, do_sample=False)
            summary = result[0]['summary_text']
            return jsonify({'summary': summary, 'source': 'huggingface'})
        except Exception:
            # Fall back to naive heuristic below on any transformer error.
            pass

    # Very simple heuristic summary as a fallback: first 2 sentences or first 200 chars
    sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if s.strip()]
    if len(sentences) >= 2:
        summary = '. '.join(sentences[:2]).strip() + '.'
    else:
        summary = (text[:200].strip() + '...') if len(text) > 200 else text

    return jsonify({'summary': summary, 'source': 'heuristic'})


@app.route('/generate-quiz', methods=['POST'])
def generate_quiz():
    """Mock MCQ generator.

    Accepts JSON: { "text": "..." }
    Returns: { "questions": [ {question, options, answerIndex} ] }
    """
    payload = request.get_json(force=True, silent=True) or {}
    text = payload.get('text')
    if not text:
        return jsonify({'error': 'Missing "text" in request body'}), 400

    # If transformers is available, attempt to produce MCQs using a text2text model.
    if _hf_available:
        global _hf_generator
        try:
            if _hf_generator is None:
                # Use a small seq2seq model; this is best-effort and may require adjustments
                _hf_generator = pipeline('text2text-generation', model='google/flan-t5-small')

            prompt = f"Generate 2 multiple-choice questions (provide options and correct answer index) from the following text:\n\n{text}\n\nOutput as JSON: [{'{'}\"question\":\"...\", \"options\": [...], \"answerIndex\": 0{'}'}]"
            res = _hf_generator(prompt, max_length=256, do_sample=False)
            # Try to parse JSON-like output. This is brittle; if parsing fails we fall back.
            import json
            out_text = res[0]['generated_text'] if isinstance(res, list) else str(res)
            # Extract JSON array from the generated text
            start = out_text.find('[')
            end = out_text.rfind(']')
            if start != -1 and end != -1 and end > start:
                json_str = out_text[start:end+1]
                try:
                    questions = json.loads(json_str)
                    return jsonify({'questions': questions, 'source': 'huggingface'})
                except Exception:
                    pass
        except Exception:
            # Fall through to mock
            pass

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
