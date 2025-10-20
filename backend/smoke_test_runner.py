#!/usr/bin/env python3
"""
Smoke test runner for the AI Active Learning Platform backend.

This script will:
- call /init-db and /seed-db to ensure the SQLite DB is initialized and populated
- call /health to verify the server is up
- exercise the main endpoints, using force_mock=True for ML-backed endpoints

Run this after starting the backend server.
"""
import requests
import time
import sys
import json

BASE = 'http://localhost:5000'

def call(method, path, payload=None, expect_status=200, timeout=30):
    url = BASE + path
    try:
        if method == 'GET':
            r = requests.get(url, timeout=timeout)
        else:
            r = requests.post(url, json=payload or {}, timeout=timeout)
    except Exception as e:
        print(f'ERROR: {method} {path} -> exception: {e}')
        return False, None

    ok = (r.status_code == expect_status)
    body = None
    try:
        body = r.json()
    except Exception:
        body = r.text
    print(f'== {method} {path} ==')
    print('status:', r.status_code)
    print(json.dumps(body, indent=2) if isinstance(body, dict) else body)
    return ok, body


def main():
    # Wait a short moment to allow server to be ready
    print('Waiting 1s for server warm-up...')
    time.sleep(1)

    ok, _ = call('GET', '/health', expect_status=200)
    if not ok:
        print('Health check failed; aborting smoke tests.')
        sys.exit(2)

    # Initialize DB schema
    print('\nCalling /init-db to ensure schema exists...')
    call('POST', '/init-db', payload={})

    # Seed DB with Faker data
    print('\nCalling /seed-db to populate sample data...')
    call('POST', '/seed-db', payload={})

    # Define endpoints to test. Use force_mock for heavy model endpoints.
    endpoints = [
        ('POST', '/fetch-transcript', {'url': 'https://youtu.be/dQw4w9WgXcQ'}),
        ('POST', '/summarize', {'text': 'This is a test transcript. It has several sentences. We want a short summary.', 'force_mock': True}),
        ('POST', '/generate-quiz', {'text': 'Supervised learning aims to predict labels for new data.', 'force_mock': True}),
        ('GET', '/generate-quiz', None),
        ('POST', '/save-progress', {'user_id': 1, 'mastery': 60, 'engagement': 70, 'accuracy': 65}),
        ('GET', '/analyze-performance', None),
        ('POST', '/save-lecture', {'title': 'Test Lecture', 'video_url': 'https://youtu.be/dQw4w9WgXcQ', 'transcript': 'Dummy transcript', 'summary': 'Dummy summary'}),
        ('GET', '/my-lectures', None),
    ]

    all_ok = True
    for method, path, payload in endpoints:
        ok, _ = call(method, path, payload)
        if not ok:
            all_ok = False

    if not all_ok:
        print('\nSome endpoint checks failed. See output above and backend.log for details.')
        sys.exit(3)

    print('\nAll endpoint checks succeeded (using mocked ML endpoints where requested).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
