## Why

当前配置管理分散在多个文件中（`backend.py` 中的 Config 类、`config.py` 加载函数、`config.example.py` 的 importer 配置），导致配置难以维护和复用。`beancount_config.py` 和 `backend.py` 使用不同的配置源，造成重复和不一致。需要统一配置架构，使所有模块从单一配置源加载配置。

## What Changes

- 将 `backend.py` 中的 Config 类提取到独立的 `config.py` 文件
- 扩展 Config 类以支持所有配置类型（系统配置、邮件配置、Beancount importers 配置）
- 统一 `config.yaml` 作为唯一配置源，添加 `importers`、`passwords`、`card_accounts`、`detail_mappings` 等配置节
- 修改 `beancount_config.py` 使用统一的 Config 类，不再依赖 `china_bean_importer_config.py`
- Config 类支持三种访问方式：属性访问（`config.data_path`）、字典访问（`config["email"]["imap"]`）、完整字典导出（`config.to_dict()`）
- Config 类提供 `get_detail_mappings()` 方法，将 YAML 配置转换为 `BillDetailMapping` 对象
- **BREAKING**: `config.yaml` 结构变更，系统配置移至 `system` 命名空间下（向后兼容通过默认值合并处理）
- **BREAKING**: 从 `backend` 导入 Config 的代码需改为从 `config` 导入

## Capabilities

### New Capabilities
- `unified-config-management`: 统一配置管理能力，支持从单一 YAML 文件加载和管理所有类型的配置（系统、邮件、importers），提供多种访问方式和对象转换功能

### Modified Capabilities
- `backend-config`: 扩展配置管理需求，增加对嵌套配置结构、多种访问模式、对象转换、默认值深度合并等功能的支持

## Impact

**受影响的文件**：
- `config.py` - 完全重写，实现统一 Config 类
- `backend.py` - 删除 Config 类定义，添加 `from config import Config` 导入
- `beancount_config.py` - 重写以使用统一 Config 类
- `main.py` - 修改导入语句（从 `config` 而非 `backend` 导入 Config）
- `config.yaml` - 扩展配置结构，添加新的配置节
- `mail.py` - 无需修改（已兼容字典访问）

**依赖**：
- 依赖 `china_bean_importers` 库的 `BillDetailMapping` 类（用于对象转换）
- 依赖 `yaml` 库（用于配置文件读写）

**向后兼容性**：
- Config 类保留所有现有的属性和方法
- 通过智能默认值合并处理旧配置文件格式
- `mail.py` 无需修改即可使用新配置
