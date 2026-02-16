## MODIFIED Requirements

### Requirement: BillManager 必须检测并初始化 data git 仓库

BillManager SHALL 提供 `git_ensure_repo()` 方法，检测 `beancount_path/.git` 是否存在。若不存在，SHALL 执行 `git init`，创建 `.gitignore`（忽略 `.ledger-period`），然后执行 `git add . && git commit -m "初始化账本"` 完成首次提交。git 仓库的工作目录 SHALL 为 `beancount_path`（即 `data/beancount/`），管理 `data/`、`rawdata/`、`archive/` 三个子目录。

#### Scenario: beancount_path/.git 不存在时自动初始化
- **WHEN** 调用 `git_ensure_repo()` 且 `beancount_path/.git` 目录不存在
- **THEN** 系统在 `beancount_path` 下执行 `git init`
- **AND** 创建 `beancount_path/.gitignore` 文件，内容包含 `.ledger-period`
- **AND** 执行 `git add .` 和 `git commit -m "初始化账本"`

#### Scenario: beancount_path/.git 已存在时跳过
- **WHEN** 调用 `git_ensure_repo()` 且 `beancount_path/.git` 目录已存在
- **THEN** 系统不执行任何操作

#### Scenario: git 命令不可用时抛出异常
- **WHEN** 系统未安装 git 命令
- **THEN** 系统抛出 `RuntimeError` 并提示用户安装 git

### Requirement: BillManager 必须在有变更时自动提交

BillManager SHALL 提供 `git_commit_if_dirty(period: str)` 方法，检查工作区状态并在有变更时提交。commit message SHALL 包含传入的账期参数。git 操作的 cwd SHALL 为 `beancount_path`。

#### Scenario: 工作区有变更时提交
- **WHEN** 调用 `git_commit_if_dirty("2026-01")` 且工作区有未提交的变更
- **THEN** 系统在 `beancount_path` 下执行 `git add .` 和 `git commit -m "账期 2026-01"`

#### Scenario: 工作区无变更时跳过
- **WHEN** 调用 `git_commit_if_dirty("2026-01")` 且工作区无变更
- **THEN** 系统不执行 commit 操作

### Requirement: BillManager 必须能丢弃所有未提交变更

BillManager SHALL 提供 `git_discard_changes()` 方法，丢弃所有未提交的工作区变更。git 操作的 cwd SHALL 为 `beancount_path`。

#### Scenario: 丢弃所有变更
- **WHEN** 调用 `git_discard_changes()` 且工作区有未提交变更
- **THEN** 系统执行 `git checkout -- .` 恢复已跟踪文件
- **AND** 执行 `git clean -fd` 删除未跟踪文件
- **AND** 调用 `clear_ledger_period()` 删除 `.ledger-period` 文件

#### Scenario: 工作区已 clean 时无副作用
- **WHEN** 调用 `git_discard_changes()` 且工作区无变更
- **THEN** 系统正常执行不报错

### Requirement: BillManager 必须能检查工作区状态

BillManager SHALL 提供 `git_is_clean() -> bool` 方法，返回工作区是否干净。git 操作的 cwd SHALL 为 `beancount_path`。

#### Scenario: 工作区干净
- **WHEN** 调用 `git_is_clean()` 且 `git status --porcelain` 输出为空
- **THEN** 返回 `True`

#### Scenario: 工作区有变更
- **WHEN** 调用 `git_is_clean()` 且 `git status --porcelain` 输出不为空
- **THEN** 返回 `False`

#### Scenario: beancount_path 未初始化 git 仓库
- **WHEN** 调用 `git_is_clean()` 且 `beancount_path/.git` 不存在
- **THEN** 返回 `True`（视为无变更状态）

### Requirement: BillManager 必须管理 .ledger-period 文件

BillManager SHALL 提供 `read_ledger_period()`, `write_ledger_period(period)`, `clear_ledger_period()` 三个方法管理 `data_path/.ledger-period` 文件。

#### Scenario: 写入账期
- **WHEN** 调用 `write_ledger_period("2026-02")`
- **THEN** 系统将 `2026-02` 写入 `data_path/.ledger-period` 文件

#### Scenario: 读取账期
- **WHEN** 调用 `read_ledger_period()` 且 `.ledger-period` 文件存在
- **THEN** 返回文件内容（如 `"2026-02"`）

#### Scenario: 文件不存在时读取返回 None
- **WHEN** 调用 `read_ledger_period()` 且 `.ledger-period` 文件不存在
- **THEN** 返回 `None`

#### Scenario: 清除账期文件
- **WHEN** 调用 `clear_ledger_period()`
- **THEN** 系统删除 `data_path/.ledger-period` 文件（如果存在）

### Requirement: beancount_path/.gitignore 必须忽略 .ledger-period

`beancount_path/.gitignore` 文件 SHALL 包含 `.ledger-period`，确保该文件不被 git 仓库追踪。

#### Scenario: .ledger-period 不被 git 追踪
- **WHEN** beancount git 仓库执行 `git status`
- **THEN** `.ledger-period` 文件不出现在变更列表中
