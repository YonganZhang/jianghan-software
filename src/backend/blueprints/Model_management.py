from flask import Blueprint, request, jsonify, current_app
from exts import db
from models import Lossimagemodel, Trainmodel, ModelConfig, User
from utils_path import resolve_content_path
import jwt
import os
import base64


manage_bp = Blueprint('model_management', __name__)


# 模型管理-分页
@manage_bp.route('/modelmagement_page', methods=['POST'])
def modelmagement():
    # 认证处理
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"code": 401, "message": "未提供认证token"}), 401

    if auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
    else:
        return jsonify({"code": 401, "message": "token格式错误，应使用Bearer格式"}), 401

    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"code": 401, "message": "token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"code": 401, "message": "无效token"}), 401

    # 验证用户存在性
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "message": "用户不存在"}), 404

    # 获取请求数据
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "message": "请求数据不能为空"}), 400

    # 处理分页参数
    try:
        page = int(data.get('pageNum', 1))
        page_size = int(data.get('pageSize', 20))
    except (TypeError, ValueError):
        page = 1
        page_size = 20

    # 确保分页参数有效
    page = max(1, page)
    page_size = max(1, min(page_size, 100))  # 限制每页最大100条

    # 获取用户的模型配置（一对一关系，直接通过user_id查询）
    model_config = ModelConfig.query.filter_by(user_id=user_id).first()

    # 分别查询最终模型和最佳模型数据
    lm_items = Lossimagemodel.query.filter_by(user_id=user_id).all()
    tm_items = Trainmodel.query.filter_by(user_id=user_id).all()

    # 计算总数据量
    total_count = len(lm_items) + len(tm_items)

    # 计算总页数
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

    # 处理页码越界
    if page > total_pages and total_pages > 0:
        page = total_pages

    # 构建合并数据
    merged_data = []

    # 处理最终模型数据
    for item in lm_items:
        if not item.trainepoch_path:
            continue  # 跳过路径为空的无效记录
        # 直接使用当前用户的模型配置
        merged_data.append({
            "id": item.id,
            "model_type": "最终模型",
            "模型名称": model_config.model_name if model_config else "未配置",
            "模型权重名称": item.trainname,
            "训练损失": getattr(item, 'zxl_loss', None),
            "验证损失": getattr(item, 'zyz_loss', None),
            "targetname": model_config.predict_target if model_config else "未配置",
            "model_name": getattr(item, 'modelname', None),
            "user_id": item.user_id  # 使用user_id而不是config_id
        })

    # 处理最佳模型数据
    for item in tm_items:
        if not item.trainepoch_path:
            continue  # 跳过路径为空的无效记录
        merged_data.append({
            "id": item.id,
            "model_type": "最佳模型",
            "模型名称": model_config.model_name if model_config else "未配置",
            "模型权重名称": item.file_name,
            "训练损失": item.avg_train_loss,
            "验证损失": item.avg_val_loss,
            "targetname": model_config.predict_target if model_config else "未配置",
            "model_name": getattr(item, 'modelname', None),
            "user_id": item.user_id  # 使用user_id而不是config_id
        })

    # 应用分页
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    current_page_data = merged_data[start_idx:end_idx]

    # 统一表头
    columns = [
        {"title": "模型类型", "dataIndex": "model_type", "key": "model_type"},
        {"title": "模型名称", "dataIndex": "模型名称", "key": "模型名称"},
        {"title": "模型权重名称", "dataIndex": "模型权重名称", "key": "模型权重名称"},
        {"title": "训练损失", "dataIndex": "训练损失", "key": "训练损失"},
        {"title": "验证损失", "dataIndex": "验证损失", "key": "验证损失"},
        {"title": "目标参数", "dataIndex": "targetname", "key": "targetname"},
        {"title": "模型标识", "dataIndex": "model_name", "key": "model_name"}
    ]

    # 构建响应
    response_data = {
        "pageNum": page,
        "pageSize": page_size,
        "totalPages": total_pages,
        "totalCount": total_count,
        "columns": columns,
        "dataSource": current_page_data
    }

    return jsonify({
        "code": "00000",
        "message": "查询成功",
        "data": response_data
    })


# 模型管理-弹出照片
@manage_bp.route('/modelmagement_pictures', methods=['POST'])
def mp():
    # 认证处理
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"code": 401, "message": "未提供认证token"}), 401

    token = auth_header.split(" ")[1] if auth_header.startswith('Bearer ') else auth_header
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']  # 获取用户ID用于权限验证
    except jwt.ExpiredSignatureError:
        return jsonify({"code": 401, "message": "token已过期"}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({"code": 401, "message": f"无效的token: {str(e)}"}), 401

    # 获取请求数据
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "message": "请求数据不能为空"}), 400

    file_id = data.get('id')
    model_type = data.get('model_type')

    # 验证必要参数
    if not file_id:
        return jsonify({"code": 400, "message": "文件ID不能为空"}), 400

    if not model_type:
        return jsonify({"code": 400, "message": "模型类型不能为空"}), 400

    # 根据模型类型查询图片数据
    try:
        if model_type == "最佳模型":
            # 添加用户ID验证，确保用户只能访问自己的数据
            tm = Trainmodel.query.filter_by(id=file_id, user_id=user_id).first()
            if not tm:
                return jsonify({"code": 404, "message": "未找到对应的最佳模型数据或无权访问"}), 404

            # 检查图片路径是否存在
            picture_path = resolve_content_path(tm.filepicture_path) if tm.filepicture_path else None
            if not picture_path or not os.path.exists(picture_path):
                return jsonify({"code": 404, "message": "图片文件不存在或路径无效"}), 404

            # 读取图片文件并进行Base64编码
            try:
                with open(picture_path, 'rb') as f:
                    picture_data = f.read()
                picture_base64 = base64.b64encode(picture_data).decode('utf-8')

                return jsonify({
                    "code": 200,
                    "message": "返回图片数据成功",
                    "data": {
                        "picture": picture_base64,
                        "format": "base64"
                    }
                })
            except Exception as e:
                current_app.logger.error(f"读取最佳模型图片文件失败: {str(e)}")
                return jsonify({"code": 500, "message": "读取图片文件失败"}), 500

        elif model_type == "最终模型":
            # 添加用户ID验证，确保用户只能访问自己的数据
            lm = Lossimagemodel.query.filter_by(id=file_id, user_id=user_id).first()
            if not lm:
                return jsonify({"code": 404, "message": "未找到对应的最终模型数据或无权访问"}), 404

            # 检查图片路径是否存在
            picture_path = resolve_content_path(lm.file_path) if lm.file_path else None
            if not picture_path or not os.path.exists(picture_path):
                return jsonify({"code": 404, "message": "图片文件不存在或路径无效"}), 404

            # 读取图片文件并进行Base64编码
            try:
                with open(picture_path, 'rb') as f:
                    picture_data = f.read()
                picture_base64 = base64.b64encode(picture_data).decode('utf-8')

                return jsonify({
                    "code": 200,
                    "message": "返回图片数据成功",
                    "data": {
                        "picture": picture_base64,
                        "format": "base64"
                    }
                })
            except Exception as e:
                current_app.logger.error(f"读取最终模型图片文件失败: {str(e)}")
                return jsonify({"code": 500, "message": "读取图片文件失败"}), 500

        else:
            return jsonify({"code": 400, "message": "不支持的模型类型"}), 400

    except Exception as e:
        # 记录错误日志
        current_app.logger.error(f"获取模型图片失败: {str(e)}")
        return jsonify({"code": 500, "message": "服务器内部错误"}), 500


# 参数表
# todo 前端传参和下面删除传参一样的
@manage_bp.route('/modelmagement_visualization', methods=['POST'])
def model_visualization():
    # 认证处理
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"code": 401, "message": "未提供认证token"}), 401

    # 验证token格式
    if not auth_header.startswith('Bearer '):
        return jsonify({"code": 401, "message": "token格式错误，应使用Bearer格式"}), 401

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']  # 获取用户ID用于权限验证
    except jwt.ExpiredSignatureError:
        return jsonify({"code": 401, "message": "token已过期"}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({"code": 401, "message": f"无效的token: {str(e)}"}), 401

    # 获取请求数据
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "message": "请求数据不能为空"}), 400

    # 验证必要参数（仅需一次验证）
    required_fields = ['id', 'model_type']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"code": 400, "message": f"缺少必要参数: {field}"}), 400

    # 验证ID是否为整数（统一变量名，避免冗余转换）
    try:
        model_id = int(data.get('id'))  # 统一用model_id，避免file_id冗余
    except ValueError:
        return jsonify({"code": 400, "message": "id必须为整数"}), 400

    model_type = data.get('model_type')

    try:
        # 根据模型类型查询对应的模型，通过一对一关系获取训练参数
        if model_type == "最佳模型":
            train_model = Trainmodel.query.filter_by(id=model_id, user_id=user_id).first()
            if not train_model:
                return jsonify({"code": 404, "message": "未找到该最佳模型或无权限访问"}), 404
            params = train_model.training_params

        elif model_type == "最终模型":
            loss_model = Lossimagemodel.query.filter_by(id=model_id, user_id=user_id).first()
            if not loss_model:
                return jsonify({"code": 404, "message": "未找到该最终模型或无权限访问"}), 404
            params = loss_model.training_params

        else:
            return jsonify({"code": 400, "message": f"不支持的模型类型: {model_type}"}), 400

        # 验证参数是否存在
        if not params:
            return jsonify({"code": 404, "message": "未找到对应的训练参数"}), 404

        # 构造响应数据
        param_data = {
            "model_name": params.model_name,
            "hidden_size": params.hidden_size,
            "num_layers": params.num_layers,
            "dropout": params.dropout,
            "grid_size": params.grid_size,
            "num_channels": params.num_channels,
            "kernel_size": params.kernel_size,
            "num_heads": params.num_heads,
            "hidden_space": params.hidden_space,
            "e_layers": params.e_layers,
            "d_ff": params.d_ff,
            "moving_avg": params.moving_avg,
            "factor": params.factor,
            "activation": params.activation,
            "use_layer_norm": params.use_layer_norm,
            "num_epochs": params.num_epochs,
            "learning_rate": params.learning_rate,
            "loss": params.loss
        }

        return jsonify({
            "code": 200,
            "message": "训练参数获取成功",
            "data": param_data
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取模型训练参数失败: {str(e)}")
        return jsonify({"code": 500, "message": "服务器内部错误，获取参数失败"}), 500


# 修改接口-修改用户选择修改的内容
@manage_bp.route('/modelmagement_modify', methods=['POST'])  # 建议修改操作用POST方法
def modify():  # 修正函数名拼写错误
    # 认证处理
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"code": 401, "message": "未提供认证token"}), 401

    # 提取token并验证格式
    if not auth_header.startswith('Bearer '):
        return jsonify({"code": 401, "message": "token格式错误，应使用Bearer格式"}), 401

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']  # 获取用户ID用于权限验证
    except jwt.ExpiredSignatureError:
        return jsonify({"code": 401, "message": "token已过期"}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({"code": 401, "message": f"无效的token: {str(e)}"}), 401

    # 获取请求数据
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "message": "请求数据不能为空"}), 400

    # 验证必要参数
    required_fields = ['id', 'model_type', 'modelname']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"code": 400, "message": f"缺少必要参数: {field}"}), 400

    # 提取参数
    file_id = data.get('id')
    model_type = data.get('model_type')
    modify_name = data.get('modelname')

    try:
        # 根据模型类型处理修改
        if model_type == "最佳模型":
            tm = Trainmodel.query.filter_by(user_id=user_id, id=file_id).first()
            if not tm:
                return jsonify({"code": 404, "message": "未找到指定的最佳模型"}), 404

            tm.modelname = modify_name
            db.session.commit()
            return jsonify({"code": 200, "message": "最佳模型名称修改成功", "data": {"new_name": modify_name}}), 200

        elif model_type == "最终模型":
            lm = Lossimagemodel.query.filter_by(user_id=user_id, id=file_id).first()
            if not lm:
                return jsonify({"code": 404, "message": "未找到指定的最终模型"}), 404

            lm.modelname = modify_name
            db.session.commit()
            return jsonify({"code": 200, "message": "最终模型名称修改成功", "data": {"new_name": modify_name}}), 200

        else:
            return jsonify({"code": 400, "message": f"不支持的模型类型: {model_type}"}), 400

    except Exception as e:
        # 发生异常时回滚事务
        db.session.rollback()
        # 记录错误日志（实际应用中建议使用logger）
        print(f"修改模型名称时发生错误: {str(e)}")
        return jsonify({"code": 500, "message": "服务器内部错误，修改失败"}), 500


# 删除接口-删除对应的类型的记录
@manage_bp.route('/modelmagement_delete', methods=['POST'])
def delete():
    # 认证处理
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"code": 401, "message": "未提供认证token"}), 401

    # 提取token并验证格式
    if not auth_header.startswith('Bearer '):
        return jsonify({"code": 401, "message": "token格式错误，应使用Bearer格式"}), 401

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']  # 获取用户ID用于权限验证
    except jwt.ExpiredSignatureError:
        return jsonify({"code": 401, "message": "token已过期"}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({"code": 401, "message": f"无效的token: {str(e)}"}), 401

    # 获取请求数据
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "message": "请求数据不能为空"}), 400

    # 验证必要参数
    required_fields = ['id', 'model_type']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"code": 400, "message": f"缺少必要参数: {field}"}), 400

    # 验证ID是否为整数
    try:
        file_id = int(data.get('id'))
    except ValueError:
        return jsonify({"code": 400, "message": "id必须为整数"}), 400

    model_type = data.get('model_type')

    try:
        # 根据模型类型处理删除（包含文件清理）
        if model_type == "最佳模型":
            model = Trainmodel.query.filter_by(id=file_id, user_id=user_id).first()
            if not model:
                return jsonify({"code": 404, "message": "未找到该最佳模型或无权限删除"}), 404

            # 先删除关联文件，再删除数据库记录
            model.delete_files()  # 调用模型的文件清理方法
            db.session.delete(model)
            db.session.commit()
            return jsonify({"code": 200, "message": "最佳模型及关联文件删除成功", "data": {"id": file_id}}), 200

        elif model_type == "最终模型":
            loss_model = Lossimagemodel.query.filter_by(id=file_id, user_id=user_id).first()
            if not loss_model:
                return jsonify({"code": 404, "message": "未找到该最终模型或无权限删除"}), 404

            # 先删除关联文件，再删除数据库记录
            loss_model.delete_files()  # 调用模型的文件清理方法
            db.session.delete(loss_model)
            db.session.commit()
            return jsonify({"code": 200, "message": "最终模型及关联文件删除成功", "data": {"id": file_id}}), 200

        else:
            return jsonify({"code": 400, "message": f"不支持的模型类型: {model_type}"}), 400

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除模型时发生错误: {str(e)}")  # 改用日志记录错误（推荐）
        return jsonify({"code": 500, "message": "服务器内部错误，删除失败"}), 500