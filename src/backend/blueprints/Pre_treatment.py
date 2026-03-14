from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timezone
import numpy as np
import hashlib
import jwt
from werkzeug.exceptions import Unauthorized
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.cluster import KMeans
from torch.utils.data import DataLoader, TensorDataset, random_split
import torch
import pickle
import gzip
from io import BytesIO, StringIO
import pandas as pd
from models import Directory, File, ModelConfig
from exts import db
import os
import uuid
import re
from models_lib.model_Autoformer import Autoformer_EncoderOnly
from models_lib.model_BiLSTM import BiLSTM
from models_lib.model_GRU import GRU
from models_lib.model_LSTM import LSTM, BPNetwork
from models_lib.model_TCN import TemporalConvNet
from models_lib.model_Trans_KAN import TimeSeriesTransformer_ekan
from models_lib.model_Transformer import TransformerModel
from tools.tool_for_pre import get_parameters
from utils_path import resolve_content_path, to_relative_content_path

# 创建蓝图
tre_bp = Blueprint('pretreatment', __name__)




def serialize_to_blob(obj):
    """将对象序列化为压缩的二进制数据"""
    buffer = BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode='wb') as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
    return buffer.getvalue()


def deserialize_from_blob(blob):
    """从二进制数据反序列化对象"""
    buffer = BytesIO(blob)
    with gzip.GzipFile(fileobj=buffer, mode='rb') as f:
        return pickle.load(f)


def get_user_id_from_token():
    """从请求头的JWT令牌中获取用户ID"""
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

        if 'exp' in payload and datetime.utcfromtimestamp(payload['exp']) < datetime.utcnow():
            raise Unauthorized('Token has expired')
        user_id = payload.get('user_id')
        if not user_id:
            raise Unauthorized('Invalid token payload')
        return user_id
    except jwt.InvalidTokenError:
        raise Unauthorized('Invalid token')


def calculate_sha256(data):
    """计算数据的SHA256哈希值"""
    return hashlib.sha256(data).hexdigest()


def get_model(args):
    """根据参数获取对应的模型实例"""
    model_name = getattr(args, "model_name", None)
    if model_name == 'GRU':
        return GRU(args)
    elif model_name == 'LSTM':
        return LSTM(args)
    elif model_name == 'BP':
        return BPNetwork(args)
    elif model_name == 'LSTM_my':
        return LSTM(args)
    elif model_name == 'BiLSTM':
        return BiLSTM(args)
    elif model_name == 'TCN':
        return TemporalConvNet(args)
    elif model_name == 'Transformer':
        return TransformerModel(args)
    elif model_name == 'Transformer_KAN':
        return TimeSeriesTransformer_ekan(args)
    elif model_name == 'TimeSeriesTransformer_ekan_large':
        return TimeSeriesTransformer_ekan(args)
    elif model_name in ('Autoformer', 'Autoformer_EncoderOnly'):
        return Autoformer_EncoderOnly(args)
    else:
        raise ValueError(f"未知模型名: {model_name}")


# ------------------------------------------------------------------------------
# 核心预处理函数
# ------------------------------------------------------------------------------
def create_time_series(data, target_column=None, sequence_length=None):
    """
    创建时序数据，支持多种场景：
    1. 带目标列的时序数据
    2. 不带目标列的时序数据
    3. 非时序数据
    返回: (X, y, feature_columns)
    """
    # 提取特征列名
    feature_columns = [c for c in data.columns if c != target_column] if target_column else list(data.columns)

    seq_len = None
    if sequence_length is not None and sequence_length != "":
        try:
            seq_len = int(sequence_length)
        except Exception:
            raise ValueError(f"sequence_length 参数无效: {sequence_length}")

    if target_column and (seq_len is None or seq_len <= 1):
        features = data[feature_columns].to_numpy()
        target = data[target_column].to_numpy()
        return features, np.array(target).reshape(-1, 1), feature_columns

    # 场景1: 带目标列的时序数据
    if target_column and seq_len:
        features = data[feature_columns].to_numpy()
        target = data[target_column].to_numpy()

        if len(features) <= seq_len:
            raise ValueError(
                f"数据长度({len(features)})不足以生成序列长度({seq_len})的样本，请减小序列长度或使用更长数据"
            )

        X, y = [], []
        for i in range(len(features) - seq_len):
            X.append(features[i:i + seq_len])
            y.append(target[i + seq_len])

        return np.array(X), np.array(y).reshape(-1, 1), feature_columns

    # 场景2: 不带目标列的时序数据
    elif seq_len and seq_len > 1:
        features = data.to_numpy()
        if len(features) < seq_len:
            raise ValueError(
                f"数据长度({len(features)})小于序列长度({seq_len})"
            )

        X = []
        for i in range(len(features) - seq_len + 1):
            X.append(features[i:i + seq_len])
        return np.array(X), None, feature_columns

    # 场景3: 非时序数据
    else:
        if target_column:
            features = data[feature_columns].to_numpy()
            target = data[target_column].to_numpy()
            return features, np.array(target).reshape(-1, 1), feature_columns
        return data.to_numpy(), None, feature_columns


def create_data_loaders(X, y=None, batch_size=32, val_ratio=0.2):
    """创建训练和验证数据加载器，支持无目标变量的情况"""
    # 转换为PyTorch张量
    X_tensor = torch.FloatTensor(X)

    # 创建数据集
    if y is not None:
        y_tensor = torch.FloatTensor(y)
        dataset = TensorDataset(X_tensor, y_tensor)
    else:
        dataset = TensorDataset(X_tensor)

    # 拆分训练集和验证集
    val_size = int(len(dataset) * val_ratio)
    train_size = len(dataset) - val_size
    train_set, val_set = random_split(dataset, [train_size, val_size])

    # 创建数据加载器
    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=batch_size)

    return train_loader, val_loader


def _decode_text_bytes(data: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "gb18030", "gbk", "latin-1"):
        try:
            return data.decode(enc)
        except Exception:
            continue
    return data.decode("utf-8", errors="ignore")


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    if "DEPTH" not in df.columns:
        for cand in ("DEPT", "Depth", "depth", "DEPT.", "DEPTH."):
            if cand in df.columns:
                df = df.rename(columns={cand: "DEPTH"})
                break
    return df


def _read_txt_bytes_to_df(data: bytes) -> pd.DataFrame:
    text = _decode_text_bytes(data)
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


def _read_supported_file_to_df(file_record: File) -> pd.DataFrame:
    file_path = resolve_content_path(file_record.content)
    if not file_path:
        raise FileNotFoundError(f"文件路径无法解析: {file_record.content}")
    with open(file_path, "rb") as f:
        file_content = f.read()

    ext = os.path.splitext(file_record.name or file_path)[1].lower()
    if file_record.type == "xlsx" or ext in (".xlsx", ".xls"):
        return pd.read_excel(BytesIO(file_content))
    if ext == ".las":
        return _read_las_bytes_to_df(file_content)
    return _read_txt_bytes_to_df(file_content)


def load_excel_files_with_index(directory_id, use_original=False):
    """
    读取目录下的Excel文件，支持读取原始文件或处理后的文件
    use_original=True: 读取原始文件
    use_original=False: 读取覆盖目录中的文件（处理后的文件）
    """
    print(f"开始从目录 {directory_id} 读取数据文件...")

    # 查询文件 - 区分原始文件和处理后的文件
    query = File.query.filter(
        File.directory_id == directory_id,
        File.deleted_at.is_(None),
        File.type.in_(["xlsx", "txt", "las"])
    )

    # 仅在读取原始文件时才过滤处理后的文件
    if use_original:
        # 排除文件名中包含处理后缀的文件（仅对原始目录有效）
        suffixes = [
            str(cfg.get("suffix"))
            for cfg in (PROCESS_OUTPUT_CONFIG or {}).values()
            if cfg and cfg.get("suffix")
        ]
        for suffix in suffixes:
            query = query.filter(~File.name.contains(f"-{suffix}"))
            query = query.filter(~File.name.contains(f"_{suffix}"))

    files = query.all()

    if not files:
        return None, None, None, "目录中没有符合条件的数据文件"

    total_files = len(files)
    data_frames = []
    file_row_info = {}
    current_start = 0
    file_mapping = {}  # 记录文件名到文件ID的映射，用于后续更新

    # 遍历处理每个文件
    for i, file in enumerate(files):
        progress = (i + 1) / total_files * 100
        print(f"正在处理文件: {file.name} (进度: {progress:.2f}%)")

        file_mapping[file.name] = file.id  # 记录文件名与ID的映射

        try:
            # 从文件路径读取内容（新模型中content存储的是路径）
            file_path = resolve_content_path(file.content)

            # 检查文件是否存在
            if not file_path or not os.path.exists(file_path):
                error_msg = f"文件 {file.name} 对应的物理文件不存在: {file_path}"
                print(error_msg)
                return None, None, None, error_msg

            df = _read_supported_file_to_df(file)
            df = _normalize_columns(df)
            df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]

            # 记录行范围信息
            row_count = len(df)
            current_end = current_start + row_count
            file_row_info[file.name] = (current_start, current_end)

            # 添加到数据框列表
            data_frames.append(df)
            current_start = current_end  # 更新起始行

        except Exception as e:
            error_msg = f"处理文件 {file.name} 失败: {str(e)}，路径: {file.content}"
            print(error_msg)
            return None, None, None, error_msg

    # 合并所有DataFrame
    if not data_frames:
        return None, None, None, "没有成功读取任何数据文件"

    df_all = pd.concat(data_frames, ignore_index=True)
    print(f"数据文件读取完成。共处理 {len(data_frames)} 个文件，总行数: {len(df_all)}")

    return df_all, file_row_info, file_mapping, ""


def Zscore(X_train_val, y_train_val, threshold=4.0, scaler_type="standard"):
    """Z-score异常样本剔除并返回归一化器"""
    print(f"开始Z-score异常样本剔除，threshold = {threshold}")

    # 1. 数据扁平化处理
    if len(X_train_val.shape) == 3:  # 时序数据
        B, T, F = X_train_val.shape
        X_flat = X_train_val.reshape(B, -1)  # [B, T*F]
    else:  # 非时序数据
        B, F = X_train_val.shape
        X_flat = X_train_val

    y_flat = y_train_val.reshape(B, 1)  # [B, 1]
    data_all = np.concatenate([X_flat, y_flat], axis=1)  # [B, T*F + 1]

    # 2. 计算Z-score
    mean = np.mean(data_all, axis=0)
    std = np.std(data_all, axis=0) + 1e-8  # 避免除零
    z_scores = np.abs((data_all - mean) / std)

    # 3. 过滤异常样本
    keep_mask = np.all(z_scores <= threshold, axis=1)
    X_filtered = X_train_val[keep_mask]
    y_filtered = y_train_val[keep_mask]

    # 4. 创建归一化器
    if scaler_type == "standard":
        scaler_X = StandardScaler().fit(X_flat[keep_mask])
        scaler_y = StandardScaler().fit(y_flat[keep_mask])
    elif scaler_type == "minmax":
        scaler_X = MinMaxScaler().fit(X_flat[keep_mask])
        scaler_y = MinMaxScaler().fit(y_flat[keep_mask])
    else:
        raise ValueError(f"不支持的归一化类型: {scaler_type}")

    print(f"Z-score 剔除完成，原样本数: {B} → 保留: {X_filtered.shape[0]}")
    return X_filtered, y_filtered.reshape(-1, 1), scaler_X, scaler_y


def get_or_create_cover_directory(parent_dir_id, user_id):
    parent_dir = Directory.query.get(parent_dir_id)
    if not parent_dir:
        raise ValueError(f"父目录 {parent_dir_id} 不存在")

    root_dir = Directory.query.get(parent_dir.root_id)
    if not root_dir:
        raise ValueError(f"根目录 {parent_dir.root_id} 不存在")

    cover_dir = Directory.query.filter(
        Directory.name == '预处理结果',
        Directory.parent_id == root_dir.id,
        Directory.user_id == user_id,
        Directory.deleted_at.is_(None),
    ).first()

    if not cover_dir:
        cover_dir = Directory(
            name='预处理结果',
            user_id=user_id,
            root_user_id=user_id,
            root_id=root_dir.id,
            parent_id=root_dir.id
        )
        db.session.add(cover_dir)
        db.session.flush()
        db.session.commit()

    cover_dir_check = Directory.query.get(cover_dir.id)
    if not cover_dir_check:
        raise ValueError(f"创建或获取覆盖目录失败，目录ID: {cover_dir.id}")

    return cover_dir.id


PROCESS_OUTPUT_CONFIG = {
    "zscore": {"dir_name": "去噪结果", "suffix": "去噪处理"},
    "basic_normalization": {"dir_name": "标准化结果", "suffix": "标准化处理"},
    "岩性分类": {"dir_name": "岩性区分结果", "suffix": "岩性区分处理"},
    "casing_bolt_removal": {"dir_name": "消除套管栓结果", "suffix": "消除套管栓处理"},
}


def _get_process_suffix(process_type: str) -> str:
    cfg = PROCESS_OUTPUT_CONFIG.get(process_type)
    if cfg and cfg.get("suffix"):
        return str(cfg["suffix"])
    return f"{process_type}处理"


def get_or_create_process_subdir(preprocess_root_id: int, user_id: int, process_type: str) -> int:
    cfg = PROCESS_OUTPUT_CONFIG.get(process_type) or {}
    dir_name = str(cfg.get("dir_name") or f"{process_type}结果")

    existing = Directory.query.filter(
        Directory.parent_id == preprocess_root_id,
        Directory.user_id == user_id,
        Directory.name == dir_name,
        Directory.deleted_at.is_(None),
    ).first()
    if existing:
        return existing.id

    parent = Directory.query.get(preprocess_root_id)
    if not parent:
        raise ValueError("预处理结果目录不存在")

    new_dir = Directory(
        name=dir_name,
        parent_id=preprocess_root_id,
        root_id=parent.root_id,
        user_id=user_id,
        root_user_id=parent.root_user_id,
    )
    db.session.add(new_dir)
    db.session.commit()
    return new_dir.id


def load_single_file_with_index(file_id):
    file_record = File.query.filter(
        File.id == file_id,
        File.deleted_at.is_(None),
    ).first()

    if not file_record:
        return None, None, None, "文件不存在或已删除"

    try:
        real_path = resolve_content_path(file_record.content)
        if not file_record.content or not real_path or not os.path.exists(real_path):
            return None, None, None, f"文件物理路径不存在: {file_record.content}"

        df = _read_supported_file_to_df(file_record)
        df = _normalize_columns(df)
        df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]

        row_count = len(df)
        file_row_info = {file_record.name: (0, row_count)}
        file_mapping = {file_record.name: file_record.id}

        return df, file_row_info, file_mapping, ""
    except Exception as e:
        return None, None, None, f"处理文件 {file_record.name} 失败: {str(e)}，路径: {file_record.content}"


# def save_processed_files(df_processed, file_row_info, file_mapping,
#                          cover_dir_id, user_id, process_type):
#     """
#     保存处理后的文件到覆盖目录，覆盖原有文件内容
#     保证覆盖目录中文件数量与原始文件一致
#     """
#     returned_file_ids = {}  # 记录每个原始文件对应的处理后文件ID
#     total_files = len(file_row_info)
#     saved_files = 0
#
#     # 验证覆盖目录是否存在
#     cover_dir = Directory.query.get(cover_dir_id)
#     if not cover_dir:
#         raise ValueError(f"覆盖目录 {cover_dir_id} 不存在，无法保存文件")
#
#     # 定义基础存储目录（与File模型的保存路径保持一致）
#     base_dir = os.path.join(current_app.root_path, 'uploads', str(user_id), f"process_{process_type}")
#     os.makedirs(base_dir, exist_ok=True)
#
#     # 保存到覆盖目录
#     for filename, (start, end) in file_row_info.items():
#         # 确保不会超出范围
#         end = min(end, len(df_processed))
#
#         # 即使没有有效数据也创建空文件，保证文件数量一致
#         if start >= end:
#             print(f"⚠️ 文件 {filename} 没有有效数据，创建空文件")
#             df_part = pd.DataFrame()  # 创建空DataFrame
#         else:
#             df_part = df_processed.iloc[start:end]
#
#         try:
#             # 将DataFrame转换为Excel二进制数据
#             output = BytesIO()
#             with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#                 df_part.to_excel(writer, index=False, sheet_name='Sheet1')
#             file_content = output.getvalue()  # 二进制内容
#
#             # 计算文件哈希和大小
#             file_hash = calculate_sha256(file_content)
#             file_size = len(file_content)
#
#             # 生成唯一文件名（保留原始文件名前缀，添加处理类型和UUID）
#             name, ext = os.path.splitext(filename)
#             unique_filename = f"{name}_{process_type}_{uuid.uuid4().hex[:8]}{ext}"
#             file_path = os.path.join(base_dir, unique_filename)
#
#             # 保存文件到磁盘
#             with open(file_path, 'wb') as f:
#                 f.write(file_content)
#
#             # 检查覆盖目录中是否已有同名文件（按名称匹配）
#             existing_file = File.query.filter_by(
#                 directory_id=cover_dir_id,
#                 name=filename,
#                 user_id=user_id,
#                 deleted_at=None
#             ).first()
#
#             if existing_file:
#                 # 若存在旧文件，先删除磁盘上的旧文件（可选）
#                 if os.path.exists(existing_file.content):
#                     os.remove(existing_file.content)
#
#                 # 更新数据库记录（路径、大小、哈希、时间）
#                 existing_file.content = file_path
#                 existing_file.size = file_size
#                 existing_file.file_hash = file_hash
#                 existing_file.updated_at = datetime.now(timezone.utc)
#                 returned_file_ids[filename] = existing_file.id
#                 saved_files += 1
#                 print(f"✓ 更新文件: {filename} (ID: {existing_file.id})，路径: {file_path}")
#             else:
#                 # 创建新文件记录（保存路径而非二进制内容）
#                 cover_file = File(
#                     name=filename,
#                     directory_id=cover_dir_id,
#                     root_id=cover_dir.root_id,
#                     user_id=user_id,
#                     type='xlsx',
#                     content=file_path,  # 存储文件路径
#                     size=file_size,
#                     file_hash=file_hash
#                 )
#                 db.session.add(cover_file)
#                 db.session.flush()  # 立即获取ID
#                 returned_file_ids[filename] = cover_file.id
#                 saved_files += 1
#                 print(f"✓ 创建文件: {filename} (ID: {cover_file.id})，路径: {file_path}")
#
#         except Exception as e:
#             print(f"❌ 处理文件 {filename} 失败: {str(e)}")
#             # 即使出错也尝试创建空文件，确保文件结构完整
#             try:
#                 # 创建空文件到磁盘
#                 name, ext = os.path.splitext(filename)
#                 empty_filename = f"{name}_empty_{uuid.uuid4().hex[:8]}{ext}"
#                 empty_file_path = os.path.join(base_dir, empty_filename)
#                 with open(empty_file_path, 'wb') as f:
#                     f.write(b'')  # 空内容
#
#                 # 创建数据库记录
#                 cover_file = File(
#                     name=filename,
#                     directory_id=cover_dir_id,
#                     root_id=cover_dir.root_id,
#                     user_id=user_id,
#                     type='xlsx',
#                     content=empty_file_path,  # 空文件路径
#                     size=0,
#                     file_hash=calculate_sha256(b'')
#                 )
#                 db.session.add(cover_file)
#                 db.session.flush()
#                 returned_file_ids[filename] = cover_file.id
#                 saved_files += 1
#                 print(f"⚠️ 为 {filename} 创建了空文件以保持结构，路径: {empty_file_path}")
#             except Exception as e2:
#                 print(f"❌ 即使创建空文件也失败: {str(e2)}")
#                 pass
#
#     db.session.commit()
#     print(f"📊 保存完成：原始文件 {total_files} 个，成功保存 {saved_files} 个到覆盖目录 (ID: {cover_dir_id})")
#
#     # 验证是否所有文件都被保存
#     if len(returned_file_ids) != total_files:
#         missing = total_files - len(returned_file_ids)
#         print(f"⚠️ 警告：有 {missing} 个文件未能保存到覆盖目录")
#
#     # 验证保存的文件是否真的存在（数据库+磁盘）
#     for filename, file_id in returned_file_ids.items():
#         saved_file = File.query.get(file_id)
#         if not saved_file:
#             print(f"❌ 验证失败：文件 {filename} (ID: {file_id}) 未实际保存到数据库")
#         elif not os.path.exists(saved_file.content):
#             print(f"❌ 验证失败：文件 {filename} (ID: {file_id}) 数据库记录存在，但磁盘文件不存在: {saved_file.content}")
#
#     return returned_file_ids

def save_processed_files(df_processed, file_row_info, file_mapping,
                         cover_dir_id, user_id, process_type):
    """
    保存处理后的文件到指定目录，不删除源文件；同名则覆盖更新内容
    """
    returned_file_ids = {}

    cover_dir = Directory.query.get(cover_dir_id)
    if not cover_dir:
        raise ValueError(f"覆盖目录 {cover_dir_id} 不存在，无法保存文件")

    base_dir = os.path.join(current_app.root_path, 'uploads', str(user_id), "preprocess", str(cover_dir_id))
    os.makedirs(base_dir, exist_ok=True)

    for filename, (start, end) in file_row_info.items():
        end = min(end, len(df_processed))
        if start >= end:
            df_part = pd.DataFrame()
        else:
            df_part = df_processed.iloc[start:end]

        try:
            source_file_id = None
            try:
                source_file_id = file_mapping.get(filename) if isinstance(file_mapping, dict) else None
            except Exception:
                source_file_id = None

            source_file = File.query.get(source_file_id) if source_file_id else None
            source_ext = os.path.splitext((source_file.name if source_file else filename) or "")[1].lower()
            source_base = os.path.splitext((source_file.name if source_file else filename) or "")[0]
            suffix = _get_process_suffix(str(process_type))
            suffix_token = f"-{suffix}"
            if source_base.endswith(suffix_token):
                out_base = source_base
            else:
                out_base = f"{source_base}{suffix_token}"

            if source_ext in (".xlsx", ".xls") or (source_file and source_file.type == "xlsx"):
                out_ext = ".xlsx"
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_part.to_excel(writer, index=False, sheet_name='Sheet1')
                file_content = output.getvalue()
                out_type = "xlsx"
            else:
                if source_ext == ".las":
                    out_ext = ".txt"
                else:
                    out_ext = source_ext if source_ext else ".txt"
                text = df_part.to_csv(index=False, sep="\t")
                file_content = text.encode("utf-8-sig")
                out_type = "txt"

            out_name = f"{out_base}{out_ext}"
            unique_filename = f"{out_base}_{uuid.uuid4().hex[:8]}{out_ext}"
            file_path = os.path.join(base_dir, unique_filename)

            with open(file_path, 'wb') as f:
                f.write(file_content)

            existing = File.query.filter(
                File.directory_id == cover_dir_id,
                File.user_id == user_id,
                File.deleted_at.is_(None),
                File.name == out_name,
            ).first()

            if existing:
                try:
                    old_real = resolve_content_path(existing.content)
                    if old_real and os.path.exists(old_real):
                        os.remove(old_real)
                except Exception:
                    pass
                existing.content = to_relative_content_path(file_path)
                existing.size = len(file_content)
                existing.file_hash = calculate_sha256(file_content)
                existing.type = out_type
                db.session.add(existing)
                db.session.flush()
                returned_file_ids[filename] = existing.id
            else:
                cover_file = File(
                    name=out_name,
                    directory_id=cover_dir_id,
                    root_id=cover_dir.root_id,
                    user_id=user_id,
                    type=out_type,
                    content=to_relative_content_path(file_path),
                    size=len(file_content),
                    file_hash=calculate_sha256(file_content),
                )
                db.session.add(cover_file)
                db.session.flush()
                returned_file_ids[filename] = cover_file.id

        except Exception as e:
            print(f"❌ 处理文件 {filename} 失败: {str(e)}")

    db.session.commit()
    return returned_file_ids



def get_processed_file_data(file_id):
    """获取处理后的文件数据并构建返回结构，将特征分为两组"""
    file_record = File.query.get(file_id)
    if not file_record:
        return {
            "code": 404,
            "data": None,
            "message": f"文件 {file_id} 不存在"
        }

    try:
        # 获取文件路径
        file_path = resolve_content_path(file_record.content)

        # 检查文件是否存在
        if not file_path or not os.path.exists(file_path):
            return {
                "code": 404,
                "data": None,
                "message": f"文件 {file_id} 对应的物理文件不存在"
            }

        if file_record.type not in ("xlsx", "txt", "las"):
            return {
                "code": 400,
                "data": None,
                "message": f"不支持的文件类型: {file_record.type}"
            }

        df = _read_supported_file_to_df(file_record)
        df = _normalize_columns(df)
        df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]

        # 检查是否有DEPTH列
        if 'DEPTH' not in df.columns:
            return {
                "code": 400,
                "data": None,
                "message": "数据文件缺少DEPTH列"
            }

        depth_series = pd.to_numeric(df['DEPTH'], errors='coerce')

        # 收集所有特征列（排除DEPTH列）
        feature_columns = [col for col in df.columns if col != 'DEPTH']
        if "cluster_label" in feature_columns:
            feature_columns.remove("cluster_label")
            feature_columns.insert(0, "cluster_label")

        # 将特征列平均分为两组
        mid_index = (len(feature_columns) + 1) // 2  # 确保分组均衡
        group1_columns = feature_columns[:mid_index]
        group2_columns = feature_columns[mid_index:]

        # 构建返回数据结构
        result = {
            "options": {
                "character1": [str(col) for col in group1_columns],
                "character2": [str(col) for col in group2_columns]
            },
            "axisData": {},
            "axisData2": {}
        }

        for col in group1_columns:
            feature_series = pd.to_numeric(df[col], errors='coerce')
            valid = pd.concat([feature_series, depth_series], axis=1).dropna()
            points = valid.to_numpy(dtype=float).tolist() if not valid.empty else []
            result["axisData"][str(col)] = points

        for col in group2_columns:
            feature_series = pd.to_numeric(df[col], errors='coerce')
            valid = pd.concat([feature_series, depth_series], axis=1).dropna()
            points = valid.to_numpy(dtype=float).tolist() if not valid.empty else []
            result["axisData2"][str(col)] = points

        return result

    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "message": f"处理文件时发生错误: {str(e)}"
        }


# 第一个预处理算法：Z-score异常样本剔除
def zscore_process(args, user_id, input_file_id, output_dir_id):
    data_train_val, file_row_info, file_mapping, error = load_single_file_with_index(input_file_id)
    if error or data_train_val is None:
        raise ValueError(f"数据读取失败: {error}")

    # 2. 获取必要参数
    target_column = args.predict_target
    sequence_length = args.sequence_length
    batch_size = args.batch_size
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(args.threshold)

    # 验证必要参数
    if not target_column:
        raise ValueError("Z-score处理需要指定predict_target")

    if "DEPTH" not in data_train_val.columns:
        raise ValueError("数据文件缺少DEPTH列")
    if target_column not in data_train_val.columns:
        raise ValueError(f"预测目标列不存在: {target_column}")

    df_numeric = data_train_val.copy()
    df_numeric = df_numeric.replace([np.inf, -np.inf], np.nan)
    for col in df_numeric.columns:
        df_numeric[col] = pd.to_numeric(df_numeric[col], errors="coerce")

    if df_numeric["DEPTH"].isna().all():
        raise ValueError("DEPTH列无法转换为数值")
    if df_numeric[target_column].isna().all():
        raise ValueError(f"预测目标列无法转换为数值: {target_column}")

    feature_cols = [c for c in df_numeric.columns if c != target_column]
    feature_df = df_numeric[feature_cols]
    medians = feature_df.median(numeric_only=True)
    df_numeric[feature_cols] = feature_df.fillna(medians).fillna(0)
    df_numeric[target_column] = df_numeric[target_column].fillna(df_numeric[target_column].median()).fillna(0)

    # 3. 时序转换
    X_train_val, y_train_val, _ = create_time_series(df_numeric, target_column, sequence_length)

    # 4. Zscore处理（返回归一化器）
    X_normalized, y_normalized, scaler_X, scaler_y = Zscore(
        X_train_val, y_train_val,
        threshold=args.threshold,
        scaler_type=args.scaler_type
    )

    # 5. 准备保存归一化后的数据
    if len(X_normalized.shape) == 3:
        X_last_step = X_normalized[:, -1, :]
    else:
        X_last_step = X_normalized

    feature_columns = df_numeric.columns.drop(target_column)
    df_normalized = pd.DataFrame(X_last_step, columns=feature_columns)
    df_normalized[target_column] = y_normalized.flatten()

    # 6. 保存处理后的文件到覆盖目录（覆盖原有内容）
    returned_file_ids = save_processed_files(df_normalized, file_row_info, file_mapping, output_dir_id, user_id, "zscore")

    if not returned_file_ids:
        raise ValueError("未找到与原始文件对应的处理结果文件")

    # 7. 生成并保存DataLoader
    train_loader, val_loader = create_data_loaders(X_normalized, y_normalized, batch_size)

    # 8. 序列化并保存到ModelConfig
    try:
        # 获取或创建配置
        config = ModelConfig.query.filter_by(user_id=user_id).first()
        if not config:
            config = ModelConfig(user_id=user_id)
            db.session.add(config)
        config.dad_id = output_dir_id
        # 保存预处理阶段的归一化器（在原始数据上拟合，用于测试时反归一化）
        config.save_pkl("x", scaler_X)
        config.save_pkl("y", scaler_y)
        db.session.commit()
        print("✅ Z-score预处理结果及归一化器已保存到模型配置")

    except Exception as e:
        db.session.rollback()
        print(f"❌ 保存Z-score预处理结果失败: {str(e)}")
        raise

    # 9. 获取返回数据（使用原始文件对应的处理后文件ID）
    original_file = File.query.get(input_file_id)
    result_file_id = returned_file_ids.get(original_file.name) if original_file else None
    if not result_file_id:
        result_data = {"message": "未找到对应的处理结果文件"}
    else:
        result_data = get_processed_file_data(result_file_id)

    print("Z-score数据处理流程完成")
    return {
        "process_type": "zscore",
        "message": "Z-score预处理成功",
        "data": result_data,
        "file_ids": returned_file_ids  # 返回所有处理后的文件ID
    }


# 第二个预处理算法：带聚类的归一化处理（岩性分类）
def normalization_with_clustering(args, user_id, input_file_id, output_dir_id):
    """带聚类的归一化处理流程（需要predict_target）"""
    print(f"args包含的属性: {dir(args)}")
    print(f"args.predict_target: {args.predict_target}")
    print(f"args.sequence_length: {args.sequence_length}")
    print(f"args.batch_size: {args.batch_size}")
    print(f"args.scaler_type: {args.scaler_type}")

    target_column = args.predict_target
    batch_size = args.batch_size

    if not target_column:
        raise ValueError("带聚类的归一化处理需要指定predict_target")

    data_train_val, file_row_info, file_mapping, error = load_single_file_with_index(input_file_id)
    if error or data_train_val is None:
        raise ValueError(f"数据读取失败: {error}")

    if "DEPTH" not in data_train_val.columns:
        raise ValueError("数据文件缺少DEPTH列")
    if target_column not in data_train_val.columns:
        raise ValueError(f"预测目标列不存在: {target_column}")

    feature_df = data_train_val.drop(columns=["DEPTH", target_column])
    if feature_df.shape[1] == 0:
        raise ValueError("可用于聚类的特征列为空")

    feature_df = feature_df.apply(pd.to_numeric, errors="coerce")
    medians = feature_df.median(numeric_only=True)
    feature_df = feature_df.fillna(medians).fillna(0)

    print(f"正在进行聚类前归一化，使用归一化器: {args.scaler_type}")
    if args.scaler_type == "minmax":
        scaler_X = MinMaxScaler()
    elif args.scaler_type == "standard":
        scaler_X = StandardScaler()
    elif args.scaler_type == "robust":
        scaler_X = RobustScaler()
    else:
        raise ValueError(f"不支持的归一化器类型: {args.scaler_type}")

    X_scaled = scaler_X.fit_transform(feature_df.to_numpy(dtype=float))

    print("开始KMeans无监督聚类（最多5类）...")
    n_samples = int(X_scaled.shape[0])
    if n_samples < 2:
        raise ValueError("样本量过小，无法进行聚类")
    n_clusters = min(5, n_samples)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)

    df_normalized = data_train_val.copy()
    df_normalized["cluster_label"] = cluster_labels.astype(int)

    returned_file_ids = save_processed_files(df_normalized, file_row_info, file_mapping, output_dir_id, user_id, "岩性分类")

    if not returned_file_ids:
        raise ValueError("未找到与原始文件对应的处理结果文件")

    try:
        config = ModelConfig.query.filter_by(user_id=user_id).first()
        if not config:
            config = ModelConfig(user_id=user_id)
            db.session.add(config)

        config.dad_id = output_dir_id

        db.session.commit()
        print("✅ 岩性分类预处理结果已保存到模型配置")

    except Exception as e:
        db.session.rollback()
        print(f"❌ 保存岩性分类预处理结果失败: {str(e)}")
        raise

    original_file = File.query.get(input_file_id)
    result_file_id = returned_file_ids.get(original_file.name) if original_file else None
    if not result_file_id:
        result_data = {"message": "未找到对应的处理结果文件"}
    else:
        result_data = get_processed_file_data(result_file_id)

    print("带聚类的归一化处理流程完成")
    return {
        "process_type": "岩性分类",
        "message": "岩性分类处理成功",
        "data": result_data,
        "file_ids": returned_file_ids  # 返回所有处理后的文件ID
    }



import numpy as np
import pandas as pd

def make_depth_denorm_unique(df_normalized: pd.DataFrame,
                             scaler_X,
                             feature_columns,
                             depth_col: str = None,
                             depth_round: int | None = None) -> pd.DataFrame:
    """
    只对第一列“深度”做反归一化，其他列保持归一化；然后按深度聚合(均值)，使深度唯一。

    参数
    ----
    df_normalized : 归一化后的二维DataFrame（你当前生成的 df_normalized）
    scaler_X      : 已fit的特征归一化器（MinMax/Standard/Robust），用于 inverse_transform
    feature_columns : 参与 scaler_X 拟合的一组特征列名（顺序需与拟合时一致）
    depth_col     : 深度列名；默认取 df_normalized.columns[0]
    depth_round   : 可选，对反归一化后的深度做 round(depth_round) 再分组，避免浮点误差导致的“近似重复深度无法合并”

    返回
    ----
    DataFrame：第一列深度为反归一化后的真实深度；其余列仍是归一化值；深度唯一（按均值聚合）。
    """

    if depth_col is None:
        depth_col = df_normalized.columns[0]

    # --- 1) 仅反归一化深度列 ---
    # 需要把当前二维表在 feature_columns 维度上进行 inverse_transform，然后只取对应深度列的反归一化结果
    # 注意：要求 feature_columns 的顺序与 scaler_X 拟合时一致，并且包含 depth_col
    if depth_col not in feature_columns:
        raise ValueError(f"depth_col='{depth_col}' 不在 feature_columns 中，无法仅反归一化深度列。")

    X_norm = df_normalized[feature_columns].to_numpy(dtype=np.float64)
    try:
        X_inv = scaler_X.inverse_transform(X_norm)  # 反归一化所有特征（不写回，只取深度列）
    except Exception as e:
        raise ValueError(f"对特征做 inverse_transform 失败：{e}")

    depth_idx = feature_columns.index(depth_col)
    depth_real = X_inv[:, depth_idx]

    # 写回第一列深度（保持其他列仍为归一化）
    out = df_normalized.copy()
    out[depth_col] = depth_real

    return out



# 第三个预处理算法：基础归一化处理
def basic_normalization_process(args, user_id, input_file_id, output_dir_id):
    """基础归一化处理流程（需要predict_target）"""
    data_train_val, file_row_info, file_mapping, error = load_single_file_with_index(input_file_id)
    if error or data_train_val is None:
        raise ValueError(f"数据读取失败: {error}")

    # 2. 获取必要参数
    target_column = args.predict_target
    sequence_length = args.sequence_length
    batch_size = args.batch_size

    # 验证必要参数
    if not target_column:
        raise ValueError("基础归一化处理需要指定predict_target")

    if "DEPTH" not in data_train_val.columns:
        raise ValueError("数据文件缺少DEPTH列")
    if target_column not in data_train_val.columns:
        raise ValueError(f"预测目标列不存在: {target_column}")

    df_numeric = data_train_val.copy()
    df_numeric = df_numeric.replace([np.inf, -np.inf], np.nan)
    for col in df_numeric.columns:
        df_numeric[col] = pd.to_numeric(df_numeric[col], errors="coerce")

    if df_numeric["DEPTH"].isna().all():
        raise ValueError("DEPTH列无法转换为数值")
    if df_numeric[target_column].isna().all():
        raise ValueError(f"预测目标列无法转换为数值: {target_column}")

    feature_cols = [c for c in df_numeric.columns if c != target_column]
    feature_df = df_numeric[feature_cols]
    medians = feature_df.median(numeric_only=True)
    df_numeric[feature_cols] = feature_df.fillna(medians).fillna(0)
    df_numeric[target_column] = df_numeric[target_column].fillna(df_numeric[target_column].median()).fillna(0)

    seq_len = getattr(args, "sequence_length", None)
    try:
        seq_len_int = int(seq_len) if seq_len is not None and seq_len != "" else None
    except Exception:
        seq_len_int = None

    if seq_len_int is not None and seq_len_int > 1 and len(df_numeric) <= seq_len_int:
        seq_len_int = None

    # 3. 将数据转换为时序数据（长度不足则自动退化为非时序标准化）
    X_train_val, y_train_val, _ = create_time_series(df_numeric, target_column, seq_len_int)

    # 4. 归一化处理
    print(f"正在进行归一化，使用归一化器: {args.scaler_type}")

    # 处理不同维度的数据
    if len(X_train_val.shape) == 3:  # 时序数据
        X_flat = X_train_val.reshape(-1, X_train_val.shape[-1])
        original_shape = X_train_val.shape
    else:  # 非时序数据
        X_flat = X_train_val
        original_shape = X_train_val.shape

    # 选择归一化器类型
    if args.scaler_type == "minmax":
        scaler_X = MinMaxScaler()
        scaler_y = MinMaxScaler()
    elif args.scaler_type == "standard":
        scaler_X = StandardScaler()
        scaler_y = StandardScaler()
    elif args.scaler_type == "robust":
        scaler_X = RobustScaler()
        scaler_y = RobustScaler()
    else:
        raise ValueError(f"不支持的归一化器类型: {args.scaler_type}")

    # 拟合并转换
    X_normalized_flat = scaler_X.fit_transform(X_flat)

    # 恢复原始形状
    if len(original_shape) == 3:
        X_normalized = X_normalized_flat.reshape(original_shape)
    else:
        X_normalized = X_normalized_flat

    y_normalized = scaler_y.fit_transform(y_train_val.reshape(-1, 1))

    # 5. 恢复 DataFrame 格式
    if len(X_normalized.shape) == 3:  # 时序数据
        X_last_step = X_normalized[:, -1, :]
    else:  # 非时序数据
        X_last_step = X_normalized

    feature_columns = df_numeric.columns.drop(target_column)
    df_normalized = pd.DataFrame(X_last_step, columns=feature_columns)
    df_normalized[target_column] = y_normalized.flatten()

    df_normalized = make_depth_denorm_unique(
        df_normalized=df_normalized,
        scaler_X=scaler_X,  # 刚刚拟合的特征归一化器
        feature_columns=list(feature_columns),
        depth_col="DEPTH" if "DEPTH" in df_normalized.columns else df_normalized.columns[0],
        depth_round=3  # 可选：比如保留到毫米级，避免浮点误差聚合失败
    )
    # 6. 保存处理后的文件到覆盖目录（覆盖原有内容）
    returned_file_ids = save_processed_files(df_normalized, file_row_info, file_mapping, output_dir_id, user_id, "basic_normalization")

    if not returned_file_ids:
        raise ValueError("未找到与原始文件对应的处理结果文件")

    # 7. 生成并保存DataLoader
    train_loader, val_loader = create_data_loaders(X_normalized, y_normalized, batch_size)

    # 8. 保存到ModelConfig（使用新的文件路径存储方式）
    try:
        # 获取或创建配置
        config = ModelConfig.query.filter_by(user_id=user_id).first()
        if not config:
            config = ModelConfig(user_id=user_id)
            db.session.add(config)

        # 保存pkl文件并记录路径（替代原来的二进制存储）
        # 会自动将文件路径写入对应的字段（trainloaderpkl, valloaderpkl, xpkl, ypkl）
        config.save_pkl('trainloader', train_loader)
        config.save_pkl('valloader', val_loader)
        config.save_pkl('x', scaler_X)
        config.save_pkl('y', scaler_y)

        # 更新其他配置
        config.dad_id = output_dir_id

        db.session.commit()
        print("✅ 基础归一化预处理结果已保存到模型配置")

    except Exception as e:
        db.session.rollback()
        print(f"❌ 保存基础归一化预处理结果失败: {str(e)}")
        raise

    # 9. 获取返回数据
    original_file = File.query.get(input_file_id)
    result_file_id = returned_file_ids.get(original_file.name) if original_file else None
    print(f"最终传入JSON函数的ID: {result_file_id}")  # 重点查看这个值
    if not result_file_id:
        result_data = {"message": "未找到对应的处理结果文件"}
    else:
        result_data = get_processed_file_data(result_file_id)


    print("基础归一化处理流程完成")
    return {
        "process_type": "basic_normalization",
        "message": "基础归一化处理成功",
        "data": result_data,
        "file_ids": returned_file_ids  # 返回所有处理后的文件ID
    }


# 第四个预处理算法：消除套管栓处理
def casing_bolt_removal_process(args, user_id, input_file_id, output_dir_id):
    """消除套管栓处理流程（不需要predict_target）"""
    data_train_val, file_row_info, file_mapping, error = load_single_file_with_index(input_file_id)
    if error or data_train_val is None:
        raise ValueError(f"数据读取失败: {error}")

    if "DEPTH" not in data_train_val.columns:
        raise ValueError("数据文件缺少DEPTH列")

    window = int(getattr(args, "window", 21) or 21)
    if window < 3:
        window = 3
    if window % 2 == 0:
        window += 1
    n_sigmas = float(getattr(args, "n_sigmas", 3.0) or 3.0)
    if n_sigmas <= 0:
        n_sigmas = 3.0

    def _despike_series(x: pd.Series) -> pd.Series:
        s = pd.to_numeric(x, errors="coerce")
        med = s.rolling(window=window, center=True, min_periods=1).median()
        diff = (s - med).abs()
        mad = diff.rolling(window=window, center=True, min_periods=1).median()
        iqr = (s.rolling(window=window, center=True, min_periods=1).quantile(0.75)
               - s.rolling(window=window, center=True, min_periods=1).quantile(0.25))
        global_scale = float(np.nanmax([np.nanmedian(iqr), np.nanpercentile(s, 75) - np.nanpercentile(s, 25),
                                        np.nanmax(s) - np.nanmin(s), 0.0]))
        eps = global_scale * 0.01 if global_scale > 0 else 1e-8
        thresh = 1.4826 * (mad.where(mad > 0, eps)) * n_sigmas
        mask = diff > thresh
        out = s.copy()
        out[mask] = med[mask]
        return out

    print(f"正在进行消除套管栓噪声处理，window={window}, n_sigmas={n_sigmas}")
    df_processed = data_train_val.copy()
    non_depth_cols = [c for c in df_processed.columns if c != "DEPTH"]
    for col in non_depth_cols:
        df_processed[col] = _despike_series(df_processed[col])

    # 6. 保存处理后的文件到覆盖目录（覆盖原有内容）
    returned_file_ids = save_processed_files(df_processed, file_row_info, file_mapping, output_dir_id, user_id, "casing_bolt_removal")

    # 验证文件是否真的保存成功
    if not returned_file_ids:
        raise ValueError("未找到与原始文件对应的处理结果文件")

    # 检查数据库中是否实际存在这些文件
    for filename, file_id in returned_file_ids.items():
        saved_file = File.query.get(file_id)
        if not saved_file:
            raise ValueError(f"文件 {filename} 保存失败，在数据库中找不到对应的记录")

    # 7. 更新配置
    try:
        # 获取或创建配置
        config = ModelConfig.query.filter_by(user_id=user_id).first()
        if not config:
            config = ModelConfig(user_id=user_id)
            db.session.add(config)

        # 更新为文件覆盖目录ID，供下一个算法使用
        config.dad_id = output_dir_id
        db.session.commit()
        print(f"✅ 已更新配置，下一个算法将使用覆盖目录 {output_dir_id}")

    except Exception as e:
        db.session.rollback()
        print(f"❌ 更新配置失败: {str(e)}")
        raise

    # 8. 获取返回数据
    original_file = File.query.get(input_file_id)
    result_file_id = returned_file_ids.get(original_file.name) if original_file else None
    if not result_file_id:
        result_data = {"message": "未找到对应的处理结果文件"}
    else:
        result_data = get_processed_file_data(result_file_id)

    print("消除套管栓处理完成")
    return {
        "process_type": "casing_bolt_removal",
        "message": "消除套管栓处理成功",
        "data": result_data,
        "file_ids": returned_file_ids  # 返回所有处理后的文件ID
    }


# 预处理算法映射表，用于动态调用
PROCESS_FUNCTIONS = {
    "zscore": zscore_process,
    "岩性分类": normalization_with_clustering,
    "basic_normalization": basic_normalization_process,
    "casing_bolt_removal": casing_bolt_removal_process
}

PROCESS_TYPE_ALIASES = {
    "岩性区分": "岩性分类",
    "消除套管栓": "casing_bolt_removal",
}


# 统一处理接口 - 支持流水线处理多个预处理算法
@tre_bp.route('/process', methods=['POST'])
def process_data():
    try:
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

        # 2. 获取请求参数
        request_data = request.json or {}
        # type必须是数组，表示处理算法的执行顺序
        process_types = request_data.get('type')

        # 3. 获取文件ID并查询数据库
        file_id_raw = request_data.get('key')
        if file_id_raw is None or file_id_raw == "":
            return jsonify({"code": 400, "message": "Missing file ID"}), 400
        try:
            file_id = int(file_id_raw)
        except (TypeError, ValueError):
            return jsonify({"code": 400, "message": "Invalid file ID"}), 400

        file_record = File.query.filter_by(id=file_id).first()
        if not file_record:
            return jsonify({"code": 404, "message": "File not found"}), 404

        # 4. 保存目录ID和预处理参数到ModelConfig表（关联当前用户）
        config = ModelConfig.query.filter_by(user_id=user_id).first()

        if config:
            # 更新现有配置的dad_id和原始文件ID
            config.dad_id = file_record.directory_id
            config.original_file_id = file_id
        else:
            # 创建新配置
            config = ModelConfig(
                dad_id=file_record.directory_id,
                original_file_id=file_id,
                user_id=user_id
            )
            db.session.add(config)

        # 持久化预处理参数（仅当请求中提供时更新）
        req_predict_target = request_data.get('predict_target')
        if req_predict_target is not None and str(req_predict_target).strip():
            config.predict_target = str(req_predict_target).strip()
        req_scaler_type = request_data.get('scaler_type')
        if req_scaler_type is not None:
            config.scaler_type = req_scaler_type
        req_sequence_length = request_data.get('sequence_length')
        if req_sequence_length is not None:
            try:
                config.sequence_length = int(req_sequence_length)
            except (ValueError, TypeError):
                pass
        req_batch_size = request_data.get('batch_size')
        if req_batch_size is not None:
            try:
                config.batch_size = int(req_batch_size)
            except (ValueError, TypeError):
                pass
        req_input_size = request_data.get('input_size')
        if req_input_size is not None:
            try:
                config.input_size = int(req_input_size)
            except (ValueError, TypeError):
                pass

        db.session.commit()
        directory_id = file_record.directory_id
        preprocess_root_id = get_or_create_cover_directory(directory_id, user_id)

        # 验证覆盖目录是否创建成功
        if not preprocess_root_id:
            return jsonify({"code": 500, "message": "创建覆盖目录失败"}), 500

        # 5. 处理算法类型格式
        # 如果是单个字符串，转换为数组
        if isinstance(process_types, str):
            process_types = [process_types]
        # 如果没有指定处理类型或为空，执行默认处理
        elif not process_types:
            result_data = get_processed_file_data(file_id)
            if isinstance(result_data, dict) and result_data.get("code") and result_data.get("data") is None:
                status_code = int(result_data.get("code") or 500)
                return jsonify({
                    "code": status_code,
                    "message": result_data.get("message") or "文件处理失败",
                    "process_type": "default",
                    "data": None
                }), status_code
            return jsonify({
                "code": 200,
                "message": "文件处理成功",
                "process_type": "default",
                "data": result_data
            })

        process_types = [PROCESS_TYPE_ALIASES.get(t, t) for t in process_types]

        # 验证处理类型是否有效
        valid_types = PROCESS_FUNCTIONS.keys()
        invalid_types = [t for t in process_types if t not in valid_types]
        if invalid_types:
            return jsonify({
                "code": 400,
                "message": f"不支持的处理类型: {', '.join(invalid_types)}",
                "valid_types": list(valid_types)
            }), 400

        # 6. 流水线执行所有指定的预处理算法
        args = get_parameters(user_id)
        last_result = None  # 只保留最后一个结果
        current_input_file_id = file_id

        for i, process_type in enumerate(process_types):
            try:
                print(f"\n===== 开始执行第 {i + 1} 个算法: {process_type} =====")

                # 保存原始predict_target值，用于后续恢复
                original_predict_target = args.predict_target

                # 特殊处理：消除套管栓不需要predict_target
                if process_type == "casing_bolt_removal":
                    args.predict_target = None
                # 对于需要predict_target的算法，确保它有值
                elif process_type in ["岩性分类", "zscore", "basic_normalization"]:
                    requested_predict_target = request_data.get('predict_target')
                    if requested_predict_target is not None and str(requested_predict_target).strip():
                        args.predict_target = requested_predict_target
                    if not args.predict_target:
                        raise ValueError(f"处理类型 {process_type} 需要指定predict_target参数")




                # 调用对应的处理函数
                process_func = PROCESS_FUNCTIONS[process_type]
                output_dir_id = get_or_create_process_subdir(preprocess_root_id, user_id, process_type)
                result = process_func(args, user_id, current_input_file_id, output_dir_id)
                # 更新最后结果
                last_result = result

                # 恢复原始predict_target值，避免影响后续算法
                args.predict_target = original_predict_target

                current_file_mapping = result.get("file_ids", {})
                if not current_file_mapping:
                    raise ValueError(f"算法 {process_type} 未成功保存任何文件")
                input_file = File.query.get(current_input_file_id)
                next_input_id = current_file_mapping.get(input_file.name) if input_file else None
                if not next_input_id:
                    raise ValueError(f"算法 {process_type} 未找到当前文件的处理结果")
                current_input_file_id = int(next_input_id)

            except Exception as e:
                # 如果在执行过程中出错，返回错误信息
                return jsonify({
                    "code": 500,
                    "message": f"执行算法 {process_type} 时出错: {str(e)}",
                    "process_type": process_type,
                    "error": True
                }), 500

        # 只返回最后一个算法的结果
        # 在process_data路由的最后部分，添加保存逻辑
        # 找到返回结果的位置，修改为：

        # 修改保存逻辑，使用绝对路径并打印
        if last_result:
            last_payload = last_result.get("data")
            if isinstance(last_payload, dict) and last_payload.get("code") and last_payload.get("data") is None:
                status_code = int(last_payload.get("code") or 500)
                return jsonify({
                    "code": status_code,
                    "message": last_payload.get("message") or last_result.get("message") or "处理失败",
                    "process_type": last_result.get("process_type"),
                    "data": None
                }), status_code

            debug_save_json = bool(request_data.get("debug_save_json"))
            if debug_save_json:
                import json
                import os
                from datetime import datetime

                save_dir = os.path.join(os.getcwd(), "processed_results")
                os.makedirs(save_dir, exist_ok=True)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(save_dir, f"result_{timestamp}.json")

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(last_result["data"], f, ensure_ascii=False)

                print(f"\n===== 结果数据已保存到绝对路径: {file_path} =====")

                return jsonify({
                    "code": 200,
                    "message": f"成功执行 {len(process_types)} 个算法步骤，返回最后一步结果。数据已保存到 {file_path}",
                    "process_type": last_result["process_type"],
                    "data": last_result["data"],
                    "saved_to": file_path
                })

            return jsonify({
                "code": 200,
                "message": f"成功执行 {len(process_types)} 个算法步骤，返回最后一步结果。",
                "process_type": last_result["process_type"],
                "data": last_result["data"]
            })
        else:
            # 保持原逻辑不变
            return jsonify({
                "code": 500,
                "message": "未获得任何处理结果"
            }), 500



    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": f"处理错误: {str(e)}"
        }), 500
