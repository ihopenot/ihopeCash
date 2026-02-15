"""
Backend module for IhopeCash - 账单管理后端模块

提供核心类:
- BillManager: 账单业务操作
"""

import os
import subprocess
import shutil
from typing import Dict, Any, Optional, Callable
from config import Config

# 进度回调类型定义
ProgressCallback = Callable[[Dict[str, Any]], None]


class BillManager:
    """账单管理器 - 所有业务操作"""
    
    def __init__(self, config: Config):
        """初始化账单管理器
        
        Args:
            config: Config 实例
        """
        self.config = config
        self.data_path = config.data_path
        self.rawdata_path = config.rawdata_path
        self.archive_path = config.archive_path
    
    def bean_identify(self) -> str:
        """识别文件类型
        
        Returns:
            命令输出
            
        Raises:
            Exception: 命令执行失败
        """
        result = subprocess.run(
            ["bean-identify", "beancount_config.py", self.rawdata_path],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise Exception(f"bean-identify 失败: {result.stderr}")
        return result.stdout
    
    def bean_extract(self, output_file: str) -> str:
        """提取交易到指定文件
        
        Args:
            output_file: 输出文件路径
            
        Returns:
            命令输出
            
        Raises:
            Exception: 命令执行失败
        """
        cmd = f"bean-extract beancount_config.py {self.rawdata_path} -- {output_file}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"bean-extract 失败: {result.stderr}")
        return result.stdout
    
    def bean_archive(self) -> str:
        """归档原始文件
        
        Returns:
            命令输出
            
        Raises:
            Exception: 命令执行失败
        """
        cmd = f"bean-file -o {self.archive_path} beancount_config.py {self.rawdata_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"bean-file 归档失败: {result.stderr}")
        return result.stdout
    
    def download_bills(self):
        """下载邮件账单
        
        Raises:
            Exception: 下载失败
        """
        try:
            from mail import DownloadFiles
            # 传入配置字典
            config_dict = self.config.to_dict()
            DownloadFiles(config_dict)
        except Exception as e:
            raise Exception(f"下载账单失败: {str(e)}")
    
    def ensure_year_directory(self, year: str) -> str:
        """确保年份目录存在并正确配置
        
        Args:
            year: 年份
            
        Returns:
            年份目录路径
        """
        year_path = f"{self.data_path}/{year}"
        
        if not os.path.exists(year_path):
            os.makedirs(year_path)
            # 创建年份 _.bean 文件
            open(f"{year_path}/_.bean", "w").write("\n")
            
            # 更新 data/main.bean
            main_bean_path = f"{self.data_path}/main.bean"
            newline = f'include "{year}/_.bean"\n'
            main_content = open(main_bean_path, encoding="utf8").read()
            if newline not in main_content:
                open(main_bean_path, "a", encoding="utf8").write(newline)
        
        return year_path
    
    def month_directory_exists(self, year: str, month: str) -> bool:
        """检查月份目录是否存在
        
        Args:
            year: 年份
            month: 月份
            
        Returns:
            是否存在
        """
        return os.path.exists(f"{self.data_path}/{year}/{month}")
    
    def create_month_directory(self, year: str, month: str, remove_if_exists: bool = False) -> str:
        """创建月份目录结构
        
        Args:
            year: 年份
            month: 月份
            remove_if_exists: 如果目录已存在是否删除重建
            
        Returns:
            月份目录路径
            
        Raises:
            FileExistsError: 目录已存在且 remove_if_exists=False
        """
        # 确保年份目录存在
        year_path = self.ensure_year_directory(year)
        month_path = f"{year_path}/{month}"
        
        # 处理已存在的情况
        if os.path.exists(month_path):
            if remove_if_exists:
                shutil.rmtree(month_path)
            else:
                raise FileExistsError(f"目录 {month_path} 已存在")
        
        # 创建月份目录
        os.makedirs(month_path)
        
        # 创建 bean 文件
        template = """include "others.bean"
include "total.bean"
"""
        open(f"{month_path}/_.bean", "w").write(template)
        open(f"{month_path}/total.bean", "w").close()
        open(f"{month_path}/others.bean", "w").close()
        
        # 更新年份 _.bean
        newline = f'include "{month}/_.bean"\n'
        year_bean_path = f"{year_path}/_.bean"
        year_bean_content = open(year_bean_path).read()
        if newline not in year_bean_content:
            open(year_bean_path, "a").write(newline)
        
        return month_path
    
    def record_balances(self, year: str, month: str, balances: Dict[str, str]):
        """记录余额断言
        
        Args:
            year: 年份
            month: 月份
            balances: 账户余额字典 {"账户名": "金额"}
        """
        balance_file = f"{self.data_path}/balance.bean"
        
        # 确保文件存在
        if not os.path.exists(balance_file):
            open(balance_file, "w").close()
        
        # 计算断言日期 (下个月1号)
        next_year = year if int(month) < 12 else str(int(year) + 1)
        next_month = str(1 if int(month) == 12 else (int(month) + 1)).rjust(2, '0')
        
        # 写入余额
        with open(balance_file, "a", encoding="utf-8") as f:
            for account, balance in balances.items():
                f.write(f"{next_year}-{next_month}-01 balance {account} {balance} CNY\n")
    
    def import_month(self, year: str, month: str, balances: Dict[str, str],
                    download: bool = True, force_overwrite: bool = False) -> Dict:
        """完整的月度导入流程
        
        Args:
            year: 年份
            month: 月份
            balances: 账户余额字典
            download: 是否下载邮件
            force_overwrite: 是否覆盖已存在目录
            
        Returns:
            {"success": bool, "message": str, "data": dict}
        """
        try:
            # 1. 下载
            if download:
                self.download_bills()
            
            # 2. 识别
            self.bean_identify()
            
            # 3. 创建目录
            month_path = self.create_month_directory(year, month, force_overwrite)
            
            # 4. 提取交易
            self.bean_extract(f"{month_path}/total.bean")
            
            # 5. 记录余额
            self.record_balances(year, month, balances)
            
            # 6. 归档
            self.bean_archive()
            
            return {
                "success": True,
                "message": "导入完成",
                "data": {
                    "year": year,
                    "month": month,
                    "path": month_path
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "data": None
            }
    
    def import_month_with_progress(
        self, 
        year: str, 
        month: str, 
        balances: Dict[str, str],
        mode: str,  # "normal", "force", "append"
        progress_callback: Optional[ProgressCallback] = None
    ) -> Dict:
        """带进度回调的完整导入流程
        
        Args:
            year: 年份
            month: 月份
            balances: 账户余额字典
            mode: 导入模式 ("normal", "force", "append")
            progress_callback: 进度回调函数
            
        Returns:
            {"success": bool, "message": str, "data": dict}
        """
        def send_progress(step: int, step_name: str, status: str, message: str, details: Optional[Dict] = None):
            """发送进度消息"""
            if progress_callback:
                progress_callback({
                    "step": step,
                    "total": 6,
                    "step_name": step_name,
                    "status": status,
                    "message": message,
                    "details": details or {}
                })
        
        try:
            # 1. 下载邮件账单
            send_progress(1, "download", "running", "正在下载邮件账单...")
            self.download_bills()
            # 统计下载的文件数
            import glob
            files_count = len(glob.glob(f"{self.rawdata_path}/*"))
            send_progress(1, "download", "success", f"邮件下载完成，共 {files_count} 个文件", {"files_count": files_count})
            
            # 2. 识别文件类型
            send_progress(2, "identify", "running", "正在识别文件类型...")
            identify_output = self.bean_identify()
            send_progress(2, "identify", "success", "文件识别完成", {"output": identify_output})
            
            # 3. 创建目录或追加文件
            if mode == "append":
                send_progress(3, "append_file", "running", "正在创建追加文件...")
                # 检查目录是否存在
                if not self.month_directory_exists(year, month):
                    raise Exception(f"目录 {self.data_path}/{year}/{month} 不存在，无法追加")
                
                # 生成时间戳文件名
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                append_name = f"append_{timestamp}"
                append_file = f"{self.data_path}/{year}/{month}/{append_name}.bean"
                open(append_file, "w").close()
                
                # 更新 _.bean
                folder_bean = f"{self.data_path}/{year}/{month}/_.bean"
                include_line = f'include "{append_name}.bean"\n'
                with open(folder_bean, "a") as f:
                    f.write(include_line)
                
                month_path = f"{self.data_path}/{year}/{month}"
                extract_target = append_file
                send_progress(3, "append_file", "success", f"追加文件创建完成: {append_name}.bean")
            else:
                send_progress(3, "create_dir", "running", "正在创建目录结构...")
                force_overwrite = (mode == "force")
                month_path = self.create_month_directory(year, month, force_overwrite)
                extract_target = f"{month_path}/total.bean"
                send_progress(3, "create_dir", "success", f"目录创建完成: {month_path}")
            
            # 4. 提取交易记录
            send_progress(4, "extract", "running", "正在提取交易记录...")
            self.bean_extract(extract_target)
            send_progress(4, "extract", "success", "交易提取完成")
            
            # 5. 记录余额断言
            send_progress(5, "balance", "running", "正在记录余额断言...")
            self.record_balances(year, month, balances)
            send_progress(5, "balance", "success", f"余额记录完成，共 {len(balances)} 个账户")
            
            # 6. 归档原始文件
            send_progress(6, "archive", "running", "正在归档原始文件...")
            self.bean_archive()
            send_progress(6, "archive", "success", "归档完成")
            
            return {
                "success": True,
                "message": "导入完成",
                "data": {
                    "year": year,
                    "month": month,
                    "path": month_path,
                    "mode": mode
                }
            }
            
        except Exception as e:
            # 发送错误消息
            send_progress(0, "error", "error", str(e))
            return {
                "success": False,
                "message": str(e),
                "data": None
            }
    
    def append_to_month(self, folder: str, name: str = "append") -> Dict:
        """追加模式 - 向已存在月份追加交易
        
        Args:
            folder: 目标目录,如 "2024/12"
            name: 追加文件名,默认 "append"
            
        Returns:
            {"success": bool, "message": str, "data": dict}
        """
        try:
            # 创建追加文件
            append_file = f"{self.data_path}/{folder}/{name}.bean"
            open(append_file, "w").close()
            
            # 更新 _.bean
            folder_bean = f"{self.data_path}/{folder}/_.bean"
            include_line = f'include "{name}.bean"\n'
            open(folder_bean, "a").write(include_line)
            
            # 提取和归档
            self.bean_extract(append_file)
            self.bean_archive()
            
            return {
                "success": True,
                "message": "追加完成",
                "data": {"file": append_file}
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "data": None
            }
    
    def import_append_mode(
        self,
        year: str,
        month: str,
        balances: Dict[str, str],
        progress_callback: Optional[ProgressCallback] = None
    ) -> Dict:
        """追加模式 - 完整流程包括下载
        
        这是 import_month_with_progress(mode="append") 的便捷封装
        
        Args:
            year: 年份
            month: 月份
            balances: 账户余额字典
            progress_callback: 进度回调函数
            
        Returns:
            {"success": bool, "message": str, "data": dict}
        """
        return self.import_month_with_progress(
            year=year,
            month=month,
            balances=balances,
            mode="append",
            progress_callback=progress_callback
        )
