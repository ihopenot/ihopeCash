import os, io, re, fitz, pyzipper
import requests
import imaplib
import email
from email.header import decode_header
from typing import List, Tuple, Dict, Any
import pandas as pd
import itertools

def decode_str(s):
    val, encoding = decode_header(s)[0]
    if encoding:
        val = val.decode(encoding)
    return val

class BaseEmailHanlder:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config
    
    def init(self, config):
        self.config = config
    
    # we already filtered the email on the server side
    def is_match(self, msg):
        raise NotImplementedError
    
    def get_data(self, msg) -> Tuple[str, bytes]:
        for part in msg.walk():
            file_name = part.get_filename()
            if file_name:
                name = decode_str(file_name)
                data = part.get_payload(decode=True)
                return name, data
    
    def post_process(self, name: str, data: bytes) -> Tuple[str, bytes]:
        return name, data
    
    def savebill(self, name: str, data: bytes):
        rawdata_path = self.config.get("rawdata_path", "rawdata") if self.config else "rawdata"
        with open(os.path.join(rawdata_path, name), "wb") as f:
            f.write(data)
    
    # just download the attachment
    def process(self, msg):
        if self.is_match(msg):
            name, data = self.get_data(msg)
            name, data = self.post_process(name, data)
            print(name)
            self.savebill(name, data)


def decrypt_zip(data, password_itr, extract_suffix=".csv", zipfile_cls=pyzipper.ZipFile, config_passwords=None):
    with zipfile_cls(io.BytesIO(data)) as zip_ref:
        for zip_info in zip_ref.infolist():
            if "/" in zip_info.filename:
                ret_name = zip_info.filename.split("/")[1]
            else:
                ret_name = zip_info.filename

            print(ret_name)
            if zip_info.filename.endswith(extract_suffix):
                # 优先使用配置中的密码
                passwords = config_passwords if config_passwords else []
                for password in passwords:
                    try:
                        with zip_ref.open(zip_info, pwd=password.encode()) as source:
                            data = source.read()
                            print(f'Successfully extracted .csv files from {password.encode()}')
                            return ret_name, data
                    except Exception as e:
                        pass

                for password in password_itr:
                    try:
                        with zip_ref.open(zip_info, pwd=bytes(password)) as source:
                            data = source.read()
                            print(f'Successfully extracted .csv files from {bytes(password)}')
                            return ret_name, data
                    except Exception as e:
                        pass
    return None


class WeChatEmailHandler(BaseEmailHanlder):
    reg_download_url = re.compile(r'"(https://tenpay.wechatpay.cn/userroll/userbilldownload/downloadfilefromemail\?.*?)"')
    password_itr = itertools.product(b"1234567890", repeat=6)

    def is_match(self, msg):
        subject = decode_str(msg["Subject"])
        return "微信支付" in subject

    def get_data(self, msg) -> Tuple[str, bytes]:
        for part in msg.walk():
            file_name = part.get_filename()
            if not file_name and not part.is_multipart():
                download_urls = self.reg_download_url.findall(part.get_payload(decode=True).decode("utf-8"))
                if len(download_urls) > 0:
                    r = requests.get(download_urls[0])
                    return "wechat.zip", r.content
        raise Exception("No download URL found in the email")
    
    def post_process(self, name: str, data: bytes) -> Tuple[str, bytes]:
        config_passwords = self.config.get("passwords", []) if self.config else []
        name, xlsfile = decrypt_zip(data, self.password_itr, ".xlsx", pyzipper.AESZipFile, config_passwords)
        xls_df = pd.read_excel(io.BytesIO(xlsfile))
        name = os.path.splitext(name)[0] + ".csv"
        return name, xls_df.to_csv(None, index=False).encode()
        # return decrypt_zip(data, self.password_itr)



class AlipayEmailHandler(BaseEmailHanlder):
    password_itr = itertools.product(b"1234567890", repeat=6)

    def is_match(self, msg):
        subject = decode_str(msg["Subject"])
        return "支付宝交易流水明细" in subject

    def post_process(self, name: str, data: bytes) -> Tuple[str, bytes]:
        config_passwords = self.config.get("passwords", []) if self.config else []
        return decrypt_zip(data, self.password_itr, config_passwords=config_passwords)


class BoCDebitEmailHandler(BaseEmailHanlder):
    password_itr = itertools.product("1234567890", repeat=6)

    def is_match(self, msg):
        subject = decode_str(msg["Subject"])
        return "中国银行交易流水" in subject

    def post_process(self, name: str, data: bytes) -> Tuple[str, bytes]:
        try:
            with fitz.open(stream=data, filetype="pdf") as doc:
                if doc.is_encrypted:
                    config_passwords = self.config.get("passwords", []) if self.config else []
                    for password in config_passwords:
                        doc.authenticate(password)
                        if not doc.is_encrypted:
                            break
                    if doc.is_encrypted:
                        for password in self.password_itr:
                            doc.authenticate("".join(password))
                            if not doc.is_encrypted:
                                break
                    if doc.is_encrypted:
                        raise Exception('Failed to decrypt')
                    print(f'Successfully decrypted {name}')
                    return name, doc.tobytes()
        except Exception as e:
            print(e)

class CCBDebitEmailHandler(BaseEmailHanlder):
    password_itr = itertools.product(b"1234567890", repeat=6)

    def is_match(self, msg):
        subject = decode_str(msg["Subject"])
        return "中国建设银行个人活期账户交易明细" in subject

    def post_process(self, name: str, data: bytes) -> Tuple[str, bytes]:
        config_passwords = self.config.get("passwords", []) if self.config else []
        name, xlsfile = decrypt_zip(data, self.password_itr, ".xls", pyzipper.AESZipFile, config_passwords)
        xls_df = pd.read_excel(io.BytesIO(xlsfile))
        name = os.path.splitext(name)[0] + ".csv"
        return name, xls_df.to_csv(None, index=False).encode()

def DownloadFiles(config: Dict[str, Any] = None):
    """下载邮件账单
    
    Args:
        config: 配置字典,如果为 None 则尝试使用旧的 config.py
    """
    # 向后兼容:如果没有传入 config,尝试加载旧的配置
    if config is None:
        try:
            from config import Config as OldConfig
            config = OldConfig
        except:
            raise Exception("需要提供 config 参数或确保 config.py 存在")
    
    # 初始化所有 handler 使用新配置
    handlers: List[BaseEmailHanlder] = [
        WeChatEmailHandler(config),
        AlipayEmailHandler(config),
        BoCDebitEmailHandler(config),
        CCBDebitEmailHandler(config),
    ]
    
    cfg = config["email"]["imap"]
    server = imaplib.IMAP4_SSL(cfg["host"], cfg["port"])
    server.login(cfg["username"], cfg["password"])

    # server.create("Bills")
    print(server.list())
    print(server.select(cfg["mailbox"]))
    _, mails = server.search(None, 'UNSEEN')
    print(mails)
    mails = mails[0].split()
    for mail in mails:
        _, data = server.fetch(mail, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])

        for handler in handlers:
            handler.process(msg)
        
        try:
            server.store(mail, '+FLAGS', '\\Seen')
        except Exception:
            server = imaplib.IMAP4_SSL(cfg["host"], cfg["port"])
            server.login(cfg["username"], cfg["password"])
            server.select(cfg["mailbox"])
            server.store(mail, '+FLAGS', '\\Seen')

    server.logout()


if __name__ == "__main__":
    DownloadFiles()
# decrypt_zip("rawdata/wechat.zip", itertools.product(b"1234567890", repeat=6))
# WeChatEmailHandler().post_process("wechat.zip", open("rawdata/wechat.zip", "rb").read())
# BoCDebitEmailHandler().post_process("KA020000001560066560001.pdf", open("rawdata/KA020000001560066560001.pdf", "rb").read())
# CCBDebitEmailHandler().post_process("hqmx_20240901131340.zip", open("rawdata/hqmx_20240901131340.zip", "rb").read())