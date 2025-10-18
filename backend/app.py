from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


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

    # Very simple heuristic summary: first 2 sentences or first 200 chars
    sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if s.strip()]
    if len(sentences) >= 2:
        summary = '. '.join(sentences[:2]).strip() + '.'
    else:
        summary = (text[:200].strip() + '...') if len(text) > 200 else text

    return jsonify({'summary': summary})


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

    # Return a small sample quiz (placeholder)
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

    return jsonify({'questions': questions})


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

    return jsonify({'chunks': chunks})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
