## 1. 扩展配置系统

- [x] 1.1 在 config.py 的 _get_default_config() 中添加 web 配置块默认值
- [x] 1.2 在 config.py 添加 web 配置属性访问器 (web_host, web_port, web_password, jwt_secret, token_expire_days)
- [x] 1.3 在 config.py 添加配置验证方法，检查默认密码和密钥是否被修改
- [x] 1.4 更新 config.yaml 示例文件，添加 web 配置块

## 2. 增强 BillManager 后端

- [x] 2.1 在 backend.py 定义进度回调类型 ProgressCallback
- [x] 2.2 在 backend.py 添加 import_month_with_progress() 方法，支持进度回调
- [x] 2.3 在 import_month_with_progress() 的 6 个步骤前后调用回调函数推送进度
- [x] 2.4 在 backend.py 添加 import_append_mode() 方法，支持追加模式的完整流程（包括下载）
- [x] 2.5 修改 append_to_month() 方法，确保支持时间戳文件名生成
- [x] 2.6 在进度消息中添加 details 字段，包含步骤特定信息（文件数、交易数等）

## 3. Web 认证模块

- [x] 3.1 创建 web/ 目录结构
- [x] 3.2 创建 web/auth.py 文件
- [x] 3.3 在 auth.py 实现 create_jwt_token() 函数，生成 JWT token
- [x] 3.4 在 auth.py 实现 verify_jwt_token() 函数，验证 JWT token
- [x] 3.5 在 auth.py 实现 verify_password() 函数，对比密码与配置
- [x] 3.6 在 auth.py 实现 get_current_user() 依赖注入函数，用于 FastAPI 端点保护

## 4. Web 任务管理模块

- [x] 4.1 创建 web/tasks.py 文件
- [x] 4.2 实现 TaskManager 类，管理异步导入任务
- [x] 4.3 实现任务队列和任务状态存储（使用 asyncio.Queue）
- [x] 4.4 实现 WebSocket 连接池管理
- [x] 4.5 实现进度广播函数，向所有连接的 WebSocket 客户端推送消息
- [x] 4.6 实现任务执行函数，包装 BillManager.import_month_with_progress() 调用

## 5. FastAPI 应用主体

- [x] 5.1 创建 web/app.py 文件，初始化 FastAPI 应用
- [x] 5.2 配置静态文件服务，挂载 /static 路径
- [x] 5.3 实现 POST /api/auth/login 端点，验证密码并返回 JWT token
- [x] 5.4 实现 GET /api/config 端点，返回余额账户列表和默认年月
- [x] 5.5 实现 POST /api/import 端点，接收导入请求并启动异步任务
- [x] 5.6 实现 WebSocket /ws/progress 端点，处理客户端连接和消息推送
- [x] 5.7 在 WebSocket 端点添加 token 验证（从查询参数读取）
- [x] 5.8 添加 CORS 中间件（如果需要）
- [x] 5.9 添加启动时配置验证，警告默认密码和密钥未修改

## 6. 前端 - 登录页面

- [x] 6.1 创建 web/static/ 目录
- [x] 6.2 创建 web/static/login.html 文件
- [x] 6.3 实现登录表单 HTML 结构（密码输入框、登录按钮）
- [x] 6.4 添加 JavaScript 处理登录表单提交
- [x] 6.5 实现调用 POST /api/auth/login 获取 token
- [x] 6.6 实现将 token 存储到 localStorage
- [x] 6.7 实现登录成功后重定向到主页面
- [x] 6.8 实现登录失败时显示错误消息

## 7. 前端 - 主界面

- [x] 7.1 创建 web/static/index.html 文件
- [x] 7.2 实现页面加载时检查 token，无效则重定向到登录页
- [x] 7.3 实现调用 GET /api/config 获取余额账户列表
- [x] 7.4 动态生成余额输入表单（根据账户列表）
- [x] 7.5 实现年份和月份下拉选择器（默认值为上个月）
- [x] 7.6 实现三种导入模式的单选按钮（通常/强制/追加）
- [x] 7.7 显示每种模式的说明文本
- [x] 7.8 实现"开始导入"按钮点击处理
- [x] 7.9 实现表单验证（余额字段非空、数字格式）
- [x] 7.10 实现调用 POST /api/import 提交导入请求
- [x] 7.11 实现禁用表单和显示进度日志区域

## 8. 前端 - 实时进度显示

- [x] 8.1 实现 WebSocket 连接到 /ws/progress（携带 token）
- [x] 8.2 实现接收进度消息并解析 JSON
- [x] 8.3 实现根据消息状态显示不同图标（✓ / ⏳ / ❌）
- [x] 8.4 实现显示步骤进度 [X/6]
- [x] 8.5 实现日志区域自动滚动到底部
- [x] 8.6 实现 WebSocket 断线自动重连机制
- [x] 8.7 实现显示成功/失败最终摘要
- [x] 8.8 实现"重置"按钮功能，清空表单和日志
- [x] 8.9 实现"退出登录"按钮，清除 token 并重定向到登录页

## 9. 前端样式

- [x] 9.1 创建 web/src/ 目录
- [x] 9.2 创建 web/src/input.css 文件，导入 Tailwind 基础样式
- [x] 9.3 在 input.css 添加自定义 Tailwind 组件类（按钮、日志条目等）
- [x] 9.4 下载 Tailwind CLI standalone 可执行文件到 web/
- [x] 9.5 创建 web/build.sh 脚本，运行 Tailwind CLI 构建命令
- [x] 9.6 运行构建生成 web/static/style.css
- [x] 9.7 在 login.html 和 index.html 引入 style.css
- [x] 9.8 应用 Tailwind 类名到 HTML 元素实现美观布局

## 10. 依赖和文档

- [x] 10.1 创建 web/requirements.txt 文件，列出 fastapi、uvicorn、pyjwt、websockets 等依赖
- [x] 10.2 创建 web/README.md 文档
- [x] 10.3 在 README 添加安装依赖说明
- [x] 10.4 在 README 添加配置 config.yaml 说明（必须修改密码和密钥）
- [x] 10.5 在 README 添加运行服务命令说明
- [x] 10.6 在 README 添加生产环境部署说明（Nginx + SSL）
- [x] 10.7 在 README 添加 systemd 服务配置示例
- [x] 10.8 在 README 添加常见问题排查

## 11. 测试

- [x] 11.1 本地测试登录功能（正确密码、错误密码）
- [x] 11.2 本地测试通常模式导入（新目录、已存在目录）
- [x] 11.3 本地测试强制模式导入（覆盖已存在目录）
- [x] 11.4 本地测试追加模式导入（追加到已有月份、目录不存在）
- [x] 11.5 测试实时进度推送（6 个步骤是否正常显示）
- [x] 11.6 测试错误处理（邮件下载失败、目录已存在等）
- [x] 11.7 测试 WebSocket 断线重连
- [x] 11.8 测试 token 过期后重新登录
- [x] 11.9 测试表单验证（空余额、非数字输入）
- [x] 11.10 测试 UI 响应式布局（不同浏览器窗口大小）

## 12. 最终检查

- [x] 12.1 确保 config.yaml.example 包含完整的 web 配置示例
- [x] 12.2 确保 .gitignore 包含 web/tailwindcss 可执行文件（可选）
- [x] 12.3 确保 web/static/style.css 已提交到 git（构建产物）
- [x] 12.4 确保现有命令行工具 main.py 功能不受影响
- [x] 12.5 验证所有 spec 要求已实现
- [x] 12.6 更新项目主 README.md，添加 Web 界面使用说明
