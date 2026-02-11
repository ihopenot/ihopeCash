## 1. Docker 基础设施

- [x] 1.1 创建 `.dockerignore`，排除 `.git`、`__pycache__`、`data/`、`rawdata/`、`archive/`、`certs/`、`*.pyc`、`.env` 等文件
- [x] 1.2 创建 `Dockerfile`：基于 `python:3.12-slim`，安装 nginx、openssl，安装项目所有 Python 依赖（requirements.txt、web/requirements.txt、china_bean_importers、beancount、fava），复制项目文件，设置工作目录为 `/app`
- [x] 1.3 创建 `docker/nginx.conf`：配置 80 端口 HTTP→HTTPS 重定向，443 端口 SSL + 反向代理（`/` → `:8000`，`/fava/` → `:5000/fava/`），包含 WebSocket 代理支持
- [x] 1.4 创建 `docker/entrypoint.sh`：检测 `/app/certs/cert.pem` 和 `key.pem` 是否存在，不存在则用 openssl 生成自签证书；启动 nginx（后台）；启动 fava（后台，`--prefix /fava`）；启动 uvicorn（前台）
- [x] 1.5 创建 `docker-compose.yml`：定义服务、端口映射（80:80、443:443）、volume 挂载（config.yaml、data/、rawdata/、archive/、main.bean、accounts.bean、certs/）、restart 策略

## 2. Web 前端导航

- [x] 2.1 修改 `web/static/index.html`：在导航栏添加"账本"按钮，链接到 `/fava/`，`target="_blank"` 新标签页打开
- [x] 2.2 修改 `web/static/config.html`：同样添加"账本"按钮，保持导航栏与 index.html 一致
