## ADDED Requirements

### Requirement: Config 类必须加载或创建配置文件
Config 类 SHALL 在初始化时尝试加载指定的 YAML 配置文件,若文件不存在则创建默认配置文件并保存。

#### Scenario: 默认加载 config.yaml
- **WHEN** 创建 Config 实例时未指定配置文件路径
- **THEN** 系统从当前目录加载 config.yaml 文件

#### Scenario: 加载指定配置文件
- **WHEN** 创建 Config 实例时指定了配置文件路径
- **THEN** 系统从指定路径加载配置文件

#### Scenario: 配置文件不存在时自动创建
- **WHEN** 指定的配置文件不存在
- **THEN** 系统创建默认配置实例并保存到指定路径
- **THEN** 加载该默认配置

### Requirement: Config 类必须提供默认配置
Config 类 SHALL 定义默认配置结构,包含 data_path, rawdata_path, archive_path, balance_accounts 等必要字段。

#### Scenario: 默认配置包含所有必要字段
- **WHEN** 创建默认配置
- **THEN** 配置包含 data_path 默认值为 "data"
- **THEN** 配置包含 rawdata_path 默认值为 "rawdata"
- **THEN** 配置包含 archive_path 默认值为 "archive"
- **THEN** 配置包含 balance_accounts 默认值为空列表

### Requirement: Config 类必须支持保存配置到文件
Config 类 SHALL 提供 `save(file_path=None)` 方法,将当前配置保存到 YAML 文件。

#### Scenario: 保存到当前配置文件路径
- **WHEN** 调用 `config.save()` 且未指定路径
- **THEN** 系统将配置保存到初始化时使用的配置文件路径

#### Scenario: 保存到指定路径
- **WHEN** 调用 `config.save("/path/to/new_config.yaml")`
- **THEN** 系统将配置保存到指定路径

### Requirement: Config 类必须支持字典式访问
Config 类 SHALL 实现 `__getitem__` 方法,支持 `config["key"]` 方式访问配置项。

#### Scenario: 使用字典方式访问存在的配置项
- **WHEN** 使用 `config["data_path"]` 访问存在的配置项
- **THEN** 返回对应的配置值

#### Scenario: 访问不存在的配置项
- **WHEN** 使用 `config["nonexistent"]` 访问不存在的配置项
- **THEN** 抛出 KeyError 异常

### Requirement: Config 类必须支持安全访问方法
Config 类 SHALL 提供 `get(key, default)` 方法,支持带默认值的安全访问。

#### Scenario: 安全访问存在的配置项
- **WHEN** 使用 `config.get("data_path")` 访问存在的配置项
- **THEN** 返回对应的配置值

#### Scenario: 安全访问不存在的配置项并提供默认值
- **WHEN** 使用 `config.get("nonexistent", "default_value")` 访问不存在的配置项
- **THEN** 返回默认值 "default_value"

### Requirement: Config 类必须提供常用配置的属性访问
Config 类 SHALL 提供属性方法访问常用配置项: data_path, rawdata_path, archive_path, balance_accounts。

#### Scenario: 通过属性访问 data_path
- **WHEN** 使用 `config.data_path` 访问数据路径
- **THEN** 返回配置中的 data_path 值

#### Scenario: 通过属性访问 balance_accounts
- **WHEN** 使用 `config.balance_accounts` 访问余额账户列表
- **THEN** 返回配置中的 balance_accounts 数组,如不存在则返回空列表

### Requirement: Config 类必须支持配置重载
Config 类 SHALL 提供 `load()` 方法,支持重新加载配置文件。

#### Scenario: 重载配置文件
- **WHEN** 调用 `config.load()` 方法
- **THEN** 系统重新读取配置文件并更新内部配置数据
