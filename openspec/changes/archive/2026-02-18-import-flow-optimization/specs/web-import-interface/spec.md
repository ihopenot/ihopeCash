## MODIFIED Requirements

### Requirement: User can fill import form

系统 SHALL 在"导入账单"区域提供表单，包含年份、月份、导入模式和账户余额输入。附件密码输入已移至"获取原文件"区域。

#### Scenario: User selects year and month
- **WHEN** user selects year from dropdown (e.g., 2025)
- **AND** user selects month from dropdown (e.g., 02)
- **THEN** system updates form state with selected values

#### Scenario: User selects import mode
- **WHEN** user selects one of three radio options (通常/强制覆盖/追加)
- **THEN** system displays mode description below radio buttons

#### Scenario: User enters balance amounts
- **WHEN** user types balance amount in each account input field
- **THEN** system validates input is numeric format

### Requirement: 用户可以在导入表单中填写附件密码

系统 SHALL 在"获取原文件"区域的邮件下载子区域中提供 passwords 动态列表输入，而非在导入表单中。

#### Scenario: passwords 输入区域显示
- **WHEN** 已认证用户打开主页面
- **THEN** 在"获取原文件"区域的"邮件下载"子区域中显示附件密码输入
- **AND** 包含动态增减的密码输入框列表

#### Scenario: 添加密码
- **WHEN** 用户点击"添加密码"按钮
- **THEN** 系统在列表末尾新增一个 password 类型的输入框

#### Scenario: 删除密码
- **WHEN** 用户点击某行密码旁的删除按钮
- **THEN** 系统移除该行密码输入框

#### Scenario: passwords 随邮件下载请求提交
- **WHEN** 用户填写了密码并点击"从邮件下载"
- **THEN** 系统将 passwords 列表包含在 `POST /api/rawdata/download-email` 请求体中

### Requirement: User can submit import request

系统 SHALL 在用户点击"开始导入"时发送导入请求到 `POST /api/import`，请求中不再包含 passwords 字段。

#### Scenario: Successful form submission
- **WHEN** user clicks "开始导入" button with all fields filled
- **THEN** system sends POST request with year, month, mode, balances（不含 passwords）
- **AND** system receives task_id in response
- **AND** system disables form and shows progress log area

#### Scenario: Form validation failure
- **WHEN** user clicks "开始导入" with empty balance fields
- **THEN** system displays validation error "请填写所有账户余额"

#### Scenario: rawdata 中无文件时阻止导入
- **WHEN** 用户点击"开始导入"
- **AND** 原文件列表为空
- **THEN** 系统提示"请先获取原文件"，不发送请求

### Requirement: 导入前必须检查未归档变更

系统 SHALL 在用户点击"开始导入"时检查 git 工作区状态，有未归档变更时提示用户。

#### Scenario: 有未归档变更时弹窗提示
- **WHEN** 用户点击"开始导入"
- **AND** `GET /api/ledger-status` 返回工作区非 clean
- **THEN** 系统弹出对话框"有未归档的变更，是否先归档？"
- **AND** 提供"先归档再导入"和"取消"两个按钮

#### Scenario: 用户选择先归档
- **WHEN** 用户在弹窗中点击"先归档再导入"
- **THEN** 系统弹出归档对话框（填写提交说明）
- **AND** 归档完成后自动继续执行导入

#### Scenario: 用户选择取消
- **WHEN** 用户在弹窗中点击"取消"
- **THEN** 系统不执行任何操作

#### Scenario: 无未归档变更时直接导入
- **WHEN** 用户点击"开始导入"
- **AND** 工作区为 clean
- **THEN** 系统直接执行导入

### Requirement: 导入界面必须包含账本状态栏

系统 SHALL 在导入界面导航栏下方展示账本状态栏卡片，展示当前账期或已同步状态。

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

### Requirement: User can see real-time progress log

系统 SHALL 在页面底部提供可滚动的执行日志区域，显示所有操作的进度消息。邮件下载、导入、归档三个操作共用此区域。

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

### Requirement: User can reset form

系统 SHALL 提供"重置"按钮来清空表单和日志区域。

#### Scenario: Reset button clears form
- **WHEN** user clicks "重置" button
- **THEN** system clears all balance input fields
- **AND** system resets mode to default (通常)
- **AND** system clears progress log area
- **AND** system re-enables form for new submission

### Requirement: 页面布局为三区域单页结构

系统 SHALL 将导入页面组织为三个区域：获取原文件、导入账单、归档，外加共用的执行日志区域。

#### Scenario: 页面显示三个功能区域
- **WHEN** 已认证用户打开导入页面
- **THEN** 页面从上到下依次展示：账本状态栏、获取原文件区域、导入账单区域、归档区域、执行日志区域

#### Scenario: 各区域独立操作
- **WHEN** 用户在任一区域执行操作
- **THEN** 其他区域不受影响（除执行日志共用外）

### Requirement: 页面引导文字使用中文

系统 SHALL 在页面所有引导文字、提示、按钮文案中使用中文，避免英文术语。

#### Scenario: 按钮和标签使用中文
- **WHEN** 页面渲染
- **THEN** 所有按钮文案为中文（如"从邮件下载"、"选择文件"、"开始导入"、"归档当前修改"）
- **AND** 所有区域标题为中文（如"获取原文件"、"导入账单"、"归档"）
- **AND** 所有提示信息为中文

### Requirement: UI uses Tailwind CSS styling

The system SHALL apply Tailwind CSS classes for modern, responsive UI appearance.

#### Scenario: Form elements styled consistently
- **WHEN** page renders
- **THEN** buttons, inputs, and containers use Tailwind utility classes
- **AND** UI appears modern with proper spacing and colors

#### Scenario: UI responsive on different screen sizes
- **WHEN** user resizes browser window
- **THEN** layout adjusts appropriately using Tailwind responsive classes

## REMOVED Requirements

### Requirement: 用户可以在导入界面撤销账本变更
**Reason**: 撤销功能移至 ledger-status-bar spec 中统一管理，包含新的选择性撤销逻辑
**Migration**: 参见 ledger-status-bar 的 MODIFIED Requirements
