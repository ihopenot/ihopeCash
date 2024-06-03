import sys
import os

# importing problem, why?
sys.path.append(os.getcwd())

from china_bean_importers import (
    wechat,
    alipay_mobile,
    boc_credit_card,
    boc_debit_card,
    cmb_debit_card,
    ccb_debit_card,
)

from china_bean_importer_config import config  # your config file name

CONFIG = [
    wechat.Importer(config),
    alipay_mobile.Importer(config),
    boc_credit_card.Importer(config),
    boc_debit_card.Importer(config),
    cmb_debit_card.Importer(config),
    ccb_debit_card.Importer(config),
]

if sys.argv[-2] == "--":
    outfile = sys.argv[-1]
    sys.stdout = open(outfile, "w", encoding="utf8")

balance_accounts = ["Assets:BoC:Card:XXX", "Assets:CCB:Card:XXX", "Assets:Alipay:YueBao", "Assets:WeChat:Balance"]