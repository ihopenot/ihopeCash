## Why

项目全面审计发现了大量 bug、安全漏洞、资源泄露和代码质量问题。包括 shell 命令注入、JWT 默认密钥硬编码、文件句柄泄露、XSS 漏洞、密码日志泄露、依赖版本未固定等。这些问题影响项目的安全性、稳定性和可维护性，需要统一修复。

排除项：明文密码比较改用哈希（暂不做）、CSRF 保护（暂不做）、逻辑架构拆分（暂不做）。

## What Changes

- 修复 `backend.py` 中 `subprocess.run(shell=True)` 的命令注入漏洞，改为 list 参数形式
- 修复 `backend.py:428` 缺少 `passwords` 参数的运行时 bug
- 修复 `backend.py` 中所有 `open()` 未使用 `with` 语句导致的文件句柄泄露（11 处）
- 修复 `backend.py:83` 可变默认参数 `passwords=[]`
- 将 `backend.py` 中硬编码路径分隔符 `/` 改为 `os.path.join()` 或 `pathlib`
- 将 `backend.py` 中函数内的 `import` 移到文件顶部
- 改进 `backend.py` 异常处理：使用 `raise ... from e`，添加日志，使用具体异常类型
- 修复 `config.py` 中 JWT 默认密钥问题：启动时检测默认值则拒绝运行或自动生成随机密钥
- 将 `config.py` 中 `yaml.FullLoader` 改为 `yaml.SafeLoader`
- 修复 `config.py` 属性方法返回内部可变引用的问题（deepcopy）
- 修复 `config.py:475` `update_from_web` 浅合并问题
- 移除 `mail.py:68, 77` 中密码泄露到日志的代码
- 修复 `mail.py` 中 IMAP 连接泄露（使用 try-finally）
- 修复 `mail.py` 中 `decrypt_zip` 返回 None 未处理的问题
- 修复 `mail.py` 中 `get_data()` 无附件时隐式返回 None 的问题
- 修复 `mail.py` 中异常吞噬和裸 `except` 问题
- 修复 `mail.py:16` 类名拼写错误 `BaseEmailHanlder` → `BaseEmailHandler`
- 修复 `mail.py:20` 未使用的 `init()` 死代码
- 修复 `beancount_config.py:43` `sys.argv` 无边界检查
- 修复 `beancount_config.py:43-45` stdout 重定向文件句柄泄露
- 修复 `beancount_config.py:11` `sys.path` 使用 cwd 而非脚本目录
- 修复 `main.py:69` "comfirm" 拼写错误
- 修复 `main.py:39` `traceback.print_exception` 用法
- 修复 `main.py:57-58` 用户输入未验证
- 修复 `web/app.py` 中 WebSocket token 从 query parameter 改为首条消息传递
- 修复 `web/app.py:748` 账户开户日期硬编码为 `1999-01-01` 改为当前日期
- 修复 `web/app.py` 错误信息泄露，使用通用错误消息
- 添加 `web/app.py` 登录速率限制
- 修复 `web/app.py` 年月参数缺少校验
- 修复前端 `setup.html`、`config.html` 中 `innerHTML` 导致的 XSS 漏洞
- 将前端 localStorage token 改为 sessionStorage（降低持久化风险）
- 提取前端重复的认证函数到共享 `auth.js`
- 修复 `config.html:693` 默认筛选列表覆盖空配置的 bug
- 固定 `requirements.txt` 和 `web/requirements.txt` 中的依赖版本
- Docker：添加非 root 用户运行
- Docker：添加 HEALTHCHECK
- Docker：Nginx 添加安全 Headers
- Docker：改进 SSL/TLS 配置
- Docker：改进 `entrypoint.sh` 错误处理
- Docker：`docker-compose.yml` 添加资源限制和日志配置
- 移除 `style.css` 中未使用的 `.password-toggle`

## Capabilities

### New Capabilities

（无新增能力）

### Modified Capabilities

- `backend-bill-operations`: 修复 shell 注入、文件泄露、缺少参数、可变默认参数、路径兼容等 bug
- `web-authentication`: JWT 默认密钥启动检查、WebSocket token 传递方式、登录速率限制、前端 token 存储改进
- `web-config-editor`: 修复 XSS 漏洞、默认筛选列表覆盖 bug
- `setup-wizard`: 修复 XSS 漏洞
- `unified-config-management`: YAML SafeLoader、属性返回 deepcopy、浅合并修复
- `docker-deployment`: 非 root 用户、安全 Headers、SSL 加固、HEALTHCHECK、资源限制

## Impact

- **后端核心文件**: `backend.py`, `config.py`, `mail.py`, `main.py`, `beancount_config.py`
- **Web 应用**: `web/app.py`, `web/auth.py`, `web/tasks.py`
- **前端页面**: `web/static/index.html`, `web/static/login.html`, `web/static/setup.html`, `web/static/config.html`, `web/static/style.css`
- **新增文件**: `web/static/auth.js`（共享认证函数）
- **部署文件**: `Dockerfile`, `docker-compose.yml`, `docker/nginx.conf`, `docker/entrypoint.sh`
- **依赖文件**: `requirements.txt`, `web/requirements.txt`
- **无 Breaking Changes**: 所有修复保持现有接口兼容
