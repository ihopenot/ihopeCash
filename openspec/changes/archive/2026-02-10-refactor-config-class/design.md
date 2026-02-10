## Context

当前 IhopeCash 项目的配置管理分散在多个文件和模块中：
- `backend.py` 中定义了 Config 类，负责加载 `config.yaml` 中的系统配置（路径、余额账户）
- `config.py` 提供了简单的 `load_config()` 函数，返回配置字典
- `china_bean_importers/config.example.py` 包含 Beancount 导入器的配置（账户映射、分类规则等）
- `beancount_config.py` 从 `china_bean_importer_config` 导入配置并传递给各个 Importer

这种分散的架构导致：
1. **配置重复**：`backend.py` 和 `mail.py` 使用不同方式访问配置
2. **难以维护**：配置分布在不同文件，修改时需要同步多处
3. **不一致**：系统配置和 importer 配置使用不同的加载机制

**约束条件**：
- 必须保持向后兼容，现有代码（`backend.py`, `main.py`, `mail.py`）应尽量少改
- `china_bean_importers` 的 Importer 类期望接收字典类型的配置
- 配置文件应保持人类可读，使用 YAML 格式

**利益相关者**：
- 开发者：需要一个清晰、统一的配置管理接口
- 最终用户：需要在单一文件中配置所有参数

## Goals / Non-Goals

**Goals:**
- 创建统一的 Config 类，管理所有配置类型（系统、邮件、importers）
- 将 Config 类提取到独立的 `config.py` 文件，消除循环依赖
- 支持三种访问方式：属性访问、字典访问、完整字典导出
- 实现智能默认值深度合并，确保所有必需字段存在
- 提供 YAML 到 Python 对象的转换（如 `BillDetailMapping`）
- 保持向后兼容，现有 API 不变

**Non-Goals:**
- 不支持动态配置热重载（仍需重启应用）
- 不提供配置加密或敏感信息保护（密码仍明文存储在 YAML 中）
- 不支持多种配置文件格式（仅支持 YAML）
- 不验证配置值的合法性（如邮箱格式、账户名称等）

## Decisions

### Decision 1: Config 类放置在独立的 config.py 文件

**决策**：将 Config 类从 `backend.py` 提取到新的 `config.py` 文件。

**理由**：
- `backend.py` 应专注于业务逻辑（BillManager），配置管理是独立职责
- 避免循环依赖：`beancount_config.py` 和 `main.py` 都需要 Config，但不需要 BillManager
- 更清晰的模块划分，符合单一职责原则

**备选方案**：
- 方案 A：保留在 `backend.py`，其他模块从 `backend` 导入 Config
  - 缺点：增加不必要的依赖，`beancount_config.py` 不需要 BillManager
- 方案 B：创建 `core.config` 模块
  - 缺点：过度设计，项目规模不需要多级模块结构

### Decision 2: 使用嵌套字典结构存储配置

**决策**：配置使用嵌套字典，顶层键为配置类别（`system`, `email`, `importers` 等）。

**理由**：
- 清晰的命名空间，避免键名冲突（如 `system.account` vs `importers.alipay.account`）
- 便于分组管理，相关配置聚合在一起
- 符合 YAML 最佳实践，层次结构清晰

**备选方案**：
- 方案 A：平铺结构（`data_path`, `email_host` 等）
  - 缺点：键名冗长，难以扩展，容易冲突
- 方案 B：多文件配置（`system.yaml`, `importers.yaml`）
  - 缺点：增加复杂度，用户需要管理多个文件

**BREAKING CHANGE**：
- 旧配置：`data_path: data`（顶层）
- 新配置：`system.data_path: data`（嵌套）
- **缓解措施**：属性访问（`config.data_path`）自动处理命名空间，`_merge_defaults()` 补全缺失字段

### Decision 3: 支持三种访问模式

**决策**：Config 类同时支持属性访问、字典访问、字典导出三种模式。

**理由**：
- **属性访问**（`config.data_path`）：最便捷，适合频繁访问的系统配置
- **字典访问**（`config["email"]["imap"]`）：最灵活，适合动态访问或嵌套配置
- **字典导出**（`config.to_dict()`）：适合传递给第三方库（如 Importer）

**实现**：
- 属性访问：`@property` 装饰器，从 `self._config["system"]` 读取
- 字典访问：`__getitem__` 魔术方法，直接返回 `self._config[key]`
- 字典导出：`to_dict()` 返回 `copy.deepcopy(self._config)`

**备选方案**：
- 方案 A：只支持字典访问
  - 缺点：代码冗长（`config["system"]["data_path"]` vs `config.data_path`）
- 方案 B：只支持属性访问
  - 缺点：无法动态访问，难以传递给 Importer

### Decision 4: 使用深度合并策略处理默认值

**决策**：实现 `_deep_merge(target, source)` 递归合并默认值和用户配置。

**理由**：
- 确保所有必需字段存在，避免 KeyError
- 用户只需配置非默认值，减少配置文件大小
- 支持嵌套配置的部分覆盖（如只配置 `importers.alipay.account`，其他字段使用默认值）

**算法**：
```python
def _deep_merge(target, source):
    for key, value in source.items():
        if key not in target:
            target[key] = value  # 添加缺失字段
        elif isinstance(value, dict) and isinstance(target[key], dict):
            _deep_merge(target[key], value)  # 递归合并嵌套字典
        # else: 保留用户配置
```

**备选方案**：
- 方案 A：简单覆盖（`config = {**defaults, **user_config}`）
  - 缺点：不支持嵌套合并，用户必须完整配置每个嵌套节点
- 方案 B：要求用户配置所有字段
  - 缺点：配置文件冗长，升级时需手动添加新字段

### Decision 5: 提供 get_detail_mappings() 转换 YAML 为对象

**决策**：Config 类提供专门的方法将 YAML 中的 `detail_mappings` 转换为 `BillDetailMapping` 对象。

**理由**：
- `china_bean_importers` 的 Importer 期望接收 `BillDetailMapping` 对象，而非字典
- 将转换逻辑封装在 Config 类中，`beancount_config.py` 只需调用方法
- 支持降级：如果库不可用，返回原始字典，不影响其他功能

**实现**：
```python
def get_detail_mappings(self):
    try:
        from china_bean_importers.common import BillDetailMapping as BDM
        return [BDM(**mapping) for mapping in self._config.get("detail_mappings", [])]
    except ImportError:
        return self._config.get("detail_mappings", [])
```

**备选方案**：
- 方案 A：在 `beancount_config.py` 中手动转换
  - 缺点：重复逻辑，如果多处需要转换则不便维护
- 方案 B：直接在 YAML 中写 Python 代码（使用 `!!python/object`）
  - 缺点：不安全，破坏 YAML 的可读性和可移植性

### Decision 6: 默认配置包含所有 Importer 字段

**决策**：`_get_default_config()` 为每个 importer（alipay、wechat 等）提供完整的默认字段。

**理由**：
- 避免 Importer 访问不存在的字段时抛出 KeyError
- 作为配置文档，用户可以查看所有可配置项
- 简化用户配置，只需修改需要的字段

**示例**：
```python
"importers": {
    "alipay": {
        "account": "Assets:Alipay:Balance",
        "huabei_account": "Liabilities:Alipay:HuaBei",
        "category_mapping": {}
    },
    # ... 其他 importers
}
```

**备选方案**：
- 方案 A：只提供顶层 `importers: {}` 默认值
  - 缺点：用户必须查阅文档了解所有字段，容易遗漏

## Risks / Trade-offs

### [Risk] BREAKING CHANGE：配置文件结构变更
**影响**：用户升级后，旧的 `config.yaml`（平铺结构）与新代码不兼容。

**缓解措施**：
1. 属性访问（`config.data_path`）自动处理新旧结构，优先从 `system.data_path` 读取，回退到顶层 `data_path`
2. `_merge_defaults()` 自动补全缺失的嵌套结构
3. 提供迁移脚本或文档，指导用户手动调整配置

**评估**：中等风险，可通过缓解措施降低影响。

### [Risk] BREAKING CHANGE：导入路径变更
**影响**：现有代码中 `from backend import Config` 将失败。

**缓解措施**：
1. 修改 `main.py`：`from config import Config`
2. 可选：在 `backend.py` 中保留兼容导入：`from config import Config`（但不推荐，增加耦合）

**评估**：低风险，影响范围小，易于修复。

### [Trade-off] 配置验证缺失
**说明**：Config 类不验证配置值的合法性（如邮箱格式、账户名称、路径是否存在等）。

**理由**：
- 验证逻辑复杂，增加维护成本
- 不同字段有不同验证规则，难以统一
- 错误配置会在运行时被发现（如连接失败、文件不存在）

**影响**：用户可能因配置错误导致运行时错误，但通过错误消息可定位问题。

### [Trade-off] 深拷贝性能开销
**说明**：`to_dict()` 使用 `copy.deepcopy()` 确保返回独立副本，可能有性能开销。

**理由**：
- 配置加载频率低（通常只在启动时），性能影响可忽略
- 确保安全性，避免外部修改影响 Config 实例

**影响**：可接受，配置对象不大，深拷贝开销在毫秒级。

### [Trade-off] china_bean_importers 硬依赖
**说明**：`get_detail_mappings()` 依赖 `china_bean_importers` 库。

**缓解措施**：
- 使用 try-except 捕获 ImportError，降级返回字典
- 仅在调用 `get_detail_mappings()` 时尝试导入，不影响 Config 类的其他功能

**影响**：如果库不可用，`beancount_config.py` 无法正常工作，但不影响 `backend.py` 和 `mail.py`。

## Migration Plan

### 步骤 1: 创建新的 config.py
- 实现完整的 Config 类，包含所有方法和属性
- 包含扩展的 `_get_default_config()`，覆盖所有配置节

### 步骤 2: 修改 backend.py
- 删除 Config 类定义（第 16-108 行）
- 添加导入：`from config import Config`
- 修改 `download_bills()`：使用 `config.to_dict()` 而非 `config._config`

### 步骤 3: 更新 config.yaml
- 添加新的配置节：`system`, `importers`, `passwords`, `card_accounts`, `detail_mappings`
- 将现有的顶层 `data_path` 等移至 `system` 命名空间下
- 从 `config.example.py` 迁移 importer 配置到 `importers` 节

### 步骤 4: 重写 beancount_config.py
- 从 `config import Config` 加载配置
- 使用 `config.to_dict()` 和 `config.get_detail_mappings()` 构建配置字典
- 移除对 `china_bean_importer_config` 的依赖

### 步骤 5: 修改 main.py
- 更新导入：`from config import Config` 而非 `from backend import Config`

### 步骤 6: 测试验证
- 运行 `python main.py` 测试完整流程
- 运行 `bean-identify beancount_config.py rawdata` 验证 beancount 集成
- 测试 `config.data_path` 等属性访问
- 测试 `config["email"]["imap"]` 字典访问
- 测试 `config.to_dict()` 字典导出

### 回滚策略
如果遇到严重问题：
1. 恢复备份的 `backend.py`（包含 Config 类）
2. 恢复备份的 `config.yaml`
3. 恢复备份的 `beancount_config.py`
4. 删除新的 `config.py`

备份命令：
```bash
cp config.py config.py.bak
cp backend.py backend.py.bak
cp config.yaml config.yaml.bak
cp beancount_config.py beancount_config.py.bak
```

## Open Questions

无。所有技术决策已明确，可以开始实现。
