## Why

项目目前需要手动安装 Python 依赖、分别启动 web/app.py 和 fava 两个进程，部署流程繁琐且缺乏标准化。需要通过 Docker Compose 实现一键部署，同时在 Web 界面中集成 Fava 入口，让用户在完成账单导入后能直接查看账本。

## What Changes

- 新增 `Dockerfile`：基于 Python 镜像，安装所有依赖（beancount、fava、nginx、项目依赖），构建完整运行环境
- 新增 `docker-compose.yml`：定义服务、端口映射（80/443）、数据卷挂载（config.yaml、data/、rawdata/、archive/、main.bean、accounts.bean、certs/）
- 新增 `docker/entrypoint.sh`：容器启动脚本，检测/生成 SSL 自签证书，依次启动 nginx、fava、uvicorn
- 新增 `docker/nginx.conf`：Nginx 反向代理配置，HTTP→HTTPS 重定向，`/` 代理到 Web 应用，`/fava/` 代理到 Fava
- 新增 `.dockerignore`：排除构建无关文件
- 修改 Web 前端导航栏：在 index.html 和 config.html 中新增"账本"按钮，链接到 `/fava/`

## Capabilities

### New Capabilities
- `docker-deployment`: Docker Compose 单容器部署方案，包含 Dockerfile、docker-compose.yml、entrypoint 启动脚本、Nginx 反代配置和 SSL 支持
- `web-fava-navigation`: Web 界面集成 Fava 导航入口，在导航栏添加跳转到 `/fava/` 的按钮

### Modified Capabilities
<!-- 无需修改现有 spec 的需求层面行为 -->

## Impact

- **新增文件**: Dockerfile, docker-compose.yml, docker/entrypoint.sh, docker/nginx.conf, .dockerignore
- **修改文件**: web/static/index.html, web/static/config.html（导航栏新增按钮）
- **新增依赖**: nginx（容器内安装）、openssl（证书生成）
- **端口**: 容器暴露 80（HTTP 重定向）和 443（HTTPS）
- **数据持久化**: 通过 volume 挂载 config.yaml、data/、rawdata/、archive/、main.bean、accounts.bean、certs/
