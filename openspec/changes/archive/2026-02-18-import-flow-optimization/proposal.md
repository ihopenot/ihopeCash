## Why

当前的导入流程是一键式的 7 步流程（git提交→邮件下载→识别→创建目录→提取→余额→归档），用户无法在中间步骤介入。实际使用中，用户需要在下载/上传原文件后先查看文件识别结果，确认无误后再执行导入，最后手动决定何时归档。此外，当前不支持本地文件上传，只能通过邮件获取账单文件。撤销操作也缺乏对原文件目录的细粒度控制。

## What Changes

- 将一体化 7 步导入流程拆分为三个独立阶段：获取原文件、导入账单、归档文件
- 新增本地文件上传功能（支持多文件、拖拽上传）
- 邮件下载独立为单独的操作端点
- 新增原文件管理 API（列表、上传、删除、识别）
- 新增归档 API（bean-file + git commit，支持自定义提交说明）
- 将 rawdata/ 从 git 跟踪中移除（加入 .gitignore）
- **BREAKING**: 改造 `POST /api/import` 接口，去掉下载和归档步骤，导入步骤从 7 步变为 5 步
- **BREAKING**: 改造 `POST /api/ledger-discard` 接口，新增 `include_rawdata` 参数支持选择性撤销
- 改造撤销弹窗，新增"同时清空原文件目录"选项
- 导入前检查 git 工作区状态，有未归档变更时提示用户先归档
- 前端页面重构为三区域单页布局
- 页面引导文字使用中文

## Capabilities

### New Capabilities
- `rawdata-management`: 原文件管理功能，包括邮件下载、本地文件上传、文件列表查看（含 bean-identify 识别结果）、单个文件删除
- `archive-operation`: 独立的归档操作，包括 bean-file 归档和 git commit，支持用户自定义提交说明

### Modified Capabilities
- `web-import-interface`: 前端页面从一体化表单重构为三区域布局（获取原文件、导入账单、归档），撤销弹窗增加原文件目录选项，导入前增加未归档变更检查
- `backend-bill-operations`: 导入流程从 7 步缩减为 5 步（去掉下载和归档），新增独立的归档方法
- `git-data-versioning`: rawdata/ 加入 .gitignore 不再被 git 跟踪，撤销操作支持可选清空 rawdata
- `ledger-status-bar`: 撤销弹窗从简单确认改为包含复选框的对话框
- `realtime-progress-tracking`: 导入进度从 7 步变为 5 步，邮件下载和归档操作复用执行日志区域但使用独立的进度推送

## Impact

- **后端 API**: 新增 4 个端点（rawdata 管理），新增 1 个端点（归档），改造 2 个端点（import、discard）
- **前端**: index.html 大幅重构，新增文件上传拖拽区域、原文件列表、归档区域
- **后端**: backend.py 新增 rawdata 文件管理方法和独立归档方法，改造导入流程
- **Git 配置**: beancount 仓库 .gitignore 新增 rawdata/ 规则
- **依赖**: python-multipart 已在 web/requirements.txt 中，无需新增依赖
