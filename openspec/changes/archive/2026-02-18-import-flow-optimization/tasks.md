## 1. Git 配置与基础设施

- [x] 1.1 修改 `git_ensure_repo()` 中 .gitignore 的创建逻辑，新增 `rawdata/` 规则
- [x] 1.2 在 BillManager 中新增 `clear_rawdata()` 方法，清空 rawdata/ 目录下所有文件
- [x] 1.3 修改 `git_discard_changes()` 方法，新增 `include_rawdata` 参数，支持可选清空 rawdata

## 2. 后端 - 原文件管理 API

- [x] 2.1 在 BillManager 中新增 `bean_identify_parsed()` 方法，解析 bean-identify 输出为结构化数据
- [x] 2.2 新增 `POST /api/rawdata/download-email` 端点，触发邮件下载，支持 WebSocket 进度推送
- [x] 2.3 新增 `POST /api/rawdata/upload` 端点，接收 multipart/form-data 多文件上传，包含文件名安全校验和大小限制
- [x] 2.4 新增 `GET /api/rawdata/files` 端点，返回文件列表及 bean-identify 识别结果
- [x] 2.5 新增 `DELETE /api/rawdata/files/{name}` 端点，删除指定原文件，包含路径遍历校验

## 3. 后端 - 导入流程改造

- [x] 3.1 修改 `import_month_with_progress()` 方法，去掉 git commit、邮件下载、归档步骤，流程缩减为 5 步
- [x] 3.2 修改 `POST /api/import` 端点，去掉 passwords 参数
- [x] 3.3 修改 TaskManager 中导入任务的创建逻辑，适配新的 5 步流程

## 4. 后端 - 归档 API

- [x] 4.1 在 BillManager 中新增 `archive_with_commit(message, progress_callback)` 方法
- [x] 4.2 新增 `POST /api/archive` 端点，接收提交说明参数，执行归档并 git commit，支持 WebSocket 进度推送

## 5. 后端 - 状态与撤销 API 改造

- [x] 5.1 修改 `GET /api/ledger-status` 端点，返回值新增 `is_clean` 字段
- [x] 5.2 修改 `POST /api/ledger-discard` 端点，接收 `include_rawdata` 参数

## 6. 前端 - 页面布局重构

- [x] 6.1 重构 index.html 页面结构为三区域布局（获取原文件、导入账单、归档）
- [x] 6.2 实现"获取原文件"区域：邮件下载子区域（含附件密码输入和下载按钮）
- [x] 6.3 实现"获取原文件"区域：本地上传子区域（拖拽区域 + 文件选择按钮，支持多文件）
- [x] 6.4 实现"获取原文件"区域：原文件列表（显示文件名、导入器名称、删除按钮）
- [x] 6.5 实现"导入账单"区域：迁移年月选择、模式选择、余额输入表单（去掉密码输入）
- [x] 6.6 实现"归档"区域：提交说明输入框 + 归档按钮，根据工作区状态启用/禁用

## 7. 前端 - 交互逻辑

- [x] 7.1 实现撤销弹窗改造：从 confirm() 改为自定义对话框，包含"同时清空原文件目录"复选框
- [x] 7.2 实现导入前检查逻辑：点击"开始导入"时检查工作区状态和 rawdata 文件
- [x] 7.3 实现邮件下载、导入、归档三个操作共用执行日志区域的逻辑
- [x] 7.4 实现各操作完成后的自动刷新：文件列表刷新、状态栏刷新、归档按钮状态更新
- [x] 7.5 确保页面所有引导文字、提示、按钮文案使用中文
