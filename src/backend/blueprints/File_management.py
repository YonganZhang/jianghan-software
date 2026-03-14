from flask import Blueprint, request, jsonify, current_app
import datetime
from models import User, Directory, File
from exts import db
import jwt
from werkzeug.exceptions import Unauthorized
import hashlib
import uuid
from io import BytesIO, StringIO
import pandas as pd
import os
import re
import numpy as np
from utils_path import resolve_content_path, to_relative_content_path


auth_bp = Blueprint('auth', __name__)

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

def calculate_sha256(data, chunk_size=8192):
    """分块计算哈希，减少内存占用，提升大文件处理速度"""
    sha256 = hashlib.sha256()
    if hasattr(data, 'read'):
        while chunk := data.read(chunk_size):
            sha256.update(chunk)
        data.seek(0)
    else:
        sha256.update(data)
    return sha256.hexdigest()


def _decode_text_bytes(data: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "gb18030", "gbk", "latin-1"):
        try:
            return data.decode(enc)
        except Exception:
            continue
    return data.decode("utf-8", errors="ignore")


def _try_parse_forward_txt(text: str):
    """
    尝试解析 Forward 软件导出的 TXT 格式。
    格式特征:
      第1行: FORWARD_TEXT_FORMAT_x.x
      后续行: KEY = VALUE (如 STDEP, ENDEP, RLEV, CURVENAME)
      END 标记头部结束
      #DEPTH ... 列名行
      数值数据行
    返回 DataFrame 或 None（不是 Forward 格式时）。
    """
    lines = text.splitlines()
    if not lines:
        return None
    # 检测 Forward 格式标识
    first = lines[0].strip()
    if not first.upper().startswith("FORWARD_TEXT_FORMAT"):
        return None

    curve_names = []
    data_start = None

    for i, ln in enumerate(lines[1:], start=1):
        stripped = ln.strip()
        if not stripped:
            continue
        # 头部 KEY = VALUE
        if "=" in stripped and data_start is None:
            key, _, val = stripped.partition("=")
            key = key.strip().upper()
            if key == "CURVENAME":
                # CURVENAME = A, B, C, ...
                curve_names = [c.strip() for c in val.split(",") if c.strip()]
            continue
        if stripped.upper() == "END":
            continue
        # 列名行: 以 #DEPTH 或 # DEPTH 开头
        if stripped.startswith("#"):
            header_str = stripped.lstrip("#").strip()
            cols = header_str.split()
            if cols:
                curve_names = cols  # 用实际列名行覆盖 (含 DEPTH)
            data_start = i + 1
            continue
        # 到达数值行
        if data_start is None:
            # 如果没有 # 列名行，检测第一个全数值行
            parts = stripped.split()
            try:
                [float(p) for p in parts]
                data_start = i
            except ValueError:
                continue

    if data_start is None:
        return None

    # 解析数据行
    rows = []
    for ln in lines[data_start:]:
        stripped = ln.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        try:
            vals = [float(p) for p in parts]
            rows.append(vals)
        except ValueError:
            continue

    if not rows:
        return None

    # 如果 curve_names 不含 DEPTH，加上
    if curve_names and curve_names[0].upper() not in ("DEPTH", "DEPT"):
        curve_names = ["DEPTH"] + curve_names

    # 对齐列数
    ncols = len(rows[0])
    if curve_names and len(curve_names) != ncols:
        if len(curve_names) == ncols - 1:
            curve_names = ["DEPTH"] + curve_names
        else:
            curve_names = [f"COL{j+1}" for j in range(ncols)]
    if not curve_names:
        curve_names = [f"COL{j+1}" for j in range(ncols)]

    df = pd.DataFrame(rows, columns=curve_names)
    return df


def _try_parse_welllog_txt(text: str):
    """
    通用测井 TXT 解析器 —— 智能跳过文件头部的注释/元数据行,
    自动检测列名行和数据起始位置。
    兼容场景:
      - 以 # 或 ~ 开头的注释行
      - KEY = VALUE 或 KEY : VALUE 形式的元数据
      - 带 # 前缀的列名行 (如 #DEPTH GR SP ...)
      - 纯列名行 (DEPTH GR SP ...)
      - 直接数值行 (无列名)
    返回 DataFrame 或 None。
    """
    lines = text.splitlines()
    if not lines:
        return None

    # ---- 第1遍: 找到第一个全数值行的位置 ----
    first_data_idx = None
    for i, ln in enumerate(lines):
        stripped = ln.strip()
        if not stripped:
            continue
        parts = stripped.lstrip("#").split()
        try:
            [float(p) for p in parts]
            first_data_idx = i
            break
        except ValueError:
            continue

    if first_data_idx is None:
        return None

    # ---- 第2遍: 在数据行之前寻找列名行 ----
    col_names = []
    # 从 first_data_idx 往上找最近的非空行作为列名候选
    for j in range(first_data_idx - 1, -1, -1):
        candidate = lines[j].strip()
        if not candidate:
            continue
        # 去掉 # 前缀
        header_text = candidate.lstrip("#").strip()
        tokens = header_text.split()
        if not tokens:
            continue
        # 列名行: 至少有一个非纯数字的 token
        has_non_numeric = False
        for t in tokens:
            try:
                float(t)
            except ValueError:
                has_non_numeric = True
                break
        if has_non_numeric and len(tokens) > 1:
            col_names = tokens
        break

    # ---- 第3遍: 收集数据行 ----
    rows = []
    for ln in lines[first_data_idx:]:
        stripped = ln.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("~"):
            continue
        parts = stripped.split()
        try:
            vals = [float(p) for p in parts]
            rows.append(vals)
        except ValueError:
            continue

    if not rows:
        return None

    ncols = len(rows[0])
    if col_names and len(col_names) != ncols:
        col_names = []  # 列数不匹配，放弃列名
    if not col_names:
        col_names = [f"COL{j+1}" for j in range(ncols)]

    # 过滤列数不一致的行
    rows = [r for r in rows if len(r) == ncols]
    if not rows:
        return None

    df = pd.DataFrame(rows, columns=col_names)
    return df


def _read_txt_bytes_to_df(data: bytes) -> pd.DataFrame:
    text = _decode_text_bytes(data)

    # 1) 尝试 Forward 格式
    df = _try_parse_forward_txt(text)
    if df is not None and df.shape[1] > 1:
        return df

    # 2) 尝试通用测井 TXT 格式（带头部注释/元数据）
    df = _try_parse_welllog_txt(text)
    if df is not None and df.shape[1] > 1:
        return df

    # 3) 回退: 传统 CSV/TSV 解析
    last_error = None
    for read_kwargs in (
        {"sep": None, "engine": "python"},
        {"sep": r"\s+", "engine": "python"},
        {"sep": ",", "engine": "python"},
        {"sep": "\t", "engine": "python"},
    ):
        try:
            df = pd.read_csv(StringIO(text), **read_kwargs)
            if df.shape[1] > 1:
                return df
        except Exception as e:
            last_error = e
            continue
    raise ValueError(f"无法解析TXT数据: {last_error}")


def _read_las_bytes_to_df(data: bytes) -> pd.DataFrame:
    text = _decode_text_bytes(data)
    lines = [ln.strip() for ln in text.splitlines()]

    curve_names = []
    rows = []
    null_value = None
    in_curve = False
    in_ascii = False

    for ln in lines:
        if not ln or ln.startswith("#"):
            continue

        if ln.lstrip().startswith("~"):
            tag = ln.strip().upper()
            in_curve = tag.startswith("~C")
            in_ascii = tag.startswith("~A") or tag.startswith("~ASCII")
            continue

        if not in_ascii:
            if null_value is None:
                m = re.match(r"^NULL\.?\s*([^\s:]+)", ln, flags=re.IGNORECASE)
                if m:
                    try:
                        null_value = float(m.group(1))
                    except Exception:
                        null_value = None
            if in_curve:
                left = ln.split(":", 1)[0].strip()
                if not left:
                    continue
                mnemonic = left.split(".", 1)[0].split()[0].strip()
                if mnemonic:
                    curve_names.append(mnemonic)
            continue

        parts = [p for p in re.split(r"\s+", ln) if p]
        if not parts:
            continue
        if not curve_names:
            curve_names = [f"COL{i + 1}" for i in range(len(parts))]
        if len(parts) < len(curve_names):
            continue
        rows.append(parts[: len(curve_names)])

    if not rows:
        raise ValueError("LAS文件缺少可解析的~A数据段")

    df = pd.DataFrame(rows, columns=curve_names)
    df = df.apply(pd.to_numeric, errors="coerce")
    if null_value is not None:
        df = df.replace(null_value, np.nan)
    return df


def _read_supported_file_to_df(file_record, file_content: bytes) -> pd.DataFrame:
    ext = os.path.splitext(file_record.name or "")[1].lower()
    if file_record.type == "xlsx" or ext in (".xlsx", ".xls"):
        return pd.read_excel(BytesIO(file_content))
    if ext == ".las":
        return _read_las_bytes_to_df(file_content)
    return _read_txt_bytes_to_df(file_content)


def _get_unique_xlsx_filename(user_id: int, directory_id: int, base_name: str, exclude_file_id=None) -> str:
    desired = f"{base_name}.xlsx"
    candidate = desired
    suffix_idx = 0
    while True:
        q = File.query.filter(
            File.user_id == user_id,
            File.directory_id == directory_id,
            File.deleted_at.is_(None),
            File.name == candidate,
        )
        if exclude_file_id is not None:
            q = q.filter(File.id != exclude_file_id)
        if not q.first():
            return candidate
        suffix_idx += 1
        if suffix_idx == 1:
            candidate = f"{base_name}-副本.xlsx"
        else:
            candidate = f"{base_name}-副本{suffix_idx}.xlsx"


# todo 数据导入-分页传表
@auth_bp.route('/page', methods=['POST'])
def get_table():
    # 身份验证部分保持不变
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
    except jwt.ExpiredSignatureError:
        return jsonify({"code": 401, "message": "token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"code": 401, "message": "无效token"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "message": "用户不存在"}), 404

    # 获取请求数据
    data = request.get_json()
    file_id = data.get('id')
    if not file_id:
        return jsonify({"code": 400, "message": "缺少文件ID"}), 400

    # 获取文件并验证所有权（逻辑不变）
    file_record = File.query.filter_by(id=file_id, user_id=user_id, deleted_at=None).first()
    if not file_record:
        return jsonify({"code": 404, "message": "文件不存在或已被删除"}), 404

    try:
        real_path = resolve_content_path(file_record.content)
        if not real_path or not os.path.exists(real_path):
            return jsonify({"code": 404, "message": "文件已损坏或被删除"}), 404

        # 从磁盘文件读取内容（关键修改：通过路径打开文件）
        with open(real_path, 'rb') as f:
            file_content = f.read()  # 读取文件二进制内容
        df = _read_supported_file_to_df(file_record, file_content)
        df.columns = [str(c).strip() for c in df.columns]
        df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
        headers = df.columns.tolist()

        # 获取分页参数
        page = data.get('pageNum', 1)  # 默认为第1页
        page_size = 20
        total_rows = len(df)
        total_pages = (total_rows + page_size - 1) // page_size

        # 处理页码范围
        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages

        # 获取当前页数据
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_data = df.iloc[start_idx:end_idx]

        # 转换为字典格式
        rows = []
        for _, row in page_data.iterrows():
            row_dict = {}
            for header in headers:
                value = row[header]
                if pd.isna(value):
                    value = None
                row_dict[header] = value
            rows.append(row_dict)

        # 构建响应结构
        columns = [{"title": header, "dataIndex": header, "key": header} for header in headers]

        response = {
            "pageNum": page,
            "pageSize": page_size,
            "totalPages": total_pages,
            "totalCount": total_rows,
            "columns": columns,
            "dataSource": rows
        }

        return jsonify({
            "code": "00000",
            "message": "查询成功",
            "data": response
        })

    except FileNotFoundError:
        return jsonify({
            "code": 404,
            "message": "文件不存在或已被删除"
        }), 404
    except PermissionError:
        return jsonify({
            "code": 403,
            "message": "没有权限访问文件"
        }), 403
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"处理文件时出错: {str(e)}"
        }), 500


# 数据导入-传目录结构和文件
@auth_bp.route('/file-structure', methods=['GET'])
def get_file_structure():
    # 认证部分保持不变
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"code": 401, "message": "未提供认证token"}), 401

    try:
        # 提取并验证token
        token = auth_header.split(" ")[1] if auth_header.startswith('Bearer ') else auth_header
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']

        # 获取用户和根目录
        user = User.query.get(user_id)
        if not user:
            return jsonify({"code": 404, "message": "用户不存在"}), 404

        root_dir = user.get_root_directory()
        if not root_dir:
            return jsonify({"code": 404, "message": "根目录不存在"}), 404

        # 递归构建目录结构的函数
        def build_directory_structure(directory_id):
            """递归构建目录结构，包含子目录和文件"""
            children = []

            # 1. 处理子目录
            sub_dirs = Directory.query.filter_by(
                parent_id=directory_id,
                deleted_at=None
            ).all()

            for dir in sub_dirs:
                children.append({
                    "id": dir.id,
                    "title": dir.name,
                    "type": "directory",
                    "children": build_directory_structure(dir.id)  # 递归调用
                })

            # 2. 处理文件
            files = File.query.filter_by(
                directory_id=directory_id,
                deleted_at=None
            ).all()

            for file in files:
                children.append({
                    "id": file.id,
                    "title": file.name,
                    "type": file.type
                })

            return children

        # 构建完整的文件结构
        structure = {
            "id": root_dir.id,
            "title": root_dir.name,
            "type": "directory",
            "children": build_directory_structure(root_dir.id)
        }

        return jsonify({
            "code": "00000",
            "message": "获取成功",
            "data": [structure]  # 保持返回数组格式
        })

    except jwt.ExpiredSignatureError:
        return jsonify({"code": 401, "message": "token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"code": 401, "message": "无效的token"}), 401
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"}), 500


"""
read_file_ms：读取上传文件内容的耗时1.07 毫秒
calculate_hash_ms：计算文件哈希值的耗时1.59 毫秒
generate_path_ms：生成存储路径和文件名的耗时0.6 毫秒
write_file_ms：将文件写入磁盘的耗时2.91 毫秒
database_operation_ms：数据库记录创建和提交的耗时114.71 毫秒
"""


# 数据导入-增加目录或文件
@auth_bp.route('/create', methods=['POST'])
def create_item():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"code": 401, "message": "未提供认证token", "data": None}), 401

    try:
        # 提取token
        if auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
        else:
            token = auth_header

        # 验证并解码token
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']

        # 获取当前用户
        current_user = User.query.get(user_id)
        if not current_user:
            return jsonify({
                "code": 404,
                "message": "用户不存在",
                "data": None
            }), 404

        # 从请求中获取操作类型
        item_type = request.form.get('type')

        if not item_type:
            return jsonify({
                "code": 400,
                "message": "缺少类型参数(type)",
                "data": None
            }), 400

        item_type = item_type.lower()

        # 处理创建目录请求
        if item_type == 'directory':
            # 从表单获取目录数据
            data = {
                'name': request.form.get('name'),
                'parent_id': request.form.get('parent_id')
            }

            # 验证必要字段
            required_fields = ['name', 'parent_id']
            if not all(data.get(field) for field in required_fields):
                return jsonify({
                    "code": 400,
                    "message": "缺少必填字段",
                    "data": None
                }), 400

            # 验证父目录
            parent = Directory.query.get(data['parent_id'])
            if not parent:
                return jsonify({
                    "code": 404,
                    "message": "父目录不存在",
                    "data": None
                }), 404

            # 验证用户对父目录的权限
            if parent.user_id != current_user.id or parent.root_user_id != current_user.id:
                return jsonify({
                    "code": 403,
                    "message": "用户没有父目录的权限",
                    "data": None
                }), 403

            # 创建新目录
            new_directory = Directory(
                name=data['name'],
                user_id=current_user.id,
                root_user_id=current_user.id,
                root_id=parent.root_id,
                parent_id=parent.id
            )

            db.session.add(new_directory)
            db.session.commit()

            return jsonify({
                "code": "00000",
                "message": "目录创建成功",
                "data": serialize_directory(new_directory)["id"]
            }), 201

        # 处理上传文件请求
        elif item_type == 'file':
            # 验证文件是否存在
            if 'file' not in request.files:
                return jsonify({
                    "code": 400,
                    "message": "没有上传文件",
                    "data": None
                }), 400

            uploaded_file = request.files['file']
            if uploaded_file.filename == '':
                return jsonify({
                    "code": 400,
                    "message": "未选择文件",
                    "data": None
                }), 400

            # 获取目录ID
            directory_id = request.form.get('parent_id')

            # 验证必要参数
            if not directory_id:
                return jsonify({
                    "code": 400,
                    "message": "缺少目录ID",
                    "data": None
                }), 400

            # 验证目录
            directory = Directory.query.get(directory_id)
            if not directory:
                return jsonify({
                    "code": 404,
                    "message": "目录不存在",
                    "data": None
                }), 404

            # 验证用户对目录的权限
            if directory.user_id != current_user.id or directory.root_user_id != current_user.id:
                return jsonify({
                    "code": 403,
                    "message": "用户没有该目录的权限",
                    "data": None
                }), 403

            # 确定文件类型
            file_type = 'txt'
            if uploaded_file.filename.lower().endswith('.xlsx'):
                file_type = 'xlsx'
            elif uploaded_file.filename.lower().endswith('.txt'):
                file_type = 'txt'
            elif uploaded_file.filename.lower().endswith('.las'):
                file_type = 'las'

            try:
                # 读取文件内容
                file_content = uploaded_file.read()

                # 计算文件哈希和大小
                file_hash = calculate_sha256(file_content)
                file_size = len(file_content)

                # 生成文件保存路径
                base_dir = os.path.join(current_app.root_path, 'uploads', str(current_user.id))
                os.makedirs(base_dir, exist_ok=True)

                # 生成唯一文件名
                filename = uploaded_file.filename
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
                file_path = os.path.join(base_dir, unique_filename)

                # 保存文件到磁盘
                with open(file_path, 'wb', buffering=10*1024*1024) as f:  # 10MB缓冲区
                    f.write(file_content)

                # 创建新文件记录，content字段存储相对路径
                new_file = File(
                    name=uploaded_file.filename,
                    directory_id=directory.id,
                    root_id=directory.root_id,
                    user_id=current_user.id,
                    type=file_type,
                    content=to_relative_content_path(file_path),
                    size=file_size,
                    file_hash=file_hash
                )

                db.session.add(new_file)
                db.session.commit()

                return jsonify({
                    "code": "00000",
                    "message": "文件上传成功",
                    "key": serialize_file(new_file)["id"],
                }), 201

            except Exception as e:
                import traceback
                traceback.print_exc()
                return jsonify({
                    "code": 500,
                    "message": f"文件处理失败: {str(e)}",
                    "data": None
                }), 500

        else:
            return jsonify({
                "code": 400,
                "message": "无效的类型参数(必须是'directory'或'file')",
                "data": None
            }), 400

    except jwt.ExpiredSignatureError:
        return jsonify({"code": 401, "message": "token已过期", "data": None}), 401
    except jwt.InvalidTokenError:
        return jsonify({"code": 401, "message": "无效的token", "data": None}), 401
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "data": None
        }), 500


@auth_bp.route('/convert-all-to-xlsx', methods=['POST'])
def convert_all_to_xlsx():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"code": 401, "message": "未提供认证token", "data": None}), 401

    try:
        if auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
        else:
            token = auth_header

        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']

        current_user = User.query.get(user_id)
        if not current_user:
            return jsonify({"code": 404, "message": "用户不存在", "data": None}), 404

        all_files = File.query.filter(
            File.user_id == user_id,
            File.deleted_at.is_(None),
        ).all()

        converted = 0
        skipped = 0
        errors: list[str] = []

        for file_record in all_files:
            try:
                name = file_record.name or ""
                ext = os.path.splitext(name)[1].lower()
                file_type = str(getattr(file_record, "type", "") or "").lower()
                if ext not in (".txt", ".las") and file_type not in ("txt", "las"):
                    continue

                real_path = resolve_content_path(file_record.content)
                if not real_path or not os.path.exists(real_path):
                    skipped += 1
                    errors.append(f"{name}: 文件路径不存在({file_record.content})")
                    continue

                with open(real_path, 'rb') as f:
                    raw_bytes = f.read()

                df = _read_supported_file_to_df(file_record, raw_bytes)
                df.columns = [str(c).strip() for c in df.columns]
                df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]

                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                xlsx_bytes = output.getvalue()

                base_name = os.path.splitext(name)[0] or "未命名"
                new_name = _get_unique_xlsx_filename(
                    user_id=user_id,
                    directory_id=int(file_record.directory_id),
                    base_name=base_name,
                    exclude_file_id=int(file_record.id),
                )

                base_dir = os.path.join(current_app.root_path, 'uploads', str(current_user.id))
                os.makedirs(base_dir, exist_ok=True)

                safe_base = os.path.splitext(new_name)[0]
                unique_filename = f"{safe_base}_{uuid.uuid4().hex[:8]}.xlsx"
                new_path = os.path.join(base_dir, unique_filename)
                with open(new_path, 'wb') as f:
                    f.write(xlsx_bytes)

                old_real_path = resolve_content_path(file_record.content)
                file_record.name = new_name
                file_record.type = "xlsx"
                file_record.content = to_relative_content_path(new_path)
                file_record.size = len(xlsx_bytes)
                file_record.file_hash = calculate_sha256(xlsx_bytes)
                db.session.add(file_record)
                db.session.flush()

                try:
                    if old_real_path and os.path.exists(old_real_path):
                        os.remove(old_real_path)
                except Exception:
                    pass

                converted += 1

            except Exception as e:
                skipped += 1
                errors.append(f"{file_record.name or ''}: {str(e)}")

        db.session.commit()
        return jsonify({
            "code": "00000",
            "message": "转换完成",
            "data": {
                "converted": converted,
                "skipped": skipped,
                "errors": errors[:50],
            }
        })

    except jwt.ExpiredSignatureError:
        return jsonify({"code": 401, "message": "token已过期", "data": None}), 401
    except jwt.InvalidTokenError:
        return jsonify({"code": 401, "message": "无效的token", "data": None}), 401
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "data": None
        }), 500


@auth_bp.route('/rename', methods=['POST'])
def rename_item():
    try:
        # 验证用户
        user_id = get_user_id_from_token()
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                "code": 404,
                "message": "用户不存在",
                "data": None
            }), 404

        # 获取请求数据
        data = request.get_json()
        if not data or 'id' not in data or 'name' not in data or 'type' not in data:
            return jsonify({
                "code": 400,
                "message": "缺少必要参数(id、name或type)",
                "data": None
            }), 400

        item_id = data['id']
        new_name = data['name']
        item_type = data['type'].lower()  # 转换为小写

        # 根据类型选择相应的模型
        if item_type == 'directory':
            model = Directory
            item_name = "目录"
        elif item_type == 'file':
            model = File
            item_name = "文件"
        else:
            return jsonify({
                "code": 400,
                "message": "无效的类型参数(必须是'directory'或'file')",
                "data": None
            }), 400

        # 查询项目并验证
        item = model.query.filter_by(id=item_id).first()
        if not item:
            return jsonify({
                "code": 404,
                "message": f"{item_name}不存在",
                "data": None
            }), 404

        # 检查权限
        if item.user_id != user.id:
            return jsonify({
                "code": 403,
                "message": f"无权限重命名此{item_name}",
                "data": None
            }), 403

        # 执行重命名
        item.name = new_name
        db.session.commit()

        return jsonify({
            "code": "00000",
            "message": f"{item_name}重命名成功",
            "data": None
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "data": None
        }), 500


# 数据导入-删除目录或文件
@auth_bp.route('/delete', methods=['POST'])
def delete_item():
    # 从请求头获取token
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"code": 401, "message": "未提供认证token"}), 401

    try:
        # 提取token
        if auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
        else:
            token = auth_header

        # 验证并解码token
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']

        # 获取用户
        user = User.query.get(user_id)
        if not user:
            return jsonify({"code": 404, "message": "用户不存在"}), 404

        # 获取请求数据
        data = request.get_json()
        if not data or 'id' not in data or 'type' not in data:
            return jsonify({
                "code": 400,
                "message": "缺少必要参数(id和type)",
                "data": None
            }), 400

        item_id = data['id']
        item_type = data['type'].lower()  # 转换为小写

        # 根据类型处理删除
        if item_type == 'directory':
            directory = Directory.query.get(item_id)
            if not directory:
                return jsonify({
                    "code": 404,
                    "message": "目录不存在",
                    "data": None
                }), 404

            # 检查用户是否有权限删除该目录
            if directory.user_id != user.id:
                return jsonify({
                    "code": 403,
                    "message": "无权限删除此目录",
                    "data": None
                }), 403

            # 执行软删除
            directory.soft_delete()
            db.session.commit()

            return jsonify({
                "code": "00000",
                "message": "目录删除成功",
                "data": None
            })

        elif item_type == 'file':
            file = File.query.get(item_id)
            if not file:
                return jsonify({
                    "code": 404,
                    "message": "文件不存在",
                    "data": None
                }), 404

            # 检查用户是否有权限删除该文件
            if file.user_id != user.id:
                return jsonify({
                    "code": 403,
                    "message": "无权限删除此文件",
                    "data": None
                }), 403

            # 执行软删除
            file.soft_delete()
            db.session.commit()

            return jsonify({
                "code": "00000",
                "message": "文件删除成功",
                "data": None
            })

        else:
            return jsonify({
                "code": 400,
                "message": "无效的类型参数(必须是'directory'或'file')",
                "data": None
            }), 400

    except jwt.ExpiredSignatureError:
        return jsonify({"code": 401, "message": "token已过期", "data": None}), 401
    except jwt.InvalidTokenError:
        return jsonify({"code": 401, "message": "无效的token", "data": None}), 401
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "data": None
        }), 500
