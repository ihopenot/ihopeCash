## Why

当前 `main.bean` 和 `accounts.bean` 位于项目根目录，Web 界面无法管理账本基本信息和账户。用户需要手动编辑 bean 文件来修改账本名称、主货币或新增/关闭账户，这对不熟悉 beancount 语法的用户不友好。将这两个文件移至 `data/` 目录下统一管理，并在 Web 配置页面提供可视化的账本配置功能。

## What Changes

- 将 `main.bean` 和 `accounts.bean` 从项目根目录移至 `data/` 目录下
- 调整 `main.bean` 内部的 `include` 路径（移除 `data/` 前缀）
- 修改 `backend.py` 中对 `main.bean` 的引用路径
- 修改 `docker/entrypoint.sh` 中 Fava 启动时的 `main.bean` 路径
- Web 应用启动时自动检测并创建默认的 `main.bean`、`accounts.bean`、`balance.bean`
- 在配置页面（`/config`）新增"账本"Tab（排在第一个），支持：
  - 查看和修改账本名称、主货币
  - 按五大账户类型分组展示现有账户
  - 通过结构化表单新增账户（下拉选类型 + 输入路径 + 前端校验）
  - 关闭账户（日期默认当天）
- 新增 4 个 API 端点用于账本信息和账户的 CRUD
- 提供迁移脚本，自动将已有的 bean 文件迁移到新位置并修正路径

## Capabilities

### New Capabilities
- `bean-file-management`: bean 文件的位置管理、启动时自动创建默认文件、迁移脚本
- `ledger-config-ui`: Web 配置页面的账本 Tab，包括基本信息编辑和账户管理交互
- `ledger-api`: 账本信息和账户管理的后端 API（读取/更新账本信息、获取/新增/关闭账户）

### Modified Capabilities
- `backend-bill-operations`: `ensure_year_directory` 中 main.bean 的路径从根目录改为 `data/main.bean`，include 路径格式从 `include "data/{year}/_.bean"` 改为 `include "{year}/_.bean"`
- `docker-deployment`: Fava 启动路径从 `fava main.bean` 改为 `fava data/main.bean`；数据卷挂载不再需要单独挂载根目录的 `main.bean` 和 `accounts.bean`（已在 `data/` 目录内）
- `web-config-editor`: 配置页面 Tab 数量从 3 个变为 4 个，新增"账本"Tab 排在第一位，默认选中"账本"Tab

## Impact

- **代码文件**: `backend.py`、`web/app.py`、`web/static/config.html`、`docker/entrypoint.sh`
- **数据文件**: `main.bean`、`accounts.bean` 位置变更
- **API**: 新增 `GET/PUT /api/ledger/info`、`GET/POST /api/ledger/accounts`、`POST /api/ledger/accounts/close`
- **依赖**: 使用 `beancount.loader` 解析 bean 文件（已有依赖）
- **Docker**: entrypoint.sh 中 Fava 路径需要更新
- **迁移**: 已有用户需要运行迁移脚本或重新部署时自动迁移
