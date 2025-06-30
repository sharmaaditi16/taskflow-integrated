from flask import request, jsonify  # Import Flask and request
from flask_cors import CORS  # Import CORS
from taskly import Taskly
from functools import wraps
import jwt
from user import User
from appconf import AppConfig
import gladiator as gl

app = AppConfig().app
CORS(app)

"""
Decorator to check if the user is authenticated.
This decorator checks if the user is logged in by verifying the JWT token.
If the token is valid, it retrieves the user ID from the token and sets it in the request context.
If the token is invalid or missing, it returns a 401 Unauthorized response.
"""
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        headers = request.headers
        token = headers.get("token")
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User().get_user_by_id(data['id'])
            user_id = current_user.json.get('user', {})
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        if 'task_id' in kwargs:
            return f(kwargs.get('task_id'),user_id)

        return f(user_id)
    return decorated

"""
Taskly API endpoints for managing tasks.
This module provides endpoints to create, retrieve, update, and delete tasks,
"""

"""
Get all tasks for a user.
This endpoint retrieves all tasks created by a specific user.
"""
@app.route('/tasks',methods=['GET']) 
@token_required
def get_tasks(user_id):
    taskly = Taskly()
    return taskly.get_tasks(user_id)

"""
Add a new task for a user.
This endpoint allows a user to create a new task by providing the task details in the request body.
"""
@app.route('/tasks', methods=['POST'])
@token_required
def add_task(user_id):
    taskly = Taskly()
    result = gl.validate(taskly.validations.task_validations, request.json)
    if str(bool(result)) is False:
        return jsonify({"error": "validations failed"}), 500

    return taskly.add_task(request, user_id)

"""
Get a specific task by ID for a user.
This endpoint retrieves a task by its ID for a specific user.
"""
@app.route('/tasks/<int:task_id>',methods=['GET'])
@token_required
def get_task_by_id_d(task_id,user_id):
    if task_id is None:
        return jsonify({"error": "task_id is required"}), 400
    taskly = Taskly()
    return taskly.get_task_by_id(task_id,user_id)

"""
Update a specific task by ID for a user.
This endpoint allows a user to update an existing task by providing the updated task details in the request body.
"""
@app.route('/tasks', methods=['PUT'])
@token_required
def update_task(user_id):
    taskly = Taskly()
    result = gl.validate(taskly.validations.task_validations, request.json)
    if str(bool(result)) is False:
        return jsonify({"error": "validations failed"}), 500
    return taskly.update_task(request, user_id)

"""
Delete a specific task by ID for a user.
This endpoint allows a user to delete a task by its ID.
"""
@app.route('/tasks/<task_id>', methods=['DELETE'])
@token_required
def delete_by_id(task_id,user_id):
    if task_id is None:
        return jsonify({"error": "task_id is required"}), 400
    taskly = Taskly()
    return taskly.delete_by_id(task_id,user_id)

"""
Create a new user.
This endpoint allows a user to create a new account by providing their user details in the request body.
"""
@app.route('/create-user', methods=['POST'])
def create_user():
    user = User()
    result = gl.validate(user.validations.user_validations, request.json)
    if str(bool(result)) is False:
        return jsonify({"error": "validations failed"}), 500
    return user.create_user(request)

"""
Gets user logged in to system against the credentials provided.
This endpoint allows a user to log in by providing their username and password in the request body.
And in response it returns a JWT token for the user.
"""
@app.route('/login',methods=['POST'])
def login():
    taskly = Taskly()
    return taskly.login(request)

"""
AI assistance bot
This endpoint allows a user to get AI-assisted task suggestions based on the provided request data.
"""
@app.route('/copilot-suggest', methods=['POST'])
@token_required
def copilot_suggest(user_id):
    return Taskly().copilot_suggest(request)

"""
AI assistance autocomplete
This endpoint allows a user to get AI-assisted task suggestions based on the provided request data.
"""
@app.route('/autocomplete', methods=['POST'])
@token_required
def autocomplete(user_id):
    taskly = Taskly()
    return taskly.autocomplete_task(request)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5000)

