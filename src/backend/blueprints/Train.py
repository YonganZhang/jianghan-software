from models import ModelConfig
from exts import db, socketio
from flask import Blueprint, request, jsonify, current_app
import jwt
import torch
import torch.nn as nn
import torch.optim as optim
from tools.data_pre import get_model
from tools.tool_for_pre import get_parameters, load_data_loaders, build_and_save_data_loaders_from_file_ids
from tools.tool_for_train import (
    train_model as external_train_model,
    set_abort_flag,
    clear_abort_flag,
    TrainingAborted,
)
from tools.tools_for_konwledge import build_physical_loss_from_equation

from contextlib import contextmanager
import sys
import re
import ast
import platform


train_bp = Blueprint('train_bp', __name__)


@contextmanager
def redirect_print():
    original_stdout = sys.stdout

    # 主类型正则（匹配前缀）
    MAIN_TYPE_PATTERN = re.compile(r'^\[(log|tuyilan|tuyihong|tuerlan|tuerhong|trainloss|trainloss1|trainloss2|trainloss3|trainloss4|trainloss5|trainloss6)\]\s*(.*)$')
    # 新增：匹配外层大括号包裹的内容（如{[1, 2, 3]}）
    BRACES_PATTERN = re.compile(r'^\{(.*)\}$')

    # 类型处理函数
    def handle_log(content):
        return {'event': 'log', 'data': {'type': 'log', 'content': content}}

    def train(content):
        return {'event': 'tuyilan', 'data': {'type': 'tuyilan', 'content': content}}

    def verfy(content):
        return {'event': 'tuyihong', 'data': {'type': 'tuyihong', 'content': content}}

    def train1(content):
        return {'event': 'tuerlan', 'data': {'type': 'tuerlan', 'content': content}}

    def verfy1(content):
        return {'event': 'tuerhong', 'data': {'type': 'tuerhong', 'content': content}}


    def trainloss(content):
        return {'event': 'trainloss', 'data': {'type': 'trainloss', 'content': content}}


    def trainloss1(content):
        return {'event': 'trainloss1', 'data': {'type': 'trainloss1', 'content': content}}

    def trainloss2(content):
        return {'event': 'trainloss2', 'data': {'type': 'trainloss2', 'content': content}}

    def trainloss3(content):
        return {'event': 'trainloss3', 'data': {'type': 'trainloss3', 'content': content}}

    def trainloss4(content):
        return {'event': 'trainloss4', 'data': {'type': 'trainloss4', 'content': content}}

    def trainloss5(content):
        return {'event': 'trainloss5', 'data': {'type': 'trainloss5', 'content': content}}

    def trainloss6(content):
        return {'event': 'trainloss6', 'data': {'type': 'trainloss6', 'content': content}}


    TYPE_HANDLERS = {
        "log": handle_log,

        "tuyilan": train,
        "tuyihong": verfy,
        "tuerlan": train1,
        "tuerhong": verfy1,

        "trainloss": trainloss,
        "trainloss1": trainloss1,
        "trainloss2": trainloss2,
        "trainloss3": trainloss3,
        "trainloss4": trainloss4,
        "trainloss5": trainloss5,
        "trainloss6": trainloss6
    }

    class TypedSocketIOStream:
        def __init__(self):
            self._buffer = ""

        @staticmethod
        def _extract_trainloss_pair(raw: str):
            """从异常字符串中兜底提取 [epoch, loss] 数值对。"""
            if not isinstance(raw, str):
                return None
            # 支持整数/小数/科学计数法
            nums = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', raw)
            if len(nums) < 2:
                return None
            try:
                x = float(nums[0])
                y = float(nums[1])
                return [x, y]
            except Exception:
                return None

        def _emit_line(self, line: str):
            cleaned_data = (line or "").strip()
            if not cleaned_data:
                return

            # 提取类型和内容字符串
            main_match = MAIN_TYPE_PATTERN.match(cleaned_data)
            if not main_match:
                data_type = "log"
                content_str = cleaned_data
            else:
                data_type, content_str = main_match.groups()

            # 关键修改：移除外层大括号（处理{[...]}格式）
            braces_match = BRACES_PATTERN.match(content_str)
            if braces_match:
                content_str = braces_match.group(1)  # 提取大括号内的内容（如[1, [0.5, 0.6]]）

            # 解析为Python原生数据结构
            try:
                content = ast.literal_eval(content_str)
            except (SyntaxError, ValueError, TypeError):
                content = content_str  # 解析失败时保留原始字符串

            # trainloss 兜底：解析失败/格式异常时强制抽取数值对，避免前端收到脏值
            if data_type.startswith('trainloss'):
                if isinstance(content, str):
                    fallback_pair = self._extract_trainloss_pair(content)
                    if fallback_pair is not None:
                        content = fallback_pair
                elif isinstance(content, (list, tuple)) and len(content) >= 2:
                    try:
                        content = [float(content[0]), float(content[1])]
                    except Exception:
                        fallback_pair = self._extract_trainloss_pair(str(content))
                        if fallback_pair is not None:
                            content = fallback_pair

            # 生成并发送 payload
            if data_type in TYPE_HANDLERS:
                payload = TYPE_HANDLERS[data_type](content)
            else:
                payload = {'event': data_type, 'data': {"type": data_type, "content": content}}

            socketio.emit('multitype_log', payload)
            try:
                socketio.sleep(0)
            except Exception:
                pass

        def write(self, data):
            original_stdout.write(data)
            text = str(data)
            if not text:
                return

            text = text.replace('\r\n', '\n').replace('\r', '\n')
            self._buffer += text

            while '\n' in self._buffer:
                line, self._buffer = self._buffer.split('\n', 1)
                self._emit_line(line)

        def flush(self):
            if self._buffer.strip():
                self._emit_line(self._buffer)
            self._buffer = ""
            original_stdout.flush()

    # 重定向标准输出
    sys.stdout = TypedSocketIOStream()
    try:
        yield
    finally:
        sys.stdout = original_stdout

def get_loss_function(loss_name, **kwargs):
    if loss_name == "mse":
        return nn.MSELoss()
    elif loss_name == "mae":
        return nn.L1Loss()
    elif loss_name == "huber":
        return nn.HuberLoss()
    elif loss_name == "smooth_l1":
        return nn.SmoothL1Loss()
    elif loss_name == "log_cosh":
        class LogCoshLoss(nn.Module):
            def forward(self, pred, target):
                return torch.mean(torch.log(torch.cosh(pred - target + 1e-12)))

        return LogCoshLoss()
    elif loss_name == "quantile":
        tau = kwargs.get("tau", 0.9)

        class QuantileLoss(nn.Module):
            def forward(self, pred, target):
                diff = pred - target
                return torch.mean(torch.max(tau * diff, (tau - 1) * diff))

        return QuantileLoss()
    elif loss_name == "mape":
        class MAPELoss(nn.Module):
            def forward(self, pred, target):
                return torch.mean(torch.abs((pred - target) / (target + 1e-6)))

        return MAPELoss()
    elif loss_name == "smape":
        class SMAPELoss(nn.Module):
            def forward(self, pred, target):
                return torch.mean(
                    2 * torch.abs(pred - target) / (torch.abs(pred) + torch.abs(target) + 1e-6)
                )

        return SMAPELoss()
    else:
        raise ValueError(f"Unsupported loss function: {loss_name}")


# 训练逻辑
def train(args, userid):
    # 模型选择
    model = get_model(args)
    # 使用GPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # 清理显存碎片
    if device.type == 'cuda':
        torch.cuda.empty_cache()

    model = model.to(device)
    print(f"模型参数量：{sum(p.numel() for p in model.parameters())}")

    # 读取数据
    train_loader, val_loader = load_data_loaders(args, userid)

    # 定义损失函数和优化器
    criterion = get_loss_function(args.loss)
    phy_equation_str = str(args.phy_equation).strip()
    phy_loss_fn = build_physical_loss_from_equation(args) if phy_equation_str else None
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)

    with redirect_print():
        try:
            tr, va = external_train_model(
                model, train_loader, val_loader, criterion,
                phy_loss_fn, optimizer, args.num_epochs,
                device, args, userid
            )
        except TrainingAborted:
            print("[log]训练已中止")
            raise

    return tr, va


@train_bp.route('/hardware', methods=['GET'])
def hardware_status():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"code": 401, "message": "未提供认证token"}), 401

    token = auth_header.split(" ")[1] if auth_header.startswith('Bearer ') else auth_header
    try:
        jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({"code": 401, "message": "token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"code": 401, "message": "无效的token"}), 401
    except Exception as e:
        return jsonify({"code": 500, "message": f"token解析失败：{str(e)}"}), 500

    gpu_available = bool(torch.cuda.is_available())
    device = 'cuda' if gpu_available else 'cpu'
    gpu_count = int(torch.cuda.device_count()) if gpu_available else 0
    gpu_name = None
    if gpu_available and gpu_count > 0:
        try:
            gpu_name = torch.cuda.get_device_name(0)
        except Exception:
            gpu_name = None

    cpu_name = platform.processor() or getattr(platform.uname(), "processor", "") or platform.machine()
    cpu_name = cpu_name or "CPU"

    return jsonify({
        "code": 200,
        "message": "ok",
        "data": {
            "device": device,
            "gpu_available": gpu_available,
            "gpu_count": gpu_count,
            "gpu_name": gpu_name,
            "cpu": cpu_name,
        }
    }), 200


# 参数接口
@train_bp.route('/parameter', methods=['POST'])
def interface():
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "message": "请求数据不能为空"}), 400

    # 1. 身份验证
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"code": 401, "message": "未提供认证token"}), 401

    # 提取token
    if auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
    else:
        token = auth_header

    # 2. 解析token
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        userid = payload.get('user_id')
        if not userid:
            return jsonify({"code": 401, "message": "token中缺少user_id"}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({"code": 401, "message": "token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"code": 401, "message": "无效的token"}), 401
    except Exception as e:
        return jsonify({"code": 500, "message": f"token解析失败：{str(e)}"}), 500

    # 3. 验证必要参数
    required_fields = [
        'model_name', 'hidden_size', 'num_layers', 'dropout',
        'num_channels', 'kernel_size', 'num_heads', 'hidden_space',
        'e_layers', 'd_ff', 'moving_avg', 'factor', 'activation',
        'use_layer_norm', 'num_epochs', 'learning_rate', 'loss'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({"code": 400, "message": f"缺少必要参数：{field}"}), 400

    # 4. 查找现有记录并更新（覆盖逻辑）
    try:
        # 查找该用户的现有配置
        existing_config = ModelConfig.query.filter_by(user_id=userid).first()

        if existing_config:
            # 存在则更新字段（覆盖原有数据）
            existing_config.model_name = data['model_name']
            existing_config.hidden_size = data['hidden_size']
            existing_config.num_layers = data['num_layers']
            existing_config.dropout = data['dropout']
            existing_config.num_channels = data['num_channels']
            existing_config.kernel_size = data['kernel_size']
            existing_config.num_heads = data['num_heads']
            existing_config.hidden_space = data['hidden_space']
            existing_config.e_layers = data['e_layers']
            existing_config.d_ff = data['d_ff']
            existing_config.moving_avg = data['moving_avg']
            existing_config.factor = data['factor']
            existing_config.activation = data['activation']
            existing_config.use_layer_norm = data['use_layer_norm']
            existing_config.num_epochs = data['num_epochs']
            existing_config.learning_rate = data['learning_rate']
            existing_config.loss = data['loss']
            # 其他需要更新的字段...

            message = "参数更新成功（覆盖原有数据）"
        else:
            # 不存在则创建新记录
            existing_config = ModelConfig(
                user_id=userid,
                model_name=data['model_name'],
                hidden_size=data['hidden_size'],
                num_layers=data['num_layers'],
                dropout=data['dropout'],
                num_channels=data['num_channels'],
                kernel_size=data['kernel_size'],
                num_heads=data['num_heads'],
                hidden_space=data['hidden_space'],
                e_layers=data['e_layers'],
                d_ff=data['d_ff'],
                moving_avg=data['moving_avg'],
                factor=data['factor'],
                activation=data['activation'],
                use_layer_norm=data['use_layer_norm'],
                num_epochs=data['num_epochs'],
                learning_rate=data['learning_rate'],
                loss=data['loss']
            )
            db.session.add(existing_config)
            message = "参数保存成功（新记录）"

        db.session.commit()
        return jsonify({
            "code": 200,
            "message": message,
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": f"操作失败：{str(e)}"}), 500


# 训练路由
@train_bp.route('/start', methods=['POST'])
def process_data():
    try:
        # 1. 身份验证
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"code": 401, "message": "未提供认证token"}), 401

        token = auth_header.split(" ")[1] if auth_header.startswith('Bearer ') else auth_header

        # 2. 解析token
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            userid = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"code": 401, "message": "token已过期"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"code": 401, "message": f"无效的token: {str(e)}"}), 401

        # 3. 执行训练
        clear_abort_flag(userid)
        args = get_parameters(userid)
        payload = request.get_json(silent=True) or {}
        file_ids = payload.get("file_ids") if isinstance(payload, dict) else None
        if file_ids:
            build_and_save_data_loaders_from_file_ids(args, userid, file_ids)
        try:
            tra, val = train(args, userid)
        except TrainingAborted:
            return jsonify({
                "code": 200,
                "message": "训练已中止",
                "data": {"train_coordinate": [], "val_coordinate": []}
            }), 200

        # 4. 返回成功响应
        return jsonify({
            "code": 200,
            "message": "训练成功",
            "data": {"train_coordinate": tra,
                     "val_coordinate":val}
        }), 200

    except Exception as e:
        current_app.logger.error(f"训练过程出错: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"训练失败: {str(e)}"
        }), 500


@train_bp.route('/stop', methods=['POST'])
def stop_train():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"code": 401, "message": "未提供认证token"}), 401

    token = auth_header.split(" ")[1] if auth_header.startswith('Bearer ') else auth_header

    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        userid = payload.get('user_id')
        if not userid:
            return jsonify({"code": 401, "message": "token中缺少user_id"}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({"code": 401, "message": "token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"code": 401, "message": "无效的token"}), 401
    except Exception as e:
        return jsonify({"code": 500, "message": f"token解析失败：{str(e)}"}), 500

    set_abort_flag(userid)
    return jsonify({"code": 200, "message": "训练中止请求已接收"}), 200
