import os

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np



# def plot_results(true_values, predicted_values, save_path, depth, args):
#     """
#     绘制真实值和预测值的散点图和曲线图，并保存到指定路径。
#
#     Parameters:
#     true_values (array-like): 真实值
#     predicted_values (array-like): 预测值
#     save_path (str): 保存结果的文件路径
#     """
#
#     depth, true_values = inverse_normalize_and_load(np.array(depth), true_values, scaler_dir=os.path.join('data_save', '本次数据读取的缓存', args.input_directory), args=args)
#     _, predicted_values = inverse_normalize_and_load(np.array(depth), predicted_values, scaler_dir=os.path.join('data_save', '本次数据读取的缓存', args.input_directory), args=args)
#
#     # 配置字体
#     mpl.rcParams['font.family'] = 'Times New Roman'
#     mpl.rcParams['font.serif'] = ['Times New Roman']
#
#     # 确保输入为 numpy 数组
#     true_values = np.array(true_values)
#     predicted_values = np.array(predicted_values)
#
#     # 创建图形和子图
#     fig, axs = plt.subplots(1, 2, figsize=(16, 6), dpi=100)
#
#     # 散点图
#     axs[0].scatter(true_values, predicted_values, alpha=0.7, edgecolors='k', s=50, c='blue', marker='o')
#     axs[0].plot([true_values.min(), true_values.max()], [true_values.min(), true_values.max()], 'r--', lw=2)
#     axs[0].set_xlabel('True Values', fontsize=14)
#     axs[0].set_ylabel('Predicted Values', fontsize=14)
#     axs[0].set_title('Scatter Plot', fontsize=16)
#     axs[0].grid(True, linestyle='--', alpha=0.7)
#     axs[0].set_aspect('equal', adjustable='box')  # 保持x轴和y轴的比例
#
#     # 曲线图
#     axs[1].plot(depth, true_values, label='True Values', color='blue', linewidth=1)
#     axs[1].plot(depth, predicted_values, label='Predicted Values', color='red', linewidth=0.5)
#     axs[1].set_xlabel('Depth/m', fontsize=14)
#     axs[1].set_ylabel('Values', fontsize=14)
#     axs[1].set_title('Line Plot', fontsize=16)
#     axs[1].legend()
#     axs[1].grid(True, linestyle='--', alpha=0.7)
#
#     # 调整布局
#     plt.tight_layout()
#
#     # 保存图像
#     plt.savefig(save_path, bbox_inches='tight', pad_inches=0.1)
#     plt.close()
#     # print(f"图像已保存到 {save_path}")

import matplotlib.gridspec as gridspec

from tools.tool_for_pre import inverse_normalize_and_load


def plot_results(true_values, predicted_values, save_path, depth, args, predict_mode=False, already_denormalized=False):
    """
    绘制预测结果的折线图与散点图（测试模式）。
    预测模式下仅绘制预测值；测试模式下绘制预测值与真值对比。
    支持坐标轴斜体标签、美观布局与科学计数关闭。
    """
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    import numpy as np
    import os
    from matplotlib.ticker import ScalarFormatter

    # 获取 scaler 路径
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scaler_dir = os.path.join(parent_dir, "data_save", "本次数据读取的缓存", args.input_directory)
    scaler_dir = scaler_dir.replace("/", "\\")

    # 反归一化
    if not already_denormalized:
        _, true_values = inverse_normalize_and_load(np.array(depth), true_values, scaler_dir=scaler_dir, args=args)
        _, predicted_values = inverse_normalize_and_load(np.array(depth), predicted_values, scaler_dir=scaler_dir, args=args)
    true_values = np.array(true_values)
    predicted_values = np.array(predicted_values)
    print(f"✅ predicted_values 范围: {predicted_values.min()} ~ {predicted_values.max()}")

    # 设置全局字体
    mpl.rcParams['font.family'] = 'Times New Roman'
    mpl.rcParams['font.serif'] = ['Times New Roman']
    mpl.rcParams['axes.titlesize'] = 26
    mpl.rcParams['axes.labelsize'] = 22
    mpl.rcParams['xtick.labelsize'] = 18
    mpl.rcParams['ytick.labelsize'] = 18
    mpl.rcParams['legend.fontsize'] = 20

    # =====================
    # 折线图 Line Plot
    # =====================
    fig, ax = plt.subplots(figsize=(6, 25))  # 更宽些，美观

    if not predict_mode and not np.isnan(true_values).all():
        ax.plot(true_values, depth, color='blue', linewidth=4, label='True Values')

    ax.plot(predicted_values, depth, color='red', linewidth=3,
            label='Predicted Values' if not predict_mode else None)

    ax.invert_yaxis()
    ax.set_xlabel(args.predict_target, labelpad=10)
    ax.set_ylabel('Depth (m)', labelpad=10)
    ax.grid(True, linestyle='--', alpha=0.7)

    # 坐标轴位置与旋转设置
    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()
    ax.tick_params(axis='x', which='major', rotation=45, direction='inout', length=6, width=1.2)
    ax.tick_params(axis='y', which='major', rotation=45, direction='inout', length=6, width=1.2)

    # ✅ 禁用科学计数法
    ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style='plain', axis='x', useOffset=False)
    ax.xaxis.get_offset_text().set_visible(False)
    # 设置坐标轴格式为普通数字
    ax.xaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    ax.xaxis.get_major_formatter().set_scientific(False)

    # 图例
    if not predict_mode:
        fig.legend(
            loc='upper center',
            bbox_to_anchor=(0.6, 1.03),
            ncol=1,
            frameon=False
        )

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    line_save_path = save_path.replace('.png', '_line.png')
    plt.savefig(line_save_path, dpi=300, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    print(f"✅ 保存折线图: {line_save_path}")

    # =====================
    # 散点图 Scatter Plot（仅测试模式）
    # =====================
    if not predict_mode and not np.isnan(true_values).all():
        plt.figure(figsize=(6, 6))
        plt.scatter(true_values, predicted_values, alpha=0.7, edgecolors='k', s=60, c='green', marker='o')

        min_val = min(true_values.min(), predicted_values.min())
        max_val = max(true_values.max(), predicted_values.max())
        plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)

        plt.xlabel('True Values', labelpad=10)
        plt.ylabel('Predicted Values', labelpad=10)
        plt.grid(True, linestyle='--', alpha=0.7)

        plt.xticks(rotation=45)
        plt.yticks(rotation=45)

        plt.tight_layout()
        scatter_save_path = save_path.replace('.png', '_scatter.png')
        plt.savefig(scatter_save_path, dpi=300, bbox_inches='tight', pad_inches=0.1)
        plt.close()
        print(f"✅ 保存散点图: {scatter_save_path}")