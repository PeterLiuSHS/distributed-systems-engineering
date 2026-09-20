"""
Baseline client without any resilience patterns for Part A testing.
"""
import requests
import time
import os
from datetime import datetime

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000/data')
TIMEOUT = 2  # seconds

def make_request():
    """Make simple HTTP request to backend without any resilience patterns"""
    try:
        start_time = time.time()
        response = requests.get(BACKEND_URL, timeout=TIMEOUT)
        response_time = round((time.time() - start_time) * 1000, 2)

        if response.status_code == 200:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] SUCCESS | Response: {response.json()} | Time: {response_time}ms")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] HTTP {response.status_code} | Error: {response.text.strip()}")

    except requests.exceptions.Timeout:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] TIMEOUT | Request exceeded {TIMEOUT}s timeout")
    except requests.exceptions.ConnectionError:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] CONNECTION ERROR | Cannot reach backend service")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] UNEXPECTED ERROR | {str(e)}")

if __name__ == '__main__':
    print("Starting baseline client (no resilience patterns)")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 60)

    request_count = 0
    while True:
        request_count += 1
        print(f"Request #{request_count}: ", end="")
        make_request()
        time.sleep(2)