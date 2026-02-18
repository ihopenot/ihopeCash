## MODIFIED Requirements

### Requirement: 数据卷必须实现持久化
系统 SHALL 通过 Docker volume 挂载实现数据持久化，容器重建不丢失数据。Docker 只需挂载 `data/` 目录和 `env.yaml`，`config.yaml` 存放在 `data/` 目录内随数据卷持久化。`docker-compose.yml` MUST 包含资源限制和日志配置。Docker MUST 只暴露 HTTPS 端口，不暴露 HTTP 端口。

#### Scenario: 环境配置文件持久化
- **WHEN** docker-compose.yml 中定义 volumes
- **THEN** 宿主机的 `env.yaml` 挂载到容器内 `/app/env.yaml`

#### Scenario: 数据目录统一挂载
- **WHEN** docker-compose.yml 中定义 volumes
- **THEN** 宿主机的 `data/` 目录挂载到容器内 `/app/data`
- **THEN** `config.yaml` 存放在 `data/config.yaml`，随数据卷持久化
- **THEN** beancount 数据（bean 文件、rawdata、archive）存放在 `data/beancount/` 下
- **THEN** 不再单独挂载 `rawdata/` 和 `archive/` 目录

#### Scenario: SSL 证书目录可选挂载
- **WHEN** 用户在宿主机有 `certs/` 目录
- **THEN** 该目录可挂载到容器内 `/app/certs/` 以使用自定义证书

#### Scenario: 只暴露 HTTPS 端口
- **WHEN** docker-compose.yml 中定义 ports
- **THEN** 只映射 HTTPS 端口（默认 443:443）
- **THEN** 不对外暴露 HTTP 端口

#### Scenario: 资源限制配置
- **WHEN** docker-compose.yml 中定义 deploy 节
- **THEN** 设置内存限制（如 2G）和 CPU 限制（如 2）
- **THEN** 设置 `restart: unless-stopped`

#### Scenario: 日志配置
- **WHEN** docker-compose.yml 中定义 logging 节
- **THEN** 使用 json-file 驱动
- **THEN** 设置 max-size 和 max-file 限制日志大小

### Requirement: 入口脚本必须检查 env.yaml 存在性
docker/entrypoint.sh SHALL 在启动服务前检查 `/app/env.yaml` 是否存在，不存在时报错退出。入口脚本 MUST 创建必要子目录并处理首次运行场景。

#### Scenario: env.yaml 存在
- **WHEN** 容器启动且 `/app/env.yaml` 存在
- **THEN** 正常继续启动流程

#### Scenario: env.yaml 不存在
- **WHEN** 容器启动且 `/app/env.yaml` 不存在
- **THEN** 脚本输出错误信息提示用户挂载 env.yaml
- **THEN** 脚本以非零退出码退出，容器停止

#### Scenario: 首次运行创建目录和占位文件
- **WHEN** 容器启动且 `data/beancount/data/main.bean` 不存在
- **THEN** 脚本创建 `data/beancount/data`、`data/beancount/rawdata`、`data/beancount/archive` 目录
- **THEN** 脚本创建空的 `data/beancount/data/main.bean` 占位文件

#### Scenario: Fava 启动不阻塞主服务
- **WHEN** 启动 Fava 后台进程
- **THEN** 脚本直接继续启动 Web 服务，不等待 Fava 就绪
- **THEN** Fava 在后台异步启动

### Requirement: Nginx 必须配置安全 Headers
docker/nginx.conf MUST 在 HTTPS server 块中添加安全响应头。CSP 策略 MUST 允许 Tailwind CDN。

#### Scenario: 安全响应头存在
- **WHEN** 客户端收到 HTTPS 响应
- **THEN** 响应包含 `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- **THEN** 响应包含 `X-Content-Type-Options: nosniff`
- **THEN** 响应包含 `X-Frame-Options: SAMEORIGIN`
- **THEN** 响应包含 `Referrer-Policy` 和 `Permissions-Policy`
- **THEN** 响应包含 `Content-Security-Policy`

#### Scenario: CSP 允许 Tailwind CDN
- **WHEN** 检查 Content-Security-Policy 头
- **THEN** `script-src` 包含 `https://cdn.tailwindcss.com`
- **THEN** `style-src` 包含 `https://cdn.tailwindcss.com`

## REMOVED Requirements

### Requirement: 容器必须以非 root 用户运行
**Reason**: Volume 挂载权限问题导致容器启动失败，此项目为个人/小团队自部署工具，root 运行可接受
**Migration**: 移除 Dockerfile 中 useradd、chown、USER appuser 相关行

## MODIFIED Requirements

### Requirement: beancount_config.py 必须纳入版本控制
项目根目录 `.gitignore` SHALL NOT 排除 `beancount_config.py`，该文件 MUST 纳入 Git 版本控制。

#### Scenario: clone 仓库后文件存在
- **WHEN** 用户 clone 仓库
- **THEN** `beancount_config.py` 存在于工作目录中
- **THEN** Docker 构建时 `COPY beancount_config.py` 不会失败
