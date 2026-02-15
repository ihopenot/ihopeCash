## MODIFIED Requirements

### Requirement: 配置页面提供分 Tab 编辑界面

系统 SHALL 在 /config 路径提供配置编辑页面，含 4 个 Tab。

#### Scenario: 账本 Tab 显示
- **WHEN** 用户切换到"账本"Tab
- **THEN** 系统显示账本基本信息（名称、主货币）编辑区域和账户管理区域（按五大类型分组展示、新增账户表单、关闭账户功能）

#### Scenario: 基础配置 Tab 显示
- **WHEN** 用户切换到"基础配置"Tab
- **THEN** 系统显示 balance_accounts 动态列表和 email.imap 各字段输入框
- **AND** 页面顶部显示警告"由于 Beancount 无法动态修改账户名，账户内有数据的情况下请不要修改账户名"

#### Scenario: 高级配置 Tab 显示
- **WHEN** 用户切换到"高级配置"Tab
- **THEN** 系统显示 importers 各分组、card_accounts 键值对、detail_mappings 列表、unknown_expense_account、unknown_income_account 等字段

#### Scenario: 修改密码 Tab 显示
- **WHEN** 用户切换到"修改密码"Tab
- **THEN** 系统显示当前密码、新密码、确认新密码三个输入框

#### Scenario: 默认选中账本 Tab
- **WHEN** 用户首次进入配置页面
- **THEN** 系统默认选中并展示"账本"Tab 的内容

#### Scenario: 保存配置成功反馈
- **WHEN** 用户点击保存按钮且保存成功
- **THEN** 系统显示成功提示消息
