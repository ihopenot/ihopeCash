## MODIFIED Requirements

### Requirement: User can see real-time progress log

系统 SHALL 在页面底部提供可滚动的执行日志区域，显示所有操作的进度消息。邮件下载、导入、归档三个操作共用此区域。当操作触发日志区显示时，页面 SHALL 自动平滑滚动到日志区域。

#### Scenario: Progress messages displayed in order
- **WHEN** system receives progress message from WebSocket
- **THEN** system appends message to log area with icon and text
- **AND** system scrolls log to bottom automatically

#### Scenario: Step indicators show progress
- **WHEN** system receives progress message with step number
- **THEN** system displays "[X/N]" prefix showing current step out of total

#### Scenario: Import completes and refreshes status bar
- **WHEN** all import steps complete successfully
- **THEN** system displays "导入完成!" message
- **AND** system calls `GET /api/ledger-status` to refresh status bar

#### Scenario: 新操作开始时清空日志
- **WHEN** 用户触发新操作（邮件下载、导入、归档）
- **THEN** 系统清空执行日志区域
- **AND** 显示新操作的进度

#### Scenario: 操作触发时自动滚动到日志区
- **WHEN** 用户点击"从邮件下载"、"开始导入"或"归档当前修改"按钮
- **AND** 系统展示执行日志区域
- **THEN** 页面自动平滑滚动到执行日志区域顶部
