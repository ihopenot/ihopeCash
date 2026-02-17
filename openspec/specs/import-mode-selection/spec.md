## ADDED Requirements

### Requirement: System supports three import modes

The system SHALL provide three import modes: normal (通常), force (强制覆盖), and append (追加).

#### Scenario: Normal mode with non-existent directory
- **WHEN** user selects normal mode
- **AND** submits import for year/month directory that does not exist
- **THEN** system creates new directory structure and imports bills

#### Scenario: Normal mode with existing directory
- **WHEN** user selects normal mode
- **AND** submits import for year/month directory that already exists
- **THEN** system returns error "目录已存在" and stops import

#### Scenario: Force mode with existing directory
- **WHEN** user selects force mode
- **AND** submits import for year/month directory that already exists
- **THEN** system deletes existing directory completely
- **AND** system creates new directory structure and imports bills

#### Scenario: Force mode with non-existent directory
- **WHEN** user selects force mode
- **AND** submits import for year/month directory that does not exist
- **THEN** system creates new directory structure and imports bills (same as normal)

#### Scenario: Append mode with existing directory
- **WHEN** user selects append mode
- **AND** submits import for year/month directory that already exists
- **THEN** system creates new bean file named "append_<timestamp>.bean"
- **AND** system adds include statement to _.bean file
- **AND** system extracts transactions to append file

#### Scenario: Append mode with non-existent directory
- **WHEN** user selects append mode
- **AND** submits import for year/month directory that does not exist
- **THEN** system returns error "目录不存在，无法追加" and stops import

### Requirement: Mode descriptions displayed to user

The system SHALL display explanatory text for each import mode in the UI.

#### Scenario: Normal mode description shown
- **WHEN** normal mode radio button is visible
- **THEN** system displays "目录已存在时报错"

#### Scenario: Force mode description shown
- **WHEN** force mode radio button is visible
- **THEN** system displays "删除已有目录并重新创建"

#### Scenario: Append mode description shown
- **WHEN** append mode radio button is visible
- **THEN** system displays "向已有月份添加新交易"

### Requirement: All modes execute full import workflow

The system SHALL execute git_commit, download, identify, extract, balance, and archive steps for all three modes.

#### Scenario: Normal mode executes 7 steps
- **WHEN** user submits normal mode import
- **THEN** system executes all 7 steps: git_commit, download, identify, create_dir, extract, balance, archive

#### Scenario: Force mode executes 7 steps
- **WHEN** user submits force mode import
- **THEN** system executes all 7 steps: git_commit, download, identify, create_dir (with delete), extract, balance, archive

#### Scenario: Append mode executes 7 steps
- **WHEN** user submits append mode import
- **THEN** system executes all 7 steps: git_commit, download, identify, append_file, extract, balance, archive

### Requirement: Append mode generates timestamped filenames

The system SHALL generate unique filenames for append mode using timestamp format "append_YYYYMMDD_HHMMSS.bean".

#### Scenario: Append file created with timestamp
- **WHEN** user submits append mode import at 2025-02-10 14:30:22
- **THEN** system creates file "append_20250210_143022.bean" in month directory

#### Scenario: Multiple appends create different files
- **WHEN** user submits append mode twice for same month
- **THEN** system creates two different append files with different timestamps

### Requirement: Append mode records balance like other modes

The system SHALL record balance assertions for append mode same as normal and force modes.

#### Scenario: Append mode records balance
- **WHEN** user submits append mode with balance values
- **THEN** system writes balance assertions to the month's others.bean file
- **AND** balance format matches other modes
