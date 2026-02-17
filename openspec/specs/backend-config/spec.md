## MODIFIED Requirements

### Requirement: Config 类必须提供默认配置
Config 类 SHALL 定义默认配置结构，包含 system、email、passwords、importers、card_accounts、detail_mappings 等所有必要配置节点。默认配置中的交易摘要过滤 SHALL 包含预设默认值。

#### Scenario: 默认配置包含系统配置节
- **WHEN** 创建默认配置
- **THEN** 配置包含 `system` 节点
- **THEN** `system` 节点包含 beancount_path 默认值为 "data/beancount"
- **THEN** `system` 节点包含 balance_accounts 默认值为空列表
- **THEN** 路径属性 `data_path`、`rawdata_path`、`archive_path` 从 `beancount_path` 硬编码派生（分别为 `beancount_path + "/data"`、`beancount_path + "/rawdata"`、`beancount_path + "/archive"`）

#### Scenario: 默认配置包含邮件配置节
- **WHEN** 创建默认配置
- **THEN** 配置包含 `email` 节点，其中包含 imap 配置（host、port、username、password、mailbox）

#### Scenario: 默认配置包含 importers 配置节
- **WHEN** 创建默认配置
- **THEN** 配置包含 `importers` 节点
- **THEN** `importers` 包含所有导入器的默认配置（alipay、wechat、thu_ecard、hsbc_hk）
- **THEN** 每个导入器配置包含其所需的所有字段及默认值
- **THEN** `importers` 包含 card_narration_whitelist 默认值为 ["财付通(银联云闪付)"]
- **THEN** `importers` 包含 card_narration_blacklist 默认值为 ["支付宝", "财付通", "美团支付"]

#### Scenario: 默认配置包含密码和账户映射配置
- **WHEN** 创建默认配置
- **THEN** 配置包含 passwords、pdf_passwords、card_accounts 字段
- **THEN** 配置包含 unknown_expense_account 和 unknown_income_account 字段
- **THEN** 配置包含 detail_mappings 字段，默认为空列表

### Requirement: Config 类必须支持双文件加载
Config 类 SHALL 接受 `env_file` 参数，初始化时先加载 `env.yaml` 再加载 `config.yaml`，`env.yaml` 必须存在否则抛出异常。

#### Scenario: env.yaml 不存在时抛出异常
- **WHEN** 创建 Config 实例时 env_file 指定的文件不存在
- **THEN** 系统抛出 FileNotFoundError 异常

#### Scenario: config.yaml 不存在时标记需要引导
- **WHEN** env.yaml 存在但 config.yaml 不存在
- **THEN** Config 对象正常创建，`setup_required` 属性为 True
- **THEN** 不自动创建 config.yaml 文件
- **THEN** 业务配置使用内存中的默认值

#### Scenario: 两个文件都存在时正常加载
- **WHEN** env.yaml 和 config.yaml 都存在
- **THEN** Config 对象正常创建，`setup_required` 属性为 False
- **THEN** 业务配置从 config.yaml 加载

#### Scenario: env.yaml 中的 web 字段覆盖 config.yaml
- **WHEN** env.yaml 和 config.yaml 都包含 web 字段
- **THEN** env.yaml 中的 web 字段值覆盖 config.yaml 中的对应值
- **THEN** env.yaml 中的 system 字段（如存在）也会覆盖 config.yaml 中的对应值，但路径相关字段（`beancount_path`、`data_path`、`rawdata_path`、`archive_path`）被排除

### Requirement: Config 类提供 setup_required 属性
Config 类 SHALL 提供 `setup_required` 属性，指示是否需要运行首次配置引导。

#### Scenario: config.yaml 不存在
- **WHEN** config.yaml 文件不存在
- **THEN** `config.setup_required` 返回 True

#### Scenario: config.yaml 存在
- **WHEN** config.yaml 文件存在
- **THEN** `config.setup_required` 返回 False

#### Scenario: 引导完成后更新状态
- **WHEN** 调用 setup 完成流程写入 config.yaml 后
- **THEN** `config.setup_required` 更新为 False

### Requirement: Config 类提供引导完成写入方法
Config 类 SHALL 提供 `complete_setup(config_data, new_accounts)` 方法，一次性写入配置和新增账户。

#### Scenario: 写入配置文件
- **WHEN** 调用 `complete_setup(config_data, new_accounts)`
- **THEN** config_data 写入 config.yaml（不包含 system 路径和 web 配置）
- **THEN** 合并默认值确保所有必要字段存在

#### Scenario: 写入新增账户
- **WHEN** new_accounts 列表非空
- **THEN** 系统将每个新增账户追加到 accounts.bean
- **THEN** 已存在于 accounts.bean 中的账户不重复添加
- **THEN** 每条记录格式为 `1999-01-01 open {Type}:{Path} {Currencies} ; {Comment}`

#### Scenario: 更新状态
- **WHEN** complete_setup 执行成功
- **THEN** 重新加载 Config
- **THEN** `setup_required` 更新为 False
