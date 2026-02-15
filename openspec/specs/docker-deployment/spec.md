## ADDED Requirements

### Requirement: Docker Compose 必须提供一键启动能力
系统 SHALL 提供 `docker-compose.yml`，用户执行 `docker compose up` 即可启动包含 Nginx、Web 应用和 Fava 的完整服务。

#### Scenario: 一键启动全部服务
- **WHEN** 用户在项目根目录执行 `docker compose up`
- **THEN** 容器内依次启动 Nginx、Fava、Uvicorn 三个进程
- **THEN** 服务在 80 和 443 端口可访问

#### Scenario: 容器异常退出后自动重启
- **WHEN** 容器主进程崩溃
- **THEN** Docker 根据 `restart: unless-stopped` 策略自动重启容器

### Requirement: Dockerfile 必须构建完整运行环境
系统 SHALL 提供 `Dockerfile`，基于 `python:3.12-slim` 镜像，安装 nginx、openssl 及所有 Python 依赖（beancount、fava、项目依赖、china_bean_importers）。

#### Scenario: 构建镜像包含所有依赖
- **WHEN** 执行 `docker build .`
- **THEN** 生成的镜像包含 nginx、openssl、Python 3.12、beancount、fava 及项目所有依赖
- **THEN** china_bean_importers 以可编辑模式安装

#### Scenario: 镜像工作目录为 /app
- **WHEN** 容器启动
- **THEN** 工作目录为 `/app`，项目文件位于该目录下

### Requirement: Nginx 必须提供 HTTPS 反向代理
系统 SHALL 配置 Nginx 监听 80 和 443 端口，80 端口自动重定向到 HTTPS，443 端口反向代理到内部 Web 应用和 Fava。

#### Scenario: HTTP 请求重定向到 HTTPS
- **WHEN** 用户通过 HTTP（端口 80）访问任意路径
- **THEN** Nginx 返回 301 重定向到对应的 HTTPS URL

#### Scenario: HTTPS 根路径代理到 Web 应用
- **WHEN** 用户通过 HTTPS 访问 `/` 或其他非 `/fava/` 路径
- **THEN** Nginx 将请求代理到 `http://127.0.0.1:8000`

#### Scenario: HTTPS /fava/ 路径代理到 Fava
- **WHEN** 用户通过 HTTPS 访问 `/fava/` 或其子路径
- **THEN** Nginx 将请求代理到 `http://127.0.0.1:5000/fava/`

#### Scenario: WebSocket 连接正确代理
- **WHEN** Web 应用通过 WebSocket 连接 `/ws/progress`
- **THEN** Nginx 正确代理 WebSocket 升级请求到后端

### Requirement: SSL 证书必须支持自动生成和外部挂载
系统 SHALL 在启动时检测 SSL 证书，无证书时自动生成自签证书，有外部证书时直接使用。

#### Scenario: 无外部证书时生成自签证书
- **WHEN** 容器启动且 `/app/certs/cert.pem` 或 `/app/certs/key.pem` 不存在
- **THEN** 系统使用 openssl 生成自签证书到 `/app/certs/` 目录
- **THEN** Nginx 使用生成的自签证书启动 HTTPS

#### Scenario: 使用外部挂载的证书
- **WHEN** 容器启动且 `/app/certs/cert.pem` 和 `/app/certs/key.pem` 存在
- **THEN** Nginx 直接使用这些证书，不生成自签证书

### Requirement: 数据卷必须实现持久化
系统 SHALL 通过 Docker volume 挂载实现数据持久化，容器重建不丢失数据。

#### Scenario: 配置文件持久化
- **WHEN** docker-compose.yml 中定义 volumes
- **THEN** 宿主机的 `config.yaml` 挂载到容器内 `/app/config.yaml`

#### Scenario: 账本数据持久化
- **WHEN** docker-compose.yml 中定义 volumes
- **THEN** 宿主机的 `data/`、`rawdata/`、`archive/` 目录分别挂载到容器内对应路径
- **THEN** `main.bean` 和 `accounts.bean` 已包含在 `data/` 目录内，不需要单独挂载

#### Scenario: SSL 证书目录可选挂载
- **WHEN** 用户在宿主机有 `certs/` 目录
- **THEN** 该目录可挂载到容器内 `/app/certs/` 以使用自定义证书

### Requirement: Fava 必须使用 /fava 路径前缀启动
系统 SHALL 使用 `--prefix /fava` 参数启动 Fava，使其在 `/fava/` 路径下可访问。

#### Scenario: Fava 以路径前缀模式运行
- **WHEN** 容器启动 Fava 进程
- **THEN** Fava 以 `fava data/main.bean --host 127.0.0.1 --port 5000 --prefix /fava` 方式启动（指向 `data/main.bean` 而非根目录 `main.bean`）
- **THEN** Fava 仅监听容器内部的 127.0.0.1，不直接对外暴露

### Requirement: 必须提供 .dockerignore 排除无关文件
系统 SHALL 提供 `.dockerignore` 文件排除构建无关的文件和目录。

#### Scenario: 排除数据和临时文件
- **WHEN** 执行 `docker build`
- **THEN** `.git`、`__pycache__`、`data/`、`rawdata/`、`archive/`、`certs/`、`*.pyc` 等文件不会被复制到镜像中
