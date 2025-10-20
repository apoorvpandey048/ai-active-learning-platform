import subprocess
import requests
import time

BASE = 'http://127.0.0.1:5000'

proc = None

def setup_module(module):
    # Start the flask app in background for tests
    global proc
    proc = subprocess.Popen(['python', 'app.py'])
    time.sleep(1)

def teardown_module(module):
    # Terminate the flask app after tests
    global proc
    if proc:
        proc.terminate()
        proc.wait()


def test_health():
    r = requests.get(BASE + '/health')
    assert r.status_code == 200
    assert r.json().get('status') == 'healthy'


def test_seed_and_generate_quiz():
    r = requests.get(BASE + '/seed-questions')
    assert r.status_code == 200
    r2 = requests.get(BASE + '/generate-quiz')
    assert r2.status_code == 200
    data = r2.json()
    assert 'questions' in data