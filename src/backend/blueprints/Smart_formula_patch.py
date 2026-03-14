# 这是一个补丁文件，用于修复文件复制权限问题
import os
import shutil
import time

def safe_copy_file(src_path, dst_path, max_retries=3):
    """
    安全地复制文件，处理权限和占用问题
    
    Args:
        src_path: 源文件路径
        dst_path: 目标文件路径
        max_retries: 最大重试次数
    
    Returns:
        bool: 是否成功
    
    Raises:
        Exception: 复制失败时抛出异常
    """
    # 如果目标文件存在，先尝试删除
    if os.path.exists(dst_path):
        for retry in range(max_retries):
            try:
                # 尝试删除旧文件
                os.remove(dst_path)
                break
            except PermissionError:
                if retry < max_retries - 1:
                    # 等待一小段时间后重试
                    time.sleep(0.5)
                else:
                    # 如果删除失败，尝试使用临时文件名
                    timestamp = int(time.time() * 1000)
                    dst_path = f"{dst_path}.{timestamp}.tmp"
    
    # 复制文件
    for retry in range(max_retries):
        try:
            shutil.copy2(src_path, dst_path)
            return True
        except PermissionError as e:
            if retry < max_retries - 1:
                time.sleep(0.5)
            else:
                raise Exception(f"文件复制失败，权限被拒绝: {str(e)}")
        except Exception as e:
            raise Exception(f"文件复制失败: {str(e)}")
    
    return False
