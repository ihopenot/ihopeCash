# IhopeCash Web 界面

IhopeCash 的 Web 导入工具，提供友好的浏览器界面替代命令行操作。

## ✨ 功能特性

- 🔐 JWT Token 认证保护
- 📊 实时进度显示（WebSocket）
- 🎯 三种导入模式（通常/强制/追加）
- 💻 现代化的响应式 UI
- 🚀 完全离线运行

## 📦 安装依赖

```bash
cd web
pip install -r requirements.txt
```

## ⚙️ 配置

在项目根目录的 `config.yaml` 中添加 Web 配置块:

```yaml
web:
  host: "0.0.0.0"                        # 监听地址，0.0.0.0 允许外网访问
  port: 8000                              # 端口
  password: "your_secure_password"        # Web 界面密码 ⚠️ 必须修改
  jwt_secret: "your_random_secret_key"    # JWT 签名密钥 ⚠️ 必须修改
  token_expire_days: 7                    # Token 有效期（天）
```

**⚠️ 安全提示**: 
- 务必修改 `password` 和 `jwt_secret` 为强密码和随机密钥
- 生产环境建议使用 HTTPS（通过 Nginx 反向代理）

## 🚀 运行服务

### 开发模式

```bash
cd web
python app.py
```

或使用 uvicorn:

```bash
cd web
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 生产模式

```bash
cd web
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1
```

**注意**: 必须使用 `--workers 1` 单进程模式，因为文件操作不是线程安全的。

## 🌐 访问界面

启动后访问: `http://localhost:8000`

首次使用:
1. 输入 `config.yaml` 中配置的密码登录
2. 系统会自动加载余额账户列表
3. 选择年月、导入模式、填写余额
4. 点击"开始导入"

## 📋 导入模式说明

| 模式 | 行为 | 适用场景 |
|------|------|---------|
| **通常模式** | 目录已存在时报错 | 首次导入该月 |
| **强制覆盖** | 删除已有目录并重建 | 重新导入，覆盖旧数据 |
| **追加模式** | 向已有月份添加新文件 | 补充遗漏的交易 |

## 🎨 前端样式构建（可选）

如果需要修改样式，需要使用 Tailwind CLI 重新构建 CSS:

1. 下载 Tailwind CLI standalone:
   ```bash
   # Linux / Mac
   curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
   chmod +x tailwindcss-linux-x64
   mv tailwindcss-linux-x64 web/tailwindcss

   # Windows
   # 从 https://github.com/tailwindlabs/tailwindcss/releases 下载对应版本
   ```

2. 构建样式:
   ```bash
   cd web
   ./build.sh             # 生产构建（最小化）
   ./build.sh --watch     # 开发模式（监听变化）
   ```

## 🐳 生产环境部署

### 使用 Nginx 反向代理 + SSL

1. **Nginx 配置示例** (`/etc/nginx/sites-available/ihopecash`):

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 主页面
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket 支持
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

2. **启用配置**:
```bash
sudo ln -s /etc/nginx/sites-available/ihopecash /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 使用 systemd 管理服务

1. **创建服务文件** (`/etc/systemd/system/ihopecash-web.service`):

```ini
[Unit]
Description=IhopeCash Web Service
After=network.target

[Service]
Type=simple
User=your-user
Group=your-group
WorkingDirectory=/path/to/ihopeCash/web
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000 --workers 1
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

2. **启用并启动服务**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ihopecash-web
sudo systemctl start ihopecash-web
sudo systemctl status ihopecash-web
```

## 🔧 常见问题排查

### 1. 启动时提示配置警告

```
⚠️  配置警告:
  - 警告: 请修改 config.yaml 中的 web.password
  - 警告: 请修改 config.yaml 中的 web.jwt_secret
```

**解决**: 编辑 `config.yaml`，修改 `web.password` 和 `web.jwt_secret` 为强密码和随机密钥。

### 2. 登录后立即跳转回登录页

**可能原因**:
- Token 验证失败
- JWT secret 配置错误

**解决**: 
1. 清除浏览器 localStorage: 开发者工具 → Application → Local Storage → 删除 `auth_token`
2. 检查 `config.yaml` 中 `jwt_secret` 是否正确配置

### 3. WebSocket 连接失败

**可能原因**:
- Token 未正确传递
- Nginx 未配置 WebSocket 支持

**解决**:
1. 检查浏览器控制台错误信息
2. 如果使用 Nginx，确保添加了 WebSocket 配置（见上文）

### 4. 导入失败: "目录已存在"

**解决**: 
- 使用"强制覆盖"模式删除已有目录
- 或使用"追加模式"向已有月份追加交易

### 5. 样式显示不正常

**解决**:
1. 检查 `web/static/style.css` 文件是否存在
2. 清除浏览器缓存: Ctrl+F5 强制刷新
3. 如需完整 Tailwind 样式，运行 `build.sh` 重新构建

## 📝 API 文档

启动服务后访问自动生成的 API 文档:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔒 安全建议

1. **生产环境必须使用 HTTPS**
2. **定期更换 JWT secret**
3. **使用强密码**（建议至少16位，包含大小写字母、数字和特殊字符）
4. **限制访问IP**（通过防火墙或 Nginx）
5. **定期备份 config.yaml**

## 🆘 技术支持

如遇问题，请提供以下信息:
- Python 版本: `python --version`
- 依赖版本: `pip list`
- 错误日志（完整输出）
- 配置文件（隐藏密码）
