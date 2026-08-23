from flask import Blueprint, request, jsonify, session
from app.models import User, TopicProgress, ExerciseStats
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    session['user_id'] = user.id
    return jsonify({'status': 'ok', 'user': {'id': user.id, 'username': user.username}})


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401

    session['user_id'] = user.id
    return jsonify({'status': 'ok', 'user': {'id': user.id, 'username': user.username}})


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'status': 'ok'})


@auth_bp.route('/me', methods=['GET'])
def get_me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    user = db.session.get(User, user_id)
    if not user:
        session.pop('user_id', None)
        return jsonify({'error': 'User not found'}), 401
        
    return jsonify({'user': {'id': user.id, 'username': user.username}})


@auth_bp.route('/reset_all_progress', methods=['POST'])
def reset_all_progress():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    # Delete all progress and stats for this user
    TopicProgress.query.filter_by(user_id=user_id).delete()
    ExerciseStats.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    return jsonify({'status': 'ok'})
