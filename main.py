import os
import shutil
import datetime
import sys
import argparse
from config import Config
from backend import BillManager

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-A", "--append", action="store_true", help="Append to existing month directory")
    parser.add_argument("--append-folder", type=str, help="Append to specified month directory")
    parser.add_argument("--append-name", type=str, default="append", help="Append to specified month directory")
    args = parser.parse_args()
    
    # 初始化配置和管理器
    config = Config()
    manager = BillManager(config)
    
    # 追加模式
    if args.append:
        print("Append mode, skip downloading and decryption.")
        result = manager.append_to_month(args.append_folder, args.append_name)
        
        if result["success"]:
            print("Append completed!")
        else:
            print(f"Append failed: {result['message']}")
            sys.exit(1)
        sys.exit(0)
    
    # 正常导入模式
    input("Downloading bills, press Enter to continue...")
    try:
        manager.download_bills()
    except Exception as e:
        print(f"Download failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    input("decryption done, press Enter to continue...")
    
    # 年月选择
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    if month == 1:
        year -= 1
        month = 12
    else:
        month -= 1
    year = str(year)
    month = str(month)
    
    opt = input(f"Create directory of {year}-{month}? (y/N):")
    if opt.lower() != "y":
        year = input("Year: ").strip()
        month = input("Month: ").strip()
        # 验证输入
        try:
            y = int(year)
            m = int(month)
            if m < 1 or m > 12:
                print("Month must be between 1 and 12")
                sys.exit(1)
        except ValueError:
            print("Year and month must be valid numbers")
            sys.exit(1)
    
    # 识别文件
    try:
        output = manager.bean_identify()
        print(output)
    except Exception as e:
        print(f"Identify failed: {e}")
        sys.exit(1)
    
    print(f"creating directory of {year}-{month}")
    input("Press Enter to confirm...")
    
    # 创建目录
    try:
        # 检查是否已存在
        if manager.month_directory_exists(year, month):
            opt = input("Directory already exists, remove it? (y/N):")
            force = opt.lower() == "y"
            if not force:
                sys.exit(0)
        else:
            force = False
        
        month_path = manager.create_month_directory(year, month, force)
        print(f"Directory created: {month_path}")
        
    except Exception as e:
        print(f"Create directory failed: {e}")
        sys.exit(1)
    
    # 导入交易
    input("Create done, press Enter to import...")
    try:
        manager.bean_extract(f"{month_path}/total.bean")
    except Exception as e:
        print(f"Import failed: {e}")
        sys.exit(1)
    
    # 录入余额
    print("Input balance")
    balances = {}
    for account in config.balance_accounts:
        balance = input(f"{account}: ")
        balances[account] = balance
    
    try:
        manager.record_balances(year, month, balances)
    except Exception as e:
        print(f"Record balance failed: {e}")
        sys.exit(1)
    
    # 归档
    input("Import done, press Enter to archive...")
    try:
        manager.bean_archive()
    except Exception as e:
        print(f"Archive failed: {e}")
        sys.exit(1)
    
    print("All done!")
