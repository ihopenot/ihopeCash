"""
Beancount 导入器配置

使用统一的 Config 类加载配置
"""

import sys
import os
import atexit

# 路径问题修复：使用脚本所在目录
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from china_bean_importers import (
    wechat,
    alipay_mobile,
    boc_credit_card,
    boc_debit_card,
    cmb_debit_card,
    ccb_debit_card,
)

# 加载统一配置
_config_instance = Config()

# 获取配置字典（用于 importers）
config = _config_instance.to_dict()

# 添加转换后的 detail_mappings
config["detail_mappings"] = _config_instance.get_detail_mappings()

# 配置导入器列表
CONFIG = [
    wechat.Importer(config),
    alipay_mobile.Importer(config),
    boc_credit_card.Importer(config),
    boc_debit_card.Importer(config),
    cmb_debit_card.Importer(config),
    ccb_debit_card.Importer(config),
]

# 处理命令行输出重定向
if len(sys.argv) >= 3 and sys.argv[-2] == "--":
    outfile = sys.argv[-1]
    _redirect_file = open(outfile, "w", encoding="utf8")
    sys.stdout = _redirect_file
    
    def _close_redirect():
        try:
            sys.stdout = sys.__stdout__
            _redirect_file.close()
        except Exception:
            pass
    
    atexit.register(_close_redirect)
