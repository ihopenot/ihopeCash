## Context

导入界面 (`web/static/index.html`) 是一个 vanilla JS 单页应用，使用 Tailwind CSS。页面从上到下依次排列：账本状态栏、获取原文件、导入账单、归档、执行日志。执行日志区域 (`#progressSection`) 位于页面最底部，默认隐藏。

后端 (`web/app.py`) 在 `startup_event` 中仅调用 `ensure_default_bean_files()` 创建默认 bean 文件，未初始化 git 仓库。`BillManager.git_is_clean()` 在 `.git` 不存在时返回 `True`，导致状态栏永远显示"已同步"。

## Goals / Non-Goals

**Goals:**
- 后台操作按钮点击后自动滚动到日志区，用户无需手动滚动
- 状态栏可手动刷新，用户能主动获取最新状态
- 应用启动即初始化 git 仓库，状态检测从一开始就正常工作

**Non-Goals:**
- 不改变日志区的展示样式或布局位置
- 不改变 git 仓库的初始化逻辑本身（`git_ensure_repo` 方法不变）
- 不改变现有的自动刷新逻辑（导入/归档完成后仍自动刷新）

## Decisions

### 1. 自动滚动：在 `showProgressSection()` 中统一处理

在 `showProgressSection()` 函数中增加 `scrollIntoView({ behavior: 'smooth', block: 'start' })`。

**理由**：所有后台操作按钮（邮件下载、导入、归档）都通过此函数展示日志区，只需改一处。使用 `smooth` 行为提供平滑滚动体验，`block: 'start'` 让日志区出现在视口顶部。

**备选方案**：在每个按钮事件中单独调用 scroll —— 但这会导致重复代码且容易遗漏。

### 2. 手动刷新按钮：使用 SVG 刷新图标

在状态栏右侧（撤销按钮之前）添加一个小型刷新图标按钮，点击调用 `loadLedgerStatus()`。按钮始终可见，使用 Tailwind 样式与现有状态栏风格一致。

**理由**：图标按钮占空间小，与状态栏紧凑布局协调。始终可见是因为用户可能在任何状态下都想确认最新情况。

### 3. 启动时初始化 git：在 `startup_event` 中调用

在 `web/app.py` 的 `startup_event` 中，`ensure_default_bean_files()` 之后创建 `BillManager` 实例并调用 `git_ensure_repo()`。

**理由**：这是最简单直接的修复。`git_ensure_repo()` 方法本身已经有幂等逻辑（检查 `.git` 存在则跳过），放在启动时调用只执行一次，后续所有 `git_is_clean()` 调用都能正常工作。

**备选方案**：在 `git_is_clean()` 中懒初始化 —— 但这会让每次状态查询都有初始化检查开销，且语义不够清晰（is_clean 不应该有初始化副作用）。

## Risks / Trade-offs

- **[风险] `scrollIntoView` 在某些旧浏览器上 `smooth` 行为不支持** → 降级为瞬间滚动，功能不受影响
- **[风险] 启动时 git 不可用** → `git_ensure_repo()` 已有 `RuntimeError` 异常处理，应用启动会失败并提示安装 git，这是合理行为
