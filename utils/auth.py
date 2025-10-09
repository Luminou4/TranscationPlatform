import jwt
from flask import request, jsonify
from functools import wraps
from config import Config

def generate_token(user_id):
    payload = {'user_id': user_id}
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        except Exception:
            return jsonify({'error': 'Invalid token'}), 401
        return f(data['user_id'], *args, **kwargs)
    return decorated