## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: Config 类 update_from_web 必须使用深度合并
`update_from_web()` 方法更新嵌套配置时 MUST 使用深度合并（而非 `dict.update()` 浅合并），以避免丢失未传入的嵌套键。

#### Scenario: 更新嵌套配置保留未传入的键
- **WHEN** 调用 `update_from_web({"system": {"data_path": "new_path"}})` 且原配置 system 下还有 rawdata_path
- **THEN** rawdata_path 保留不变，data_path 被更新
