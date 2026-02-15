## MODIFIED Requirements

### Requirement: BillManager 必须管理年份目录结构
BillManager 类 SHALL 提供 `ensure_year_directory(year)` 方法,确保年份目录存在并正确配置。

#### Scenario: 创建新年份目录
- **WHEN** 调用 `manager.ensure_year_directory("2024")` 且目录不存在
- **THEN** 系统创建 data/2024 目录
- **THEN** 创建 data/2024/_.bean 文件
- **THEN** 在 `data/main.bean` 中添加 `include "2024/_.bean"` 语句（路径相对于 data 目录，不含 `data/` 前缀）

#### Scenario: 年份目录已存在
- **WHEN** 调用 `manager.ensure_year_directory("2024")` 且目录已存在
- **THEN** 系统不重复创建,直接返回目录路径
