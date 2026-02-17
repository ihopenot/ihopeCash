## Requirements

### Requirement: Bean 文件位于 data 目录

系统 SHALL 将 `main.bean`、`accounts.bean` 存放在 `data/` 目录下。`main.bean` 中的 `include` 路径 SHALL 使用相对于 `data/` 目录的路径（如 `include "accounts.bean"`、`include "2026/_.bean"`）。

#### Scenario: 新安装时文件位置
- **WHEN** 系统首次部署
- **THEN** `data/main.bean` 和 `data/accounts.bean` 由启动逻辑自动创建在 `data/` 目录下

#### Scenario: 后端引用路径
- **WHEN** `backend.py` 需要读写 `main.bean`
- **THEN** SHALL 使用 `data/main.bean` 路径（即 `{data_path}/main.bean`）

#### Scenario: Fava 启动路径
- **WHEN** Docker entrypoint 启动 Fava
- **THEN** SHALL 指向 `/app/data/beancount/data/main.bean`

### Requirement: 启动时自动创建默认文件

Web 应用启动时 SHALL 检测 `data/main.bean`、`data/accounts.bean` 是否存在，不存在时 SHALL 自动创建默认文件。同时确保 `data/`、`rawdata/`、`archive/` 三个目录存在。

#### Scenario: main.bean 不存在
- **WHEN** Web 应用启动且 `data/main.bean` 不存在或为空文件
- **THEN** 系统 SHALL 创建 `data/main.bean`，内容包含默认账本名称 `ihopeCash`、默认主货币 `CNY`、以及对 `accounts.bean` 的 include 语句

#### Scenario: accounts.bean 不存在
- **WHEN** Web 应用启动且 `data/accounts.bean` 不存在
- **THEN** 系统 SHALL 创建空的 `data/accounts.bean`

#### Scenario: 文件已存在时不覆盖
- **WHEN** Web 应用启动且 `data/main.bean` 已存在且非空
- **THEN** 系统 SHALL 不修改已有文件

#### Scenario: 目录不存在时自动创建
- **WHEN** Web 应用启动且 `data/`、`rawdata/`、`archive/` 目录不存在
- **THEN** 系统 SHALL 使用 `os.makedirs(exist_ok=True)` 创建所有三个目录

### Requirement: 迁移脚本

系统 SHALL 提供迁移脚本 `migrate.py`，将根目录的 `main.bean` 和 `accounts.bean` 迁移到 `data/` 目录下。

#### Scenario: 正常迁移
- **WHEN** 根目录存在 `main.bean` 和 `accounts.bean`，且 `data/` 目录下不存在同名文件
- **THEN** 脚本 SHALL 将文件移动到 `data/` 目录，并修正 `main.bean` 中的 include 路径（将 `include "data/xxx"` 改为 `include "xxx"`，将 `include "accounts.bean"` 保持不变）

#### Scenario: 幂等执行
- **WHEN** 迁移脚本执行时 `data/main.bean` 已存在
- **THEN** 脚本 SHALL 跳过迁移并提示文件已在目标位置

#### Scenario: 根目录文件不存在
- **WHEN** 迁移脚本执行时根目录不存在 `main.bean`
- **THEN** 脚本 SHALL 提示无需迁移

### Requirement: backend.py 动态追加 include 路径适配

`backend.py` 中 `ensure_year_directory` 方法向 `main.bean` 追加年份 include 时，SHALL 使用相对于 `data/` 目录的路径格式。

#### Scenario: 创建新年份目录
- **WHEN** `ensure_year_directory("2027")` 被调用且 `data/2027/` 不存在
- **THEN** SHALL 在 `data/main.bean` 中追加 `include "2027/_.bean"`（而非 `include "data/2027/_.bean"`）
