"""
Backend module for IhopeCash - 账单管理后端模块

提供核心类:
- BillManager: 账单业务操作
"""

import os
import glob
import logging
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from config import Config

logger = logging.getLogger(__name__)

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
        self.beancount_path = config.beancount_path
        self.data_path = config.data_path
        self.rawdata_path = config.rawdata_path
        self.archive_path = config.archive_path
    
    # ==================== Git 操作 ====================
    
    def _run_git(self, args: List[str]) -> subprocess.CompletedProcess:
        """执行 git 命令
        
        Args:
            args: git 子命令和参数列表，如 ["status", "--porcelain"]
            
        Returns:
            subprocess.CompletedProcess 结果
            
        Raises:
            RuntimeError: git 命令执行失败
        """
        cmd = ["git"] + args
        result = subprocess.run(
            cmd,
            cwd=self.beancount_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"git {args[0]} 失败: {result.stderr.strip()}")
        return result
    
    def git_ensure_repo(self):
        """检测并初始化 beancount git 仓库
        
        如果 beancount_path/.git 不存在，执行 git init，创建 .gitignore，并完成首次提交。
        
        Raises:
            RuntimeError: git 未安装或初始化失败
        """
        git_dir = os.path.join(self.beancount_path, ".git")
        if os.path.exists(git_dir):
            return
        
        # 检测 git 是否可用
        try:
            subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
        except FileNotFoundError:
            raise RuntimeError("未检测到 git 命令，请先安装 git")
        
        # git init
        self._run_git(["init"])
        
        # 设置 git 用户信息
        self._run_git(["config", "user.email", "ihopecash@local"])
        self._run_git(["config", "user.name", "ihopeCash"])
        
        # 创建 .gitignore
        gitignore_path = os.path.join(self.beancount_path, ".gitignore")
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write(".ledger-period\n")
        
        # 首次提交
        self._run_git(["add", "."])
        self._run_git(["commit", "-m", "初始化账本"])
    
    def git_is_clean(self) -> bool:
        """检查 beancount git 工作区是否干净
        
        Returns:
            True 表示工作区干净（无变更），False 表示有未提交变更。
            如果 beancount_path/.git 不存在，返回 True。
        """
        git_dir = os.path.join(self.beancount_path, ".git")
        if not os.path.exists(git_dir):
            return True
        
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.beancount_path,
            capture_output=True,
            text=True
        )
        return result.stdout.strip() == ""
    
    def git_commit_if_dirty(self, period: str):
        """有变更时自动提交
        
        Args:
            period: 账期，用于 commit message，如 "2026-01"
        """
        if self.git_is_clean():
            return
        
        self._run_git(["add", "."])
        self._run_git(["commit", "-m", f"账期 {period}"])
    
    def git_discard_changes(self):
        """丢弃所有未提交的工作区变更
        
        执行 git checkout -- . 恢复已跟踪文件，git clean -fd 删除未跟踪文件，
        并清除 .ledger-period 文件。
        """
        git_dir = os.path.join(self.beancount_path, ".git")
        if not os.path.exists(git_dir):
            return
        
        self._run_git(["checkout", "--", "."])
        self._run_git(["clean", "-fd"])
        self.clear_ledger_period()
    
    # ==================== 账期文件管理 ====================
    
    def read_ledger_period(self) -> Optional[str]:
        """读取当前账期
        
        Returns:
            账期字符串（如 "2026-02"），文件不存在时返回 None
        """
        period_file = os.path.join(self.data_path, ".ledger-period")
        if not os.path.exists(period_file):
            return None
        with open(period_file, "r", encoding="utf-8") as f:
            return f.read().strip() or None
    
    def write_ledger_period(self, period: str):
        """写入当前账期
        
        Args:
            period: 账期字符串，如 "2026-02"
        """
        period_file = os.path.join(self.data_path, ".ledger-period")
        with open(period_file, "w", encoding="utf-8") as f:
            f.write(period)
    
    def clear_ledger_period(self):
        """清除账期文件"""
        period_file = os.path.join(self.data_path, ".ledger-period")
        if os.path.exists(period_file):
            os.remove(period_file)
    
    # ==================== Beancount 命令封装 ====================
    
    def bean_identify(self) -> str:
        """识别文件类型
        
        Returns:
            命令输出
            
        Raises:
            RuntimeError: 命令执行失败
        """
        result = subprocess.run(
            ["bean-identify", "beancount_config.py", self.rawdata_path],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"bean-identify 失败: {result.stderr}")
        return result.stdout
    
    def bean_extract(self, output_file: str) -> str:
        """提取交易到指定文件
        
        Args:
            output_file: 输出文件路径
            
        Returns:
            命令输出
            
        Raises:
            RuntimeError: 命令执行失败
        """
        result = subprocess.run(
            ["bean-extract", "beancount_config.py", self.rawdata_path, "--", output_file],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"bean-extract 失败: {result.stderr}")
        return result.stdout
    
    def bean_archive(self) -> str:
        """归档原始文件
        
        Returns:
            命令输出
            
        Raises:
            RuntimeError: 命令执行失败
        """
        result = subprocess.run(
            ["bean-file", "-o", self.archive_path, "beancount_config.py", self.rawdata_path],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"bean-file 归档失败: {result.stderr}")
        return result.stdout
    
    def download_bills(self, passwords=None):
        """下载邮件账单
        
        Args:
            passwords: 密码列表，默认为 None
        
        Raises:
            RuntimeError: 下载失败
        """
        if passwords is None:
            passwords = []
        try:
            from mail import DownloadFiles
            # 传入配置字典
            config_dict = self.config.to_dict()
            config_dict["passwords"] = passwords
            # 确保 rawdata 和 archive 目录存在
            os.makedirs(config_dict.get("rawdata_path", self.rawdata_path), exist_ok=True)
            os.makedirs(config_dict.get("archive_path", self.archive_path), exist_ok=True)
            DownloadFiles(config_dict)
        except Exception as e:
            logger.exception("下载账单失败")
            raise RuntimeError(f"下载账单失败: {str(e)}") from e
    
    def ensure_year_directory(self, year: str) -> str:
        """确保年份目录存在并正确配置
        
        Args:
            year: 年份
            
        Returns:
            年份目录路径
        """
        year_path = os.path.join(self.data_path, year)
        
        if not os.path.exists(year_path):
            os.makedirs(year_path)
            # 创建年份 _.bean 文件
            with open(os.path.join(year_path, "_.bean"), "w") as f:
                f.write("\n")
            
            # 更新 data/main.bean
            main_bean_path = os.path.join(self.data_path, "main.bean")
            newline = f'include "{year}/_.bean"\n'
            with open(main_bean_path, encoding="utf8") as f:
                main_content = f.read()
            if newline not in main_content:
                with open(main_bean_path, "a", encoding="utf8") as f:
                    f.write(newline)
        
        return year_path
    
    def month_directory_exists(self, year: str, month: str) -> bool:
        """检查月份目录是否存在
        
        Args:
            year: 年份
            month: 月份
            
        Returns:
            是否存在
        """
        return os.path.exists(os.path.join(self.data_path, year, month))
    
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
        month_path = os.path.join(year_path, month)
        
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
        with open(os.path.join(month_path, "_.bean"), "w") as f:
            f.write(template)
        Path(os.path.join(month_path, "total.bean")).touch()
        Path(os.path.join(month_path, "others.bean")).touch()
        
        # 更新年份 _.bean
        newline = f'include "{month}/_.bean"\n'
        year_bean_path = os.path.join(year_path, "_.bean")
        with open(year_bean_path) as f:
            year_bean_content = f.read()
        if newline not in year_bean_content:
            with open(year_bean_path, "a") as f:
                f.write(newline)
        
        return month_path
    
    def record_balances(self, year: str, month: str, balances: Dict[str, str]):
        """记录余额断言到对应账期的 others.bean
        
        Args:
            year: 年份
            month: 月份
            balances: 账户余额字典 {"账户名": "金额"}
        """
        others_file = os.path.join(self.data_path, year, month, "others.bean")
        
        # 确保目录和文件存在
        os.makedirs(os.path.dirname(others_file), exist_ok=True)
        if not os.path.exists(others_file):
            Path(others_file).touch()
        
        # 计算断言日期 (下个月1号)
        next_year = year if int(month) < 12 else str(int(year) + 1)
        next_month = str(1 if int(month) == 12 else (int(month) + 1)).rjust(2, '0')
        
        # 追加写入余额
        with open(others_file, "a", encoding="utf-8") as f:
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
            self.bean_extract(os.path.join(month_path, "total.bean"))
            
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
            logger.exception("月度导入失败")
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
        passwords: List[str],
        progress_callback: Optional[ProgressCallback] = None
    ) -> Dict:
        """带进度回调的完整导入流程
        
        Args:
            year: 年份
            month: 月份
            balances: 账户余额字典
            mode: 导入模式 ("normal", "force", "append")
            passwords: 密码列表
            progress_callback: 进度回调函数
            
        Returns:
            {"success": bool, "message": str, "data": dict}
        """
        def send_progress(step: int, step_name: str, status: str, message: str, details: Optional[Dict] = None):
            """发送进度消息"""
            if progress_callback:
                progress_callback({
                    "step": step,
                    "total": 7,
                    "step_name": step_name,
                    "status": status,
                    "message": message,
                    "details": details or {}
                })
        
        try:
            # 1. Git 提交上期变更
            send_progress(1, "git_commit", "running", "正在检查版本管理状态...")
            git_dir = os.path.join(self.beancount_path, ".git")
            if not os.path.exists(git_dir):
                send_progress(1, "git_commit", "running", "正在初始化版本管理...")
                self.git_ensure_repo()
                send_progress(1, "git_commit", "success", "版本管理初始化完成")
            elif not self.git_is_clean():
                send_progress(1, "git_commit", "running", "正在提交上期变更...")
                prev_period = self.read_ledger_period() or "未知账期"
                self.git_commit_if_dirty(prev_period)
                self.clear_ledger_period()
                send_progress(1, "git_commit", "success", f"上期变更已提交（{prev_period}）")
            else:
                send_progress(1, "git_commit", "success", "无待提交的变更，跳过")
            
            # 2. 下载邮件账单
            send_progress(2, "download", "running", "正在下载邮件账单（如需暴力破解密码可能耗时较长）...")
            self.download_bills(passwords)
            files_count = len(glob.glob(os.path.join(self.rawdata_path, "*")))
            send_progress(2, "download", "success", f"邮件下载完成，共 {files_count} 个文件", {"files_count": files_count})
            
            # 3. 识别文件类型
            send_progress(3, "identify", "running", "正在识别文件类型...")
            identify_output = self.bean_identify()
            send_progress(3, "identify", "success", "文件识别完成", {"output": identify_output})
            
            # 4. 创建目录或追加文件
            if mode == "append":
                send_progress(4, "append_file", "running", "正在创建追加文件...")
                if not self.month_directory_exists(year, month):
                    raise RuntimeError(f"目录 {os.path.join(self.data_path, year, month)} 不存在，无法追加")
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                append_name = f"append_{timestamp}"
                append_file = os.path.join(self.data_path, year, month, f"{append_name}.bean")
                Path(append_file).touch()
                
                folder_bean = os.path.join(self.data_path, year, month, "_.bean")
                include_line = f'include "{append_name}.bean"\n'
                with open(folder_bean, "a") as f:
                    f.write(include_line)
                
                month_path = os.path.join(self.data_path, year, month)
                extract_target = append_file
                send_progress(4, "append_file", "success", f"追加文件创建完成: {append_name}.bean")
            else:
                send_progress(4, "create_dir", "running", "正在创建目录结构...")
                force_overwrite = (mode == "force")
                month_path = self.create_month_directory(year, month, force_overwrite)
                extract_target = os.path.join(month_path, "total.bean")
                send_progress(4, "create_dir", "success", f"目录创建完成: {month_path}")
            
            # 5. 提取交易记录
            send_progress(5, "extract", "running", "正在提取交易记录...")
            self.bean_extract(extract_target)
            send_progress(5, "extract", "success", "交易提取完成")
            
            # 6. 记录余额断言
            send_progress(6, "balance", "running", "正在记录余额断言...")
            self.record_balances(year, month, balances)
            send_progress(6, "balance", "success", f"余额记录完成，共 {len(balances)} 个账户")
            
            # 7. 归档原始文件
            send_progress(7, "archive", "running", "正在归档原始文件...")
            self.bean_archive()
            send_progress(7, "archive", "success", "归档完成")
            
            # 写入本次账期
            period = f"{year}-{str(month).zfill(2)}"
            self.write_ledger_period(period)
            
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
            logger.exception("带进度导入失败")
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
            append_file = os.path.join(self.data_path, folder, f"{name}.bean")
            Path(append_file).touch()
            
            # 更新 _.bean
            folder_bean = os.path.join(self.data_path, folder, "_.bean")
            include_line = f'include "{name}.bean"\n'
            with open(folder_bean, "a") as f:
                f.write(include_line)
            
            # 提取和归档
            self.bean_extract(append_file)
            self.bean_archive()
            
            return {
                "success": True,
                "message": "追加完成",
                "data": {"file": append_file}
            }
            
        except Exception as e:
            logger.exception("追加模式失败")
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
        passwords: List[str] = None,
        progress_callback: Optional[ProgressCallback] = None
    ) -> Dict:
        """追加模式 - 完整流程包括下载
        
        这是 import_month_with_progress(mode="append") 的便捷封装
        
        Args:
            year: 年份
            month: 月份
            balances: 账户余额字典
            passwords: 密码列表
            progress_callback: 进度回调函数
            
        Returns:
            {"success": bool, "message": str, "data": dict}
        """
        if passwords is None:
            passwords = []
        return self.import_month_with_progress(
            year=year,
            month=month,
            balances=balances,
            mode="append",
            passwords=passwords,
            progress_callback=progress_callback
        )
