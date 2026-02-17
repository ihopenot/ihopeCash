## MODIFIED Requirements

### Requirement: Step 10 余额账户配置
引导页 SHALL 在第十步提供余额账户列表配置。

#### Scenario: 余额账户使用下拉选择
- **WHEN** 用户进入 Step 10
- **THEN** 提供下拉选择组件添加余额账户
- **THEN** 下拉列表包含现有账户、引导中临时新增的账户和卡号映射中配置的账户
- **THEN** 可以添加多个余额账户，每个旁边有删除按钮

### Requirement: 账户下拉选择组件
引导页所有账户字段 SHALL 使用统一的下拉选择组件，不允许手动输入。

#### Scenario: 下拉列表数据源
- **WHEN** 渲染账户下拉组件
- **THEN** 下拉列表包含服务端现有账户（GET /api/ledger/accounts）和引导中临时新增的账户
- **THEN** 下拉列表还包含从 `setupConfig.card_accounts` 中拼出的完整账户名
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
