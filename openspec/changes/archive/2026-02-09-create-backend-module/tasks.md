## 1. 创建 backend.py - Config 类

- [x] 1.1 创建 backend.py 文件,定义 Config 类框架
- [x] 1.2 实现 __init__ 方法,接收 config_file 参数 (默认 "config.yaml")
- [x] 1.3 实现 _get_default_config 方法,返回默认配置字典
- [x] 1.4 实现 load 方法,加载 YAML 配置文件,文件不存在时调用 save 创建默认配置
- [x] 1.5 实现 save 方法,将配置保存到 YAML 文件
- [x] 1.6 实现 __getitem__ 方法,支持 config["key"] 访问
- [x] 1.7 实现 get 方法,支持 config.get(key, default) 安全访问
- [x] 1.8 实现属性方法: data_path, rawdata_path, archive_path, balance_accounts

## 2. 创建 backend.py - BillManager 类框架

- [x] 2.1 定义 BillManager 类,__init__ 接收 Config 实例
- [x] 2.2 在 __init__ 中保存配置引用,提取常用路径到实例变量

## 3. 实现 BillManager - Beancount 命令封装

- [x] 3.1 实现 bean_identify 方法,调用 bean-identify 命令
- [x] 3.2 实现 bean_extract 方法,调用 bean-extract 命令
- [x] 3.3 实现 bean_archive 方法,调用 bean-file 命令
- [x] 3.4 确保命令失败时抛出异常并包含错误信息

## 4. 实现 BillManager - 邮件下载

- [x] 4.1 实现 download_bills 方法,调用 mail.DownloadFiles()
- [x] 4.2 添加异常处理,捕获并重新抛出邮件下载错误

## 5. 实现 BillManager - 目录管理

- [x] 5.1 实现 ensure_year_directory 方法,创建年份目录并配置 _.bean 和 main.bean
- [x] 5.2 实现 month_directory_exists 方法,检查月份目录是否存在
- [x] 5.3 实现 create_month_directory 方法,创建月份目录结构
- [x] 5.4 在 create_month_directory 中处理 remove_if_exists 参数,已存在时删除或抛出异常
- [x] 5.5 创建 _.bean, total.bean, others.bean 文件并配置 include 语句

## 6. 实现 BillManager - 余额管理

- [x] 6.1 实现 record_balances 方法,接收 year, month, balances 字典
- [x] 6.2 计算下个月1号日期作为断言日期
- [x] 6.3 确保 balance.bean 文件存在,不存在则创建
- [x] 6.4 追加余额断言到 balance.bean 文件,格式为 "YYYY-MM-DD balance <account> <amount> CNY"

## 7. 实现 BillManager - 完整工作流

- [x] 7.1 实现 import_month 方法,接收 year, month, balances, download, force_overwrite 参数
- [x] 7.2 在 import_month 中按顺序调用: download_bills (可选), bean_identify, create_month_directory, bean_extract, record_balances, bean_archive
- [x] 7.3 添加 try-except 块,捕获异常并返回 {"success": False, "message": "..."}
- [x] 7.4 成功时返回 {"success": True, "message": "导入完成", "data": {...}}

## 8. 实现 BillManager - 追加模式

- [x] 8.1 实现 append_to_month 方法,接收 folder, name 参数
- [x] 8.2 创建追加 .bean 文件并更新目录的 _.bean include 语句
- [x] 8.3 调用 bean_extract 提取交易到追加文件
- [x] 8.4 调用 bean_archive 归档原始文件
- [x] 8.5 返回成功/失败字典格式结果

## 9. 重构 main.py

- [x] 9.1 备份原始 main.py 为 main.py.backup
- [x] 9.2 导入 backend 模块: from backend import Config, BillManager
- [x] 9.3 初始化 Config 和 BillManager 实例
- [x] 9.4 重构追加模式分支,使用 manager.append_to_month
- [x] 9.5 重构正常模式下载步骤,使用 manager.download_bills
- [x] 9.6 重构识别文件步骤,使用 manager.bean_identify
- [x] 9.7 重构目录创建步骤,使用 manager.create_month_directory 和 manager.month_directory_exists
- [x] 9.8 重构提取交易步骤,使用 manager.bean_extract
- [x] 9.9 重构余额录入步骤,使用 manager.record_balances
- [x] 9.10 重构归档步骤,使用 manager.bean_archive
- [x] 9.11 保持所有 input() 交互不变

## 10. 测试验证

- [x] 10.1 测试首次运行自动创建 config.yaml
- [x] 10.2 测试正常导入流程: python main.py (完整流程)
- [x] 10.3 测试追加模式: python main.py -A --append-folder "2024/12"
- [x] 10.4 测试目录已存在时的覆盖提示
- [x] 10.5 测试错误处理: 邮件下载失败、命令执行失败等场景
- [x] 10.6 验证生成的文件和目录结构与原来一致
- [x] 10.7 验证 balance.bean 余额断言格式正确
