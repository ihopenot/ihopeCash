## ADDED Requirements

### Requirement: 引导页 HTML 文件
系统 SHALL 提供 `web/static/setup.html`，包含 11 步引导流程的单页应用。

#### Scenario: 引导页包含所有步骤
- **WHEN** 用户访问 /setup
- **THEN** 页面包含以下步骤：Step 1 邮箱配置、Step 2 通用账户、Step 3 支付宝配置、Step 4 微信配置、Step 5 清华饭卡、Step 6 HSBC HK、Step 7 交易摘要过滤、Step 8 卡号账户映射、Step 9 交易匹配规则、Step 10 余额账户、Step 11 确认页

#### Scenario: 步骤导航
- **WHEN** 用户在任意步骤
- **THEN** 页面显示"上一步"和"下一步"按钮（第一步无"上一步"，最后一步为"确认并完成配置"）
- **THEN** 页面顶部显示步骤进度指示器

### Requirement: Step 1 邮箱配置
引导页 SHALL 在第一步提供邮箱 IMAP 配置表单。

#### Scenario: 邮箱表单字段
- **WHEN** 用户进入 Step 1
- **THEN** 表单包含 IMAP 服务器、端口、用户名、密码、邮箱文件夹五个输入框
- **THEN** 各字段使用默认值预填（host: imap.qq.com, port: 993, mailbox: Bills）

### Requirement: Step 2 通用账户配置
引导页 SHALL 在第二步提供默认支出和默认收入账户的配置。

#### Scenario: 通用账户使用下拉选择
- **WHEN** 用户进入 Step 2
- **THEN** "默认支出账户"和"默认收入账户"均为下拉选择组件
- **THEN** 下拉列表包含现有账户和引导中临时新增的账户
- **THEN** 每个下拉旁提供"新增账户"按钮

### Requirement: Step 3-5 导入器配置
引导页 SHALL 在 Step 3（支付宝）、Step 4（微信）、Step 5（清华饭卡）分别提供对应导入器的账户配置。

#### Scenario: 支付宝配置字段
- **WHEN** 用户进入 Step 3
- **THEN** 表单包含 account、huabei_account、douyin_monthly_payment_account、yuebao_account、red_packet_income_account、red_packet_expense_account 六个下拉选择字段
- **THEN** 每个字段旁提供"新增账户"按钮

#### Scenario: 微信配置字段
- **WHEN** 用户进入 Step 4
- **THEN** 表单包含 account、lingqiantong_account、red_packet_income_account、red_packet_expense_account、family_card_expense_account、group_payment_expense_account、group_payment_income_account、transfer_expense_account、transfer_income_account 九个下拉选择字段

#### Scenario: 清华饭卡配置字段
- **WHEN** 用户进入 Step 5
- **THEN** 表单包含 account 一个下拉选择字段

### Requirement: Step 6 HSBC HK 配置拆分
引导页 SHALL 将 HSBC HK 配置拆分为三条独立配置项展示。

#### Scenario: HSBC HK 三条配置项
- **WHEN** 用户进入 Step 6
- **THEN** 第一条为 use_cnh 开关（checkbox）
- **THEN** 第二条为 One 账户的下拉选择
- **THEN** 第三条为 PULSE 账户的下拉选择
- **THEN** 每个账户下拉旁提供"新增账户"按钮

#### Scenario: HSBC HK 数据合并
- **WHEN** 引导完成提交配置
- **THEN** 前端将三条配置合并为 `hsbc_hk: { use_cnh: bool, account_mapping: { One: <账户>, PULSE: <账户> } }` 格式

### Requirement: Step 7 交易摘要过滤（带默认值）
引导页 SHALL 在第七步提供交易摘要白名单和黑名单配置，并预填默认值。

#### Scenario: 白名单默认值
- **WHEN** 用户进入 Step 7
- **THEN** 白名单预填默认值：["财付通(银联云闪付)"]
- **THEN** 用户可以添加或删除白名单条目

#### Scenario: 黑名单默认值
- **WHEN** 用户进入 Step 7
- **THEN** 黑名单预填默认值：["支付宝", "财付通", "美团支付"]
- **THEN** 用户可以添加或删除黑名单条目

### Requirement: Step 8 卡号账户映射三栏设计
引导页 SHALL 在第八步提供三栏式卡号账户映射配置。

#### Scenario: 三栏输入
- **WHEN** 用户进入 Step 8
- **THEN** 每条映射包含三栏：分类下拉（Assets/Liabilities/Income/Expenses/Equity）、自定义中间名称输入框、4位字符串输入框

#### Scenario: 自动补冒号
- **WHEN** 用户输入中间名称 "BOC:Card"（末尾无冒号）
- **THEN** 系统自动在拼接时补上冒号，预览显示 "Assets:BOC:Card:1234"

#### Scenario: 实时预览
- **WHEN** 用户修改三栏中任一字段
- **THEN** 预览区域实时显示拼接后的完整账户名

#### Scenario: 4位字符串校验
- **WHEN** 用户输入的字符串长度不为4
- **THEN** 显示错误提示"必须为4位字符"
- **WHEN** 用户输入的字符串包含非数字非大写字母的字符
- **THEN** 显示错误提示"只允许数字和大写字母"

#### Scenario: 中间名称校验
- **WHEN** 用户输入的中间名称中存在以小写字母开头的段
- **THEN** 显示错误提示"每段必须以大写字母或数字开头"

#### Scenario: 完整账户名校验
- **WHEN** 拼接后的完整账户名不符合 Beancount 账户命名规则
- **THEN** 预览区域显示错误标记

#### Scenario: 前端到后端数据转换
- **WHEN** 提交配置
- **THEN** 三栏值 [Assets, BOC:Card, 1234] 转换为 `card_accounts: { Assets: { "BOC:Card:": ["1234"] } }` 嵌套结构

### Requirement: Step 9 交易匹配规则
引导页 SHALL 在第九步提供交易匹配规则配置，默认为空。

#### Scenario: 默认留空
- **WHEN** 用户进入 Step 9
- **THEN** 规则列表为空
- **THEN** 用户可以通过"添加规则"按钮新增规则

#### Scenario: 规则字段
- **WHEN** 用户添加一条规则
- **THEN** 规则包含 payee_keywords、narration_keywords、account（下拉选择）、tags 四个字段

### Requirement: Step 10 余额账户配置
引导页 SHALL 在第十步提供余额账户列表配置。

#### Scenario: 余额账户使用下拉选择
- **WHEN** 用户进入 Step 10
- **THEN** 提供下拉选择组件添加余额账户
- **THEN** 下拉列表包含现有账户和引导中临时新增的账户
- **THEN** 可以添加多个余额账户，每个旁边有删除按钮

### Requirement: Step 11 确认页
引导页 SHALL 在最后一步提供所有配置的汇总确认。

#### Scenario: 汇总展示
- **WHEN** 用户进入 Step 11
- **THEN** 页面分区展示所有步骤的配置摘要
- **THEN** 展示引导过程中将要新增的账户列表
- **THEN** 每个区域提供"修改"按钮

#### Scenario: 修改按钮跳回对应步骤
- **WHEN** 用户点击某区域的"修改"按钮
- **THEN** 页面跳转回该区域对应的步骤
- **THEN** 该步骤保留之前填写的数据

#### Scenario: 确认提交
- **WHEN** 用户点击"确认并完成配置"按钮
- **THEN** 前端将所有临时配置和新增账户通过 POST /api/setup/complete 提交到后端
- **THEN** 成功后页面跳转到首页

### Requirement: 账户下拉选择组件
引导页所有账户字段 SHALL 使用统一的下拉选择组件，不允许手动输入。

#### Scenario: 下拉列表数据源
- **WHEN** 渲染账户下拉组件
- **THEN** 下拉列表包含服务端现有账户（GET /api/ledger/accounts）和引导中临时新增的账户
- **THEN** 不允许用户在下拉框中手动输入

#### Scenario: 内联新增账户
- **WHEN** 用户点击下拉旁的"新增账户"按钮
- **THEN** 弹出内联新增表单（账户类型、路径、货币、备注）
- **THEN** 提交后新账户加入前端 tempAccounts 列表（不调用后端 API）
- **THEN** 新账户自动被选中到当前下拉框

#### Scenario: 临时账户跨步骤可见
- **WHEN** Step 3 中新增了一个临时账户
- **THEN** Step 4、Step 5 等后续步骤的下拉列表中也能看到该账户

#### Scenario: 新增账户去重
- **WHEN** 用户尝试新增一个已在 tempAccounts 或服务端账户中存在的账户
- **THEN** 系统提示该账户已存在，不重复添加

### Requirement: 前端临时状态管理
引导页 SHALL 在前端维护所有配置的临时状态，不在中间步骤调用后端保存。

#### Scenario: 步骤间数据保留
- **WHEN** 用户从 Step 3 跳到 Step 4 再跳回 Step 3
- **THEN** Step 3 的数据保持不变

#### Scenario: 刷新页面丢失数据
- **WHEN** 用户在引导过程中刷新页面
- **THEN** 所有临时数据丢失，引导从头开始

### Requirement: 引导 API - 获取状态
系统 SHALL 提供 GET /api/setup/status 端点，返回引导状态。

#### Scenario: 需要引导
- **WHEN** config.yaml 不存在
- **THEN** GET /api/setup/status 返回 `{ "setup_required": true }`

#### Scenario: 无需引导
- **WHEN** config.yaml 已存在
- **THEN** GET /api/setup/status 返回 `{ "setup_required": false }`

#### Scenario: 无需认证
- **WHEN** 未认证用户请求 GET /api/setup/status
- **THEN** 系统正常返回结果（此端点不需要认证）

### Requirement: 引导 API - 获取默认配置
系统 SHALL 提供 GET /api/setup/defaults 端点，返回引导页使用的默认配置。

#### Scenario: 返回默认配置
- **WHEN** 已认证用户请求 GET /api/setup/defaults
- **THEN** 返回包含所有导入器默认值、交易摘要过滤默认值（白名单 ["财付通(银联云闪付)"]、黑名单 ["支付宝", "财付通", "美团支付"]）的配置

#### Scenario: 需要认证
- **WHEN** 未认证用户请求 GET /api/setup/defaults
- **THEN** 系统返回 401 Unauthorized

### Requirement: 引导 API - 完成配置
系统 SHALL 提供 POST /api/setup/complete 端点，一次性写入所有配置和新增账户。

#### Scenario: 成功完成配置
- **WHEN** 已认证用户提交有效的配置和新增账户列表
- **THEN** 系统写入 config.yaml（不含 system 路径和 web 配置）
- **THEN** 系统将新增账户追加到 accounts.bean（去重，不重复添加已存在的账户）
- **THEN** config.setup_required 设为 False
- **THEN** 返回 `{ "success": true, "message": "配置完成" }`

#### Scenario: 引导已完成时拒绝
- **WHEN** config.setup_required 为 False 时调用 POST /api/setup/complete
- **THEN** 系统返回 403 Forbidden

#### Scenario: 配置校验失败
- **WHEN** 提交的配置中包含不合法的账户名
- **THEN** 系统返回 400 错误，包含具体错误信息

### Requirement: Web 中间件引导拦截
系统 SHALL 在 setup_required 为 True 时，拦截所有非引导路径的请求。

#### Scenario: 引导模式下允许的路径
- **WHEN** setup_required 为 True
- **THEN** 允许访问：/login、/api/auth/login、/setup、/api/setup/*、/static/*
- **THEN** 其他路径返回 302 重定向到 /setup

#### Scenario: 引导完成后引导页不可访问
- **WHEN** setup_required 为 False
- **THEN** 访问 /setup 返回 302 重定向到 /
- **THEN** POST /api/setup/complete 返回 403

#### Scenario: 引导页需要登录
- **WHEN** 未登录用户访问 /setup
- **THEN** 页面检查 localStorage 中的 auth_token
- **THEN** 如果没有 token，重定向到 /login

## ADDED Requirements (XSS Prevention)

### Requirement: 引导页所有动态渲染必须防止 XSS
setup.html 中所有使用 `innerHTML` 拼接用户数据或配置数据的地方 MUST 使用 `escapeHtml()` 函数转义，或改用 DOM API（`createElement` + `textContent`）。

#### Scenario: 账户名称安全渲染
- **WHEN** 系统在引导页渲染账户名称（balance_accounts、账户下拉等）
- **THEN** 账户名称 MUST 通过 `escapeHtml()` 转义后再插入 innerHTML
- **THEN** 或使用 `element.textContent = accountName` 方式渲染

#### Scenario: 配置值安全渲染
- **WHEN** 系统在确认页（Step 11）渲染用户输入的配置值
- **THEN** 所有配置值 MUST 通过 `escapeHtml()` 转义
- **THEN** 防止包含 HTML 标签的值被解析执行

#### Scenario: 密码输入框 value 属性安全设置
- **WHEN** 系统渲染密码输入框的 value 属性
- **THEN** value 值 MUST 通过 `escapeHtml()` 转义，防止引号闭合注入
