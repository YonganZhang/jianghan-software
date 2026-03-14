from flask import Blueprint, request, jsonify, current_app
import datetime
from models import User, Directory, File, ModelConfig
from exts import db
import jwt
from werkzeug.exceptions import Unauthorized
import hashlib

user_bp = Blueprint('user', __name__)


# 健康检查端点 - 用于前端确认后端服务已就绪
@user_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': '服务已就绪'}), 200


def serialize_directory(directory):
    return {
        'id': directory.id,
        'name': directory.name,
        'parent_id': directory.parent_id,
        'root_id': directory.root_id,
        'user_id': directory.user_id,
        'root_user_id': directory.root_user_id,
        'created_at': directory.created_at.isoformat(),
        'updated_at': directory.updated_at.isoformat(),
        'deleted_at': directory.deleted_at.isoformat() if directory.deleted_at else None,
        'is_root': directory.is_root,
        'path': directory.get_path()
    }

def serialize_file(file):
    return {
        'id': file.id,
        'name': file.name,
        'type': file.type,
        'size': file.size,
        'directory_id': file.directory_id,
        'root_id': file.root_id,
        'user_id': file.user_id,
        'created_at': file.created_at.isoformat(),
        'updated_at': file.updated_at.isoformat(),
        'deleted_at': file.deleted_at.isoformat() if file.deleted_at else None,
        'file_hash': file.file_hash,
        'is_root_level': file.is_root_level,
        'full_path': file.full_path
    }

def get_user_id_from_token():
    # 从请求头中获取 JWT 令牌
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise Unauthorized('Missing or invalid Authorization header')
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )

        # 使用 datetime.datetime.utcfromtimestamp()
        if 'exp' in payload and datetime.datetime.utcfromtimestamp(payload['exp']) < datetime.datetime.utcnow():
            raise Unauthorized('Token has expired')
        user_id = payload.get('user_id')
        if not user_id:
            raise Unauthorized('Invalid token payload')
        return user_id
    except jwt.InvalidTokenError:
        raise Unauthorized('Invalid token')

def calculate_sha256(data):
    return hashlib.sha256(data).hexdigest()



# 数据导入-注册
@user_bp.route('/sign', methods=['POST'])
def sign():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data or 'email' not in data:
        return jsonify({'error': '必须提供用户名、密码和邮箱'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 409

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已被注册'}), 409

    new_user = User(
        username=data['username'],
        email=data['email'],
        role='user'  # 新注册用户默认为普通用户
    )
    new_user.password = data['password']  # 触发密码哈希
    db.session.add(new_user)
    try:
        # 第一次flush生成用户ID
        db.session.flush()

        # 创建用户的根目录
        root_dir = Directory.create_root(new_user)
        db.session.add(root_dir)

        # 第二次flush生成根目录ID
        db.session.flush()

        # 创建四个默认子目录
        subdir_names = ["训练数据", "测试数据", "公式映射数据", "预处理数据"]
        for name in subdir_names:
            sub_dir = Directory(
                name=name,
                parent_id=root_dir.id,
                root_id=root_dir.id,
                user_id=new_user.id,
                root_user_id=new_user.id
            )
            db.session.add(sub_dir)

        # ===== 修正从这里开始 =====
        # 创建预设模型配置（使用正确的用户ID）
        config = ModelConfig(
            user_id=new_user.id,  # 直接使用用户对象ID
            model_name="Transformer",
            hidden_size=8,
            num_layers=5,
            dropout=0.1,
            grid_size=200,
            num_channels='25,50,25',
            kernel_size=3,
            num_heads=4,
            hidden_space=8,
            e_layers=2,
            d_ff=64,
            moving_avg=24,
            factor=4,
            activation="tanh",
            use_layer_norm=False,
            seq_len=64,
            num_epochs=150,
            learning_rate=0.0005,
            # 使用相对路径或根据实际结构调整
            input_directory="训练数据",
            predict_target='RD',
            input_size=15,
            batch_size=1024,
            output_size=1,
            sequence_length=64,
            scaler_type="standard",
            loss="mae",
            phy_equation=None,
            phy_loss_type='mse',
            phy_loss_weight=0,
            phy_loss_lower=0,
            phy_loss_upper=0,
            number = 1
        )
        db.session.add(config)
        db.session.commit()

        return jsonify({
            'code': "00000",
            'message': '用户注册成功，已创建根目录和默认子目录',
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'注册失败: {str(e)}'}), 500


# 数据导入-登录
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': '用户名或密码为空'}), 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.verify_password(data['password']):
        return jsonify({'error': '无效的用户名或密码'}), 401

    user.last_login = datetime.datetime.utcnow()
    db.session.commit()

    token_payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }

    token = jwt.encode(
        token_payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

    # 构建符合要求的返回结构
    response_data = {
        "code": "00000",
        "message": "登录成功",
        "data": {
            "token": token,
            "userInfo": {
                "id": user.id,
                "username": user.username,
                "role": getattr(user, 'role', 'user'),  # 如果role字段不存在，默认为'user'
            }
        }
    }

    return jsonify(response_data), 200


# 获取用户列表（仅管理员可访问）
@user_bp.route('/users', methods=['GET'])
def get_users():
    try:
        user_id = get_user_id_from_token()
        current_user = User.query.get(user_id)
        
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': '权限不足，仅管理员可访问'}), 403
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 10, type=int)
        
        # 查询用户列表
        pagination = User.query.paginate(page=page, per_page=page_size, error_out=False)
        
        users_list = []
        for user in pagination.items:
            users_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            })
        
        return jsonify({
            'code': '00000',
            'message': '获取用户列表成功',
            'data': {
                'users': users_list,
                'total': pagination.total,
                'page': page,
                'pageSize': page_size
            }
        }), 200
    except Exception as e:
        return jsonify({'error': f'获取用户列表失败: {str(e)}'}), 500


# 删除用户（仅管理员可访问）
@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        current_user_id = get_user_id_from_token()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': '权限不足，仅管理员可访问'}), 403
        
        # 不能删除自己
        if current_user_id == user_id:
            return jsonify({'error': '不能删除当前登录的管理员账号'}), 400
        
        # 查找要删除的用户
        user_to_delete = User.query.get(user_id)
        if not user_to_delete:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查是否是管理员
        if user_to_delete.role == 'admin':
            return jsonify({'error': '不能删除管理员账号'}), 400
        
        # 手动删除相关数据（确保完全清理）
        try:
            print(f"\n开始删除用户 {user_to_delete.username} (ID: {user_id})")
            
            # 1. 删除用户的所有文件（先删除文件，避免外键约束）
            from models import Directory, File
            print("  步骤1: 删除文件...")
            all_files = File.query.filter_by(user_id=user_id).all()
            print(f"    找到 {len(all_files)} 个文件")
            for file in all_files:
                db.session.delete(file)
            
            # 2. 删除用户的所有目录（包括root_user_id和user_id）
            print("  步骤2: 删除目录...")
            directories = Directory.query.filter(
                (Directory.user_id == user_id) | (Directory.root_user_id == user_id)
            ).all()
            print(f"    找到 {len(directories)} 个目录（含用户目录与根目录）")

            dir_by_id = {d.id: d for d in directories}
            remaining_ids = set(dir_by_id.keys())
            children_by_parent_id = {}
            for d in directories:
                if d.parent_id is not None and d.parent_id in remaining_ids:
                    children_by_parent_id.setdefault(d.parent_id, set()).add(d.id)

            deleted_directory_count = 0
            while remaining_ids:
                leaf_ids = [
                    dir_id
                    for dir_id in remaining_ids
                    if not children_by_parent_id.get(dir_id)
                ]
                if not leaf_ids:
                    leaf_ids = list(remaining_ids)

                for dir_id in leaf_ids:
                    dir_obj = dir_by_id[dir_id]

                    leftover_files = File.query.filter_by(directory_id=dir_id).all()
                    for f in leftover_files:
                        if f not in all_files:
                            db.session.delete(f)

                    db.session.delete(dir_obj)
                    deleted_directory_count += 1
                    remaining_ids.discard(dir_id)

                    parent_id = dir_obj.parent_id
                    if parent_id is not None and parent_id in children_by_parent_id:
                        children_by_parent_id[parent_id].discard(dir_id)
                        if not children_by_parent_id[parent_id]:
                            children_by_parent_id.pop(parent_id, None)

                if deleted_directory_count > len(dir_by_id) * 2:
                    break

            print(f"    删除了 {deleted_directory_count} 个目录")
            
            # 3. 删除用户的模型配置
            print("  步骤3: 删除模型配置...")
            from models import ModelConfig
            config = ModelConfig.query.filter_by(user_id=user_id).first()
            if config:
                db.session.delete(config)
                print("    删除了模型配置")
            
            # 4. 删除用户的训练模型
            print("  步骤4: 删除训练模型...")
            from models import Trainmodel
            train_models = Trainmodel.query.filter_by(user_id=user_id).all()
            print(f"    找到 {len(train_models)} 个训练模型")
            for model in train_models:
                db.session.delete(model)
            
            # 5. 删除用户的智能公式
            print("  步骤5: 删除智能公式...")
            from models import Smartformula
            formulas = Smartformula.query.filter_by(user_id=user_id).all()
            print(f"    找到 {len(formulas)} 个智能公式")
            for formula in formulas:
                db.session.delete(formula)
            
            # 6. 删除用户的损失图片模型
            print("  步骤6: 删除损失图片...")
            from models import Lossimagemodel
            loss_images = Lossimagemodel.query.filter_by(user_id=user_id).all()
            print(f"    找到 {len(loss_images)} 个损失图片")
            for loss_image in loss_images:
                db.session.delete(loss_image)
            
            # 7. 最后删除用户
            print("  步骤7: 删除用户...")
            db.session.delete(user_to_delete)
            
            # 提交所有更改
            print("  提交数据库更改...")
            db.session.commit()
            print(f"✓ 成功删除用户 {user_to_delete.username}\n")
            
            return jsonify({
                'code': '00000',
                'message': '删除用户成功'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            import traceback
            error_detail = traceback.format_exc()
            print(f"❌ 删除用户时出错:\n{error_detail}")
            return jsonify({'error': f'删除用户失败: {str(e)}'}), 500
            
    except Exception as e:
        db.session.rollback()
        import traceback
        error_detail = traceback.format_exc()
        print(f"删除用户验证时出错: {error_detail}")
        return jsonify({'error': f'删除用户失败: {str(e)}'}), 500


# 修改用户信息（仅管理员可访问）
@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        current_user_id = get_user_id_from_token()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': '权限不足，仅管理员可访问'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供要修改的数据'}), 400
        
        # 查找要修改的用户
        user_to_update = User.query.get(user_id)
        if not user_to_update:
            return jsonify({'error': '用户不存在'}), 404
        
        # 更新用户名
        if 'username' in data and data['username']:
            # 检查用户名是否已存在
            existing = User.query.filter(User.username == data['username'], User.id != user_id).first()
            if existing:
                return jsonify({'error': '用户名已存在'}), 409
            user_to_update.username = data['username']
        
        # 更新邮箱
        if 'email' in data and data['email']:
            # 检查邮箱是否已存在
            existing = User.query.filter(User.email == data['email'], User.id != user_id).first()
            if existing:
                return jsonify({'error': '邮箱已被使用'}), 409
            user_to_update.email = data['email']
        
        # 更新密码
        if 'password' in data and data['password']:
            user_to_update.password = data['password']
        
        # 更新角色（不能修改自己的角色）
        if 'role' in data and data['role']:
            if current_user_id == user_id:
                return jsonify({'error': '不能修改自己的角色'}), 400
            if data['role'] in ['admin', 'user']:
                user_to_update.role = data['role']
        
        db.session.commit()
        
        return jsonify({
            'code': '00000',
            'message': '修改用户信息成功'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'修改用户信息失败: {str(e)}'}), 500


# 重置用户密码（仅管理员可访问）
@user_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
def reset_password(user_id):
    try:
        current_user_id = get_user_id_from_token()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': '权限不足，仅管理员可访问'}), 403
        
        data = request.get_json()
        new_password = data.get('password')
        
        if not new_password:
            return jsonify({'error': '请提供新密码'}), 400
        
        # 查找要重置密码的用户
        user_to_reset = User.query.get(user_id)
        if not user_to_reset:
            return jsonify({'error': '用户不存在'}), 404
        
        user_to_reset.password = new_password
        db.session.commit()
        
        return jsonify({
            'code': '00000',
            'message': '重置密码成功'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'重置密码失败: {str(e)}'}), 500
