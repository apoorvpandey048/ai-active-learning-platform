import requests
import json
import time

BASE = 'http://localhost:5000'


def wait_for_health(timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(BASE + '/health', timeout=2)
            if r.status_code == 200:
                print('health:', r.json())
                return True
        except Exception as e:
            pass
        time.sleep(0.5)
    print('health: timed out waiting for server')
    return False


def post_init_and_seed():
    try:
        r = requests.post(BASE + '/init-db', timeout=10)
        print('/init-db ->', r.status_code, r.text)
    except Exception as e:
        print('/init-db error', e)
    try:
        r = requests.post(BASE + '/seed-db', timeout=30)
        print('/seed-db ->', r.status_code)
        try:
            print(json.dumps(r.json(), indent=2))
        except Exception:
            print(r.text)
    except Exception as e:
        print('/seed-db error', e)


endpoints = [
    ('fetch-transcript', 'POST', {'url': 'https://youtu.be/dQw4w9WgXcQ'}),
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
            r = requests.get(url, timeout=10)
        else:
            r = requests.post(url, json=payload, timeout=20)
        print(f'== {method} {ep} ==')
        print(r.status_code)
        try:
            print(json.dumps(r.json(), indent=2))
        except Exception:
            print(r.text)
    except Exception as e:
        print(f'Error calling {ep}: {e}')


if __name__ == '__main__':
    if not wait_for_health(15):
        raise SystemExit('server not healthy')
    post_init_and_seed()
    for ep, method, payload in endpoints:
        call(ep, method, payload)
