## ADDED Requirements

### Requirement: 导入界面必须包含账本状态栏

系统 SHALL 在导入界面导航栏下方、账单信息表单上方新增账本状态栏卡片，展示当前账期或已同步状态。

#### Scenario: 页面加载时展示账本状态
- **WHEN** 已认证用户打开导入页面
- **THEN** 系统调用 `GET /api/ledger-status` 获取状态
- **AND** 根据返回结果渲染状态栏

#### Scenario: 状态栏展示当前账期
- **WHEN** API 返回 `period` 为 `"2026-02"`
- **THEN** 状态栏显示 "当前账期: 2026年2月"
- **AND** 右侧显示"撤销变更"按钮

#### Scenario: 状态栏展示已同步
- **WHEN** API 返回 `period` 为 null
- **THEN** 状态栏显示 "账本已同步"
- **AND** 不显示"撤销变更"按钮

### Requirement: 用户可以在导入界面撤销账本变更

系统 SHALL 在用户点击"撤销变更"按钮后弹出二次确认对话框，确认后执行撤销。

#### Scenario: 点击撤销弹出确认
- **WHEN** 用户点击"撤销变更"按钮
- **THEN** 弹出确认对话框，提示此操作不可恢复

#### Scenario: 确认后执行撤销
- **WHEN** 用户在确认对话框中确认
- **THEN** 系统调用 `POST /api/ledger-discard`
- **AND** 成功后刷新状态栏显示"账本已同步"

#### Scenario: 取消撤销
- **WHEN** 用户在确认对话框中取消
- **THEN** 不执行任何操作

## MODIFIED Requirements

### Requirement: User can see real-time progress log

The system SHALL display a scrollable log area showing import progress messages received via WebSocket.

#### Scenario: Progress messages displayed in order
- **WHEN** system receives progress message from WebSocket
- **THEN** system appends message to log area with icon and text
- **AND** system scrolls log to bottom automatically

#### Scenario: Step indicators show progress
- **WHEN** system receives progress message with step number
- **THEN** system displays "[X/7]" prefix showing current step (total changed from 6 to 7)

#### Scenario: Import completes and refreshes status bar
- **WHEN** all 7 steps complete successfully
- **THEN** system displays "导入完成!" message
- **AND** system calls `GET /api/ledger-status` to refresh status bar

#### Scenario: Success messages show checkmark
- **WHEN** system receives message with status "success"
- **THEN** system displays "✓" icon before message text

#### Scenario: Running messages show loading icon
- **WHEN** system receives message with status "running"
- **THEN** system displays "▶" icon before message text

#### Scenario: Error messages show error icon
- **WHEN** system receives message with status "error"
- **THEN** system displays "✗" icon before message text
