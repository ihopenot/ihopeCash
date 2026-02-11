## ADDED Requirements

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

## MODIFIED Requirements

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
