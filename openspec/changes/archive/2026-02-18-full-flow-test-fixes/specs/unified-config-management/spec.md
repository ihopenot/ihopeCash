## MODIFIED Requirements

### Requirement: Config 类必须提供扩展的默认配置
Config 类 SHALL 提供包含所有配置类型的默认配置结构。系统路径配置简化为单一 `beancount_path`，下级路径硬编码派生。

#### Scenario: 默认配置包含系统配置节
- **WHEN** 创建默认配置
- **THEN** 配置包含 `system` 节点，其中包含 `beancount_path`（默认 `"data/beancount"`）和 `balance_accounts`
- **THEN** 配置不再包含独立的 `data_path`、`rawdata_path`、`archive_path` 配置项

#### Scenario: 默认配置包含邮件配置节
- **WHEN** 创建默认配置
- **THEN** 配置包含 `email` 节点，其中包含 imap 服务器配置

#### Scenario: 默认配置包含 importers 配置节
- **WHEN** 创建默认配置
- **THEN** 配置包含 `importers` 节点，其中包含各类导入器的默认配置（alipay、wechat、thu_ecard、hsbc_hk 等）

#### Scenario: 默认配置包含密码配置
- **WHEN** 创建默认配置
- **THEN** 配置包含 `passwords` 和 `pdf_passwords` 字段，默认为空列表

#### Scenario: 默认配置包含账户映射配置
- **WHEN** 创建默认配置
- **THEN** 配置包含 `card_accounts`、`unknown_expense_account`、`unknown_income_account` 字段

#### Scenario: 默认配置包含 detail_mappings 配置
- **WHEN** 创建默认配置
- **THEN** 配置包含 `detail_mappings` 字段，默认为空列表

### Requirement: Config 路径属性从 beancount_path 硬编码派生
Config 类 SHALL 提供 `beancount_path`、`data_path`、`rawdata_path`、`archive_path` 四个属性。`data_path`、`rawdata_path`、`archive_path` SHALL 从 `beancount_path` 硬编码派生，不可独立配置。

#### Scenario: beancount_path 属性
- **WHEN** 访问 `config.beancount_path`
- **THEN** 返回 `system.beancount_path` 的值（默认 `"data/beancount"`）

#### Scenario: data_path 硬编码派生
- **WHEN** 访问 `config.data_path`
- **THEN** 返回 `beancount_path + "/data"`（如 `"data/beancount/data"`）

#### Scenario: rawdata_path 硬编码派生
- **WHEN** 访问 `config.rawdata_path`
- **THEN** 返回 `beancount_path + "/rawdata"`（如 `"data/beancount/rawdata"`）

#### Scenario: archive_path 硬编码派生
- **WHEN** 访问 `config.archive_path`
- **THEN** 返回 `beancount_path + "/archive"`（如 `"data/beancount/archive"`）

### Requirement: Config 默认配置文件路径
Config 类的 `config_file` 参数默认值 SHALL 为 `"data/config.yaml"`。

#### Scenario: 默认配置文件路径
- **WHEN** 创建 `Config()` 实例不传参
- **THEN** `config_file` 为 `"data/config.yaml"`

#### Scenario: config.yaml 不存在时标记需要引导
- **WHEN** `data/config.yaml` 不存在
- **THEN** `config.setup_required` 为 `True`

### Requirement: env.yaml 不覆盖路径配置
env.yaml 中的 system 覆盖逻辑 SHALL NOT 覆盖路径相关配置（`beancount_path`、`data_path`、`rawdata_path`、`archive_path`），这些路径由代码硬编码管理。

#### Scenario: env.yaml system 覆盖不影响路径
- **WHEN** env.yaml 中包含 `system.beancount_path` 配置
- **THEN** 该配置被忽略，路径仍由代码默认值决定

### Requirement: Config 类 update_from_web 必须使用深度合并
`update_from_web()` 方法更新嵌套配置时 MUST 使用深度合并（而非 `dict.update()` 浅合并），以避免丢失未传入的嵌套键。路径相关字段不可通过 Web 更新。

#### Scenario: 更新嵌套配置保留未传入的键
- **WHEN** 调用 `update_from_web({"email": {"imap": {"host": "new_host"}}})` 且原配置 email.imap 下还有 port
- **THEN** port 保留不变，host 被更新

#### Scenario: Web 更新不影响路径配置
- **WHEN** 调用 `update_from_web` 传入 `system.beancount_path`
- **THEN** 路径配置不被修改
