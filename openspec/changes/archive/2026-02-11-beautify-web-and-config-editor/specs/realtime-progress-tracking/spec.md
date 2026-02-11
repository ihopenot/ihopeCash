## MODIFIED Requirements

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
