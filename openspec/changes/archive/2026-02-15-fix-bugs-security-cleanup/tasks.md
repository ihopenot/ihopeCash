## 1. backend.py 安全与 Bug 修复

- [x] 1.1 将 `bean_extract()` 中 `subprocess.run(cmd, shell=True)` 改为 list 参数形式
- [x] 1.2 将 `bean_archive()` 中 `subprocess.run(cmd, shell=True)` 改为 list 参数形式
- [x] 1.3 修复 `download_bills()` 可变默认参数 `passwords=[]` 改为 `passwords=None`
- [x] 1.4 修复 `import_month_with_progress` 追加模式调用处缺少 `passwords` 参数的 bug
- [x] 1.5 将所有 `open()` 调用改为 `with` 语句（11 处文件句柄泄露）
- [x] 1.6 将仅创建空文件的 `open(path, "w").close()` 改为 `pathlib.Path(path).touch()`
- [x] 1.7 将所有硬编码 `/` 路径拼接改为 `os.path.join()`
- [x] 1.8 将函数内 `import glob` 和 `from datetime import datetime` 移到文件顶部
- [x] 1.9 将所有 `raise Exception(...)` 改为 `raise RuntimeError(...)` 并使用 `from e` 保留堆栈
- [x] 1.10 在异常处理的 `except` 块中添加 `logging` 日志记录

## 2. config.py 安全与质量修复

- [x] 2.1 将所有 `yaml.FullLoader` 替换为 `yaml.SafeLoader`
- [x] 2.2 修复属性方法返回内部可变引用：`balance_accounts` 等返回 `copy.deepcopy()`
- [x] 2.3 修复 `get_detail_mappings()` 中 ImportError try-except 范围过宽，缩窄到仅 import 语句；返回原始数据时使用 deepcopy
- [x] 2.4 修复 `update_from_web()` 使用 `dict.update()` 浅合并改为深度合并

## 3. mail.py 安全与 Bug 修复

- [x] 3.1 移除 `decrypt_zip()` 中将密码打印到日志的 print 语句（第 68、77 行）
- [x] 3.2 修复 `get_data()` 无附件时隐式返回 None，改为抛出明确异常
- [x] 3.3 修复 `decrypt_zip()` 返回值为 None 时的调用方（`post_process`）未检查的问题
- [x] 3.4 修复 IMAP 连接（`DownloadFiles()`）使用 try-finally 确保 `server.logout()`
- [x] 3.5 修复裸 `except: pass` 和 `except Exception as e: pass` 改为具体异常类型并记录日志
- [x] 3.6 修复类名拼写错误 `BaseEmailHanlder` → `BaseEmailHandler`
- [x] 3.7 移除未使用的 `init()` 死代码方法

## 4. main.py 和 beancount_config.py 修复

- [x] 4.1 修复 `main.py:69` 拼写错误 "comfirm" → "confirm"
- [x] 4.2 修复 `main.py:39` `traceback.print_exception(e)` 改为 `traceback.print_exc()`
- [x] 4.3 修复 `main.py:57-58` 用户输入年月验证
- [x] 4.4 修复 `beancount_config.py:43` `sys.argv` 无边界检查
- [x] 4.5 修复 `beancount_config.py:43-45` stdout 重定向文件句柄泄露，改用 `with` 或 `atexit`
- [x] 4.6 修复 `beancount_config.py:11` `sys.path.append(os.getcwd())` 改为使用脚本目录

## 5. Web 后端安全加固

- [x] 5.1 实现 JWT secret 默认值自动替换：启动时检测并生成随机密钥写入 env.yaml
- [x] 5.2 实现登录速率限制：内存级 IP 失败计数，5 次失败锁定 5 分钟
- [x] 5.3 将 WebSocket token 从 query parameter 改为首条消息传递（修改 `web/app.py` WebSocket 端点）
- [x] 5.4 修改 `web/auth.py` 添加 `verify_ws_token` 支持从消息中验证 token
- [x] 5.5 将所有 API 错误响应改为通用消息，不暴露内部细节
- [x] 5.6 添加导入 API 的 year/month 参数校验（1<=month<=12, year 为数字）
- [x] 5.7 修复 `web/app.py:748` 账户开户日期从 `1999-01-01` 改为 `datetime.date.today().isoformat()`

## 6. 前端安全与去重

- [x] 6.1 创建 `web/static/auth.js` 共享模块，包含 `checkAuth()`, `getAuthHeaders()`, `escapeHtml()` 函数
- [x] 6.2 修改 `login.html` 引用 auth.js，移除内联重复函数，localStorage 改为 sessionStorage
- [x] 6.3 修改 `index.html` 引用 auth.js，移除内联重复函数，localStorage 改为 sessionStorage，WebSocket 连接改为消息传递 token
- [x] 6.4 修改 `setup.html` 引用 auth.js，移除内联重复函数，localStorage 改为 sessionStorage，修复所有 innerHTML XSS（使用 escapeHtml）
- [x] 6.5 修改 `config.html` 引用 auth.js，移除内联重复函数，localStorage 改为 sessionStorage，修复所有 innerHTML XSS
- [x] 6.6 修复 `config.html` 交易摘要过滤默认值覆盖空配置的 bug
- [x] 6.7 移除 `style.css` 中未使用的 `.password-toggle` 样式

## 7. Docker 部署加固

- [x] 7.1 Dockerfile 添加非 root 用户（`appuser`，UID 1000）和 `USER` 指令
- [x] 7.2 Dockerfile 添加 HEALTHCHECK 指令
- [x] 7.3 `docker/nginx.conf` 添加安全 Headers（HSTS, X-Content-Type-Options, X-Frame-Options）
- [x] 7.4 `docker/nginx.conf` 加固 SSL/TLS 配置（优先 TLS 1.3，ECDHE 加密套件，session cache）
- [x] 7.5 `docker/entrypoint.sh` 添加后台进程（Fava）健康检查
- [x] 7.6 `docker-compose.yml` 添加资源限制（memory, cpus）和 restart 策略
- [x] 7.7 `docker-compose.yml` 添加日志配置（max-size, max-file）
- [x] ~~7.8 `docker-compose.yml` 将 env.yaml 挂载改为只读（`:ro`）~~ 已回退：JWT 密钥自动生成需要写入 env.yaml

## 8. 依赖版本固定

- [x] 8.1 为 `requirements.txt` 中所有依赖添加版本范围约束
- [x] 8.2 为 `web/requirements.txt` 中所有依赖添加版本范围约束
