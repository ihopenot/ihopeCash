## MODIFIED Requirements

### Requirement: All API endpoints require authentication

The system SHALL protect all API endpoints (except /api/auth/login and /api/setup/status) with JWT token authentication. Setup API endpoints (/api/setup/defaults, /api/setup/complete) SHALL also require authentication. The login endpoint MUST implement rate limiting: after 5 failed attempts from the same IP within a time window, the system SHALL block further attempts for 5 minutes. Error responses MUST use generic messages, not exposing internal details.

#### Scenario: API request with valid token
- **WHEN** user sends request with valid JWT token in Authorization header
- **THEN** system processes the request normally

#### Scenario: API request with invalid token
- **WHEN** user sends request with invalid or expired JWT token
- **THEN** system returns 401 Unauthorized error with generic message

#### Scenario: API request without token
- **WHEN** user sends request without Authorization header
- **THEN** system returns 401 Unauthorized error

#### Scenario: Setup status endpoint does not require authentication
- **WHEN** unauthenticated user requests GET /api/setup/status
- **THEN** system returns the setup status normally without requiring authentication

#### Scenario: Setup API endpoints require authentication
- **WHEN** unauthenticated user requests GET /api/setup/defaults or POST /api/setup/complete
- **THEN** system returns 401 Unauthorized error

#### Scenario: Login rate limiting
- **WHEN** 5 failed login attempts from the same IP address within a time window
- **THEN** system returns 429 Too Many Requests error
- **THEN** system blocks the IP for 5 minutes

#### Scenario: Rate limit reset
- **WHEN** 5 minutes have passed since the IP was blocked
- **THEN** system allows login attempts from the IP again

#### Scenario: Error responses do not expose internal details
- **WHEN** any API endpoint encounters an internal error
- **THEN** system returns generic error message to client (e.g., "操作失败")
- **THEN** system logs the detailed error information server-side

### Requirement: Authentication works with env.yaml password during setup

During setup mode (config.yaml does not exist), the system SHALL authenticate users using the password from env.yaml's web.password field.

#### Scenario: Login during setup mode
- **WHEN** setup_required is True
- **AND** user submits the password from env.yaml's web.password
- **THEN** system returns a valid JWT token

#### Scenario: JWT secret from env.yaml during setup
- **WHEN** setup_required is True
- **THEN** JWT tokens are signed using jwt_secret from env.yaml

## ADDED Requirements

### Requirement: JWT secret 默认值必须自动替换
系统启动时 MUST 检测 `jwt_secret` 是否为默认值 `"change_this_secret_key"`。如果是，系统 SHALL 自动生成一个随机的安全密钥并写入 env.yaml。

#### Scenario: 检测到默认 JWT secret
- **WHEN** 系统启动时 env.yaml 中 `jwt_secret` 为 `"change_this_secret_key"`
- **THEN** 系统使用 `secrets.token_hex(32)` 生成随机密钥
- **THEN** 系统将新密钥写入 env.yaml
- **THEN** 系统使用新密钥签发 JWT token

#### Scenario: 已自定义 JWT secret
- **WHEN** 系统启动时 env.yaml 中 `jwt_secret` 不是默认值
- **THEN** 系统直接使用该密钥，不做修改

### Requirement: WebSocket 认证必须通过消息传递 token
WebSocket 连接 MUST NOT 在 URL query parameter 中传递 JWT token。token SHALL 在 WebSocket 连接建立后通过首条消息发送。

#### Scenario: WebSocket 认证流程
- **WHEN** 前端建立 WebSocket 连接
- **THEN** 连接 URL 不包含 token 参数
- **THEN** 连接建立后，前端发送 `{"token": "<jwt_token>", "task_id": "<task_id>"}` 作为首条消息
- **THEN** 后端验证 token 有效后开始推送进度数据

#### Scenario: WebSocket token 无效
- **WHEN** WebSocket 首条消息中的 token 无效或缺失
- **THEN** 后端关闭连接，返回 1008 (Policy Violation) 关闭码

### Requirement: 前端 token 必须存储在 sessionStorage
所有前端页面 MUST 使用 `sessionStorage`（而非 `localStorage`）存储 JWT token，以确保标签页关闭后 token 自动清除。

#### Scenario: 登录成功后存储 token
- **WHEN** 用户登录成功
- **THEN** 前端使用 `sessionStorage.setItem('auth_token', token)` 存储 token

#### Scenario: 标签页关闭后 token 清除
- **WHEN** 用户关闭浏览器标签页
- **THEN** sessionStorage 中的 token 自动清除
- **THEN** 再次打开页面时需要重新登录

### Requirement: 前端认证函数必须提取为共享模块
所有 HTML 页面中重复的认证函数（`checkAuth()`, `getAuthHeaders()` 等）MUST 提取到共享的 `web/static/auth.js` 文件中。各页面通过 `<script src="/static/auth.js">` 引用。

#### Scenario: 共享 auth.js 文件存在
- **WHEN** 检查 `web/static/auth.js` 文件
- **THEN** 文件包含 `checkAuth()`, `getAuthHeaders()`, `escapeHtml()` 等通用函数

#### Scenario: 各 HTML 页面引用共享文件
- **WHEN** 检查 index.html, login.html, setup.html, config.html
- **THEN** 每个文件通过 `<script src="/static/auth.js">` 引用共享模块
- **THEN** 不再内联定义重复的认证函数

### Requirement: Import 请求必须验证年月参数
导入 API 端点 MUST 验证 year 和 month 参数的合法性。

#### Scenario: 合法的年月参数
- **WHEN** 用户提交 year="2024", month="12"
- **THEN** 系统正常处理请求

#### Scenario: 非法的月份
- **WHEN** 用户提交 month="13" 或 month="0"
- **THEN** 系统返回 400 Bad Request 错误

#### Scenario: 非法的年份
- **WHEN** 用户提交非数字的 year
- **THEN** 系统返回 400 Bad Request 错误
