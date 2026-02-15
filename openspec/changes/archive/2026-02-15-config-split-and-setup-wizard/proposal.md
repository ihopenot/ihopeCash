## Why

当前所有配置（系统路径、Web 服务、邮箱、导入器、账户映射等）集中在一个 `config.yaml` 文件中，Docker 部署时需要将其挂载到宿主机。这导致两个问题：(1) 敏感业务配置（邮箱密码、账户信息等）暴露在宿主机文件系统中，无法完全通过 Web 界面管理；(2) 首次部署时用户需要手动编辑 YAML 文件配置所有账户，体验差且容易出错。

## What Changes

- **配置文件拆分**：将 `system`（路径配置）和 `web`（服务配置）从 `config.yaml` 拆出到新的 `env.yaml`，Docker 只需挂载 `env.yaml`，`config.yaml` 完全通过 Web 管理
- **Config 类改造**：支持双文件加载（`env.yaml` + `config.yaml`），`env.yaml` 必须存在否则报错，`config.yaml` 不存在时标记为需要引导（`setup_required`）而非自动创建默认文件
- **Docker 部署调整**：`docker-compose.yml` 移除 `config.yaml` 挂载，新增 `env.yaml` 挂载；入口脚本增加 `env.yaml` 存在性检查
- **首次运行引导页**：新增 `setup.html`，包含 11 步引导流程（邮箱 → 通用账户 → 支付宝 → 微信 → 清华饭卡 → HSBC HK → 交易摘要过滤 → 卡号账户映射 → 交易匹配规则 → 余额账户 → 确认），所有修改临时存储在前端，最终确认后一次性落地
- **引导页 API**：新增 `/api/setup/*` 端点，包括获取默认配置、提交最终配置（同时写入 `config.yaml` 和 `accounts.bean`）
- **Web 中间件**：`setup_required` 为 true 时，除引导相关路径和登录路径外，所有请求重定向到引导页
- **账户选择组件**：引导页中所有账户字段使用下拉选择（现有账户 + 引导中新增的临时账户），不允许手动输入，提供内联新增表单
- **HSBC HK 配置拆分**：前端将 `use_cnh` 单独一条，`One` 和 `PULSE` 账户各一条展示，后端收到后合并回原格式
- **卡号账户映射改造**：前端分三栏（分类下拉 + 自定义名称 + 4位字符串），自动补冒号，实时预览完整账户名并校验合法性
- **交易摘要过滤默认值**：引导页预填当前实际使用的白名单/黑名单默认值

## Capabilities

### New Capabilities
- `env-config`: 环境配置文件（env.yaml）的定义、加载、校验，以及与 config.yaml 的合并策略
- `setup-wizard`: 首次运行引导流程，包括引导页前端（setup.html）、引导 API 端点、中间件拦截、临时状态管理、最终配置落地

### Modified Capabilities
- `backend-config`: Config 类需要支持双文件加载，env.yaml 必须存在否则报错，config.yaml 不存在时标记 setup_required 而非自动创建
- `docker-deployment`: docker-compose.yml 移除 config.yaml 挂载，新增 env.yaml 挂载；entrypoint.sh 增加 env.yaml 检查
- `web-config-editor`: 高级配置中 HSBC HK 部分拆分为三条（use_cnh + One + PULSE），卡号账户映射改为三栏交互，交易摘要过滤提供默认值
- `web-authentication`: 引导页路由需要纳入认证流程（引导页需要登录后才能访问）

## Impact

- **config.py**: 核心改造，双文件加载逻辑、setup_required 属性
- **web/app.py**: 新增中间件、setup API 端点、引导页路由
- **web/auth.py**: 认证逻辑需兼容 setup 路径
- **web/static/setup.html**: 全新文件，11 步引导页
- **web/static/config.html**: HSBC HK 拆分、卡号映射三栏、交易摘要过滤默认值
- **docker-compose.yml**: 卷挂载调整
- **docker/entrypoint.sh**: env.yaml 检查
- **Dockerfile**: VOLUME 声明调整
- **env.yaml / env.example.yaml**: 新增文件
- **beancount_config.py**: 无需修改（Config() 自动适配）
- **web/tasks.py, web/auth.py**: Config() 实例化行为变化，需确认兼容
