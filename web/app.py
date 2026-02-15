"""
FastAPI 主应用 - IhopeCash Web 界面
"""

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import datetime
import re
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

if config.setup_required:
    print("📋 首次运行，需要完成配置引导")
    print()


# ==================== 引导拦截中间件 ====================

# 引导模式下允许通过的路径前缀
_SETUP_ALLOWED_PREFIXES = (
    "/login",
    "/api/auth/login",
    "/setup",
    "/api/setup/",
    "/api/ledger/accounts",
    "/static/",
)


@app.middleware("http")
async def check_setup_middleware(request: Request, call_next):
    """引导拦截中间件
    
    setup_required 为 True 时，仅允许引导相关路径通过，其他重定向到 /setup。
    setup_required 为 False 时，/setup 和 /api/setup/* 路径重定向到 / 或返回 403。
    """
    path = request.url.path
    
    if config.setup_required:
        # 引导模式：只允许特定路径
        allowed = any(path.startswith(prefix) for prefix in _SETUP_ALLOWED_PREFIXES)
        if not allowed:
            return RedirectResponse(url="/setup", status_code=302)
    else:
        # 正常模式：/setup 页面重定向到首页
        if path == "/setup":
            return RedirectResponse(url="/", status_code=302)
        # /api/setup/complete 在正常模式下返回 403
        if path == "/api/setup/complete":
            return JSONResponse(
                status_code=403,
                content={"detail": "配置引导已完成，无法再次执行"}
            )
    
    response = await call_next(request)
    return response


# ==================== 启动事件 ====================

def ensure_default_bean_files():
    """确保默认 bean 文件存在"""
    data_path = config.data_path
    os.makedirs(data_path, exist_ok=True)
    
    # data/main.bean
    main_bean = os.path.join(data_path, "main.bean")
    if not os.path.exists(main_bean):
        with open(main_bean, "w", encoding="utf-8") as f:
            f.write('option "title" "ihopeCash"\n')
            f.write('option "operating_currency" "CNY"\n')
            f.write('\n')
            f.write('include "accounts.bean"\n')
            f.write('include "balance.bean"\n')
        print(f"已创建默认文件: {main_bean}")
    
    # data/accounts.bean
    accounts_bean = os.path.join(data_path, "accounts.bean")
    if not os.path.exists(accounts_bean):
        open(accounts_bean, "w", encoding="utf-8").close()
        print(f"已创建默认文件: {accounts_bean}")
    
    # data/balance.bean
    balance_bean = os.path.join(data_path, "balance.bean")
    if not os.path.exists(balance_bean):
        open(balance_bean, "w", encoding="utf-8").close()
        print(f"已创建默认文件: {balance_bean}")


@app.on_event("startup")
async def startup_event():
    """应用启动时确保默认文件存在"""
    ensure_default_bean_files()


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
    passwords: List[str] = []


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    current_password: str
    new_password: str


class LedgerInfoRequest(BaseModel):
    """账本信息更新请求"""
    title: str
    operating_currency: str


class AddAccountRequest(BaseModel):
    """新增账户请求"""
    account_type: str  # Assets, Liabilities, Income, Expenses, Equity
    path: str  # 如 BoC:Card:1234
    currencies: str = ""  # 货币，留空支持所有货币
    comment: str = ""  # 备注


class CloseAccountRequest(BaseModel):
    """关闭账户请求"""
    account_name: str  # 完整账户名，如 Assets:BoC:Card:1234
    date: str = ""  # 关闭日期，留空默认当天


class SetupCompleteRequest(BaseModel):
    """引导完成请求"""
    config: Dict[str, Any]
    new_accounts: List[Dict[str, str]] = []


# ==================== 引导 API ====================

@app.get("/setup")
async def setup_page():
    """引导页面"""
    return FileResponse("web/static/setup.html")


@app.get("/api/setup/status")
async def get_setup_status():
    """获取引导状态（无需认证）
    
    Returns:
        { setup_required: bool }
    """
    return {"setup_required": config.setup_required}


@app.get("/api/setup/defaults")
async def get_setup_defaults(user: dict = Depends(get_current_user)):
    """获取引导默认配置（需认证）
    
    Returns:
        包含所有导入器和交易摘要过滤默认值的配置
    """
    return config.get_setup_defaults()


@app.post("/api/setup/complete")
async def complete_setup(
    request: SetupCompleteRequest,
    user: dict = Depends(get_current_user)
):
    """完成配置引导（需认证）
    
    一次性写入所有配置和新增账户。
    
    Args:
        request: 包含 config 和 new_accounts
        
    Returns:
        操作结果
    """
    if not config.setup_required:
        raise HTTPException(status_code=403, detail="配置引导已完成，无法再次执行")
    
    # 校验 new_accounts 中的账户名合法性
    for acc in request.new_accounts:
        account_type = acc.get("account_type", "")
        path = acc.get("path", "").strip()
        
        if account_type not in VALID_ACCOUNT_TYPES:
            raise HTTPException(status_code=400, detail=f"无效的账户类型: {account_type}")
        
        if not path:
            raise HTTPException(status_code=400, detail="账户路径不能为空")
        
        # 校验路径格式
        error = _validate_account_path(path)
        if error:
            raise HTTPException(status_code=400, detail=f"账户 {account_type}:{path} 格式错误: {error}")
    
    try:
        config.complete_setup(request.config, request.new_accounts)
        return {"success": True, "message": "配置完成"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配置写入失败: {str(e)}")


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
        mode=request.mode,
        passwords=request.passwords
    )
    
    return {
        "success": True,
        "task_id": task_id,
        "message": "导入任务已启动"
    }


@app.get("/config")
async def config_page():
    """配置页面"""
    return FileResponse("web/static/config.html")


@app.get("/api/config/full")
async def get_full_config(user: dict = Depends(get_current_user)):
    """获取完整可编辑配置（脱敏后）
    
    需要认证
    
    Returns:
        脱敏后的可编辑配置
    """
    return config.get_editable_config()


@app.put("/api/config/full")
async def update_full_config(
    data: Dict[str, Any],
    user: dict = Depends(get_current_user)
):
    """保存配置
    
    需要认证。后端强制跳过受保护字段。
    
    Args:
        data: 前端提交的配置数据
        
    Returns:
        操作结果
    """
    try:
        config.update_from_web(data)
        return {"success": True, "message": "配置已保存"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")


@app.post("/api/config/change-password")
async def change_password(
    request: ChangePasswordRequest,
    user: dict = Depends(get_current_user)
):
    """修改登录密码
    
    需要认证，需验证当前密码。
    
    Args:
        request: 修改密码请求
        
    Returns:
        操作结果
    """
    # 验证当前密码
    if not verify_password(request.current_password, config):
        raise HTTPException(status_code=400, detail="当前密码错误")
    
    # 验证新密码非空
    if not request.new_password.strip():
        raise HTTPException(status_code=400, detail="新密码不能为空")
    
    try:
        config.update_web_password(request.new_password)
        return {"success": True, "message": "密码已修改"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"修改密码失败: {str(e)}")


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


# ==================== 账本管理 API ====================

VALID_ACCOUNT_TYPES = ["Assets", "Liabilities", "Income", "Expenses", "Equity"]


def _get_main_bean_path() -> str:
    """获取 main.bean 路径"""
    return os.path.join(config.data_path, "main.bean")


def _get_accounts_bean_path() -> str:
    """获取 accounts.bean 路径"""
    return os.path.join(config.data_path, "accounts.bean")


def _validate_account_path(path: str) -> Optional[str]:
    """校验账户路径格式
    
    Args:
        path: 账户路径（不含类型前缀）
        
    Returns:
        错误信息，None 表示通过
    """
    if not path:
        return "账户路径不能为空"
    if path.startswith(":") or path.endswith(":"):
        return "路径格式不正确"
    if "::" in path:
        return "路径格式不正确"
    
    segments = path.split(":")
    first_segment = segments[0]
    if not re.match(r'^[A-Z0-9]', first_segment):
        return "账户路径的第一段必须以大写字母或数字开头"
    
    for i, segment in enumerate(segments[1:], start=2):
        if not segment:
            continue
        if re.match(r'^[a-z]', segment):
            return f"账户路径第{i}段 \"{segment}\" 不能以小写字母开头"
    
    return None


def _parse_ledger_info() -> dict:
    """使用 beancount.loader 解析账本信息
    
    Returns:
        {"title": str, "operating_currency": str}
    """
    from beancount import loader
    
    main_bean = _get_main_bean_path()
    entries, errors, options_map = loader.load_file(main_bean)
    
    return {
        "title": options_map.get("title", "ihopeCash"),
        "operating_currency": options_map.get("operating_currency", ["CNY"])[0] if options_map.get("operating_currency") else "CNY"
    }


def _parse_accounts() -> list:
    """使用 beancount.loader 解析所有账户
    
    Returns:
        账户列表，每个元素为 dict
    """
    from beancount import loader
    from beancount.core import data as beancount_data
    
    main_bean = _get_main_bean_path()
    entries, errors, options_map = loader.load_file(main_bean)
    
    # 收集所有 Open 和 Close entries
    open_entries = {}
    close_entries = {}
    
    for entry in entries:
        if isinstance(entry, beancount_data.Open):
            open_entries[entry.account] = entry
        elif isinstance(entry, beancount_data.Close):
            close_entries[entry.account] = entry
    
    # 从 accounts.bean 文件读取行尾注释
    comments = _extract_comments_from_file(_get_accounts_bean_path())
    
    # 构建账户列表
    accounts = []
    for account_name, open_entry in open_entries.items():
        is_closed = account_name in close_entries
        account_info = {
            "date": str(open_entry.date),
            "name": account_name,
            "currencies": list(open_entry.currencies) if open_entry.currencies else [],
            "comment": comments.get(account_name, ""),
            "status": "closed" if is_closed else "open",
        }
        if is_closed:
            account_info["close_date"] = str(close_entries[account_name].date)
        accounts.append(account_info)
    
    return accounts


def _ensure_trailing_newline(file_path: str):
    """确保文件以换行符结尾，避免追加内容时与最后一行连在一起"""
    if not os.path.exists(file_path):
        return
    with open(file_path, "rb") as f:
        f.seek(0, 2)  # 移到文件末尾
        if f.tell() == 0:
            return  # 空文件
        f.seek(-1, 2)  # 移到最后一个字节
        if f.read(1) != b'\n':
            with open(file_path, "a", encoding="utf-8") as fa:
                fa.write("\n")


def _extract_comments_from_file(file_path: str) -> dict:
    """从 bean 文件中提取行尾注释
    
    Args:
        file_path: bean 文件路径
        
    Returns:
        {账户名: 注释} 的字典
    """
    comments = {}
    if not os.path.exists(file_path):
        return comments
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            # 匹配 open 指令行的注释: YYYY-MM-DD open Account:Name [CURRENCY] ; 注释
            match = re.match(
                r'\d{4}-\d{2}-\d{2}\s+open\s+(\S+)(?:\s+\S+)?\s*;\s*(.+)$',
                line.strip()
            )
            if match:
                comments[match.group(1)] = match.group(2).strip()
    
    return comments


@app.get("/api/ledger/info")
async def get_ledger_info(user: dict = Depends(get_current_user)):
    """获取账本基本信息
    
    需要认证
    
    Returns:
        账本名称和主货币
    """
    try:
        info = _parse_ledger_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取账本信息失败: {str(e)}")


@app.put("/api/ledger/info")
async def update_ledger_info(
    request: LedgerInfoRequest,
    user: dict = Depends(get_current_user)
):
    """更新账本基本信息
    
    需要认证
    
    Args:
        request: 包含 title 和 operating_currency
        
    Returns:
        操作结果
    """
    if not request.title.strip():
        raise HTTPException(status_code=400, detail="账本名称不能为空")
    
    if not request.operating_currency.strip():
        raise HTTPException(status_code=400, detail="主货币不能为空")
    
    try:
        main_bean = _get_main_bean_path()
        with open(main_bean, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 替换 title
        content = re.sub(
            r'option\s+"title"\s+"[^"]*"',
            f'option "title" "{request.title.strip()}"',
            content
        )
        
        # 替换 operating_currency
        content = re.sub(
            r'option\s+"operating_currency"\s+"[^"]*"',
            f'option "operating_currency" "{request.operating_currency.strip()}"',
            content
        )
        
        with open(main_bean, "w", encoding="utf-8") as f:
            f.write(content)
        
        return {"success": True, "message": "账本信息已更新"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新账本信息失败: {str(e)}")


@app.get("/api/ledger/accounts")
async def get_ledger_accounts(user: dict = Depends(get_current_user)):
    """获取所有账户列表
    
    需要认证
    
    Returns:
        按五大类型分组的账户列表
    """
    try:
        accounts = _parse_accounts()
        
        # 按类型分组
        grouped = {t: [] for t in VALID_ACCOUNT_TYPES}
        for acc in accounts:
            top_type = acc["name"].split(":")[0]
            if top_type in grouped:
                grouped[top_type].append(acc)
        
        return {"accounts": grouped}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取账户列表失败: {str(e)}")


@app.post("/api/ledger/accounts")
async def add_ledger_account(
    request: AddAccountRequest,
    user: dict = Depends(get_current_user)
):
    """新增账户
    
    需要认证
    
    Args:
        request: 新增账户请求
        
    Returns:
        操作结果
    """
    # 校验账户类型
    if request.account_type not in VALID_ACCOUNT_TYPES:
        raise HTTPException(status_code=400, detail="无效的账户类型")
    
    # 校验路径
    path = request.path.strip()
    error = _validate_account_path(path)
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    # 构建完整账户名
    full_account = f"{request.account_type}:{path}"
    
    # 检查账户是否已存在
    try:
        existing_accounts = _parse_accounts()
        for acc in existing_accounts:
            if acc["name"] == full_account:
                raise HTTPException(status_code=400, detail="账户已存在")
    except HTTPException:
        raise
    except Exception:
        pass  # 解析失败时跳过重复检查
    
    # 构建 open 指令
    currencies_part = f" {request.currencies.strip()}" if request.currencies.strip() else ""
    comment_part = f" ; {request.comment.strip()}" if request.comment.strip() else ""
    line = f"1999-01-01 open {full_account}{currencies_part}{comment_part}\n"
    
    try:
        accounts_bean = _get_accounts_bean_path()
        _ensure_trailing_newline(accounts_bean)
        with open(accounts_bean, "a", encoding="utf-8") as f:
            f.write(line)
        return {"success": True, "message": f"账户 {full_account} 已创建"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建账户失败: {str(e)}")


@app.post("/api/ledger/accounts/close")
async def close_ledger_account(
    request: CloseAccountRequest,
    user: dict = Depends(get_current_user)
):
    """关闭账户
    
    需要认证
    
    Args:
        request: 关闭账户请求
        
    Returns:
        操作结果
    """
    account_name = request.account_name.strip()
    if not account_name:
        raise HTTPException(status_code=400, detail="账户名不能为空")
    
    # 确定关闭日期
    close_date = request.date.strip() if request.date.strip() else datetime.date.today().isoformat()
    
    # 校验账户存在且未关闭
    try:
        accounts = _parse_accounts()
        found = False
        for acc in accounts:
            if acc["name"] == account_name:
                found = True
                if acc["status"] == "closed":
                    raise HTTPException(status_code=400, detail="账户已关闭")
                break
        
        if not found:
            raise HTTPException(status_code=400, detail="账户不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"校验账户失败: {str(e)}")
    
    # 追加 close 指令
    line = f"{close_date} close {account_name}\n"
    
    try:
        accounts_bean = _get_accounts_bean_path()
        _ensure_trailing_newline(accounts_bean)
        with open(accounts_bean, "a", encoding="utf-8") as f:
            f.write(line)
        return {"success": True, "message": f"账户 {account_name} 已关闭"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"关闭账户失败: {str(e)}")


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
