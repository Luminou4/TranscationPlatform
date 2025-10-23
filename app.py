from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from routes.item_routes import item_bp
from routes.user_routes import user_bp
from routes.upload_routes import upload_bp
from routes.order_routes import order_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

# 注册蓝图
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(upload_bp, url_prefix='/api')
app.register_blueprint(item_bp, url_prefix='/api')
app.register_blueprint(order_bp, url_prefix='/api')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    from flask import send_from_directory
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

# 初始化数据库
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8800)