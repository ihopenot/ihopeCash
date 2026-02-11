## Context

IhopeCash 当前通过手动安装依赖、手动启动 web/app.py 和 fava 两个进程来运行。没有标准化的部署方案。Web 界面和 Fava 账本查看器之间没有导航关联，用户需要分别记住两个端口。

项目的关键约束：
- web/app.py 使用 FastAPI + Uvicorn，单进程模式（`workers=1`）避免文件操作冲突
- Fava 需要访问 main.bean 及其 include 链（data/、accounts.bean）
- china_bean_importers 是 git submodule，需要 `pip install -e` 安装
- beancount 版本要求 < 3

## Goals / Non-Goals

**Goals:**
- `docker compose up` 一键启动全部服务（Nginx + Web + Fava）
- Nginx 统一入口，HTTPS 支持，HTTP 自动重定向到 HTTPS
- Fava 通过 `/fava/` 路径前缀访问，无需记忆额外端口
- 无证书时自动生成自签证书，有外部证书时直接使用
- Web 导航栏集成 Fava 入口
- 数据通过 volume 持久化，容器可随时重建

**Non-Goals:**
- 不重构 main.bean / accounts.bean 的文件结构
- 不引入多容器编排（保持单容器方案）
- 不集成 Let's Encrypt 自动证书续期
- 不修改 web/app.py 的业务逻辑

## Decisions

### D1: 单容器 + 多进程

**选择**: 在一个容器内运行 Nginx、Uvicorn、Fava 三个进程

**理由**: Web 和 Fava 共享相同的文件系统（main.bean、data/、config.yaml），多容器需要复杂的共享 volume 配置且没有实际隔离收益。

**替代方案**: 多容器 + 共享 volume。增加了 docker-compose 复杂度，对于个人使用的记账工具不值得。

### D2: entrypoint.sh 管理进程（不用 supervisord）

**选择**: 用 shell 脚本后台启动 nginx 和 fava，前台运行 uvicorn

**理由**: 只有三个进程，不需要 supervisord 的复杂性。uvicorn 作为前台进程，如果崩溃容器自动退出，由 Docker 的 `restart: unless-stopped` 策略处理重启。

**替代方案**: supervisord。增加镜像体积和配置复杂度，对三个稳定进程来说过度设计。

### D3: Nginx 统一反代 + HTTPS

**选择**: Nginx 监听 80/443，反代到内部 8000（Web）和 5000（Fava）

**配置**:
```
:80  → 301 重定向到 https://$host$request_uri
:443 → /         proxy_pass http://127.0.0.1:8000
       /fava/    proxy_pass http://127.0.0.1:5000/fava/
```

**理由**: 统一入口，用户只需知道一个地址。HTTPS 保护认证 token 传输。

### D4: SSL 证书策略 - 自签兜底 + 外部挂载

**选择**: entrypoint.sh 检测 `/app/certs/cert.pem` 和 `/app/certs/key.pem`，不存在则用 openssl 生成自签证书

**理由**: 开箱即用（自签证书），生产环境可挂载真实证书替换。

### D5: Fava 使用 `--prefix /fava` 参数

**选择**: 启动 Fava 时指定 `fava main.bean --host 127.0.0.1 --port 5000 --prefix /fava`

**理由**: Fava 原生支持 URL 前缀配置，配合 Nginx 反代可以无缝集成到同一域名下。

### D6: 基础镜像选择 python:3.12-slim

**选择**: 使用 `python:3.12-slim` 作为基础镜像

**理由**: 体积较小，包含完整 Python 运行时。通过 apt 安装 nginx 和 openssl。beancount < 3 在 Python 3.12 上运行正常。

### D7: Web 前端 Fava 按钮

**选择**: 在导航栏"导入"和"配置"旁边添加"账本"按钮，链接到 `/fava/`，新标签页打开

**理由**: 使用相对路径 `/fava/`，无论从什么域名/IP 访问都能正确跳转。新标签页打开避免中断导入操作。

## Risks / Trade-offs

- **[单容器单点故障]** → Fava 崩溃不影响 Web，但 Nginx 崩溃全部不可用。使用 `restart: unless-stopped` 缓解。
- **[自签证书浏览器警告]** → 首次访问需要用户手动确认信任。文档中说明如何挂载真实证书。
- **[镜像体积]** → 包含 nginx + Python + beancount + fava + 项目依赖，镜像较大。可后续优化多阶段构建。
- **[Uvicorn 工作目录]** → web/app.py 中静态文件路径是 `web/static`，Docker 中必须从 `/app/` 目录启动 uvicorn，使用 `web.app:app` 模块路径。
