from flask import Flask, jsonify, request
from models import get_all, get_by_id, create, update, delete

app = Flask(__name__)


# Basic 404 handler for consistent error JSON.
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404


# GET all users.
@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(get_all())


# GET single user by ID.
@app.route('/api/users/<id>', methods=['GET'])
def get_user(id):
    user = get_by_id(id)
    if user:
        return jsonify(user)
    # Triggers the 404 handler.
    return not_found("User not found")


# POST new user - with JSON validation.
@app.route('/api/users', methods=['POST'])
def create_user():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    new_user = create(name, email)
    if not new_user:
        return jsonify({"error": "Failed to create user"}), 400

    # 201 Created with Location header (REST best practice).
    response = jsonify(new_user)
    response.status_code = 201
    response.headers["Location"] = f"/api/users/{new_user['id']}"
    return response


# PUT update user by ID.
@app.route('/api/users/<id>', methods=['PUT'])
def update_user(id):
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    updated_user = update(id, name, email)
    if not updated_user:
        # Triggers 404.
        return not_found("User not found")

    return jsonify(updated_user)


# DELETE user by ID.
@app.route('/api/users/<id>', methods=['DELETE'])
def delete_user(id):
    if delete(id):
        return '', 204  # No Content
    # Triggers 404.
    return not_found("User not found")


if __name__ == '__main__':
    # Run on 0.0.0.0 for Docker access, no debug in prod.
    app.run(host="0.0.0.0", port=5000)