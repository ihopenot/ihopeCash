## Requirements

### Requirement: 用户可以查看可编辑配置

系统 SHALL 提供 GET /api/config/full 端点，返回脱敏后的可编辑配置。

#### Scenario: 成功获取可编辑配置
- **WHEN** 已认证用户请求 GET /api/config/full
- **THEN** 系统返回配置 JSON，包含 system.balance_accounts、email、importers、card_accounts、detail_mappings、unknown_expense_account、unknown_income_account 字段

#### Scenario: 敏感字段脱敏返回
- **WHEN** 系统返回配置
- **THEN** email.imap.password 字段值为空字符串

#### Scenario: 不可编辑字段不返回
- **WHEN** 系统返回配置
- **THEN** 返回数据不包含 web 节点、system.data_path、system.rawdata_path、system.archive_path、passwords、pdf_passwords 字段

#### Scenario: 未认证用户被拒绝
- **WHEN** 未认证用户请求 GET /api/config/full
- **THEN** 系统返回 401 Unauthorized

### Requirement: 用户可以保存配置

系统 SHALL 提供 PUT /api/config/full 端点，保存用户提交的配置并热重载。

#### Scenario: 成功保存配置
- **WHEN** 已认证用户提交有效配置到 PUT /api/config/full
- **THEN** 系统将配置写入 config.yaml
- **AND** 系统重新加载配置到内存
- **AND** 系统返回 {"success": true, "message": "配置已保存"}

#### Scenario: 后端强制跳过受保护字段
- **WHEN** 用户提交的配置包含 web、system.data_path、system.rawdata_path、system.archive_path、passwords、pdf_passwords 字段
- **THEN** 系统自动忽略这些字段，保留原配置值

#### Scenario: 敏感字段空值跳过
- **WHEN** 用户提交的 email.imap.password 为空字符串
- **THEN** 系统保留原来的 email.imap.password 值不覆盖

#### Scenario: 敏感字段非空值更新
- **WHEN** 用户提交的 email.imap.password 为非空新值
- **THEN** 系统更新 email.imap.password 为新值

#### Scenario: 未认证用户被拒绝
- **WHEN** 未认证用户提交 PUT /api/config/full
- **THEN** 系统返回 401 Unauthorized

### Requirement: 用户可以修改登录密码

系统 SHALL 提供 POST /api/config/change-password 端点，验证当前密码后修改登录密码。

#### Scenario: 成功修改密码
- **WHEN** 已认证用户提交正确的当前密码和新密码
- **THEN** 系统更新 config.yaml 中的 web.password
- **AND** 系统重新加载配置
- **AND** 系统返回 {"success": true, "message": "密码已修改"}

#### Scenario: 当前密码错误
- **WHEN** 已认证用户提交错误的当前密码
- **THEN** 系统返回 400 错误，消息为 "当前密码错误"

#### Scenario: 新密码为空
- **WHEN** 已认证用户提交空的新密码
- **THEN** 系统返回 400 错误，消息为 "新密码不能为空"

### Requirement: Config 类提供配置编辑方法

Config 类 SHALL 提供 get_editable_config()、update_from_web()、update_web_password() 方法。

#### Scenario: get_editable_config 返回脱敏配置
- **WHEN** 调用 config.get_editable_config()
- **THEN** 返回不包含 web 节点、路径字段、passwords、pdf_passwords 的配置字典
- **AND** email.imap.password 为空字符串

#### Scenario: update_from_web 保护受保护字段
- **WHEN** 调用 config.update_from_web(data)
- **THEN** 系统自动跳过 web、system.data_path、system.rawdata_path、system.archive_path、passwords、pdf_passwords 字段
- **AND** email.imap.password 为空时保留原值
- **AND** 保存到 config.yaml 并重新加载

#### Scenario: update_web_password 更新登录密码
- **WHEN** 调用 config.update_web_password("new_password")
- **THEN** 系统更新 config.yaml 中 web.password 字段并保存

### Requirement: 配置页面提供分 Tab 编辑界面

系统 SHALL 在 /config 路径提供配置编辑页面，含 3 个 Tab。

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

#### Scenario: 保存配置成功反馈
- **WHEN** 用户点击保存按钮且保存成功
- **THEN** 系统显示成功提示消息
