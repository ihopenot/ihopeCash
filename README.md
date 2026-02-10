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
pip install -r requirements.txt
```

## config

将 `config.example.yaml` 复制为 `config.yaml`，并修改其中的配置信息：

```bash
cp config.example.yaml config.yaml
```

### 配置说明

#### email - 邮箱配置
通过 IMAP 自动下载邮件附件中的账单。默认配置为 QQ 邮箱，请修改为你的邮箱服务商信息：
- `host`: IMAP 服务器地址
- `port`: IMAP 端口（通常为 993）
- `username`: 邮箱账号
- `password`: 邮箱密码或授权码
- `mailbox`: 邮箱文件夹（建议使用邮箱的分类功能，将账单邮件单独分类到一个文件夹）

**注意**：导入脚本只会读取未读邮件，并在处理后标记为已读。需要处理的邮件需要在邮箱中标记为未读。

**目前支持网络下载的账单**：
 - 中国银行借记卡账单
 - 建设银行借记卡账单
 - 微信账单
 - 支付宝账单

#### passwords - 附件解压密码
PDF 和 ZIP 附件的解压密码列表。如果不填或解压失败，程序会尝试爆破密码（可能需要数分钟）。

#### rawdata_path / data_path / archive_path
原始账单、处理后数据、归档文件的存放路径。

#### balance_accounts - 余额断言账户
需要录入余额断言的账户列表。设置后，导入脚本会提示你输入这些账户的余额。


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
配置好了imap之后导入脚本会自动从邮箱拉取账单

手动导入的话需要将对应的附件解密解压缩，并转换成对应importer支持的格式

### 使用main.py导入
```
python main.py
```

## fava
使用fava webui查看和编辑beancount中的账单
```
pip install fava
fava main.bean
```

## TODO
[ ] 卡号不存在时无法识别rawdata文件