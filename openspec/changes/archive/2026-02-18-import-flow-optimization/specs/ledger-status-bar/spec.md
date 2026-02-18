## MODIFIED Requirements

### Requirement: 用户可以通过状态栏撤销变更

系统 SHALL 在用户点击"撤销变更"按钮后弹出包含复选框的确认对话框，用户可选择是否同时清空原文件目录。

#### Scenario: 用户点击撤销变更
- **WHEN** 用户点击状态栏的"撤销变更"按钮
- **THEN** 系统弹出自定义确认对话框
- **AND** 对话框包含复选框"同时清空原文件目录"
- **AND** 对话框包含说明文字"勾选后将同时删除原文件目录中的所有文件，否则仅回退导入结果，保留原文件。"
- **AND** 提供"取消"和"确认撤销"按钮

#### Scenario: 用户确认撤销（不勾选清空原文件）
- **WHEN** 用户未勾选"同时清空原文件目录"
- **AND** 点击"确认撤销"
- **THEN** 系统调用 `POST /api/ledger-discard`，请求体为 `{"include_rawdata": false}`
- **AND** 成功后刷新状态栏，显示"账本已同步"

#### Scenario: 用户确认撤销（勾选清空原文件）
- **WHEN** 用户勾选"同时清空原文件目录"
- **AND** 点击"确认撤销"
- **THEN** 系统调用 `POST /api/ledger-discard`，请求体为 `{"include_rawdata": true}`
- **AND** 成功后刷新状态栏
- **AND** 刷新原文件列表（因为 rawdata 已被清空）

#### Scenario: 用户取消撤销
- **WHEN** 用户在确认对话框中点击"取消"
- **THEN** 系统不执行任何操作，状态栏保持不变

#### Scenario: 撤销请求失败
- **WHEN** `POST /api/ledger-discard` 返回错误
- **THEN** 系统显示错误提示

### Requirement: 后端必须提供账本变更撤销 API

系统 SHALL 提供 `POST /api/ledger-discard` 端点，执行 git 变更丢弃操作，支持可选清空 rawdata。该端点 MUST 要求认证。

#### Scenario: 撤销不含 rawdata
- **WHEN** 客户端请求 `POST /api/ledger-discard`，请求体为 `{"include_rawdata": false}`
- **THEN** 系统调用 `git_discard_changes(include_rawdata=False)`
- **AND** 返回 `{"success": true, "message": "变更已撤销"}`

#### Scenario: 撤销包含 rawdata
- **WHEN** 客户端请求 `POST /api/ledger-discard`，请求体为 `{"include_rawdata": true}`
- **THEN** 系统调用 `git_discard_changes(include_rawdata=True)`
- **AND** 返回 `{"success": true, "message": "变更已撤销，原文件已清空"}`

#### Scenario: 无变更可撤销
- **WHEN** 客户端请求 `POST /api/ledger-discard` 且工作区已 clean
- **THEN** 返回 `{"success": true, "message": "无变更需要撤销"}`

#### Scenario: 撤销失败
- **WHEN** git 操作执行失败
- **THEN** 返回 `{"success": false, "message": "<错误信息>"}`

#### Scenario: 未认证请求
- **WHEN** 未认证客户端请求 `POST /api/ledger-discard`
- **THEN** 返回 401 状态码

### Requirement: 后端必须提供账本状态查询 API

系统 SHALL 提供 `GET /api/ledger-status` 端点，返回当前账本状态。该端点 MUST 要求认证。返回值 MUST 包含 `is_clean` 字段。

#### Scenario: 有正在编辑的账期
- **WHEN** 客户端请求 `GET /api/ledger-status`
- **AND** `.ledger-period` 文件存在且工作区不是 clean
- **THEN** 返回 `{"period": "2026-02", "is_clean": false}`

#### Scenario: 账本已同步
- **WHEN** 客户端请求 `GET /api/ledger-status`
- **AND** 工作区是 clean 的
- **THEN** 返回 `{"period": null, "is_clean": true}`
- **AND** 如果 `.ledger-period` 文件存在则清理它

#### Scenario: 未认证请求
- **WHEN** 未认证客户端请求 `GET /api/ledger-status`
- **THEN** 返回 401 状态码
