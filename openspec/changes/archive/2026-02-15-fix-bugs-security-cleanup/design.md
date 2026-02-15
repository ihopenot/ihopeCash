## Context

项目全面审计发现 5 个严重漏洞、9 个高危问题、11 个中等问题和 9 个低级问题。涉及后端核心（`backend.py`, `config.py`, `mail.py`, `main.py`, `beancount_config.py`）、Web 层（`web/app.py`, `web/auth.py`, `web/tasks.py`）、前端（4 个 HTML 文件）和部署配置（Docker 相关文件）。

当前状态：项目功能正常运行但存在安全和稳定性风险。

## Goals / Non-Goals

**Goals:**
- 消除所有命令注入漏洞
- 修复所有资源泄露（文件句柄、网络连接）
- 加固 JWT 和认证安全
- 修复前端 XSS 漏洞
- 改进错误处理和日志
- 加固 Docker 部署安全
- 固定依赖版本
- 修复所有已知 bug 和拼写错误

**Non-Goals:**
- 不改为密码哈希（bcrypt/argon2）验证方式
- 不添加 CSRF 保护
- 不做逻辑架构拆分（config.py、backend.py 模块化）
- 不重写前端为 SPA 框架

## Decisions

### D1: subprocess 调用方式

**决定：** 将所有 `subprocess.run(cmd, shell=True)` 改为 list 参数形式，不使用 shell。

**原因：** `shell=True` + f-string 拼接是经典的命令注入漏洞。list 形式由 Python 直接执行，不经过 shell 解释。

**具体变更：**
- `bean-extract` 调用：`subprocess.run(["bean-extract", "beancount_config.py", self.rawdata_path, "--", output_file], ...)`
- `bean-file` 调用：`subprocess.run(["bean-file", "-o", self.archive_path, "beancount_config.py", self.rawdata_path], ...)`

### D2: 文件句柄修复策略

**决定：** 全部改用 `with` 语句；对于仅创建空文件的 `open(path, "w").close()` 改用 `pathlib.Path(path).touch()`。

**原因：** `with` 是 Python 标准的资源管理方式，保证异常时也能正确关闭文件。

### D3: 路径处理

**决定：** 使用 `os.path.join()` 替代所有硬编码的 `/` 路径拼接。

**原因：** 项目在 Windows 上运行（`env` 显示 `platform: win32`），`os.path.join` 自动处理平台差异。不使用 `pathlib` 是因为改动量最小。

### D4: JWT 安全加固

**决定：**
1. 启动时检测 `jwt_secret` 是否为默认值 `"change_this_secret_key"`，如果是则自动生成随机密钥并写入 env.yaml。
2. WebSocket token 从 query parameter 改为在 WebSocket 连接建立后通过首条消息传递。

**替代方案考虑：**
- 方案 A：拒绝启动（用户体验差，新部署者困惑）
- 方案 B：自动生成随机密钥（选择此方案——安全且零摩擦）
- 对于 web_password 保持默认值 `"change_this_password"` 不变，因为密码修改涉及哈希改造，属于排除范围

### D5: 前端 XSS 修复

**决定：** 将所有使用 `innerHTML` 拼接用户数据的地方改为 DOM API（`createElement` + `textContent`）或模板字面量中对变量进行 HTML 转义。

**转义函数：**
```javascript
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
```

### D6: 前端代码去重

**决定：** 提取共享的 `auth.js` 文件，包含 `checkAuth()`, `getAuthHeaders()`, `escapeHtml()` 等通用函数。所有 HTML 页面引用此文件。

### D7: Token 存储

**决定：** 从 `localStorage` 改为 `sessionStorage`。

**原因：** `sessionStorage` 在标签页关闭后自动清除，降低 token 持久化泄露风险。虽然仍可被 XSS 读取，但结合 D5 的 XSS 修复可大幅降低风险。改为 httpOnly cookie 需要后端大幅改造，不在本次范围。

### D8: 登录速率限制

**决定：** 在 `web/app.py` 中实现简单的内存级速率限制，使用 dict 记录 IP 的失败次数和时间窗口。5 次失败后锁定 5 分钟。

**原因：** 不引入新依赖（如 slowapi），实现简单有效。单进程/少量用户场景下内存方案足够。

### D9: YAML SafeLoader

**决定：** 将所有 `yaml.FullLoader` 替换为 `yaml.SafeLoader`。

**原因：** 配置文件不需要 Python 对象实例化功能，SafeLoader 更安全。

### D10: Docker 安全加固

**决定：**
1. Dockerfile 添加 `RUN useradd -m -u 1000 appuser` 和 `USER appuser`
2. Nginx 添加安全 headers（HSTS, X-Content-Type-Options, X-Frame-Options）
3. SSL 配置加强（优先 TLS 1.3，强加密套件）
4. 添加 HEALTHCHECK 指令
5. `entrypoint.sh` 添加后台进程健康检查
6. `docker-compose.yml` 添加资源限制和日志配置

### D11: 依赖版本固定

**决定：** 为 `requirements.txt` 和 `web/requirements.txt` 中所有依赖添加版本范围约束（`>=x.y.z,<next_major`）。

### D12: mail.py 错误处理改进

**决定：**
1. `get_data()` 无附件时 raise 明确异常
2. `decrypt_zip` 返回值检查
3. IMAP 连接使用 try-finally 确保 logout
4. 移除密码 print 语句
5. 具体化异常类型（`RuntimeError` 替代 bare `except`）

## Risks / Trade-offs

- [风险] 自动生成 JWT secret 可能导致已有 token 失效 → 缓解：仅在检测到默认值时触发，已修改过的部署不受影响
- [风险] sessionStorage 导致每次打开新标签都需要重新登录 → 缓解：这是可接受的安全-便利权衡
- [风险] 内存级速率限制在重启后丢失 → 缓解：单用户场景可接受
- [风险] SafeLoader 可能破坏使用了 Python 对象的配置文件 → 缓解：检查确认配置文件中无 Python 对象标签
- [风险] Docker 非 root 用户可能导致文件权限问题 → 缓解：在 Dockerfile 中正确设置目录权限
