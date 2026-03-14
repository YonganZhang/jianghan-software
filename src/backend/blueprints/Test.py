import os
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from torch.utils.data import DataLoader, TensorDataset
import torch
from tools.data_pre import get_model
from tools.tool_for_pre import get_parameters
import zipfile
from tools.tool_for_test import plot_results
from models import Directory, File, Lossimagemodel, Trainmodel, Errtab, ModelConfig
from flask import Blueprint, request, jsonify, current_app
import jwt
import pickle
from exts import db, socketio
from contextlib import contextmanager
import sys
import re
import ast
import gzip
from io import BytesIO
from utils_path import resolve_content_path
from typing import Any


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


txt_bp = Blueprint('txt_bp', __name__)


@contextmanager
def redirect_print():
    original_stdout = sys.stdout

    # 主类型正则（匹配前缀）
    MAIN_TYPE_PATTERN = re.compile(r'^\[(log)\]\s*(.*)$')
    # 新增：匹配外层大括号包裹的内容（如{[1, 2, 3]}）
    BRACES_PATTERN = re.compile(r'^\{(.*)\}$')

    # 类型处理函数
    def handle_log(content):
        return {'event': 'log', 'data': {'type': 'log', 'content': content}}

    TYPE_HANDLERS = {
        "log": handle_log
    }

    class TypedSocketIOStream:
        def write(self, data):
            original_stdout.write(data)
            cleaned_data = data.strip()
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

            # 生成并发送 payload
            if data_type in TYPE_HANDLERS:
                payload = TYPE_HANDLERS[data_type](content)
            else:
                payload = {'event': data_type, 'data': {"type": data_type, "content": content}}

            socketio.emit('multitype_log', payload)

        def flush(self):
            original_stdout.flush()

    # 重定向标准输出
    sys.stdout = TypedSocketIOStream()
    try:
        yield
    finally:
        sys.stdout = original_stdout


def test_main(args, idm, userid, dir_id, typemd, predict_mode=False):
    all_results = []
    # 获取指定目录
    directory = Directory.query.get(dir_id)
    if not directory:
        print(f"[log]错误：未找到ID为{dir_id}的目录")
        return all_results  # 返回空列表

    # 获取目录中未删除的文件
    files = directory.files.filter(File.deleted_at.is_(None)).all()
    if not files:
        print(f"[log]目录ID {dir_id} 中没有找到可用文件")
        return all_results  # 返回空列表

    # 生成时间戳用于结果目录命名
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y%m%d_%H%M%S")
    base_result_dir = f"[log]预测结果_{formatted_time}" if predict_mode else f"测试结果_{formatted_time}"
    # os.makedirs(base_result_dir, exist_ok=True)

    scaler_X_train, scaler_y_train = load_training_scalers(userid)
    print(f"[log]scaler加载: X={'OK' if scaler_X_train is not None else 'None'}, "
          f"y={'OK' if scaler_y_train is not None else 'None'}")

    # 获取所有预处理输出目录 ID（dad_id 及其兄弟目录）
    config = ModelConfig.query.filter_by(user_id=userid).first()
    preprocessed_dir_id = config.dad_id if config else None
    preprocessed_dir_ids = get_preprocessed_dir_ids(preprocessed_dir_id)
    print(f"[log]预处理目录ID(dad_id): {preprocessed_dir_id}, 全部预处理目录: {preprocessed_dir_ids}")

    for file_idx, file in enumerate(files, 1):
        print(f"[log]开始处理第{file_idx}/{len(files)}个文件 (dir_id={file.directory_id})")
        try:
            file_path = resolve_content_path(file.content)
            if not file_path or not os.path.exists(file_path):
                print(f"[log]文件不存在：{file_path}，跳过")
                continue

            fid = file.id  # 移到此处，确保所有文件类型都能获取到fid
            data = None  # 初始化data变量

            # 根据文件类型选择打开方式
            if file.type == 'xlsx':
                # 读取Excel文件
                with open(file_path, 'rb') as f:
                    excel_data = BytesIO(f.read())
                # 尝试读取Excel
                try:
                    data = pd.read_excel(excel_data)
                except Exception as e1:
                    print(f"[log]Excel读取失败：{str(e1)}，跳过该文件")
                    continue
            elif file.type == 'txt':
                # 读取txt文件（根据实际格式调整参数，如分隔符）
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # 示例：假设是逗号分隔的CSV格式，根据实际情况修改sep参数
                        data = pd.read_csv(f, sep=',')
                except Exception as e1:
                    print(f"[log]TXT读取失败：{str(e1)}，跳过该文件")
                    continue
            else:
                print(f"[log]不支持的文件类型：{file.type}，跳过")
                continue

            # 检查数据是否为DataFrame
            if not isinstance(data, pd.DataFrame):
                print(f"[log]文件{file_idx}内容不是DataFrame格式，跳过")
                continue

        except Exception as e:
            print(f"[log]获取文件{file_idx}内容失败：{str(e)}，跳过")
            continue

        target_column = args.predict_target
        if target_column not in data.columns:
            print(f"[log]文件中未找到目标列'{target_column}'，跳过")
            continue

        sequence_length = args.sequence_length
        if predict_mode:
            data[target_column] = 0

        try:
            X_test, y_test, _ = create_time_series(data, target_column, sequence_length)
            if len(X_test) == 0 or len(y_test) == 0:
                print(f"[log]文件{file_idx}无法生成有效时序数据，跳过")
                continue
        except Exception as e:
            print(f"[log]文件{file_idx}转换时序数据失败：{str(e)}，跳过")
            continue

        try:
            # ---- 归一化策略 ----
            # 预处理数据（来自预处理流水线任意步骤的目录）：目标列已归一化
            # 原始数据：所有列均为原始尺度，需全量归一化
            is_preprocessed = (file.directory_id in preprocessed_dir_ids)
            print(f"[log]归一化路径: is_preprocessed={is_preprocessed}, "
                  f"file.dir_id={file.directory_id}, 预处理目录集={preprocessed_dir_ids}")
            print(f"[log]归一化前 y_test范围: [{np.min(y_test):.4f}, {np.max(y_test):.4f}]")

            if scaler_X_train is not None and scaler_y_train is not None:
                if is_preprocessed:
                    # 预处理数据：仅归一化 DEPTH 列，其余保持不变
                    X_new_normalized, y_new_normalized = normalize_preprocessed_data(
                        X_test, y_test, scaler_X_train
                    )
                else:
                    # 原始数据：全量归一化
                    X_new_normalized, y_new_normalized = normalize_with_scalers(
                        X_test, y_test, scaler_X_train, scaler_y_train
                    )
                scaler_X, scaler_y = scaler_X_train, scaler_y_train
            else:
                # 无训练归一化器时的回退方案（不推荐，精度会下降）
                X_new_normalized, y_new_normalized, scaler_X, scaler_y = normalize_and_load(X_test, y_test)
        except Exception as e:
            print(f"[log]文件{file_idx}归一化失败：{str(e)}，跳过")
            continue

        # 创建数据加载器
        batch_size = args.batch_size
        test_dataset = TensorDataset(
            torch.tensor(X_new_normalized, dtype=torch.float32),
            torch.tensor(y_new_normalized, dtype=torch.float32)
        )
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

        file_results = test(args, idm, typemd, test_loader, scaler_X, scaler_y, fid, userid, predict_mode)
        if file_results:
            all_results.append(file_results)

    return all_results


def test_main_by_file_ids(args, idm, userid, file_ids, typemd, predict_mode=False):
    all_results = []
    if not file_ids:
        return all_results

    normalized_ids = []
    for x in file_ids:
        try:
            normalized_ids.append(int(x))
        except (TypeError, ValueError):
            continue
    normalized_ids = list(dict.fromkeys(normalized_ids))
    if not normalized_ids:
        return all_results

    files = File.query.filter(File.id.in_(normalized_ids), File.deleted_at.is_(None)).all()
    if not files:
        print("[log]未找到可用的测试文件")
        return all_results

    scaler_X_train, scaler_y_train = load_training_scalers(userid)
    print(f"[log]scaler加载: X={'OK' if scaler_X_train is not None else 'None'}, "
          f"y={'OK' if scaler_y_train is not None else 'None'}")

    # 获取所有预处理输出目录 ID（dad_id 及其兄弟目录）
    config = ModelConfig.query.filter_by(user_id=userid).first()
    preprocessed_dir_id = config.dad_id if config else None
    preprocessed_dir_ids = get_preprocessed_dir_ids(preprocessed_dir_id)
    print(f"[log]预处理目录ID(dad_id): {preprocessed_dir_id}, 全部预处理目录: {preprocessed_dir_ids}")

    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y%m%d_%H%M%S")
    base_result_dir = f"[log]预测结果_{formatted_time}" if predict_mode else f"测试结果_{formatted_time}"

    for file_idx, file in enumerate(files, 1):
        print(f"[log]开始处理第{file_idx}/{len(files)}个文件 (dir_id={file.directory_id})")
        try:
            file_path = resolve_content_path(file.content)
            if not file_path or not os.path.exists(file_path):
                print(f"[log]文件不存在：{file_path}，跳过")
                continue

            fid = file.id
            data = None

            if file.type == 'xlsx':
                with open(file_path, 'rb') as f:
                    excel_data = BytesIO(f.read())
                try:
                    data = pd.read_excel(excel_data)
                except Exception as e1:
                    print(f"[log]Excel读取失败：{str(e1)}，跳过该文件")
                    continue
            elif file.type == 'txt':
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = pd.read_csv(f, sep=',')
                except Exception as e1:
                    print(f"[log]TXT读取失败：{str(e1)}，跳过该文件")
                    continue
            else:
                print(f"[log]不支持的文件类型：{file.type}，跳过")
                continue

            if not isinstance(data, pd.DataFrame):
                print(f"[log]文件{file_idx}内容不是DataFrame格式，跳过")
                continue

        except Exception as e:
            print(f"[log]获取文件{file_idx}内容失败：{str(e)}，跳过")
            continue

        target_column = args.predict_target
        if target_column not in data.columns:
            print(f"[log]文件中未找到目标列'{target_column}'，跳过")
            continue

        sequence_length = args.sequence_length
        if predict_mode:
            data[target_column] = 0

        try:
            X_test, y_test, _ = create_time_series(data, target_column, sequence_length)
            if len(X_test) == 0 or len(y_test) == 0:
                print(f"[log]文件{file_idx}无法生成有效时序数据，跳过")
                continue
        except Exception as e:
            print(f"[log]文件{file_idx}转换时序数据失败：{str(e)}，跳过")
            continue

        try:
            # ---- 归一化策略 ----
            is_preprocessed = (file.directory_id in preprocessed_dir_ids)
            print(f"[log]归一化路径: is_preprocessed={is_preprocessed}, "
                  f"file.dir_id={file.directory_id}, 预处理目录集={preprocessed_dir_ids}")
            print(f"[log]归一化前 y_test范围: [{np.min(y_test):.4f}, {np.max(y_test):.4f}]")

            if scaler_X_train is not None and scaler_y_train is not None:
                if is_preprocessed:
                    X_new_normalized, y_new_normalized = normalize_preprocessed_data(
                        X_test, y_test, scaler_X_train
                    )
                else:
                    X_new_normalized, y_new_normalized = normalize_with_scalers(
                        X_test, y_test, scaler_X_train, scaler_y_train
                    )
                scaler_X, scaler_y = scaler_X_train, scaler_y_train
            else:
                X_new_normalized, y_new_normalized, scaler_X, scaler_y = normalize_and_load(X_test, y_test)
        except Exception as e:
            print(f"[log]文件{file_idx}归一化失败：{str(e)}，跳过")
            continue

        batch_size = args.batch_size
        test_dataset = TensorDataset(
            torch.tensor(X_new_normalized, dtype=torch.float32),
            torch.tensor(y_new_normalized, dtype=torch.float32)
        )
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

        file_results = test(args, idm, typemd, test_loader, scaler_X, scaler_y, fid, userid, predict_mode)
        if file_results:
            all_results.append(file_results)

    return all_results


def test(args, idm, typemd, test_loader, scaler_X, scaler_y, fid, userid, predict_mode=False):
    # 初始化模型
    model = get_model(args)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    model.eval()

    # 从数据库加载模型（根据新的路径存储方式）
    try:
        if typemd == "final-data":
            # 加载最终模型（Lossimagemodel）
            model_file = Lossimagemodel.query.get(idm)
            if not model_file:
                raise ValueError(f"[log]未找到用户{userid}的最终模型文件（ID: {idm}）")

            # 获取模型文件路径并验证
            model_path = resolve_content_path(model_file.trainepoch_path) if model_file.trainepoch_path else None
            if not model_path or not os.path.exists(model_path):
                raise FileNotFoundError(f"[log]最终模型文件不存在或路径无效: {model_path}")

            # 读取gzip压缩的pickle文件（匹配save_trainepoch的保存格式）
            with gzip.open(model_path, 'rb') as f:
                model_state_dict = pickle.load(f)

            # 加载模型参数
            model.load_state_dict(model_state_dict)
            print("[log]最终模型加载成功")

        elif typemd == "best-data":
            # 加载最佳模型（Trainmodel）
            model_file = Trainmodel.query.get(idm)
            if not model_file:
                raise ValueError(f"[log]未找到用户{userid}的最佳模型文件（ID: {idm}）")

            # 获取模型文件路径并验证
            model_path = resolve_content_path(model_file.trainepoch_path) if model_file.trainepoch_path else None
            if not model_path or not os.path.exists(model_path):
                raise FileNotFoundError(f"[log]最佳模型文件不存在或路径无效: {model_path}")

            # 读取gzip压缩的pickle文件
            with gzip.open(model_path, 'rb') as f:
                model_state_dict = pickle.load(f)

            # 加载模型参数
            model.load_state_dict(model_state_dict)
            print("[log]最佳模型加载成功")

    except Exception as e:
        print(f"[log]模型加载失败：{str(e)}")
        return None

    # 推理过程
    all_predictions = []
    all_targets = []
    depth = []
    print("[log]开始推理...")

    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            all_predictions.extend(outputs.cpu().numpy())
            all_targets.extend(targets.cpu().numpy())
            depth.extend(inputs[:, -1, 0].cpu().numpy())

    # 转换为numpy数组
    all_predictions = np.array(all_predictions)
    all_targets = np.array(all_targets)
    depth = np.array(depth)

    # 反归一化
    try:
        depth_inv, all_targets_inv = inverse_normalize_and_load(
            depth, all_targets, scaler_X, scaler_y, args=args
        )
        _, all_predictions_inv = inverse_normalize_and_load(
            depth, all_predictions, scaler_X, scaler_y, args=args
        )
        print(f"[log]反归一化完成 — targets范围: [{all_targets_inv.min():.4f}, {all_targets_inv.max():.4f}], "
              f"predictions范围: [{all_predictions_inv.min():.4f}, {all_predictions_inv.max():.4f}]")
    except Exception as e:
        print(f"[log]反归一化失败：{str(e)}")
        return None

    all_targets_inv = np.asarray(all_targets_inv).reshape(-1)
    all_predictions_inv = np.asarray(all_predictions_inv).reshape(-1)
    depth_inv = np.asarray(depth_inv).reshape(-1)

    # ---- 按深度去重：滑动窗口产生大量重复深度，按深度分组取均值 ----
    df_result = pd.DataFrame({
        'depth': depth_inv,
        'pred': all_predictions_inv,
        'true': all_targets_inv
    })
    df_grouped = df_result.groupby('depth', sort=True).mean().reset_index()
    depth_dedup = df_grouped['depth'].values
    pred_dedup = df_grouped['pred'].values
    true_dedup = df_grouped['true'].values

    # 预测值对应的深度坐标 [[x0,y0], [x1,y1], ...]
    prediction_coords = [
        [float(pred_dedup[i]), float(depth_dedup[i])]
        for i in range(len(pred_dedup))
    ]

    # 真实值对应的深度坐标（仅测试模式）
    true_coords = None
    if not predict_mode:
        true_coords = [
            [float(true_dedup[i]), float(depth_dedup[i])]
            for i in range(len(true_dedup))
        ]
        # 计算评估指标
        mse = mean_squared_error(all_targets_inv, all_predictions_inv)
        mae = mean_absolute_error(all_targets_inv, all_predictions_inv)
        rmse = np.sqrt(mse)
        r2 = r2_score(all_targets_inv, all_predictions_inv)

        # 先查询是否已有该file_id的记录
        existing_err = Errtab.query.filter_by(file_id=fid).first()

        if existing_err:
            # 如果存在，就更新现有记录
            existing_err.MSE = mse
            existing_err.MAE = mae
            existing_err.RMSE = rmse
            existing_err.R2 = r2
        else:
            # 如果不存在，才创建新记录
            wc = Errtab(
                file_id=fid,
                MSE=mse,
                MAE=mae,
                RMSE=rmse,
                R2=r2
            )
            db.session.add(wc)

        # 最后提交事务
        db.session.commit()
        print(f"[log]评估指标已保存至数据库")

    print(f"[log]当前文件处理完成")
    # 将坐标结果保存到字典并返回
    return {
        "文件id": fid,
        "prediction_coords": prediction_coords,
        "true_coords": true_coords
    }


def create_time_series(data, target_column, sequence_length):
    """将DataFrame转换为时序数据（返回X, y, feature_columns三个值）"""
    print("[log]开始转换为时序数据...")
    feature_columns = [c for c in data.columns if c != target_column]
    X, y = [], []
    total_sequences = len(data) - sequence_length

    if total_sequences <= 0:
        print(f"[log]警告：数据长度({len(data)})小于序列长度({sequence_length})，无法生成时序数据")
        return np.array(X), np.array(y), feature_columns

    for i in range(total_sequences):
        X.append(data.iloc[i:i + sequence_length][feature_columns].values)
        y.append(data.iloc[i + sequence_length - 1][target_column])

    print(f"[log]时序数据转换完成，生成了{len(X)}个序列")
    return np.array(X), np.array(y), feature_columns


def normalize_and_load(X_new, y_new):
    """归一化特征和目标值（返回4个值）"""
    scaler_X = StandardScaler()
    scaler_y = StandardScaler()

    X_reshaped = X_new.reshape(-1, X_new.shape[-1])
    scaler_X.fit(X_reshaped)
    X_normalized = scaler_X.transform(X_reshaped).reshape(X_new.shape)

    y_reshaped = y_new.reshape(-1, 1)
    scaler_y.fit(y_reshaped)
    y_normalized = scaler_y.transform(y_reshaped)

    return X_normalized, y_normalized, scaler_X, scaler_y


def load_training_scalers(userid):
    try:
        config = ModelConfig.query.filter_by(user_id=userid).first()
        if not config:
            return None, None
        scaler_X = config.load_pkl('x')
        scaler_y = config.load_pkl('y')
        return scaler_X, scaler_y
    except Exception as e:
        print(f"[log]加载训练归一化器失败：{str(e)}")
        return None, None


def get_preprocessed_dir_ids(dad_id):
    """获取所有预处理输出目录 ID（dad_id 及其同级兄弟目录）。
    预处理流水线的每一步（去噪→标准化→岩性区分等）都在同一父目录下
    创建子目录，dad_id 仅记录最后一步。测试文件可能来自任意中间步骤，
    因此需要匹配所有兄弟目录。"""
    if dad_id is None:
        return set()
    dad_dir = Directory.query.get(dad_id)
    if not dad_dir or not dad_dir.parent_id:
        return {dad_id}
    siblings = Directory.query.filter_by(parent_id=dad_dir.parent_id).all()
    return {d.id for d in siblings}


def normalize_with_scalers(X_new, y_new, scaler_X, scaler_y):
    X_reshaped = X_new.reshape(-1, X_new.shape[-1])
    X_normalized = scaler_X.transform(X_reshaped).reshape(X_new.shape)
    y_normalized = scaler_y.transform(np.asarray(y_new).reshape(-1, 1))
    return X_normalized, y_normalized


def normalize_preprocessed_data(X_test, y_test, scaler_X):
    """
    【预处理数据专用归一化】
    预处理阶段 make_depth_denorm_unique() 将 DEPTH（第 0 列）反归一化为原始尺度，
    其余特征列和目标列保持归一化状态。
    因此这里只需对 DEPTH 列做归一化，其余列直接透传。

    参数:
        X_test: shape (n_samples, seq_len, n_features)，第 0 列为原始 DEPTH，其余已归一化
        y_test: shape (n_samples,) 或 (n_samples, 1)，已归一化
        scaler_X: 训练阶段拟合的特征归一化器（StandardScaler/MinMaxScaler/RobustScaler）

    返回:
        X_normalized: shape 同 X_test，所有列均为归一化值
        y_normalized: shape (n_samples, 1)，保持原归一化值不变
    """
    X = X_test.copy()
    flat = X.reshape(-1, X.shape[-1])

    # 构造与 scaler_X 输入维度一致的辅助矩阵，仅填充 DEPTH 列
    n_features_expected = getattr(scaler_X, 'n_features_in_', flat.shape[1])
    dummy = np.zeros((flat.shape[0], int(n_features_expected)), dtype=float)
    dummy[:, 0] = flat[:, 0]

    # scaler_X.transform 对每列独立归一化，只取第 0 列结果
    flat[:, 0] = scaler_X.transform(dummy)[:, 0]

    X_normalized = flat.reshape(X_test.shape)
    # 目标列已归一化，直接 reshape 为 (n, 1) 以匹配后续流程
    y_normalized = np.asarray(y_test).reshape(-1, 1)
    return X_normalized, y_normalized


def inverse_normalize_and_load(depth, y_normalized, scaler_X, scaler_y, args=None):
    """反归一化处理"""
    if args is None or not hasattr(args, 'input_size'):
        raise ValueError("[log]反归一化需要args包含input_size属性")

    depth = np.asarray(depth).reshape(-1)
    n_features = getattr(scaler_X, 'n_features_in_', args.input_size)
    depth_matrix = np.zeros((len(depth), int(n_features)), dtype=float)
    depth_matrix[:, 0] = depth
    depth_inv = scaler_X.inverse_transform(depth_matrix)[:, 0]

    y_original = scaler_y.inverse_transform(np.asarray(y_normalized).reshape(-1, 1)).reshape(-1)

    return depth_inv, y_original


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

        # 检查文件类型是否为xlsx
        if file_record.type != 'xlsx':
            return {
                "code": 400,
                "data": None,
                "message": f"不支持的文件类型: {file_record.type}，仅支持xlsx格式"
            }

        # 读取文件内容
        with open(file_path, 'rb') as f:
            file_content = f.read()

        # 处理Excel数据
        excel_data = BytesIO(file_content)
        df = pd.read_excel(excel_data)

        # ---- 预处理文件检测：若来自预处理目录，特征列需反归一化为原始尺度 ----
        try:
            user_id = file_record.user_id
            config = ModelConfig.query.filter_by(user_id=user_id).first()
            preprocessed_dir_id = config.dad_id if config else None
            preprocessed_dir_ids = get_preprocessed_dir_ids(preprocessed_dir_id)
            is_preprocessed = (file_record.directory_id in preprocessed_dir_ids)

            if is_preprocessed and config:
                scaler_X = config.load_pkl('x')
                if scaler_X is not None:
                    feature_cols = [c for c in df.columns if c != 'DEPTH']
                    if len(feature_cols) > 0:
                        # 构造与 scaler_X 输入维度一致的矩阵
                        n_expected = getattr(scaler_X, 'n_features_in_', len(feature_cols) + 1)
                        dummy = np.zeros((len(df), n_expected), dtype=float)
                        # 第 0 列放 DEPTH（已是原始尺度，inverse_transform 后会变，但我们不用它）
                        # 第 1~N 列放归一化的特征值
                        for i, col in enumerate(feature_cols):
                            col_idx = i + 1  # DEPTH 占第 0 列
                            if col_idx < n_expected:
                                dummy[:, col_idx] = df[col].values
                        original = scaler_X.inverse_transform(dummy)
                        for i, col in enumerate(feature_cols):
                            col_idx = i + 1
                            if col_idx < n_expected:
                                df[col] = original[:, col_idx]
        except Exception as e:
            # 反归一化失败时回退到原始数据展示，不阻塞流程
            print(f"[log]曲线反归一化失败（回退原始数据）: {e}")

        # 检查是否有DEPTH列
        if 'DEPTH' not in df.columns:
            return {
                "code": 400,
                "data": None,
                "message": "Excel文件缺少DEPTH列"
            }

        # 获取深度列数据
        depth_data = df['DEPTH']

        # 收集所有特征列（排除DEPTH列）
        feature_columns = [col for col in df.columns if col != 'DEPTH']

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

        # 处理第一组特征列
        for col in group1_columns:
            points = []
            for idx in range(len(df)):
                feature_val = df[col].iloc[idx]
                depth_val = depth_data.iloc[idx]

                # 跳过空值
                if pd.notna(feature_val) and pd.notna(depth_val):
                    points.append([
                        float(feature_val),  # 特征值
                        float(depth_val)  # 深度值
                    ])
            result["axisData"][str(col)] = points

        # 处理第二组特征列
        for col in group2_columns:
            points = []
            for idx in range(len(df)):
                feature_val = df[col].iloc[idx]
                depth_val = depth_data.iloc[idx]

                # 跳过空值
                if pd.notna(feature_val) and pd.notna(depth_val):
                    points.append([
                        float(feature_val),  # 特征值
                        float(depth_val)  # 深度值
                    ])
            result["axisData2"][str(col)] = points

        return result

    except Exception as e:
        return {
            "code": 500,
            "data": None,
            "message": f"处理文件时发生错误: {str(e)}"
        }


def get_coordinates_by_file_id(data_list, target_file_id):
    """
    从数据列表中通过文件id获取对应的预测坐标和真实坐标
    """
    for item in data_list:
        # 匹配目标文件id
        if item.get("文件id") == target_file_id:
            # 返回与数据中一致的键（prediction_coords/true_coords）
            return {
                "prediction_coords": item.get("prediction_coords"),
                "true_coords": item.get("true_coords")
            }
    # 未找到时返回None
    return None


# 上传原始测试文件
@txt_bp.route('/getfile', methods=['POST'])
def get_data():
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
    request_data = request.json


    file_id = request_data.get('file_id')
    file_record = File.query.get(file_id)
    if not file_record:
        return jsonify({"code": 404, "message": "文件不存在"}), 404
    if file_record.user_id != user_id:
        return jsonify({"code": 403, "message": "没有权限访问此文件"}), 403
    if file_id:
        result_data = get_processed_file_data(file_id)
        return jsonify({
            "code": 200,
            "message": "文件上传成功",
            "process_type": "default",
            "data": result_data
        })
    else:
        return jsonify({"code": 400, "message": "Missing file ID"}), 400


# 上传模型接口
@txt_bp.route('/modelname', methods=['GET'])
def model():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"code": 401, "message": "未提供认证token"}), 401

    # 提取token
    token = auth_header.split(" ")[1] if auth_header.startswith('Bearer ') else auth_header

    try:
        # 验证token
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        userid = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"code": 401, "message": "token已过期"}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({"code": 401, "message": f"无效的token: {str(e)}"}), 401

    # 查询所有最终模型
    models = Lossimagemodel.query.filter_by(user_id=userid).all()
    # 查询所有最佳模型
    models1 = Trainmodel.query.filter_by(user_id=userid).all()
    # 构建模型列表（过滤掉路径为空的无效记录）
    model_list = []
    model_list1 = []
    # 上传最终模型
    for model_obj in models:
        if not model_obj.trainepoch_path:
            continue
        model_list.append({
            "id": model_obj.id,
            "name": model_obj.trainname,  # 确保字段名正确
            "type": "final-data"
        })

    # 上传最佳模型
    for model_obj in models1:
        if not model_obj.trainepoch_path:
            continue
        model_list1.append({
            "id": model_obj.id,
            "name": model_obj.file_name,  # 确保字段名正确
            "type": "best-data"
        })

    return jsonify({
        "code": 200,
        "message": "成功",
        "data": {
            "final-data": model_list,
            "best-data": model_list1
        }
    })


# 测试接口
@txt_bp.route('/test', methods=['POST'])
def txt():
    try:
        # 检查请求Content-Type是否为JSON
        if request.content_type != 'application/json':
            return jsonify({
                "code": 415,
                "message": "不支持的媒体类型，请使用application/json"
            }), 415

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

        # 3. 获取请求参数
        try:
            data = request.get_json()
            if not data:
                return jsonify({"code": 400, "message": "请求数据为空"}), 400
        except Exception as e:
            return jsonify({"code": 400, "message": f"解析JSON数据失败: {str(e)}"}), 400

        # 4. 验证必要参数
        required_fields = ['file_id', 'idm', 'predict_mode', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({"code": 400, "message": f"缺少必要参数: {field}"}), 400

        file_ids = data.get('file_ids')
        dir_id = data.get('dir_id')
        if not (dir_id is not None or (isinstance(file_ids, list) and len(file_ids) > 0)):
            return jsonify({"code": 400, "message": "缺少必要参数: dir_id 或 file_ids"}), 400

        file_id = data['file_id']

        idm = data['idm']
        # todo 新更改---加上区分最佳和最终的id变量(type的值要么是---"final-data"，要么是---"best-data")
        typemd = data.get('type')
        predict_mode = data['predict_mode']

        # 5. 获取模型参数
        try:
            args = get_parameters(userid)
            if not args:
                return jsonify({"code": 500, "message": "获取模型参数失败"}), 500
        except Exception as e:
            return jsonify({"code": 500, "message": f"获取参数时出错: {str(e)}"}), 500
        try:
            with redirect_print():
                if isinstance(file_ids, list) and len(file_ids) > 0:
                    all_saved_coordinates = test_main_by_file_ids(
                        args, idm, userid, file_ids, typemd, predict_mode=predict_mode
                    )
                else:
                    all_saved_coordinates = test_main(args, idm, userid, dir_id, typemd, predict_mode=predict_mode)
        except Exception as e:
            print(f"处理文件时出错：{str(e)}")
            return jsonify({"code": 500, "message": f"处理文件时出错: {str(e)}"}), 500

        result = get_coordinates_by_file_id(all_saved_coordinates, file_id)
        if not result:
            return jsonify({"code": 404, "message": "未找到对应文件的预测结果"}), 404
        h = result["prediction_coords"]
        j = result["true_coords"]
        # 查询误差记录
        ero = Errtab.query.filter_by(file_id=file_id).first()

        # 处理查询结果为空的情况
        if not ero:
            # 可以返回空字典或提示信息，根据业务需求调整
            csero = {}
            # 可选：打印日志便于调试
            print(f"未找到file_id={file_id}对应的误差记录")
        else:
            # 查询成功时提取指标
            csero = {
                "MSE": ero.MSE,
                "MAE": ero.MAE,
                "RMSE": ero.RMSE,
                "R2": ero.R2
            }

        # todo 用户点到错误的表
        return jsonify({
            "code": 200,
            "message": "处理成功",
            "data": {
                "prediction_coords": result["prediction_coords"],
                "true_coords": result["true_coords"],
                "table": csero
            }
        })

    except Exception as e:
        error_msg = f"程序运行出错：{str(e)}"
        print(error_msg)
        # 确保任何异常情况下都返回有效的响应
        return jsonify({
            "code": 500,
            "message": error_msg
        }), 500
