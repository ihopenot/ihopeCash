## MODIFIED Requirements

### Requirement: 配置页面提供分 Tab 编辑界面

系统 SHALL 在 /config 路径提供配置编辑页面，含 4 个 Tab。高级配置 Tab 中 HSBC HK 部分拆分为三条独立配置项，卡号账户映射改为三栏交互式编辑，交易摘要过滤提供默认值。

#### Scenario: 账本 Tab 显示
- **WHEN** 用户切换到"账本"Tab
- **THEN** 系统显示账本基本信息（名称、主货币）编辑区域和账户管理区域（按五大类型分组展示、新增账户表单、关闭账户功能）

#### Scenario: 基础配置 Tab 显示
- **WHEN** 用户切换到"基础配置"Tab
- **THEN** 系统显示 balance_accounts 动态列表和 email.imap 各字段输入框
- **AND** 页面顶部显示警告"由于 Beancount 无法动态修改账户名，账户内有数据的情况下请不要修改账户名"

#### Scenario: 高级配置 Tab - HSBC HK 拆分展示
- **WHEN** 用户切换到"高级配置"Tab
- **THEN** HSBC HK 区域显示三条独立配置项：use_cnh 开关（checkbox）、One 账户输入框、PULSE 账户输入框
- **THEN** 不再使用 JSON textarea 编辑 account_mapping

#### Scenario: 高级配置 Tab - HSBC HK 数据提交
- **WHEN** 用户保存高级配置
- **THEN** 前端将 use_cnh、One 账户、PULSE 账户合并为 `hsbc_hk: { use_cnh: bool, account_mapping: { One: <值>, PULSE: <值> } }` 格式提交

#### Scenario: 高级配置 Tab - 卡号账户映射三栏编辑
- **WHEN** 用户查看卡号账户映射区域
- **THEN** 每条映射显示为三栏：分类下拉（Assets/Liabilities/Income/Expenses/Equity）、自定义中间名称输入框、4位字符串输入框
- **THEN** 不再使用 JSON textarea 编辑 card_accounts

#### Scenario: 高级配置 Tab - 卡号映射实时预览
- **WHEN** 用户修改卡号映射的任一栏
- **THEN** 预览区域实时显示拼接后的完整账户名（自动在中间名称末尾补冒号）
- **THEN** 校验拼接结果是否为合法 Beancount 账户名

#### Scenario: 高级配置 Tab - 卡号映射校验
- **WHEN** 4位字符串长度不为4或包含非法字符（只允许数字和大写字母）
- **THEN** 显示错误提示
- **WHEN** 中间名称中存在以小写字母开头的段
- **THEN** 显示错误提示

#### Scenario: 高级配置 Tab - 卡号映射数据提交
- **WHEN** 用户保存高级配置
- **THEN** 前端将三栏值转换为 `card_accounts: { <分类>: { "<中间名称>:": ["<4位字符>"] } }` 嵌套结构提交

#### Scenario: 高级配置 Tab - 交易摘要过滤默认值
- **WHEN** 白名单或黑名单为空（首次加载默认配置时）
- **THEN** 白名单预填 ["财付通(银联云闪付)"]
- **THEN** 黑名单预填 ["支付宝", "财付通", "美团支付"]

#### Scenario: 修改密码 Tab 显示
- **WHEN** 用户切换到"修改密码"Tab
- **THEN** 系统显示当前密码、新密码、确认新密码三个输入框

#### Scenario: 默认选中账本 Tab
- **WHEN** 用户首次进入配置页面
- **THEN** 系统默认选中并展示"账本"Tab 的内容

#### Scenario: 保存配置成功反馈
- **WHEN** 用户点击保存按钮且保存成功
- **THEN** 系统显示成功提示消息
