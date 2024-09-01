import os
import shutil
import zipfile
import fitz
import pandas as pd
from config import Config

datapath = "data"
rawdatapath = "rawdata"
archivepath = "archive"

template = """include "others.bean"
include "total.bean"
"""

def decrypt_rawdata(remove_origin=True):
    for filename in os.listdir(rawdatapath):
        filepath = os.path.join(rawdatapath, filename)
        
        # 获取文件名（不包含后缀）
        file_basename = os.path.splitext(filename)[0]
        
        # 如果是.zip文件，尝试解压
        if filename.endswith('.zip'):
            try:
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    for zip_info in zip_ref.infolist():
                        if zip_info.filename.endswith('.csv'):
                            extracted_path = os.path.join(rawdatapath, os.path.basename(zip_info.filename))
                            with zip_ref.open(zip_info, pwd=file_basename.encode()) as source, open(extracted_path, 'wb') as target:
                                target.write(source.read())
                print(f'Successfully extracted .csv files from {filename}')
                if remove_origin:
                    os.remove(filepath)
            except Exception as e:
                print(f'Failed to extract .csv files from {filename}: {e}')
        
        # 如果是.pdf文件，尝试解密
        elif filename.endswith('.pdf'):
            try:
                is_encrypted = False
                with fitz.open(filepath) as doc:
                    if doc.is_encrypted:
                        is_encrypted = True
                        doc.authenticate(file_basename)
                        if doc.is_encrypted:
                            raise Exception('Failed to decrypt')
                        decrypted_filepath = os.path.join(rawdatapath, f'decrypted_{filename}')
                        doc.save(decrypted_filepath)
                        print(f'Successfully decrypted {filename}')
                if remove_origin and is_encrypted:
                    os.remove(filepath)
            except Exception as e:
                print(f'Failed to decrypt {filename}: {e}')
        if filename.endswith('.xls'):
            try:
                # 读取 .xls 文件并转换为 .csv 文件
                xls_df = pd.read_excel(filepath)
                extracted_path = os.path.join(rawdatapath, file_basename) + ".csv"
                xls_df.to_csv(extracted_path, index=False)
                print(f'Successfully converted {filename} to .csv')
                if remove_origin:
                    os.remove(filepath)
            except Exception as e:
                print(f'Failed to convert {filename} to .csv: {e}')

if __name__ == "__main__":
    opt = input("Decrypting rawdata, Do you want to remove the original files? (Y/n)")
    rm_ori = False if len(opt) > 0 and opt[0].lower() == 'n' else True
    decrypt_rawdata(rm_ori)
    input("decryption done, press Enter to continue...")

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
        others.write(f"{year}-{str(month+1).rjust(2, "0")}-01 balance {account} {balance} CNY\n")
    others.close()

    input("Import done, press Enter to archive...")
    os.system(f"bean-file -o {archivepath} config.py {rawdatapath}")

    print("All done!")
