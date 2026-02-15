## ADDED Requirements

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
