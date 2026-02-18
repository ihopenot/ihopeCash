## MODIFIED Requirements

### Requirement: System tracks import progress in 5 steps

系统 SHALL 将导入工作流划分为 5 个可追踪的步骤: identify, create_dir, extract, balance, write_period。

#### Scenario: All 5 steps executed in order
- **WHEN** user submits import request
- **THEN** system executes steps in sequence: identify → create_dir → extract → balance → write_period

#### Scenario: Each step reports start and completion
- **WHEN** system begins a step
- **THEN** system sends progress message with status "running"
- **AND** when step completes successfully, system sends progress message with status "success"

#### Scenario: Step failure stops workflow
- **WHEN** any step fails with error
- **THEN** system sends progress message with status "error"
- **AND** system stops execution and does not proceed to next step

### Requirement: Progress message format is standardized

系统 SHALL 以 JSON 格式发送进度消息，包含 task_id, step, total, step_name, status, message, details 字段。total 值在导入流程中为 5。

#### Scenario: Running step message structure
- **WHEN** system starts step 1 (identify)
- **THEN** message contains: `{"task_id": "...", "step": 1, "total": 5, "step_name": "identify", "status": "running", "message": "正在识别文件类型..."}`

#### Scenario: Success step message structure
- **WHEN** system completes step 1 (identify)
- **THEN** message contains: `{"task_id": "...", "step": 1, "total": 5, "step_name": "identify", "status": "success", "message": "文件识别完成", "details": {"output": "..."}}`

#### Scenario: Error step message structure
- **WHEN** system fails at step 2 (create_dir)
- **THEN** message contains: `{"task_id": "...", "step": 2, "total": 5, "step_name": "create_dir", "status": "error", "message": "目录已存在"}`

## ADDED Requirements

### Requirement: 邮件下载操作通过 WebSocket 推送进度

系统 SHALL 在执行邮件下载时通过 WebSocket 推送进度消息到执行日志区域。

#### Scenario: 下载开始
- **WHEN** 邮件下载开始
- **THEN** 系统推送 `{"step": 1, "total": 1, "step_name": "download", "status": "running", "message": "正在下载邮件账单..."}`

#### Scenario: 下载完成
- **WHEN** 邮件下载完成
- **THEN** 系统推送 `{"step": 1, "total": 1, "step_name": "download", "status": "success", "message": "邮件下载完成，共 N 个文件", "details": {"files_count": N}}`

#### Scenario: 下载失败
- **WHEN** 邮件下载失败
- **THEN** 系统推送 `{"step": 1, "total": 1, "step_name": "download", "status": "error", "message": "<错误信息>"}`

### Requirement: 归档操作通过 WebSocket 推送进度

系统 SHALL 在执行归档时通过 WebSocket 推送进度消息到执行日志区域。

#### Scenario: 归档步骤进度
- **WHEN** 归档操作执行
- **THEN** 系统推送两个步骤的进度：
- **AND** Step 1: bean-file 归档（"正在归档原始文件..." → "归档完成"）
- **AND** Step 2: git commit（"正在提交变更..." → "提交完成"）

#### Scenario: 归档失败
- **WHEN** 归档过程中发生错误
- **THEN** 系统推送 error 状态的进度消息
