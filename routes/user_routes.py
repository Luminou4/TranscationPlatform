from flask import Blueprint, request, jsonify
from models import db, User
from utils.auth import generate_token
from werkzeug.security import generate_password_hash, check_password_hash

user_bp = Blueprint('user_bp', __name__)

# 注册接口
@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': '用户名或密码不能为空'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400

    hashed_pwd = generate_password_hash(password)
    user = User(username=username, password=hashed_pwd)
    db.session.add(user)
    db.session.commit()

    return jsonify({'msg': '注册成功'})

# 登录接口
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': '用户名或密码错误'}), 401

    token = generate_token(user.id)
    return jsonify({'msg': '登录成功', 'token': token, 'user_id': user.id})