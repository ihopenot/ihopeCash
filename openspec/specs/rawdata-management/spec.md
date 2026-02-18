## ADDED Requirements

### Requirement: 用户可以通过邮件下载原文件

系统 SHALL 提供 `POST /api/rawdata/download-email` 端点，触发邮件账单下载。该端点 MUST 要求认证。

#### Scenario: 成功下载邮件账单
- **WHEN** 客户端请求 `POST /api/rawdata/download-email`，请求体为 `{"passwords": ["abc", "123"]}`
- **THEN** 系统调用 `BillManager.download_bills(passwords)` 下载邮件账单到 rawdata/ 目录
- **AND** 返回 `{"success": true, "message": "邮件下载完成"}`

#### Scenario: 不传密码时使用空列表
- **WHEN** 客户端请求 `POST /api/rawdata/download-email`，请求体为 `{"passwords": []}`
- **THEN** 系统以空密码列表调用下载
- **AND** 正常执行下载流程

#### Scenario: 下载过程中通过 WebSocket 推送进度
- **WHEN** 邮件下载开始执行
- **THEN** 系统通过 WebSocket 向已连接的客户端推送进度消息
- **AND** 下载完成后推送成功消息，包含 rawdata/ 中的文件数量

#### Scenario: 下载失败
- **WHEN** 邮件下载过程发生错误
- **THEN** 返回 `{"success": false, "message": "<错误信息>"}`

#### Scenario: 未认证请求
- **WHEN** 未认证客户端请求该端点
- **THEN** 返回 401 状态码

### Requirement: 用户可以上传本地文件

系统 SHALL 提供 `POST /api/rawdata/upload` 端点，接收 multipart/form-data 格式的文件上传。该端点 MUST 要求认证。MUST 支持同时上传多个文件。

#### Scenario: 成功上传单个文件
- **WHEN** 客户端上传一个文件（如 wechat.csv）
- **THEN** 系统将文件保存到 rawdata/ 目录，保留原始文件名
- **AND** 返回 `{"success": true, "message": "上传完成", "files": ["wechat.csv"]}`

#### Scenario: 成功上传多个文件
- **WHEN** 客户端同时上传多个文件（如 wechat.csv, alipay.csv）
- **THEN** 系统将所有文件保存到 rawdata/ 目录
- **AND** 返回 `{"success": true, "message": "上传完成", "files": ["wechat.csv", "alipay.csv"]}`

#### Scenario: 同名文件覆盖
- **WHEN** 上传的文件名与 rawdata/ 中已有文件同名
- **THEN** 系统覆盖旧文件

#### Scenario: 文件名安全校验
- **WHEN** 上传的文件名包含路径遍历字符（如 `../etc/passwd`）
- **THEN** 系统拒绝该文件，返回 400 错误

#### Scenario: 文件大小超限
- **WHEN** 上传的单个文件超过 50MB
- **THEN** 系统拒绝该文件，返回 400 错误

#### Scenario: 未认证请求
- **WHEN** 未认证客户端请求该端点
- **THEN** 返回 401 状态码

### Requirement: 用户可以查看原文件列表及识别结果

系统 SHALL 提供 `GET /api/rawdata/files` 端点，返回 rawdata/ 中的文件列表以及 bean-identify 的识别结果。该端点 MUST 要求认证。

#### Scenario: rawdata 中有文件
- **WHEN** 客户端请求 `GET /api/rawdata/files`
- **AND** rawdata/ 目录中有文件
- **THEN** 系统调用 bean-identify 并解析输出
- **AND** 返回 `{"files": [{"name": "wechat.csv", "size": 12345, "importer": "微信账单导入器"}, {"name": "unknown.pdf", "size": 67890, "importer": null}]}`

#### Scenario: rawdata 为空
- **WHEN** 客户端请求 `GET /api/rawdata/files`
- **AND** rawdata/ 目录为空
- **THEN** 返回 `{"files": []}`

#### Scenario: bean-identify 执行失败时仍返回文件列表
- **WHEN** bean-identify 命令执行失败
- **THEN** 系统仍返回文件列表，但所有文件的 importer 字段为 null

#### Scenario: 未认证请求
- **WHEN** 未认证客户端请求该端点
- **THEN** 返回 401 状态码

### Requirement: 用户可以删除单个原文件

系统 SHALL 提供 `DELETE /api/rawdata/files/{name}` 端点，删除 rawdata/ 中的指定文件。该端点 MUST 要求认证。

#### Scenario: 成功删除文件
- **WHEN** 客户端请求 `DELETE /api/rawdata/files/wechat.csv`
- **AND** 该文件存在于 rawdata/ 目录中
- **THEN** 系统删除该文件
- **AND** 返回 `{"success": true, "message": "文件已删除"}`

#### Scenario: 文件不存在
- **WHEN** 客户端请求删除一个不存在的文件
- **THEN** 返回 404 错误

#### Scenario: 文件名安全校验
- **WHEN** 请求的文件名包含路径遍历字符（如 `../`）
- **THEN** 系统拒绝操作，返回 400 错误

#### Scenario: 未认证请求
- **WHEN** 未认证客户端请求该端点
- **THEN** 返回 401 状态码

### Requirement: 后端必须提供 bean-identify 结果解析功能

BillManager SHALL 提供 `bean_identify_parsed()` 方法，调用 bean-identify 并将文本输出解析为结构化数据。

#### Scenario: 成功解析识别结果
- **WHEN** 调用 `manager.bean_identify_parsed()`
- **AND** rawdata/ 中有可识别的文件
- **THEN** 返回字典，键为文件名，值为 importer 名称（如 `{"wechat.csv": "微信账单导入器"}`）

#### Scenario: 文件未被识别
- **WHEN** rawdata/ 中有文件但 bean-identify 无法识别
- **THEN** 该文件在返回字典中的值为 null

#### Scenario: rawdata 为空
- **WHEN** rawdata/ 目录为空
- **THEN** 返回空字典 `{}`

#### Scenario: bean-identify 命令失败
- **WHEN** bean-identify 命令执行失败
- **THEN** 返回空字典 `{}`，不抛出异常

### Requirement: 前端必须提供文件拖拽上传区域

系统 SHALL 在"获取原文件"区域提供拖拽上传区域，支持拖拽和点击选择两种方式上传文件。MUST 支持同时选择多个文件。

#### Scenario: 用户拖拽文件上传
- **WHEN** 用户将文件拖拽到上传区域
- **THEN** 上传区域高亮显示
- **AND** 松开后自动调用 `POST /api/rawdata/upload` 上传文件
- **AND** 上传完成后自动刷新原文件列表

#### Scenario: 用户点击选择文件
- **WHEN** 用户点击上传区域的"选择文件"按钮
- **THEN** 系统弹出文件选择对话框，允许选择多个文件
- **AND** 选择后自动上传并刷新列表

#### Scenario: 上传过程中显示状态
- **WHEN** 文件正在上传
- **THEN** 上传区域显示上传状态

### Requirement: 前端必须展示原文件列表

系统 SHALL 在"获取原文件"区域展示当前 rawdata/ 中的文件列表，包括文件名、识别的导入器名称和删除按钮。

#### Scenario: 有文件时显示列表
- **WHEN** rawdata/ 中有文件
- **THEN** 系统展示文件列表，每行显示文件名、对应的导入器名称（中文）、删除按钮

#### Scenario: 无文件时显示提示
- **WHEN** rawdata/ 中无文件
- **THEN** 显示"暂无原文件"提示

#### Scenario: 未识别的文件标记
- **WHEN** 某文件未被 bean-identify 识别
- **THEN** 导入器列显示"（未识别）"

#### Scenario: 删除文件后刷新列表
- **WHEN** 用户点击某文件的删除按钮
- **THEN** 系统调用 `DELETE /api/rawdata/files/{name}`
- **AND** 成功后自动刷新文件列表

#### Scenario: 邮件下载完成后刷新列表
- **WHEN** 邮件下载操作完成
- **THEN** 系统自动刷新原文件列表

#### Scenario: 文件上传完成后刷新列表
- **WHEN** 文件上传操作完成
- **THEN** 系统自动刷新原文件列表

### Requirement: 前端邮件下载区域包含附件密码输入

系统 SHALL 在"获取原文件"区域的邮件下载子区域中提供附件密码输入功能和下载按钮。

#### Scenario: 添加附件密码
- **WHEN** 用户点击"添加密码"按钮
- **THEN** 系统在密码列表末尾新增一个 password 类型输入框

#### Scenario: 删除附件密码
- **WHEN** 用户点击某行密码旁的删除按钮
- **THEN** 系统移除该行密码输入框

#### Scenario: 点击从邮件下载按钮
- **WHEN** 用户点击"从邮件下载"按钮
- **THEN** 系统收集密码列表
- **AND** 调用 `POST /api/rawdata/download-email`
- **AND** 下载过程中按钮禁用
- **AND** 进度显示在执行日志区域
