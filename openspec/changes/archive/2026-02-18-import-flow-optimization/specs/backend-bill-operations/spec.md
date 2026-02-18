## MODIFIED Requirements

### Requirement: BillManager 必须提供完整月度导入工作流

BillManager 类 SHALL 提供 `import_month_with_progress(year, month, balances, mode, progress_callback)` 方法，执行导入流程。流程 SHALL 从 7 步缩减为 5 步，去掉邮件下载和归档步骤。`passwords` 参数不再需要。

#### Scenario: 完整导入流程成功（5步）
- **WHEN** 调用 `manager.import_month_with_progress("2026", "02", {...}, mode="normal")`
- **THEN** 系统依次执行: 识别文件(Step 1)、创建目录(Step 2)、提取交易(Step 3)、记录余额(Step 4)、写入账期(Step 5)
- **AND** 进度回调的 total 值为 5
- **AND** 返回 `{"success": True, "message": "导入完成", "data": {...}}`

#### Scenario: Step 1 识别文件
- **WHEN** 导入开始
- **THEN** 系统调用 `bean_identify()` 识别 rawdata/ 中的文件
- **AND** 发送进度消息 "正在识别文件类型..."

#### Scenario: Step 2 创建目录（通常/强制模式）
- **WHEN** 模式为 "normal" 或 "force"
- **THEN** 系统调用 `create_month_directory(year, month, force_overwrite)`
- **AND** 提取目标为 `data/{year}/{month}/total.bean`

#### Scenario: Step 2 创建追加文件（追加模式）
- **WHEN** 模式为 "append"
- **AND** 月份目录已存在
- **THEN** 系统创建带时间戳的追加文件 `append_{timestamp}.bean`
- **AND** 在 `_.bean` 中添加 include 语句

#### Scenario: Step 3 提取交易
- **WHEN** 目录/文件创建完成
- **THEN** 系统调用 `bean_extract(extract_target)` 提取交易记录

#### Scenario: Step 4 记录余额断言
- **WHEN** 交易提取完成
- **THEN** 系统调用 `record_balances(year, month, balances)` 记录余额

#### Scenario: Step 5 写入账期
- **WHEN** 余额记录完成
- **THEN** 系统调用 `write_ledger_period(period)` 写入本次账期

#### Scenario: 导入过程中发生错误
- **WHEN** 导入过程中任一步骤失败
- **THEN** 使用 logging 记录完整异常堆栈
- **AND** 发送 error 进度消息
- **AND** 返回 `{"success": False, "message": "<错误信息>", "data": None}`

## ADDED Requirements

### Requirement: BillManager 必须提供独立的归档并提交方法

BillManager 类 SHALL 提供 `archive_with_commit(message, progress_callback)` 方法，执行 bean-file 归档和 git commit。

#### Scenario: 成功归档并提交
- **WHEN** 调用 `manager.archive_with_commit("2026年1月账单")`
- **THEN** 系统依次执行 `bean_archive()`、`git add .`、`git commit -m "2026年1月账单"`
- **AND** 调用 `clear_ledger_period()` 清除账期文件
- **AND** 通过 progress_callback 推送各步骤进度

#### Scenario: 工作区无变更时拒绝归档
- **WHEN** 调用 `archive_with_commit()` 且 git 工作区为 clean
- **THEN** 抛出 RuntimeError，提示无变更需要归档

#### Scenario: bean-file 失败时不执行 git commit
- **WHEN** `bean_archive()` 抛出异常
- **THEN** 系统不执行 git commit
- **AND** 异常向上传播

### Requirement: BillManager 必须提供 bean-identify 结果解析方法

BillManager 类 SHALL 提供 `bean_identify_parsed()` 方法，将 bean-identify 的文本输出解析为结构化数据。

#### Scenario: 成功解析
- **WHEN** 调用 `manager.bean_identify_parsed()`
- **THEN** 返回字典，键为文件名，值为 importer 名称

#### Scenario: 命令失败时返回空字典
- **WHEN** bean-identify 命令失败
- **THEN** 返回空字典 `{}`，不抛出异常

### Requirement: BillManager 必须提供 rawdata 文件清理方法

BillManager 类 SHALL 提供 `clear_rawdata()` 方法，清空 rawdata/ 目录下的所有文件。

#### Scenario: 清空 rawdata 目录
- **WHEN** 调用 `manager.clear_rawdata()`
- **AND** rawdata/ 中有文件
- **THEN** 系统删除 rawdata/ 下的所有文件和子目录
- **AND** rawdata/ 目录本身保留

#### Scenario: rawdata 已为空
- **WHEN** 调用 `manager.clear_rawdata()`
- **AND** rawdata/ 中无文件
- **THEN** 系统正常执行不报错
