## Context

IhopeCash 是一个基于 Beancount 的记账系统，账本数据存放在 `data/` 目录中。用户通过 Web 界面导入邮件账单，导入后会在 Fava 或编辑器中手动修改对账。目前 `data/` 目录没有版本控制，导入覆盖或误操作后无法恢复。

主项目 `.gitignore` 已忽略 `data/*`，说明设计意图是将数据与代码分离。

当前导入流程为 6 步（下载→识别→建目录→提取→余额→归档），由 `BillManager.import_month_with_progress()` 执行，通过 WebSocket 实时推送进度。

## Goals / Non-Goals

**Goals:**
- 为 data/ 目录建立独立 git 仓库，自动在每次导入前提交变更快照
- 用户在导入界面能看到当前正在编辑的账期
- 用户能通过撤销操作丢弃未提交的修改，回到上次导入后的状态

**Non-Goals:**
- 不提供 git 历史浏览或 diff 查看功能
- 不提供按文件或按月份的细粒度撤销
- 不管理 git 远程仓库（push/pull）
- 不更改现有 6 步导入逻辑本身

## Decisions

### Decision 1: data/ 使用独立 git 仓库

在 `data/` 目录内 `git init`，与主项目仓库完全独立。

**理由：**
- 代码变更与数据变更关注点不同，独立仓库保持 commit history 干净
- `.gitignore` 已在忽略 `data/*`，设计意图一致
- 撤销操作只影响数据，不会波及代码仓库

**替代方案：** 用主项目仓库管理 data/ —— 否决，因为代码和数据 commit 会混合，撤销风险大。

### Decision 2: 通过 `.ledger-period` 文件持久化当前账期

在 `data/.ledger-period` 中存储当前账期（如 `2026-02`），该文件通过 `data/.gitignore` 排除在 git 管理之外。

**写入时机：** 导入完成后写入本次选择的年月。
**删除时机：** 用户撤销变更时删除；检测到工作区 clean 且文件存在时也清理。
**读取时机：** 页面加载时通过 API 读取，用于状态栏展示。

**理由：** 简单可靠，服务重启后不丢失状态。相比从 git diff 推断账期更准确，相比存在后端内存或数据库中更轻量。

### Decision 3: git 操作通过 subprocess 调用系统 git 命令

不引入 GitPython 等第三方库，直接通过 `subprocess.run()` 调用 git CLI。

**理由：**
- 项目已有通过 subprocess 调用 bean-identify / bean-extract / bean-file 的模式
- 所需 git 操作非常简单（init、add、commit、checkout、clean、status）
- 无需新增依赖，Docker 镜像中已有 git

### Decision 4: 导入流程变为 7 步，Step 0 为 git 提交

在 `import_month_with_progress` 方法的现有 6 步之前插入 Step 0（git 自动提交），总步数变为 7。

**Step 0 逻辑：**
1. 检测 `data/.git` 是否存在，不存在则 `git init` + 首次全量提交
2. 检测工作区是否有变更（`git status --porcelain`）
3. 有变更则读取 `.ledger-period` 获取上一次账期，执行 `git add . && git commit -m "账期 YYYY-MM"`
4. 无变更则跳过
5. 提交完成后删除 `.ledger-period`（上一个账期已定稿）

**导入完成后：** 写入新的 `.ledger-period` 为本次选择的年月。

**理由：** 在导入之前提交确保了用户的手动修改被保存，导入引入的新数据在工作区中作为下一个编辑周期。

### Decision 5: 撤销操作使用 git checkout + git clean

撤销通过 `git checkout -- .` 恢复已跟踪文件 + `git clean -fd` 删除未跟踪文件实现全量回退。

**理由：** 用户明确要求全部撤销（非细粒度），这是最简单直接的方式。相比 `git reset --hard HEAD` 更安全（不移动 HEAD）。

### Decision 6: 新增两个 API 端点

- `GET /api/ledger-status`：返回账本状态（账期或 clean）
- `POST /api/ledger-discard`：执行撤销操作

两个端点都需要认证。ledger-discard 不需要请求体（全量撤销，无参数）。

### Decision 7: git 操作方法封装在 BillManager 中

在 `BillManager` 类中新增以下方法：
- `git_ensure_repo()` —— 检测并初始化 data git 仓库
- `git_commit_if_dirty(period: str)` —— 有变更时提交，commit message 包含账期
- `git_discard_changes()` —— 丢弃所有未提交变更
- `git_is_clean() -> bool` —— 检查工作区是否 clean
- `read_ledger_period() -> Optional[str]` —— 读取当前账期
- `write_ledger_period(period: str)` —— 写入当前账期
- `clear_ledger_period()` —— 清除账期文件

**理由：** BillManager 已经是所有账本操作的核心类，git 操作与之紧密关联。

## Risks / Trade-offs

- **[风险] git 未安装** → 在 `git_ensure_repo` 时检测，未安装则抛出明确错误提示。Docker 镜像确保包含 git。
- **[风险] 撤销操作不可逆** → 通过前端二次确认弹窗缓解。确认弹窗需明确告知风险。
- **[风险] 首次初始化时 data/ 下已有大量历史数据** → 首次 commit 可能较慢，通过进度回调告知用户"正在初始化版本管理"。
- **[权衡] commit message 只包含账期，不包含详细变更** → 简洁优先，用户可通过 `git log` / `git diff` 查看详情。
- **[权衡] .ledger-period 与 git 状态可能不一致** → API 返回状态时同时检查 git clean 状态，如果 clean 但 .ledger-period 存在则清理。
