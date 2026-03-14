import torch

# 构造物理 loss 函数
import torch

import os
import pickle
import torch

def build_physical_loss_from_equation(args):
    """
    构建带物理上下边界约束的 loss 函数，支持归一化边界。
    支持表达式如：x0 + x1**2 - x2 - y = 0 或 x0 + y**2
    变量支持：x0, x1, ..., y, dy_dx, d2y_dx2
    """
    equation = str(args.phy_equation)
    loss_type = str(args.phy_loss_type).lower()
    lower_bound_raw = float(getattr(args, "phy_loss_lower", 0.0))
    upper_bound_raw = float(getattr(args, "phy_loss_upper", 0.0))

    # 读取 scaler_y 进行归一化
    scaler_dir = os.path.join("data_save/本次数据读取的缓存", args.input_directory)
    try:
        with open(os.path.join(scaler_dir, "scaler_y.pkl"), "rb") as f:
            scaler_y = pickle.load(f)
        lower_bound = float(scaler_y.transform([[lower_bound_raw]])[0][0])
        upper_bound = float(scaler_y.transform([[upper_bound_raw]])[0][0])
    except Exception as e:
        print(f"⚠️ 无法加载 scaler_y，使用原始边界值: {e}")
        lower_bound = lower_bound_raw
        upper_bound = upper_bound_raw

    # 提取表达式左边（例如 "x0 + x1 - y"）
    if '=' in equation:
        expr = equation.split('=')[0].strip()
    else:
        expr = equation.strip()

    print_once = True  # 仅首次打印

    def physical_loss(x, y_pred, return_lhs=False):
        nonlocal print_once

        x = x.requires_grad_(True)
        x = x[:, -1, :].requires_grad_(True)  # 取每个样本最后一个时间步的输入
        y = y_pred.squeeze(-1).requires_grad_(True)

        # ✅ 首次打印信息
        if print_once:
            print(f"📘 设置的物理约束表达式: {expr}")
            print(f"🔢 真实边界: lower={lower_bound_raw}, upper={upper_bound_raw}")
            print(f"📐 归一化边界: lower={lower_bound:.4f}, upper={upper_bound:.4f}")
            print_once = False

        # 🔐 安全处理无效表达式
        if expr.lower() in ["", "nan", "none"] or expr.strip() == "":
            lhs = y  # 默认将预测值 y 作为被约束目标

            if upper_bound == lower_bound:
                error = lhs - lower_bound
            else:
                error = torch.where(lhs < lower_bound, lhs - lower_bound,
                                    torch.where(lhs > upper_bound, lhs - upper_bound,
                                                torch.zeros_like(lhs)))

            if return_lhs:
                return lhs

            if loss_type == "mse":
                return (error ** 2).mean()
            elif loss_type == "mae":
                return error.abs().mean()
            else:
                raise NotImplementedError(f"未知物理loss类型: {loss_type}")

        local_dict = {
            **{f"x{i}": x[:, i] for i in range(x.shape[1])},
            "y": y
        }

        # 衍生导数项
        try:
            dy_dx = torch.autograd.grad(
                y, x, grad_outputs=torch.ones_like(y), create_graph=True, retain_graph=True
            )[0]
            local_dict["dy_dx"] = dy_dx[:, 0]

            d2y_dx2 = torch.autograd.grad(
                dy_dx[:, 0], x, grad_outputs=torch.ones_like(dy_dx[:, 0]), create_graph=True, retain_graph=True
            )[0]
            local_dict["d2y_dx2"] = d2y_dx2[:, 0]
        except:
            local_dict["dy_dx"] = torch.zeros_like(y)
            local_dict["d2y_dx2"] = torch.zeros_like(y)

        try:
            lhs = eval(expr, {"torch": torch}, local_dict)
        except Exception as e:
            raise ValueError(f"❌ 无法解析表达式 `{expr}`：{e}")

        if return_lhs:
            return lhs

        # ✅ 区间误差计算
        if upper_bound == lower_bound:
            error = lhs - lower_bound
        else:
            error = torch.where(lhs < lower_bound, lhs - lower_bound,
                                torch.where(lhs > upper_bound, lhs - upper_bound,
                                            torch.zeros_like(lhs)))  # 在范围内则误差为 0

        # ✅ 使用 error 作为最终 loss 的输入
        if loss_type == "mse":
            return (error ** 2).mean()
        elif loss_type == "mae":
            return error.abs().mean()
        else:
            raise NotImplementedError(f"未知物理loss类型: {loss_type}")

    return physical_loss




import torch
from types import SimpleNamespace

def debug_physical_loss():
    # 构造 toy 数据
    x = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]])  # 共6列
    y = torch.tensor([[12.5]])  # 满足：6 + 5² - 3*2 - 2*26 = 0

    # 构造一个假的 args
    args = SimpleNamespace()
    args.phy_equation = "x5 + x4**2 - x2*x1 - 2*y = 0"
    args.phy_loss_type = "mse"
    args.phy_loss_weight = 1.0


    print("📌 设置的物理公式:")
    print(f"    {args.phy_equation}")



    phy_loss_fn = build_physical_loss_from_equation(args)

    # ✅ 1. 正确y输入
    lhs = phy_loss_fn(x, y, return_lhs=True)
    loss_val = phy_loss_fn(x, y)

    print("\n✅ 正确构造的样本:")
    print(f"x = {x.detach().numpy()}")
    print(f"y = {y.detach().numpy()}")
    print(f"→ 公式左侧表达式值: {lhs.detach().numpy()}")
    print(f"→ 最终loss值: {loss_val.item():.8f}")

    # ✅ 2. 错误y输入
    y_wrong = torch.tensor([[1.0]], requires_grad=True)
    lhs_wrong = phy_loss_fn(x, y_wrong, return_lhs=True)
    loss_wrong = phy_loss_fn(x, y_wrong)

    print("\n❌ 错误构造的样本:")
    print(f"x = {x.detach().numpy()}")
    print(f"y_wrong = {y_wrong.detach().numpy()}")
    print(f"→ 公式左侧表达式值: {lhs_wrong.detach().numpy()}")
    print(f"→ 最终loss值: {loss_wrong.item():.8f}")

if __name__ == "__main__":
    debug_physical_loss()
