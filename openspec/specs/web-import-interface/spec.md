## ADDED Requirements

### Requirement: User can view balance accounts from config

The system SHALL fetch and display balance accounts list from config.yaml on page load via GET /api/config endpoint.

#### Scenario: Page loads with balance accounts
- **WHEN** authenticated user opens the main page
- **THEN** system displays input fields for each account in config.balance_accounts

#### Scenario: Default year and month displayed
- **WHEN** authenticated user opens the main page
- **THEN** system pre-fills year and month fields with current or previous month

### Requirement: User can fill import form

The system SHALL provide a form with fields for year, month, import mode, and balance amounts for each account.

#### Scenario: User selects year and month
- **WHEN** user selects year from dropdown (e.g., 2025)
- **AND** user selects month from dropdown (e.g., 02)
- **THEN** system updates form state with selected values

#### Scenario: User selects import mode
- **WHEN** user selects one of three radio options (normal/force/append)
- **THEN** system displays mode description below radio buttons

#### Scenario: User enters balance amounts
- **WHEN** user types balance amount in each account input field
- **THEN** system validates input is numeric format

### Requirement: 用户可以在导入表单中填写附件密码

系统 SHALL 在导入表单中提供 passwords 动态列表输入区域，用户每次导入时手动填写附件解压密码。

#### Scenario: passwords 输入区域显示
- **WHEN** 已认证用户打开主页面
- **THEN** 在"账单信息"和"账户余额"之间显示"附件密码"卡片
- **AND** 卡片内包含动态增减的密码输入框列表

#### Scenario: 添加密码
- **WHEN** 用户点击"添加密码"按钮
- **THEN** 系统在列表末尾新增一个 password 类型的输入框

#### Scenario: 删除密码
- **WHEN** 用户点击某行密码旁的删除按钮
- **THEN** 系统移除该行密码输入框

#### Scenario: passwords 为空提交
- **WHEN** 用户未填写任何密码直接提交导入
- **THEN** 系统正常提交，passwords 为空列表

#### Scenario: passwords 随导入请求提交
- **WHEN** 用户填写了密码并点击"开始导入"
- **THEN** 系统将 passwords 列表包含在 POST /api/import 请求体中

### Requirement: User can submit import request

The system SHALL send import request to POST /api/import with form data including passwords and receive task_id.

#### Scenario: Successful form submission
- **WHEN** user clicks "开始导入" button with all fields filled
- **THEN** system sends POST request with year, month, mode, balances, and passwords
- **AND** system receives task_id in response
- **AND** system disables form and shows progress log area

#### Scenario: Form validation failure
- **WHEN** user clicks "开始导入" with empty balance fields
- **THEN** system displays validation error "请填写所有账户余额"

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

### Requirement: User can see real-time progress log

The system SHALL display a scrollable log area showing import progress messages received via WebSocket.

#### Scenario: Progress messages displayed in order
- **WHEN** system receives progress message from WebSocket
- **THEN** system appends message to log area with icon and text
- **AND** system scrolls log to bottom automatically

#### Scenario: Step indicators show progress
- **WHEN** system receives progress message with step number
- **THEN** system displays "[X/7]" prefix showing current step out of 7 total

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

### Requirement: User can see final result

The system SHALL display success or error summary after import completes.

#### Scenario: Import success summary
- **WHEN** all 7 steps complete successfully
- **THEN** system displays green success banner with summary
- **AND** system shows "导入成功" message
- **AND** system shows file count and transaction count if available

#### Scenario: Import error summary
- **WHEN** any step fails with error
- **THEN** system displays red error banner with error message
- **AND** system shows which step failed
- **AND** system suggests mitigation (e.g., "请选择强制覆盖模式")

### Requirement: User can reset form

The system SHALL provide a "重置" button to clear form and log area.

#### Scenario: Reset button clears form
- **WHEN** user clicks "重置" button
- **THEN** system clears all balance input fields
- **AND** system resets mode to default (normal)
- **AND** system clears progress log area
- **AND** system re-enables form for new submission

### Requirement: UI uses Tailwind CSS styling

The system SHALL apply Tailwind CSS classes for modern, responsive UI appearance.

#### Scenario: Form elements styled consistently
- **WHEN** page renders
- **THEN** buttons, inputs, and containers use Tailwind utility classes
- **AND** UI appears modern with proper spacing and colors

#### Scenario: UI responsive on different screen sizes
- **WHEN** user resizes browser window
- **THEN** layout adjusts appropriately using Tailwind responsive classes
