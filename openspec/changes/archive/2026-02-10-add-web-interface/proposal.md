## Why

当前 IhopeCash 只能通过命令行工具导入账单，需要手动确认每个步骤，操作繁琐且容易出错。添加 Web 界面可以简化操作流程，提供更直观的用户体验，实时查看导入进度，并支持远程访问。

## What Changes

- 新增基于 FastAPI 的 Web 后端服务
- 新增现代化的 Web 前端界面（使用 Tailwind CSS）
- 实现 JWT Token 认证保护所有接口
- 支持三种导入模式：通常模式、强制覆盖模式、追加模式
- 通过 WebSocket 实时推送导入进度（6 个步骤）
- 扩展配置系统支持 Web 服务配置（host、port、password 等）
- 增强 BillManager 支持进度回调机制
- 保留现有命令行工具，两种方式并存

## Capabilities

### New Capabilities

- `web-authentication`: Web 界面的用户认证系统，基于 JWT Token
- `web-import-interface`: Web 界面的账单导入功能，包括表单、实时进度展示
- `import-mode-selection`: 三种导入模式的选择和实现（通常/强制/追加）
- `realtime-progress-tracking`: 导入过程的实时进度跟踪和推送机制
- `web-configuration`: Web 服务的配置管理（host、port、认证等）

### Modified Capabilities

<!-- 无现有 capability 需要修改 -->

## Impact

**新增文件**:
- `web/app.py` - FastAPI 主应用
- `web/auth.py` - JWT 认证模块
- `web/tasks.py` - 异步任务管理
- `web/static/login.html` - 登录页面
- `web/static/index.html` - 主界面
- `web/static/style.css` - Tailwind CSS 构建产物
- `web/src/input.css` - Tailwind CSS 源文件
- `web/requirements.txt` - Web 依赖
- `web/build.sh` - CSS 构建脚本
- `web/README.md` - Web 模块文档

**修改文件**:
- `config.py` - 扩展支持 web 配置项
- `backend.py` - 添加进度回调机制、改进追加模式

**依赖新增**:
- fastapi
- uvicorn[standard]
- pyjwt
- websockets
- python-multipart

**不影响**:
- 现有命令行工具 `main.py` 保持不变
- 现有配置结构向后兼容
- 现有账本数据格式不变
