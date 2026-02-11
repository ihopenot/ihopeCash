## ADDED Requirements

### Requirement: System tracks import progress in 6 steps

The system SHALL divide import workflow into 6 trackable steps: download, identify, create_dir, extract, balance, archive.

#### Scenario: All 6 steps executed in order
- **WHEN** user submits import request
- **THEN** system executes steps in sequence: download → identify → create_dir → extract → balance → archive

#### Scenario: Each step reports start and completion
- **WHEN** system begins a step
- **THEN** system sends progress message with status "running"
- **AND** when step completes successfully, system sends progress message with status "success"

#### Scenario: Step failure stops workflow
- **WHEN** any step fails with error
- **THEN** system sends progress message with status "error"
- **AND** system stops execution and does not proceed to next step

### Requirement: Progress messages sent via WebSocket

The system SHALL push progress messages to client via WebSocket connection at /ws/progress.

#### Scenario: WebSocket connection established
- **WHEN** client connects to /ws/progress with valid token
- **THEN** system accepts connection and keeps it open for message push

#### Scenario: Progress message pushed to client
- **WHEN** import step changes state (running/success/error)
- **THEN** system immediately sends JSON message to connected WebSocket client

### Requirement: Progress message format is standardized

The system SHALL send progress messages as JSON with fields: task_id, step, total, step_name, status, message, details.

#### Scenario: Running step message structure
- **WHEN** system starts step 1 (download)
- **THEN** message contains: `{"task_id": "...", "step": 1, "total": 6, "step_name": "download", "status": "running", "message": "正在下载邮件账单..."}`

#### Scenario: Success step message structure
- **WHEN** system completes step 2 (identify)
- **THEN** message contains: `{"task_id": "...", "step": 2, "total": 6, "step_name": "identify", "status": "success", "message": "文件识别完成", "details": {...}}`

#### Scenario: Error step message structure
- **WHEN** system fails at step 3 (create_dir)
- **THEN** message contains: `{"task_id": "...", "step": 3, "total": 6, "step_name": "create_dir", "status": "error", "message": "目录 data/2025/2 已存在"}`

### Requirement: Progress callback mechanism in BillManager

The system SHALL extend BillManager class with progress_callback parameter and passwords parameter in import methods.

#### Scenario: Callback invoked at each step
- **WHEN** BillManager executes import_month_with_progress()
- **THEN** callback function is called before and after each of 6 steps

#### Scenario: Callback receives progress dict
- **WHEN** callback is invoked
- **THEN** callback receives dict with step, total, step_name, status, message, details fields

#### Scenario: Passwords passed to import method
- **WHEN** TaskManager creates import task with passwords parameter
- **THEN** passwords list is passed through to BillManager.import_month_with_progress()
- **AND** BillManager uses the provided passwords for file decryption instead of reading from config

### Requirement: Step details provide additional context

The system SHALL include optional details field with step-specific information.

#### Scenario: Download step includes file count
- **WHEN** download step completes successfully
- **THEN** details field contains: `{"files_count": 15}`

#### Scenario: Identify step includes file breakdown
- **WHEN** identify step completes successfully
- **THEN** details field contains: `{"alipay": 5, "wechat": 8, "boc": 2}`

#### Scenario: Extract step includes transaction count
- **WHEN** extract step completes successfully
- **THEN** details field contains: `{"transactions_count": 287}`

### Requirement: WebSocket handles disconnection gracefully

The system SHALL handle WebSocket disconnection and allow client reconnection.

#### Scenario: Client disconnects during import
- **WHEN** WebSocket connection drops during import
- **THEN** system continues import process without interruption
- **AND** client can reconnect and resume receiving messages

#### Scenario: Client reconnects after disconnection
- **WHEN** client reconnects to WebSocket
- **THEN** system accepts new connection
- **AND** client can query task status via HTTP API if needed

### Requirement: Task ID uniquely identifies import session

The system SHALL generate unique task_id for each import request and include it in all progress messages.

#### Scenario: Task ID returned on import start
- **WHEN** user submits POST /api/import
- **THEN** system returns unique task_id in response

#### Scenario: Task ID included in all progress messages
- **WHEN** system sends any progress message for an import
- **THEN** message includes the task_id for that import session
