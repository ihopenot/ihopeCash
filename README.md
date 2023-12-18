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

## 导入数据
各个平台导出的账单放rawdata里，中行借记卡账单pdf密码需要修改config中的pdf_passwords

### 使用main.py导入
```
python main.py
```

### 手动导入
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