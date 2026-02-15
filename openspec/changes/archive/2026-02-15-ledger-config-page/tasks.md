## 1. 迁移脚本与文件搬迁

- [x] 1.1 创建 `migrate.py` 迁移脚本：检测根目录 `main.bean` 和 `accounts.bean`，移动到 `data/` 目录，修正 `main.bean` 中的 include 路径（去掉 `data/` 前缀），幂等设计
- [x] 1.2 修改 `backend.py` 中 `ensure_year_directory` 方法：将 `open("main.bean")` 改为 `open("data/main.bean")`，将追加的 include 路径从 `include "{data_path}/{year}/_.bean"` 改为 `include "{year}/_.bean"`
- [x] 1.3 修改 `docker/entrypoint.sh`：将 `fava /app/main.bean` 改为 `fava /app/data/main.bean`，在 Fava 启动前执行迁移脚本

## 2. 启动时自动创建默认文件

- [x] 2.1 在 `web/app.py` 中添加 FastAPI startup 事件：检测并创建 `data/` 目录、`data/main.bean`（含默认 title/currency/include）、`data/accounts.bean`（空文件）、`data/balance.bean`（空文件）

## 3. 后端 API — 账本信息

- [x] 3.1 在 `web/app.py` 中新增 `GET /api/ledger/info` 端点：使用 `beancount.loader` 解析 `data/main.bean`，提取 `option "title"` 和 `option "operating_currency"` 返回
- [x] 3.2 在 `web/app.py` 中新增 `PUT /api/ledger/info` 端点：接收 title 和 operating_currency，用正则替换 `data/main.bean` 中对应的 option 行，校验 title 非空

## 4. 后端 API — 账户管理

- [x] 4.1 在 `web/app.py` 中新增 `GET /api/ledger/accounts` 端点：使用 `beancount.loader` 解析账本，提取所有 Open/Close entries，按五大类型分组，返回账户列表（含 date、name、currencies、comment、status、close_date）
- [x] 4.2 在 `web/app.py` 中新增 `POST /api/ledger/accounts` 端点：接收 account_type、path、currencies、comment，校验 account_type 合法性、path 第一段以字母/数字开头、账户不重复，追加 open 指令到 `data/accounts.bean`
- [x] 4.3 在 `web/app.py` 中新增 `POST /api/ledger/accounts/close` 端点：接收 account_name 和 date（默认当天），校验账户存在且未关闭，追加 close 指令到 `data/accounts.bean`

## 5. 前端 — 配置页面"账本"Tab

- [x] 5.1 修改 `web/static/config.html`：在 Tab 栏最前面新增"账本"Tab 按钮，新增对应的 Tab 内容区域，调整默认选中为"账本"Tab
- [x] 5.2 实现"基本信息"区域：账本名称输入框、主货币输入框、保存按钮，加载时调用 `GET /api/ledger/info`，保存时调用 `PUT /api/ledger/info`
- [x] 5.3 实现"新增账户"表单：账户类型下拉框（5种类型，中文标签）、账户路径输入框、货币输入框（placeholder "留空支持所有货币"）、备注输入框、实时预览区域、"添加账户"按钮
- [x] 5.4 实现前端账户路径校验：检测路径第一个 `:` 之前的部分是否以 `[A-Za-z0-9]` 开头，检测路径不为空、不以 `:` 开头/结尾、不含 `::`，不通过时显示错误提示
- [x] 5.5 实现账户列表展示：按五大类型分组，每组可折叠，显示账户名/货币/备注，open 状态显示"关闭"按钮，closed 状态灰色+删除线
- [x] 5.6 实现关闭账户交互：点击"关闭"弹出确认对话框，显示账户名、日期输入框（默认当天）、警告提示，确认后调用 `POST /api/ledger/accounts/close` 并刷新列表

## 6. 集成测试与验证

- [x] 6.1 验证迁移脚本：在根目录存在旧文件时执行迁移，确认文件位置和 include 路径正确；再次执行确认幂等
- [x] 6.2 验证启动自动创建：删除 data 目录下的 bean 文件后启动 Web 应用，确认默认文件被创建
- [x] 6.3 验证账本信息 API：通过 Web 界面修改账本名称和主货币，确认 `data/main.bean` 内容更新
- [x] 6.4 验证账户管理全流程：新增账户 → 列表刷新展示 → 关闭账户 → 列表展示灰色删除线
