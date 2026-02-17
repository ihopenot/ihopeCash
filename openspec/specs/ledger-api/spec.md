## Requirements

### Requirement: 获取账本基本信息 API

系统 SHALL 提供 `GET /api/ledger/info` 端点，返回账本名称和主货币。该端点 MUST 需要 JWT 认证。

#### Scenario: 成功获取账本信息
- **WHEN** 已认证用户请求 `GET /api/ledger/info`
- **THEN** 系统 SHALL 使用 `beancount.loader` 解析 `data/main.bean`，返回 JSON：`{"title": "ihopeCash", "operating_currency": "CNY"}`

#### Scenario: 未认证访问
- **WHEN** 未认证用户请求 `GET /api/ledger/info`
- **THEN** 系统 SHALL 返回 401 状态码

### Requirement: 更新账本基本信息 API

系统 SHALL 提供 `PUT /api/ledger/info` 端点，更新账本名称和主货币。该端点 MUST 需要 JWT 认证。

#### Scenario: 成功更新账本名称
- **WHEN** 已认证用户提交 `PUT /api/ledger/info`，body 为 `{"title": "MyLedger", "operating_currency": "CNY"}`
- **THEN** 系统 SHALL 修改 `data/main.bean` 中对应的 `option "title"` 和 `option "operating_currency"` 行，返回 `{"success": true}`

#### Scenario: 字段为空
- **WHEN** 已认证用户提交 `PUT /api/ledger/info`，body 中 `title` 为空字符串
- **THEN** 系统 SHALL 返回 400 状态码，提示"账本名称不能为空"

### Requirement: 获取账户列表 API

系统 SHALL 提供 `GET /api/ledger/accounts` 端点，返回所有账户信息。该端点 MUST 需要 JWT 认证。

#### Scenario: 成功获取账户列表
- **WHEN** 已认证用户请求 `GET /api/ledger/accounts`
- **THEN** 系统 SHALL 使用 `beancount.loader` 解析账本，返回所有 Open 和 Close entries，格式为 JSON 数组，每个元素包含 `date`（开户日期）、`name`（账户全名）、`currencies`（货币列表，可为空数组）、`comment`（备注，从行尾注释提取）、`status`（"open" 或 "closed"）、`close_date`（关闭日期，仅 closed 状态有值）

#### Scenario: 账户按类型分组
- **WHEN** 返回账户列表
- **THEN** 账户 SHALL 按顶级类型（Assets、Liabilities、Income、Expenses、Equity）分组返回

### Requirement: 新增账户 API

系统 SHALL 提供 `POST /api/ledger/accounts` 端点，在 `data/accounts.bean` 中新增账户。该端点 MUST 需要 JWT 认证。

#### Scenario: 成功新增账户
- **WHEN** 已认证用户提交 `POST /api/ledger/accounts`，body 为 `{"account_type": "Assets", "path": "BoC:Card:1234", "currencies": "CNY", "comment": "中行储蓄卡"}`
- **THEN** 系统 SHALL 在 `data/accounts.bean` 末尾追加 `<当天日期> open Assets:BoC:Card:1234 CNY ; 中行储蓄卡`（日期使用 `datetime.date.today().isoformat()`），返回 `{"success": true}`

#### Scenario: 新增账户货币为空
- **WHEN** 已认证用户提交 `POST /api/ledger/accounts`，body 中 `currencies` 为空字符串
- **THEN** 系统 SHALL 追加不含货币的 open 指令：`<当天日期> open Assets:BoC:Card:1234`（支持任意货币）

#### Scenario: 账户类型无效
- **WHEN** 已认证用户提交 `POST /api/ledger/accounts`，body 中 `account_type` 不在 Assets/Liabilities/Income/Expenses/Equity 中
- **THEN** 系统 SHALL 返回 400 状态码，提示"无效的账户类型"

#### Scenario: 账户路径校验 — 第二级名称以中文开头
- **WHEN** 已认证用户提交 `POST /api/ledger/accounts`，body 中 `path` 为 `中行:Card`
- **THEN** 系统 SHALL 返回 400 状态码，提示"账户路径的第一段必须以大写字母或数字开头"

#### Scenario: 账户路径为空
- **WHEN** 已认证用户提交 `POST /api/ledger/accounts`，body 中 `path` 为空
- **THEN** 系统 SHALL 返回 400 状态码，提示"账户路径不能为空"

#### Scenario: 账户已存在
- **WHEN** 已认证用户提交的账户全名（`account_type:path`）已在账本中存在
- **THEN** 系统 SHALL 返回 400 状态码，提示"账户已存在"

### Requirement: 关闭账户 API

系统 SHALL 提供 `POST /api/ledger/accounts/close` 端点，在 `data/accounts.bean` 中追加 close 指令。该端点 MUST 需要 JWT 认证。

#### Scenario: 成功关闭账户
- **WHEN** 已认证用户提交 `POST /api/ledger/accounts/close`，body 为 `{"account_name": "Assets:BoC:Card:1234", "date": "2026-02-14"}`
- **THEN** 系统 SHALL 在 `data/accounts.bean` 末尾追加 `2026-02-14 close Assets:BoC:Card:1234`，返回 `{"success": true}`

#### Scenario: 关闭日期默认为当天
- **WHEN** 已认证用户提交 `POST /api/ledger/accounts/close`，body 中 `date` 为空或未提供
- **THEN** 系统 SHALL 使用当天日期作为关闭日期

#### Scenario: 账户不存在
- **WHEN** 已认证用户提交的 `account_name` 在账本中不存在
- **THEN** 系统 SHALL 返回 400 状态码，提示"账户不存在"

#### Scenario: 账户已关闭
- **WHEN** 已认证用户提交的 `account_name` 已有 close 记录
- **THEN** 系统 SHALL 返回 400 状态码，提示"账户已关闭"
