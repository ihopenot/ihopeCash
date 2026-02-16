## Context

项目经过全流程测试（从零 clone → Docker 部署 → 配置引导 → 账单导入），发现 12 个阻断/高危/中等问题。核心痛点是：目录结构分散导致 Docker 需要挂载多个 volume，且新用户首次部署时权限、文件缺失等问题频发。

当前目录结构：
```
/app/
├── data/           (volume 挂载)  ← bean 文件
├── rawdata/        (volume 挂载)  ← 原始账单
├── archive/        (volume 挂载)  ← 归档数据
├── certs/          (volume 挂载)  ← SSL 证书
├── env.yaml        (volume 挂载)  ← 环境配置
├── config.yaml     (未挂载!)      ← 业务配置，容器重启丢失
```

## Goals / Non-Goals

**Goals:**
- 新用户 clone 仓库后能一次性跑通 `docker compose up`
- 数据目录合并为单一挂载点，简化部署
- 所有前端交互问题修复，引导和配置体验一致
- Git 版本管理范围覆盖整个 beancount 工作区

**Non-Goals:**
- 不重构 Config 类的 API 接口
- 不改动邮件下载逻辑（#12 已单独修复）
- 不引入新的依赖或工具
- 不改变 env.yaml 和 certs 的挂载方式
- 不设计旧结构迁移策略

## Decisions

### 决策 1: 目录结构重组 + 路径配置简化

**新结构：**
```
/app/
├── data/                    (唯一数据 volume)
│   ├── config.yaml          ← 业务配置（持久化）
│   └── beancount/           ← beancount 工作区 (beancount_path)
│       ├── .git/            ← git 仓库（管理整个 beancount/）
│       ├── data/            ← bean 文件 (data_path，硬编码)
│       │   ├── main.bean
│       │   ├── accounts.bean
│       │   ├── balance.bean
│       │   └── 2024/
│       ├── rawdata/         ← 原始账单 (rawdata_path，硬编码)
│       └── archive/         ← 归档数据 (archive_path，硬编码)
├── certs/                   (volume 挂载，不变)
├── env.yaml                 (volume 挂载，不变)
```

**路径配置简化：** config 中只保留一个 `beancount_path` 配置项，下级路径全部硬编码派生：

```python
# config.py 默认值
system:
    beancount_path: "data/beancount"

# 属性（硬编码派生，不可配置）
data_path     = beancount_path + "/data"
rawdata_path  = beancount_path + "/rawdata"
archive_path  = beancount_path + "/archive"
```

移除 env.yaml 中对路径的覆盖逻辑。原 config.py 中的 `_PROTECTED_SYSTEM_KEYS` 和相关 pop 逻辑一并清理。

`config_file` 默认值改为 `"data/config.yaml"`。

### 决策 2: Docker 权限 — 移除 appuser，全程 root

删除 Dockerfile 中 `useradd`、`chown`、`USER appuser` 相关行。此项目为个人/小团队自部署工具，root 运行可接受。

### 决策 3: Docker 只暴露 HTTPS 端口

`docker-compose.yml` 移除 80 端口映射，只保留 443。Nginx HTTP server block 保留（容器内部用），但不对外暴露。

### 决策 4: Entrypoint 启动流程修复

1. 创建必要子目录（`data/beancount/data`、`data/beancount/rawdata`、`data/beancount/archive`）
2. 在启动 Fava 前，检查 `main.bean` 是否存在，不存在则 `touch` 创建空占位文件
3. Fava 启动后不做 30 秒阻塞等待，直接后台启动继续执行

### 决策 5: CSP 允许 Tailwind CDN

`nginx.conf` CSP 头的 `script-src` 和 `style-src` 加上 `https://cdn.tailwindcss.com`。

### 决策 6: 前端联动修复

**余额账户联动（#9）：** `setup.html` 的 `getAllAccounts()` 中增加遍历 `setupConfig.card_accounts`，将卡号映射中拼出的完整账户名加入账户列表。

**配置页下拉选择（#10）：** `config.html` 中：
- 页面加载时调用 `/api/ledger/accounts` 获取账户列表
- 将通用账户（默认支出/收入、HSBC One/PULSE）和余额账户的 `<input type="text">` 替换为 `<select>` + "新增"按钮
- 复用与 setup.html 类似的 `getAllAccounts()` + `refreshAllSelects()` 模式

**卡号映射冒号（#11）：** `config.html` 的 `renderCardAccounts()` 中 `addCardAccountRow(category, middleName.replace(/:$/, ''), ...)` 去尾冒号。

### 决策 7: Git 管理范围扩展到 beancount 工作区

`backend.py` 中 git 操作的 `cwd` 从 `self.data_path` 改为 `self.beancount_path`（即 `data/beancount/`）。BillManager 初始化新增 `self.beancount_path = config.beancount_path`，所有 git 方法中 `cwd` 改为 `self.beancount_path`。

### 决策 8: beancount_config.py 纳入 Git

项目根目录 `.gitignore` 移除 `beancount_config.py` 行，执行 `git add beancount_config.py`。

## Risks / Trade-offs

- **[风险] 容器以 root 运行** → 对于自部署个人工具可接受，未来可重新引入非 root 用户
- **[风险] CDN 引用的 Tailwind** → CSP 放开了 `cdn.tailwindcss.com`，长期应切换到本地构建
- **[风险] 移除 HTTP 端口** → 用户如果习惯用 HTTP 访问会连不上
