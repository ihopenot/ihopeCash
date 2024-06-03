# IhopeCash

基于Beancount的记账脚本，使用了[china_bean_importers](https://github.com/jiegec/china_bean_importers)批量导入账单。

# Usage
建议使用poetry或venv或conda管理单独环境
也可以直接pip install

```
git clone --recursive https://github.com/ihopenot/ihopeCash
```

## poetry
```
poetry shell

pip install -r china_bean_importers/requirements.txt
```

## 导出数据
从各个平台导出账单，放到rawdata目录下，并将文件名重命名为解压密码或pdf文档密码。

### wechat（微信）
我 -> 服务 -> 钱包 -> 账单 -> 常见问题 -> 下载账单 -> 用于个人对账
解压出csv文件

### alipay_mobile（支付宝）
我的 -> 账单 -> 开具交易流水证明 -> 用于个人对账
解压出csv文件

### boc_debit_card（中行借记卡）
首页 -> 更多 -> 助手 -> 交易流水打印

### ccb_debit_card（建行借记卡）
首页 -> 账户 -> 明细 -> 导出 -> 流水打印申请 -> 发送方式（Excel）
建行导出的zip是aes加密的，需要手动解压出来xls文件

## 导入数据
main.py脚本会自动解压解密zip文件或pdf文件
建行的zip包需要自行解压，脚本会自动把xls转成csv

### 使用main.py导入
```
python main.py
```

### 手动导入
手动解压解密zip和pdf文件，或者把pdf文件密码写入config.py中的pdf_passwords
```
bean-identify config.py rawdata
bean-extract config.py rawdata -- data/$YEAR/$MONTH/total.bean
bean-file -o data/$YEAR/$MONTH config.py rawdata
```

## fava
使用fava webui查看和编辑beancount中的账单
```
pip install fava
fava main.bean
```