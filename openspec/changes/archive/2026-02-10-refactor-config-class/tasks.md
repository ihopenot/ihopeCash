## 1. 准备工作

- [x] 1.1 备份现有文件（config.py, backend.py, config.yaml, beancount_config.py）
- [x] 1.2 验证现有代码能正常运行，作为基准测试

## 2. 创建新的 config.py

- [x] 2.1 创建 config.py 文件，添加基本的类结构和文档字符串
- [x] 2.2 实现 __init__ 方法，接收 config_file 参数
- [x] 2.3 实现 _get_default_config 方法，定义 system 配置节的默认值
- [x] 2.4 实现 _get_default_config 中的 email 配置节默认值
- [x] 2.5 实现 _get_default_config 中的 passwords 和 pdf_passwords 默认值
- [x] 2.6 实现 _get_default_config 中的 importers.alipay 完整默认配置
- [x] 2.7 实现 _get_default_config 中的 importers.wechat 完整默认配置
- [x] 2.8 实现 _get_default_config 中的 importers.thu_ecard 默认配置
- [x] 2.9 实现 _get_default_config 中的 importers.hsbc_hk 默认配置
- [x] 2.10 实现 _get_default_config 中的 card_narration_whitelist/blacklist 默认值
- [x] 2.11 实现 _get_default_config 中的 card_accounts、unknown_*_account、detail_mappings 默认值

## 3. 实现配置加载和保存

- [x] 3.1 实现 load 方法，加载 YAML 配置文件
- [x] 3.2 实现 load 方法中配置文件不存在时的创建逻辑
- [x] 3.3 实现 _deep_merge 方法，递归合并嵌套字典
- [x] 3.4 实现 _merge_defaults 方法，调用 _deep_merge 合并默认配置
- [x] 3.5 在 load 方法中调用 _merge_defaults 确保所有字段存在
- [x] 3.6 实现 save 方法，将配置保存到 YAML 文件

## 4. 实现访问接口

- [x] 4.1 实现 __getitem__ 方法，支持字典式访问
- [x] 4.2 实现 get 方法，支持带默认值的安全访问
- [x] 4.3 实现 to_dict 方法，使用 deepcopy 返回配置副本
- [x] 4.4 实现 data_path 属性，从 system.data_path 读取
- [x] 4.5 实现 rawdata_path 属性，从 system.rawdata_path 读取
- [x] 4.6 实现 archive_path 属性，从 system.archive_path 读取
- [x] 4.7 实现 balance_accounts 属性，从 system.balance_accounts 读取

## 5. 实现便捷访问方法

- [x] 5.1 实现 get_detail_mappings 方法，尝试导入 BillDetailMapping
- [x] 5.2 在 get_detail_mappings 中实现 YAML 到 BDM 对象的转换逻辑
- [x] 5.3 在 get_detail_mappings 中实现 ImportError 的降级处理
- [x] 5.4 实现 get_email_config 方法
- [x] 5.5 实现 get_importer_config 方法，接收 importer_name 参数
- [x] 5.6 实现 get_passwords 方法，合并并去重 passwords 和 pdf_passwords

## 6. 实现调试辅助方法

- [x] 6.1 实现 __repr__ 方法
- [x] 6.2 实现 __str__ 方法
- [x] 6.3 实现 keys 方法，返回顶层配置键列表
- [x] 6.4 实现 _print_dict 递归打印方法
- [x] 6.5 实现 print_structure 方法，调用 _print_dict

## 7. 修改 backend.py

- [x] 7.1 在 backend.py 顶部添加 from config import Config 导入
- [x] 7.2 删除 backend.py 中的 Config 类定义（第 16-108 行左右）
- [x] 7.3 修改 BillManager.download_bills 方法，使用 config.to_dict() 替代 config._config
- [x] 7.4 验证 backend.py 没有其他对 Config 类的引用

## 8. 更新 config.yaml

- [x] 8.1 创建新的 config.yaml 结构，添加 system 配置节
- [x] 8.2 将现有的 data_path、rawdata_path、archive_path、balance_accounts 移至 system 下
- [x] 8.3 保留 email 配置节（已存在）
- [x] 8.4 添加 passwords 配置节（可以从 config.example.py 的 pdf_passwords 迁移）
- [x] 8.5 添加 importers 配置节，从 config.example.py 迁移 alipay 配置
- [x] 8.6 添加 importers.wechat 配置，从 config.example.py 迁移
- [x] 8.7 添加 importers.thu_ecard 配置（如需要）
- [x] 8.8 添加 importers.hsbc_hk 配置（如需要）
- [x] 8.9 添加 card_narration_whitelist/blacklist 到 importers 节
- [x] 8.10 添加 card_accounts 配置节，从 config.example.py 迁移
- [x] 8.11 添加 unknown_expense_account 和 unknown_income_account 配置
- [x] 8.12 添加 detail_mappings 配置节，从 config.example.py 的 BDM 转换为 YAML 格式

## 9. 重写 beancount_config.py

- [x] 9.1 修改导入语句，从 config import Config
- [x] 9.2 创建 Config 实例：_config_instance = Config()
- [x] 9.3 使用 _config_instance.to_dict() 获取配置字典
- [x] 9.4 调用 _config_instance.get_detail_mappings() 并赋值给 config["detail_mappings"]
- [x] 9.5 验证 CONFIG 列表正确初始化所有 Importer
- [x] 9.6 删除对 china_bean_importer_config 的导入（如存在）

## 10. 修改 main.py

- [x] 10.1 修改导入语句，从 from backend import Config 改为 from config import Config
- [x] 10.2 验证 main.py 中其他代码无需修改

## 11. 测试验证

- [x] 11.1 测试 Config 类基本功能：加载、保存、默认值合并
- [x] 11.2 测试属性访问：config.data_path、config.balance_accounts
- [x] 11.3 测试字典访问：config["system"]["data_path"]、config["email"]["imap"]["host"]
- [x] 11.4 测试 to_dict 方法返回深拷贝
- [x] 11.5 测试 get_detail_mappings 转换功能
- [x] 11.6 测试 get_email_config、get_importer_config、get_passwords
- [x] 11.7 运行 python main.py 测试完整的业务流程
- [x] 11.8 运行 bean-identify beancount_config.py rawdata 验证 beancount 集成 (需要安装依赖)
- [x] 11.9 测试向后兼容：使用旧格式的 config.yaml 是否能正常工作
- [x] 11.10 验证 mail.py 无需修改即可使用新配置

## 12. 清理和文档

- [x] 12.1 删除备份文件（如果所有测试通过）
- [x] 12.2 更新项目文档，说明新的配置结构
- [x] 12.3 创建 config.yaml.example 作为配置模板
- [x] 12.4 （可选）删除或标记为弃用的 china_bean_importer_config.py
