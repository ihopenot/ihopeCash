"""
任务管理模块 - 异步导入任务和 WebSocket 连接管理
"""

import asyncio
import uuid
from typing import Dict, Any, Set
from fastapi import WebSocket
import sys
import os

# 添加父目录到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from backend import BillManager


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
            
            # 定义进度回调
            async def progress_callback(progress_data: Dict[str, Any]):
                """进度回调函数 - 广播到所有连接的 WebSocket"""
                # 添加 task_id
                progress_data["task_id"] = task_id
                
                # 保存进度到任务状态
                self.task_status[task_id]["progress"].append(progress_data)
                
                # 广播到所有 WebSocket 连接
                await self.broadcast_progress(task_id, progress_data)
            
            # 包装同步回调为异步
            def sync_progress_callback(progress_data: Dict[str, Any]):
                asyncio.create_task(progress_callback(progress_data))
            
            # 执行导入
            result = manager.import_month_with_progress(
                year=year,
                month=month,
                balances=balances,
                mode=mode,
                progress_callback=sync_progress_callback
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
                "total": 6,
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
