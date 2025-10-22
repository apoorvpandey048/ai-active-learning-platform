import os
import time
import requests
import pytest

# Read base URL from environment so CI can point tests at a deployed backend
API_BASE = os.environ.get("API_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
HEALTH_URL = f"{API_BASE}/health"
TIMEOUT = float(os.environ.get("API_TIMEOUT", "3"))
RETRY_SECONDS = int(os.environ.get("API_HEALTH_RETRY_SECONDS", "0"))


def is_backend_up(url=HEALTH_URL, timeout=TIMEOUT):
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code == 200
    except requests.RequestException:
        return False


@pytest.fixture(scope="session", autouse=True)
def require_backend():
    # Optional short wait loop useful for cold-starting remote services
    if RETRY_SECONDS > 0:
        deadline = time.time() + RETRY_SECONDS
        while time.time() < deadline:
            if is_backend_up():
                break
            time.sleep(0.5)
    if not is_backend_up():
        pytest.skip(f"Backend not reachable at {API_BASE} - skipping integration tests")


def test_health():
    r = requests.get(HEALTH_URL, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.json().get('status') == 'healthy'


def test_seed_and_generate_quiz():
    seed_url = f"{API_BASE}/seed-questions"
    r = requests.post(seed_url, json={}, timeout=TIMEOUT)
    assert r.status_code in (200, 201, 202)

    gen_url = f"{API_BASE}/generate-quiz"
    r2 = requests.get(gen_url, timeout=TIMEOUT)
    assert r2.status_code == 200
    data = r2.json()
    assert 'questions' in data