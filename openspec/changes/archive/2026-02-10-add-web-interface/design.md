## Context

IhopeCash 当前通过 `main.py` 提供命令行界面，需要手动确认每个步骤。核心逻辑已经封装在 `backend.py` 的 `BillManager` 类中，但缺少 Web 访问接口。

**现有架构**:
- `config.py`: 统一配置管理
- `backend.py`: BillManager 类封装所有业务逻辑
- `main.py`: 命令行交互界面
- `mail.py`: 邮件下载功能
- `beancount_config.py`: Beancount 导入器配置

**约束**:
- 单用户使用（个人财务工具）
- 需要密码保护（处理敏感财务数据）
- 可能部署到远程服务器
- 需要完全离线运行（不依赖外部 CDN）

## Goals / Non-Goals

**Goals:**
- 提供简洁美观的 Web 界面替代命令行操作
- 实时显示导入进度，无需手动确认每步
- 支持三种导入模式（通常/强制/追加）
- 使用 JWT Token 保护所有接口
- 完全离线运行，无外部依赖
- 保持现有命令行工具可用

**Non-Goals:**
- 多用户管理系统（仅单用户）
- 复杂的权限系统（只需简单密码保护）
- 账本可视化/报表功能（只做导入）
- 移动端适配（桌面浏览器为主）
- 历史任务记录（暂不实现）

## Decisions

### 1. 后端框架: FastAPI

**选择 FastAPI 而非 Flask/Django**

理由:
- **异步支持**: 原生支持 WebSocket，适合实时进度推送
- **自动文档**: 自动生成 OpenAPI 文档，便于调试
- **类型提示**: 基于 Pydantic，参数验证更简单
- **性能**: ASGI 服务器性能优于 WSGI
- **轻量**: 比 Django 更轻，比 Flask 更现代

替代方案:
- Flask + Flask-SocketIO: 需要额外依赖，异步支持不如 FastAPI
- Django: 太重，不需要 ORM 和 admin 等功能

### 2. 认证方案: JWT Token

**选择 JWT 而非 Session**

理由:
- **无状态**: 服务器无需存储 session，重启不影响已登录用户
- **简单**: 单用户场景，JWT 足够安全且实现简单
- **跨域友好**: 未来如果前后端分离部署，JWT 更方便

实现细节:
- 密码明文存储在 `config.yaml`（单用户可接受）
- Token 有效期 7 天（可配置）
- 使用 PyJWT 库生成和验证 token
- 所有 API 和 WebSocket 需要 token 认证

替代方案:
- Session + Cookie: 需要 session 存储，重启后失效
- OAuth2: 过于复杂，单用户无需第三方登录

### 3. 实时通信: WebSocket

**选择 WebSocket 而非 Server-Sent Events (SSE)**

理由:
- **双向通信**: 未来可能需要取消任务等交互
- **FastAPI 原生支持**: uvicorn 内置 WebSocket 支持
- **更标准**: 浏览器支持更好

实现方式:
- 客户端连接时携带 token: `ws://host/ws/progress?token=xxx`
- 服务端维护连接池，任务进度广播到对应连接
- 断线自动重连机制

替代方案:
- SSE: 单向通信，实现更简单，但扩展性差
- 长轮询: 性能差，延迟高

### 4. 前端样式: Tailwind CSS (Standalone CLI)

**选择 Tailwind CLI 而非 CDN 或完整 npm 包**

理由:
- **离线运行**: 构建后的 CSS 文件本地化，无需外部依赖
- **体积小**: 只包含使用的样式类，通常 5-20KB
- **无需 Node.js**: Standalone CLI 是单个可执行文件
- **开发效率**: Utility-first 开发速度快
- **美观**: 现代化的默认样式

构建流程:
```bash
./tailwindcss -i src/input.css -o static/style.css --minify
```

替代方案:
- CDN: 依赖外网，可能被墙或不稳定
- 手写 CSS: 开发效率低，UI 质量难保证
- PicoCSS: 更简单但定制性差

### 5. 前端框架: Vanilla JavaScript

**选择原生 JS 而非 React/Vue**

理由:
- **简单**: 功能不复杂，无需引入框架
- **无构建**: 无需 webpack/vite 等打包工具
- **离线**: 无需 npm 依赖
- **单文件**: HTML + JS 都在一个文件内，部署简单

实现方式:
- 使用 Fetch API 调用后端
- 使用 WebSocket API 接收实时进度
- 使用 localStorage 存储 JWT token

替代方案:
- React/Vue: 功能过于简单，引入框架增加复杂度
- jQuery: 现代浏览器 API 已足够强大，无需额外库

### 6. 进度回调机制

**在 BillManager 中添加回调函数参数**

设计:
```python
def import_month_with_progress(
    self,
    year: str,
    month: str,
    balances: Dict[str, str],
    mode: str,
    progress_callback: Callable[[dict], None]
):
    # 每一步操作前后调用 callback
    progress_callback({
        "step": 1,
        "total": 6,
        "step_name": "download",
        "status": "running",
        "message": "正在下载邮件账单..."
    })
    
    self.download_bills()
    
    progress_callback({
        "step": 1,
        "total": 6,
        "step_name": "download",
        "status": "success",
        "message": "邮件下载完成，共 15 个文件",
        "details": {"files_count": 15}
    })
    # ... 后续步骤
```

6 个步骤:
1. download - 下载邮件账单
2. identify - 识别文件类型
3. create_dir - 创建目录结构
4. extract - 提取交易记录
5. balance - 记录余额断言
6. archive - 归档原始文件

### 7. 三种导入模式实现

**通过参数控制不同行为**

- **normal**: `import_month(force_overwrite=False)` - 目录存在时报错
- **force**: `import_month(force_overwrite=True)` - 删除已有目录
- **append**: `import_append_mode()` - 新增方法，向已有月份追加

追加模式改进:
- 现有 `append_to_month()` 跳过下载和识别
- 新增 `import_append_mode()` 包含完整流程
- 自动生成文件名: `append_{timestamp}.bean`

### 8. 配置扩展

**在 config.yaml 新增 web 配置块**

```yaml
web:
  host: "0.0.0.0"                      # 0.0.0.0 允许外网访问
  port: 8000                            # 默认端口
  password: "change_this_password"      # Web 界面密码
  jwt_secret: "change_random_secret"    # JWT 签名密钥（必须改）
  token_expire_days: 7                  # Token 有效期
```

`config.py` 扩展:
- 添加 `@property` 访问器读取 web 配置
- `_merge_defaults()` 自动补全缺失的配置项
- 保持向后兼容，无 web 配置时不影响命令行工具

### 9. 文件结构

```
web/
├── app.py              # FastAPI 主应用
├── auth.py             # JWT 认证模块
├── tasks.py            # 异步任务管理
├── static/
│   ├── login.html      # 登录页面
│   ├── index.html      # 主界面
│   └── style.css       # 构建后的 Tailwind CSS
├── src/
│   └── input.css       # Tailwind 源文件
├── requirements.txt    # Python 依赖
├── build.sh           # CSS 构建脚本
└── README.md          # 部署文档
```

**模块职责**:
- `app.py`: HTTP 端点、WebSocket 端点、静态文件服务
- `auth.py`: JWT 生成/验证、认证依赖注入
- `tasks.py`: 异步任务队列、进度广播管理

## Risks / Trade-offs

### 1. 密码明文存储

**风险**: `config.yaml` 中密码明文存储，文件泄露会暴露密码

**缓解**:
- 文件权限设置为 600 (仅所有者可读写)
- 建议使用强密码
- 单用户场景，风险可接受
- 未来可改进为 bcrypt hash 存储

### 2. 单线程任务执行

**风险**: FastAPI 默认多 worker，但 BillManager 操作文件不是线程安全的

**缓解**:
- 启动时指定 `--workers 1` 单进程运行
- 使用 asyncio.Lock 保护任务队列
- 同时只允许一个导入任务运行

### 3. WebSocket 断线重连

**风险**: 网络不稳定时 WebSocket 可能断开，导致进度消息丢失

**缓解**:
- 前端实现自动重连机制
- 服务端缓存最近任务状态，重连后可查询
- 最终成功/失败状态通过 HTTP 轮询兜底

### 4. 长时间任务超时

**风险**: 邮件下载或文件处理可能耗时较长，浏览器可能超时

**缓解**:
- WebSocket 保持连接，定期发送心跳
- 设置合理的超时时间（如 10 分钟）
- 显示详细进度，用户知道任务在执行

### 5. Tailwind CSS 构建依赖

**风险**: 开发者需要安装 Tailwind CLI 才能修改样式

**缓解**:
- 提供构建脚本 `build.sh` 简化操作
- 构建后的 `style.css` 提交到 git，用户可直接使用
- 文档说明如何下载 Tailwind CLI

### 6. 没有 HTTPS

**风险**: HTTP 传输密码明文，可能被中间人攻击

**缓解**:
- 本地使用 (localhost) 风险很低
- 生产环境建议用 Nginx 反向代理 + SSL 证书
- 文档说明 HTTPS 配置方法

## Migration Plan

### 部署步骤

1. **安装依赖**
   ```bash
   pip install -r web/requirements.txt
   ```

2. **配置 config.yaml**
   ```yaml
   web:
     host: "0.0.0.0"
     port: 8000
     password: "你的强密码"
     jwt_secret: "随机生成的密钥"
     token_expire_days: 7
   ```

3. **构建前端样式**（可选，已有构建产物）
   ```bash
   cd web
   ./tailwindcss -i src/input.css -o static/style.css --minify
   ```

4. **启动服务**
   ```bash
   cd web
   uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1
   ```

5. **访问界面**
   - 浏览器打开 `http://localhost:8000`
   - 输入 config.yaml 中配置的密码登录

### 生产环境部署（Nginx + SSL）

1. **Nginx 配置示例**
   ```nginx
   server {
       listen 443 ssl;
       server_name your-domain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

2. **使用 systemd 管理服务**
   ```ini
   [Unit]
   Description=IhopeCash Web Service
   After=network.target
   
   [Service]
   Type=simple
   User=your-user
   WorkingDirectory=/path/to/ihopeCash/web
   ExecStart=/path/to/venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000 --workers 1
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

### 回滚策略

如果 Web 界面出现问题:
1. 停止 uvicorn 服务
2. 继续使用命令行工具 `python main.py`（功能不受影响）
3. 删除 `web/` 目录及相关依赖
4. 从 config.yaml 删除 `web` 配置块（可选）

**零风险**: Web 模块完全独立，不影响现有命令行工具。

## Open Questions

1. **追加模式的余额记录**: 确认追加模式也需要记录余额（已确认 - 是的）

2. **Token 刷新机制**: 7 天后需要重新登录，是否需要自动刷新 token？
   - 当前方案: 不刷新，过期后重新登录
   - 可选改进: 临近过期时自动签发新 token

3. **任务取消**: 是否需要支持中途取消导入任务？
   - 当前方案: 不支持取消
   - 风险: 长时间任务无法中断
   - 未来可通过 WebSocket 双向通信实现

4. **错误重试**: 某一步失败后，是否支持从失败步骤重试？
   - 当前方案: 失败后需要重新提交表单
   - 可选改进: 缓存表单数据，提供"重试"按钮
