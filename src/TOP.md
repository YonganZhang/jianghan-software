# 江汉 Software 项目部署 — 当前状态与待办

## 项目概况

| 项目 | 值 |
|------|------|
| 项目名 | 江汉 Software（Flask + Vue 3 全栈） |
| 部署目录 | `D:\projects\software\` |
| conda 环境 | `software` (Python 3.10) |
| 本地端口 | 5000 |
| FRP 公网端口 | 8447 (152.136.225.228:8447) |
| 域名 | software.yongan.site:8447（DNS 待配置） |
| 自启任务 | `JianghanSoftware`（schtasks ONSTART） |
| 启动脚本 | `D:\projects\software\start_deploy.bat` |

## 已完成

- [x] 项目文件传输到 `D:\projects\software\`
- [x] conda 环境 `software` (Py3.10) 创建 + 所有 Python 依赖安装
- [x] PyTorch + CUDA 安装（GPU 推理可用）
- [x] PySR/juliacall/juliapkg Python 包安装
- [x] 前端 `npm install` + `npm run build`（dist 已生成）
- [x] FRP 端口映射 5000→8447（`D:\frp\frpc.toml` 已配置，frpc 已重启）
- [x] 腾讯云防火墙 TCP 8447 已放行
- [x] 启动脚本 `start_deploy.bat` 已创建
- [x] 开机自启任务 `JianghanSoftware` 已注册
- [x] Flask 服务已通过 `schtasks /Run` 启动并验证
- [x] HTTP 200 验证通过：Tailscale (100.80.89.12:5000) + FRP (152.136.225.228:8447)
- [x] 数据库空库自动初始化（admin/admin）

## 待完成（需要宁波机 AI 处理）

### 1. 安装 Julia 运行时（优先级：中）

PySR 智能公式映射功能依赖 Julia 运行时。目前 Python 包（pysr, juliacall, juliapkg）已安装，但系统级 Julia 二进制未安装。

**操作步骤：**
1. 下载 Julia 1.10.x Windows 安装包（或 portable 版解压到 `D:\Julia\`）
2. 将 `D:\Julia\bin` 加入系统 PATH
3. 验证：`julia --version`
4. 在 software conda 环境中验证：`D:\Anaconda\envs\software\python.exe -c "import pysr; print('OK')"`
   - 首次运行 PySR 会自动编译 Julia 包，耗时较长（可能 10-30 分钟）

> 注意：不装 Julia 不影响项目其他功能（训练、预测、数据管理等），只影响智能公式映射。

### 2. 验证开机自启（优先级：低）

目前服务是通过手动 `schtasks /Run /TN JianghanSoftware` 启动的，尚未经过重启验证。

**验证方法：** 下次宁波机重启后，检查：
- `netstat -ano | findstr :5000 | findstr LISTENING`
- `curl http://127.0.0.1:5000/`

如果没有自动启动，检查任务计划程序中 `JianghanSoftware` 的运行记录和错误信息。

## 待用户手动完成

### DNS A 记录

在腾讯云 DNSPod 添加：
- 类型：A
- 主机记录：`software`
- 记录值：`152.136.225.228`
- 域名：`yongan.site`

配置后可通过 `http://software.yongan.site:8447` 访问。

## 关键路径

```
D:\projects\software\
├── backend\
│   ├── app.py                  # Flask 主入口
│   ├── instance\wenjie.db      # SQLite 数据库（自动创建）
│   └── logs\
│       ├── backend.log         # Flask 运行日志
│       └── deploy.log          # 启动脚本输出日志
├── frontend\
│   └── dist\                   # Vue 3 构建产物（Flask 直接 serve）
├── start_deploy.bat            # 启动脚本（schtasks 调用）
└── start_debug.py              # 调试启动脚本（可删除）
    start_flask.py              # 备用启动脚本（可删除）
```

## 启动方式

```cmd
:: 手动启动
schtasks /Run /TN JianghanSoftware

:: 手动停止
taskkill /F /IM python.exe /FI "WINDOWTITLE eq D:\projects\software*"
:: 或找 PID 后 taskkill /F /PID <pid>

:: 查看状态
netstat -ano | findstr :5000
```

## 注意事项

- `start_deploy.bat` 中设置了 `PYTHONIOENCODING=utf-8`，这是必须的（代码中有 emoji 字符，Windows GBK 默认编码会崩溃）
- 通过 SSH 后台启动进程（subprocess.Popen / PowerShell Start-Process）在 Windows 上不可靠，必须通过 schtasks 启动
- `debug=True` 目前开启中（app.py L292），生产环境建议改为 `False`
