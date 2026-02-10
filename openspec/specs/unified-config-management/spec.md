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
Config 类 SHALL 在加载配置时，将默认配置与用户配置进行深度合并，确保所有必需字段存在。

#### Scenario: 用户配置缺少某些字段时自动补全
- **WHEN** 用户配置文件缺少某些默认配置字段
- **THEN** 系统自动使用默认值补全缺失字段
- **THEN** 不覆盖用户已设置的配置值

#### Scenario: 嵌套配置的深度合并
- **WHEN** 用户配置的嵌套结构缺少某些子字段
- **THEN** 系统自动补全缺失的子字段
- **THEN** 保留用户已设置的嵌套值

### Requirement: Config 类必须提供扩展的默认配置
Config 类 SHALL 提供包含所有配置类型的默认配置结构，包括系统配置、邮件配置、importers 配置、账户映射等。

#### Scenario: 默认配置包含系统配置节
- **WHEN** 创建默认配置
- **THEN** 配置包含 `system` 节点，其中包含 data_path、rawdata_path、archive_path、balance_accounts

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
Config 类 SHALL 提供 `get_detail_mappings()` 方法，将 YAML 配置中的 detail_mappings 转换为 BillDetailMapping 对象列表。

#### Scenario: 转换 detail_mappings 为对象
- **WHEN** 调用 `config.get_detail_mappings()` 方法且 china_bean_importers 库可用
- **THEN** 返回 BillDetailMapping 对象列表
- **THEN** 每个对象包含 payee_keywords、narration_keywords、account、tags、metadata 字段

#### Scenario: china_bean_importers 不可用时返回原始数据
- **WHEN** 调用 `config.get_detail_mappings()` 方法但 china_bean_importers 库不可用
- **THEN** 返回原始的字典列表
- **THEN** 不抛出异常

### Requirement: Config 类必须提供便捷访问方法
Config 类 SHALL 提供特定配置节的便捷访问方法，简化常用配置的获取。

#### Scenario: 获取邮件配置
- **WHEN** 调用 `config.get_email_config()` 方法
- **THEN** 返回完整的 email 配置字典

#### Scenario: 获取指定导入器配置
- **WHEN** 调用 `config.get_importer_config("alipay")` 方法
- **THEN** 返回对应导入器的配置字典

#### Scenario: 获取密码列表
- **WHEN** 调用 `config.get_passwords()` 方法
- **THEN** 返回合并了 passwords 和 pdf_passwords 的去重列表

### Requirement: Config 类必须支持配置结构检查
Config 类 SHALL 提供方法检查和显示配置结构，方便调试和验证。

#### Scenario: 获取所有顶层配置键
- **WHEN** 调用 `config.keys()` 方法
- **THEN** 返回所有顶层配置键的列表

#### Scenario: 打印配置结构
- **WHEN** 调用 `config.print_structure()` 方法
- **THEN** 以树形结构打印配置的层次结构
