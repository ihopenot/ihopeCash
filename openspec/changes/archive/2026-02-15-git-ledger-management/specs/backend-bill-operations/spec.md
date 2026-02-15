## MODIFIED Requirements

### Requirement: BillManager 必须提供完整月度导入工作流

BillManager 类 SHALL 提供 `import_month_with_progress(year, month, balances, passwords, mode, progress_callback)` 方法，执行完整导入流程。流程 SHALL 从 6 步扩展为 7 步，新增 Step 1 为 git 自动提交。`passwords` 参数 MUST 在所有调用点正确传递。异常处理 MUST 记录日志。

#### Scenario: 完整导入流程成功（7步）
- **WHEN** 调用 `manager.import_month_with_progress("2026", "02", {...}, passwords=[...], mode="normal")`
- **THEN** 系统依次执行: git提交(Step 1)、下载账单(Step 2)、识别文件(Step 3)、创建目录(Step 4)、提取交易(Step 5)、记录余额(Step 6)、归档文件(Step 7)
- **AND** 进度回调的 total 值为 7
- **AND** 返回 `{"success": True, "message": "导入完成", "data": {...}}`

#### Scenario: Step 1 git 提交流程 - 首次初始化
- **WHEN** 导入开始且 `data/.git` 不存在
- **THEN** 系统调用 `git_ensure_repo()` 初始化仓库
- **AND** 发送进度消息 "正在初始化版本管理..."
- **AND** 发送完成消息 "版本管理初始化完成"

#### Scenario: Step 1 git 提交流程 - 提交已有变更
- **WHEN** 导入开始且工作区有未提交变更
- **THEN** 系统从 `.ledger-period` 读取上一次账期
- **AND** 调用 `git_commit_if_dirty(上一次账期)` 提交变更
- **AND** 发送进度消息 "正在提交上期变更..."
- **AND** 提交完成后删除 `.ledger-period`

#### Scenario: Step 1 git 提交流程 - 无变更跳过
- **WHEN** 导入开始且工作区无变更
- **THEN** 系统跳过 git 提交
- **AND** 发送消息 "无待提交的变更，跳过"

#### Scenario: 导入完成后写入当前账期
- **WHEN** 7步全部执行成功
- **THEN** 系统调用 `write_ledger_period` 写入本次选择的年月（如 "2026-02"）

#### Scenario: 导入过程中发生错误
- **WHEN** 导入过程中任一步骤失败
- **THEN** 使用 logging 记录完整异常堆栈
- **AND** 返回 `{"success": False, "message": "<错误信息>", "data": None}`

#### Scenario: 追加模式调用必须传递 passwords 参数
- **WHEN** 以追加模式调用 `import_month_with_progress`
- **THEN** `passwords` 参数 MUST 被正确传递（不可遗漏）
