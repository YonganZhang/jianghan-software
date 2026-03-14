import os
from datetime import datetime
import threading
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 强制使用非交互后端，避免 GUI 后端干扰 CUDA
import torch
from matplotlib import pyplot as plt
import matplotlib as mpl
from torch import optim
import shutil
from models import Trainmodel, ModelConfig, Lossimagemodel, Trainingparameters
from exts import db
from io import BytesIO


class TrainingAborted(Exception):
    pass


_abort_flags = {}
_abort_lock = threading.Lock()


def set_abort_flag(user_id):
    if user_id is None:
        return
    with _abort_lock:
        _abort_flags[int(user_id)] = True


def clear_abort_flag(user_id):
    if user_id is None:
        return
    with _abort_lock:
        _abort_flags[int(user_id)] = False


def check_abort_flag(user_id):
    if user_id is None:
        return False
    with _abort_lock:
        return bool(_abort_flags.get(int(user_id), False))


def copy_config_to_training_params(model_config):
    """将ModelConfig的值复制到Trainingparameters实例"""
    training_params = Trainingparameters()

    # 复制所有共有的字段
    training_params.model_name = model_config.model_name
    training_params.hidden_size = model_config.hidden_size
    training_params.num_layers = model_config.num_layers
    training_params.dropout = model_config.dropout
    training_params.grid_size = model_config.grid_size
    training_params.num_channels = model_config.num_channels
    training_params.kernel_size = model_config.kernel_size
    training_params.num_heads = model_config.num_heads
    training_params.hidden_space = model_config.hidden_space
    training_params.e_layers = model_config.e_layers
    training_params.d_ff = model_config.d_ff
    training_params.moving_avg = model_config.moving_avg
    training_params.factor = model_config.factor
    training_params.activation = model_config.activation
    training_params.use_layer_norm = model_config.use_layer_norm
    training_params.num_epochs = model_config.num_epochs
    training_params.learning_rate = model_config.learning_rate
    training_params.loss = model_config.loss

    return training_params









def save_and_move_model_folder(model, save_path, file_name):
    # 解析路径
    save_dir = os.path.dirname(save_path)  # 原本想存的 Transformer_KAN--26--20--27--50 目录
    parent_dir = os.path.dirname(save_dir)  # 应该是 models_save/套后数据

    # Step 1: 先在 models_save/Transformer_KAN--26--20--27--50/ 保存模型
    file_save_path = os.path.join(parent_dir, file_name)
    torch.save(model.state_dict(), file_save_path)
    # print(f"✅ 模型先保存到了临时目录: {parent_dir}")

    # Step 2: 再把整个 Transformer_KAN--26--20--27--50 文件夹剪切到 models_save/套后数据/
    final_target_dir = save_path
    os.makedirs(parent_dir, exist_ok=True)  # 确保 models_save/套后数据/ 目录存在

    shutil.move(file_save_path, final_target_dir)
    # print(f"✅ 成功剪切整个文件夹到最终目录: {final_target_dir}")


def train_model(model, train_loader, val_loader, criterion, phy_loss_fn, optimizer, num_epochs, device, args, userid):
    # 获取用户的ModelConfig
    model_config = ModelConfig.query.filter_by(user_id=userid).first()
    if not model_config:
        raise ValueError(f"用户 {userid} 没有模型配置记录")

    # 加载目标列归一化器，用于将拟合图数据反归一化为原始尺度
    # scaler_y 在预处理阶段通过 config.save_pkl('y', scaler_y) 保存
    try:
        scaler_y_for_plot = model_config.load_pkl('y')
    except Exception:
        scaler_y_for_plot = None  # 加载失败时拟合图仍显示归一化值

    # 创建Trainingparameters实例并赋值
    training_params = copy_config_to_training_params(model_config)

    # 添加到数据库
    db.session.add(training_params)
    db.session.commit()

    base_batch = model_config.number or 0
    numberr = base_batch + 1
    model_config.number = numberr
    db.session.add(model_config)
    db.session.commit()
    # 1. 训练开始时，创建一个关联当前参数的Trainmodel（初始为空）
    best_train_model = Trainmodel(
        user_id=userid,
        batch_number=numberr,
        training_params=training_params  # 关联当前训练参数
    )
    db.session.add(best_train_model)
    db.session.commit()  # 先保存到数据库，获得记录ID
    zb1 = []
    zb2 = []
    zb3 = []
    zb4 = []
    zb5 = []
    zb6 = []

    train_losses = []
    val_losses = []
    train_data_losses, train_phy_losses = [], []
    val_data_losses, val_phy_losses = [], []
    print("------开始训练------")
    # 使用 ReduceLROnPlateau 调度器
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.9, patience=10, verbose=True)
    # 求一下路径
    parts = os.path.normpath(args.input_directory).split(os.sep)
    second_last_folder = parts[-1]

    min_val_loss = float('inf')
    # 拟合图推送频率：总 epoch 少时每轮推，多时降频，最多约 100 次
    fit_interval = max(1, num_epochs // 100)
    for epoch in range(num_epochs):
        if check_abort_flag(userid):
            raise TrainingAborted("训练已中止")
        model.train()
        total_train_loss = 0
        total_train_data_loss = 0
        total_train_phy_loss = 0
        for inputs, targets in train_loader:
            if check_abort_flag(userid):
                raise TrainingAborted("训练已中止")
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)

            loss_data = criterion(outputs, targets.squeeze())

            if phy_loss_fn is not None and args.phy_loss_weight > 0:
                loss_phy = phy_loss_fn(inputs, outputs)
                loss = loss_data + args.phy_loss_weight * loss_phy
            else:
                loss_phy = torch.tensor(0.0, device=device)
                loss = loss_data

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_train_loss += loss.item()
            total_train_data_loss += loss_data.item()
            total_train_phy_loss += loss_phy.item()


        avg_train_loss = total_train_loss / len(train_loader)
        avg_train_data_loss = total_train_data_loss / len(train_loader)
        avg_train_phy_loss = total_train_phy_loss / len(train_loader)
        train_losses.append(avg_train_loss)
        train_data_losses.append(avg_train_data_loss)
        train_phy_losses.append(avg_train_phy_loss)
        # -------------------- 验证阶段 --------------------
        model.eval()
        total_val_loss = 0
        total_val_data_loss = 0
        total_val_phy_loss = 0

        with torch.no_grad():
            for inputs, targets in val_loader:
                if check_abort_flag(userid):
                    raise TrainingAborted("训练已中止")
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs)

                loss_data = criterion(outputs, targets.squeeze())
                if phy_loss_fn is not None and args.phy_loss_weight > 0:
                    loss_phy = phy_loss_fn(inputs, outputs)
                    loss = loss_data + args.phy_loss_weight * loss_phy
                else:
                    loss_phy = torch.tensor(0.0, device=device)
                    loss = loss_data

                total_val_loss += loss.item()
                total_val_data_loss += loss_data.item()
                total_val_phy_loss += loss_phy.item()
        # todo 保存最小--------------------------------------------------------------------------------------------------------------
        avg_val_loss = total_val_loss / len(val_loader)

        if avg_val_loss < min_val_loss:
            min_val_loss = avg_val_loss  # 更新最小损失值
            cur_time = datetime.now()
            format_time = cur_time.strftime("%Y%m%d_%H%M%S")
            # 关键：先同步 CUDA，再将 state_dict 拷贝到 CPU
            # 避免 pickle.dump 序列化 GPU 张量时触发 "invalid resource handle"
            if device.type == 'cuda':
                torch.cuda.synchronize()
            model_data = {k: v.cpu() for k, v in model.state_dict().items()}

            # todo -----------------------------------------------------------------保存损失图
            # 配置字体
            mpl.rcParams['font.family'] = 'Times New Roman'
            mpl.rcParams['font.serif'] = ['Times New Roman']
            mpl.rcParams['axes.titlesize'] = 20
            mpl.rcParams['axes.labelsize'] = 16
            mpl.rcParams['xtick.labelsize'] = 14
            mpl.rcParams['ytick.labelsize'] = 14
            mpl.rcParams['legend.fontsize'] = 14

            # 创建图像（截至当前epoch的损失曲线）
            plt.figure(figsize=(10, 6))
            # 训练损失曲线（蓝色）
            plt.plot(range(1, len(train_losses) + 1), train_losses,
                     label='Training Loss', color='blue', linestyle='-', marker='o')
            # 验证损失曲线（红色）
            plt.plot(range(1, len(val_losses) + 1), val_losses,
                     label='Validation Loss', color='red', linestyle='-', marker='o')

            # 标记当前最佳模型的位置（可选）
            plt.scatter([epoch + 1], [min_val_loss], color='green', s=100, zorder=5,
                        label=f'Best Val Loss: {min_val_loss:.4f}')

            # 坐标轴与标题设置
            plt.xlabel('Epoch')  # 横坐标
            plt.ylabel('Loss')  # 纵坐标
            plt.title(f'Training and Validation Loss (Best Model at Epoch {epoch + 1})')
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.7)

            # 保存图像到内存缓冲区
            buffer_best = BytesIO()
            plt.savefig(buffer_best, format='png', bbox_inches='tight', dpi=100)
            buffer_best.seek(0)
            best_loss_image_binary = buffer_best.getvalue()
            plt.close()
            # todo -----------------------------------------------------------------保存损失图

            # 2. 更新已有的best_train_model，而不是新建
            best_train_model.file_name = f'best_model_{format_time}.pth'
            best_train_model.avg_val_loss = str(avg_val_loss)
            best_train_model.avg_train_loss = str(avg_train_loss)
            best_train_model.filepicture_name = f'best_loss_epoch_{epoch + 1}.png'

            # 更新文件（会覆盖旧文件路径）
            best_train_model.save_trainepoch(model_data)
            best_train_model.save_picture(best_loss_image_binary)

            db.session.commit()  # 提交更新
            print(f"[log]已更新最佳模型: {avg_val_loss:.4f}")


        avg_val_data_loss = total_val_data_loss / len(val_loader)
        avg_val_phy_loss = total_val_phy_loss / len(val_loader)

        val_losses.append(avg_val_loss)
        val_data_losses.append(avg_val_data_loss)
        val_phy_losses.append(avg_val_phy_loss)

        scheduler.step(avg_val_loss)
        print(f'[log]Epoch [{epoch + 1}/{num_epochs}] '
              f'Train: Total {avg_train_loss:.4f} | Data {avg_train_data_loss:.4f} | Phy {avg_train_phy_loss:.4f} || '
              f'Val: Total {avg_val_loss:.4f} | Data {avg_val_data_loss:.4f} | Phy {avg_val_phy_loss:.4f}')

        print(f"[trainloss1]{{[{epoch + 1}, {avg_train_loss}]}}")
        print(f"[trainloss2]{{[{epoch + 1}, {avg_train_data_loss}]}}")
        print(f"[trainloss3]{{[{epoch + 1}, {avg_train_phy_loss}]}}")
        print(f"[trainloss4]{{[{epoch + 1}, {avg_val_loss}]}}")
        print(f"[trainloss5]{{[{epoch + 1}, {avg_val_data_loss}]}}")
        print(f"[trainloss6]{{[{epoch + 1}, {avg_val_phy_loss}]}}")


        # todo---------------------------------------------------------------------------------------------------------------------------------------------
        if (epoch + 1) % 25 == 0:
            zb1.append([epoch + 1, avg_train_loss])
            zb2.append([epoch + 1, avg_train_data_loss])
            zb3.append([epoch + 1, avg_train_phy_loss])
            zb4.append([epoch + 1, avg_val_loss])
            zb5.append([epoch + 1, avg_val_data_loss])
            zb6.append([epoch + 1, avg_val_phy_loss])

        # ---- 拟合图数据推送（自适应频率）----
        # 避免前端内存爆炸导致浏览器崩溃
        if (epoch + 1) % fit_interval == 0 or (epoch + 1) == num_epochs:
            model.eval()
            inputs_train, targets_train = next(iter(train_loader))
            inputs_train, targets_train = inputs_train.to(device), targets_train.to(device)
            with torch.no_grad():
                outputs_train = model(inputs_train)

            max_len = min(targets_train.shape[0], 50)
            y_true_train = targets_train[0:max_len].detach().cpu().numpy().flatten()
            y_pred_train = outputs_train[0:max_len].detach().cpu().numpy().flatten()

            # 取一个验证样本
            inputs_val, targets_val = next(iter(val_loader))
            inputs_val, targets_val = inputs_val.to(device), targets_val.to(device)
            with torch.no_grad():
                outputs_val = model(inputs_val)

            y_true_val = targets_val[0:max_len].detach().cpu().numpy().flatten()
            y_pred_val = outputs_val[0:max_len].detach().cpu().numpy().flatten()

            # 显式释放 GPU 张量引用，减少显存占用
            del inputs_train, targets_train, outputs_train
            del inputs_val, targets_val, outputs_val

            # ---- 反归一化：将模型输出从标准化空间还原为原始物理量纲 ----
            # 训练/验证数据来自 DataLoader（已归一化），模型输出也在归一化空间
            # 前端拟合图需要展示原始尺度，因此用 scaler_y 做 inverse_transform
            if scaler_y_for_plot is not None:
                y_true_train = scaler_y_for_plot.inverse_transform(
                    y_true_train.reshape(-1, 1)).flatten()
                y_pred_train = scaler_y_for_plot.inverse_transform(
                    y_pred_train.reshape(-1, 1)).flatten()
                y_true_val = scaler_y_for_plot.inverse_transform(
                    y_true_val.reshape(-1, 1)).flatten()
                y_pred_val = scaler_y_for_plot.inverse_transform(
                    y_pred_val.reshape(-1, 1)).flatten()

            formatted_list = [[float(value), idx] for idx, value in enumerate(y_true_train)]
            formatted_list1 = [[float(value), idx] for idx, value in enumerate(y_pred_train)]
            formatted_list2 = [[float(value), idx] for idx, value in enumerate(y_true_val)]
            formatted_list3 = [[float(value), idx] for idx, value in enumerate(y_pred_val)]

            # 格式化输出，确保前端接收正确格式
            print(f"[tuyilan]{formatted_list}")
            print(f"[tuyihong]{formatted_list1}")
            print(f"[tuerlan]{formatted_list2}")
            print(f"[tuerhong]{formatted_list3}")


    print("------训练完成------")
    # kk = Coordinate(
    #     user_id = userid,
    #     fc1 = zb1,
    #     fc2 = zb2,
    #     fc3 = zb3,
    #     fc4 = zb4,
    #     fc5 = zb5,
    #     fc6 = zb6,
    #     loss_number=numberr)
    # db.session.add(kk)
    # db.session.commit()



    # todo 最终保存模型
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y%m%d_%H%M%S")
    # 同步 CUDA 并将 state_dict 拷贝到 CPU，避免序列化 GPU 张量
    if device.type == 'cuda':
        torch.cuda.synchronize()
    final_model_data = {k: v.cpu() for k, v in model.state_dict().items()}

    # 配置字体
    mpl.rcParams['font.family'] = 'Times New Roman'
    mpl.rcParams['font.serif'] = ['Times New Roman']
    mpl.rcParams['axes.titlesize'] = 20  # 图标题字体大小
    mpl.rcParams['axes.labelsize'] = 16  # x轴、y轴标签字体大小
    mpl.rcParams['xtick.labelsize'] = 14  # x轴刻度字体大小
    mpl.rcParams['ytick.labelsize'] = 14  # y轴刻度字体大小
    mpl.rcParams['legend.fontsize'] = 14  # 图例字体大小

    # 创建图像
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, num_epochs + 1), train_losses, label='Training Loss', color='blue', linestyle='-', marker='o')
    plt.plot(range(1, num_epochs + 1), val_losses, label='Validation Loss', color='red', linestyle='-', marker='o')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    plt.grid(True)

    # 将图像保存到内存缓冲区（二进制数据）
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    buffer.seek(0)  # 将指针移回缓冲区的开头
    train_coordinates = [[epoch, loss] for epoch, loss in zip(range(1, num_epochs + 1), train_losses)]
    # 验证损失坐标
    val_coordinates = [[epoch, loss] for epoch, loss in zip(range(1, num_epochs + 1), val_losses)]
    zxl_loss = train_losses[-1]
    zyz_loss = val_losses[-1]
    loss_image_binary = buffer.getvalue()
    plt.close()  # 释放 matplotlib 图像资源

    # 1. 创建Lossimagemodel实例（不直接传二进制数据）
    PP = Lossimagemodel(
        user_id=userid,
        file_name='loss_plot.png',
        trainname=f'epoch_last_{formatted_time}.pth',
        batch_number=numberr,
        zxl_loss=str(zxl_loss),
        zyz_loss=str(zyz_loss),
        training_params = training_params
    )

    # 2. 调用方法保存文件并记录路径
    PP.save_image(loss_image_binary)  # 保存损失图到文件，自动更新file_path
    PP.save_trainepoch(final_model_data)  # 保存模型数据到文件，自动更新trainepoch_path

    # 3. 提交到数据库
    db.session.add(PP)
    db.session.commit()
    print(f"模型和损失图已经保存到数据库")
    return train_coordinates, val_coordinates
