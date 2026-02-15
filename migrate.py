"""
迁移脚本 - 将 main.bean 和 accounts.bean 从项目根目录迁移到 data/ 目录

功能：
1. 将根目录的 main.bean 移动到 data/main.bean
2. 将根目录的 accounts.bean 移动到 data/accounts.bean
3. 修正 data/main.bean 中的 include 路径（去掉 data/ 前缀）
4. 幂等设计：已迁移则跳过

使用方式：
    python migrate.py
"""

import os
import re
import shutil


def migrate():
    """执行迁移"""
    data_dir = "data"
    
    # 确保 data 目录存在
    os.makedirs(data_dir, exist_ok=True)
    
    migrated = False
    
    # 迁移 main.bean
    src_main = "main.bean"
    dst_main = os.path.join(data_dir, "main.bean")
    
    if os.path.exists(src_main) and not os.path.exists(dst_main):
        shutil.move(src_main, dst_main)
        print(f"已迁移: {src_main} -> {dst_main}")
        
        # 修正 include 路径
        fix_include_paths(dst_main, data_dir)
        migrated = True
    elif os.path.exists(dst_main):
        print(f"跳过: {dst_main} 已存在")
    elif not os.path.exists(src_main):
        print(f"跳过: {src_main} 不存在，无需迁移")
    
    # 迁移 accounts.bean
    src_accounts = "accounts.bean"
    dst_accounts = os.path.join(data_dir, "accounts.bean")
    
    if os.path.exists(src_accounts) and not os.path.exists(dst_accounts):
        shutil.move(src_accounts, dst_accounts)
        print(f"已迁移: {src_accounts} -> {dst_accounts}")
        migrated = True
    elif os.path.exists(dst_accounts):
        print(f"跳过: {dst_accounts} 已存在")
    elif not os.path.exists(src_accounts):
        print(f"跳过: {src_accounts} 不存在，无需迁移")
    
    if migrated:
        print("迁移完成")
    else:
        print("无需迁移")


def fix_include_paths(main_bean_path: str, data_dir: str):
    """修正 main.bean 中的 include 路径
    
    将 include "data/xxx" 改为 include "xxx"
    将 include "accounts.bean" 保持不变（已在同目录下）
    
    Args:
        main_bean_path: main.bean 文件路径
        data_dir: data 目录名
    """
    with open(main_bean_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 替换 include "data/..." 为 include "..."
    # 匹配 include "data/xxx" 格式
    prefix = data_dir.rstrip("/") + "/"
    pattern = re.compile(r'include\s+"' + re.escape(prefix) + r'([^"]+)"')
    new_content = pattern.sub(r'include "\1"', content)
    
    if new_content != content:
        with open(main_bean_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"已修正 {main_bean_path} 中的 include 路径")
    else:
        print(f"{main_bean_path} 中的 include 路径无需修正")


if __name__ == "__main__":
    migrate()
