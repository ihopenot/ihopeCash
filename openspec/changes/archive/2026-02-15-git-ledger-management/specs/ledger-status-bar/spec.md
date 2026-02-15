## ADDED Requirements

### Requirement: 导入界面必须展示账本状态栏

系统 SHALL 在导入界面顶部（导航栏下方、账单信息表单上方）展示账本状态栏卡片。

#### Scenario: 有正在编辑的账期
- **WHEN** API 返回 `period` 不为 null（如 `"2026-02"`）
- **THEN** 状态栏显示 "当前账期: 2026年2月"
- **AND** 状态栏右侧显示"撤销变更"按钮

#### Scenario: 账本已同步
- **WHEN** API 返回 `period` 为 null
- **THEN** 状态栏显示 "账本已同步"
- **AND** 不显示"撤销变更"按钮

#### Scenario: 页面加载时获取状态
- **WHEN** 页面初始化完成
- **THEN** 系统调用 `GET /api/ledger-status` 获取当前状态并更新状态栏

#### Scenario: 导入完成后更新状态栏
- **WHEN** 导入流程全部完成（7步成功）
- **THEN** 系统重新调用 `GET /api/ledger-status` 刷新状态栏

### Requirement: 用户可以通过状态栏撤销变更

系统 SHALL 在用户点击"撤销变更"按钮后弹出确认对话框，用户二次确认后调用撤销 API。

#### Scenario: 用户点击撤销变更
- **WHEN** 用户点击状态栏的"撤销变更"按钮
- **THEN** 系统弹出确认对话框，内容包含 "即将丢弃上次提交以来的所有修改，此操作不可恢复。"

#### Scenario: 用户确认撤销
- **WHEN** 用户在确认对话框中点击"确认撤销"
- **THEN** 系统调用 `POST /api/ledger-discard`
- **AND** 成功后刷新状态栏，显示"账本已同步"

#### Scenario: 用户取消撤销
- **WHEN** 用户在确认对话框中点击"取消"
- **THEN** 系统不执行任何操作，状态栏保持不变

#### Scenario: 撤销请求失败
- **WHEN** `POST /api/ledger-discard` 返回错误
- **THEN** 系统显示错误提示

### Requirement: 后端必须提供账本状态查询 API

系统 SHALL 提供 `GET /api/ledger-status` 端点，返回当前账本状态。该端点 MUST 要求认证。

#### Scenario: 有正在编辑的账期
- **WHEN** 客户端请求 `GET /api/ledger-status`
- **AND** `.ledger-period` 文件存在且工作区不是 clean
- **THEN** 返回 `{"period": "2026-02"}`

#### Scenario: 账本已同步
- **WHEN** 客户端请求 `GET /api/ledger-status`
- **AND** 工作区是 clean 的
- **THEN** 返回 `{"period": null}`
- **AND** 如果 `.ledger-period` 文件存在则清理它

#### Scenario: data 未初始化 git
- **WHEN** 客户端请求 `GET /api/ledger-status`
- **AND** `data/.git` 不存在
- **THEN** 返回 `{"period": null}`

#### Scenario: 未认证请求
- **WHEN** 未认证客户端请求 `GET /api/ledger-status`
- **THEN** 返回 401 状态码

### Requirement: 后端必须提供账本变更撤销 API

系统 SHALL 提供 `POST /api/ledger-discard` 端点，执行 git 变更丢弃操作。该端点 MUST 要求认证。

#### Scenario: 成功撤销变更
- **WHEN** 客户端请求 `POST /api/ledger-discard`
- **THEN** 系统调用 `git_discard_changes()` 丢弃所有变更
- **AND** 返回 `{"success": true, "message": "变更已撤销"}`

#### Scenario: 无变更可撤销
- **WHEN** 客户端请求 `POST /api/ledger-discard` 且工作区已 clean
- **THEN** 返回 `{"success": true, "message": "无变更需要撤销"}`

#### Scenario: 撤销失败
- **WHEN** git 操作执行失败
- **THEN** 返回 `{"success": false, "message": "<错误信息>"}`

#### Scenario: 未认证请求
- **WHEN** 未认证客户端请求 `POST /api/ledger-discard`
- **THEN** 返回 401 状态码
