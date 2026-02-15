"""
统一配置管理模块

提供 Config 类用于管理所有应用配置，包括：
- 环境配置（路径、Web 服务）来自 env.yaml
- 业务配置（邮件、导入器、账户映射等）来自 config.yaml
"""

import os
import re
import yaml
import copy
from typing import Dict, Any, Optional, List


class Config:
    """统一配置管理类
    
    职责：
    1. 加载 env.yaml（环境配置，必须存在）和 config.yaml（业务配置，可不存在）
    2. 提供便捷的属性访问（向后兼容 backend.py）
    3. 支持字典式访问（用于 mail.py）
    4. 提供完整 dict（用于 beancount_config.py）
    5. 将 YAML 配置转换为特定对象（如 BillDetailMapping）
    6. 提供首次引导完成后的配置写入方法
    
    使用方式：
        # 初始化（双文件加载）
        config = Config()  # 默认加载 env.yaml + config.yaml
        config = Config("custom_config.yaml", env_file="custom_env.yaml")
        
        # 检查是否需要引导
        if config.setup_required:
            # 引导流程...
            pass
        
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
    
    def __init__(self, config_file: str = "config.yaml", env_file: str = "env.yaml"):
        """初始化配置管理器
        
        Args:
            config_file: 业务配置文件路径，默认为 config.yaml
            env_file: 环境配置文件路径，默认为 env.yaml
            
        Raises:
            FileNotFoundError: env_file 不存在时抛出
        """
        self.config_file = config_file
        self.env_file = env_file
        self._config: Dict[str, Any] = {}
        self._setup_required: bool = False
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
                "card_narration_whitelist": ["财付通(银联云闪付)"],
                "card_narration_blacklist": ["支付宝", "财付通", "美团支付"]
            },
            "card_accounts": {},
            "unknown_expense_account": "Expenses:Unknown",
            "unknown_income_account": "Income:Unknown",
            "detail_mappings": [],
            "web": {
                "host": "0.0.0.0",
                "port": 8000,
                "password": "change_this_password",
                "jwt_secret": "change_this_secret_key",
                "token_expire_days": 7
            }
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
    
    def _deep_override(self, target: dict, source: dict):
        """深度覆盖字典（source 中的值覆盖 target 中的值）
        
        Args:
            target: 目标字典（会被修改）
            source: 源字典
        """
        for key, value in source.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                self._deep_override(target[key], value)
            else:
                target[key] = value
    
    def _merge_defaults(self):
        """将默认配置合并到当前配置中（不覆盖已存在的值）"""
        defaults = self._get_default_config()
        self._deep_merge(self._config, defaults)
    
    def _load_env(self) -> Dict[str, Any]:
        """加载环境配置文件
        
        Returns:
            环境配置字典
            
        Raises:
            FileNotFoundError: env_file 不存在
        """
        if not os.path.exists(self.env_file):
            raise FileNotFoundError(
                f"环境配置文件 {self.env_file} 不存在。"
                f"请复制 env.example.yaml 为 {self.env_file} 并修改配置。"
            )
        
        with open(self.env_file, 'r', encoding='utf-8') as f:
            env_config = yaml.load(f, Loader=yaml.FullLoader) or {}
        
        return env_config
    
    def load(self):
        """加载配置文件
        
        加载流程：
        1. 加载 env.yaml（必须存在，否则抛出 FileNotFoundError）
        2. 加载 config.yaml（不存在则标记 setup_required，不自动创建）
        3. env.yaml 中的 system/web 字段覆盖 config.yaml 中的对应字段
        4. 合并默认配置确保所有必需字段存在
        """
        # 1. 加载环境配置
        env_config = self._load_env()
        
        # 2. 加载业务配置
        if not os.path.exists(self.config_file):
            # config.yaml 不存在，标记需要引导
            self._setup_required = True
            self._config = self._get_default_config()
        else:
            # 加载现有业务配置
            self._setup_required = False
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.load(f, Loader=yaml.FullLoader) or {}
            # 合并默认配置（确保所有必需字段存在）
            self._merge_defaults()
        
        # 3. env.yaml 中的 system/web 覆盖 config 中的对应字段
        if "system" in env_config:
            if "system" not in self._config:
                self._config["system"] = {}
            self._deep_override(self._config["system"], env_config["system"])
        
        if "web" in env_config:
            if "web" not in self._config:
                self._config["web"] = {}
            self._deep_override(self._config["web"], env_config["web"])
    
    @property
    def setup_required(self) -> bool:
        """是否需要运行首次配置引导"""
        return self._setup_required
    
    @setup_required.setter
    def setup_required(self, value: bool):
        """设置引导状态"""
        self._setup_required = value
    
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
    
    # ==================== Web 配置属性 ====================
    
    @property
    def web_host(self) -> str:
        """Web 服务监听地址"""
        return self._config.get("web", {}).get("host", "0.0.0.0")
    
    @property
    def web_port(self) -> int:
        """Web 服务端口"""
        return self._config.get("web", {}).get("port", 8000)
    
    @property
    def web_password(self) -> str:
        """Web 界面密码"""
        return self._config.get("web", {}).get("password", "change_this_password")
    
    @property
    def jwt_secret(self) -> str:
        """JWT 签名密钥"""
        return self._config.get("web", {}).get("jwt_secret", "change_this_secret_key")
    
    @property
    def token_expire_days(self) -> int:
        """Token 有效期（天）"""
        return self._config.get("web", {}).get("token_expire_days", 7)
    
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
    
    def validate_web_config(self) -> List[str]:
        """验证 Web 配置，返回警告列表
        
        Returns:
            警告信息列表
        """
        warnings = []
        
        # 检查密码是否为默认值
        if self.web_password == "change_this_password":
            warnings.append("警告: 请修改 env.yaml 中的 web.password")
        
        # 检查 JWT 密钥是否为默认值
        if self.jwt_secret == "change_this_secret_key":
            warnings.append("警告: 请修改 env.yaml 中的 web.jwt_secret")
        
        return warnings
    
    # ==================== Web 端配置编辑 ====================
    
    # 受保护的顶层字段（PUT 时自动跳过）
    _PROTECTED_TOP_KEYS = {"web", "passwords", "pdf_passwords"}
    # 受保护的 system 子字段
    _PROTECTED_SYSTEM_KEYS = {"data_path", "rawdata_path", "archive_path"}
    
    def get_editable_config(self) -> Dict[str, Any]:
        """返回脱敏后的可编辑配置
        
        排除: web 节点、路径字段、passwords、pdf_passwords
        脱敏: email.imap.password 置为空字符串
        
        Returns:
            脱敏后的可编辑配置字典
        """
        result = copy.deepcopy(self._config)
        
        # 移除受保护的顶层字段
        for key in self._PROTECTED_TOP_KEYS:
            result.pop(key, None)
        
        # 移除受保护的 system 子字段
        if "system" in result:
            for key in self._PROTECTED_SYSTEM_KEYS:
                result["system"].pop(key, None)
        
        # 脱敏: email.imap.password 置空
        if "email" in result and "imap" in result.get("email", {}):
            result["email"]["imap"]["password"] = ""
        
        return result
    
    def update_from_web(self, data: Dict[str, Any]):
        """从 Web 端提交的数据更新配置
        
        后端强制跳过受保护字段，email.imap.password 空值跳过、非空更新。
        保存到文件并重新加载。
        
        Args:
            data: 前端提交的配置数据
        """
        # 移除受保护的顶层字段（即使前端提交了也忽略）
        for key in self._PROTECTED_TOP_KEYS:
            data.pop(key, None)
        
        # 处理 system 字段：保护路径字段
        if "system" in data:
            for key in self._PROTECTED_SYSTEM_KEYS:
                data["system"].pop(key, None)
            # 合并 system 的可编辑字段
            if "system" in self._config:
                self._config["system"].update(data.pop("system"))
            else:
                self._config["system"] = data.pop("system")
        
        # 处理 email.imap.password：空值跳过，非空更新
        if "email" in data and "imap" in data.get("email", {}):
            new_email_password = data["email"]["imap"].get("password", "")
            if not new_email_password:
                # 空值 -> 保留原密码
                original_password = self._config.get("email", {}).get("imap", {}).get("password", "")
                data["email"]["imap"]["password"] = original_password
        
        # 合并其余可编辑字段
        for key, value in data.items():
            if isinstance(value, dict) and isinstance(self._config.get(key), dict):
                self._config[key].update(value)
            else:
                self._config[key] = value
        
        # 保存并重新加载
        self.save()
        self.load()
    
    def update_web_password(self, new_password: str):
        """更新 Web 登录密码
        
        注意：密码存储在 env.yaml 中，此方法更新 env.yaml。
        
        Args:
            new_password: 新密码
        """
        # 加载当前 env.yaml
        with open(self.env_file, 'r', encoding='utf-8') as f:
            env_config = yaml.load(f, Loader=yaml.FullLoader) or {}
        
        # 更新密码
        if "web" not in env_config:
            env_config["web"] = {}
        env_config["web"]["password"] = new_password
        
        # 保存 env.yaml
        with open(self.env_file, 'w', encoding='utf-8') as f:
            yaml.dump(
                env_config,
                f,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False
            )
        
        # 重新加载
        self.load()
    
    # ==================== 首次引导 ====================
    
    def get_setup_defaults(self) -> Dict[str, Any]:
        """返回引导页使用的默认配置
        
        Returns:
            包含所有导入器和交易摘要过滤默认值的配置
        """
        defaults = self._get_default_config()
        # 移除不需要在引导中配置的字段
        defaults.pop("web", None)
        defaults.pop("passwords", None)
        defaults.pop("pdf_passwords", None)
        if "system" in defaults:
            defaults["system"].pop("data_path", None)
            defaults["system"].pop("rawdata_path", None)
            defaults["system"].pop("archive_path", None)
        return defaults
    
    def complete_setup(self, config_data: Dict[str, Any], new_accounts: List[Dict[str, str]]):
        """完成首次引导，一次性写入配置和新增账户
        
        Args:
            config_data: 业务配置数据（不含 system 路径和 web）
            new_accounts: 新增账户列表，每项包含 account_type, path, currencies, comment
        """
        # 1. 构建完整的业务配置
        # 移除可能从前端提交的 system 路径和 web 字段
        config_data.pop("web", None)
        if "system" in config_data:
            config_data["system"].pop("data_path", None)
            config_data["system"].pop("rawdata_path", None)
            config_data["system"].pop("archive_path", None)
        
        # 以默认配置为基础，用前端数据覆盖
        self._config = self._get_default_config()
        for key, value in config_data.items():
            if isinstance(value, dict) and isinstance(self._config.get(key), dict):
                self._deep_override(self._config[key], value)
            else:
                self._config[key] = value
        
        # 2. 写入 config.yaml（不含 system 路径和 web，这些来自 env.yaml）
        # 创建要保存的配置副本
        save_config = copy.deepcopy(self._config)
        # 从保存的配置中移除 system 路径字段（这些来自 env.yaml）
        if "system" in save_config:
            save_config["system"].pop("data_path", None)
            save_config["system"].pop("rawdata_path", None)
            save_config["system"].pop("archive_path", None)
            # 如果 system 只剩空字典，保留它（因为有 balance_accounts）
        # 移除 web 配置（来自 env.yaml）
        save_config.pop("web", None)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(
                save_config,
                f,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False
            )
        
        # 3. 写入新增账户到 accounts.bean
        if new_accounts:
            self._write_new_accounts(new_accounts)
        
        # 4. 重新加载配置
        self.load()
    
    def _write_new_accounts(self, new_accounts: List[Dict[str, str]]):
        """将新增账户写入 accounts.bean（去重）
        
        Args:
            new_accounts: 新增账户列表
        """
        accounts_bean = os.path.join(self.data_path, "accounts.bean")
        
        # 读取已有账户名
        existing_accounts = set()
        if os.path.exists(accounts_bean):
            with open(accounts_bean, 'r', encoding='utf-8') as f:
                for line in f:
                    match = re.match(r'\d{4}-\d{2}-\d{2}\s+open\s+(\S+)', line.strip())
                    if match:
                        existing_accounts.add(match.group(1))
        
        # 去重并写入
        lines_to_add = []
        seen = set()
        for acc in new_accounts:
            account_type = acc.get("account_type", "")
            path = acc.get("path", "").strip()
            if not account_type or not path:
                continue
            
            full_account = f"{account_type}:{path}"
            if full_account in existing_accounts or full_account in seen:
                continue
            
            seen.add(full_account)
            
            currencies = acc.get("currencies", "").strip()
            comment = acc.get("comment", "").strip()
            
            currencies_part = f" {currencies}" if currencies else ""
            comment_part = f" ; {comment}" if comment else ""
            lines_to_add.append(f"1999-01-01 open {full_account}{currencies_part}{comment_part}\n")
        
        if lines_to_add:
            # 确保文件以换行符结尾
            if os.path.exists(accounts_bean):
                with open(accounts_bean, "rb") as f:
                    f.seek(0, 2)
                    if f.tell() > 0:
                        f.seek(-1, 2)
                        if f.read(1) != b'\n':
                            with open(accounts_bean, "a", encoding="utf-8") as fa:
                                fa.write("\n")
            
            with open(accounts_bean, "a", encoding="utf-8") as f:
                for line in lines_to_add:
                    f.write(line)
    
    # ==================== 调试与信息 ====================
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"Config(config_file='{self.config_file}', env_file='{self.env_file}')"
    
    def __str__(self) -> str:
        """可读的字符串表示"""
        return f"Config loaded from '{self.config_file}' + '{self.env_file}' with {len(self._config)} top-level keys"
    
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
