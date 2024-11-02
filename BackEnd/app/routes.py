from flask import Blueprint, request, jsonify
from .models import db, Task, User

routes_blueprint = Blueprint('router', __name__)

# User Routes

# Register user
@routes_blueprint.route('/users', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists!"}), 400

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201

# Login user
@routes_blueprint.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):  # Assume check_password method exists
        return jsonify({"message": "Login successful!", "user_id": user.id, "username": user.username}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

# Get user information by ID
@routes_blueprint.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user:
        return jsonify({"id": user.id, "username": user.username}), 200
    else:
        return jsonify({'error': 'User not found!'}), 404

# Update user information by ID
@routes_blueprint.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = User.query.get(id)

    if user:
        user.username = data.get('username', user.username)
        db.session.commit()
        return jsonify({'message': 'User updated successfully!'}), 200
    else:
        return jsonify({'error': 'User not found!'}), 404

# Delete a user by ID
@routes_blueprint.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200

# Get all users
@routes_blueprint.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username} for user in users]), 200





# Task Routes

# Add a new task
@routes_blueprint.route('/task', methods=['POST'])
def add_task():
    data = request.get_json()
    
    # Ensure user_id is provided
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    # Create a new task with user_id
    new_task = Task(
        title=data.get('title'),
        description=data.get('description'),
        status=data.get('status', 'Pending'),  # Default to 'Pending' if not provided
        due_date=data.get('due_date'),
        user_id=user_id
    )
    
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task added"}), 201


# Get tasks for a specific user
@routes_blueprint.route('/tasks/user/<int:user_id>', methods=['GET'])
def get_user_tasks(user_id):
    tasks = Task.query.filter_by(user_id=user_id).all()  # Fetch tasks for the specific user
    return jsonify([{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'due_date': task.due_date.strftime('%Y-%m-%d'),
        'status': task.status,
        'user_id': task.user_id
    } for task in tasks]), 200

# Get tasks, with optional search query
@routes_blueprint.route('/tasks', methods=['GET'])
def get_tasks():
    search_query = request.args.get('search', '')
    if search_query:
        tasks = Task.query.filter(Task.title.ilike(f'%{search_query}%')).all()
    else:
        tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])

# Update a task by ID
@routes_blueprint.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    data = request.get_json()
    task = Task.query.get(id)

    if task:
        task.title = data.get('title')
        task.description = data.get('description')
        task.status = data.get('status')
        task.due_date = data.get('due_date')
        db.session.commit()
        return jsonify({'message': 'Task updated successfully!'}), 200
    else:
        return jsonify({'error': 'Task not found!'}), 404

# Delete a task by ID
@routes_blueprint.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200

# Get task by ID
@routes_blueprint.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):
    task = Task.query.get(id)
    if task:
        return jsonify(task.to_dict()), 200
    else:
        return jsonify({'error': 'Task not found!'}), 404

# Get task status statistics
@routes_blueprint.route('/status_stats', methods=['GET'])
def status_stats():
    stats = db.session.query(
        Task.status, db.func.count(Task.id)
    ).group_by(Task.status).all()

    result = {status: count for status, count in stats}
    return jsonify(result)
