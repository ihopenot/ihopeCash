#!/usr/bin/env python
"""测试 backend 模块功能"""

import os
import sys

def test_config_creation():
    """测试 Config 自动创建配置文件"""
    print("=" * 50)
    print("测试 1: Config 自动创建配置文件")
    print("=" * 50)
    
    # 先导入 backend 创建配置
    from backend import Config
    
    config = Config()
    print("✓ Config 实例创建成功")
    
    # 验证配置文件已创建
    if os.path.exists("config.yaml"):
        print("✓ config.yaml 文件已自动创建")
    else:
        print("✗ config.yaml 文件未创建")
        return False
    
    # 验证配置值
    print(f"  - data_path: {config.data_path}")
    print(f"  - rawdata_path: {config.rawdata_path}")
    print(f"  - archive_path: {config.archive_path}")
    print(f"  - balance_accounts: {config.balance_accounts}")
    
    # 验证字典访问
    assert config["data_path"] == "data", "字典访问失败"
    print("✓ 字典式访问正常")
    
    # 验证 get 方法
    assert config.get("data_path") == "data", "get 方法失败"
    assert config.get("nonexistent", "default") == "default", "get 默认值失败"
    print("✓ get 方法正常")
    
    print("\n✓ 测试 1 通过!\n")
    return True

def test_billmanager_init():
    """测试 BillManager 初始化"""
    print("=" * 50)
    print("测试 2: BillManager 初始化")
    print("=" * 50)
    
    from backend import Config, BillManager
    
    config = Config()
    manager = BillManager(config)
    
    print("✓ BillManager 实例创建成功")
    print(f"  - data_path: {manager.data_path}")
    print(f"  - rawdata_path: {manager.rawdata_path}")
    print(f"  - archive_path: {manager.archive_path}")
    
    print("\n✓ 测试 2 通过!\n")
    return True

def test_directory_methods():
    """测试目录管理方法"""
    print("=" * 50)
    print("测试 3: 目录管理方法")
    print("=" * 50)
    
    from backend import Config, BillManager
    
    config = Config()
    manager = BillManager(config)
    
    # 测试 month_directory_exists
    exists = manager.month_directory_exists("2024", "12")
    print(f"✓ month_directory_exists('2024', '12'): {exists}")
    
    print("\n✓ 测试 3 通过!\n")
    return True

def test_config_save_load():
    """测试配置保存和重载"""
    print("=" * 50)
    print("测试 4: 配置保存和重载")
    print("=" * 50)
    
    from backend import Config
    
    config = Config()
    
    # 修改配置
    config._config["test_key"] = "test_value"
    
    # 保存到临时文件
    config.save("config_test.yaml")
    print("✓ 配置保存成功")
    
    # 重新加载
    config2 = Config("config_test.yaml")
    assert config2.get("test_key") == "test_value", "配置重载失败"
    print("✓ 配置重载成功")
    
    # 清理
    os.remove("config_test.yaml")
    print("✓ 测试文件已清理")
    
    print("\n✓ 测试 4 通过!\n")
    return True

if __name__ == "__main__":
    all_passed = True
    
    try:
        all_passed &= test_config_creation()
        all_passed &= test_billmanager_init()
        all_passed &= test_directory_methods()
        all_passed &= test_config_save_load()
        
        print("=" * 50)
        if all_passed:
            print("✓ 所有测试通过!")
        else:
            print("✗ 部分测试失败")
            sys.exit(1)
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
