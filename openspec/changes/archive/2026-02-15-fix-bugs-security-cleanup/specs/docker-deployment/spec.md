## MODIFIED Requirements

### Requirement: 数据卷必须实现持久化
系统 SHALL 通过 Docker volume 挂载实现数据持久化，容器重建不丢失数据。Docker 只需挂载 env.yaml，不再挂载 config.yaml。`env.yaml` MUST 以只读方式挂载（`:ro`）。`docker-compose.yml` MUST 包含资源限制和日志配置。

#### Scenario: 环境配置文件持久化
- **WHEN** docker-compose.yml 中定义 volumes
- **THEN** 宿主机的 `env.yaml` 挂载到容器内 `/app/env.yaml:ro`（只读）
- **THEN** 不挂载 config.yaml（config.yaml 仅存在于容器内部，通过 Web 管理）

#### Scenario: 账本数据持久化
- **WHEN** docker-compose.yml 中定义 volumes
- **THEN** 宿主机的 `data/`、`rawdata/`、`archive/` 目录分别挂载到容器内对应路径
- **THEN** `main.bean` 和 `accounts.bean` 已包含在 `data/` 目录内，不需要单独挂载

#### Scenario: SSL 证书目录可选挂载
- **WHEN** 用户在宿主机有 `certs/` 目录
- **THEN** 该目录可挂载到容器内 `/app/certs/` 以使用自定义证书

#### Scenario: 资源限制配置
- **WHEN** docker-compose.yml 中定义 deploy 节
- **THEN** 设置内存限制（如 2G）和 CPU 限制（如 2）
- **THEN** 设置 `restart: unless-stopped`

#### Scenario: 日志配置
- **WHEN** docker-compose.yml 中定义 logging 节
- **THEN** 使用 json-file 驱动
- **THEN** 设置 max-size 和 max-file 限制日志大小

### Requirement: 入口脚本必须检查 env.yaml 存在性
docker/entrypoint.sh SHALL 在启动服务前检查 `/app/env.yaml` 是否存在，不存在时报错退出。入口脚本 MUST 对后台进程进行基本健康检查。

#### Scenario: env.yaml 存在
- **WHEN** 容器启动且 `/app/env.yaml` 存在
- **THEN** 正常继续启动流程

#### Scenario: env.yaml 不存在
- **WHEN** 容器启动且 `/app/env.yaml` 不存在
- **THEN** 脚本输出错误信息提示用户挂载 env.yaml
- **THEN** 脚本以非零退出码退出，容器停止

#### Scenario: 后台进程健康检查
- **WHEN** 启动 Fava 后台进程后
- **THEN** 脚本等待短暂时间后检查进程是否存活
- **THEN** 进程未存活时输出错误信息并退出

## ADDED Requirements

### Requirement: 容器必须以非 root 用户运行
Dockerfile MUST 创建非 root 用户（如 `appuser`，UID 1000）并使用 `USER` 指令切换。应用目录 MUST 设置正确的文件权限。

#### Scenario: 非 root 用户运行
- **WHEN** 容器启动
- **THEN** 所有进程以 appuser（UID 1000）身份运行
- **THEN** 不以 root 身份运行任何服务进程

#### Scenario: 文件权限正确
- **WHEN** Dockerfile 构建镜像
- **THEN** /app 目录及其子目录的所有权设置为 appuser
- **THEN** 挂载卷的写入操作正常工作

### Requirement: Docker HEALTHCHECK 必须配置
Dockerfile MUST 包含 HEALTHCHECK 指令，定期检查应用健康状态。

#### Scenario: 健康检查通过
- **WHEN** 应用正常运行
- **THEN** HEALTHCHECK 命令返回成功（exit 0）

#### Scenario: 健康检查失败
- **WHEN** 应用无响应
- **THEN** HEALTHCHECK 命令返回失败
- **THEN** Docker 标记容器为 unhealthy

### Requirement: Nginx 必须配置安全 Headers
docker/nginx.conf MUST 在 HTTPS server 块中添加安全响应头。

#### Scenario: 安全响应头存在
- **WHEN** 客户端收到 HTTPS 响应
- **THEN** 响应包含 `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- **THEN** 响应包含 `X-Content-Type-Options: nosniff`
- **THEN** 响应包含 `X-Frame-Options: DENY`

### Requirement: Nginx SSL/TLS 配置必须加固
docker/nginx.conf MUST 使用强加密配置。

#### Scenario: TLS 协议和加密套件
- **WHEN** 检查 nginx SSL 配置
- **THEN** `ssl_protocols` 优先 TLSv1.3，保留 TLSv1.2 兼容
- **THEN** `ssl_prefer_server_ciphers` 设为 on
- **THEN** `ssl_ciphers` 使用 ECDHE 加密套件
- **THEN** 配置 `ssl_session_cache` 和 `ssl_session_timeout`

### Requirement: 依赖版本必须固定
`requirements.txt` 和 `web/requirements.txt` 中所有依赖 MUST 指定版本范围约束。

#### Scenario: 主依赖版本固定
- **WHEN** 检查 `requirements.txt`
- **THEN** 每个依赖包含 `>=最低版本` 约束

#### Scenario: Web 依赖版本固定
- **WHEN** 检查 `web/requirements.txt`
- **THEN** 每个依赖包含 `>=最低版本,<下一大版本` 范围约束

### Requirement: 账户开户日期必须使用当前日期
`web/app.py` 中创建新账户时 MUST 使用当前日期（`datetime.date.today().isoformat()`），而非硬编码 `1999-01-01`。

#### Scenario: 新建账户使用当前日期
- **WHEN** 通过 Web API 创建新的 Beancount 账户
- **THEN** open 指令的日期为请求当天的日期（YYYY-MM-DD 格式）
