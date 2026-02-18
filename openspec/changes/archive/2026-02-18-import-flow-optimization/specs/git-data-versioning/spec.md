## MODIFIED Requirements

### Requirement: BillManager 必须检测并初始化 data git 仓库

BillManager SHALL 提供 `git_ensure_repo()` 方法，检测 `data/.git` 是否存在。若不存在，SHALL 执行 `git init`，创建 `data/.gitignore`（忽略 `.ledger-period` 和 `rawdata/`），然后执行 `git add . && git commit -m "初始化账本"` 完成首次提交。

#### Scenario: data/.git 不存在时自动初始化
- **WHEN** 调用 `git_ensure_repo()` 且 `data/.git` 目录不存在
- **THEN** 系统在 data/ 下执行 `git init`
- **AND** 创建 `data/.gitignore` 文件，内容包含 `.ledger-period` 和 `rawdata/`
- **AND** 执行 `git add .` 和 `git commit -m "初始化账本"`

#### Scenario: data/.git 已存在时跳过
- **WHEN** 调用 `git_ensure_repo()` 且 `data/.git` 目录已存在
- **THEN** 系统不执行任何操作

#### Scenario: git 命令不可用时抛出异常
- **WHEN** 系统未安装 git 命令
- **THEN** 系统抛出 `RuntimeError` 并提示用户安装 git

### Requirement: BillManager 必须能丢弃所有未提交变更

BillManager SHALL 提供 `git_discard_changes(include_rawdata=False)` 方法，丢弃所有未提交的工作区变更，并可选清空 rawdata 目录。

#### Scenario: 不包含 rawdata 的撤销
- **WHEN** 调用 `git_discard_changes(include_rawdata=False)`
- **THEN** 系统执行 `git checkout -- .` 恢复已跟踪文件
- **AND** 执行 `git clean -fd` 删除未跟踪文件
- **AND** 调用 `clear_ledger_period()` 删除 `.ledger-period` 文件
- **AND** rawdata/ 目录不受影响

#### Scenario: 包含 rawdata 的撤销
- **WHEN** 调用 `git_discard_changes(include_rawdata=True)`
- **THEN** 系统执行 `git checkout -- .` 恢复已跟踪文件
- **AND** 执行 `git clean -fd` 删除未跟踪文件
- **AND** 调用 `clear_ledger_period()` 删除 `.ledger-period` 文件
- **AND** 调用 `clear_rawdata()` 清空 rawdata/ 目录下所有文件

#### Scenario: 工作区已 clean 时无副作用
- **WHEN** 调用 `git_discard_changes()` 且工作区无变更
- **THEN** 系统正常执行不报错

### Requirement: data/.gitignore 必须忽略 .ledger-period 和 rawdata/

`data/.gitignore` 文件 SHALL 包含 `.ledger-period` 和 `rawdata/`，确保这两项不被 data git 仓库追踪。

#### Scenario: .ledger-period 不被 git 追踪
- **WHEN** data git 仓库执行 `git status`
- **THEN** `.ledger-period` 文件不出现在变更列表中

#### Scenario: rawdata/ 不被 git 追踪
- **WHEN** data git 仓库执行 `git status`
- **THEN** rawdata/ 目录及其内容不出现在变更列表中
