## Context

当前 main.py 是交互式 CLI 脚本,包含约100行代码,混合了业务逻辑、用户交互、文件操作和外部命令调用。用户希望开发 Web 应用,但现有架构无法复用业务逻辑。

现有依赖:
- mail.py: 提供 DownloadFiles() 函数下载邮件账单
- config.py: 全局字典 Config 加载 YAML 配置
- beancount CLI 工具: bean-identify, bean-extract, bean-file
- 文件系统: data/{year}/{month}/*.bean 结构

约束:
- 不改变数据存储方式和目录结构
- CLI 用户体验保持不变
- 不引入重量级框架或数据库

## Goals / Non-Goals

**Goals:**
- 将业务逻辑提取到独立 backend.py 模块
- 提供两个核心类: Config (配置管理) 和 BillManager (业务操作)
- main.py 变为薄的 CLI 包装层
- 为未来 Web API 预留扩展能力

**Non-Goals:**
- 不实现 Web 框架或 API 接口 (留待后续)
- 不改造 mail.py 或 Beancount 工具
- 不添加数据库或缓存层
- 不实现进度反馈机制 (用户明确不需要)

## Decisions

### 决策 1: 两个类的职责划分

**选择**: Config 类负责配置,BillManager 类负责所有业务操作

**理由**:
- 用户明确要求只维护两个类,避免过度设计
- Config 独立是因为未来可能扩展配置验证、热重载、环境变量覆盖等功能
- BillManager 聚合所有操作,避免类之间的依赖传递

**替代方案**: 单个 BillService 类包含配置 → 拒绝,因为配置管理有独立扩展需求

### 决策 2: Config 类自动创建默认配置

**选择**: 配置文件不存在时,自动创建默认配置并保存

**理由**:
- 改善首次运行体验,减少手动配置步骤
- 用户可以直接编辑生成的 config.yaml
- 默认值: data_path="data", rawdata_path="rawdata", archive_path="archive", balance_accounts=[]

**替代方案**: 抛出异常要求手动创建 → 拒绝,用户体验差

### 决策 3: BillManager 方法返回值设计

**选择**: 
- 单步操作 (如 bean_identify): 成功返回输出,失败抛异常
- 工作流方法 (如 import_month): 返回 `{"success": bool, "message": str, "data": dict}`

**理由**:
- 单步操作异常处理简单直接,CLI 可以直接捕获
- 工作流方法需要统一返回格式,方便未来 Web API 序列化为 JSON
- 避免部分成功部分失败的模糊状态

**替代方案**: 全部返回字典 → 过度设计,单步操作用异常更符合 Python 习惯

### 决策 4: subprocess 调用 Beancount 命令

**选择**: 使用 subprocess.run 封装命令调用,捕获 stdout/stderr

**理由**:
- Beancount 工具没有 Python API,必须调用命令行
- subprocess.run 支持超时、输出捕获、返回码检查
- shell=True 用于支持管道和重定向 (如 bean-extract 的 -- 语法)

**风险**: shell=True 有命令注入风险 → 缓解: 所有路径来自配置和用户输入,不拼接外部不可信数据

### 决策 5: main.py 重构策略

**选择**: 保留所有 input() 交互,用 backend 替换业务逻辑部分

**理由**:
- 用户要求 CLI 体验不变
- input() 是 CLI 特有的,不应该移到 backend
- main.py 负责交互,backend 负责执行

**示例**:
```
# 之前
os.system(f"bean-extract ...")

# 之后
manager.bean_extract(output_file)
```

### 决策 6: 与现有 config.py 的关系

**选择**: backend.Config 内部可以复用 config.py 的 load_config 逻辑,但作为独立类提供

**理由**:
- 不破坏向后兼容 (其他脚本可能依赖 config.py)
- Config 类提供更丰富的接口 (属性访问、save、重载)
- 未来可以完全替换 config.py 的实现

## Risks / Trade-offs

### 风险 1: Beancount 命令路径依赖
**风险**: bean-* 命令需要在 PATH 中,否则 subprocess 调用失败
**缓解**: 在 Config 中支持配置 beancount_bin_path,默认使用 PATH

### 风险 2: 并发安全
**风险**: 多个 BillManager 实例同时操作文件系统可能冲突
**缓解**: 当前为单用户工具,未来需要时可以添加文件锁

### 风险 3: 错误处理粒度
**风险**: import_month 工作流中任一步骤失败,前面步骤的副作用 (如创建目录) 不会回滚
**缓解**: 文档说明失败后需要手动清理,未来可以添加事务式回滚

### Trade-off 1: 去掉进度反馈
**取舍**: 用户不需要进度反馈机制,后端方法直接执行
**影响**: 长时间操作 (如下载) 期间无法感知进度,但简化了架构
**接受理由**: 用户明确表示不需要,CLI 中可以在调用前后打印提示

### Trade-off 2: 返回字典而非自定义类型
**取舍**: 工作流方法返回普通字典,不定义 Result 类
**影响**: 类型提示较弱,IDE 自动补全受限
**接受理由**: 轻量化优先,字典易于序列化为 JSON

## Migration Plan

### 实施步骤
1. 创建 backend.py,实现 Config 和 BillManager 类
2. 编写单元测试验证核心方法 (可选但推荐)
3. 重构 main.py,替换业务逻辑调用为 backend 方法
4. 测试 CLI 完整流程确保功能正常
5. 测试追加模式 (-A 参数)
6. 更新 README.md 文档 (可选)

### 回滚策略
- 保留原始 main.py 为 main.py.backup
- 如果重构后出现问题,直接恢复备份文件
- backend.py 为新增文件,删除即可

### 验收标准
- CLI 所有功能正常: 下载、导入、追加模式
- 命令行参数和交互流程不变
- 现有数据文件和目录结构正常读写
- 无回归问题

## Open Questions

无待解决问题,设计已明确。
