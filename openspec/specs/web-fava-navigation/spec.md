## ADDED Requirements

### Requirement: Web 导航栏必须包含 Fava 账本入口
Web 界面的顶部导航栏 SHALL 在"导入"和"配置"按钮旁边添加"账本"按钮，链接到 Fava 页面。

#### Scenario: 导航栏显示账本按钮
- **WHEN** 用户访问 Web 界面的任意页面（首页或配置页）
- **THEN** 导航栏显示"账本"按钮，样式与其他导航按钮一致

#### Scenario: 点击账本按钮跳转到 Fava
- **WHEN** 用户点击导航栏的"账本"按钮
- **THEN** 浏览器在新标签页中打开 `/fava/` 路径

#### Scenario: 导航栏在所有页面保持一致
- **WHEN** 用户在 index.html 或 config.html 页面
- **THEN** 导航栏的按钮布局和样式完全一致，均包含"导入"、"配置"、"账本"三个入口
