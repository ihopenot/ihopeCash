## MODIFIED Requirements

### Requirement: Config 类必须提供默认配置
Config 类 SHALL 定义默认配置结构，包含 system、email、passwords、importers、card_accounts、detail_mappings 等所有必要配置节点。

#### Scenario: 默认配置包含系统配置节
- **WHEN** 创建默认配置
- **THEN** 配置包含 `system` 节点
- **THEN** `system` 节点包含 data_path 默认值为 "data"
- **THEN** `system` 节点包含 rawdata_path 默认值为 "rawdata"
- **THEN** `system` 节点包含 archive_path 默认值为 "archive"
- **THEN** `system` 节点包含 balance_accounts 默认值为空列表

#### Scenario: 默认配置包含邮件配置节
- **WHEN** 创建默认配置
- **THEN** 配置包含 `email` 节点，其中包含 imap 配置（host、port、username、password、mailbox）

#### Scenario: 默认配置包含 importers 配置节
- **WHEN** 创建默认配置
- **THEN** 配置包含 `importers` 节点
- **THEN** `importers` 包含所有导入器的默认配置（alipay、wechat、thu_ecard、hsbc_hk）
- **THEN** 每个导入器配置包含其所需的所有字段及默认值

#### Scenario: 默认配置包含密码和账户映射配置
- **WHEN** 创建默认配置
- **THEN** 配置包含 passwords、pdf_passwords、card_accounts 字段
- **THEN** 配置包含 unknown_expense_account 和 unknown_income_account 字段
- **THEN** 配置包含 detail_mappings 字段，默认为空列表

### Requirement: Config 类必须提供常用配置的属性访问
Config 类 SHALL 提供属性方法访问常用配置项: data_path, rawdata_path, archive_path, balance_accounts，并从 system 命名空间读取。

#### Scenario: 通过属性访问 data_path
- **WHEN** 使用 `config.data_path` 访问数据路径
- **THEN** 返回 `system.data_path` 的配置值
- **THEN** 若 `system.data_path` 不存在，返回默认值 "data"

#### Scenario: 通过属性访问 rawdata_path
- **WHEN** 使用 `config.rawdata_path` 访问原始数据路径
- **THEN** 返回 `system.rawdata_path` 的配置值
- **THEN** 若 `system.rawdata_path` 不存在，返回默认值 "rawdata"

#### Scenario: 通过属性访问 archive_path
- **WHEN** 使用 `config.archive_path` 访问归档路径
- **THEN** 返回 `system.archive_path` 的配置值
- **THEN** 若 `system.archive_path` 不存在，返回默认值 "archive"

#### Scenario: 通过属性访问 balance_accounts
- **WHEN** 使用 `config.balance_accounts` 访问余额账户列表
- **THEN** 返回 `system.balance_accounts` 的配置值
- **THEN** 若 `system.balance_accounts` 不存在，返回空列表

### Requirement: Config 类必须支持字典式访问
Config 类 SHALL 实现 `__getitem__` 方法，支持 `config["key"]` 方式访问顶层和嵌套配置项。

#### Scenario: 使用字典方式访问顶层配置项
- **WHEN** 使用 `config["system"]` 访问存在的顶层配置项
- **THEN** 返回对应的配置值

#### Scenario: 使用字典方式访问嵌套配置项
- **WHEN** 使用 `config["system"]["data_path"]` 访问嵌套配置项
- **THEN** 返回对应的配置值

#### Scenario: 访问不存在的顶层配置项
- **WHEN** 使用 `config["nonexistent"]` 访问不存在的配置项
- **THEN** 抛出 KeyError 异常

## ADDED Requirements

### Requirement: Config 类必须支持配置的深度合并
Config 类 SHALL 提供 `_merge_defaults()` 方法，在加载配置时将默认配置与用户配置深度合并。

#### Scenario: 合并时保留用户配置
- **WHEN** 用户配置和默认配置都存在某个字段
- **THEN** 保留用户配置的值，不使用默认值

#### Scenario: 合并时补全缺失字段
- **WHEN** 用户配置缺少某个默认配置字段
- **THEN** 自动添加该字段及其默认值

#### Scenario: 嵌套字典的深度合并
- **WHEN** 用户配置的嵌套字典缺少某些子字段
- **THEN** 递归合并，补全缺失的嵌套字段
- **THEN** 保留用户已设置的嵌套值
