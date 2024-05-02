import os
import shutil
from china_bean_importers.config import balance_accounts

datapath = "data"
rawdatapath = "rawdata"
archivepath = "archive"

template = """include "others.bean"
include "total.bean"
"""

if __name__ == "__main__":
    year = input("Year: ")
    month = input("Month: ")

    os.system(f"bean-identify config.py {rawdatapath}")

    print(f"creating directory of {year}-{month}")
    input("Press Enter to comfirm...")

    if not os.path.exists(f"{datapath}/{year}"):
        os.makedirs(f"{datapath}/{year}")
        open(f"{datapath}/{year}/_.bean", "w").write("\n")
        newline = f'include "{datapath}/{year}/_.bean"\n'
        if open(f"main.bean").read().find(newline) == -1:
            open(f"main.bean", "a").write(newline)

    if os.path.exists(f"{datapath}/{year}/{month}"):
        shutil.rmtree(f"{datapath}/{year}/{month}")
    os.makedirs(f"{datapath}/{year}/{month}")

    open(f"{datapath}/{year}/{month}/_.bean", "w").write(template)
    open(f"{datapath}/{year}/{month}/total.bean", "w")
    others = open(f"{datapath}/{year}/{month}/others.bean", "w")
    
    newline = f'include "{month}/_.bean"\n'
    if open(f"{datapath}/{year}/_.bean").read().find(newline) == -1:
        open(f"{datapath}/{year}/_.bean", "a").write(newline)

    input("Create done, press Enter to import...")
    os.system(
        f"bean-extract config.py {rawdatapath} -- {datapath}/{year}/{month}/total.bean"
    )

    print("Input balance")
    for account in balance_accounts:
        balance = input(f"{account}: ")
        others.write(f"{year}-{month}-01 balance {account} {balance} CNY\n")
    others.close()

    input("Import done, press Enter to archive...")
    os.system(f"bean-file -o {archivepath} config.py {rawdatapath}")

    print("All done!")
