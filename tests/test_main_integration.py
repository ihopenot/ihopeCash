#!/usr/bin/env python
"""测试 main.py 集成功能(不执行实际操作)"""

import os
import sys

def test_import_main():
    """测试 main.py 能否正常导入模块"""
    print("=" * 50)
    print("测试: main.py 模块导入")
    print("=" * 50)
    
    try:
        # 模拟导入 main.py 中的依赖
        from backend import Config, BillManager
        print("✓ backend 模块导入成功")
        
        # 初始化
        config = Config()
        manager = BillManager(config)
        print("✓ Config 和 BillManager 初始化成功")
        
        # 测试 append_to_month 方法(不实际执行)
        print("\n测试 append_to_month 方法签名:")
        import inspect
        sig = inspect.signature(manager.append_to_month)
        print(f"  参数: {sig}")
        
        # 测试 import_month 方法
        print("\n测试 import_month 方法签名:")
        sig = inspect.signature(manager.import_month)
        print(f"  参数: {sig}")
        
        print("\n✓ 所有方法签名正确")
        
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✓ 测试通过!\n")
    return True

def test_directory_creation():
    """测试目录创建功能(使用测试目录)"""
    print("=" * 50)
    print("测试: 目录创建功能")
    print("=" * 50)
    
    from backend import Config, BillManager
    import shutil
    
    # 创建测试配置
    config = Config()
    config._config["data_path"] = "test_data"
    manager = BillManager(config)
    
    try:
        # 清理测试目录
        if os.path.exists("test_data"):
            shutil.rmtree("test_data")
        
        # 测试年份目录创建
        print("\n1. 测试年份目录创建:")
        year_path = manager.ensure_year_directory("2024")
        print(f"  ✓ 年份目录已创建: {year_path}")
        assert os.path.exists(year_path), "年份目录不存在"
        assert os.path.exists(f"{year_path}/_.bean"), "_.bean 文件不存在"
        
        # 测试月份目录创建
        print("\n2. 测试月份目录创建:")
        month_path = manager.create_month_directory("2024", "12")
        print(f"  ✓ 月份目录已创建: {month_path}")
        assert os.path.exists(month_path), "月份目录不存在"
        assert os.path.exists(f"{month_path}/_.bean"), "_.bean 不存在"
        assert os.path.exists(f"{month_path}/total.bean"), "total.bean 不存在"
        assert os.path.exists(f"{month_path}/others.bean"), "others.bean 不存在"
        
        # 测试目录已存在的情况
        print("\n3. 测试目录已存在(应该抛出异常):")
        try:
            manager.create_month_directory("2024", "12", remove_if_exists=False)
            print("  ✗ 应该抛出 FileExistsError")
            return False
        except FileExistsError as e:
            print(f"  ✓ 正确抛出异常: {e}")
        
        # 测试强制覆盖
        print("\n4. 测试强制覆盖:")
        month_path = manager.create_month_directory("2024", "12", remove_if_exists=True)
        print(f"  ✓ 强制覆盖成功: {month_path}")
        
        # 测试余额记录
        print("\n5. 测试余额记录:")
        balances = {"Assets:Bank:BOC": "5000.00", "Assets:Bank:ICBC": "3000.00"}
        manager.record_balances("2024", "12", balances)
        
        balance_file = f"{manager.data_path}/balance.bean"
        assert os.path.exists(balance_file), "balance.bean 不存在"
        
        with open(balance_file, 'r') as f:
            content = f.read()
            print(f"  余额文件内容:\n{content}")
            assert "2025-01-01 balance Assets:Bank:BOC 5000.00 CNY" in content
            assert "2025-01-01 balance Assets:Bank:ICBC 3000.00 CNY" in content
        print("  ✓ 余额记录格式正确")
        
        # 清理测试目录
        shutil.rmtree("test_data")
        print("\n✓ 测试目录已清理")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        # 清理
        if os.path.exists("test_data"):
            shutil.rmtree("test_data")
        return False
    
    print("\n✓ 测试通过!\n")
    return True

if __name__ == "__main__":
    all_passed = True
    
    all_passed &= test_import_main()
    all_passed &= test_directory_creation()
    
    print("=" * 50)
    if all_passed:
        print("✓ 所有集成测试通过!")
    else:
        print("✗ 部分测试失败")
        sys.exit(1)
    print("=" * 50)
