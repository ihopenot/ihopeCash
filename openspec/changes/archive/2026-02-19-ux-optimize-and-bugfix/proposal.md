## Why

导入界面存在两个体验问题和一个 bug：1）用户点击与后台交互的按钮（邮件下载、开始导入、归档）后，执行日志在页面底部，用户需手动滚动才能看到进度；2）账本状态栏没有手动刷新按钮，当自动刷新未生效时用户无法主动获取最新状态；3）`git_ensure_repo()` 仅在归档时才调用，导致应用启动后 git 仓库可能不存在，`git_is_clean()` 在无 `.git` 目录时直接返回 `True`，使状态栏始终显示"账本已同步"，无法检测到导入产生的变更。

## What Changes

- 点击"从邮件下载"、"开始导入"、"归档当前修改"按钮后，页面自动平滑滚动到执行日志区域
- 账本状态栏增加手动刷新按钮，点击后重新获取 `GET /api/ledger-status` 并更新状态显示
- 应用启动时（`startup_event`）调用 `git_ensure_repo()`，确保 git 仓库在所有功能可用前就已初始化

## Capabilities

### New Capabilities

（无新增能力）

### Modified Capabilities

- `web-import-interface`: 后台操作按钮点击后自动滚动到执行日志区域
- `ledger-status-bar`: 增加手动刷新状态按钮
- `git-data-versioning`: 应用启动时确保 git 仓库已初始化，而非仅在归档时

## Impact

- `web/static/index.html`: 修改 `showProgressSection()` 函数增加滚动逻辑；状态栏 HTML 增加刷新按钮及对应事件绑定
- `web/app.py`: `startup_event` 中增加 `git_ensure_repo()` 调用
