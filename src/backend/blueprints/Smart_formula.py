from flask import Blueprint, request, jsonify, current_app
import jwt
import subprocess
import logging
import os
import json
import re
from datetime import datetime
import pandas as pd
from exts import db, socketio
from models import Smartformula, User, File
import base64
from werkzeug.utils import secure_filename
import shutil
from sqlalchemy import func
import time as time_module
import threading
import uuid
import sys
from utils_path import resolve_content_path

# 全局任务状态存储（生产环境应使用Redis等持久化方案）
task_status = {}

# 全局进程引用（用于中止）
current_process = None
process_lock = threading.Lock()

def clean_ansi(text):
    """移除ANSI转义字符（进度条等）"""
    import re
    # 移除ANSI转义序列
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    # 移除回车符（进度条更新）
    text = text.replace('\r', '')
    # 移除其他控制字符
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    return text.strip()

def emit_log(message, log_type="log"):
    """发送日志到WebSocket"""
    try:
        # 清理ANSI转义字符
        message = clean_ansi(str(message))
        # 跳过空消息和纯进度条消息
        if not message or message.isspace():
            return
        # 仅跳过明显的进度条噪音，保留完整业务日志用于排障
        skip_patterns = [
            '%|', 'it/s', 'ETA', '━', '█', '▏', '▎', '▍', '▌', '▋', '▊', '▉',
            '[A',  # ANSI残留
        ]
        if any(x in message for x in skip_patterns):
            return
        # 跳过只有数字和空格的行（进度信息）
        if message.replace(' ', '').replace('.', '').replace('-', '').replace('e', '').replace('+', '').isdigit():
            return
        # 保留有用的进度信息
        keep_patterns = ['[进度]', '[Epoch', '样本数', '特征数', '公式搜索', '已保存', '===']
        is_progress = any(x in message for x in keep_patterns)
        # 如果不是进度信息，检查是否是纯数字表格行
        if not is_progress and len(message) < 5:
            return
            
        payload = {
            'event': 'log',
            'data': {
                'type': log_type,
                'content': message
            }
        }
        socketio.emit('multitype_log', payload)
        socketio.sleep(0)
    except Exception as e:
        logger.warning(f"WebSocket日志发送失败: {e}")

# 配置日志：改为DEBUG级别，显示更多排查信息
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

smart_formula_bp = Blueprint('smart_formula', __name__)

ALLOWED_EXTENSIONS = {'xlsx'}

def read_coord_json(coord_path):
    """读取坐标JSON文件，转为字符串（适配数据库coordinate字段的String类型）"""
    if not coord_path or not os.path.exists(coord_path):
        logger.warning(f"坐标文件路径不存在: {coord_path}")
        return ""

    try:
        with open(coord_path, 'r', encoding='utf-8') as f:
            coord_data = json.load(f)  # 读JSON文件内容
        return json.dumps(coord_data)  # 转为JSON字符串（方便存入String字段）
    except Exception as e:
        logger.error(f"读取坐标文件[{coord_path}]失败: {str(e)}")
        return ""  # 缺失时存空字符串，避免数据库字段为None


def get_sorted_jsons_with_index(folder_path, start_index=0):
    """
    获取目录下所有JSON文件的排序信息
    :param folder_path: 目标目录路径
    :param start_index: 起始索引（默认从0开始）
    :return: 列表，每个元素为 (索引, 文件名, 文件路径)
    """
    if not os.path.exists(folder_path):
        logger.warning(f"JSON文件目录不存在: {folder_path}")
        return []

    json_extension = '.json'  # 只筛选JSON文件
    json_files = []

    # 遍历目录下的所有文件
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # 筛选文件：必须是文件且以.json结尾（不区分大小写）
        if os.path.isfile(file_path) and filename.lower().endswith(json_extension):
            json_files.append((filename, file_path))  # 暂存 (文件名, 完整路径)

    # 按文件名排序（与处理图片的逻辑一致）
    json_files_sorted = sorted(json_files, key=lambda x: x[0])

    # 生成带索引的结果（索引从start_index开始）
    result = [(idx, filename, file_path) for idx, (filename, file_path) in
              enumerate(json_files_sorted, start=start_index)]
    # 新增日志：打印JSON文件索引列表
    logger.debug(f"JSON文件索引-文件名对应：{[(idx, name) for idx, name, _ in result]}")
    return result


def get_sorted_images_with_index(folder_path, start_index=0):
    """
    获取目录下所有图片文件的排序信息
    :param folder_path: 目标目录路径
    :param start_index: 起始索引（默认从0开始，此参数已废弃）
    :return: 列表，每个元素为 (索引, 文件名, 文件路径)，索引使用文件名中的实际数字
    """
    if not os.path.exists(folder_path):
        logger.warning(f"图片文件目录不存在: {folder_path}")
        return []

    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif', '.tif')
    image_files = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.lower().endswith(image_extensions):
            # 跳过带时间戳的旧文件
            if re.search(r'_\d{13}\.', filename):
                continue
            
            # 提取文件名中的数字作为索引
            # 统一格式: plot_000.png 或 eq_000_c1.png
            num_match = re.search(r'(?:plot_|eq_)(\d+)', filename)
            if num_match:
                file_num = int(num_match.group(1))
            else:
                # 兼容旧格式: plot岩心TOC正常__公式1.tif
                num_match = re.search(r'公式(\d+)', filename)
                if num_match:
                    file_num = int(num_match.group(1)) - 1
                else:
                    num_match = re.search(r'(\d+)', filename)
                    file_num = int(num_match.group(1)) if num_match else 0
            image_files.append((file_num, filename, file_path))

    # 按索引排序
    image_files_sorted = sorted(image_files, key=lambda x: x[0])
    # 使用文件名中的实际数字作为索引
    result = [(file_num, filename, file_path) for file_num, filename, file_path in image_files_sorted]

    logger.info(f"图片目录[{folder_path}]找到 {len(result)} 个图片")
    return result


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def safe_copy_file(src_path, dst_path, max_retries=3):
    """
    安全地复制文件，处理权限和占用问题
    """
    # 如果目标文件已存在，先尝试删除
    if os.path.exists(dst_path):
        for retry in range(max_retries):
            try:
                os.remove(dst_path)
                logger.info(f"删除已存在的目标文件：{dst_path}")
                break
            except PermissionError:
                if retry < max_retries - 1:
                    logger.warning(f"删除文件失败，等待重试 ({retry + 1}/{max_retries})")
                    time_module.sleep(0.5)
                else:
                    # 文件被占用，使用带时间戳的临时文件名
                    timestamp = int(time_module.time() * 1000)
                    base, ext = os.path.splitext(dst_path)
                    dst_path = f"{base}_{timestamp}{ext}"
                    logger.warning(f"目标文件被占用，使用临时文件名：{dst_path}")
    
    # 复制文件
    for retry in range(max_retries):
        try:
            shutil.copy2(src_path, dst_path)
            return dst_path
        except PermissionError as e:
            if retry < max_retries - 1:
                logger.warning(f"复制文件失败，等待重试 ({retry + 1}/{max_retries})")
                time_module.sleep(0.5)
            else:
                raise Exception(f"文件复制失败，权限被拒绝: {str(e)}")
        except Exception as e:
            raise Exception(f"文件复制失败: {str(e)}")
    
    return dst_path


# 获取Excel文件列名API
@smart_formula_bp.route('/get-excel-columns/<int:file_id>', methods=['GET'])
def get_excel_columns(file_id):
    """根据文件ID获取Excel文件的列名列表"""
    try:
        # 认证校验
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"code": 401, "message": "未提供认证token"}), 401
        
        token = auth_header.split(" ")[1] if auth_header.startswith('Bearer ') else auth_header
        
        try:
            jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except Exception as e:
            return jsonify({"code": 401, "message": f"token解析失败: {str(e)}"}), 401
        
        # 查询文件
        file = File.query.get(file_id)
        if not file:
            return jsonify({"code": 404, "message": f"ID为{file_id}的文件不存在"}), 404
        
        file_path = resolve_content_path(file.content)
        if not file_path or not os.path.exists(file_path):
            return jsonify({"code": 404, "message": "文件不存在于服务器"}), 404
        
        # 读取Excel列名
        df = pd.read_excel(file_path, engine='openpyxl', nrows=0)  # 只读取表头
        columns = list(df.columns)
        
        # 过滤掉Unnamed列
        columns = [c for c in columns if not str(c).startswith('Unnamed')]
        
        logger.info(f"✅ 获取文件 {file_id} 的列名: {columns}")
        
        return jsonify({
            "code": 200,
            "columns": columns,
            "count": len(columns)
        })
        
    except Exception as e:
        logger.error(f"获取列名失败: {str(e)}", exc_info=True)
        return jsonify({"code": 500, "message": f"获取列名失败: {str(e)}"}), 500


# 获取任务状态API
@smart_formula_bp.route('/task-status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """查询异步任务的执行状态"""
    global task_status
    if task_id not in task_status:
        return jsonify({"code": 404, "message": "任务不存在"}), 404
    
    status = task_status[task_id]
    return jsonify({
        "code": 200,
        "task_id": task_id,
        "status": status.get("status", "unknown"),  # pending, running, completed, failed
        "message": status.get("message", ""),
        "result": status.get("result"),
        "started_at": status.get("started_at"),
        "completed_at": status.get("completed_at")
    })


# 获取用户当前运行中的任务
@smart_formula_bp.route('/user-running-task', methods=['GET'])
def get_user_running_task():
    """查询当前用户是否有运行中的预测任务"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"code": 401, "message": "未提供认证token"}), 401
    
    token = auth_header.split(" ")[1] if auth_header.startswith('Bearer ') else auth_header
    
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except Exception as e:
        return jsonify({"code": 401, "message": f"token解析失败: {str(e)}"}), 401
    
    global task_status
    # 查找该用户的运行中任务
    running_task = None
    for task_id, status in task_status.items():
        if status.get("user_id") == user_id and status.get("status") == "running":
            running_task = {
                "task_id": task_id,
                "status": status.get("status"),
                "message": status.get("message", ""),
                "started_at": status.get("started_at")
            }
            break
    
    return jsonify({
        "code": 200,
        "has_running_task": running_task is not None,
        "task": running_task
    })


# 中止公式拟合
@smart_formula_bp.route('/stop-smart-formula', methods=['POST'])
def stop_smart_formula():
    """中止正在运行的公式拟合进程"""
    global current_process
    
    with process_lock:
        if current_process is not None and current_process.poll() is None:
            try:
                # 终止进程
                current_process.terminate()
                # 等待进程结束
                current_process.wait(timeout=5)
                logger.info("✅ 公式拟合进程已中止")
                current_process = None
                return jsonify({"code": 200, "message": "拟合已中止"})
            except subprocess.TimeoutExpired:
                # 如果terminate不起作用，强制kill
                current_process.kill()
                current_process = None
                logger.warning("⚠️ 进程强制终止")
                return jsonify({"code": 200, "message": "拟合已强制中止"})
            except Exception as e:
                logger.error(f"中止进程失败: {str(e)}")
                return jsonify({"code": 500, "message": f"中止失败: {str(e)}"}), 500
        else:
            return jsonify({"code": 200, "message": "没有正在运行的拟合任务"})


# 合并后的单路由：接收参数→处理文件→执行算法→入库结果
@smart_formula_bp.route('/run-smart-formula', methods=['POST'])
def run_smart_formula():
    try:
        # ---------------- 1. 认证校验（沿用原有逻辑） ----------------
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            logger.warning("⚠️  未提供Authorization请求头")
            return jsonify({"code": 401, "message": "未提供认证token"}), 401

        # 提取token
        token = auth_header.split(" ")[1] if auth_header.startswith('Bearer ') else auth_header

        # 验证token并获取用户ID
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
            logger.info(f"✅ token验证通过，用户ID：{user_id}")
        except jwt.ExpiredSignatureError:
            logger.warning("⚠️  token已过期")
            return jsonify({"code": 401, "message": "token已过期"}), 401
        except jwt.InvalidTokenError as e:
            logger.error(f"⚠️  token无效：{str(e)}")
            return jsonify({"code": 401, "message": f"token无效: {str(e)}"}), 401
        except Exception as e:
            logger.error(f"⚠️  token解析失败：{str(e)}", exc_info=True)
            return jsonify({"code": 401, "message": f"token解析失败: {str(e)}"}), 401


        # ---------------- 2. 接收前端参数并校验 ----------------
        data = request.get_json()
        if not data:
            return jsonify({"code": 400, "message": "未接收到配置参数"}), 400

        # 必传参数校验
        required_params = ['id', '目标文件名', '目标目录', '目标参数']
        for param in required_params:
            if param not in data:
                logger.error(f"缺少必传参数: {param}")
                return jsonify({"code": 400, "message": f"缺少必传参数: {param}"}), 400

        # 提取核心参数
        file_id = data['id']
        target_dir_name = data['目标目录']
        target_filename = data['目标文件名']
        target_param = data['目标参数']
        # 过滤id，保留前端所有配置参数（用于存储和算法调用）
        config_params = {k: v for k, v in data.items() if k != 'id'}
        logger.info(f"✅ 接收前端参数完成，共{len(config_params)}个配置项")


        # ---------------- 3. 处理原始文件（复制到目标目录） ----------------
        # 从数据库查询原始文件
        file = File.query.get(file_id)
        if not file:
            return jsonify({"code": 404, "message": f"ID为{file_id}的文件不存在"}), 404

        original_file_path = resolve_content_path(file.content)
        if not original_file_path or not os.path.exists(original_file_path):
            return jsonify({"code": 404, "message": "原始文件不存在于服务器"}), 404

        # 复制文件到前端指定目录（使用安全复制函数）
        target_dir = os.path.join(current_app.root_path, target_dir_name)
        os.makedirs(target_dir, exist_ok=True)
        target_file_path = os.path.join(target_dir, target_filename)
        
        try:
            target_file_path = safe_copy_file(original_file_path, target_file_path)
            logger.info(f"✅ 原始文件复制完成：{target_file_path}")
        except Exception as e:
            logger.error(f"文件复制失败: {str(e)}")
            return jsonify({"code": 500, "message": f"文件复制失败：{str(e)}。请确保文件未被其他程序（如Excel）占用。"}), 500


        # ---------------- 4. 保存参数到算法识别路径 ----------------
        # 生成参数Excel（算法依赖此文件）
        params_df = pd.DataFrame(list(config_params.items()), columns=['Parameter', 'Value'])
        settings_dir = os.path.join(current_app.root_path, '运行前设置')
        os.makedirs(settings_dir, exist_ok=True)
        params_excel_path = os.path.join(settings_dir, 'parameters_template.xlsx')
        
        # 如果参数文件已存在，先尝试删除（处理文件占用问题）
        if os.path.exists(params_excel_path):
            try:
                os.remove(params_excel_path)
                logger.info(f"删除已存在的参数文件：{params_excel_path}")
            except PermissionError:
                # 文件被占用，使用带时间戳的临时文件名
                import time as time_module
                timestamp = int(time_module.time() * 1000)
                base, ext = os.path.splitext(params_excel_path)
                params_excel_path = f"{base}_{timestamp}{ext}"
                logger.warning(f"参数文件被占用，使用临时文件名：{params_excel_path}")
        
        try:
            # 打印要保存的关键参数
            logger.info(f"📊 准备保存的参数:")
            for _, row in params_df.iterrows():
                if row['Parameter'] in ['niterations', 'populations', 'population_size', 'ncycles_per_iteration']:
                    logger.info(f"   {row['Parameter']} = {row['Value']}")
            
            params_df.to_excel(params_excel_path, index=False, engine='openpyxl')
            logger.info(f"✅ 参数文件保存完成：{params_excel_path}")
        except PermissionError as e:
            logger.error(f"参数文件保存权限错误: {str(e)}")
            return jsonify({"code": 500, "message": f"参数文件保存失败：权限被拒绝。请确保文件未被Excel等程序占用后重试。"}), 500
        except Exception as e:
            logger.error(f"参数文件保存失败: {str(e)}")
            return jsonify({"code": 500, "message": f"参数文件保存失败：{str(e)}"}), 500

        # ---------------- 5. 清理旧结果文件 ----------------
        # 在运行前清理目标目录，避免旧文件干扰
        target_filename_no_ext = os.path.splitext(target_filename)[0]
        plot_root_dir = os.path.join(current_app.root_path, '绘图', target_dir_name, target_filename_no_ext)
        
        if os.path.exists(plot_root_dir):
            emit_log(f"🧹 清理旧结果文件...", "info")
            try:
                import shutil
                shutil.rmtree(plot_root_dir)
                logger.info(f"✅ 已清理旧目录: {plot_root_dir}")
            except Exception as e:
                logger.warning(f"清理旧目录失败: {str(e)}")
                # 尝试删除单个文件
                for root, dirs, files in os.walk(plot_root_dir):
                    for f in files:
                        try:
                            os.remove(os.path.join(root, f))
                        except:
                            pass

        # ---------------- 6. 执行算法脚本 ----------------
        global current_process
        app_root = current_app.root_path
        script_path = os.path.join(app_root, 'new_main_2.py')
        if not os.path.exists(script_path):
            logger.error(f"算法脚本不存在: {script_path}")
            emit_log(f"❌ 算法脚本不存在: {script_path}", "error")
            return jsonify({"code": 500, "message": f"算法脚本不存在: {script_path}"}), 500

        # 执行脚本（使用Popen以便可以中止，并实时读取输出）
        # 将参数文件路径作为命令行参数传递
        logger.info(f"🚀 开始执行算法脚本：{script_path}")
        logger.info(f"📄 参数文件路径：{params_excel_path}")
        emit_log(f"🚀 开始执行公式拟合算法...", "info")
        emit_log(f"📁 目标文件: {target_filename}", "info")
        emit_log(f"📊 目标参数: {target_param}", "info")
        
        with process_lock:
            current_process = subprocess.Popen(
                [sys.executable, "-u", script_path, "--params", params_excel_path],  # 传递参数文件路径
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 合并stderr到stdout
                text=True,
                encoding='utf-8',
                bufsize=1,  # 行缓冲
                cwd=app_root  # 设置工作目录
            )
        
        # 实时读取并发送日志
        stdout_lines = []
        try:
            for line in iter(current_process.stdout.readline, ''):
                if line:
                    line = line.strip()
                    stdout_lines.append(line)
                    emit_log(line, "log")
                    logger.debug(f"[算法输出] {line}")
                if current_process.poll() is not None:
                    break
        except Exception as e:
            logger.error(f"读取进程输出失败: {e}")
        
        # 等待进程完成
        returncode = current_process.wait()
        
        with process_lock:
            current_process = None
        
        logger.info(f"✅ 脚本执行完成，返回码: {returncode}")
        emit_log(f"✅ 算法执行完成，返回码: {returncode}", "info")

        # 脚本执行失败直接返回
        if returncode != 0:
            error_msg = '\n'.join(stdout_lines[-10:]) if stdout_lines else "未知错误"
            logger.error(f"脚本执行错误: {error_msg}")
            emit_log(f"❌ 算法执行失败: {error_msg}", "error")
            return jsonify({
                "code": 500,
                "状态": "失败",
                "错误": error_msg
            }), 500


        # ---------------- 7. 动态生成结果路径（避免硬编码） ----------------
        emit_log("📂 正在检查结果文件...", "info")
        # 路径已在清理步骤中定义，这里只需补充子目录
        target_folder = plot_root_dir  # 预测对比图目录
        target_folder1 = os.path.join(plot_root_dir, 'latex_per_equation')  # 公式图片目录
        json_folder = plot_root_dir  # JSON坐标目录
        # Excel文件路径（依赖目标参数名）- 查找最新的文件（可能带时间戳）
        def find_latest_excel(directory, pattern):
            """查找匹配模式的最新Excel文件"""
            import glob
            import re
            # 匹配不带时间戳和带时间戳的文件
            base_pattern = os.path.join(directory, pattern)
            # 查找所有匹配的文件
            matches = glob.glob(base_pattern.replace('.xlsx', '*.xlsx'))
            if not matches:
                return None
            # 按修改时间排序，返回最新的
            matches.sort(key=os.path.getmtime, reverse=True)
            logger.info(f"找到Excel文件: {matches[0]} (共{len(matches)}个匹配)")
            return matches[0]
        
        excel_path = find_latest_excel(plot_root_dir, f'各级复杂度公式_每级最优_{target_param}.xlsx')
        excel_path1 = find_latest_excel(plot_root_dir, f'各级复杂度公式_逐式指标_{target_param}.xlsx')

        # 校验结果路径是否存在
        for path in [target_folder, target_folder1, json_folder]:
            if not os.path.exists(path):
                logger.error(f"结果目录不存在: {path}")
                emit_log(f"❌ 结果目录不存在: {path}", "error")
                return jsonify({"code": 500, "message": f"结果目录不存在: {path}"}), 500
        for path in [excel_path, excel_path1]:
            if not path or not os.path.exists(path):
                logger.error(f"结果Excel不存在: {path}")
                emit_log(f"❌ 结果Excel不存在: {path}", "error")
                return jsonify({"code": 500, "message": f"结果Excel不存在: {path}"}), 500

        emit_log("✅ 结果文件检查通过", "info")

        # ---------------- 8. 处理结果数据并入库 ----------------
        emit_log("💾 正在保存结果到数据库...", "info")
        # 生成批次号
        max_batch = db.session.query(func.max(Smartformula.batch_number)).scalar() or 0
        current_batch = max_batch + 1
        logger.info(f"📦 当前批次号: {current_batch}")

        # 获取排序后的文件列表
        sorted_images = get_sorted_images_with_index(target_folder, start_index=0)
        sorted_formula_images = get_sorted_images_with_index(target_folder1, start_index=0)
        sorted_jsons = get_sorted_jsons_with_index(json_folder, start_index=0)
        coord_dict = {idx: path for idx, name, path in sorted_jsons}

        emit_log(f"📷 找到 {len(sorted_images)} 个拟合图, {len(sorted_formula_images)} 个公式图", "info")

        # 读取Excel结果
        df_best = pd.read_excel(excel_path)  # 每级最优
        df_step = pd.read_excel(excel_path1)  # 逐级指标
        
        # 处理Excel索引为整数
        df_best['index'] = pd.to_numeric(df_best['index'], errors='coerce').fillna(0).astype(int)
        df_step['index'] = pd.to_numeric(df_step['index'], errors='coerce').fillna(0).astype(int)

        # 转换Excel数据为字典（index为键）
        best_params = {
            row['index']: row.drop('index').to_dict()
            for _, row in df_best.iterrows()
        }
        step_params = {
            row['index']: row.drop('index').to_dict()
            for _, row in df_step.iterrows()
        }
        
        logger.info(f"📊 加载结果完成：每级最优{len(best_params)}条，逐级指标{len(step_params)}条")
        emit_log(f"📊 发现 {len(step_params)} 个公式待入库", "info")


        # ---------------- 9. 遍历结果入库（使用逐级指标，包含所有公式） ----------------
        matched_count = 0
        skipped_count = 0
        # 关键修复：使用 step_params（所有公式）而不是 best_params（每级最优）
        for idx in step_params.keys():
            # 匹配文件和数据
            img_info = next((item for item in sorted_images if item[0] == idx), None)
            formula_info = next((item for item in sorted_formula_images if item[0] == idx), None)
            coord_content = read_coord_json(coord_dict.get(idx)) if idx in coord_dict else ""
            step_param = step_params.get(idx, {})  # 使用逐级指标参数（包含所有公式）

            # 校验关键数据 - 只需要图片和step_param
            if not (img_info and formula_info and step_param):
                logger.warning(f"索引{idx}缺失关键数据: img={img_info is not None}, formula={formula_info is not None}, param={bool(step_param)}")
                skipped_count += 1
                continue

            # 校验图片文件存在性
            external_pred_path = img_info[2]
            external_formula_path = formula_info[2]
            if not (os.path.exists(external_pred_path) and os.path.exists(external_formula_path)):
                logger.warning(f"索引{idx}图片不存在: pred={os.path.exists(external_pred_path)}, formula={os.path.exists(external_formula_path)}")
                skipped_count += 1
                continue

            # 创建数据库记录 - 使用step_param作为主要数据源
            new_record = Smartformula(
                user_id=user_id,
                file_name=None,
                file_path=None,
                formula_name=None,
                formula_path=None,
                coordinate=coord_content,
                # 主要参数（来自逐级指标）
                index=str(idx),
                complexity=str(step_param.get('complexity', "")),
                loss=str(step_param.get('loss', "")),
                score=str(step_param.get('score', "")),
                r2=str(step_param.get('r2', "")),
                mae=str(step_param.get('mae', "")),
                mse=str(step_param.get('mse', "")),
                rmse=str(step_param.get('rmse', "")),
                latex=step_param.get('latex', ""),
                # 备用字段（同样使用step_param）
                indexb=str(idx),
                complexityb=str(step_param.get('complexity', "")),
                lossb=str(step_param.get('loss', "")),
                scoreb=str(step_param.get('score', "")),
                r2b=str(step_param.get('r2', "")),
                maeb=str(step_param.get('mae', "")),
                mseb=str(step_param.get('mse', "")),
                rmseb=str(step_param.get('rmse', "")),
                latexb=step_param.get('latex', ""),
                # 批次号
                batch_number=current_batch,
                created_at=datetime.utcnow(),
            )

            # 复制图片到存储目录
            try:
                # 保存预测对比图
                with open(external_pred_path, 'rb') as f:
                    new_record.save_prediction_plot(f.read(), file_ext='png')
                # 保存公式图片
                with open(external_formula_path, 'rb') as f:
                    new_record.save_formula_image(f.read(), file_ext='png')
            except Exception as e:
                logger.error(f"索引{idx}图片保存失败: {str(e)}", exc_info=True)
                continue

            # 添加到数据库会话
            db.session.add(new_record)
            matched_count += 1
            logger.debug(f"索引{idx}已加入会话")


        logger.info(f"📊 入库统计: 成功={matched_count}, 跳过={skipped_count}, 总计={len(step_params)}")
        emit_log(f"📊 入库统计: 成功={matched_count}, 跳过={skipped_count}", "info")

        # ---------------- 10. 提交数据库事务 ----------------
        try:
            db.session.commit()
            logger.info(f"✅ 批次{current_batch}成功入库{matched_count}条记录")
            emit_log(f"✅ 成功保存 {matched_count} 条公式记录到数据库", "info")
        except Exception as e:
            db.session.rollback()
            logger.error(f"数据库提交失败: {str(e)}", exc_info=True)
            emit_log(f"❌ 数据库保存失败: {str(e)}", "error")
            return jsonify({"code": 500, "message": f"数据入库失败: {str(e)}"}), 500


        # ---------------- 10. 返回成功结果 ----------------
        emit_log(f"🎉 公式拟合完成！共生成 {matched_count} 个公式", "info")
        return jsonify({
            "code": 200,
            "状态": "成功",
            "批次号": current_batch,
            "匹配成功记录数": matched_count,
            "入库记录数": matched_count,
            "配置参数": config_params,  # 可选：返回参数供前端校验
            # "脚本输出": script_result.stdout[:1000],
        })

    except Exception as e:
        logger.error(f"接口执行异常: {str(e)}", exc_info=True)
        emit_log(f"❌ 接口执行异常: {str(e)}", "error")
        return jsonify({
            "code": 500,
            "状态": "异常",
            "原因": str(e)
        }), 500




# 返回用户最新批次的图片(最新公式) - 每个公式包含拟合图和公式图
@smart_formula_bp.route('/Reimage', methods=['GET'])
def Reimage():
    # 1. 身份验证
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"code": "401", "message": "未提供认证token"}), 401

    token = auth_header.split(" ")[1] if auth_header.startswith('Bearer ') else auth_header

    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except Exception as e:
        return jsonify({"code": "401", "message": f"token解析失败: {str(e)}"}), 401

    try:
        # 查询用户的最新批次号
        latest_batch = db.session.query(db.func.max(Smartformula.batch_number)). \
            filter(Smartformula.user_id == user_id).scalar()

        if not latest_batch:
            return jsonify({"code": "404", "message": "未找到该用户的图片数据"}), 404

        # 查询该用户最新批次的所有记录
        latest_records = Smartformula.query.filter(
            Smartformula.user_id == user_id,
            Smartformula.batch_number == latest_batch
        ).order_by(Smartformula.id).all()

        if not latest_records:
            return jsonify({"code": "404", "message": "未找到最新批次的图片数据"}), 404

        # 处理图片数据，每个公式包含拟合图和公式图
        result = []
        for record in latest_records:
            item = {
                "id": record.id,
                "index": record.index,
                "complexity": record.complexity,
                "r2": record.r2,
                "mae": record.mae,
                "rmse": record.rmse,
                "latex": record.latex,
                "data": {}
            }
            
            # 读取拟合曲线图（预测对比图）
            if record.file_path and os.path.exists(record.file_path):
                try:
                    with open(record.file_path, 'rb') as f:
                        file_data = f.read()
                    item["data"]["prediction_picture"] = base64.b64encode(file_data).decode('utf-8')
                except Exception as e:
                    logger.warning(f"读取拟合图失败: {str(e)}")
            
            # 读取公式图片（LaTeX公式图）
            if record.formula_path and os.path.exists(record.formula_path):
                try:
                    with open(record.formula_path, 'rb') as f:
                        file_data = f.read()
                    item["data"]["formula_picture"] = base64.b64encode(file_data).decode('utf-8')
                except Exception as e:
                    logger.warning(f"读取公式图失败: {str(e)}")
            
            # 只有当至少有一张图片时才添加
            if item["data"]:
                result.append(item)

        if not result:
            return jsonify({"code": "404", "message": "图片数据不存在或无法读取"}), 404

        logger.info(f"返回 {len(result)} 个公式的图片数据")
        return jsonify({
            "code": "200",
            "message": "返回图片数据成功",
            "image_count": len(result),
            "批次": latest_batch,
            "images": result
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"获取图片失败: {str(e)}", exc_info=True)
        return jsonify({"code": "500", "message": f"获取图片失败: {str(e)}"}), 500



# 点击图片 给前端发送坐标和公式图片（图片）----前端 data = {'id': 1}
@smart_formula_bp.route('/Resmart', methods=['POST'])
def Resmart():
    # 1. 身份验证
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"code": 401, "message": "未提供认证token"}), 401

    if auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
    else:
        token = auth_header

    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except Exception as e:
        return jsonify({"code": 401, "message": f"token解析失败: {str(e)}"}), 401

    try:
        # 获取前端传入的id
        data = request.get_json()
        if not data or 'id' not in data:
            return jsonify({"code": 400, "message": "请求中未包含id参数"}), 400

        smart_id = data['id']

        # 验证id是否为整数
        try:
            smart_id = int(smart_id)
        except ValueError:
            return jsonify({"code": 400, "message": "id必须为整数"}), 400

        # 根据id查询对应的记录
        formula_record = Smartformula.query.filter_by(
            id=smart_id,
            user_id=user_id  # 确保只能查询当前用户的记录
        ).first()

        if not formula_record:
            return jsonify({"code": 404, "message": f"未找到id为{smart_id}的记录"}), 404

        # 处理公式图片数据（从文件路径读取）
        formula_image_data = None
        if formula_record.formula_path and os.path.exists(formula_record.formula_path):
            try:
                import base64
                with open(formula_record.formula_path, 'rb') as f:
                    file_data = f.read()
                formula_image_data = base64.b64encode(file_data).decode('utf-8')
            except Exception as e:
                print(f"读取公式图片失败: {str(e)}")
                # 不中断请求，仅记录错误并返回None

        # 准备返回结果
        result = {
            "id": formula_record.id,
            "coordinate": formula_record.coordinate,  # 返回坐标数据
            "formula_image": {
                "data": {
                    "picture": formula_image_data,
                    "format": "base64"
                } if formula_image_data else None
            }
        }

        return jsonify({
            "code": 200,
            "message": "查询成功",
            "data": result
        })

    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"}), 500



# 返回公式中所有的记录（已有公式分页）----前端 data = {'id': 1,'pageNum': 1}
@smart_formula_bp.route('/Formulaspage', methods=['POST'])
def Formulaspage():
    # 1. 身份验证
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"code": "401", "message": "未提供认证token"}), 401

    if auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
    else:
        return jsonify({"code": "401", "message": "token格式错误，应使用Bearer格式"}), 401

    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"code": "401", "message": "token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"code": "401", "message": "无效token"}), 401
    except Exception as e:
        return jsonify({"code": "401", "message": f"token解析失败: {str(e)}"}), 401

    # 验证用户存在性
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": "404", "message": "用户不存在"}), 404

    # 获取请求数据
    data = request.get_json()
    if not data:
        return jsonify({"code": "400", "message": "请求数据不能为空"}), 400

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

    # 使用数据库分页查询，提高性能
    pagination = Smartformula.query.filter_by(user_id=user_id).paginate(
        page=page, per_page=page_size, error_out=False
    )

    # 获取当前页数据
    formulas = pagination.items
    total_count = pagination.total
    total_pages = pagination.pages

    # 处理公式数据
    formula_list = []
    for formula in formulas:
        # 处理公式图片数据（从文件读取并转base64）
        formula_image = None
        if formula.formula_path and os.path.exists(formula.formula_path):
            try:
                import base64
                with open(formula.formula_path, 'rb') as f:
                    file_data = f.read()
                formula_image = {
                    "data": {
                        "picture": base64.b64encode(file_data).decode('utf-8'),
                        "format": "base64"
                    }
                }
            except Exception as e:
                print(f"读取公式图片失败: {str(e)}")
                formula_image = None

        formula_list.append({
            "id": formula.id,
            "formula_name": formula.formula_name,  # 字段名从Formula_name改为formula_name
            "created_at": formula.created_at.isoformat() if formula.created_at else None,
            "formula_image": formula_image,
            "r2b": formula.r2b,
            "config_params": formula.config_params  # 添加配置参数字段
        })

    # 定义表头
    columns = [
        {"title": "公式名称", "dataIndex": "formula_name", "key": "formula_name"},
        {"title": "保存时间", "dataIndex": "created_at", "key": "created_at"},
        {"title": "公式图片", "dataIndex": "formula_image", "key": "formula_image"},
        {"title": "r2b指标", "dataIndex": "r2b", "key": "r2b"}
    ]

    # 构建响应数据
    response_data = {
        "pageNum": page,
        "pageSize": page_size,
        "totalPages": total_pages,
        "totalCount": total_count,
        "columns": columns,
        "dataSource": formula_list  # 已分页，直接使用当前页数据
    }

    return jsonify({
        "code": "00000",
        "message": "查询成功",
        "data": response_data
    })



# 删除所有中的某条记录----data = {'id': 1}
@smart_formula_bp.route('/Deleterecord', methods=['POST'])
def Deleterecord():
    # 1. 身份验证
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
    except Exception as e:
        return jsonify({"code": 401, "message": f"token解析失败: {str(e)}"}), 401

    try:
        # 2. 获取前端传入的id
        data = request.get_json()
        if not data or 'id' not in data:
            return jsonify({"code": 400, "message": "请求中未包含id参数"}), 400

        record_id = data['id']

        # 验证id是否为整数
        try:
            record_id = int(record_id)
        except ValueError:
            return jsonify({"code": 400, "message": "id必须为整数"}), 400

        # 3. 查询对应的记录并验证权限（只能删除自己的记录）
        record = Smartformula.query.filter_by(
            id=record_id,
            user_id=user_id
        ).first()

        if not record:
            return jsonify({"code": 404, "message": f"未找到id为{record_id}的记录或无权限删除"}), 404

        # 4. 先删除关联的图片文件
        try:
            record.delete_files()  # 调用模型中的方法删除图片文件
        except Exception as e:
            print(f"删除图片文件时发生错误: {str(e)}")
            # 即使删除文件失败，仍继续删除数据库记录，但在消息中提示
            # 也可以选择在此处返回错误，根据业务需求决定

        # 5. 再删除数据库记录
        db.session.delete(record)
        db.session.commit()

        return jsonify({
            "code": 200,
            "message": f"id为{record_id}的记录及关联图片已成功删除"
        })

    except Exception as e:
        # 发生错误时回滚事务
        db.session.rollback()
        return jsonify({"code": 500, "message": f"删除失败: {str(e)}"}), 500




# 前端发送表文件id然后我从file数据库中拿到它的路径并存放到算法使用的路径
@smart_formula_bp.route('/rename-save-file', methods=['POST'])
def rename_and_save_file():
    """
    接收文件ID，获取对应文件，重命名为TOC.xlsx并保存到test目录
    """
    # 获取前端传来的文件ID
    data = request.get_json()
    if not data or 'file_id' not in data:
        return jsonify({'error': '请提供文件ID'}), 400

    file_id = data['file_id']

    # 验证文件ID是否为整数
    try:
        file_id = int(file_id)
    except ValueError:
        return jsonify({'error': '文件ID必须是整数'}), 400

    # 根据ID查询文件
    file = File.query.filter_by(id=file_id, deleted_at=None).first()
    if not file:
        return jsonify({'error': '未找到指定文件或文件已被删除'}), 404

    # 检查原始文件是否存在
    original_path = resolve_content_path(file.content)
    if not original_path or not os.path.exists(original_path):
        return jsonify({'error': '原始文件不存在于服务器中'}), 404

    # 定义目标保存路径
    app_root = current_app.root_path
    script_path = os.path.join(app_root, 'test')
    target_path = os.path.join(script_path, 'TOC.xlsx')

    try:
        # 确保目标目录存在
        os.makedirs(script_path, exist_ok=True)

        # 读取原始文件内容
        with open(original_path, 'rb') as f:
            file_content = f.read()

        # 保存到目标路径（会覆盖已有文件）
        with open(target_path, 'wb') as f:
            f.write(file_content)

        return jsonify({
            'message': '文件已成功重命名并保存',
            'original_file': file.name,
            'saved_path': target_path
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'处理文件时发生错误: {str(e)}'}), 500
