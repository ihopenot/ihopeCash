"""
迁移脚本 - 处理数据目录结构变更

当前结构:
  data/
  ├── config.yaml
  └── beancount/
      ├── data/          (bean 文件)
      ├── rawdata/       (原始账单)
      └── archive/       (归档数据)

使用方式：
    python migrate.py
"""

import os


def migrate():
    """执行迁移"""
    # 确保新目录结构存在
    for d in ["data/beancount/data", "data/beancount/rawdata", "data/beancount/archive"]:
        os.makedirs(d, exist_ok=True)
    
    print("目录结构检查完成")


if __name__ == "__main__":
    migrate()
