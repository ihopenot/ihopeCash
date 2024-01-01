import os
import shutil

datapath = "./data"
rawdatapath = "./rawdata"
archivepath = "./archive"

template = """include "others.bean"
include "total.bean"
"""

if __name__ == "__main__":
    year = input("Year: ")
    month = input("Month: ")

    os.system(f"bean-identify config.py {rawdatapath}")

    print(f"creating directory of {year}-{month}")
    input("Press Enter to comfirm...")

    if os.path.exists(f"{datapath}/{year}/{month}"):
        shutil.rmtree(f"{datapath}/{year}/{month}")
    os.makedirs(f"{datapath}/{year}/{month}")

    open(f"{datapath}/{year}/{month}/_.bean", "w").write(template)
    open(f"{datapath}/{year}/{month}/total.bean", "w")
    open(f"{datapath}/{year}/{month}/others.bean", "w")
    
    newline = f'include "{month}/_.bean"\n'
    if open(f"{datapath}/{year}/_.bean").read().find(newline) == -1:
        open(f"{datapath}/{year}/_.bean", "a").write(newline)

    input("Create done, press Enter to import...")
    os.system(
        f"bean-extract config.py {rawdatapath} -- {datapath}/{year}/{month}/total.bean"
    )

    input("Import done, press Enter to archive...")
    os.system(f"bean-file -o {archivepath} config.py {rawdatapath}")

    print("All done!")
