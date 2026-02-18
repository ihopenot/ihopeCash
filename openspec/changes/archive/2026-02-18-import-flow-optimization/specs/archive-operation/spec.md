## ADDED Requirements

### Requirement: 用户可以手动执行归档操作

系统 SHALL 提供 `POST /api/archive` 端点，执行 bean-file 归档和 git commit。该端点 MUST 要求认证。

#### Scenario: 成功归档
- **WHEN** 客户端请求 `POST /api/archive`，请求体为 `{"message": "2026年1月账单"}`
- **THEN** 系统依次执行 `bean_archive()`（bean-file 归档原文件到 archive/）和 `git add . && git commit -m "2026年1月账单"`
- **AND** 调用 `clear_ledger_period()` 清除账期文件
- **AND** 返回 `{"success": true, "message": "归档完成"}`

#### Scenario: 工作区无变更
- **WHEN** 客户端请求归档但 git 工作区为 clean
- **THEN** 返回 `{"success": false, "message": "无变更需要归档"}`

#### Scenario: 归档过程中通过 WebSocket 推送进度
- **WHEN** 归档操作开始执行
- **THEN** 系统通过 WebSocket 向已连接的客户端推送进度消息
- **AND** 推送 bean-file 归档步骤和 git commit 步骤的状态

#### Scenario: bean-file 执行失败
- **WHEN** bean-file 命令执行失败
- **THEN** 系统不执行 git commit
- **AND** 返回 `{"success": false, "message": "<错误信息>"}`

#### Scenario: git commit 失败
- **WHEN** bean-file 成功但 git commit 失败
- **THEN** 返回 `{"success": false, "message": "<错误信息>"}`

#### Scenario: 未提供提交说明
- **WHEN** 请求体中 message 为空字符串
- **THEN** 返回 400 错误，提示"提交说明不能为空"

#### Scenario: 未认证请求
- **WHEN** 未认证客户端请求该端点
- **THEN** 返回 401 状态码

### Requirement: 后端必须提供独立的归档方法

BillManager SHALL 提供 `archive_with_commit(message)` 方法，执行 bean-file 归档并 git commit。

#### Scenario: 成功归档并提交
- **WHEN** 调用 `manager.archive_with_commit("2026年1月账单")`
- **THEN** 系统依次执行 `bean_archive()`、`git add .`、`git commit -m "2026年1月账单"`
- **AND** 调用 `clear_ledger_period()` 清除账期文件

#### Scenario: bean-file 失败时不执行 git commit
- **WHEN** `bean_archive()` 抛出异常
- **THEN** 系统不执行 git commit
- **AND** 异常向上传播

### Requirement: 前端必须提供归档区域

系统 SHALL 在页面底部（导入区域下方、执行日志上方）展示归档区域，包含提交说明输入框和归档按钮。

#### Scenario: 工作区有变更时显示归档区域
- **WHEN** `GET /api/ledger-status` 返回 `is_clean=false`
- **THEN** 归档按钮可点击
- **AND** 提交说明输入框可编辑

#### Scenario: 工作区无变更时禁用归档
- **WHEN** `GET /api/ledger-status` 返回 `is_clean=true`
- **THEN** 归档按钮禁用
- **AND** 显示"无需归档"提示

#### Scenario: 用户点击归档按钮
- **WHEN** 用户填写提交说明并点击"归档当前修改"按钮
- **THEN** 系统调用 `POST /api/archive`
- **AND** 归档过程中按钮禁用
- **AND** 进度显示在执行日志区域
- **AND** 成功后刷新状态栏

#### Scenario: 提交说明为空时阻止提交
- **WHEN** 用户未填写提交说明就点击归档按钮
- **THEN** 系统提示"请填写提交说明"
