## Context

当前 Web 界面使用 FastAPI 提供静态 HTML 页面，前端通过手写的 Tailwind 模拟 CSS 实现样式。style.css 约 112 行，手动模拟了部分 Tailwind 工具类但存在错误（如 `justify-between: space-between` 写法错误），缺少响应式支持和许多常用类。

后端 `config.py` 的 Config 类已支持加载/保存 YAML 配置、字典式访问、属性访问等功能，但缺少 Web 端配置编辑所需的脱敏返回和安全更新方法。

`web/tasks.py` 的 TaskManager 在创建导入任务时从 Config 读取 passwords，现需改为从请求参数传入。

## Goals / Non-Goals

**Goals:**
- 使用 Tailwind CDN 全面美化三个 Web 页面（login/index/config），统一视觉风格
- 增加顶部导航栏实现页面间导航
- 提供安全的 Web 端配置编辑能力，后端强制校验不可编辑和敏感字段
- 将 passwords 从静态配置改为导入时动态传入
- 配置保存后热重载，无需重启服务

**Non-Goals:**
- 不支持从 Web 端编辑 web 节点配置、路径类配置、passwords、pdf_passwords
- 不做配置内容验证（仅保存，由用户负责正确性）
- 不引入前端构建工具链（仅使用 CDN）
- 不做 Tailwind 生产构建优化（保留 build.sh 供未来使用）
- 不做用户角色/权限管理

## Decisions

### 1. 前端样式方案：Tailwind CDN

**选择**: 在 HTML 中引入 `<script src="https://cdn.tailwindcss.com"></script>`

**替代方案**:
- 继续手写 CSS：维护成本高，类名不完整
- Tailwind CLI 构建：需要额外工具链，开发体验差

**理由**: CDN 方式零配置、开发即时生效、所有 Tailwind 类可用。生产环境可通过已有的 build.sh 切换为构建方式。

### 2. 配置编辑 API 设计：单个完整端点

**选择**: `GET/PUT /api/config/full` 一次性返回/保存全部可编辑配置

**替代方案**:
- 每个配置节一个端点（`/api/config/email`, `/api/config/importers` 等）：端点过多，维护复杂

**理由**: 配置项总量有限，单端点降低复杂度。PUT 时后端负责与原配置合并，保护不可编辑字段。

### 3. 敏感字段与不可编辑字段保护策略

**选择**: 后端维护一份"受保护字段"列表。GET 返回时敏感字段置为空字符串；PUT 保存时后端强制校验，无论前端提交什么值，受保护字段一律自动跳过、保留原值，不依赖前端行为。

受保护字段（PUT 时自动跳过）：
- `web` 整个节点（通过修改密码专用接口修改 web.password）
- `system.data_path`, `system.rawdata_path`, `system.archive_path`
- `passwords`, `pdf_passwords`
- `email.imap.password`（仅通过单独逻辑处理：空值跳过，非空值更新）

**理由**: 安全性不应依赖前端，后端必须作为最终防线。即使前端被篡改或绕过，后端也能保证敏感配置不被意外修改。

### 4. 配置热重载方式

**选择**: 保存成功后，后端直接调用 `config.load()` 重新加载。由于 `app.py` 中的 `config` 是模块级变量，重新加载后所有后续请求使用新配置。

**理由**: 单进程模式（workers=1）下安全可行，无需进程间通信。

### 5. 页面组织：独立 HTML 文件

**选择**: config.html 作为独立页面，与 index.html 共享相同的导航栏样式但各自独立

**替代方案**:
- SPA 方式在 index.html 中用 JS 切换视图：增加单文件复杂度

**理由**: 保持每个页面职责单一，HTML 内嵌 JS 的架构不适合做 SPA。页面间通过导航栏链接跳转。

## Risks / Trade-offs

- **[CDN 依赖外网]** → Tailwind CDN 需要联网；离线环境可使用 build.sh 预构建 CSS 替代
- **[配置保存无业务验证]** → 用户可能写入无效配置导致功能异常 → 页面顶部显示醒目警告，提醒用户谨慎修改账户名等关键配置
- **[passwords 每次手动输入]** → 用户体验略有下降 → 可后续考虑前端 localStorage 记忆（本次不实现）
- **[单端点全量保存]** → 并发编辑可能冲突 → 单用户场景下风险极低
