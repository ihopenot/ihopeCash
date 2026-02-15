## 1. 环境配置文件（env.yaml）

- [x] 1.1 创建 `env.example.yaml` 模板文件，包含 system（data_path、rawdata_path、archive_path）和 web（host、port、password、jwt_secret、token_expire_days）配置项及注释
- [x] 1.2 创建当前项目使用的 `env.yaml`，从现有 config.yaml 中提取 system 和 web 配置

## 2. Config 类改造（config.py）

- [x] 2.1 修改 `Config.__init__` 接受 `env_file` 参数（默认 "env.yaml"），实现双文件加载逻辑：先加载 env.yaml（不存在则抛 FileNotFoundError），再加载 config.yaml（不存在则 setup_required=True 不创建文件）
- [x] 2.2 实现 env.yaml 中 system/web 字段覆盖 config.yaml 对应字段的合并逻辑
- [x] 2.3 添加 `setup_required` 属性
- [x] 2.4 修改 `_get_default_config()` 中 importers.card_narration_whitelist 默认值为 ["财付通(银联云闪付)"]，card_narration_blacklist 默认值为 ["支付宝", "财付通", "美团支付"]
- [x] 2.5 实现 `complete_setup(config_data, new_accounts)` 方法：写入 config.yaml、追加 accounts.bean（去重）、更新 setup_required

## 3. Docker 部署调整

- [x] 3.1 修改 `docker-compose.yml`：移除 config.yaml 挂载，新增 env.yaml 挂载
- [x] 3.2 修改 `docker/entrypoint.sh`：在启动服务前添加 env.yaml 存在性检查，不存在则报错退出
- [x] 3.3 修改 `Dockerfile`：调整 VOLUME 声明（如有需要）— Dockerfile 无需修改，不含 config.yaml 相关声明

## 4. Web 后端 - 引导 API 和中间件（web/app.py）

- [x] 4.1 添加引导拦截中间件：setup_required 为 True 时，仅允许 /login、/api/auth/login、/setup、/api/setup/*、/static/* 路径，其他重定向到 /setup
- [x] 4.2 实现 `GET /setup` 路由，返回 setup.html 静态页面
- [x] 4.3 实现 `GET /api/setup/status` 端点（无需认证），返回 `{ setup_required: bool }`
- [x] 4.4 实现 `GET /api/setup/defaults` 端点（需认证），返回包含所有导入器和交易摘要过滤默认值的配置
- [x] 4.5 实现 `POST /api/setup/complete` 端点（需认证）：校验 setup_required、校验配置合法性、调用 config.complete_setup()、返回结果
- [x] 4.6 引导完成后 /setup 路径重定向到 /

## 5. Web 前端 - 引导页（web/static/setup.html）

- [x] 5.1 创建 setup.html 基础结构：步骤进度指示器、步骤容器、上一步/下一步按钮、全局状态管理（setupState 对象含 currentStep、tempAccounts、config）
- [x] 5.2 实现账户下拉选择组件：加载服务端账户 + tempAccounts 合并、不允许手动输入、内联新增表单（弹出后填写账户类型/路径/货币/备注，提交后加入 tempAccounts 并自动选中）、新增账户去重校验
- [x] 5.3 实现 Step 1 邮箱配置：IMAP 服务器、端口、用户名、密码、邮箱文件夹输入框，预填默认值
- [x] 5.4 实现 Step 2 通用账户配置：默认支出账户和默认收入账户的下拉选择 + 新增按钮
- [x] 5.5 实现 Step 3 支付宝配置：6 个账户字段的下拉选择
- [x] 5.6 实现 Step 4 微信配置：9 个账户字段的下拉选择
- [x] 5.7 实现 Step 5 清华饭卡配置：1 个账户字段的下拉选择
- [x] 5.8 实现 Step 6 HSBC HK 配置：use_cnh 开关 + One 账户下拉 + PULSE 账户下拉，提交时合并为 hsbc_hk 格式
- [x] 5.9 实现 Step 7 交易摘要过滤：白名单和黑名单动态列表，预填默认值（白名单 ["财付通(银联云闪付)"]，黑名单 ["支付宝", "财付通", "美团支付"]）
- [x] 5.10 实现 Step 8 卡号账户映射：三栏输入（分类下拉 + 中间名称 + 4位字符串）、自动补冒号、实时预览、4位字符校验（数字和大写字母）、中间名称段首字母校验、完整账户名合法性校验
- [x] 5.11 实现 Step 9 交易匹配规则：默认空列表、添加规则按钮、规则字段（payee_keywords、narration_keywords、account 下拉选择、tags）
- [x] 5.12 实现 Step 10 余额账户配置：下拉选择添加余额账户，可添加多个，可删除
- [x] 5.13 实现 Step 11 确认页：分区汇总展示所有配置、新增账户列表、每区域"修改"按钮跳回对应步骤、"确认并完成配置"按钮提交 POST /api/setup/complete、成功后跳转首页

## 6. 配置页面改造（web/static/config.html）

- [x] 6.1 HSBC HK 区域：将 JSON textarea 替换为三条独立配置项（use_cnh checkbox + One 账户输入框 + PULSE 账户输入框），保存时合并为原格式
- [x] 6.2 卡号账户映射区域：将 JSON textarea 替换为三栏交互式编辑（分类下拉 + 中间名称 + 4位字符串），添加实时预览和校验逻辑，保存时转换为嵌套结构
- [x] 6.3 交易摘要过滤区域：加载时如果列表为空则预填默认值

## 7. 登录页适配

- [x] 7.1 修改 login.html：登录成功后检查 setup_required 状态（GET /api/setup/status），如需引导则跳转 /setup，否则跳转 /
