import requests
import os

BACKEND = os.environ.get('BACKEND_URL', 'http://127.0.0.1:5000')

if __name__ == '__main__':
    try:
        h = requests.get(BACKEND + '/health', timeout=10).text
        print('health:', h)
    except Exception as e:
        print('health check failed:', e)
    try:
        ms = requests.get(BACKEND + '/models/status', timeout=20)
        print('models/status:', ms.status_code)
        try:
            print(ms.json())
        except Exception:
            print(ms.text)
    except Exception as e:
        print('models status failed:', e)
