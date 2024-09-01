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
将beancount_config.example.py和config.example.yaml复制一份，改名为beancount_config.py和config.yaml, 并将其中一些敏感信息修改成你对应的信息

imap是通过网络下载邮件附件，里面的信息填你自己的邮箱服务商提供的信息，默认的配置是qq邮箱

passwords是这些附件的解压密码，如果不填或者解压失败的话会爆破密码，可能会花费数分钟的时间

为了避免影响其他邮件，建议使用邮箱的分类功能将账单邮件单独分在一个mailbox内

导入脚本只会读取状态的为未读的邮件，并在处理后将其标记为已读，需要在邮箱里将需要处理邮件标为未读

目前支持网络下载的账单：
 - 中国银行借记卡账单
 - 建设银行借记卡账单
 - 微信账单
 - 支付宝账单

balance_account是需要录入余额断言的账户，设置好之后导入脚本会主动让你输入余额


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