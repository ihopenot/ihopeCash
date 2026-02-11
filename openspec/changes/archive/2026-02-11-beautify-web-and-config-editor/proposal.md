## Why

当前 Web 界面使用手写的 Tailwind 模拟 CSS，视觉效果单调且存在样式错误；功能上仅支持账单导入，缺少配置管理能力，用户必须手动编辑 config.yaml 文件。同时 passwords 存储在配置文件中不够灵活，应改为每次导入时由用户手动提供。

## What Changes

- 引入 Tailwind CDN 替代手写的模拟 CSS，全面美化登录页、主页面
- 增加顶部导航栏，支持"导入"和"配置"页面切换
- 在导入表单中新增 passwords 动态列表输入区域，用户每次导入时手动填写附件解压密码
- **BREAKING**: `ImportRequest` 接口新增 `passwords` 字段，passwords 不再从 config.yaml 读取
- 新建配置编辑页面（config.html），含 3 个 Tab：基础配置（balance_accounts + email）、高级配置（importers + card_accounts + detail_mappings 等）、修改登录密码
- 后端新增配置读取/保存/修改密码的 API 端点
- Config 类新增配置编辑相关方法
- 敏感字段（email 密码）后端脱敏返回，前端不显示但可修改
- `web`、路径类配置、`passwords`、`pdf_passwords` 不支持从 Web 端编辑

## Capabilities

### New Capabilities
- `web-config-editor`: Web 端配置编辑功能，包含分 Tab 的结构化表单编辑、敏感字段脱敏处理、保存后热重载配置
- `web-ui-beautify`: 使用 Tailwind CDN 美化所有 Web 页面，增加导航栏和统一的视觉风格

### Modified Capabilities
- `web-import-interface`: 导入表单新增 passwords 动态列表输入区域；导入 API 新增 passwords 参数
- `realtime-progress-tracking`: 任务创建和执行流程透传 passwords 参数

## Impact

- **后端文件**: `config.py`（新增方法）、`web/app.py`（新增 API 端点）、`web/tasks.py`（透传 passwords）
- **前端文件**: `web/static/style.css`（精简）、`web/static/login.html`（美化）、`web/static/index.html`（美化+passwords 输入）、`web/static/config.html`（新建）
- **API 变更**: `POST /api/import` 新增 passwords 字段（**BREAKING**）；新增 `GET/PUT /api/config/full`、`POST /api/config/change-password`
- **配置影响**: passwords 从配置文件读取移至运行时传入；pdf_passwords 保持不变
