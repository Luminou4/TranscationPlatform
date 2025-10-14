import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from config import Config
from model.request_response import RequestResponse
from utils.auth import token_required

upload_bp = Blueprint('upload_bp', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload', methods=['POST'])
@token_required
def upload_file(user_id):
    if 'file' not in request.files:
        return jsonify(RequestResponse.error_response(code="999",msg="没有文件上传"))

    file = request.files['file']
    if file.filename == '':
        return jsonify(RequestResponse.error_response(code="999",msg="文件名为空"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(save_path)
        return jsonify(RequestResponse.success_response({ 'url': f'/uploads/{filename}'}))


    else:
        return jsonify(RequestResponse.error_response(code="999",msg="不支持的文件类型"))


