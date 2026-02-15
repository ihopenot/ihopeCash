## MODIFIED Requirements

### Requirement: BillManager 必须封装 bean-extract 命令
BillManager 类 SHALL 提供 `bean_extract(output_file)` 方法,提取交易记录到指定文件。该方法 MUST 使用 list 参数形式调用 subprocess（不使用 `shell=True`），以防止命令注入。

#### Scenario: 成功提取交易到文件
- **WHEN** 调用 `manager.bean_extract("data/2024/12/total.bean")`
- **THEN** 系统使用 `subprocess.run(["bean-extract", "beancount_config.py", rawdata_path, "--", output_file])` 执行命令
- **THEN** 返回命令输出

#### Scenario: 提取失败时抛出异常
- **WHEN** bean-extract 命令返回非零退出码
- **THEN** 系统抛出 `RuntimeError` 异常并包含错误信息

### Requirement: BillManager 必须封装 bean-file 归档命令
BillManager 类 SHALL 提供 `bean_archive()` 方法,执行 bean-file 命令归档原始文件。该方法 MUST 使用 list 参数形式调用 subprocess（不使用 `shell=True`），以防止命令注入。

#### Scenario: 成功归档文件
- **WHEN** 调用 `manager.bean_archive()`
- **THEN** 系统使用 `subprocess.run(["bean-file", "-o", archive_path, "beancount_config.py", rawdata_path])` 执行命令

#### Scenario: 归档失败时抛出异常
- **WHEN** bean-file 命令返回非零退出码
- **THEN** 系统抛出 `RuntimeError` 异常并包含错误信息

### Requirement: BillManager 必须提供邮件账单下载功能
BillManager 类 SHALL 提供 `download_bills(passwords=None)` 方法,调用 mail.py 的 DownloadFiles 函数下载邮件账单。默认参数 MUST 使用 `None` 而非可变对象 `[]`。

#### Scenario: 成功下载账单
- **WHEN** 调用 `manager.download_bills()`
- **THEN** 系统调用 mail.DownloadFiles() 下载账单到 rawdata 目录

#### Scenario: 下载失败时抛出异常
- **WHEN** 邮件下载过程发生错误
- **THEN** 系统使用 `raise RuntimeError(...) from e` 抛出异常，保留原始堆栈信息

### Requirement: BillManager 必须管理年份目录结构
BillManager 类 SHALL 提供 `ensure_year_directory(year)` 方法,确保年份目录存在并正确配置。所有文件路径拼接 MUST 使用 `os.path.join()` 而非硬编码 `/` 分隔符。所有文件操作 MUST 使用 `with` 语句管理文件句柄。仅创建空文件时 MUST 使用 `pathlib.Path.touch()`。

#### Scenario: 创建新年份目录
- **WHEN** 调用 `manager.ensure_year_directory("2024")` 且目录不存在
- **THEN** 系统使用 `os.path.join(data_path, year)` 构建路径并创建目录
- **THEN** 使用 `with open(...)` 创建 `_.bean` 文件
- **THEN** 使用 `with open(...)` 读取和追加 `main.bean`
- **THEN** 在 `data/main.bean` 中添加 `include "2024/_.bean"` 语句（路径相对于 data 目录，不含 `data/` 前缀）

#### Scenario: 年份目录已存在
- **WHEN** 调用 `manager.ensure_year_directory("2024")` 且目录已存在
- **THEN** 系统不重复创建,直接返回目录路径

### Requirement: BillManager 必须创建月份目录结构
BillManager 类 SHALL 提供 `create_month_directory(year, month, remove_if_exists)` 方法,创建月份目录及必要文件。所有文件路径拼接 MUST 使用 `os.path.join()`。创建空文件 MUST 使用 `pathlib.Path.touch()`。文件读写 MUST 使用 `with` 语句。

#### Scenario: 创建新月份目录
- **WHEN** 调用 `manager.create_month_directory("2024", "12", False)` 且目录不存在
- **THEN** 系统使用 `os.path.join()` 构建所有路径
- **THEN** 使用 `with open(...)` 创建 `_.bean` 文件
- **THEN** 使用 `Path.touch()` 创建 `total.bean` 和 `others.bean`
- **THEN** 使用 `with open(...)` 读取和追加年份 `_.bean`
- **THEN** 返回月份目录路径

#### Scenario: 月份目录已存在且不覆盖
- **WHEN** 调用 `manager.create_month_directory("2024", "12", False)` 且目录已存在
- **THEN** 系统抛出 FileExistsError 异常

#### Scenario: 月份目录已存在且强制覆盖
- **WHEN** 调用 `manager.create_month_directory("2024", "12", True)` 且目录已存在
- **THEN** 系统删除旧目录并重新创建

### Requirement: BillManager 必须记录余额断言
BillManager 类 SHALL 提供 `record_balances(year, month, balances)` 方法,记录账户余额断言。文件路径 MUST 使用 `os.path.join()`。文件操作 MUST 使用 `with` 语句。

#### Scenario: 记录余额到 balance.bean
- **WHEN** 调用 `manager.record_balances("2024", "12", {"Assets:Bank:BOC": "5000.00"})`
- **THEN** 系统在 data/balance.bean 中追加余额断言
- **THEN** 断言日期为下个月1号 (2025-01-01)
- **THEN** 断言格式为 "YYYY-MM-DD balance <account> <amount> CNY"

#### Scenario: balance.bean 不存在时自动创建
- **WHEN** data/balance.bean 文件不存在
- **THEN** 系统使用 `Path.touch()` 创建该文件后再写入余额

### Requirement: BillManager 必须提供完整月度导入工作流
BillManager 类 SHALL 提供 `import_month_with_progress(year, month, balances, passwords, mode, progress_callback)` 方法,执行完整导入流程。`passwords` 参数 MUST 在所有调用点正确传递。异常处理 MUST 记录日志。

#### Scenario: 完整导入流程成功
- **WHEN** 调用 `manager.import_month_with_progress("2024", "12", {...}, passwords=[...], mode="normal")`
- **THEN** 系统依次执行: 下载账单、识别文件、创建目录、提取交易、记录余额、归档文件
- **THEN** 返回 `{"success": True, "message": "导入完成", "data": {...}}`

#### Scenario: 导入过程中发生错误
- **WHEN** 导入过程中任一步骤失败
- **THEN** 使用 logging 记录完整异常堆栈
- **THEN** 返回 `{"success": False, "message": "<错误信息>", "data": None}`

#### Scenario: 追加模式调用必须传递 passwords 参数
- **WHEN** 以追加模式调用 `import_month_with_progress`
- **THEN** `passwords` 参数 MUST 被正确传递（不可遗漏）

### Requirement: BillManager 必须提供追加模式
BillManager 类 SHALL 提供 `append_to_month(folder, name)` 方法,向已存在月份追加交易。文件路径 MUST 使用 `os.path.join()`。创建空文件 MUST 使用 `Path.touch()`。文件写入 MUST 使用 `with` 语句。

#### Scenario: 成功追加交易
- **WHEN** 调用 `manager.append_to_month("2024/12", "append")`
- **THEN** 系统使用 `Path.touch()` 创建 append.bean 文件
- **THEN** 使用 `with open(...)` 在 `_.bean` 中添加 include 语句
- **THEN** 提取交易到 append.bean
- **THEN** 归档原始文件
- **THEN** 返回 `{"success": True, "message": "追加完成", "data": {...}}`

#### Scenario: 追加过程失败
- **WHEN** 追加过程中发生错误
- **THEN** 使用 logging 记录完整异常堆栈
- **THEN** 返回 `{"success": False, "message": "<错误信息>", "data": None}`

## ADDED Requirements

### Requirement: backend.py 模块级导入必须在文件顶部
所有 `import` 语句（如 `import glob`, `from datetime import datetime`）MUST 放在文件顶部，不允许在函数内部延迟导入。

#### Scenario: 文件顶部包含所有必需导入
- **WHEN** 检查 `backend.py` 文件顶部
- **THEN** `import glob` 和 `from datetime import datetime` 等语句位于模块级别

### Requirement: BillManager 异常类型必须具体化
BillManager 类中所有手动抛出的异常 MUST 使用具体的异常类型（如 `RuntimeError`、`FileExistsError`），不使用通用的 `Exception`。异常链 MUST 使用 `raise ... from e` 保留原始堆栈。

#### Scenario: subprocess 失败抛出 RuntimeError
- **WHEN** bean-identify、bean-extract 或 bean-file 命令执行失败
- **THEN** 系统抛出 `RuntimeError` 而非 `Exception`

#### Scenario: 异常保留原始堆栈信息
- **WHEN** 捕获底层异常后需要重新抛出
- **THEN** 系统使用 `raise RuntimeError("...") from e` 语法
