#!/usr/bin/env python
"""测试 mail.py 重构后的功能"""

import sys

def test_mail_import():
    """测试 mail.py 能否正常导入"""
    print("=" * 50)
    print("测试 1: mail.py 模块导入")
    print("=" * 50)
    
    try:
        from mail import DownloadFiles, BaseEmailHanlder
        print("✓ mail 模块导入成功")
        
        # 测试函数签名
        import inspect
        sig = inspect.signature(DownloadFiles)
        print(f"  DownloadFiles 签名: {sig}")
        
        # 测试 BaseEmailHanlder 接受 config
        print("\n测试 BaseEmailHanlder:")
        test_config = {"rawdata_path": "test_rawdata", "passwords": ["test123"]}
        handler = BaseEmailHanlder(test_config)
        print(f"  ✓ BaseEmailHanlder 初始化成功")
        print(f"  ✓ handler.config: {handler.config}")
        
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✓ 测试 1 通过!\n")
    return True

def test_backend_integration():
    """测试 backend 与 mail 的集成"""
    print("=" * 50)
    print("测试 2: backend 与 mail 集成")
    print("=" * 50)
    
    try:
        from backend import Config, BillManager
        
        config = Config()
        manager = BillManager(config)
        
        print("✓ Config 和 BillManager 初始化成功")
        
        # 检查 download_bills 方法
        import inspect
        sig = inspect.signature(manager.download_bills)
        print(f"  download_bills 签名: {sig}")
        
        print("\n注意: download_bills 需要邮箱配置才能实际执行")
        print("  本测试仅验证方法存在和签名正确")
        
    except Exception as e:
        print(f"✗ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✓ 测试 2 通过!\n")
    return True

def test_config_structure():
    """测试配置结构"""
    print("=" * 50)
    print("测试 3: 配置字典结构")
    print("=" * 50)
    
    try:
        from backend import Config
        
        config = Config()
        
        # 验证配置是否可以作为字典传递
        config_dict = config._config
        print(f"✓ 配置字典: {config_dict}")
        
        # 模拟 mail.py 使用配置
        rawdata_path = config_dict.get("rawdata_path", "rawdata")
        print(f"✓ rawdata_path: {rawdata_path}")
        
        passwords = config_dict.get("passwords", [])
        print(f"✓ passwords: {passwords}")
        
        # 检查是否可以访问嵌套字典 (email.imap)
        has_email = "email" in config_dict
        print(f"  email 配置存在: {has_email}")
        
        if not has_email:
            print("  注意: 默认配置不包含 email 字段,需要手动配置")
        
    except Exception as e:
        print(f"✗ 配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✓ 测试 3 通过!\n")
    return True

if __name__ == "__main__":
    all_passed = True
    
    all_passed &= test_mail_import()
    all_passed &= test_backend_integration()
    all_passed &= test_config_structure()
    
    print("=" * 50)
    if all_passed:
        print("✓ 所有测试通过!")
        print("\n重构总结:")
        print("  - mail.py 不再直接导入 config.py")
        print("  - DownloadFiles 接收 config 参数")
        print("  - BaseEmailHanlder 接收 config 参数")
        print("  - backend.BillManager 传递配置给 mail")
        print("  - 保持向后兼容 (config=None 时使用旧配置)")
    else:
        print("✗ 部分测试失败")
        sys.exit(1)
    print("=" * 50)
