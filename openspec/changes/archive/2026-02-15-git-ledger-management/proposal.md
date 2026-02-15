## Why

目前 data/ 目录中的账本数据没有版本控制保护。用户在 Fava 或编辑器中手动修改账本后，如果操作失误或导入覆盖了数据，无法回退到之前的状态。需要为 data/ 目录引入独立的 git 仓库管理，在每次导入前自动提交已有变更作为快照，并提供撤销能力让用户可以丢弃未定稿的修改。

## What Changes

- data/ 目录新增独立 git 仓库，与主项目仓库分离
- 导入流程新增 Step 0：在执行现有 6 步之前，自动检测并初始化 data git 仓库，提交所有未提交的变更
- commit message 包含账期信息（用户选择的年月）
- 新增 `data/.ledger-period` 文件记录当前正在编辑的账期，不纳入 git
- 导入界面新增"账本状态栏"，展示当前正在编辑的账期或已同步状态
- 状态栏支持撤销操作：二次确认后 git 丢弃所有未提交变更，恢复到上次提交状态

## Capabilities

### New Capabilities
- `git-data-versioning`: data/ 目录的独立 git 仓库管理，包括初始化、自动提交、变更丢弃等 git 操作
- `ledger-status-bar`: 导入界面的账本状态栏，展示当前账期和撤销操作

### Modified Capabilities
- `backend-bill-operations`: 导入流程新增 Step 0 git 提交步骤，总步数从 6 变为 7
- `web-import-interface`: 导入界面新增账本状态栏区域

## Impact

- **backend.py**: 新增 git 操作方法（init、commit、status、discard），修改 `import_month_with_progress` 增加 Step 0
- **web/app.py**: 新增 API 端点 `GET /api/ledger-status` 和 `POST /api/ledger-discard`
- **web/static/index.html**: 新增账本状态栏 UI 组件和撤销交互逻辑
- **data/.gitignore**: 新增，忽略 `.ledger-period` 文件
- **data/.ledger-period**: 新增，记录当前账期（不纳入 git）
- **依赖**: 无新增外部依赖，git 通过 subprocess 调用系统命令
