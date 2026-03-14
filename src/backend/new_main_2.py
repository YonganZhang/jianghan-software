import os
import json
import numpy as np
import pandas as pd
import warnings
import argparse
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pysr import PySRRegressor
from sklearn.metrics import r2_score
import shutil

warnings.filterwarnings("ignore", category=UserWarning)

# ========= 字体设置：自动选择可用中文字体，修复中文方块 & 负号 =========
def set_chinese_font():
    candidates = [
        "SimHei", "Microsoft YaHei", "SimSun",
        "Noto Sans CJK SC", "Noto Sans CJK JP", "WenQuanYi Zen Hei",
        "Arial Unicode MS"
    ]
    available = set(f.name for f in font_manager.fontManager.ttflist)
    chosen = None
    for name in candidates:
        if name in available:
            chosen = name
            break
    if chosen is None:
        # 回退到 DejaVuSans（常见），至少不乱码
        chosen = "DejaVu Sans"
    mpl.rcParams['font.family'] = chosen
    mpl.rcParams['font.sans-serif'] = [chosen]
    mpl.rcParams['axes.unicode_minus'] = False  # 负号正常显示

# ===== 全局绘图外观设置 =====
set_chinese_font()
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.dpi'] = 300
mpl.rcParams['font.serif'] = ['Times New Roman']



def save_latex_as_image(latex_str, out_path):
    """把 LaTeX 公式保存为 PNG 图片"""
    fig, ax = plt.subplots(figsize=(6, 1))
    ax.axis("off")
    # 注意加 $ 包裹
    ax.text(0.5, 0.5, f"${latex_str}$", fontsize=16, ha="center", va="center")
    # TODO: 保存“单条公式的 LaTeX 渲染图片（PNG）”
    # - 内容来源：参数 latex_str（通常由 model.latex(...) 或 per_eq_df["latex"] 产生）
    # - 坐标/文字：本函数只渲染数学公式，未使用数据曲线
    # - 输出路径：out_path（调用方传入，通常位于 绘图/<目标目录>/<文件名去后缀>/latex_per_equation/eq_*.png）
    # - 命名规则：由调用方在构造 out_path 时决定（参见 main 中构造 fn_img 的代码）
    # 先删除已存在的文件（处理权限问题）
    if os.path.exists(out_path):
        try:
            os.remove(out_path)
        except:
            pass
    
    try:
        plt.savefig(out_path, bbox_inches="tight", pad_inches=0.2, dpi=300)
    except PermissionError:
        import time as t
        base, ext = os.path.splitext(out_path)
        out_path = f"{base}_{int(t.time()*1000)}{ext}"
        plt.savefig(out_path, bbox_inches="tight", pad_inches=0.2, dpi=300)
        print(f"警告：原文件被占用，保存到：{out_path}")
    plt.close(fig)


def get_Data(data_path, name_):
    import pandas as pd
    import time as time_module
    df = pd.read_excel(data_path, engine='openpyxl')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.loc[:, ~df.columns.str.contains('^jing_ming')]
    df.dropna(inplace=True)
    
    print(f"[进度] 原始数据形状: {df.shape}")
    print(f"[进度] 目标列 '{name_}' 统计: min={df[name_].min():.4f}, max={df[name_].max():.4f}, mean={df[name_].mean():.4f}")
    
    label = df[name_].values.ravel()  # 转为1D数组，PySR需要1D
    data1 = df.drop([name_], axis=1)
    data0 = data1
    label0 = label  # 保持1D

    columns_info = pd.DataFrame({
        'Column Name': data1.columns,
        'Column Index': [f"x{i}" for i in range(len(data1.columns))]
    }).T

    output_dir = '表头文件'
    output_file = os.path.join(output_dir, 'data_with_column_info.xlsx')
    os.makedirs(output_dir, exist_ok=True)
    
    # 如果文件已存在，先尝试删除（处理文件占用问题）
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
        except PermissionError:
            # 文件被占用，使用带时间戳的临时文件名
            timestamp = int(time_module.time() * 1000)
            base, ext = os.path.splitext(output_file)
            output_file = f"{base}_{timestamp}{ext}"
            print(f"警告：原文件被占用，使用临时文件名：{output_file}")
    # TODO: 保存“列名映射表”到 Excel
    # - 内容来源：columns_info（两行：第一行为所有特征列名；第二行为对应索引x0,x1,...）
    # - 数据来源变量：data1.columns（即原始 Excel 去掉目标列 name_ 后的自变量列）
    # - 输出路径：表头文件/data_with_column_info.xlsx（初次写入，默认 sheet 为 Sheet1）
    columns_info.to_excel(output_file, index=False, engine='openpyxl')
    # TODO: 追加保存“去除目标列后的特征数据表 data1”到同一个 Excel
    # - 内容来源：data1（= 原始 df 删除目标列 name_ 后的 DataFrame）
    # - 追加写入到 sheet_name='data1'
    # - 输出路径：表头文件/data_with_column_info.xlsx（以追加模式写入）
    with pd.ExcelWriter(output_file, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    return data0, label0

def my_code():

    # ========= 工具函数 =========
    def ensure_dir(path):
        os.makedirs(path, exist_ok=True)
        return path

    def compute_metrics(label, result):
        result = np.asarray(result, dtype=float)
        label = np.asarray(label, dtype=float)
        result[np.isnan(result)] = 0.0
        r2  = float(r2_score(label, result))
        mae = float(np.mean(np.abs(label - result)))
        mse = float(np.mean((label - result) ** 2))
        rmse = float(np.sqrt(mse))
        return r2, mae, mse, rmse

    # ================== 每条方程逐一评估 ==================
    def evaluate_all_equations(model, X, y, precision_latex=3):
        """
        返回 DataFrame: [index, complexity, loss, score, r2, mae, mse, rmse, latex]
        """
        eqdf = getattr(model, "equations_", None)
        
        print(f"[进度] model.equations_ 行数: {len(eqdf) if eqdf is not None else 0}")
        
        if eqdf is None or len(eqdf) == 0:
            return pd.DataFrame()

        rows = []
        y = np.asarray(y).reshape(-1)
        for idx in eqdf.index:
            yhat = model.predict(X, index=int(idx))  # 官方支持 index 选择公式
            r2, mae, mse, rmse = compute_metrics(y, np.asarray(yhat).reshape(-1))
            complexity = eqdf.loc[idx, "complexity"] if "complexity" in eqdf.columns else None
            loss = eqdf.loc[idx, "loss"] if "loss" in eqdf.columns else None
            score = eqdf.loc[idx, "score"] if "score" in eqdf.columns else None
            try:
                latex_i = model.latex(index=int(idx), precision=precision_latex)
            except Exception:
                latex_i = ""
            rows.append({
                "index": int(idx),
                "complexity": complexity,
                "loss": float(loss) if loss is not None else None,
                "score": float(score) if score is not None else None,
                "r2": r2, "mae": mae, "mse": mse, "rmse": rmse,
                "latex": latex_i,
            })
        return pd.DataFrame(rows)

    # ========= 参数表（更细致说明 & 石油孔隙度案例）=========
    import pandas as pd

    def default_parameters_table():
        """
        说明：
        - 本表将“算子选择”改为逐个开关（是/否），更直观：勾选即纳入搜索空间。
        - 约束（constraints）默认用 {} 表示空；等价于留空。
        - maxdepth 用 -1 表示“自适应”，等价于留空。
        - select_k_features 用 0 表示不启用特征筛选，等价于留空。
        - 这样不会出现空单元格，但和留空效果一致。
        """
        rows = [
            # ===== 数据相关 =====
            ("目标目录", "test", "任意有效目录",
             "输出目录上级名称。用于按数据源组织输出，如 'test/TOC.xlsx'。"
             "建议用简短英文/拼音，避免路径过长或含特殊符号。"
             "例如针对不同井别或区块，可分为 test_A、test_B。", "数据相关"),

            ("目标文件名", "TOC.xlsx", "如 data1.xlsx",
             "输入的 Excel 文件名（含扩展名），需放在目标目录下。"
             "通常包含原始实验/测井结果数据，例如 'TOC.xlsx'、'孔隙度.xlsx'。"
             "建议文件名体现内容，以便快速识别。", "数据相关"),

            ("目标参数", "岩心TOC", "任意目标变量名称",
             "要拟合/预测的目标列名。例如 '岩心TOC'、'孔隙度(%)'、'渗透率'。"
             "必须与 Excel 表头一致。"
             "石油领域常用于有机质丰度(TOC)、孔隙度、渗透率等指标建模。", "数据相关"),

            ("深度列表头", "Depth", "Depth/DEPTH/深度/depth/或空",
             "深度列的列名。如果未检测到对应列，则默认第一列为深度。"
             "深度是油气地质中最常见的自变量，通常作为横轴。"
             "常见名称有 'Depth'、'DEPTH' 或中文 '深度'。", "数据相关"),

            # ===== 算子选择（是/否）——一元 =====
            ("考虑cos", "是", "是/否",
             "是否允许余弦函数 cos(x) 出现在回归公式中。"
             "cos 可表达周期性规律，如旋回沉积或曲线振荡。"
             "但在孔隙度、TOC 等平滑趋势参数拟合中，容易带来非物理震荡。"
             "若确有明显周期性再启用。", "算子选择"),

            ("考虑sin", "是", "是/否",
             "是否允许正弦函数 sin(x)。"
             "与 cos 类似，用于周期性模式建模。"
             "适用于波浪状、循环性的地层特征，但通常石油储层曲线不明显。"
             "默认关闭以避免不必要的震荡项。", "算子选择"),

            ("考虑exp", "是", "是/否",
             "是否纳入指数函数 exp(x)。"
             "在地质中常用于描述压实导致的孔隙度随深度呈指数衰减，"
             "或有机质成熟度呈指数增长等现象。"
             "若变量对目标参数存在衰减/增强趋势，开启较合理。", "算子选择"),

            ("考虑log", "是", "是/否",
             "是否纳入对数函数 log(x)。"
             "对数可把乘性关系转化为加性关系，对右偏分布拉直。"
             "石油领域常用于渗透率分布建模。"
             "注意输入必须大于 0，否则会报错。", "算子选择"),

            ("考虑inv(x)=1/x", "是", "是/否",
             "是否纳入倒数算子 1/x。"
             "用于表达“随变量增大而快速衰减”的规律，如裂缝密度影响渗透率。"
             "但对接近 0 的数值敏感，易引发数值不稳定。", "算子选择"),

            # ===== 算子选择（是/否）——二元 =====
            ("考虑+", "是", "是/否",
             "加法运算。最基础的线性组合方式。"
             "通常用于叠加多个独立效应，建议始终保留。", "算子选择"),

            ("考虑-", "是", "是/否",
             "减法运算。允许变量之间形成差异关系。"
             "如“压实效应 - 胀裂效应”。"
             "建议保留，否则表达能力不足。", "算子选择"),

            ("考虑*", "是", "是/否",
             "乘法。可表达交互项，体现两个变量联合效应。"
             "例如“孔隙度 * 渗透率影响产能”。"
             "通常必需，建议保留。", "算子选择"),

            ("考虑/", "是", "是/否",
             "除法。常见于比值关系，如“孔隙度/渗透率”。"
             "能刻画相对效应，但要注意零除风险。", "算子选择"),

            ("考虑^", "是", "是/否",
             "幂运算。可表达非线性增强/衰减效应。"
             "例如 TOC^2 强调高丰度样本的贡献。"
             "但容易过拟合，默认关闭，必要时手动开启。", "算子选择"),

            # ===== 约束 =====
            ("constraints", '{"^": [-3, 3]}', "JSON 字符串",
             "用于限制表达式复杂度或禁止某些组合。"
             "例如 {\"^\": [-3, 3]} 表示幂运算的指数范围在 -3 到 3 之间。", "搜索复杂度/结构控制"),

            ("nested_constraints", '{"log": {"log": 0}, "sin": {"sin": 1}}', "JSON 字符串",
             "嵌套约束，限制算子嵌套深度。"
             "默认配置：禁止 log 自嵌套，禁止 sin/cos 互相或自嵌套。"
             "例如 {\"sin\": {\"sin\": 1}} 表示允许最多两层 sin 嵌套。", "搜索复杂度/结构控制"),

            # ===== 搜索复杂度/结构控制 =====
            ("maxsize", 50, "正整数",
             "表达式复杂度上限，表示语法树节点总数。"
             "越大越灵活，但过大可能过拟合。"
             "建议地质建模初期设 20~40。", "搜索复杂度/结构控制"),

            ("maxdepth", "智能计算", "正整数或留空",
             "-1 表示自适应深度控制。"
             "设为正整数则固定最大树深度。"
             "推荐用默认 -1，让算法自适应调整。", "搜索复杂度/结构控制"),

            ("warmup_maxsize_by", 0.0, "0~1",
             "逐步放宽复杂度的比例。"
             "例如设为 0.5，前半程搜索较简单模型，后半程逐步增加复杂度。"
             "可提升稳定性，减少早期过拟合。", "搜索复杂度/结构控制"),

            ("use_frequency", 1, "0/1",
             "是否在进化搜索中使用复杂度频率。"
             "开启后会平衡搜索，避免总是偏向低复杂度或高复杂度。", "搜索复杂度/结构控制"),

            ("use_frequency_in_tournament", 1, "0/1",
             "在候选比较时是否考虑复杂度频率。"
             "若开启，选择过程中会偏好多样化公式。", "搜索复杂度/结构控制"),

            ("adaptive_parsimony_scaling", 1040.0, "正浮点",
             "自适应简约惩罚强度。"
             "数值越大，算法越倾向于选择更简单的公式。"
             "避免出现复杂但过拟合的表达式。", "搜索复杂度/结构控制"),

            ("should_simplify", 1, "0/1",
             "是否启用代数化简。"
             "开启后公式会被自动化简，如 x+x → 2x。"
             "通常建议开启，能提升可解释性。", "搜索复杂度/结构控制"),

            # ===== 搜索规模 =====
            ("niterations", 80, "正整数",
             "进化迭代次数。越大结果越稳定，但计算更耗时。"
             "一般设 30~50 就能收敛。", "搜索规模"),

            ("populations", 40, "正整数",
             "种群数量。多个种群并行进化，有助于多样化搜索。"
             "通常 10~30 之间。", "搜索规模"),

            ("population_size", 1000, "正整数",
             "每个种群的个体数。越大越全面，但计算量也增加。"
             "1000 是经验值，适合大多数情况。", "搜索规模"),

            ("ncycles_per_iteration", 300, "正整数",
             "每次迭代的突变/选择循环次数。"
             "循环越多，搜索越充分，但速度更慢。", "搜索规模"),

            # ===== 目标/选择 =====
            ("elementwise_loss", "L2DistLoss()", "Julia 表达式",
             "逐点损失函数。L2 距离 (均方误差) 常用于连续变量拟合。"
             "在 TOC、孔隙度预测中，能平滑惩罚大误差。"
             "可换为 L1 等以增强鲁棒性。", "目标/选择"),

            ("model_selection", "best", '"best"/"accuracy"/"score"',
             "最终模型选择标准。"
             "best：综合考虑复杂度和精度，推荐默认。"
             "accuracy：更偏向精度。"
             "score：使用内部评分。", "目标/选择"),

            # ===== 特征筛选 =====
            ("select_k_features", "5", "正整数或空",
             "是否在回归前执行特征选择。"
             "空表示不启用；正整数表示最多选择多少特征。"
             "适合输入特征较多的情况。", "特征筛选"),

            # ===== 常数优化 =====
            ("optimize_probability", 0.14, "0~1",
             "常数优化的概率。"
             "值越大，搜索过程中更频繁尝试优化常数项。"
             "能提高公式精度，但速度更慢。", "常数优化"),

            ("optimizer_algorithm", "BFGS", '"BFGS"/"NelderMead"',
             "用于常数优化的算法。"
             "BFGS：拟牛顿法，收敛快，适合光滑问题。"
             "NelderMead：单纯形法，更鲁棒但可能慢。", "常数优化"),

            ("optimizer_iterations", 8, "正整数",
             "单次常数优化的最大迭代步数。"
             "过大可能耗时过长，过小则不充分。", "常数优化"),

            ("optimizer_nrestarts", 2, "非负整数",
             "常数优化的随机重启次数。"
             "重启能帮助跳出局部最优。"
             "推荐 2~5。", "常数优化"),

            # ===== 交叉概率 =====
            ("crossover_probability", 0.0259, "0~1",
             "遗传算法中交叉操作的概率。"
             "值越大，新个体来源于父代交叉的比例越高。"
             "过大可能导致收敛慢，过小则缺乏多样性。", "交叉概率"),
        ]

        df = pd.DataFrame(rows, columns=["Parameter", "Value", "PossibleValues", "Description", "Category"])

        # 转换：Excel 里显示 "智能计算"，但内部保存为空字符串
        df["Value_internal"] = df["Value"].replace("智能计算", "")

        return df

    def ensure_parameter_excel(excel_path):
        parent = os.path.dirname(excel_path)
        if parent:
            ensure_dir(parent)
        if not os.path.exists(excel_path):
            df = default_parameters_table()
            # TODO: 自动创建并保存“参数模板 Excel”
            # - 内容来源：default_parameters_table() 生成的 df（列包含 Parameter/Value/PossibleValues/Description/Category/Value_internal）
            # - 使用场景：首次运行且 excel_path 不存在时
            # - 输出路径：excel_path（默认：运行前设置/parameters_template.xlsx）
            df.to_excel(excel_path, index=False)
            print(f"[Info] 已自动创建参数模板: {excel_path}")

    def load_parameters_from_excel(excel_path):
        ensure_parameter_excel(excel_path)
        df = pd.read_excel(excel_path)
        print(f"[进度] 读取参数文件: {excel_path}")
        print(f"[进度] 参数文件列名: {list(df.columns)}")
        
        if "PossibleValues" not in df.columns:
            df["PossibleValues"] = ""
        if "Description" not in df.columns:
            df["Description"] = ""
        parameters = df.set_index("Parameter")["Value"].to_dict()
        
        # 打印关键参数
        print(f"[进度] 读取到的参数数量: {len(parameters)}")
        key_params = ['niterations', 'populations', 'population_size', 'ncycles_per_iteration']
        for k in key_params:
            if k in parameters:
                print(f"[进度] 参数 {k} = {parameters[k]}")

        a = parameters.get("目标目录", "test")
        b = parameters.get("目标文件名", "TOC.xlsx")
        c = parameters.get("目标参数", "岩心TOC")
        depth_col = parameters.get("深度列表头", "Depth")
        for k in ["目标目录", "目标文件名", "目标参数", "深度列表头"]:
            parameters.pop(k, None)
        args = argparse.Namespace(**parameters)
        return a, b, c, depth_col, args

    def extract_depth_and_strip(data, depth_col=None):
        if isinstance(data, pd.DataFrame):
            df = data.copy()
            chosen = None
            if depth_col and depth_col in df.columns:
                chosen = depth_col
            else:
                for c in ["Depth", "DEPTH", "深度", "depth"]:
                    if c in df.columns:
                        chosen = c
                        break
            if chosen is None:
                chosen = df.columns[0]

            depth = df[chosen].to_numpy().ravel()
            X_no_depth = df.drop(columns=chosen)  # 保留 DataFrame，不转 numpy
            return depth, X_no_depth
        else:
            arr = np.asarray(data)
            depth = arr[:, 0].ravel()
            X_no_depth = pd.DataFrame(arr[:, 1:], columns=[f"x{i}" for i in range(arr.shape[1] - 1)])
            return depth, X_no_depth

    def pic2(i, depth, result, label, file_path, name__):
        plt.figure(figsize=(8, 5), dpi=100)
        mpl.rcParams['font.size'] = 12
        # 曲线：真实值与预测值
        plt.plot(label, depth, 'r-', linewidth=2, label='真实值')  # 深度在Y轴
        plt.plot(result, depth, 'b--', linewidth=1.5, label='预测值')
        # 轴标签
        plt.ylabel('深度 (m)')
        plt.xlabel(name_)
        # 计算R²
        r2 = r2_score(label.ravel(), np.asarray(result).ravel())
        plt.title(f"公式 {i+1} 拟合效果 (R²={r2:.4f})")
        plt.gca().invert_yaxis()  # 深度轴反转（深度向下增加）
        plt.legend(loc='best')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        folder, file_name = os.path.split(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        new_path = ensure_dir(os.path.join("绘图", folder, file_name_without_ext))
        out_path = os.path.join(new_path, f'plot_{i:03d}.png')  # 使用PNG格式，索引命名
        # TODO: 保存“单条公式的拟合曲线图（TIFF）”
        # - 横轴来源：depth（extract_depth_and_strip() 从原始表中选取的深度列，单位 m）
        # - 纵轴（真实）：label（来自 get_Data(..., name_) 抽取的目标列 name_ 的真实值，形状与 depth 对齐）
        # - 纵轴（预测）：result（= model.predict(X_no_depth, index=i) 对应第 i+1 条公式的预测）
        # - 图例：'真实值' 与 '预测值'；标题含“展示公式 i+1”
        # - y 轴标签：name_（参数“目标参数”，例如“岩心TOC”）
        # - 输出路径：绘图/<目标目录>/<目标文件名无后缀>/plot{name_}{name__}_公式{i+1}.tif
        # - 命名细节：name__ 在调用中固定为 "正常_"，用于标注绘图模式
        # 先删除已存在的文件（处理权限问题）
        if os.path.exists(out_path):
            try:
                os.remove(out_path)
            except:
                pass
        try:
            plt.savefig(out_path, bbox_inches='tight')
        except PermissionError:
            import time as t
            base, ext = os.path.splitext(out_path)
            out_path = f"{base}_{int(t.time()*1000)}{ext}"
            plt.savefig(out_path, bbox_inches='tight')
        plt.close()
        print("每条公式的拟合图像已保存在本地:", out_path)

    # ========= 解析辅助 =========
    def parse_yesno(x, default=True):
        if x is None or str(x).strip()=="":
            return default
        s = str(x).strip().lower()
        if s in ["是", "yes", "y", "true", "1", "t"]:
            return True
        if s in ["否", "no", "n", "false", "0", "f"]:
            return False
        try:
            return bool(int(x))
        except Exception:
            return default

    def parse_json_or_mapping(s):
        if s is None or (isinstance(s, float) and np.isnan(s)) or str(s).strip() == "":
            return None
        s = str(s).strip()
        try:
            d = json.loads(s)
            return d
        except Exception:
            result = {}
            for token in s.split(";"):
                token = token.strip()
                if not token:
                    continue
                parts = token.split(":")
                if len(parts) >= 2:
                    key = parts[0].strip()
                    val = parts[1].strip()
                    try:
                        result[key] = float(val) if (val.replace('.','',1).isdigit()) else val
                    except Exception:
                        result[key] = val
            return result or None

    def parse_constraints(s):
        """
        解析“复杂度约束”：
        - 一元算子 -> 整数（最大参数表达式复杂度）；-1 不受限
        - 二元算子 -> (left_max, right_max) 整数元组；-1 不受限
        支持：
          JSON: '{"^":[-1,1], "log":9}'
          简写: '^:-1:1; log:9'
        """
        if s is None or (isinstance(s, float) and np.isnan(s)) or str(s).strip() == "":
            return None
        s = str(s).strip()

        def to_int_or_minus1(x):
            lx = str(x).strip().lower()
            if lx in ("inf", "+inf", "null", "none"):
                return -1
            return int(float(x))

        # JSON
        try:
            d = json.loads(s)
            out = {}
            for k, v in d.items():
                if isinstance(v, (list, tuple)) and len(v) == 2:
                    out[k] = (to_int_or_minus1(v[0]), to_int_or_minus1(v[1]))
                else:
                    out[k] = to_int_or_minus1(v)
            return out or None
        except Exception:
            pass

        # 简写
        out = {}
        for token in s.split(";"):
            token = token.strip()
            if not token:
                continue
            parts = [p.strip() for p in token.split(":")]
            if len(parts) == 3:
                op, a, b = parts
                out[op] = (to_int_or_minus1(a), to_int_or_minus1(b))
            elif len(parts) == 2:
                op, n = parts
                out[op] = to_int_or_minus1(n)
        return out or None

    def _to_int(x, default=None):
        if x is None or (isinstance(x, float) and np.isnan(x)) or str(x).strip()=="":
            return default
        try:
            return int(x)
        except Exception:
            try:
                return int(float(x))
            except Exception:
                return default

    def _to_float(x, default=None):
        if x is None or (isinstance(x, float) and np.isnan(x)) or str(x).strip()=="":
            return default
        try:
            return float(x)
        except Exception:
            return default

    def _to_bool(x, default=False):
        if x is None or str(x).strip()=="":
            return default
        try:
            return bool(int(x))
        except Exception:
            if isinstance(x, bool):
                return x
            s = str(x).strip().lower()
            if s in ["true", "t", "yes", "y", "是"]:
                return True
            if s in ["false", "f", "no", "n", "否"]:
                return False
            return default

    def build_pysr_from_args(args):
        # ===== 从“是否考虑算子”开关构建算子集合 =====
        use_cos = parse_yesno(getattr(args, "考虑cos", "否"), False)
        use_sin = parse_yesno(getattr(args, "考虑sin", "否"), False)
        use_exp = parse_yesno(getattr(args, "考虑exp", "是"), True)
        use_log = parse_yesno(getattr(args, "考虑log", "是"), True)
        use_inv = parse_yesno(getattr(args, "考虑inv(x)=1/x", "是"), True)

        unary_ops = []
        if use_cos: unary_ops.append("cos")
        if use_sin: unary_ops.append("sin")
        if use_exp: unary_ops.append("exp")
        if use_log: unary_ops.append("log")
        if use_inv: unary_ops.append("inv(x) = 1/x")
        # 若全部关闭，至少给个恒等（否则无一元算子也可，只是搜索更靠二元/常数）
        # 这里允许为空

        use_add = parse_yesno(getattr(args, "考虑+", "是"), True)
        use_sub = parse_yesno(getattr(args, "考虑-", "是"), True)
        use_mul = parse_yesno(getattr(args, "考虑*", "是"), True)
        use_div = parse_yesno(getattr(args, "考虑/", "是"), True)
        use_pow = parse_yesno(getattr(args, "考虑^", "否"), False)

        bin_ops = []
        if use_add: bin_ops.append("+")
        if use_sub: bin_ops.append("-")
        if use_mul: bin_ops.append("*")
        if use_div: bin_ops.append("/")
        if use_pow: bin_ops.append("^")
        if not bin_ops:
            # 至少保留加法保证可组式
            bin_ops = ["+"]

        # 约束
        constraints_raw = parse_constraints(getattr(args, "constraints", None))
        # NOTE: 这里不强制清洗到“仅限已启用算子”，因为 PySR 会据 operators 过滤；
        # 如需严格，可在此过滤：constraints = {k:v for k,v in constraints_raw.items() if k in unary_ops+bin_ops}
        constraints = constraints_raw

        nested_constraints = getattr(args, "nested_constraints", None)
        if isinstance(nested_constraints, str) and nested_constraints.strip():
            try:
                nested_constraints = json.loads(nested_constraints)
            except Exception:
                nested_constraints = None
        else:
            nested_constraints = None

        # SymPy 映射（保留 inv 映射）
        extra_sympy_mappings = {"inv": (lambda x: 1/x)}

        # 复杂度/结构
        maxsize = _to_int(getattr(args, "maxsize", 30), 30)
        maxdepth = _to_int(getattr(args, "maxdepth", None), None)
        warmup_maxsize_by = _to_float(getattr(args, "warmup_maxsize_by", 0.0), 0.0)
        use_frequency = _to_bool(getattr(args, "use_frequency", 1), True)
        use_frequency_in_tournament = _to_bool(getattr(args, "use_frequency_in_tournament", 1), True)
        adaptive_parsimony_scaling = _to_float(getattr(args, "adaptive_parsimony_scaling", 1040.0), 1040.0)
        should_simplify = _to_bool(getattr(args, "should_simplify", 1), True)

        complexity_of_operators = parse_json_or_mapping(getattr(args, "complexity_of_operators", None))

        # 搜索规模 - 平衡速度和拟合效果
        niterations = _to_int(getattr(args, "niterations", 40), 40)  # 迭代次数
        populations = _to_int(getattr(args, "populations", 15), 15)    # 种群数
        population_size = _to_int(getattr(args, "population_size", 33), 33)  # 每个种群的大小（PySR推荐）
        ncycles_per_iteration = _to_int(getattr(args, "ncycles_per_iteration", 550), 550)  # 每次迭代的循环数

        # 目标/选择
        elementwise_loss = getattr(args, "elementwise_loss", 'L2DistLoss()')
        model_selection = str(getattr(args, "model_selection", "best"))
        select_k_features = _to_int(getattr(args, "select_k_features", None), None)
        parsimony = _to_float(getattr(args, "parsimony", 0.0), 0.0)

        # 常数优化
        optimize_probability = _to_float(getattr(args, "optimize_probability", 0.14), 0.14)
        optimizer_algorithm = str(getattr(args, "optimizer_algorithm", "BFGS"))
        optimizer_iterations = _to_int(getattr(args, "optimizer_iterations", 8), 8)
        optimizer_nrestarts = _to_int(getattr(args, "optimizer_nrestarts", 2), 2)

        # 交叉概率
        crossover_probability = _to_float(getattr(args, "crossover_probability", 0.0259), 0.0259)

        # 关键：禁止 PySR 写任何输出文件/目录
        output_directory = "缓存目录"   # 占位，不会写

        kwargs = dict(
            # 搜索空间
            binary_operators=bin_ops,
            unary_operators=unary_ops,
            constraints=constraints,
            nested_constraints=nested_constraints,
            extra_sympy_mappings=extra_sympy_mappings,

            # 复杂度/结构策略 - 关键：增大maxsize以获得更多公式
            maxsize=maxsize if maxsize and maxsize > 0 else 40,  # 最大公式复杂度，决定公式数量上限
            maxdepth=maxdepth if maxdepth and maxdepth > 0 else None,
            warmup_maxsize_by=warmup_maxsize_by if warmup_maxsize_by else 0.0,
            use_frequency=use_frequency,
            use_frequency_in_tournament=use_frequency_in_tournament,
            adaptive_parsimony_scaling=adaptive_parsimony_scaling if adaptive_parsimony_scaling else 20.0,
            should_simplify=should_simplify,
            complexity_of_operators=complexity_of_operators,
            parsimony=parsimony if parsimony else 0.0032,  # 复杂度惩罚，小值允许更复杂的公式

            # 搜索规模
            niterations=niterations,
            populations=populations,
            population_size=population_size,
            ncycles_per_iteration=ncycles_per_iteration,

            # 目标/选择
            elementwise_loss=elementwise_loss,
            model_selection=model_selection,
            select_k_features=select_k_features,

            # 常数优化 - 关键：提高优化概率和迭代次数
            optimize_probability=optimize_probability if optimize_probability else 0.14,
            optimizer_algorithm=optimizer_algorithm,
            optimizer_iterations=optimizer_iterations if optimizer_iterations else 8,
            optimizer_nrestarts=optimizer_nrestarts if optimizer_nrestarts else 2,

            # 交叉
            crossover_probability=crossover_probability if crossover_probability else 0.066,

            # 不写文件
            output_directory=output_directory,
            
            # 额外优化参数 - 提高拟合效果
            batching=False,  # 使用全部数据
            turbo=True,  # 启用turbo模式
            early_stop_condition=None,  # 不早停
            precision=64,  # 双精度
            
            # 关键参数：控制公式复杂度范围
            weight_optimize=0.001,  # 权重优化
            mutation_weights=None,  # 使用默认突变权重
            
        )

        # 删除 None，避免版本不识别时报错
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        return PySRRegressor(**kwargs)

    # ========= 主流程 =========
    # 解析命令行参数
    import sys
    print(f"[进度] 命令行参数: {sys.argv}")
    
    cli_parser = argparse.ArgumentParser(description='PySR公式拟合算法')
    cli_parser.add_argument('--params', type=str, default="运行前设置/parameters_template.xlsx",
                           help='参数文件路径')
    cli_args, _ = cli_parser.parse_known_args()
    
    excel_path = cli_args.params
    print(f"[进度] 使用参数文件: {excel_path}")
    print(f"[进度] 参数文件是否存在: {os.path.exists(excel_path)}")
    
    a, b, c, depth_col_from_excel, args = load_parameters_from_excel(excel_path)
    
    # 打印所有参数
    print(f"[进度] ===== 完整参数列表 =====")
    for k, v in vars(args).items():
        print(f"[进度]   {k} = {v}")

    name1 = b
    global name_
    name_ = c
    file_path = os.path.join(a, name1)

    print(f"[进度] 正在加载数据: {file_path}")
    data, label = get_Data(file_path, name_)
    print(f"[进度] 数据加载完成，样本数: {len(label)}")
    
    depth, X_no_depth = extract_depth_and_strip(data, depth_col_from_excel)
    print(f"[进度] 特征数: {X_no_depth.shape[1]}, 特征名: {list(X_no_depth.columns)}")
    
    # 确保label是1D数组
    label = np.asarray(label).ravel()
    print(f"[进度] 标签形状: {label.shape}, 标签统计: min={label.min():.4f}, max={label.max():.4f}, std={label.std():.4f}")
    
    # 检查数据质量
    X_array = X_no_depth.values if hasattr(X_no_depth, 'values') else np.asarray(X_no_depth)
    print(f"[进度] 特征矩阵形状: {X_array.shape}")
    print(f"[进度] 特征统计: min={X_array.min():.4f}, max={X_array.max():.4f}")

    model = build_pysr_from_args(args)
    
    # 打印模型配置
    print(f"[进度] PySR配置:")
    print(f"[进度]   niterations={model.niterations}")
    print(f"[进度]   populations={model.populations}")
    print(f"[进度]   population_size={model.population_size}")
    print(f"[进度]   maxsize={model.maxsize}")
    print(f"[进度]   binary_operators={model.binary_operators}")
    print(f"[进度]   unary_operators={model.unary_operators}")
    print(f"[进度] 开始公式搜索...")
    
    import sys
    sys.stdout.flush()
    
    # 使用verbosity控制输出
    model.verbosity = 1  # 减少Julia内部输出
    model.progress = False  # 禁用进度条（避免乱码）
    
    # 训练模型
    model.fit(X_no_depth, label)
    print(f"[进度] 公式搜索完成!")
    
    try:
        model.refresh()
    except Exception:
        pass

    print(model)
    try:
        print("公式的 LaTeX 形式:\n", model.latex(precision=2))
    except Exception:
        pass

    # ========== 逐式评估 + 仅绘制“每个公式”的图 ==========
    # （注意：不再绘制总体的 plot{name_}正常_.tif；也不再生成 equations_table_*.tex 和 {name_}.xlsx）
    try:
        num_eq = len(model.equations_)
        print(f"\n[进度] ===== 共发现 {num_eq} 个公式 =====")
        for idx in model.equations_.index:
            try:
                y_pred = model.predict(X_no_depth, index=int(idx))
                r2 = r2_score(label, y_pred)
                complexity = model.equations_.loc[idx, 'complexity']
                print(f"[进度] 公式{idx}: 复杂度={complexity}, R2={r2:.4f}")
            except:
                pass
    except Exception as e:
        print(f"[进度] 获取公式失败: {e}")
        num_eq = 0

    folder, file_name = os.path.split(file_path)
    file_name_without_ext = os.path.splitext(file_name)[0]
    new_path = ensure_dir(os.path.join("绘图", folder, file_name_without_ext))
    # 注：此处 ensure_dir 仅创建目录，不产生文件，无需 TODO

    # 分别画每个公式
    if num_eq > 0:
        for i in range(num_eq):
            result_i = model.predict(X_no_depth, i)
            pic2(i, depth, result_i, label, file_path, "正常_")

    # 逐式评估与导出
    per_eq_df = evaluate_all_equations(model, X_no_depth, label, precision_latex=3)
    
    print(f"[进度] per_eq_df 行数: {len(per_eq_df)}")
    
    if len(per_eq_df):
        # 导出逐式 latex（每条一个 .png）
        latex_dir = ensure_dir(os.path.join(new_path, "latex_per_equation"))
        for _, row in per_eq_df.sort_values(["complexity", "index"]).iterrows():
            fn_img = os.path.join(latex_dir, f"eq_{int(row['index']):03d}.png")
            # TODO: 为“每条公式”保存对应的 LaTeX 公式图片（PNG）
            # - 公式来源：row["latex"]（evaluate_all_equations 中由 model.latex(...) 生成）
            # - 文件命名：eq_<index三位>_c<复杂度>.png（复杂度缺失时为 -1）
            # - 输出目录：latex_dir = 绘图/<目标目录>/<文件名无后缀>/latex_per_equation/
            save_latex_as_image(str(row["latex"]), fn_img)

        # 逐式指标（完整表）
        per_eq_xlsx = os.path.join(new_path, f"各级复杂度公式_逐式指标_{name_}.xlsx")
        # TODO: 保存“逐条公式的评价指标表（Excel）”
        # - 表格来源：per_eq_df，列含：
        #   * index/complexity/loss/score：来自 model.equations_ 原始信息
        #   * r2/mae/mse/rmse：compute_metrics(label, yhat) 计算，label 来自原始目标列，yhat 来自 model.predict(X_no_depth, index=...)
        #   * latex：该公式的 LaTeX 字符串（model.latex）
        # - 输出路径：绘图/<目标目录>/<文件名无后缀>/各级复杂度公式_逐式指标_{name_}.xlsx
        if os.path.exists(per_eq_xlsx):
            try:
                os.remove(per_eq_xlsx)
            except:
                pass
        try:
            per_eq_df.to_excel(per_eq_xlsx, index=False, engine='openpyxl')
        except PermissionError:
            import time as t
            base, ext = os.path.splitext(per_eq_xlsx)
            per_eq_xlsx = f"{base}_{int(t.time()*1000)}{ext}"
            per_eq_df.to_excel(per_eq_xlsx, index=False, engine='openpyxl')
        print("已保存：", per_eq_xlsx)

        # 每个复杂度取 R2 最优
        best_by_complexity = (per_eq_df.sort_values(["complexity", "r2"], ascending=[True, False])
                              .groupby("complexity", as_index=False).head(1))
        best_xlsx = os.path.join(new_path, f"各级复杂度公式_每级最优_{name_}.xlsx")
        # TODO: 保存“按复杂度分组的最优公式表（Excel）”
        # - 生成方式：per_eq_df 先按 complexity 升序、r2 降序排序，然后 groupby("complexity").head(1) 取每组 R2 最高的一条
        # - 表格内容：继承 per_eq_df 的列（index/complexity/loss/score/r2/mae/mse/rmse/latex）
        # - 输出路径：绘图/<目标目录>/<文件名无后缀>/各级复杂度公式_每级最优_{name_}.xlsx
        if os.path.exists(best_xlsx):
            try:
                os.remove(best_xlsx)
            except:
                pass
        try:
            best_by_complexity.to_excel(best_xlsx, index=False, engine='openpyxl')
        except PermissionError:
            import time as t
            base, ext = os.path.splitext(best_xlsx)
            best_xlsx = f"{base}_{int(t.time()*1000)}{ext}"
            best_by_complexity.to_excel(best_xlsx, index=False, engine='openpyxl')
        print("已保存：", best_xlsx)

    # ========= 最后清理缓存 =========
    if os.path.exists("缓存目录"):
        shutil.rmtree("缓存目录")
        print("[Info] 已清理缓存目录")


if __name__ == "__main__":
    my_code()
    print("===== 公式拟合任务完成 =====")
