## MODIFIED Requirements

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
