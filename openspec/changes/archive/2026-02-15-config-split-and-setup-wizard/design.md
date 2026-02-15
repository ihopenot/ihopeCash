## Context

当前 IhopeCash 的所有配置集中在 `config.yaml` 中，Docker 部署时直接挂载该文件到宿主机。这意味着邮箱密码、账户映射等敏感业务配置都暴露在宿主机上。同时首次部署需要手动编辑 YAML 文件，用户体验差。

现有架构中，`Config` 类（config.py）在 `config.yaml` 不存在时会自动创建默认配置文件。所有依赖 `Config()` 的模块（web/app.py、web/auth.py、web/tasks.py、beancount_config.py）都会触发这一行为。

## Goals / Non-Goals

**Goals:**
- 将部署相关配置（路径、Web 服务）与业务配置分离，Docker 只需挂载部署配置
- 提供首次运行引导页，引导用户通过 Web 完成所有业务配置
- 引导过程中所有修改为临时状态，最终确认后一次性落地
- 账户选择使用下拉组件，支持选择现有账户或内联新增

**Non-Goals:**
- 不改变现有配置项的语义或结构（拆分只是物理位置变化）
- 不修改 Beancount 导入器逻辑
- 不重构现有配置编辑页面（config.html）的整体架构，仅局部调整 HSBC HK、卡号映射、交易摘要过滤
- 不支持多用户或权限系统

## Decisions

### D1: 配置文件拆分策略

**选择**: 新增 `env.yaml` 存放 `system.*` 和 `web.*`，`config.yaml` 存放剩余业务配置

**理由**: `system` 下的路径配置和 `web` 下的服务配置是部署层面的，与具体业务无关。分离后 Docker 只挂载 `env.yaml`，业务配置完全封闭在容器内通过 Web 管理。

**替代方案**:
- 环境变量：适合少量简单配置，但 Web 配置有嵌套结构，环境变量表达不便
- 将所有配置都移到数据库：改动过大，且与 Beancount 生态（基于文件）不一致

### D2: Config 类双文件加载合并

**选择**: `Config.__init__(config_file="config.yaml", env_file="env.yaml")`，先加载 `env.yaml`（必须存在），再加载 `config.yaml`（可不存在），`env.yaml` 中的 `system` 和 `web` 字段始终覆盖 `config.yaml` 中的对应字段。

**加载流程**:
1. 加载 `env.yaml` → 不存在则 `raise FileNotFoundError`
2. 加载 `config.yaml` → 不存在则 `self.setup_required = True`，使用内存默认值，不写文件
3. 合并：`env` 的 `system`/`web` 覆盖 `config` 的对应字段
4. 合并默认值（_merge_defaults）

**理由**: 保持 Config 类的单一入口不变，所有消费方（web/app.py、beancount_config.py 等）无需修改调用方式。`env.yaml` 中的配置优先级最高，确保部署配置不被 Web 编辑覆盖。

### D3: 首次运行判断与引导拦截

**选择**: `config.yaml` 不存在时 `setup_required = True`，Web 中间件拦截所有非引导路径重定向到 `/setup`

**允许通过的路径**:
- `/login`, `/api/auth/login`（登录，引导页需要认证）
- `/setup`, `/api/setup/*`（引导页及其 API）
- `/static/*`（静态资源）

**引导页需要登录**: 密码来自 `env.yaml` 的 `web.password`，确保安全性。

**引导完成后**: 创建 `config.yaml`，设置 `setup_required = False`，`/setup` 路径不再可访问（返回 404 或重定向到首页）。

### D4: 引导页临时状态管理

**选择**: 纯前端状态管理（JavaScript 对象），不使用后端会话

**数据结构**:
```javascript
const setupState = {
    currentStep: 0,
    tempAccounts: [],    // { account_type, path, currencies, comment }
    config: { ... }      // 与 config.yaml 结构一致的临时配置
};
```

**理由**: 引导是单次操作，不需要持久化中间状态。前端状态管理简单直接，避免引入后端会话机制。用户刷新页面会丢失进度，但首次配置场景下这是可接受的。

### D5: 账户选择下拉组件

**选择**: 下拉列表 = 服务端现有账户（`GET /api/ledger/accounts`）+ 前端 `tempAccounts`。不允许手动输入，只能从下拉选择或通过新增表单创建。

**新增表单**: 内联在下拉旁边，提交后账户加入 `tempAccounts`（不调后端 API），自动选中新增账户。

**理由**: 严格的下拉选择保证配置中的账户名格式正确。临时账户在确认时和配置一起批量写入 `accounts.bean`，保持原子性。

### D6: HSBC HK 前端拆分

**选择**: 前端展示为三条独立配置项：`use_cnh` 开关 + `One` 账户下拉 + `PULSE` 账户下拉。后端 `POST /api/setup/complete` 接收时合并回 `hsbc_hk: { use_cnh: bool, account_mapping: { One: ..., PULSE: ... } }` 格式写入 config.yaml。

同样的拆分逻辑也应用到 config.html 的高级配置中，替换当前的 JSON textarea。

### D7: 卡号账户映射三栏设计

**选择**: 三栏输入 → 分类下拉（5种 Beancount 类型）+ 自定义中间名称 + 4位字符串。系统自动在中间名称末尾补冒号（如果用户没有输入的话），实时预览拼接后的完整账户名。

**校验规则**:
- 4位字符串：长度必须为4，允许数字和大写字母
- 中间名称：每段（冒号分隔）首字母必须大写或数字
- 拼接结果：必须是合法 Beancount 账户名

**后端存储格式不变**: `card_accounts: { Assets: { BOC:Card: ['1234'] } }`

**前端 → 后端转换**: 三栏值 `[Assets, BOC:Card, 1234]` 转为嵌套结构。注意同一分类下可能有多个中间名称，同一中间名称下可能有多个卡号。

### D8: Setup API 设计

**新增端点**:

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/api/setup/status` | No | 返回 `{ setup_required: bool }` |
| GET | `/api/setup/defaults` | Yes | 返回默认配置（含交易摘要过滤默认值） |
| POST | `/api/setup/complete` | Yes | 接收完整配置 + 新增账户，一次性写入 |

`/api/setup/status` 不需要认证，因为前端需要在登录前判断是否需要引导（决定登录后跳转到引导页还是首页）。

`POST /api/setup/complete` 请求体:
```json
{
  "config": { /* 业务配置，不含 system 路径和 web */ },
  "new_accounts": [
    { "account_type": "Assets", "path": "Alipay:Balance", "currencies": "", "comment": "" }
  ]
}
```

处理流程:
1. 校验 `setup_required == True`，否则返回 403
2. 校验配置结构合法性
3. 校验每个 new_account 的账户名合法性
4. 去重 new_accounts（可能多个步骤引用了同一账户）
5. 写入 `config.yaml`
6. 追加 `accounts.bean`（仅新增不在已有列表中的账户）
7. 重新加载 Config，`setup_required = False`

## Risks / Trade-offs

**[风险] 引导页刷新丢失进度** → 可接受，首次配置场景下用户可以重新填写。未来可考虑 localStorage 暂存，但不在本次范围内。

**[风险] beancount_config.py 在模块导入时执行 Config()** → 在引导完成前，如果 bean 命令被调用，Config() 会使用默认值。但引导期间不会触发导入任务，所以这条路径不会被执行。安全。

**[风险] env.yaml 与 config.yaml 中 system/web 字段的冲突** → env.yaml 始终优先覆盖。`update_from_web()` 已有保护逻辑跳过 web 和 system 路径字段，不会通过 Web 编辑覆盖 env 配置。

**[风险] 现有用户升级兼容性** → 现有用户已有 config.yaml。需要：(1) 提供 env.example.yaml 模板；(2) 文档说明从现有 config.yaml 中提取 system/web 到 env.yaml；(3) Config 加载时如果 config.yaml 已存在，不触发引导流程，正常运行。

**[取舍] 引导页需要登录** → 增加了一步操作，但保证了安全性。密码来自 env.yaml，部署者在创建 env.yaml 时已设定。

## Migration Plan

1. 创建 `env.example.yaml` 模板文件
2. 修改 Config 类支持双文件加载
3. 修改 docker-compose.yml 和 entrypoint.sh
4. 实现引导页前端和后端 API
5. 修改 config.html 的 HSBC HK、卡号映射、交易摘要过滤部分
6. 更新 README 说明新的部署流程

**回滚策略**: 如果需要回滚，将 `env.yaml` 中的 `system` 和 `web` 字段合并回 `config.yaml`，恢复 docker-compose.yml 挂载 config.yaml 即可。

## Open Questions

（无，所有关键决策已在 explore 阶段与用户确认）
