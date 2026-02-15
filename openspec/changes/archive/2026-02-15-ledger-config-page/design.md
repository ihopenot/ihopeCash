## Context

IhopeCash 是一个基于 Beancount 的个人记账系统，使用 FastAPI 提供 Web 界面。当前 `main.bean`（账本主文件）和 `accounts.bean`（账户定义）位于项目根目录，只能通过手动编辑文件来管理。Web 配置页面（`/config`）已有 Tab 结构（基础配置、高级配置、修改密码），需要在其中新增"账本"Tab。

当前架构：
- `backend.py` 直接以 `open("main.bean")` 读写根目录文件
- `docker/entrypoint.sh` 中 Fava 指向 `/app/main.bean`
- `main.bean` 中的 include 路径以 `data/` 为前缀（如 `include "data/2026/_.bean"`）

## Goals / Non-Goals

**Goals:**
- 将 bean 文件统一归入 `data/` 目录，使数据与代码分离
- Web 启动时自动创建缺失的默认 bean 文件
- 在配置页面提供账本基本信息（名称、主货币）的可视化编辑
- 在配置页面提供账户的分类展示、新增和关闭功能
- 提供迁移脚本，平滑迁移已有数据

**Non-Goals:**
- 不支持删除或重命名已有账户
- 不支持编辑 main.bean 中的 include 语句
- 不支持在 Web 界面直接编辑 bean 文件原始文本
- 不做 Fava 功能的替代

## Decisions

### 1. Bean 文件解析策略：读取用 beancount.loader，写入用文本操作

**选择**: 混合模式 — 用 `beancount.loader.load_file()` 读取和解析 bean 文件，用文本操作（正则替换 + 文件追加）写入。

**原因**: beancount 库提供了可靠的解析能力（提取 options、Open/Close entries），但没有提供写入 API。直接操作文本文件对于 `option` 行替换和 `open`/`close` 指令追加来说足够简单可靠。

**替代方案**: 纯正则解析 — 虽然对简单场景可行，但可能遗漏 beancount 的边缘情况（如多文件 include、插件生成的 entries 等）。

### 2. 文件位置：bean 文件移至 data/ 目录

**选择**: `main.bean`、`accounts.bean` 均放在 `data/` 目录下。

**原因**: `data/` 目录已经是数据存放的标准位置（年份目录、balance.bean 都在其中），将账本核心文件也放入此目录使得数据管理更统一。迁移后 main.bean 的 include 路径也变得更简洁（无需 `data/` 前缀）。

### 3. 默认文件策略：启动时自动创建空白模板

**选择**: Web 启动时检测 `data/main.bean`、`data/accounts.bean`、`data/balance.bean`，不存在则创建默认内容。

**默认 main.bean**:
```beancount
option "title" "ihopeCash"
option "operating_currency" "CNY"

include "accounts.bean"
include "balance.bean"
```

**默认 accounts.bean**: 空文件。

**默认 balance.bean**: 空文件。

**原因**: 空白 accounts.bean 让用户通过 Web 界面从零开始配置账户，避免预置不必要的默认账户。

### 4. 前端账户校验：仅检测第二级名称开头

**选择**: 用户选择顶级类型（Assets/Liabilities/Income/Expenses/Equity）后输入路径，仅校验路径第一段（即拼接后的第二级）是否以英文字母或数字开头。后续层级允许中文。

**校验正则**: `/^[A-Za-z0-9]/` 应用于路径的第一个 `:` 之前的部分。

**原因**: Beancount 要求第二级名称以 ASCII 字母或数字开头，但后续层级可以包含中文。只做最小必要的校验，避免过度限制。

### 5. UI 布局：账本作为配置页面的第一个 Tab

**选择**: 在 `/config` 页面的 Tab 栏中，将"账本"放在第一个位置，其后依次为"基础配置"、"高级配置"、"修改密码"。

**原因**: 账本信息和账户是系统最核心的配置，放在第一个 Tab 便于用户首次使用时快速配置。

### 6. 账户关闭：追加 close 指令到 accounts.bean

**选择**: 关闭账户时在 `accounts.bean` 末尾追加 `YYYY-MM-DD close Account:Name` 行，日期默认当天。

**原因**: Beancount 的 close 指令表示账户在指定日期后不再接受新交易。追加到同一文件保持数据集中。不物理删除 open 行，因为历史交易仍需要它。

## Risks / Trade-offs

- **[并发写入]** → Web 端修改 bean 文件时如果 Fava 同时在读取可能导致竞争条件。缓解：单 worker 部署 + 文件写入为原子操作（先写临时文件再 rename，或内容足够小可忽略）。
- **[迁移失败]** → 已有用户的 main.bean 可能包含非标准的 include 路径。缓解：迁移脚本做幂等设计，检测已迁移状态；失败时给出明确错误信息。
- **[beancount 版本兼容]** → 不同版本的 beancount loader API 可能有差异。缓解：锁定 beancount 版本依赖。
- **[空 accounts.bean 体验]** → 全新安装时账本为空，导入前必须先配置账户。缓解：可在后续版本添加初始化引导。

## Migration Plan

1. 提供 `migrate.py` 迁移脚本，执行以下操作：
   - 检测根目录是否存在 `main.bean` 和 `accounts.bean`
   - 将文件移动到 `data/` 目录
   - 修正 `data/main.bean` 中的 include 路径（去掉 `data/` 前缀）
   - 如果 `accounts.bean` 的 include 路径也需调整则一并处理
2. 脚本幂等：如果文件已在 `data/` 下则跳过
3. Docker 部署时可在 entrypoint.sh 中先执行迁移脚本

## Open Questions

（已在探索阶段全部明确，无遗留问题）
