# Usage
```
cd china_bean_importers
poetry shell
cd ..

bean-identify config.py rawdata
bean-extract config.py rawdata -- data/$YEAR/$MONTH/total.bean
bean-file -o data/$YEAR/$MONTH config.py rawdata
```