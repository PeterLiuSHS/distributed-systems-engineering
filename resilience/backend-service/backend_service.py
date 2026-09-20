"""
Backend service with configurable failure modes for resilience testing.
"""
from flask import Flask, jsonify
import random
import time
import os

app = Flask(__name__)

@app.route('/data')
def get_data():
    """
    Main endpoint that simulates various failure scenarios:
    - 20% chance: 5-second delay (timeout simulation)
    - 30% chance: Internal server error
    - 50% chance: Successful response
    """
    random_value = random.random()

    if random_value < 0.4:
        # Simulate slow response (timeout scenario)
        time.sleep(5)
        return jsonify({
            "status": "success",
            "message": "Delayed response after 5 seconds",
            "data": random.randint(1, 100)
        })
    elif random_value < 0.8:
        # Simulate server error
        return jsonify({
            "error": "Internal Server Error",
            "message": "Backend service temporarily unavailable"
        }), 500
    else:
        # Successful response
        return jsonify({
            "status": "success",
            "message": "Request processed successfully",
            "data": random.randint(1, 100),
            "timestamp": time.time()
        })

@app.route('/health')
def health_check():
    """Health check endpoint for Kubernetes liveness probes"""
    return jsonify({"status": "healthy", "service": "backend"})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)