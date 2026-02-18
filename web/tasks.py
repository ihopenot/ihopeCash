"""
任务管理模块 - 异步导入任务和 WebSocket 连接管理
"""

import asyncio
import uuid
import functools
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Set
from fastapi import WebSocket
import sys
import os

# 添加父目录到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from backend import BillManager


# 线程池，用于运行同步的导入操作
_executor = ThreadPoolExecutor(max_workers=2)


class TaskManager:
    """任务管理器 - 管理导入任务和 WebSocket 连接"""
    
    def __init__(self):
        """初始化任务管理器"""
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_status: Dict[str, Dict[str, Any]] = {}
        self.websocket_connections: Dict[str, Set[WebSocket]] = {}  # task_id -> Set[WebSocket]
        self.lock = asyncio.Lock()
    
    async def create_task(
        self,
        year: str,
        month: str,
        balances: Dict[str, str],
        mode: str
    ) -> str:
        """创建新的导入任务
        
        Args:
            year: 年份
            month: 月份
            balances: 账户余额字典
            mode: 导入模式 (normal/force/append)
            
        Returns:
            task_id
        """
        task_id = str(uuid.uuid4())
        
        # 初始化任务状态
        self.task_status[task_id] = {
            "status": "pending",
            "year": year,
            "month": month,
            "mode": mode,
            "progress": []
        }
        
        # 初始化 WebSocket 连接集合
        self.websocket_connections[task_id] = set()
        
        # 创建异步任务
        task = asyncio.create_task(
            self._execute_import(task_id, year, month, balances, mode)
        )
        self.active_tasks[task_id] = task
        
        return task_id
    
    async def _execute_import(
        self,
        task_id: str,
        year: str,
        month: str,
        balances: Dict[str, str],
        mode: str
    ):
        """执行导入任务（在后台运行）
        
        将同步的 import_month_with_progress 放到线程池执行，
        避免阻塞事件循环，使 WebSocket 消息能实时推送。
        
        Args:
            task_id: 任务 ID
            year: 年份
            month: 月份
            balances: 账户余额字典
            mode: 导入模式
        """
        try:
            # 更新状态为运行中
            self.task_status[task_id]["status"] = "running"
            
            # 创建配置和管理器
            config = Config()
            manager = BillManager(config)
            
            # 获取事件循环引用（在主线程中）
            loop = asyncio.get_running_loop()
            
            # 定义线程安全的进度回调
            def thread_safe_progress_callback(progress_data: Dict[str, Any]):
                """从工作线程安全地发送进度到事件循环"""
                progress_data["task_id"] = task_id
                self.task_status[task_id]["progress"].append(progress_data)
                # 线程安全地提交协程到事件循环
                asyncio.run_coroutine_threadsafe(
                    self.broadcast_progress(task_id, progress_data),
                    loop
                )
            
            # 在线程池中执行同步导入
            result = await loop.run_in_executor(
                _executor,
                functools.partial(
                    manager.import_month_with_progress,
                    year=year,
                    month=month,
                    balances=balances,
                    mode=mode,
                    progress_callback=thread_safe_progress_callback
                )
            )
            
            # 更新最终状态
            if result["success"]:
                self.task_status[task_id]["status"] = "completed"
                self.task_status[task_id]["result"] = result
            else:
                self.task_status[task_id]["status"] = "failed"
                self.task_status[task_id]["error"] = result["message"]
            
        except Exception as e:
            self.task_status[task_id]["status"] = "failed"
            self.task_status[task_id]["error"] = str(e)
            
            # 广播错误消息
            await self.broadcast_progress(task_id, {
                "task_id": task_id,
                "step": 0,
                "total": 5,
                "step_name": "error",
                "status": "error",
                "message": str(e)
            })
        
        finally:
            # 清理任务
            async with self.lock:
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]
    
    async def add_websocket(self, task_id: str, websocket: WebSocket):
        """添加 WebSocket 连接到任务
        
        Args:
            task_id: 任务 ID
            websocket: WebSocket 连接
        """
        if task_id not in self.websocket_connections:
            self.websocket_connections[task_id] = set()
        
        self.websocket_connections[task_id].add(websocket)
    
    async def create_download_task(self, passwords: list = None) -> str:
        """创建邮件下载任务
        
        Args:
            passwords: 附件解压密码列表
            
        Returns:
            task_id
        """
        task_id = str(uuid.uuid4())
        
        self.task_status[task_id] = {
            "status": "pending",
            "type": "download",
            "progress": []
        }
        self.websocket_connections[task_id] = set()
        
        task = asyncio.create_task(
            self._execute_download(task_id, passwords or [])
        )
        self.active_tasks[task_id] = task
        
        return task_id
    
    async def _execute_download(self, task_id: str, passwords: list):
        """执行邮件下载任务"""
        import glob as glob_module
        
        try:
            self.task_status[task_id]["status"] = "running"
            
            config = Config()
            manager = BillManager(config)
            loop = asyncio.get_running_loop()
            
            def thread_safe_progress(progress_data):
                progress_data["task_id"] = task_id
                self.task_status[task_id]["progress"].append(progress_data)
                asyncio.run_coroutine_threadsafe(
                    self.broadcast_progress(task_id, progress_data),
                    loop
                )
            
            def do_download():
                thread_safe_progress({
                    "step": 1, "total": 1, "step_name": "download",
                    "status": "running", "message": "正在下载邮件账单...", "details": {}
                })
                try:
                    manager.download_bills(passwords)
                    files_count = len(glob_module.glob(os.path.join(manager.rawdata_path, "*")))
                    thread_safe_progress({
                        "step": 1, "total": 1, "step_name": "download",
                        "status": "success",
                        "message": f"邮件下载完成，共 {files_count} 个文件",
                        "details": {"files_count": files_count}
                    })
                except Exception as e:
                    thread_safe_progress({
                        "step": 1, "total": 1, "step_name": "download",
                        "status": "error", "message": str(e), "details": {}
                    })
                    raise
            
            await loop.run_in_executor(_executor, do_download)
            self.task_status[task_id]["status"] = "completed"
            
        except Exception as e:
            self.task_status[task_id]["status"] = "failed"
            self.task_status[task_id]["error"] = str(e)
        finally:
            async with self.lock:
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]
    
    async def create_archive_task(self, message: str) -> str:
        """创建归档任务
        
        Args:
            message: git commit 提交说明
            
        Returns:
            task_id
        """
        task_id = str(uuid.uuid4())
        
        self.task_status[task_id] = {
            "status": "pending",
            "type": "archive",
            "progress": []
        }
        self.websocket_connections[task_id] = set()
        
        task = asyncio.create_task(
            self._execute_archive(task_id, message)
        )
        self.active_tasks[task_id] = task
        
        return task_id
    
    async def _execute_archive(self, task_id: str, message: str):
        """执行归档任务"""
        try:
            self.task_status[task_id]["status"] = "running"
            
            config = Config()
            manager = BillManager(config)
            loop = asyncio.get_running_loop()
            
            def thread_safe_progress(progress_data):
                progress_data["task_id"] = task_id
                self.task_status[task_id]["progress"].append(progress_data)
                asyncio.run_coroutine_threadsafe(
                    self.broadcast_progress(task_id, progress_data),
                    loop
                )
            
            await loop.run_in_executor(
                _executor,
                functools.partial(
                    manager.archive_with_commit,
                    message=message,
                    progress_callback=thread_safe_progress
                )
            )
            self.task_status[task_id]["status"] = "completed"
            
        except Exception as e:
            self.task_status[task_id]["status"] = "failed"
            self.task_status[task_id]["error"] = str(e)
            await self.broadcast_progress(task_id, {
                "task_id": task_id,
                "step": 0, "total": 2, "step_name": "error",
                "status": "error", "message": str(e)
            })
        finally:
            async with self.lock:
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]
    
    async def remove_websocket(self, task_id: str, websocket: WebSocket):
        """移除 WebSocket 连接
        
        Args:
            task_id: 任务 ID
            websocket: WebSocket 连接
        """
        if task_id in self.websocket_connections:
            self.websocket_connections[task_id].discard(websocket)
    
    async def broadcast_progress(self, task_id: str, progress_data: Dict[str, Any]):
        """广播进度消息到所有连接的 WebSocket
        
        Args:
            task_id: 任务 ID
            progress_data: 进度数据
        """
        if task_id not in self.websocket_connections:
            return
        
        # 获取所有连接
        connections = list(self.websocket_connections[task_id])
        
        # 广播消息
        disconnected = []
        for ws in connections:
            try:
                await ws.send_json(progress_data)
            except Exception:
                # 连接已断开，标记删除
                disconnected.append(ws)
        
        # 清理断开的连接
        for ws in disconnected:
            await self.remove_websocket(task_id, ws)
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务状态字典
        """
        return self.task_status.get(task_id, {"status": "not_found"})


# 全局任务管理器实例
task_manager = TaskManager()
