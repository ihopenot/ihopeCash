## ADDED Requirements

### Requirement: Config 类必须支持嵌套配置结构访问
Config 类 SHALL 支持访问嵌套的配置结构，允许通过多级键访问深层配置项。

#### Scenario: 访问嵌套配置项
- **WHEN** 使用 `config["email"]["imap"]["host"]` 访问嵌套配置
- **THEN** 返回对应的嵌套配置值

#### Scenario: 访问不存在的嵌套配置项
- **WHEN** 使用 `config["nonexistent"]["nested"]` 访问不存在的嵌套配置
- **THEN** 抛出 KeyError 异常

### Requirement: Config 类必须提供完整配置字典导出
Config 类 SHALL 提供 `to_dict()` 方法，返回完整配置的深拷贝字典，用于传递给其他模块。

#### Scenario: 导出完整配置字典
- **WHEN** 调用 `config.to_dict()` 方法
- **THEN** 返回包含所有配置项的字典深拷贝
- **THEN** 修改返回的字典不影响 Config 实例的内部配置

### Requirement: Config 类必须支持默认值深度合并
Config 类 SHALL 在加载配置时，将默认配置与用户配置进行深度合并，确保所有必需字段存在。YAML 加载 MUST 使用 `yaml.SafeLoader`（而非 `FullLoader`），以防止 Python 对象实例化攻击。

#### Scenario: 用户配置缺少某些字段时自动补全
- **WHEN** 用户配置文件缺少某些默认配置字段
- **THEN** 系统自动使用默认值补全缺失字段
- **THEN** 不覆盖用户已设置的配置值

#### Scenario: 嵌套配置的深度合并
- **WHEN** 用户配置的嵌套结构缺少某些子字段
- **THEN** 系统自动补全缺失的子字段
- **THEN** 保留用户已设置的嵌套值

#### Scenario: YAML 安全加载
- **WHEN** 系统加载 env.yaml 或 config.yaml
- **THEN** 使用 `yaml.load(f, Loader=yaml.SafeLoader)` 加载
- **THEN** 不允许实例化 Python 对象

### Requirement: Config 类必须提供扩展的默认配置
Config 类 SHALL 提供包含所有配置类型的默认配置结构，包括系统配置、邮件配置、importers 配置、账户映射等。

#### Scenario: 默认配置包含系统配置节
- **WHEN** 创建默认配置
- **THEN** 配置包含 `system` 节点，其中包含 beancount_path、balance_accounts（路径属性 data_path、rawdata_path、archive_path 由 beancount_path 硬编码派生）

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

### Requirement: Config 类必须提供对象转换功能
Config 类 SHALL 提供 `get_detail_mappings()` 方法，将 YAML 配置中的 detail_mappings 转换为 BillDetailMapping 对象列表。`ImportError` 的 try-except 范围 MUST 仅覆盖 import 语句本身，不覆盖后续转换逻辑。返回原始数据时 MUST 返回深拷贝。

#### Scenario: 转换 detail_mappings 为对象
- **WHEN** 调用 `config.get_detail_mappings()` 方法且 china_bean_importers 库可用
- **THEN** 返回 BillDetailMapping 对象列表
- **THEN** 每个对象包含 payee_keywords、narration_keywords、account、tags、metadata 字段

#### Scenario: china_bean_importers 不可用时返回原始数据深拷贝
- **WHEN** 调用 `config.get_detail_mappings()` 方法但 china_bean_importers 库不可用
- **THEN** 返回原始字典列表的深拷贝
- **THEN** 不抛出异常

### Requirement: Config 类必须提供便捷访问方法
Config 类 SHALL 提供特定配置节的便捷访问方法，简化常用配置的获取。返回列表或字典类型的属性 MUST 返回深拷贝，防止调用者修改内部状态。

#### Scenario: 获取邮件配置
- **WHEN** 调用 `config.get_email_config()` 方法
- **THEN** 返回完整的 email 配置字典

#### Scenario: 获取指定导入器配置
- **WHEN** 调用 `config.get_importer_config("alipay")` 方法
- **THEN** 返回对应导入器的配置字典

#### Scenario: 获取密码列表
- **WHEN** 调用 `config.get_passwords()` 方法
- **THEN** 返回合并了 passwords 和 pdf_passwords 的去重列表

#### Scenario: 返回值不影响内部状态
- **WHEN** 调用者修改 `config.balance_accounts` 返回的列表
- **THEN** Config 实例的内部配置不受影响

### Requirement: Config 类必须支持配置结构检查
Config 类 SHALL 提供方法检查和显示配置结构，方便调试和验证。

#### Scenario: 获取所有顶层配置键
- **WHEN** 调用 `config.keys()` 方法
- **THEN** 返回所有顶层配置键的列表

#### Scenario: 打印配置结构
- **WHEN** 调用 `config.print_structure()` 方法
- **THEN** 以树形结构打印配置的层次结构

## MODIFIED Requirements

### Requirement: Config 类 update_from_web 必须使用深度合并
`update_from_web()` 方法更新嵌套配置时 MUST 使用深度合并（而非 `dict.update()` 浅合并），以避免丢失未传入的嵌套键。

#### Scenario: 更新嵌套配置保留未传入的键
- **WHEN** 调用 `update_from_web({"system": {"balance_accounts": ["Assets:BOC"]}})` 且原配置 system 下还有 beancount_path
- **THEN** beancount_path 保留不变，balance_accounts 被更新
