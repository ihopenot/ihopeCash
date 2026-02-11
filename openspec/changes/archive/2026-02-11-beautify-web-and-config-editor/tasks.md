## 1. 后端：Config 类扩展

- [x] 1.1 在 config.py 的 Config 类中新增 `get_editable_config()` 方法，返回脱敏后的可编辑配置（排除 web、路径字段、passwords、pdf_passwords；email.imap.password 置空）
- [x] 1.2 在 config.py 的 Config 类中新增 `update_from_web(data)` 方法，后端强制跳过受保护字段（web、路径、passwords、pdf_passwords），email.imap.password 空值跳过、非空更新，保存并重新加载
- [x] 1.3 在 config.py 的 Config 类中新增 `update_web_password(new_password)` 方法，更新 web.password 并保存重新加载

## 2. 后端：任务管理 passwords 透传

- [x] 2.1 修改 web/tasks.py 的 `create_task()` 和 `_execute_import()` 方法，增加 passwords 参数并传递给 BillManager

## 3. 后端：API 端点扩展

- [x] 3.1 修改 web/app.py 的 ImportRequest 模型，增加 `passwords: List[str]` 字段（默认空列表），并将 passwords 传递给 task_manager.create_task()
- [x] 3.2 新增 GET /config 路由，返回 config.html 页面
- [x] 3.3 新增 GET /api/config/full 端点，调用 config.get_editable_config() 返回脱敏配置
- [x] 3.4 新增 PUT /api/config/full 端点，调用 config.update_from_web(data) 保存配置
- [x] 3.5 新增 POST /api/config/change-password 端点，验证当前密码后调用 config.update_web_password()

## 4. 前端：样式精简

- [x] 4.1 精简 web/static/style.css，移除手写 Tailwind 模拟类，仅保留自定义样式（log-entry 等）

## 5. 前端：登录页美化

- [x] 5.1 重写 web/static/login.html，引入 Tailwind CDN，渐变背景 + 居中卡片 + 现代化表单样式

## 6. 前端：主页面美化

- [x] 6.1 重写 web/static/index.html，引入 Tailwind CDN，增加顶部导航栏（品牌名 + 导入/配置切换 + 退出按钮）
- [x] 6.2 在导入表单中新增 passwords 动态列表输入区域（添加/删除密码输入框），提交时将 passwords 包含在请求中
- [x] 6.3 美化表单卡片、按钮、日志区域样式（状态颜色区分）

## 7. 前端：配置编辑页面

- [x] 7.1 新建 web/static/config.html，包含顶部导航栏和 3 个 Tab 切换界面
- [x] 7.2 实现 Tab 1 基础配置：balance_accounts 动态增减列表 + email.imap 各字段输入框，顶部显示账户名修改警告
- [x] 7.3 实现 Tab 2 高级配置：importers 各分组字段、card_accounts 键值对编辑、detail_mappings 列表编辑、unknown_expense/income_account、card_narration_whitelist/blacklist
- [x] 7.4 实现 Tab 3 修改密码：当前密码 + 新密码 + 确认密码表单，调用 POST /api/config/change-password
- [x] 7.5 实现配置加载（GET /api/config/full）和保存（PUT /api/config/full）逻辑，保存成功后显示提示
