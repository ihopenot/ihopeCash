## MODIFIED Requirements

### Requirement: BillManager 必须检测并初始化 data git 仓库

BillManager SHALL 提供 `git_ensure_repo()` 方法，检测 `data/.git` 是否存在。若不存在，SHALL 执行 `git init`，创建 `data/.gitignore`（忽略 `.ledger-period` 和 `rawdata/`），然后执行 `git add . && git commit -m "初始化账本"` 完成首次提交。

应用 SHALL 在启动时调用 `git_ensure_repo()`，确保 git 仓库在所有功能可用前就已初始化。

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

#### Scenario: 应用启动时确保 git 仓库已初始化
- **WHEN** 应用启动（`startup_event` 触发）
- **THEN** 系统在 `ensure_default_bean_files()` 之后调用 `git_ensure_repo()`
- **AND** 后续所有 `git_is_clean()` 调用都能正确检测工作区状态
