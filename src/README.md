# 项目接口与算法说明

本项目包含前端（Vue 3 + Electron）与后端（Flask + Socket.IO），以下内容基于现有代码梳理，覆盖前端接口封装、后端接口定义、算法功能与数据流转细节。

## 基础信息

- 前端请求基址（前端 axios 封装）：生产环境 `http://127.0.0.1:5000/api`，开发环境 `/api`
- 后端服务入口：Flask 运行在 `0.0.0.0:5000`
- 统一鉴权方式：`Authorization: Bearer <token>`

## 启动流程与环境要求

### 环境要求

- Python 3 与 pip
- Node.js 18+
- npm 或 yarn

### 启动后端服务（Flask + Socket.IO）

1. 进入后端目录：`后端/`
2. 安装依赖：`pip install -r requirements.txt`
3. 启动服务：`python app.py`
4. 服务地址：`http://127.0.0.1:5000`

后端默认使用 SQLite 数据库，数据库文件为 `wenjie.db`，位于后端目录下。

### 启动前端（Vue + Electron）

1. 进入前端目录：`前端/`
2. 安装依赖：`npm install`
3. 启动开发服务：
   - Web 模式：`npm run dev`
   - 桌面模式：`npm run electron:dev`

前端开发服务器端口为 `5179`，并通过 `/api` 代理到 `http://127.0.0.1:5000`。

### 推荐启动顺序

1. 先启动后端服务
2. 再启动前端（Web 或 Electron）

### 可能的启动注意点

- `npm run electron:dev` 默认等待 `http://localhost:5173`，但当前 Vite 端口为 `5179`，需要统一端口后再启动。

## 前端接口封装

前端接口集中在 [api.ts](file:///e:/学术/3.申博/申博-测井项目/25年项目-江汉油田/软件开发/软件开发/前端/src/utils/api.ts)，axios 拦截逻辑在 [axios.ts](file:///e:/学术/3.申博/申博-测井项目/25年项目-江汉油田/软件开发/软件开发/前端/src/utils/axios.ts)。

### 鉴权与错误处理

- 自动携带 `Authorization` 头
- 响应 `code === 401` 时清理 token 并跳转登录页
- 网络错误、HTTP 错误统一提示

### 前端 API 列表（与后端路径对应）

#### 认证

- `loginApi` → `POST /login`
  请求：`{ username, password }`
  响应：`{ code, message, data: { token, userInfo } }`

#### 数据导入（文件/目录）

- `getTreeData` → `GET /data-import/directory-file/file-structure`
- `addTreeNode` → `POST /data-import/directory-file/create`（multipart/form-data）
- `editTreeNode` → `POST /data-import/directory-file/rename`
- `deleteTreeNode` → `POST /data-import/directory-file/delete`
- `getDataSource` → `POST /data-import/directory-file/page`

#### 数据预处理

- `getEchartsData` → `POST /pretreatment/process`
- `getOriginData` → `POST /pretreatment/process-file`
  当前后端未找到 `/pretreatment/process-file` 实现，需补齐或调整前端调用。

#### 模型训练

- `parameter` → `POST /train/parameter`
- `startTrain` → `POST /train/start`

#### 模型测试

- `getAddSelect` → `GET /modelname`
- `getModelTestingResult` → `POST /getfile`
- `getTestOutputResult` → `POST /test`

#### 模型管理

- `getPreprocessModelResults` → `POST /model-management/modelmagement_page`
- `getLossChart` → `POST /model-management/modelmagement_pictures`
- `getParameters` → `POST /model-management/modelmagement_visualization`
- `editModelResults` → `POST /model-management/modelmagement_modify`
- `deleteModelResults` → `POST /model-management/modelmagement_delete`

#### 智能公式映射

- `runSmartFormula` → `POST /run-smart-formula`
- `getFormulaImage` → `GET /Reimage`
- `getFormulaSpecificImage` → `POST /Resmart`
- `getFormulaPageList` → `POST /Formulaspage`
- `deleteFormulaPageList` → `POST /Deleterecord`
- `FormulaDetail` → `POST /FormulaDetail`
  当前后端未找到 `/FormulaDetail` 实现，需补齐或调整前端调用。

## 后端接口清单

后端入口注册蓝图见 [app.py](file:///e:/学术/3.申博/申博-测井项目/25年项目-江汉油田/软件开发/软件开发/后端/app.py)，路径前缀如下：

- 用户：`/api`
- 文件管理：`/api/data-import/directory-file`
- 预处理：`/api/pretreatment`
- 训练：`/api/train`
- 测试：`/api`
- 模型管理：`/api/model-management`
- 智能公式映射：`/api`

### 用户与认证（User）

文件：[User.py](file:///e:/学术/3.申博/申博-测井项目/25年项目-江汉油田/软件开发/软件开发/后端/blueprints/User.py)

- `POST /api/sign` 注册请求：`{ username, password, email }`逻辑：创建用户、根目录与默认子目录，初始化模型配置响应：`{ code: "00000", message }`
- `POST /api/login` 登录
  请求：`{ username, password }`
  响应：`{ code: "00000", message, data: { token, userInfo } }`

### 文件与目录管理（File_management）

文件：[File_management.py](file:///e:/学术/3.申博/申博-测井项目/25年项目-江汉油田/软件开发/软件开发/后端/blueprints/File_management.py)

- `POST /api/data-import/directory-file/page`请求：`{ id, pageNum }`（`pageSize` 固定 20）响应：分页表格结构 `{ pageNum, pageSize, totalPages, totalCount, columns, dataSource }`
- `GET /api/data-import/directory-file/file-structure`响应：树形目录结构 `[{ id, title, type, children }]`
- `POST /api/data-import/directory-file/create`multipart/form-data目录创建：`type=directory` + `name` + `parent_id`文件上传：`type=file` + `file` + `parent_id`
- `POST /api/data-import/directory-file/rename`请求：`{ id, name, type }`（type: directory | file）
- `POST /api/data-import/directory-file/delete`
  请求：`{ id, type }`
  逻辑：软删除目录或文件

### 预处理（Pre_treatment）

文件：[Pre_treatment.py](file:///e:/学术/3.申博/申博-测井项目/25年项目-江汉油田/软件开发/软件开发/后端/blueprints/Pre_treatment.py)

- `POST /api/pretreatment/process`请求：
  - `key`: 文件 ID
  - `type`: 预处理算法数组或字符串可选：`zscore`、`岩性分类`、`basic_normalization`、`casing_bolt_removal`
  - `predict_target`: 部分算法需要（如 `zscore`、`岩性分类`、`basic_normalization`）
    响应：
  - 成功：`{ code: 200, message, process_type, data, saved_to }`
  - data 为图表坐标结构：`{ options, axisData, axisData2 }`

数据结构说明：

- `options.character1` / `options.character2`：两组特征名称
- `axisData` / `axisData2`：`{ 特征名: [[特征值, DEPTH], ...] }`

### 训练（Train）

文件：[Train.py](file:///e:/学术/3.申博/申博-测井项目/25年项目-江汉油田/软件开发/软件开发/后端/blueprints/Train.py)

- `POST /api/train/parameter`请求：模型与训练参数（字段较多，详见 [tool_for_pre.py](file:///e:/学术/3.申博/申博-测井项目/25年项目-江汉油田/软件开发/软件开发/后端/tools/tool_for_pre.py) `get_parameters`）响应：`{ code: 200, message }`
- `POST /api/train/start`
  逻辑：加载模型配置并执行训练
  响应：`{ code: 200, message, data: { train_coordinate, val_coordinate } }`

### 测试（Test）

文件：[Test.py](file:///e:/学术/3.申博/申博-测井项目/25年项目-江汉油田/软件开发/软件开发/后端/blueprints/Test.py)

- `POST /api/getfile`请求：`{ file_id }`响应：与预处理一致的图表结构 `data`
- `GET /api/modelname`响应：可用模型列表

  ```
  {
    "data": {
      "final-data": [{ id, name, type }],
      "best-data": [{ id, name, type }]
    }
  }
  ```
- `POST /api/test`
  请求：`{ dir_id, file_id, idm, type, predict_mode }`
  响应：预测与真实坐标 + 误差指标

  ```
  {
    "data": {
      "prediction_coords": [...],
      "true_coords": [...],
      "table": { MSE, MAE, RMSE, R2 }
    }
  }
  ```

### 模型管理（Model_management）

文件：[Model_management.py](file:///e:/学术/3.申博/申博-测井项目/25年项目-江汉油田/软件开发/软件开发/后端/blueprints/Model_management.py)

- `POST /api/model-management/modelmagement_page`请求：`{ pageNum, pageSize }`响应：合并“最终模型/最佳模型”的分页列表
- `POST /api/model-management/modelmagement_pictures`请求：`{ id, model_type }`响应：Base64 图片数据
- `POST /api/model-management/modelmagement_visualization`请求：`{ id, model_type }`响应：训练参数明细（model_name、hidden_size 等）
- `POST /api/model-management/modelmagement_modify`请求：`{ id, model_type, modelname }`
- `POST /api/model-management/modelmagement_delete`
  请求：`{ id, model_type }`

### 智能公式映射（Smart_formula）

文件：[Smart_formula.py](file:///e:/学术/3.申博/申博-测井项目/25年项目-江汉油田/软件开发/软件开发/后端/blueprints/Smart_formula.py)

- `POST /api/run-smart-formula`必填参数：`id`, `目标文件名`, `目标目录`, `目标参数`处理流程：

  - 从 File 表读取原始文件并复制到 `目标目录/目标文件名`
  - 生成参数 Excel：`运行前设置/parameters_template.xlsx`
  - 执行算法脚本 `new_main_2.py`
  - 读取算法输出目录：`绘图/<目标目录>/<目标文件名去后缀>/`
  - 解析公式图、预测图、JSON 坐标、Excel 指标并入库
    响应：

  ```
  {
    "code": 200,
    "状态": "成功",
    "批次号": <int>,
    "匹配成功记录数": <int>,
    "入库记录数": <int>,
    "配置参数": { ... }
  }
  ```
- `GET /api/Reimage`返回最新批次的预测图和公式图（Base64）
- `POST /api/Resmart`请求：`{ id }`返回：坐标数据 + 公式图片
- `POST /api/Formulaspage`请求：`{ pageNum, pageSize }`返回：分页公式列表
- `POST /api/Deleterecord`请求：`{ id }`删除公式记录并清理图片文件
- `POST /api/rename-save-file`
  请求：`{ file_id }`
  功能：将指定文件复制为 `test/TOC.xlsx`，供算法使用

## 算法功能概览

### 预处理算法

预处理算法在 [Pre_treatment.py](file:///e:/学术/3.申博/申博-测井项目/25年项目-江汉油田/软件开发/软件开发/后端/blueprints/Pre_treatment.py) 定义，统一由 `/pretreatment/process` 调度：

- `zscore`：异常样本剔除 + 归一化，保存覆盖目录文件与 DataLoader
- `岩性分类`：聚类归一化处理（KMeans）
- `basic_normalization`：基础归一化 + 生成并保存归一化器
- `casing_bolt_removal`：消除套管栓影响（无需 predict_target）

### 训练模型

模型选择逻辑见 [data_pre.py](file:///e:/学术/3.申博/申博-测井项目/25年项目-江汉油田/软件开发/软件开发/后端/tools/data_pre.py)：

- GRU / LSTM / BiLSTM / TCN / Transformer
- Transformer_KAN / Autoformer_EncoderOnly / BP

训练参数来源见 [tool_for_pre.py](file:///e:/学术/3.申博/申博-测井项目/25年项目-江汉油田/软件开发/软件开发/后端/tools/tool_for_pre.py) `get_parameters`，包含：

- 网络结构参数（hidden_size、num_layers、num_heads 等）
- 训练参数（num_epochs、learning_rate、loss）
- 物理约束参数（phy_equation、phy_loss_type、phy_loss_weight）

### 智能公式映射

核心接口 `/run-smart-formula` 负责：

1. 文件复制与参数准备
2. 执行 `new_main_2.py`
3. 解析结果图、公式图、坐标 JSON、Excel 指标
4. 写入 Smartformula 表并生成批次号

## Socket.IO 事件（前端）

前端 Socket 定义在 [socket.ts](file:///e:/学术/3.申博/申博-测井项目/25年项目-江汉油田/软件开发/软件开发/前端/src/socket.ts)，连接地址固定为 `http://127.0.0.1:5000`。

- `data` 事件：支持 `payload.event === "log"` 的日志消息
- `multitype_log` 事件：
  - `trainloss*` → 训练损失曲线
  - `tuyi*` → 训练曲线
  - `tuer*` → 验证曲线

## 关键差异与待补齐项

- 前端存在 `/pretreatment/process-file` 调用，但后端未实现
- 前端存在 `/FormulaDetail` 调用，但后端未实现

建议在后端补齐对应接口，或在前端移除/替换调用。
