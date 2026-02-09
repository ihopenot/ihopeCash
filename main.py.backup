import os
import shutil
from mail import DownloadFiles
import datetime
from config import Config
import sys
import argparse

datapath = Config["data_path"]
rawdatapath = Config["rawdata_path"]
archivepath = Config["archive_path"]

template = """include "others.bean"
include "total.bean"
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-A", "--append", action="store_true", help="Append to existing month directory")
    parser.add_argument("--append-folder", type=str, help="Append to specified month directory")
    parser.add_argument("--append-name", type=str, default="append", help="Append to specified month directory")
    args = parser.parse_args()

    if args.append:
        print("Append mode, skip downloading and decryption.")
        open(f"{datapath}/{args.append_folder}/{args.append_name}.bean", "w")
        open(f"{datapath}/{args.append_folder}/_.bean", "a").write(f"include \"{args.append_name}.bean\"\n")
        os.system(
            f"bean-extract beancount_config.py {rawdatapath} -- {datapath}/{args.append_folder}/{args.append_name}.bean"
        )
        os.system(f"bean-file -o {archivepath} beancount_config.py {rawdatapath}")
        sys.exit(0)

    input("Downloading bills, press Enter to continue...")
    DownloadFiles()
    # decrypt_rawdata(rm_ori)
    input("decryption done, press Enter to continue...")

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
        year = input("Year: ")
        month = input("Month: ")

    os.system(f"bean-identify beancount_config.py {rawdatapath}")

    print(f"creating directory of {year}-{month}")
    input("Press Enter to comfirm...")

    if not os.path.exists(f"{datapath}/{year}"):
        os.makedirs(f"{datapath}/{year}")
        open(f"{datapath}/{year}/_.bean", "w").write("\n")
        newline = f'include "{datapath}/{year}/_.bean"\n'
        if open(f"main.bean", encoding="utf8").read().find(newline) == -1:
            open(f"main.bean", "a", encoding="utf8").write(newline)

    if os.path.exists(f"{datapath}/{year}/{month}"):
        opt = input("Directory already exists, remove it? (y/N):")
        if opt.lower() != "y":
            exit(0)
        shutil.rmtree(f"{datapath}/{year}/{month}")
    os.makedirs(f"{datapath}/{year}/{month}")

    open(f"{datapath}/{year}/{month}/_.bean", "w").write(template)
    open(f"{datapath}/{year}/{month}/total.bean", "w")
    open(f"{datapath}/{year}/{month}/others.bean", "w")
    # balance_file = open(f"{datapath}/balance.bean", "w")

    if not os.path.exists(f"{datapath}/balance.bean"):
        open(f"{datapath}/balance.bean", "w").close()
    balance_file = open(f"{datapath}/balance.bean", "a", encoding="utf-8")
    
    newline = f'include "{month}/_.bean"\n'
    if open(f"{datapath}/{year}/_.bean").read().find(newline) == -1:
        open(f"{datapath}/{year}/_.bean", "a").write(newline)

    input("Create done, press Enter to import...")
    os.system(
        f"bean-extract beancount_config.py {rawdatapath} -- {datapath}/{year}/{month}/total.bean"
    )

    print("Input balance")
    for account in Config["balance_accounts"]:
        balance = input(f"{account}: ")
        balance_file.write(f"{year if int(month) < 12 else str(int(year)+1)}-{str(1 if int(month) == 12 else (int(month)+1)).rjust(2, '0')}-01 balance {account} {balance} CNY\n")
    balance_file.close()

    input("Import done, press Enter to archive...")
    os.system(f"bean-file -o {archivepath} beancount_config.py {rawdatapath}")

    print("All done!")
