## ADDED Requirements

### Requirement: User can view balance accounts from config

The system SHALL fetch and display balance accounts list from config.yaml on page load via GET /api/config endpoint.

#### Scenario: Page loads with balance accounts
- **WHEN** authenticated user opens the main page
- **THEN** system displays input fields for each account in config.balance_accounts

#### Scenario: Default year and month displayed
- **WHEN** authenticated user opens the main page
- **THEN** system pre-fills year and month fields with current or previous month

### Requirement: User can fill import form

The system SHALL provide a form with fields for year, month, import mode, and balance amounts for each account.

#### Scenario: User selects year and month
- **WHEN** user selects year from dropdown (e.g., 2025)
- **AND** user selects month from dropdown (e.g., 02)
- **THEN** system updates form state with selected values

#### Scenario: User selects import mode
- **WHEN** user selects one of three radio options (normal/force/append)
- **THEN** system displays mode description below radio buttons

#### Scenario: User enters balance amounts
- **WHEN** user types balance amount in each account input field
- **THEN** system validates input is numeric format

### Requirement: User can submit import request

The system SHALL send import request to POST /api/import with form data and receive task_id.

#### Scenario: Successful form submission
- **WHEN** user clicks "开始导入" button with all fields filled
- **THEN** system sends POST request with year, month, mode, and balances
- **AND** system receives task_id in response
- **AND** system disables form and shows progress log area

#### Scenario: Form validation failure
- **WHEN** user clicks "开始导入" with empty balance fields
- **THEN** system displays validation error "请填写所有账户余额"

### Requirement: User can see real-time progress log

The system SHALL display a scrollable log area showing import progress messages received via WebSocket.

#### Scenario: Progress messages displayed in order
- **WHEN** system receives progress message from WebSocket
- **THEN** system appends message to log area with icon and text
- **AND** system scrolls log to bottom automatically

#### Scenario: Step indicators show progress
- **WHEN** system receives progress message with step number
- **THEN** system displays "[X/6]" prefix showing current step

#### Scenario: Success messages show checkmark
- **WHEN** system receives message with status "success"
- **THEN** system displays "✓" icon before message text

#### Scenario: Running messages show loading icon
- **WHEN** system receives message with status "running"
- **THEN** system displays "⏳" icon before message text

#### Scenario: Error messages show error icon
- **WHEN** system receives message with status "error"
- **THEN** system displays "❌" icon before message text

### Requirement: User can see final result

The system SHALL display success or error summary after import completes.

#### Scenario: Import success summary
- **WHEN** all 6 steps complete successfully
- **THEN** system displays green success banner with summary
- **AND** system shows "导入成功" message
- **AND** system shows file count and transaction count if available

#### Scenario: Import error summary
- **WHEN** any step fails with error
- **THEN** system displays red error banner with error message
- **AND** system shows which step failed
- **AND** system suggests mitigation (e.g., "请选择强制覆盖模式")

### Requirement: User can reset form

The system SHALL provide a "重置" button to clear form and log area.

#### Scenario: Reset button clears form
- **WHEN** user clicks "重置" button
- **THEN** system clears all balance input fields
- **AND** system resets mode to default (normal)
- **AND** system clears progress log area
- **AND** system re-enables form for new submission

### Requirement: UI uses Tailwind CSS styling

The system SHALL apply Tailwind CSS classes for modern, responsive UI appearance.

#### Scenario: Form elements styled consistently
- **WHEN** page renders
- **THEN** buttons, inputs, and containers use Tailwind utility classes
- **AND** UI appears modern with proper spacing and colors

#### Scenario: UI responsive on different screen sizes
- **WHEN** user resizes browser window
- **THEN** layout adjusts appropriately using Tailwind responsive classes
