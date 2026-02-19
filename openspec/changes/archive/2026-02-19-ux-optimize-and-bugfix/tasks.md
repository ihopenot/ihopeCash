## 1. 自动滚动到执行日志区

- [x] 1.1 修改 `web/static/index.html` 中 `showProgressSection()` 函数，在取消隐藏后调用 `progressSection.scrollIntoView({ behavior: 'smooth', block: 'start' })`

## 2. 账本状态栏手动刷新按钮

- [x] 2.1 在 `web/static/index.html` 的账本状态栏 HTML 中，撤销按钮之前添加刷新图标按钮（SVG 刷新图标），使用 Tailwind 样式
- [x] 2.2 在 JavaScript 中获取刷新按钮 DOM 元素，绑定 click 事件调用 `loadLedgerStatus()`
- [x] 2.3 在 `style.css` 中添加刷新按钮的旋转动画（`spin` keyframes），点击时短暂旋转提供加载反馈

## 3. 应用启动时初始化 git 仓库

- [x] 3.1 修改 `web/app.py` 的 `startup_event()` 函数，在 `ensure_default_bean_files()` 之后创建 `BillManager` 实例并调用 `git_ensure_repo()`
