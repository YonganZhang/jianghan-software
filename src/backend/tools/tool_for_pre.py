import argparse
import os
import pickle
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler
import gzip
import pickle  # 必须导入 pickle
from io import BytesIO
from exts import db
from models import ModelConfig, File, Directory
from sqlalchemy.exc import SQLAlchemyError


# ============ 固定范围归一化器 ============
# 基于测井曲线物理量纲的固定 min-max 范围，保证不同数据集归一化结果一致
WELL_LOG_RANGES = {
    'DEPTH': (0, 6000),       # 深度 (m)
    'GR':    (0, 150),        # 自然伽马 (API)
    'SP':    (0, 100),        # 自然电位 (mV)
    'CAL':   (6, 16),         # 井径 (in)
    'DEN':   (1.9, 2.9),      # 密度 (g/cm³)
    'CNL':   (-15, 45),       # 中子 (%)
    'AC':    (30, 130),       # 声波时差 (μs/ft)
    'RD':    (0.1, 1000),     # 深侧向电阻率 (Ω·m)
    'RS':    (0.1, 1000),     # 浅侧向电阻率 (Ω·m)
    'TOC':   (0, 10),         # 有机碳含量 (%)
    'POR':   (0, 40),         # 孔隙度 (%)
    'PERM':  (0.001, 1000),   # 渗透率 (mD)
    'SW':    (0, 100),        # 含水饱和度 (%)
    'RT':    (0.1, 1000),     # 真电阻率 (Ω·m)
}


class FixedRangeScaler:
    """基于测井曲线物理范围的固定 MinMax 归一化器。

    与 sklearn scaler 接口兼容（transform / inverse_transform / n_features_in_）。
    策略：
      1. 已知曲线名 → 使用 WELL_LOG_RANGES 中的固定物理范围
      2. 未知曲线名 → 使用训练数据的 1%~99% 分位数（抗异常值）
      3. 所有范围随对象 pickle 保存，测试/预测时自动复用
    归一化目标区间: [0, 1]
    """

    def __init__(self):
        self.n_features_in_ = None
        self._min = None       # shape (n_features,)
        self._range = None     # shape (n_features,) = max - min
        self._col_names = None
        self._source = None    # 记录每列范围来源: 'fixed' 或 'data'

    def fit(self, X, col_names=None):
        """拟合：根据列名确定每列的归一化范围。

        Args:
            X: ndarray, shape (n_samples, n_features)
            col_names: list[str], 每列对应的曲线名称
        """
        n_features = X.shape[1]
        self.n_features_in_ = n_features
        self._col_names = list(col_names) if col_names else [f'col_{i}' for i in range(n_features)]

        mins = np.zeros(n_features, dtype=float)
        ranges = np.ones(n_features, dtype=float)
        sources = []

        for i, name in enumerate(self._col_names):
            prefix = name.split(' ')[0].upper()
            if prefix in WELL_LOG_RANGES:
                lo, hi = WELL_LOG_RANGES[prefix]
                sources.append('fixed')
            else:
                # 未知曲线：用 1%~99% 分位数，比 min/max 更抗异常值
                col_data = X[:, i]
                valid = col_data[np.isfinite(col_data)]
                if len(valid) > 0:
                    lo = float(np.percentile(valid, 1))
                    hi = float(np.percentile(valid, 99))
                else:
                    lo, hi = 0.0, 1.0
                # 加 5% padding 防止边界值归一化后恰好为 0/1
                pad = (hi - lo) * 0.05 if hi > lo else 1.0
                lo -= pad
                hi += pad
                sources.append('data')

            mins[i] = lo
            ranges[i] = hi - lo if (hi - lo) != 0 else 1.0

        self._min = mins
        self._range = ranges
        self._source = sources
        return self

    def transform(self, X):
        """归一化到 [0, 1]"""
        return (X - self._min) / self._range

    def inverse_transform(self, X):
        """反归一化回原始尺度"""
        return X * self._range + self._min

    def fit_transform(self, X, col_names=None):
        self.fit(X, col_names=col_names)
        return self.transform(X)

    def summary(self):
        """返回每列的范围摘要（调试用）"""
        lines = []
        if self._col_names and self._min is not None:
            for i, name in enumerate(self._col_names):
                src = self._source[i] if self._source else '?'
                lo = self._min[i]
                hi = lo + self._range[i]
                lines.append(f"  {name}: [{lo:.4f}, {hi:.4f}] ({src})")
        return '\n'.join(lines)



def load_excel_files(directory):
    """
    读取指定目录下的所有xlsx文件并合并成一个DataFrame
    """
    print("开始读取Excel文件...")
    files = [f for f in os.listdir(directory) if f.endswith('.xlsx')]
    total_files = len(files)
    data_frames = []
    for i, file in enumerate(files):
        progress = (i + 1) / total_files * 100
        print(f"正在读取文件: {file} (全文件读取进度：{progress:.2f}%)")
        df = pd.read_excel(os.path.join(directory, file))
        data_frames.append(df)
    print("Excel文件读取完成。")
    return pd.concat(data_frames, ignore_index=True)


def create_time_series(data, target_column, sequence_length):
    """
    将DataFrame转换为时序数据。
    返回: X(ndarray), y(ndarray), feature_columns(list[str])
    """
    print("开始转换为时序数据...")
    feature_columns = [c for c in data.columns if c != target_column]
    X, y = [], []
    total_sequences = len(data) - sequence_length
    for i in range(total_sequences):
        X.append(data.iloc[i:i + sequence_length][feature_columns].values)
        y.append(data.iloc[i + sequence_length - 1][target_column])
    print("时序数据转换完成。")
    return np.array(X), np.array(y), feature_columns


def split_data(X, y, test_size=0.2, val_size=0.2):
    """
    将数据分为训练集、验证集和测试集
    """
    print("开始划分数据集...")
    # X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=test_size + val_size, random_state=42)
    # X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=test_size / (test_size + val_size), random_state=42)
    # print("数据集划分完成。")
    # return X_train, X_val, X_test, y_train, y_val, y_test

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=test_size + val_size, random_state=42)
    print("数据集划分完成。")
    return X_train, X_val, y_train, y_val


def create_data_loaders(X_train, X_val, y_train, y_val, batch_size=32):
    """
    创建数据加载器
    """
    print("开始创建数据加载器...")
    train_dataset = TensorDataset(torch.tensor(X_train, dtype=torch.float32), torch.tensor(y_train, dtype=torch.float32))
    val_dataset = TensorDataset(torch.tensor(X_val, dtype=torch.float32), torch.tensor(y_val, dtype=torch.float32))

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=True)

    print("数据加载器创建完成。")

    return train_loader, val_loader


def normalize_and_save(X_train_val, y_train_val, save_dir="data_save/本次数据读取的缓存",
                       scaler_type="minmax", col_names_X=None, col_name_y=None):
    """
    对X_train_val和y_train_val进行归一化，并保存归一化器到指定目录。
    scaler_type: 选择 'fixed', 'minmax', 'standard', 'robust'
    col_names_X: 特征列名列表（fixed 类型必需）
    col_name_y: 目标列名（fixed 类型必需）
    """
    print(f"正在进行归一化，使用归一化器: {scaler_type}")
    os.makedirs(save_dir, exist_ok=True)

    X_flat = X_train_val.reshape(-1, X_train_val.shape[-1])  # 展平

    # 选择归一化器类型
    if scaler_type == "fixed":
        scaler_X = FixedRangeScaler()
        scaler_y = FixedRangeScaler()
    elif scaler_type == "minmax":
        scaler_X = MinMaxScaler()
        scaler_y = MinMaxScaler()
    elif scaler_type == "standard":
        scaler_X = StandardScaler()
        scaler_y = StandardScaler()
    elif scaler_type == "robust":
        scaler_X = RobustScaler()
        scaler_y = RobustScaler()
    else:
        raise ValueError(f"不支持的归一化器类型: {scaler_type}")

    # 拟合并转换
    if isinstance(scaler_X, FixedRangeScaler):
        X_normalized = scaler_X.fit_transform(X_flat, col_names=col_names_X).reshape(X_train_val.shape)
        y_normalized = scaler_y.fit_transform(
            y_train_val.reshape(-1, 1),
            col_names=[col_name_y] if col_name_y else None
        )
    else:
        X_normalized = scaler_X.fit_transform(X_flat).reshape(X_train_val.shape)
        y_normalized = scaler_y.fit_transform(y_train_val.reshape(-1, 1))

    # 保存归一化器
    with open(os.path.join(save_dir, "scaler_X.pkl"), 'wb') as f:
        pickle.dump(scaler_X, f)
    with open(os.path.join(save_dir, "scaler_y.pkl"), 'wb') as f:
        pickle.dump(scaler_y, f)

    print("归一化完毕且已保存归一化器。")
    return X_normalized, y_normalized


def normalize_and_load(X_new, y_new, scaler_dir="data_save/本次数据读取的缓存"):
    """
    使用保存的归一化器对新数据进行归一化。

    :param X_new: 新的特征数据，形状为(Batch size, sequence len, features)
    :param y_new: 新的标签数据，形状为(Batch size,)
    :param scaler_dir: 归一化器的保存路径
    :return: 归一化后的X和y
    """
    # 加载已保存的归一化器
    with open(os.path.join(scaler_dir, "scaler_X.pkl"), 'rb') as f:
        scaler_X = pickle.load(f)

    with open(os.path.join(scaler_dir, "scaler_y.pkl"), 'rb') as f:
        scaler_y = pickle.load(f)

    # 对特征数据进行归一化
    X_normalized = scaler_X.transform(X_new.reshape(-1, X_new.shape[-1])).reshape(X_new.shape)

    # 对标签数据进行归一化
    y_normalized = scaler_y.transform(y_new.reshape(-1, 1))

    return X_normalized, y_normalized


def inverse_normalize_and_load(depth, y_normalized, scaler_dir="data_save/本次数据读取的缓存", args=None):
    """
    使用保存的归一化器对预测结果进行反归一化。

    :param X_normalized: 归一化后的特征数据，形状为(Batch size, sequence len, features)
    :param y_normalized: 归一化后的标签数据，形状为(Batch size,)
    :param scaler_dir: 归一化器的保存路径
    :return: 反归一化后的X和y
    """
    # 加载归一化器
    with open(os.path.join(scaler_dir, "scaler_X.pkl"), 'rb') as f:
        scaler_X = pickle.load(f)

    with open(os.path.join(scaler_dir, "scaler_y.pkl"), 'rb') as f:
        scaler_y = pickle.load(f)

    depth_expanded = np.tile(depth[:, np.newaxis], (1, args.input_size))
    # 对特征数据进行反归一化
    X_original = scaler_X.inverse_transform(depth_expanded)
    Depth = X_original[:, 0]
    # 对标签数据进行反归一化
    y_original = scaler_y.inverse_transform(y_normalized.reshape(-1, 1))

    return Depth, y_original


def inverse_normalize_and_load_ture(my_input, y_normalized, scaler_dir="data_save/本次数据读取的缓存", args=None):
    """
    使用保存的归一化器对预测结果进行反归一化。

    :param X_normalized: 归一化后的特征数据，形状为(Batch size, sequence len, features)
    :param y_normalized: 归一化后的标签数据，形状为(Batch size,)
    :param scaler_dir: 归一化器的保存路径
    :return: 反归一化后的X和y
    """
    # 加载归一化器
    with open(os.path.join(scaler_dir, "scaler_X.pkl"), 'rb') as f:
        scaler_X = pickle.load(f)

    with open(os.path.join(scaler_dir, "scaler_y.pkl"), 'rb') as f:
        scaler_y = pickle.load(f)

    # 对特征数据进行反归一化
    X_original = scaler_X.inverse_transform(my_input)
    # 对标签数据进行反归一化
    y_original = scaler_y.inverse_transform(y_normalized.reshape(-1, 1))

    return X_original, y_original


def remove_outliers_and_interpolate(
        df,
        lower_quantile=0.05,
        upper_quantile=0.95,
        raise_if_all_nan=True,
        args=None
):
    """
    通过分位数法删除异常值，并用均值填充首尾 NaN + 线性插值填充其他 NaN。

    参数:
        df (pd.DataFrame): 输入数据框
        lower_quantile (float): 下分位数阈值（默认 0.05）
        upper_quantile (float): 上分位数阈值（默认 0.95）
        raise_if_all_nan (bool): 如果整列为 NaN 是否报错（默认 True）

    返回:
        pd.DataFrame: 处理后的数据框
    抛出:
        ValueError: 如果整列为 NaN 且 raise_if_all_nan=True
    """
    df_processed = df.copy()
    target_column = args.predict_target
    # 检查目标列是否存在
    if target_column not in df_processed.columns:
        raise ValueError(f"目标列 '{target_column}' 不存在！")

    # 检查目标列是否全为 NaN
    if df_processed[target_column].isna().all():
        if raise_if_all_nan:
            raise ValueError(f"目标列 '{target_column}' 全为 NaN，无法处理！")
        else:
            return df_processed  # 直接返回原数据

    # 标记目标列的异常值
    lower_bound = df_processed[target_column].quantile(lower_quantile)
    upper_bound = df_processed[target_column].quantile(upper_quantile)
    mask = (df_processed[target_column] < lower_bound) | (df_processed[target_column] > upper_bound)

    # 将目标列的异常值设为 NaN，并同步设置同行的其他列为 NaN
    df_processed.loc[mask, df_processed.columns[1:]] = np.nan

    # 对每一列分别用该列的均值填充首尾 NaN
    for column in df_processed.columns:
        if pd.api.types.is_numeric_dtype(df_processed[column]):
            non_nan_mean = df_processed[column].mean()
            if pd.isna(df_processed[column].iloc[0]):
                df_processed[column].iloc[0] = non_nan_mean
            if pd.isna(df_processed[column].iloc[-1]):
                df_processed[column].iloc[-1] = non_nan_mean

    # 对所有列线性插值（因为其他列可能因同步操作产生 NaN）
    df_processed = df_processed.interpolate(method='linear')

    return df_processed


def add_random_noise_to_third_column(df_processed, args):
    """
    将 df_processed 第三列修改为 预测目标列 + [0, 0.05) 的随机噪声。
    """
    target_column = args.predict_target
    target_values = df_processed[target_column].values

    # 生成 0-0.05 的随机数数组
    random_noise = np.random.uniform(0, 15, size=len(target_values))

    # 计算新的值
    new_values = target_values + random_noise

    # 修改第三列
    third_col_name = df_processed.columns[2]
    df_processed[third_col_name] = new_values

    return df_processed


def Z_score(data_train_val, args):
    pass
    return data_train_val


def rock_classificate(data_train_val, args):
    pass
    return data_train_val


def clear_taoguan(data_train_val, args):
    pass
    return data_train_val


def main(directory, target_column, sequence_length, batch_size=32, normalization_path="data_save/本次数据读取的缓存", args=None):
    print("开始数据处理流程...")

    # 读取所有xlsx文件并合并
    data_train_val = load_excel_files(os.path.join(directory, "训练集和验证集"))

    # Z_score
    data_train_val = Z_score(data_train_val, args)

    # 岩性区分
    data_train_val = rock_classificate(data_train_val, args)

    # 消除套管栓
    data_train_val = clear_taoguan(data_train_val, args)

    # 将数据转换为时序数据
    X_train_val, y_train_val, feature_cols = create_time_series(data_train_val, target_column, sequence_length)

    # 归一化（归一化并保存归一化器）
    X_train_val_normalized, y_train_val_normalized = normalize_and_save(
        X_train_val, y_train_val, save_dir=normalization_path,
        scaler_type=args.scaler_type, col_names_X=feature_cols, col_name_y=target_column
    )


    # 划分训练集、验证集和测试集
    X_train, X_val, y_train, y_val = split_data(X_train_val_normalized, y_train_val_normalized)

    # 创建数据加载器
    train_loader, val_loader = create_data_loaders(X_train, X_val, y_train, y_val, batch_size)

    # 打印数据集的形状
    print(f'注意：以下为输入情况：')
    print(f'训练集: X={X_train.shape}, y={y_train.shape}')
    print(f'验证集: X={X_val.shape}, y={y_val.shape}')

    print("数据预处理流程完成")

    return train_loader, val_loader


def save_data_loaders(train_loader, val_loader, save_directory="data_save/本次数据读取的缓存"):
    """
    保存数据加载器到指定目录并存储目录路径
    """
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    with open(os.path.join(save_directory, 'train_loader.pkl'), 'wb') as f:
        pickle.dump(train_loader, f)
    with open(os.path.join(save_directory, 'val_loader.pkl'), 'wb') as f:
        pickle.dump(val_loader, f)


# todo 更改--------------------------------------------------------------------------------------------------------------


def deserialize_from_blob(blob):
    """从二进制数据反序列化对象"""
    if blob is None:
        raise ValueError("Received None blob data")

    buffer = BytesIO(blob)
    try:
        with gzip.GzipFile(fileobj=buffer, mode='rb') as f:
            return pickle.load(f)
    except (gzip.BadGzipFile, pickle.UnpicklingError) as e:
        raise RuntimeError(f"Deserialization failed: {str(e)}")


def load_data_loaders(args, userid):
    """
    从数据库加载数据加载器（适配文件路径存储方式）
    """
    try:
        # 获取用户配置
        model_config = ModelConfig.query.filter_by(user_id=userid).first()
        if not model_config:
            raise ValueError(f"用户 {userid} 没有模型配置记录")

        # 复用ModelConfig的load_pkl方法加载数据（内部已处理文件路径验证和解压）
        train_loader = model_config.load_pkl('trainloader')
        val_loader = model_config.load_pkl('valloader')

        print(f"数据加载器已从文件加载 (用户: {userid})")
        return train_loader, val_loader

    except SQLAlchemyError as e:
        raise RuntimeError(f"数据库查询失败: {str(e)}")
    except FileNotFoundError as e:
        raise RuntimeError(f"pkl文件不存在: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"加载数据加载器失败: {str(e)}")

# todo 更改--------------------------------------------------------------------------------------------------------------


def _read_file_record_to_df(file_record: File) -> pd.DataFrame:
    file_path = getattr(file_record, "content", None)
    if not file_path:
        raise ValueError(f"文件 {file_record.id} 缺少content路径")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件 {file_record.id} 物理文件不存在: {file_path}")

    if file_record.type == "xlsx":
        df = pd.read_excel(file_path)
    else:
        try:
            df = pd.read_csv(file_path, sep="\t", encoding="utf-8-sig")
        except Exception:
            df = pd.read_csv(file_path, sep=None, engine="python")

    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
    return df


def build_and_save_data_loaders_from_file_ids(args, user_id: int, file_ids):
    if not file_ids or not isinstance(file_ids, (list, tuple)):
        raise ValueError("file_ids 不能为空，且必须为数组")

    dfs = []
    for fid in file_ids:
        try:
            fid_int = int(fid)
        except Exception:
            raise ValueError(f"非法 file_id: {fid}")

        file_record = File.query.get(fid_int)
        if not file_record or getattr(file_record, "deleted_at", None) is not None:
            raise ValueError(f"文件不存在或已删除: {fid_int}")
        if int(getattr(file_record, "user_id")) != int(user_id):
            raise ValueError(f"无权限使用该文件: {fid_int}")

        dfs.append(_read_file_record_to_df(file_record))

    if not dfs:
        raise ValueError("未读取到任何训练文件")

    df_all = pd.concat(dfs, ignore_index=True)

    target_column = getattr(args, "predict_target", None)
    sequence_length = int(getattr(args, "sequence_length", 0) or 0)
    batch_size = int(getattr(args, "batch_size", 0) or 0)
    scaler_type = getattr(args, "scaler_type", "standard")

    if not target_column:
        raise ValueError("缺少 predict_target，无法构建训练数据")
    if target_column not in df_all.columns:
        raise ValueError(f"目标列 '{target_column}' 不存在于选择的数据中")
    if sequence_length <= 0:
        raise ValueError("sequence_length 必须大于 0")
    if batch_size <= 0:
        raise ValueError("batch_size 必须大于 0")

    X_train_val, y_train_val, feature_cols = create_time_series(df_all, target_column, sequence_length)

    # ---- 检测训练文件是否来自预处理目录（已归一化）----
    config = ModelConfig.query.filter_by(user_id=user_id).first()
    already_normalized = False
    if config and config.dad_id:
        dad_dir = Directory.query.get(config.dad_id)
        if dad_dir and dad_dir.parent_id:
            siblings = {d.id for d in Directory.query.filter_by(parent_id=dad_dir.parent_id).all()}
        else:
            siblings = {config.dad_id}
        file_dir_ids = {File.query.get(int(fid)).directory_id for fid in file_ids
                        if File.query.get(int(fid)) is not None}
        if file_dir_ids and file_dir_ids.issubset(siblings):
            already_normalized = True
            print(f"[log]训练文件来自预处理目录，数据已归一化，跳过重复归一化")

    if already_normalized:
        # 数据已归一化，直接使用；加载预处理阶段保存的原始 scaler
        X_normalized = X_train_val
        y_normalized = np.asarray(y_train_val).reshape(-1, 1)
        scaler_X = config.load_pkl('x')
        scaler_y = config.load_pkl('y')
        if scaler_X is None or scaler_y is None:
            raise ValueError("预处理阶段的归一化器未找到，请重新执行预处理步骤")
        print(f"[log]使用预处理阶段的归一化器: scaler_y.mean_={getattr(scaler_y, 'mean_', 'N/A')}")
    else:
        # 原始数据，需要归一化
        if len(X_train_val.shape) == 3:
            X_flat = X_train_val.reshape(-1, X_train_val.shape[-1])
            original_shape = X_train_val.shape
        else:
            X_flat = X_train_val
            original_shape = X_train_val.shape

        if scaler_type == "fixed":
            scaler_X = FixedRangeScaler()
            scaler_y = FixedRangeScaler()
        elif scaler_type == "minmax":
            scaler_X = MinMaxScaler()
            scaler_y = MinMaxScaler()
        elif scaler_type == "standard":
            scaler_X = StandardScaler()
            scaler_y = StandardScaler()
        elif scaler_type == "robust":
            scaler_X = RobustScaler()
            scaler_y = RobustScaler()
        else:
            raise ValueError(f"不支持的归一化器类型: {scaler_type}")

        if isinstance(scaler_X, FixedRangeScaler):
            X_normalized_flat = scaler_X.fit_transform(X_flat, col_names=feature_cols)
            y_normalized = scaler_y.fit_transform(
                np.asarray(y_train_val).reshape(-1, 1), col_names=[target_column]
            )
        else:
            X_normalized_flat = scaler_X.fit_transform(X_flat)
            y_normalized = scaler_y.fit_transform(np.asarray(y_train_val).reshape(-1, 1))
        if len(original_shape) == 3:
            X_normalized = X_normalized_flat.reshape(original_shape)
        else:
            X_normalized = X_normalized_flat

    X_train, X_val, y_train, y_val = split_data(X_normalized, y_normalized)
    train_loader, val_loader = create_data_loaders(X_train, X_val, y_train, y_val, batch_size)

    try:
        if not config:
            config = ModelConfig(user_id=user_id)
            db.session.add(config)

        config.save_pkl("trainloader", train_loader)
        config.save_pkl("valloader", val_loader)
        if not already_normalized:
            # 仅在非预处理数据时覆盖 scaler（保留预处理阶段的原始 scaler）
            config.save_pkl("x", scaler_X)
            config.save_pkl("y", scaler_y)

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return train_loader, val_loader



def parse_int_list(arg):
    return [int(x) for x in arg.split(',')]







import argparse
import pandas as pd
import os
from models import ModelConfig
from exts import db

def parse_int_list(s):
    return [int(i) for i in s.split(',') if i.strip().isdigit()]


def get_parameters(user_id):
    # 修正后的参数信息定义 - 使用嵌套字典结构
    param_info = {
        "model_name": {"value": "Transformer",
                       "choices": "LSTM,GRU,BiLSTM,TCN,Transformer,Transformer_KAN,BP,Autoformer", "help": "选择模型结构"},
        "hidden_size": {"value": 8, "choices": "", "help": "隐藏层维度"},
        "num_layers": {"value": 5, "choices": "", "help": "网络层数"},
        "dropout": {"value": 0.1, "choices": "", "help": "Dropout概率"},
        "grid_size": {"value": 200, "choices": "", "help": "KAN模块的grid大小"},
        "num_channels": {"value": "25,50,25", "choices": "", "help": "TCN中每层通道数"},
        "kernel_size": {"value": 3, "choices": "", "help": "TCN中卷积核大小"},
        "num_heads": {"value": 4, "choices": "", "help": "Transformer多头注意力数"},
        "hidden_space": {"value": 8, "choices": "", "help": "Transformer注意力空间维度"},
        "e_layers": {"value": 2, "choices": "", "help": "Autoformer编码器层数"},
        "d_ff": {"value": 64, "choices": "", "help": "前馈神经网络维度"},
        "moving_avg": {"value": 24, "choices": "", "help": "Autoformer滑动平均窗口大小"},
        "factor": {"value": 4, "choices": "", "help": "AutoCorrelation的top-k因子"},
        "activation": {"value": "tanh", "choices": "relu,leaky_relu,elu,gelu,sigmoid,tanh,softplus,silu,none",
                       "help": "激活函数"},
        "use_layer_norm": {"value": False, "choices": "True,False", "help": "是否使用LayerNorm"},
        "seq_len": {"value": 64, "choices": "", "help": "输入序列长度"},
        "num_epochs": {"value": 150, "choices": "", "help": "训练轮数"},
        "learning_rate": {"value": 0.0005, "choices": "", "help": "学习率"},
        "input_directory": {"value": "data_save/5口井新数据", "choices": "", "help": "输入数据目录"},
        "predict_target": {"value": "RD", "choices": "", "help": "预测目标列"},
        "input_size": {"value": 15, "choices": "", "help": "输入特征维度"},
        "batch_size": {"value": 1024, "choices": "", "help": "批次大小"},
        "output_size": {"value": 1, "choices": "", "help": "输出特征维度"},
        "sequence_length": {"value": 64, "choices": "", "help": "序列长度"},
        "scaler_type": {"value": "standard", "choices": "fixed,minmax,standard,robust", "help": "归一化器类型（fixed=固定物理范围）"},
        "loss": {"value": "mae", "choices": "mse,mae,huber,smooth_l1,log_cosh,quantile,mape,smape",
                 "help": "回归任务损失函数类型"},

        # 物理 loss 相关参数
        "phy_equation": {"value": "", "choices": "", "help": "知识约束表达式，例如 'x0 + x1 - x2 * y = 0'"},
        "phy_loss_type": {"value": "mse", "choices": "mse,mae", "help": "物理loss类型"},
        "phy_loss_weight": {"value": 0.0, "choices": "", "help": "物理loss加权系数 beta"},
        "phy_loss_lower": {"value": 0.0, "choices": "", "help": "物理loss表达式的下边界"},
        "phy_loss_upper": {"value": 0.0, "choices": "", "help": "物理loss表达式的上边界"},
    }

    config = ModelConfig.query.filter_by(user_id=user_id).first()




    # 读取并更新 value_dict
    value_dict = {}
    for column in ModelConfig.__table__.columns:
        # 跳过不需要的字段
        if column.name in ['user_id', 'updated_at']:
            continue

        key = column.name
        val = getattr(config, key)

        # 特殊处理num_channels字段
        if key == 'num_channels':
            value_dict[key] = [int(x) for x in val.split(',')] if val else []
            continue

        # 布尔类型字段处理
        if column.type.python_type == bool:
            value_dict[key] = bool(val)
        # 整数字段处理
        elif isinstance(val, int) or (isinstance(val, str) and val.isdigit()):
            value_dict[key] = int(val)
        # 浮点数字段处理
        elif isinstance(val, float):
            value_dict[key] = float(val)
        # 尝试转换为浮点数
        else:
            try:
                value_dict[key] = float(val)
            except (ValueError, TypeError):
                value_dict[key] = str(val)

    # 构建 argparse 对象
    parser = argparse.ArgumentParser(description='训练模型的脚本')
    for name, val in value_dict.items():
        # 获取参数元信息
        info = param_info.get(name, {})
        choices = info.get("choices")
        help_str = info.get("help", "")

        # 特殊处理布尔参数
        if name == "use_layer_norm":
            parser.add_argument(f'--{name}',
                                action='store_true' if val else 'store_false',
                                help=help_str)
        # 处理num_channels列表
        elif name == "num_channels":
            parser.add_argument(f'--{name}',
                                type=lambda s: [int(x) for x in s.split(',')],
                                default=val,
                                help=help_str)
        # 处理有选择项的参数
        elif choices:
            choices_list = [c.strip() for c in choices.split(",")]
            parser.add_argument(f'--{name}',
                                type=type(val),
                                default=val,
                                choices=choices_list,
                                help=help_str)
        # 其他普通参数
        else:
            parser.add_argument(f'--{name}',
                                type=type(val),
                                default=val,
                                help=help_str)

    args, _ = parser.parse_known_args()
    return args


