"""
统一配置管理模块

提供 Config 类用于管理所有应用配置，包括：
- 系统配置（路径、余额账户等）
- 邮件配置
- Beancount 导入器配置
- 账户映射和交易匹配规则
"""

import os
import yaml
import copy
from typing import Dict, Any, Optional, List


class Config:
    """统一配置管理类
    
    职责：
    1. 加载/保存 config.yaml
    2. 提供便捷的属性访问（向后兼容 backend.py）
    3. 支持字典式访问（用于 mail.py）
    4. 提供完整 dict（用于 beancount_config.py）
    5. 将 YAML 配置转换为特定对象（如 BillDetailMapping）
    
    使用方式：
        # 初始化
        config = Config()  # 默认加载 config.yaml
        config = Config("custom_config.yaml")  # 自定义配置文件
        
        # 属性访问（便捷方式）
        config.data_path              # "data"
        config.rawdata_path           # "rawdata"
        config.balance_accounts       # [...]
        
        # 字典访问（灵活方式）
        config["system"]["data_path"]       # "data"
        config["email"]["imap"]["host"]     # "imap.qq.com"
        config["importers"]["alipay"]       # {...}
        
        # 安全访问（带默认值）
        config.get("passwords", [])
        
        # 获取完整配置字典（用于传递给其他模块）
        config_dict = config.to_dict()
        
        # 获取转换后的对象
        detail_mappings = config.get_detail_mappings()  # List[BillDetailMapping]
    """
    
    def __init__(self, config_file: str = "config.yaml"):
        """初始化配置管理器
        
        Args:
            config_file: 配置文件路径，默认为 config.yaml
        """
        self.config_file = config_file
        self._config: Dict[str, Any] = {}
        self.load()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """返回默认配置字典
        
        Returns:
            默认配置字典
        """
        return {
            "system": {
                "data_path": "data",
                "rawdata_path": "rawdata",
                "archive_path": "archive",
                "balance_accounts": []
            },
            "email": {
                "imap": {
                    "host": "imap.qq.com",
                    "port": 993,
                    "username": "",
                    "password": "",
                    "mailbox": "Bills"
                }
            },
            "passwords": [],
            "pdf_passwords": [],
            "importers": {
                "alipay": {
                    "account": "Assets:Alipay:Balance",
                    "huabei_account": "Liabilities:Alipay:HuaBei",
                    "douyin_monthly_payment_account": "Liabilities:DouyinMonthlyPayment",
                    "yuebao_account": "Assets:Alipay:YueBao",
                    "red_packet_income_account": "Income:RedPacket",
                    "red_packet_expense_account": "Expenses:RedPacket",
                    "category_mapping": {}
                },
                "wechat": {
                    "account": "Assets:WeChat:Balance",
                    "lingqiantong_account": "Assets:WeChat:LingQianTong",
                    "red_packet_income_account": "Income:RedPacket",
                    "red_packet_expense_account": "Expenses:RedPacket",
                    "family_card_expense_account": "Expenses:WeChat:FamilyCard",
                    "group_payment_expense_account": "Expenses:Unknown",
                    "group_payment_income_account": "Income:Unknown",
                    "transfer_expense_account": "Expenses:Unknown",
                    "transfer_income_account": "Income:Unknown"
                },
                "thu_ecard": {
                    "account": "Assets:Card:THU"
                },
                "hsbc_hk": {
                    "account_mapping": {},
                    "use_cnh": False
                },
                "card_narration_whitelist": [],
                "card_narration_blacklist": []
            },
            "card_accounts": {},
            "unknown_expense_account": "Expenses:Unknown",
            "unknown_income_account": "Income:Unknown",
            "detail_mappings": []
        }
    
    def _deep_merge(self, target: dict, source: dict):
        """深度合并字典（source 中的值只在 target 中不存在时才添加）
        
        Args:
            target: 目标字典（会被修改）
            source: 源字典
        """
        for key, value in source.items():
            if key not in target:
                target[key] = value
            elif isinstance(value, dict) and isinstance(target[key], dict):
                self._deep_merge(target[key], value)
    
    def _merge_defaults(self):
        """将默认配置合并到当前配置中（不覆盖已存在的值）"""
        defaults = self._get_default_config()
        self._deep_merge(self._config, defaults)
    
    def load(self):
        """加载配置文件，文件不存在时创建默认配置"""
        if not os.path.exists(self.config_file):
            # 配置文件不存在，创建默认配置
            self._config = self._get_default_config()
            self.save()
        else:
            # 加载现有配置文件
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.load(f, Loader=yaml.FullLoader) or {}
            
            # 合并默认配置（确保所有必需字段存在）
            self._merge_defaults()
    
    def save(self, file_path: Optional[str] = None):
        """保存配置到 YAML 文件
        
        Args:
            file_path: 保存路径，默认为初始化时的配置文件路径
        """
        target_path = file_path if file_path else self.config_file
        with open(target_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                self._config,
                f,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False
            )
    
    # ==================== 字典式访问 ====================
    
    def __getitem__(self, key: str) -> Any:
        """支持字典式访问: config["key"]
        
        Args:
            key: 配置项键名
            
        Returns:
            配置值
            
        Raises:
            KeyError: 配置项不存在
        """
        return self._config[key]
    
    def get(self, key: str, default: Any = None) -> Any:
        """安全访问配置项，支持默认值
        
        Args:
            key: 配置项键名
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        return self._config.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """返回配置的完整字典副本
        
        用于传递给需要 dict 的模块（如 mail.py, beancount_config.py）
        
        Returns:
            配置字典的深拷贝
        """
        return copy.deepcopy(self._config)
    
    # ==================== 系统配置属性 ====================
    
    @property
    def data_path(self) -> str:
        """数据目录路径"""
        return self._config.get("system", {}).get("data_path", "data")
    
    @property
    def rawdata_path(self) -> str:
        """原始数据目录路径"""
        return self._config.get("system", {}).get("rawdata_path", "rawdata")
    
    @property
    def archive_path(self) -> str:
        """归档目录路径"""
        return self._config.get("system", {}).get("archive_path", "archive")
    
    @property
    def balance_accounts(self) -> List[str]:
        """余额账户列表"""
        return self._config.get("system", {}).get("balance_accounts", [])
    
    # ==================== 特殊转换方法 ====================
    
    def get_detail_mappings(self) -> List[Any]:
        """获取 detail_mappings 并转换为 BillDetailMapping 对象列表
        
        Returns:
            BillDetailMapping 对象列表
            如果 china_bean_importers 不可用，返回原始 dict 列表
        """
        mappings_data = self._config.get("detail_mappings", [])
        
        # 尝试导入 BillDetailMapping
        try:
            from china_bean_importers.common import BillDetailMapping as BDM
            
            # 转换为 BDM 对象
            result = []
            for mapping in mappings_data:
                bdm = BDM(
                    narration_keywords=mapping.get("narration_keywords", []),
                    payee_keywords=mapping.get("payee_keywords", []),
                    destination_account=mapping.get("account", ""),
                    additional_tags=mapping.get("tags", []),
                    additional_metadata=mapping.get("metadata", {})
                )
                result.append(bdm)
            return result
            
        except ImportError:
            # china_bean_importers 不可用，返回原始数据
            return mappings_data
    
    # ==================== 便捷访问方法 ====================
    
    def get_email_config(self) -> Dict[str, Any]:
        """获取邮件配置
        
        Returns:
            邮件配置字典
        """
        return self._config.get("email", {})
    
    def get_importer_config(self, importer_name: str) -> Dict[str, Any]:
        """获取指定导入器的配置
        
        Args:
            importer_name: 导入器名称（如 "alipay", "wechat"）
            
        Returns:
            导入器配置字典
        """
        return self._config.get("importers", {}).get(importer_name, {})
    
    def get_passwords(self) -> List[str]:
        """获取密码列表（用于解密文件）
        
        Returns:
            密码列表（合并 passwords 和 pdf_passwords）
        """
        passwords = set()
        passwords.update(self._config.get("passwords", []))
        passwords.update(self._config.get("pdf_passwords", []))
        return list(passwords)
    
    # ==================== 调试与信息 ====================
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"Config(config_file='{self.config_file}')"
    
    def __str__(self) -> str:
        """可读的字符串表示"""
        return f"Config loaded from '{self.config_file}' with {len(self._config)} top-level keys"
    
    def keys(self) -> List[str]:
        """返回所有顶层配置键"""
        return list(self._config.keys())
    
    def _print_dict(self, d: dict, indent: int):
        """递归打印字典结构"""
        for key, value in d.items():
            print("  " * indent + f"- {key}")
            if isinstance(value, dict):
                self._print_dict(value, indent + 1)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                print("  " * (indent + 1) + f"[{len(value)} items]")
    
    def print_structure(self, indent: int = 0):
        """打印配置结构（用于调试）
        
        Args:
            indent: 缩进级别
        """
        self._print_dict(self._config, indent)




