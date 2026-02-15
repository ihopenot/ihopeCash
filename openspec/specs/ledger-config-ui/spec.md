## Requirements

### Requirement: 配置页面新增"账本"Tab

配置页面（`/config`）SHALL 在现有 Tab 栏最前面新增"账本"Tab。Tab 顺序 SHALL 为：账本、基础配置、高级配置、修改密码。页面加载时 SHALL 默认选中"账本"Tab。

#### Scenario: Tab 显示顺序
- **WHEN** 用户访问 `/config` 页面
- **THEN** Tab 栏 SHALL 按顺序显示：账本、基础配置、高级配置、修改密码

#### Scenario: 默认选中
- **WHEN** 用户首次进入配置页面
- **THEN** SHALL 默认展示"账本"Tab 的内容

### Requirement: 账本基本信息编辑

"账本"Tab 内 SHALL 包含"基本信息"区域，展示账本名称和主货币，支持编辑和保存。

#### Scenario: 展示账本基本信息
- **WHEN** 用户切换到"账本"Tab
- **THEN** 系统 SHALL 调用 `GET /api/ledger/info`，在表单中展示当前的账本名称和主货币

#### Scenario: 保存基本信息
- **WHEN** 用户修改账本名称或主货币后点击"保存基本信息"按钮
- **THEN** 系统 SHALL 调用 `PUT /api/ledger/info` 提交修改，成功后显示提示消息

### Requirement: 账户分组展示

"账本"Tab 内 SHALL 包含"账户管理"区域，按五大类型分组展示所有账户。

#### Scenario: 账户按类型分组
- **WHEN** 用户查看账户管理区域
- **THEN** 系统 SHALL 将账户按 Assets（资产）、Liabilities（负债）、Income（收入）、Expenses（支出）、Equity（权益）五个分组展示，每个分组显示分组名称（中英文）和账户数量

#### Scenario: 分组可折叠
- **WHEN** 用户点击分组标题
- **THEN** 该分组 SHALL 切换展开/折叠状态

#### Scenario: 账户信息展示
- **WHEN** 分组展开
- **THEN** 每个账户行 SHALL 展示账户全名、货币、备注，以及操作按钮

#### Scenario: 已关闭账户展示
- **WHEN** 账户状态为 closed
- **THEN** 账户行 SHALL 以灰色样式和删除线展示，不显示"关闭"按钮

#### Scenario: 开放账户展示
- **WHEN** 账户状态为 open
- **THEN** 账户行 SHALL 显示"关闭"按钮

### Requirement: 新增账户表单

"账户管理"区域顶部 SHALL 包含结构化的新增账户表单。

#### Scenario: 表单结构
- **WHEN** 用户查看新增账户表单
- **THEN** 表单 SHALL 包含：账户类型下拉框（Assets/Liabilities/Income/Expenses/Equity，显示中文标签）、账户路径输入框、货币输入框（默认留空）、备注输入框、"添加账户"按钮

#### Scenario: 货币留空提示
- **WHEN** 用户查看货币输入框
- **THEN** 输入框 SHALL 显示 placeholder 提示"留空支持所有货币"

#### Scenario: 实时预览
- **WHEN** 用户在表单中输入内容
- **THEN** 表单下方 SHALL 实时展示最终的 beancount 语句预览，格式如 `1999-01-01 open Assets:BoC:Card CNY ; 备注`

#### Scenario: 提交新增账户
- **WHEN** 用户填写表单后点击"添加账户"按钮
- **THEN** 系统 SHALL 调用 `POST /api/ledger/accounts`，成功后刷新账户列表并清空表单

### Requirement: 前端账户路径校验

新增账户表单 SHALL 对账户路径进行前端实时校验。

#### Scenario: 第二级名称以字母开头
- **WHEN** 用户输入路径为 `BoC:Card:中行`
- **THEN** 校验 SHALL 通过（第二级 `BoC` 以字母开头）

#### Scenario: 第二级名称以数字开头
- **WHEN** 用户输入路径为 `123Bank:Card`
- **THEN** 校验 SHALL 通过（第二级 `123Bank` 以数字开头）

#### Scenario: 第二级名称以中文开头
- **WHEN** 用户输入路径为 `中行:Card`
- **THEN** 校验 SHALL 不通过，显示错误提示"第一段名称必须以英文字母或数字开头"

#### Scenario: 路径为空
- **WHEN** 用户未输入路径就点击"添加账户"
- **THEN** 校验 SHALL 不通过，显示错误提示

#### Scenario: 路径格式异常
- **WHEN** 用户输入路径以 `:` 开头或结尾，或包含连续 `::`
- **THEN** 校验 SHALL 不通过，显示错误提示"路径格式不正确"

### Requirement: 关闭账户交互

用户点击账户行的"关闭"按钮后 SHALL 弹出确认对话框。

#### Scenario: 弹出确认对话框
- **WHEN** 用户点击某账户的"关闭"按钮
- **THEN** SHALL 弹出确认对话框，显示账户名称、日期输入框（默认当天日期）、警告提示（关闭后不可再记录新交易，且余额必须为零）、"取消"和"确认关闭"按钮

#### Scenario: 确认关闭
- **WHEN** 用户在对话框中点击"确认关闭"
- **THEN** 系统 SHALL 调用 `POST /api/ledger/accounts/close`，成功后刷新账户列表并关闭对话框

#### Scenario: 取消关闭
- **WHEN** 用户在对话框中点击"取消"
- **THEN** 对话框 SHALL 关闭，不执行任何操作

### Requirement: 顶部导航栏保持不变

配置页面和其他页面的顶部导航栏 SHALL 保持现有结构：导入、配置、账本（指向 Fava 的外部链接）。

#### Scenario: 导航栏链接
- **WHEN** 用户查看顶部导航栏
- **THEN** SHALL 显示"导入"（链接到 `/`）、"配置"（链接到 `/config`）、"账本"（链接到 `/fava/`，新窗口打开）
