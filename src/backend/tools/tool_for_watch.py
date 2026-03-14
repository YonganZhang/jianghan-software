import matplotlib
matplotlib.use('Agg')  # 强制使用非交互后端，避免 GUI 后端干扰 CUDA
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.ticker import ScalarFormatter
import numpy as np
from io import BytesIO

def plot_fit_comparison(y_true, y_pred, title, max_len=500):
    """
    纵向可视化预测与真实值对比（一个样本），返回图片的二进制数据
    """
    # 限制长度
    length = min(len(y_true), len(y_pred), max_len)
    y_true = np.array(y_true[:length])
    y_pred = np.array(y_pred[:length])

    # 设置全局字体样式
    mpl.rcParams['font.family'] = 'Times New Roman'
    mpl.rcParams['font.serif'] = ['Times New Roman']
    mpl.rcParams['axes.titlesize'] = 22
    mpl.rcParams['axes.labelsize'] = 18
    mpl.rcParams['xtick.labelsize'] = 14
    mpl.rcParams['ytick.labelsize'] = 14
    mpl.rcParams['legend.fontsize'] = 16

    # 竖向折线图（深度/时间步在 Y 轴）
    fig, ax = plt.subplots(figsize=(5, 10))  # 宽度小，高度大（竖向）

    ax.plot(y_true, range(length), color='blue', linewidth=2, marker='o', label='True')
    ax.plot(y_pred, range(length), color='red', linewidth=2, marker='x', label='Predicted')

    ax.invert_yaxis()
    ax.set_xlabel('Value', labelpad=8)
    ax.set_ylabel('Time Step', labelpad=8)
    ax.set_title(title)
    ax.grid(True, linestyle='--', alpha=0.7)

    # 横轴格式优化
    ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style='plain', axis='x', useOffset=False)
    ax.xaxis.get_offset_text().set_visible(False)

    # 美观设置
    ax.tick_params(axis='x', direction='inout', length=5, width=1.2)
    ax.tick_params(axis='y', direction='inout', length=5, width=1.2)
    ax.legend(loc='lower right')

    plt.tight_layout()

    # 关键修改：用 BytesIO 在内存中存储图片二进制数据
    img_buffer = BytesIO()  # 创建内存二进制流
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', pad_inches=0.1)
    img_buffer.seek(0)  # 将指针移到流的开头，以便读取
    img_binary_data = img_buffer.read()  # 读取二进制数据到变量

    # 清理资源
    plt.close()
    img_buffer.close()

    return title, img_binary_data  # 返回图片的二进制数据       from exts import db

