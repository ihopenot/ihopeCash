"""
FastAPI 主应用 - IhopeCash Web 界面
"""

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import datetime
import sys
import os

# 添加父目录到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from web.auth import (
    verify_password, 
    create_jwt_token, 
    get_current_user,
    verify_ws_token
)
from web.tasks import task_manager

# 创建 FastAPI 应用
app = FastAPI(
    title="IhopeCash Web",
    description="IhopeCash 账单导入 Web 界面",
    version="1.0.0"
)

# 加载配置
config = Config()

# 配置验证 - 启动时检查默认值
warnings = config.validate_web_config()
if warnings:
    print("\n⚠️  配置警告:")
    for warning in warnings:
        print(f"  - {warning}")
    print()

# 挂载静态文件
app.mount("/static", StaticFiles(directory="web/static"), name="static")


# ==================== 数据模型 ====================

class LoginRequest(BaseModel):
    """登录请求"""
    password: str


class ImportRequest(BaseModel):
    """导入请求"""
    year: str
    month: str
    mode: str  # "normal", "force", "append"
    balances: Dict[str, str]


# ==================== API 端点 ====================

@app.get("/")
async def root():
    """根路径 - 返回主页面"""
    return FileResponse("web/static/index.html")


@app.get("/login")
async def login_page():
    """登录页面"""
    return FileResponse("web/static/login.html")


@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """登录端点 - 验证密码并返回 JWT token
    
    Args:
        request: 登录请求（包含密码）
        
    Returns:
        包含 token 和过期时间的字典
    """
    # 验证密码
    if not verify_password(request.password, config):
        raise HTTPException(status_code=401, detail="密码错误")
    
    # 生成 token
    token_data = create_jwt_token(config)
    
    return {
        "success": True,
        **token_data
    }


@app.get("/api/config")
async def get_config(user: dict = Depends(get_current_user)):
    """获取配置信息
    
    需要认证
    
    Returns:
        配置信息（余额账户列表、默认年月）
    """
    # 计算默认年月（上个月）
    now = datetime.datetime.now()
    if now.month == 1:
        default_year = now.year - 1
        default_month = 12
    else:
        default_year = now.year
        default_month = now.month - 1
    
    return {
        "balance_accounts": config.balance_accounts,
        "default_year": default_year,
        "default_month": default_month
    }


@app.post("/api/import")
async def start_import(
    request: ImportRequest,
    user: dict = Depends(get_current_user)
):
    """启动导入任务
    
    需要认证
    
    Args:
        request: 导入请求
        
    Returns:
        任务 ID
    """
    # 验证模式
    if request.mode not in ["normal", "force", "append"]:
        raise HTTPException(status_code=400, detail="无效的导入模式")
    
    # 创建任务
    task_id = await task_manager.create_task(
        year=request.year,
        month=request.month,
        balances=request.balances,
        mode=request.mode
    )
    
    return {
        "success": True,
        "task_id": task_id,
        "message": "导入任务已启动"
    }


@app.websocket("/ws/progress")
async def websocket_progress(websocket: WebSocket, token: str = None):
    """WebSocket 端点 - 实时推送导入进度
    
    需要认证（通过查询参数 token）
    
    Args:
        websocket: WebSocket 连接
        token: JWT token（查询参数）
    """
    # 验证 token
    try:
        verify_ws_token(token)
    except HTTPException:
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    # 接受连接
    await websocket.accept()
    
    # 等待客户端发送 task_id
    try:
        data = await websocket.receive_json()
        task_id = data.get("task_id")
        
        if not task_id:
            await websocket.close(code=1008, reason="Missing task_id")
            return
        
        # 添加到连接池
        await task_manager.add_websocket(task_id, websocket)
        
        # 发送历史进度（如果有）
        task_status = task_manager.get_task_status(task_id)
        if task_status.get("progress"):
            for progress in task_status["progress"]:
                await websocket.send_json(progress)
        
        # 保持连接，等待消息或断开
        while True:
            # 接收消息（用于心跳或其他命令）
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # 清理连接
        if 'task_id' in locals():
            await task_manager.remove_websocket(task_id, websocket)


# ==================== CORS 中间件（可选）====================

# 如果需要跨域访问，取消注释以下代码
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # 生产环境应该限制具体域名
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# ==================== 启动配置 ====================

if __name__ == "__main__":
    import uvicorn
    
    print(f"🚀 启动 IhopeCash Web 服务")
    print(f"   监听地址: {config.web_host}:{config.web_port}")
    print(f"   访问地址: http://localhost:{config.web_port}")
    print()
    
    uvicorn.run(
        "app:app",
        host=config.web_host,
        port=config.web_port,
        workers=1,  # 单进程，避免文件操作冲突
        reload=False
    )
