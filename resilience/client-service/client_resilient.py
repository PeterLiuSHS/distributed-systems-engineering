"""
Resilient client implementing Circuit Breaker and Retry patterns with detailed logging
"""
import requests
import time
import os
from datetime import datetime
from pybreaker import CircuitBreaker, CircuitBreakerError
from tenacity import retry, wait_exponential_jitter, stop_after_attempt, retry_if_exception_type

# Configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000/data')
TIMEOUT = 2

# Circuit Breaker Configuration
circuit_breaker = CircuitBreaker(
    fail_max=3,           # Open after 3 consecutive failures
    reset_timeout=15      # Wait 15 seconds before attempting to close
)

class BackendCallError(Exception):
    """Custom exception for backend call failures"""
    pass

# Global variable to track retry attempts across function calls
current_retry_attempts = {}

def log_retry_attempt(retry_state):
    """Callback function to log retry attempts"""
    if retry_state.fn.__name__ not in current_retry_attempts:
        current_retry_attempts[retry_state.fn.__name__] = 0
    current_retry_attempts[retry_state.fn.__name__] = retry_state.attempt_number

    wait_time = getattr(retry_state.next_action, 'sleep', 0) if hasattr(retry_state, 'next_action') else 0
    print(f"  [RETRY] Attempt #{retry_state.attempt_number}, next retry in {wait_time:.1f}s")

@circuit_breaker
@retry(
    wait=wait_exponential_jitter(initial=1, max=4),  # Exponential backoff with jitter: 1s, 2s, 4s
    stop=stop_after_attempt(3),                      # Max 3 retry attempts (1 original + 2 retries)
    retry=retry_if_exception_type(BackendCallError), # Only retry on specific exceptions
    before_sleep=log_retry_attempt                   # Log before each retry attempt
)
def call_backend_with_retry():
    """
    Make resilient call to backend with retry logic and circuit breaker protection
    """
    try:
        start_time = time.time()
        response = requests.get(BACKEND_URL, timeout=TIMEOUT)
        response_time = round((time.time() - start_time) * 1000, 2)

        if response.status_code == 200:
            return {
                "status": "success",
                "data": response.json(),
                "response_time": response_time
            }
        else:
            # Raise exception for non-200 status to trigger retry/circuit breaker
            raise BackendCallError(f"HTTP {response.status_code}: {response.text}")

    except requests.exceptions.Timeout:
        raise BackendCallError(f"Request timeout after {TIMEOUT}s")
    except requests.exceptions.ConnectionError:
        raise BackendCallError("Connection error - cannot reach backend")
    except Exception as e:
        raise BackendCallError(f"Unexpected error: {str(e)}")

def make_resilient_request():
    """Make request with resilience patterns"""
    # Reset retry counter for this request
    current_retry_attempts['call_backend_with_retry'] = 0

    try:
        result = call_backend_with_retry()
        total_attempts = current_retry_attempts.get('call_backend_with_retry', 0) + 1
        if total_attempts > 1:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] SUCCESS after {total_attempts} attempts | "
                  f"Response: {result['data']} | Time: {result['response_time']}ms | "
                  f"Circuit State: {circuit_breaker.state}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] SUCCESS | "
                  f"Response: {result['data']} | Time: {result['response_time']}ms | "
                  f"Circuit State: {circuit_breaker.state}")

    except CircuitBreakerError:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] CIRCUIT OPEN | "
              f"Requests blocked by circuit breaker | "
              f"Circuit State: {circuit_breaker.state}")
    except Exception as e:
        total_attempts = current_retry_attempts.get('call_backend_with_retry', 0) + 1
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ALL {total_attempts} ATTEMPTS FAILED | "
              f"Error: {str(e)} | Circuit State: {circuit_breaker.state}")

if __name__ == '__main__':
    print("Starting resilient client (with Circuit Breaker + Retry patterns)")
    print(f"Backend URL: {BACKEND_URL}")
    print("Circuit Breaker Config: fail_max=3, reset_timeout=15")
    print("Retry Config: exponential backoff with jitter, max_attempts=3")
    print("=" * 80)

    request_count = 0
    while True:
        request_count += 1
        print(f"Request #{request_count}:")
        make_resilient_request()
        time.sleep(2)