## Why

从零 clone 仓库并通过 Docker 跑通全流程时，发现 12 个问题（1 个已单独修复），涵盖构建失败、容器权限、启动流程、前端交互和数据持久化。这些问题导致新用户无法完成首次部署和配置引导。

## What Changes

- **BREAKING**: 目录结构重组 —— `rawdata/`、`archive/` 移入 `data/beancount/` 下，`config.yaml` 移入 `data/`，原 `data/` 下的 bean 文件移入 `data/beancount/`
- **BREAKING**: Docker 只挂载 `data/` 一个数据卷（`env.yaml` 和 `certs/` 保持不变）
- **BREAKING**: Docker 只暴露 HTTPS 端口，移除 HTTP 端口映射
- 移除 Dockerfile 中的 appuser，容器内全程使用 root
- 将 `beancount_config.py` 纳入 Git 版本控制
- 修复 entrypoint.sh 启动流程：首次运行时创建空 `main.bean` 占位，Fava 启动不阻塞主服务
- Nginx CSP 头允许 Tailwind CDN
- 引导页余额账户下拉框联动卡号映射中的账户
- 配置页账户字段统一改为下拉选择+新增模式
- 配置页卡号映射中间名称去除末尾多余冒号
- Git 数据版本管理范围从 `data/` 改为 `data/beancount/`

## Capabilities

### New Capabilities

（无新增能力）

### Modified Capabilities

- `docker-deployment`: 目录结构重组，单数据卷挂载，移除 appuser，只暴露 HTTPS 端口，entrypoint 启动流程修复，CSP 修复
- `setup-wizard`: 余额账户下拉框联动卡号映射中的账户
- `web-config-editor`: 账户字段改为下拉选择+新增模式，卡号映射中间名称去尾冒号
- `git-data-versioning`: git 管理范围从 `data/` 改为 `data/beancount/`
- `unified-config-management`: config.yaml 默认路径改为 `data/config.yaml`，data_path/rawdata_path/archive_path 默认值更新

## Impact

- **Docker 配置**: `Dockerfile`、`docker-compose.yml`、`docker/entrypoint.sh`、`docker/nginx.conf`
- **核心配置**: `config.py`（默认路径变更）
- **后端**: `backend.py`（git cwd 变更、路径引用）
- **前端**: `web/static/setup.html`、`web/static/config.html`
- **Web 应用**: `web/app.py`（bean 文件路径）
- **版本控制**: `.gitignore`、`.dockerignore`
- **迁移**: `migrate.py`（需新增旧→新目录结构迁移逻辑）
- **已有部署**: 需要手动将旧目录结构迁移到新结构
