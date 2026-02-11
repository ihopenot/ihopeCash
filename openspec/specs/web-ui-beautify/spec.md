## Requirements

### Requirement: 所有页面使用 Tailwind CDN

系统 SHALL 在所有 HTML 页面的 head 中引入 Tailwind CDN 脚本，替代手写的模拟 CSS。

#### Scenario: Tailwind CDN 引入
- **WHEN** 任意页面加载
- **THEN** 页面 head 中包含 `<script src="https://cdn.tailwindcss.com"></script>`
- **AND** 所有 Tailwind 工具类正常生效

#### Scenario: style.css 精简
- **WHEN** 页面加载 style.css
- **THEN** style.css 仅包含自定义样式（如 log-entry），不包含手写的 Tailwind 模拟类

### Requirement: 页面包含统一的顶部导航栏

系统 SHALL 在主页面和配置页面显示统一的顶部导航栏。

#### Scenario: 导航栏显示品牌名和导航链接
- **WHEN** 已认证用户打开主页面或配置页面
- **THEN** 页面顶部显示"IhopeCash"品牌名
- **AND** 显示"导入"和"配置"两个导航链接
- **AND** 显示"退出登录"按钮

#### Scenario: 当前页面导航高亮
- **WHEN** 用户在导入页面
- **THEN** "导入"导航链接显示为活跃状态（高亮）

#### Scenario: 导航链接跳转
- **WHEN** 用户点击"配置"导航链接
- **THEN** 页面跳转到 /config 路径

### Requirement: 登录页面美化

系统 SHALL 提供美化的登录页面，包含渐变背景和现代化表单样式。

#### Scenario: 登录页渐变背景
- **WHEN** 用户打开登录页
- **THEN** 页面显示渐变色背景
- **AND** 登录表单居中显示在卡片容器中

#### Scenario: 登录表单样式统一
- **WHEN** 登录页渲染
- **THEN** 密码输入框和登录按钮使用统一的 Tailwind 样式

### Requirement: 主页面布局美化

系统 SHALL 美化主页面的表单布局和日志显示区域。

#### Scenario: 表单卡片分区清晰
- **WHEN** 主页面渲染
- **THEN** 账单信息、附件密码、账户余额分别显示在独立卡片中
- **AND** 每个卡片有清晰的标题和分隔

#### Scenario: 日志区域状态颜色区分
- **WHEN** 进度日志显示不同状态的消息
- **THEN** success 状态使用绿色样式
- **AND** error 状态使用红色样式
- **AND** running 状态使用蓝色/黄色样式
