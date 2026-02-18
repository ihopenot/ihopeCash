## Context

当前 IhopeCash 的导入流程是一体化的 7 步流程，用户点击"开始导入"后从邮件下载到归档全部自动完成。这种设计在简单场景下可用，但存在以下问题：

1. 用户无法在下载后、导入前检查原文件是否正确
2. 不支持本地文件上传，只能通过邮件获取账单
3. 归档时机由系统决定，用户无法控制
4. 撤销操作会同时回退 rawdata 和 data 中的变更，无法选择性保留原文件
5. rawdata/ 被 git 跟踪，导致 git 状态同时受原文件和导入结果影响

后端使用 FastAPI + subprocess 调用 beancount 工具链，前端为 Tailwind CSS + 原生 JS 的单页应用。

## Goals / Non-Goals

**Goals:**
- 将导入流程拆分为三个用户可控阶段：获取原文件、导入账单、归档
- 支持本地文件上传（多文件、拖拽）
- 允许用户在导入前查看原文件识别结果
- 允许用户自定义归档提交说明
- 撤销时可选择是否清空原文件
- rawdata 与 git 解耦，git 状态只反映导入结果

**Non-Goals:**
- 不改变 beancount 工具链本身（bean-identify, bean-extract, bean-file）
- 不改变邮件下载的核心逻辑（mail.py）
- 不改变认证系统
- 不改变配置管理流程
- 不做数据迁移（不处理已有仓库中 rawdata 被 git 跟踪的历史）

## Decisions

### 1. rawdata/ 加入 .gitignore

**决定**: 在 `git_ensure_repo()` 创建 .gitignore 时，同时写入 `rawdata/` 规则。

**理由**: rawdata 是临时中转区，不应参与版本管理。将其从 git 中移除后：
- `git_is_clean()` 只反映导入产生的变更（data/ 和 archive/）
- 撤销操作逻辑更清晰：git 回退是 git 的事，rawdata 清理是文件系统的事
- 导入前检查 `git_is_clean()` 不会被新下载的文件干扰

**替代方案**: 保持 rawdata 被 git 跟踪，用 `git checkout -- data/` 实现选择性回退。放弃此方案是因为 git 操作变得复杂且容易出错。

### 2. 撤销实现：git 回退 + 可选文件清理

**决定**: `POST /api/ledger-discard` 接收 `include_rawdata` 参数。
- 始终执行 `git checkout -- .` + `git clean -fd` 回退 git 跟踪的变更
- 当 `include_rawdata=true` 时，额外清空 rawdata/ 目录下的所有文件

**理由**: rawdata 不在 git 中，git 回退不会影响它。清空 rawdata 是独立的文件系统操作，简单可靠。

### 3. 三阶段复用同一个执行日志区域

**决定**: 邮件下载、导入、归档三个操作共用页面底部的执行日志区域，通过 WebSocket 推送进度。

**理由**: 避免 UI 过于复杂。三个阶段不会同时执行，复用日志区域既节省空间又保持一致体验。每次新操作开始时清空日志。

### 4. 导入前检查工作区状态

**决定**: 用户点击"开始导入"时，前端调用 `GET /api/ledger-status` 检查。若 `is_clean=false`，弹窗提示"有未归档的变更，是否先归档？"，提供"先归档再导入"和"取消"两个选项。

**理由**: 不归档直接导入会把新旧变更混在一起，无法区分。不提供"跳过归档继续导入"选项，避免用户误操作。

### 5. 文件上传使用 FastAPI UploadFile

**决定**: `POST /api/rawdata/upload` 接收 `multipart/form-data`，使用 `List[UploadFile]` 参数。文件直接保存到 rawdata/ 目录，保留原始文件名。

**理由**: FastAPI 原生支持，python-multipart 依赖已存在。文件名保留原始名称是因为 beancount importer 依赖文件名进行识别。

**安全考虑**: 限制单文件最大 50MB（与 nginx 配置一致），校验文件名不含路径遍历字符。

### 6. bean-identify 结果解析

**决定**: `GET /api/rawdata/files` 端点同时返回文件列表和 bean-identify 结果。后端调用 `bean_identify()` 并解析其文本输出，将每个文件与其对应的 importer 名称关联。

**bean-identify 输出格式**:
```
**** /path/to/rawdata/wechat.csv
     Importer:    wechat
```

解析逻辑：按 `****` 分段，提取文件路径和 importer 名称。未识别的文件标记为 null。

### 7. 归档 API 设计

**决定**: `POST /api/archive` 接收 `{message: "提交说明"}`，执行：
1. `bean_archive()`（bean-file 归档原文件到 archive/）
2. `git add .` + `git commit -m "<用户提交说明>"`

**理由**: 将归档与 git 提交合并为一个原子操作，避免中间状态。提交说明由用户填写，替代原来自动生成的"账期 YYYY-MM"格式。

### 8. 导入步骤缩减为 5 步

**决定**: `POST /api/import` 的执行步骤变为：
1. 识别文件（bean-identify）
2. 创建目录/追加文件
3. 提取交易（bean-extract）
4. 记录余额断言
5. 写入账期（.ledger-period）

去掉原来的 Step 1（git commit 上期）和 Step 7（归档）。

**理由**: git commit 的时机改为归档时由用户主动触发；邮件下载移到获取原文件阶段。导入前如果有未归档变更，由前端检查并引导用户先归档。

## Risks / Trade-offs

- **[用户可能忘记归档]** → 状态栏持续显示"有未归档变更"提醒，导入前强制检查
- **[rawdata 文件名冲突]** → 上传同名文件时覆盖旧文件（bean-identify 会重新识别）
- **[bean-identify 输出格式变化]** → 解析逻辑做容错处理，无法解析时返回原始文本
- **[大文件上传]** → nginx 已配置 50MB 限制，后端也做校验
