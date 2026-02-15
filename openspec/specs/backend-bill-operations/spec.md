## ADDED Requirements

### Requirement: BillManager 必须提供邮件账单下载功能
BillManager 类 SHALL 提供 `download_bills()` 方法,调用 mail.py 的 DownloadFiles 函数下载邮件账单。

#### Scenario: 成功下载账单
- **WHEN** 调用 `manager.download_bills()`
- **THEN** 系统调用 mail.DownloadFiles() 下载账单到 rawdata 目录

#### Scenario: 下载失败时抛出异常
- **WHEN** 邮件下载过程发生错误
- **THEN** 系统抛出异常并包含错误信息

### Requirement: BillManager 必须封装 bean-identify 命令
BillManager 类 SHALL 提供 `bean_identify()` 方法,执行 bean-identify 命令识别文件类型。

#### Scenario: 成功识别文件
- **WHEN** 调用 `manager.bean_identify()`
- **THEN** 系统执行 bean-identify 命令并返回输出

#### Scenario: 识别失败时抛出异常
- **WHEN** bean-identify 命令返回非零退出码
- **THEN** 系统抛出异常并包含错误信息

### Requirement: BillManager 必须封装 bean-extract 命令
BillManager 类 SHALL 提供 `bean_extract(output_file)` 方法,提取交易记录到指定文件。

#### Scenario: 成功提取交易到文件
- **WHEN** 调用 `manager.bean_extract("data/2024/12/total.bean")`
- **THEN** 系统执行 bean-extract 命令提取交易到指定文件
- **THEN** 返回命令输出

#### Scenario: 提取失败时抛出异常
- **WHEN** bean-extract 命令返回非零退出码
- **THEN** 系统抛出异常并包含错误信息

### Requirement: BillManager 必须封装 bean-file 归档命令
BillManager 类 SHALL 提供 `bean_archive()` 方法,执行 bean-file 命令归档原始文件。

#### Scenario: 成功归档文件
- **WHEN** 调用 `manager.bean_archive()`
- **THEN** 系统执行 bean-file 命令将 rawdata 文件归档到 archive 目录

#### Scenario: 归档失败时抛出异常
- **WHEN** bean-file 命令返回非零退出码
- **THEN** 系统抛出异常并包含错误信息

### Requirement: BillManager 必须管理年份目录结构
BillManager 类 SHALL 提供 `ensure_year_directory(year)` 方法,确保年份目录存在并正确配置。

#### Scenario: 创建新年份目录
- **WHEN** 调用 `manager.ensure_year_directory("2024")` 且目录不存在
- **THEN** 系统创建 data/2024 目录
- **THEN** 创建 data/2024/_.bean 文件
- **THEN** 在 `data/main.bean` 中添加 `include "2024/_.bean"` 语句（路径相对于 data 目录，不含 `data/` 前缀）

#### Scenario: 年份目录已存在
- **WHEN** 调用 `manager.ensure_year_directory("2024")` 且目录已存在
- **THEN** 系统不重复创建,直接返回目录路径

### Requirement: BillManager 必须检查月份目录是否存在
BillManager 类 SHALL 提供 `month_directory_exists(year, month)` 方法,检查月份目录是否存在。

#### Scenario: 月份目录存在
- **WHEN** 调用 `manager.month_directory_exists("2024", "12")` 且目录存在
- **THEN** 返回 True

#### Scenario: 月份目录不存在
- **WHEN** 调用 `manager.month_directory_exists("2024", "12")` 且目录不存在
- **THEN** 返回 False

### Requirement: BillManager 必须创建月份目录结构
BillManager 类 SHALL 提供 `create_month_directory(year, month, remove_if_exists)` 方法,创建月份目录及必要文件。

#### Scenario: 创建新月份目录
- **WHEN** 调用 `manager.create_month_directory("2024", "12", False)` 且目录不存在
- **THEN** 系统创建 data/2024/12 目录
- **THEN** 创建 _.bean, total.bean, others.bean 文件
- **THEN** 在年份 _.bean 中添加 include 语句
- **THEN** 返回月份目录路径

#### Scenario: 月份目录已存在且不覆盖
- **WHEN** 调用 `manager.create_month_directory("2024", "12", False)` 且目录已存在
- **THEN** 系统抛出 FileExistsError 异常

#### Scenario: 月份目录已存在且强制覆盖
- **WHEN** 调用 `manager.create_month_directory("2024", "12", True)` 且目录已存在
- **THEN** 系统删除旧目录并重新创建

### Requirement: BillManager 必须记录余额断言
BillManager 类 SHALL 提供 `record_balances(year, month, balances)` 方法,记录账户余额断言。

#### Scenario: 记录余额到 balance.bean
- **WHEN** 调用 `manager.record_balances("2024", "12", {"Assets:Bank:BOC": "5000.00"})`
- **THEN** 系统在 data/balance.bean 中追加余额断言
- **THEN** 断言日期为下个月1号 (2025-01-01)
- **THEN** 断言格式为 "YYYY-MM-DD balance <account> <amount> CNY"

#### Scenario: balance.bean 不存在时自动创建
- **WHEN** data/balance.bean 文件不存在
- **THEN** 系统创建该文件后再写入余额

### Requirement: BillManager 必须提供完整月度导入工作流
BillManager 类 SHALL 提供 `import_month(year, month, balances, download, force_overwrite)` 方法,执行完整导入流程。

#### Scenario: 完整导入流程成功
- **WHEN** 调用 `manager.import_month("2024", "12", {...}, download=True, force_overwrite=False)`
- **THEN** 系统依次执行: 下载账单、识别文件、创建目录、提取交易、记录余额、归档文件
- **THEN** 返回 `{"success": True, "message": "导入完成", "data": {...}}`

#### Scenario: 导入过程中发生错误
- **WHEN** 导入过程中任一步骤失败
- **THEN** 返回 `{"success": False, "message": "<错误信息>", "data": None}`

#### Scenario: 跳过下载直接导入
- **WHEN** 调用时设置 `download=False`
- **THEN** 系统跳过下载步骤,直接从识别文件开始

### Requirement: BillManager 必须提供追加模式
BillManager 类 SHALL 提供 `append_to_month(folder, name)` 方法,向已存在月份追加交易。

#### Scenario: 成功追加交易
- **WHEN** 调用 `manager.append_to_month("2024/12", "append")`
- **THEN** 系统在 data/2024/12 目录创建 append.bean 文件
- **THEN** 在 _.bean 中添加 include 语句
- **THEN** 提取交易到 append.bean
- **THEN** 归档原始文件
- **THEN** 返回 `{"success": True, "message": "追加完成", "data": {...}}`

#### Scenario: 追加过程失败
- **WHEN** 追加过程中发生错误
- **THEN** 返回 `{"success": False, "message": "<错误信息>", "data": None}`
