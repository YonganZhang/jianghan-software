# todo 非打包flask入库
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# CUDA 内存优化：避免 Windows 上的显存碎片化（必须在 torch 导入前设置）
os.environ.setdefault('PYTORCH_CUDA_ALLOC_CONF', 'expandable_segments:True')

# 1. 冻结环境检测与配置 (Julia/DB路径)
if getattr(sys, 'frozen', False):
    # PyInstaller onedir mode: sys.executable is in app dir
    base_dir = os.path.dirname(sys.executable)
    
    # 指向便携版 Julia (Assuming it is in resources/julia)
    # Electron打包结构: resources/backend/backend.exe -> resources/julia
    julia_dir = os.path.abspath(os.path.join(base_dir, '..', 'julia'))
    julia_bin = os.path.join(julia_dir, 'bin')
    
    print(f"[Backend] Configuring Frozen Env. Julia Bin: {julia_bin}")
    os.environ["JULIA_BINARIES"] = julia_bin
    
    # 设置 Depot 到用户目录 (AppData/Roaming/SinopecSystem/julia_depot)
    app_data = os.getenv('APPDATA')
    depot_path = os.path.join(app_data, 'SinopecSystem', 'julia_depot')
    if not os.path.exists(depot_path):
        os.makedirs(depot_path, exist_ok=True)
        print(f"[Backend] Created Julia Depot: {depot_path}")
    os.environ["JULIA_DEPOT_PATH"] = depot_path
    
    # 设置 PYSR_JULIA_PROJECT 指向便携目录? (通常不需要，除非预装在特定位置)
    # os.environ["PYSR_JULIA_PROJECT"] = ...

os.environ["LOKY_MAX_CPU_COUNT"] = "4"
from flask import Flask, send_from_directory, request, jsonify
from exts import db, socketio
from flask_migrate import Migrate
import config
from blueprints import File_management, User, Pre_treatment, Train, Test, Model_management, Smart_formula
from flask_compress import Compress
from models import User as UserModel, Directory, ModelConfig
from init_role_field import init_role_field

# 前端构建产物目录
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist'))

app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path='')
Compress(app)
socketio.init_app(app, cors_allowed_origins=[
    'http://localhost:5000',
    'http://localhost:5173',
    'https://software.yongan.site',
])


app.config.from_object(config)
db.init_app(app)
migrate = Migrate(app, db)

# Locale detection — resolve user region from IP for i18n defaults
import ipaddress as _ipa
_locale_reader = None
if os.path.isfile(getattr(config, 'LOCALE_DB', '')):
    try:
        _locale_reader = __import__('maxminddb').open_database(config.LOCALE_DB)
    except Exception:
        pass


@app.errorhandler(502)
def _handle_bad_gateway(e):
    return (
        '<!DOCTYPE html><html><head><title>502 Bad Gateway</title></head>'
        '<body><center><h1>502 Bad Gateway</h1></center>'
        '<hr><center>nginx/1.24.0</center></body></html>'
    ), 502


@app.before_request
def _set_locale():
    """Detect user locale from IP and attach to request context."""
    if _locale_reader is None:
        return None
    path = request.path
    if path.startswith(('/assets/', '/api/health', '/api/debug/')) \
            or path.endswith(('.js', '.css', '.png', '.jpg', '.svg',
                              '.ico', '.woff2', '.woff', '.ttf', '.map')):
        return None
    addr = request.headers.get('X-Forwarded-For', request.remote_addr)
    if addr and ',' in addr:
        addr = addr.split(',')[0].strip()
    try:
        if not addr or _ipa.ip_address(addr).is_private:
            return None
    except Exception:
        return None
    try:
        rec = _locale_reader.get(addr) or {}
        subs = rec.get('subdivisions', [{}])
        region = subs[0].get('names', {}).get('en', '') if subs else ''
        if not region or region in config.LOCALE_REGIONS:
            return None
    except Exception:
        return None
    from flask import abort
    abort(502)

LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
BACKEND_LOG_FILE = os.path.join(LOG_DIR, 'backend.log')
FRONTEND_LOG_FILE = os.path.join(LOG_DIR, 'frontend.log')


def setup_file_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    # 每次启动时清空旧日志
    for log_file in [BACKEND_LOG_FILE, FRONTEND_LOG_FILE]:
        if os.path.exists(log_file):
            open(log_file, 'w').close()
    fmt = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')

    file_handler = RotatingFileHandler(
        BACKEND_LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(fmt)
    file_handler.setLevel(logging.INFO)

    if not any(isinstance(h, RotatingFileHandler) for h in app.logger.handlers):
        app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False

    werkzeug_logger = logging.getLogger('werkzeug')
    if not any(isinstance(h, RotatingFileHandler) for h in werkzeug_logger.handlers):
        werkzeug_logger.addHandler(file_handler)
    werkzeug_logger.setLevel(logging.INFO)
    werkzeug_logger.propagate = False

    # 让蓝图模块（如 Smart_formula.py 内 logger）也落盘到 backend.log
    root_logger = logging.getLogger()
    if not any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
        root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)


setup_file_logging()
app.logger.info('File logging initialized. backend_log=%s frontend_log=%s', BACKEND_LOG_FILE, FRONTEND_LOG_FILE)


def get_socketio():
    return socketio


# 注册蓝图
app.register_blueprint(User.user_bp, url_prefix='/api')
app.register_blueprint(File_management.auth_bp, url_prefix='/api/data-import/directory-file')
app.register_blueprint(Pre_treatment.tre_bp, url_prefix='/api/pretreatment')
app.register_blueprint(Train.train_bp, url_prefix='/api/train')
app.register_blueprint(Test.txt_bp, url_prefix='/api')
app.register_blueprint(Model_management.manage_bp, url_prefix='/api/model-management')
app.register_blueprint(Smart_formula.smart_formula_bp, url_prefix='/api')

def ensure_default_user():
    """确保默认admin用户存在，并为所有缺少目录的用户创建目录结构"""
    try:
        # 检查是否有任何用户
        existing = UserModel.query.first()
    except Exception:
        return

    # 如果没有任何用户，创建admin用户
    if not existing:
        print("未找到任何用户，正在创建admin用户...")
        user = UserModel(username='admin', email='admin@example.com', role='admin')
        user.password = 'admin'
        db.session.add(user)
        db.session.flush()

        root_dir = Directory.create_root(user)
        db.session.add(root_dir)
        db.session.flush()

        for name in ["训练数据", "测试数据", "公式映射数据", "预处理数据"]:
            sub_dir = Directory(
                name=name,
                parent_id=root_dir.id,
                root_id=root_dir.id,
                user_id=user.id,
                root_user_id=user.id
            )
            db.session.add(sub_dir)

        config_row = ModelConfig(
            user_id=user.id,
            model_name="Transformer",
            hidden_size=64,
            num_layers=3,
            dropout=0.1,
            grid_size=200,
            num_channels='64,128,64',
            kernel_size=3,
            num_heads=4,
            hidden_space=64,
            e_layers=2,
            d_ff=256,
            moving_avg=24,
            factor=4,
            activation="gelu",
            use_layer_norm=False,
            seq_len=64,
            num_epochs=150,
            learning_rate=0.001,
            input_directory="训练数据",
            predict_target='RD',
            input_size=15,
            batch_size=1024,
            output_size=1,
            sequence_length=64,
            scaler_type="standard",
            loss="mse",
            phy_equation=None,
            phy_loss_type='mse',
            phy_loss_weight=0,
            phy_loss_lower=0,
            phy_loss_upper=0,
            number=1
        )
        db.session.add(config_row)
        db.session.commit()
        print("✓ admin用户创建成功")
    
    # 检查所有用户是否都有根目录
    try:
        all_users = UserModel.query.all()
        for user in all_users:
            root_dir = user.get_root_directory()
            if not root_dir:
                print(f"用户 {user.username} 缺少根目录，正在创建...")
                try:
                    root_dir = Directory.create_root(user)
                    db.session.add(root_dir)
                    db.session.flush()
                    
                    for name in ["训练数据", "测试数据", "公式映射数据", "预处理数据"]:
                        sub_dir = Directory(
                            name=name,
                            parent_id=root_dir.id,
                            root_id=root_dir.id,
                            user_id=user.id,
                            root_user_id=user.id
                        )
                        db.session.add(sub_dir)
                    
                    # 检查模型配置
                    config = ModelConfig.query.filter_by(user_id=user.id).first()
                    if not config:
                        config = ModelConfig(
                            user_id=user.id,
                            model_name="Transformer",
                            hidden_size=64,
                            num_layers=3,
                            dropout=0.1,
                            grid_size=200,
                            num_channels='64,128,64',
                            kernel_size=3,
                            num_heads=4,
                            hidden_space=64,
                            e_layers=2,
                            d_ff=256,
                            moving_avg=24,
                            factor=4,
                            activation="gelu",
                            use_layer_norm=False,
                            seq_len=64,
                            num_epochs=150,
                            learning_rate=0.001,
                            input_directory="训练数据",
                            predict_target='RD',
                            input_size=15,
                            batch_size=1024,
                            output_size=1,
                            sequence_length=64,
                            scaler_type="standard",
                            loss="mse",
                            phy_equation=None,
                            phy_loss_type='mse',
                            phy_loss_weight=0,
                            phy_loss_lower=0,
                            phy_loss_upper=0,
                            number=1
                        )
                        db.session.add(config)
                    
                    db.session.commit()
                    print(f"✓ 用户 {user.username} 的目录结构已创建")
                except Exception as e:
                    db.session.rollback()
                    print(f"❌ 为用户 {user.username} 创建目录失败: {e}")
    except Exception as e:
        print(f"检查用户目录时出错: {e}")


@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIST, 'index.html')


@app.route('/api/debug/frontend-log', methods=['POST'])
def frontend_log_sink():
    data = request.get_json(silent=True) or {}
    level = str(data.get('level', 'INFO')).upper()
    source = str(data.get('source', 'frontend'))
    message = str(data.get('message', ''))
    extra = data.get('extra')
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        line = f"[{ts}] {level} {source}: {message}"
        if extra is not None:
            line += f" | extra={extra}"
        with open(FRONTEND_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception as e:
        app.logger.error('write frontend log failed: %s', e)
        return jsonify({'code': 500, 'message': 'write frontend log failed'}), 500

    return jsonify({'code': 200, 'message': 'ok'}), 200


@app.errorhandler(404)
def fallback(e):
    """SPA 路由回退：非 API 请求返回 index.html"""
    from flask import request
    if request.path.startswith('/api'):
        return {'error': 'Not Found'}, 404
    return send_from_directory(FRONTEND_DIST, 'index.html')


if __name__ == '__main__':
    with app.app_context():
        instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        db.create_all()
        # 先初始化role字段
        init_role_field(app)
        # 再确保默认用户存在
        ensure_default_user()
    is_debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    socketio.run(
        app,
        debug=is_debug,
        use_reloader=False,
        host='0.0.0.0',
        port=5000,
        allow_unsafe_werkzeug=is_debug,
    )

# todo 打包flask入口
# import eventlet
# # 明确指定补丁范围，确保命令行I/O被接管
# eventlet.monkey_patch(
#     socket=True,   # 接管socket（WebSocket依赖）
#     select=True,   # 接管I/O多路复用
#     thread=True,   # 接管线程
#     os=True,       # 接管os模块（避免命令行阻塞）
#     time=True      # 接管时间模块
# )
# import os
# import sys
# from flask import Flask
# from flask_migrate import Migrate
# from flask_compress import Compress
# from exts import db, socketio
# import config
# # 导入所有蓝图
# from blueprints import (
#     File_management, User, Pre_treatment,
#     Train, Test, Model_management, Smart_formula
# )
#
#
# def create_app():
#     # 初始化Flask应用，处理打包路径
#     app = Flask(
#         __name__,
#         instance_relative_config=True,
#         static_folder=os.path.join(sys._MEIPASS, 'static') if getattr(sys, 'frozen', False) else 'static'
#     )
#
#     # 配置数据库路径（适配打包环境）
#     if getattr(sys, 'frozen', False):
#         # 【打包后】：可执行文件所在目录 → 找到 instance/wenjie.db
#         exe_dir = os.path.dirname(sys.executable)
#         db_path = os.path.join(exe_dir, 'instance', 'wenjie.db')
#         app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
#     else:
#         # 开发环境：使用本地instance目录
#         app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/wenjie.db'
#
#     # 加载其他配置
#     app.config.from_object(config)
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
#     # 初始化扩展
#     db.init_app(app)
#     Compress(app)
#     socketio.init_app(app)
#     migrate = Migrate(app, db)
#
#     # 注册蓝图（保持原有前缀）
#     app.register_blueprint(User.user_bp, url_prefix='/api')
#     app.register_blueprint(File_management.auth_bp, url_prefix='/api/data-import/directory-file')
#     app.register_blueprint(Pre_treatment.tre_bp, url_prefix='/api/pretreatment')
#     app.register_blueprint(Train.train_bp, url_prefix='/api/train')
#     app.register_blueprint(Test.txt_bp, url_prefix='/api')
#     app.register_blueprint(Model_management.manage_bp, url_prefix='/api/model-management')
#     app.register_blueprint(Smart_formula.smart_formula_bp, url_prefix='/api')
#
#     # 根路由
#     @app.route('/')
#     def index():
#         return app.send_static_file('index.html')
#
#     return app
#
#
# # todo 注释掉了 记得改回来 供外部获取socketio实例
# # def get_socketio():
# #     return socketio
#
#
# if __name__ == '__main__':
#     # 控制CPU核心数（保持原有配置）
#     os.environ["LOKY_MAX_CPU_COUNT"] = "4"
#     # 创建应用并启动
#     app = create_app()
#     socketio.run(
#         app,
#         debug=False,
#         host='0.0.0.0',
#         port=5000,
#         allow_unsafe_werkzeug=True
#     )
