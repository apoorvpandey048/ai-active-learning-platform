import requests
import json

BASE = 'http://localhost:5000'

endpoints = [
    ('fetch-transcript', 'POST', {'url': 'https://youtu.be/dQw4w9WgXcQ'}),
    # Force mock to avoid HF model loading during tests
    ('summarize', 'POST', {'text': 'This is a test transcript. It has several sentences. We want a short summary.', 'force_mock': True}),
    ('generate-quiz', 'POST', {'text': 'Supervised learning aims to predict labels for new data.', 'force_mock': True}),
    ('generate-quiz', 'GET', None),
    ('save-progress', 'POST', {'user_id': 1, 'week': 'Week 1', 'mastery': 60, 'engagement': 70, 'accuracy': 65}),
    ('analyze-performance', 'GET', None),
    ('save-lecture', 'POST', {'title': 'Test Lecture', 'video_url': 'https://youtu.be/dQw4w9WgXcQ', 'transcript': 'Dummy transcript', 'summary': 'Dummy summary'}),
    ('my-lectures', 'GET', None),
]


def call(ep, method, payload=None):
    url = BASE + '/' + ep
    try:
        if method == 'GET':
            r = requests.get(url, timeout=30)
        else:
            r = requests.post(url, json=payload, timeout=30)
        print(f'== {method} {ep} ==')
        print(r.status_code)
        try:
            print(json.dumps(r.json(), indent=2))
        except Exception:
            print(r.text)
    except Exception as e:
        print(f'Error calling {ep}: {e}')


if __name__ == '__main__':
    for ep, method, payload in endpoints:
        call(ep, method, payload)
