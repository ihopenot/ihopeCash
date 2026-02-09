## Why

当前 main.py 是交互式脚本,所有业务逻辑与 CLI 交互耦合在一起,无法用于 Web 应用或 API 服务。需要将核心业务逻辑提取到独立的后端模块,实现逻辑层与界面层分离,为未来的 Web 界面开发做准备。

## What Changes

- 创建新文件 `backend.py`,包含两个核心类:
  - `Config` 类: 封装配置文件读取和管理,替代现有的 `config.py` 全局变量方式
  - `BillManager` 类: 封装所有业务操作(邮件下载、目录管理、Beancount 命令调用、余额记录、完整工作流)
- 重构 `main.py`,改为使用 `backend.py` 提供的服务,保持 CLI 交互体验不变
- 保持 `mail.py` 和现有文件系统结构不变
- 所有 Beancount 数据管理方式保持不变

## Capabilities

### New Capabilities
- `backend-config`: 配置管理能力,支持加载、访问、未来扩展验证和热重载
- `backend-bill-operations`: 账单业务操作能力,包括下载、识别、提取、归档、目录管理、余额记录等所有核心功能

### Modified Capabilities
<!-- 没有修改现有能力的需求规格,只是重构实现 -->

## Impact

- **新增文件**: `backend.py`
- **修改文件**: `main.py` (使用新的 backend 模块)
- **弃用但保留**: `config.py` (向后兼容,可能被 backend.Config 内部使用)
- **无影响**: `mail.py`, `beancount_config.py`, 所有数据文件和目录结构
- **向后兼容**: CLI 使用方式和参数保持不变
- **未来扩展**: 为 Web API 接口预留架构基础
