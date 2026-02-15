## ADDED Requirements

### Requirement: env.yaml 定义部署环境配置
系统 SHALL 使用 `env.yaml` 文件存放部署环境相关配置，包含 `system`（路径配置）和 `web`（Web 服务配置）两个顶层节点。

#### Scenario: env.yaml 包含 system 路径配置
- **WHEN** 加载 env.yaml
- **THEN** 文件包含 `system` 节点
- **THEN** `system` 包含 `data_path`（默认 "data"）、`rawdata_path`（默认 "rawdata"）、`archive_path`（默认 "archive"）

#### Scenario: env.yaml 包含 web 服务配置
- **WHEN** 加载 env.yaml
- **THEN** 文件包含 `web` 节点
- **THEN** `web` 包含 `host`、`port`、`password`、`jwt_secret`、`token_expire_days`

#### Scenario: env.yaml 不存在时应用必须报错退出
- **WHEN** 应用启动时 env.yaml 不存在
- **THEN** 系统抛出 `FileNotFoundError` 异常，应用无法启动

### Requirement: env.yaml 配置优先级高于 config.yaml
Config 类加载时，`env.yaml` 中的 `system` 和 `web` 字段 SHALL 始终覆盖 `config.yaml` 中的对应字段。

#### Scenario: env.yaml 的 system 字段覆盖 config.yaml
- **WHEN** env.yaml 中 `system.data_path` 为 "custom_data"
- **AND** config.yaml 中 `system.data_path` 为 "data"
- **THEN** Config 对象的 `data_path` 属性返回 "custom_data"

#### Scenario: env.yaml 的 web 字段覆盖 config.yaml
- **WHEN** env.yaml 中 `web.port` 为 9000
- **AND** config.yaml 中 `web.port` 为 8000
- **THEN** Config 对象的 `web_port` 属性返回 9000

### Requirement: 提供 env.example.yaml 模板文件
系统 SHALL 在项目根目录提供 `env.example.yaml` 模板文件，包含所有环境配置项及其默认值和注释说明。

#### Scenario: 用户可基于模板创建 env.yaml
- **WHEN** 用户复制 env.example.yaml 为 env.yaml
- **THEN** 文件包含所有必要配置项
- **THEN** password 和 jwt_secret 使用占位符值提醒用户修改

### Requirement: Config 类支持双文件初始化
Config 类 SHALL 接受 `env_file` 参数（默认 "env.yaml"），初始化时加载两个文件。

#### Scenario: 双文件加载
- **WHEN** 创建 Config 实例 `Config(config_file="config.yaml", env_file="env.yaml")`
- **THEN** 系统先加载 env.yaml 获取 system 和 web 配置
- **THEN** 再加载 config.yaml 获取业务配置
- **THEN** env.yaml 中的 system 和 web 覆盖 config.yaml 中的对应字段

#### Scenario: 仅 env.yaml 存在
- **WHEN** env.yaml 存在但 config.yaml 不存在
- **THEN** Config 对象正常创建
- **THEN** `config.setup_required` 为 True
- **THEN** 业务配置使用内存中的默认值
- **THEN** 不自动创建 config.yaml 文件

#### Scenario: 两个文件都存在
- **WHEN** env.yaml 和 config.yaml 都存在
- **THEN** Config 对象正常创建
- **THEN** `config.setup_required` 为 False
