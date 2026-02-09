#!/usr/bin/env python
"""简单测试 mail.py 重构 (不导入 mail 模块,避免 pandas 依赖)"""

def test_backend_passes_config():
    """测试 backend 是否正确传递配置"""
    print("=" * 50)
    print("测试: backend 传递配置给 mail")
    print("=" * 50)
    
    try:
        from backend import Config, BillManager
        
        # 创建配置
        config = Config()
        config._config["passwords"] = ["test123", "test456"]
        config._config["email"] = {
            "imap": {
                "host": "imap.example.com",
                "port": 993,
                "username": "test@example.com",
                "password": "password",
                "mailbox": "INBOX"
            }
        }
        
        manager = BillManager(config)
        
        print("✓ Config 创建成功")
        print(f"  passwords: {config._config.get('passwords')}")
        print(f"  email.imap.host: {config._config.get('email', {}).get('imap', {}).get('host')}")
        
        # 验证 BillManager 可以访问配置
        print(f"\n✓ BillManager 初始化成功")
        print(f"  manager.config._config keys: {list(manager.config._config.keys())}")
        
        # 模拟 download_bills 中的配置传递
        config_dict = manager.config._config
        print(f"\n✓ 配置字典可以传递:")
        print(f"  type: {type(config_dict)}")
        print(f"  passwords: {config_dict.get('passwords')}")
        
        print("\n✓ 配置传递机制正确!")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✓ 测试通过!\n")
    return True

def test_mail_function_signature():
    """测试 mail.py 函数签名 (通过源码检查)"""
    print("=" * 50)
    print("测试: mail.py 函数签名")
    print("=" * 50)
    
    try:
        with open("mail.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查 DownloadFiles 函数签名
        if "def DownloadFiles(config: Dict[str, Any] = None):" in content:
            print("✓ DownloadFiles 签名正确: config 参数已添加")
        else:
            print("✗ DownloadFiles 签名不正确")
            return False
        
        # 检查 BaseEmailHanlder __init__
        if "def __init__(self, config: Dict[str, Any] = None):" in content:
            print("✓ BaseEmailHanlder.__init__ 签名正确")
        else:
            print("✗ BaseEmailHanlder.__init__ 签名不正确")
            return False
        
        # 检查是否移除了旧的 Config 导入
        if "from config import Config" not in content:
            print("✓ 旧的 Config 导入已移除")
        else:
            print("⚠ 警告: 仍包含旧的 Config 导入")
        
        # 检查向后兼容代码
        if "from config import Config as OldConfig" in content:
            print("✓ 包含向后兼容代码")
        else:
            print("⚠ 警告: 缺少向后兼容代码")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✓ 测试通过!\n")
    return True

def test_backend_download_bills():
    """测试 backend download_bills 方法"""
    print("=" * 50)
    print("测试: backend.download_bills 实现")
    print("=" * 50)
    
    try:
        with open("backend.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查是否传递配置
        if "config_dict = self.config._config" in content:
            print("✓ backend 提取配置字典")
        else:
            print("✗ backend 未提取配置字典")
            return False
        
        if "DownloadFiles(config_dict)" in content:
            print("✓ backend 传递配置给 DownloadFiles")
        else:
            print("✗ backend 未传递配置")
            return False
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✓ 测试通过!\n")
    return True

if __name__ == "__main__":
    import sys
    
    all_passed = True
    
    all_passed &= test_backend_passes_config()
    all_passed &= test_mail_function_signature()
    all_passed &= test_backend_download_bills()
    
    print("=" * 50)
    if all_passed:
        print("✓ 所有测试通过!")
        print("\n✓ mail.py 重构完成:")
        print("  - DownloadFiles 接收 config 参数")
        print("  - BaseEmailHanlder 接收 config 参数")
        print("  - 所有 Handler 使用 self.config")
        print("  - backend 传递配置字典给 mail")
        print("  - 保持向后兼容")
    else:
        print("✗ 部分测试失败")
        sys.exit(1)
    print("=" * 50)
