"""
文件路径工具：统一使用相对路径存储，解决跨机器迁移问题。

数据库中 file.content 存储相对于 backend/ 目录的路径，如:
    uploads/3/file_abc123.las

读取文件时通过 resolve_content_path() 还原为绝对路径。
"""
import os
from flask import current_app


def resolve_content_path(content: str | None) -> str | None:
    """将数据库中存储的路径解析为磁盘绝对路径。

    兼容逻辑：
    1. 空值 → None
    2. 相对路径 → 拼接 current_app.root_path
    3. 绝对路径且文件存在 → 直接返回（兼容旧数据）
    4. 绝对路径但文件不存在 → 尝试提取 uploads/ 之后的相对部分再拼接
    """
    if not content:
        return None

    # 相对路径：直接拼接
    if not os.path.isabs(content):
        return os.path.join(current_app.root_path, content)

    # 绝对路径且存在：直接用
    if os.path.exists(content):
        return content

    # 绝对路径但不存在：尝试提取 uploads/ 之后的部分
    normalized = content.replace("\\", "/")
    marker = "uploads/"
    idx = normalized.find(marker)
    if idx != -1:
        relative = normalized[idx:]  # e.g. "uploads/3/file.las"
        candidate = os.path.join(current_app.root_path, relative)
        if os.path.exists(candidate):
            return candidate

    return None


def to_relative_content_path(abs_path: str) -> str:
    """将绝对路径转为相对于 current_app.root_path 的相对路径。"""
    root = current_app.root_path.replace("\\", "/").rstrip("/") + "/"
    normalized = abs_path.replace("\\", "/")
    if normalized.startswith(root):
        return normalized[len(root):]

    # 兜底：提取 uploads/ 之后的部分
    marker = "uploads/"
    idx = normalized.find(marker)
    if idx != -1:
        return normalized[idx:]

    # 实在无法转换，返回原路径
    return abs_path
