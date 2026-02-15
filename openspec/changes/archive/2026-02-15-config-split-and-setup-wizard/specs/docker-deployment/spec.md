## MODIFIED Requirements

### Requirement: 数据卷必须实现持久化
系统 SHALL 通过 Docker volume 挂载实现数据持久化，容器重建不丢失数据。Docker 只需挂载 env.yaml，不再挂载 config.yaml。

#### Scenario: 环境配置文件持久化
- **WHEN** docker-compose.yml 中定义 volumes
- **THEN** 宿主机的 `env.yaml` 挂载到容器内 `/app/env.yaml`
- **THEN** 不挂载 config.yaml（config.yaml 仅存在于容器内部，通过 Web 管理）

#### Scenario: 账本数据持久化
- **WHEN** docker-compose.yml 中定义 volumes
- **THEN** 宿主机的 `data/`、`rawdata/`、`archive/` 目录分别挂载到容器内对应路径
- **THEN** `main.bean` 和 `accounts.bean` 已包含在 `data/` 目录内，不需要单独挂载

#### Scenario: SSL 证书目录可选挂载
- **WHEN** 用户在宿主机有 `certs/` 目录
- **THEN** 该目录可挂载到容器内 `/app/certs/` 以使用自定义证书

## ADDED Requirements

### Requirement: 入口脚本必须检查 env.yaml 存在性
docker/entrypoint.sh SHALL 在启动服务前检查 `/app/env.yaml` 是否存在，不存在时报错退出。

#### Scenario: env.yaml 存在
- **WHEN** 容器启动且 `/app/env.yaml` 存在
- **THEN** 正常继续启动流程

#### Scenario: env.yaml 不存在
- **WHEN** 容器启动且 `/app/env.yaml` 不存在
- **THEN** 脚本输出错误信息提示用户挂载 env.yaml
- **THEN** 脚本以非零退出码退出，容器停止
