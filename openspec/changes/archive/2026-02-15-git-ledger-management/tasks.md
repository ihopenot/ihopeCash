## 1. Git 操作方法（backend.py）

- [x] 1.1 在 BillManager 中新增 `_run_git(args)` 私有方法，封装 subprocess 调用 git 命令（工作目录为 data_path）
- [x] 1.2 新增 `git_ensure_repo()` 方法：检测 data/.git，不存在则 init + 创建 .gitignore + 首次全量提交
- [x] 1.3 新增 `git_is_clean()` 方法：通过 `git status --porcelain` 判断工作区是否干净
- [x] 1.4 新增 `git_commit_if_dirty(period)` 方法：有变更时 git add + commit，message 包含账期
- [x] 1.5 新增 `git_discard_changes()` 方法：git checkout -- . + git clean -fd + 清除 .ledger-period

## 2. 账期文件管理（backend.py）

- [x] 2.1 新增 `read_ledger_period()` 方法：读取 data/.ledger-period 文件内容，不存在返回 None
- [x] 2.2 新增 `write_ledger_period(period)` 方法：将账期写入 data/.ledger-period
- [x] 2.3 新增 `clear_ledger_period()` 方法：删除 data/.ledger-period 文件

## 3. 导入流程改造（backend.py）

- [x] 3.1 修改 `import_month_with_progress` 的 total 从 6 改为 7
- [x] 3.2 在现有 Step 1 之前插入新 Step 1（git 提交）：调用 git_ensure_repo + git_commit_if_dirty + clear_ledger_period
- [x] 3.3 现有 Step 1~6 的编号顺移为 Step 2~7
- [x] 3.4 在导入成功返回前调用 write_ledger_period 写入本次账期

## 4. 后端 API（web/app.py）

- [x] 4.1 新增 `GET /api/ledger-status` 端点：读取 ledger-period，结合 git_is_clean 判断，返回 `{"period": ...}`
- [x] 4.2 新增 `POST /api/ledger-discard` 端点：调用 git_discard_changes，返回操作结果

## 5. 前端状态栏（web/static/index.html）

- [x] 5.1 在导航栏下方、账单信息表单上方新增账本状态栏 HTML 结构
- [x] 5.2 新增 `loadLedgerStatus()` 函数：调用 GET /api/ledger-status，根据返回的 period 渲染状态栏
- [x] 5.3 在 `init()` 中调用 `loadLedgerStatus()` 初始化状态栏
- [x] 5.4 新增撤销变更按钮点击处理：弹出二次确认对话框，确认后调用 POST /api/ledger-discard，成功后刷新状态栏
- [x] 5.5 在导入完成回调（handleProgress 中 step === total && status === 'success'）中调用 `loadLedgerStatus()` 刷新状态栏
