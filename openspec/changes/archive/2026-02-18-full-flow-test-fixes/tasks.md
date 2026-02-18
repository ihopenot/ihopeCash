## 1. Git 版本控制修复

- [x] 1.1 `.gitignore` 移除 `beancount_config.py` 行
- [x] 1.2 `git add beancount_config.py`

## 2. Config 路径重组

- [x] 2.1 `config.py` 默认配置中 `system` 节移除 `data_path`/`rawdata_path`/`archive_path`，新增 `beancount_path: "data/beancount"`
- [x] 2.2 `config.py` 新增 `beancount_path` 属性，返回 `system.beancount_path`
- [x] 2.3 `config.py` 修改 `data_path`/`rawdata_path`/`archive_path` 属性，改为从 `beancount_path` 硬编码派生
- [x] 2.4 `config.py` 默认 `config_file` 参数改为 `"data/config.yaml"`
- [x] 2.5 `config.py` 移除 `_PROTECTED_SYSTEM_KEYS` 中的 `data_path`/`rawdata_path`/`archive_path` 及相关 pop 逻辑
- [x] 2.6 `config.py` env.yaml 覆盖逻辑中排除路径相关字段

## 3. Backend git 范围扩展

- [x] 3.1 `backend.py` BillManager 初始化新增 `self.beancount_path = config.beancount_path`
- [x] 3.2 `backend.py` `_run_git` 的 `cwd` 从 `self.data_path` 改为 `self.beancount_path`
- [x] 3.3 `backend.py` `git_ensure_repo` 中 `.git` 检测路径和 `.gitignore` 路径改为 `self.beancount_path`
- [x] 3.4 `backend.py` `git_is_clean` 中 `.git` 检测路径改为 `self.beancount_path`
- [x] 3.5 `backend.py` `git_commit_if_dirty` 中 `.git` 检测路径改为 `self.beancount_path`
- [x] 3.6 `backend.py` `.ledger-period` 文件路径保持在 `self.data_path` 下不变

## 4. Docker 构建修复

- [x] 4.1 `Dockerfile` 移除 `RUN useradd -m -u 1000 appuser`
- [x] 4.2 `Dockerfile` 移除 `USER appuser`
- [x] 4.3 `Dockerfile` 移除所有 `chown` 相关行
- [x] 4.4 `Dockerfile` `mkdir -p` 简化为只创建 `/app/data`
- [x] 4.5 `docker-compose.yml` volumes 简化为 `./data:/app/data`、`./env.yaml:/app/env.yaml`、`./certs:/app/certs`
- [x] 4.6 `docker-compose.yml` ports 移除 80 端口映射，只保留 443
- [x] 4.7 `.dockerignore` 更新路径（移除 `rawdata/`、`archive/`、`config.yaml` 单独条目，改为 `data/`）

## 5. Entrypoint 启动流程修复

- [x] 5.1 `entrypoint.sh` 添加创建 `data/beancount/data`、`data/beancount/rawdata`、`data/beancount/archive` 子目录逻辑
- [x] 5.2 `entrypoint.sh` 添加 `main.bean` 不存在时 `touch` 创建空占位文件
- [x] 5.3 `entrypoint.sh` 移除 Fava 启动后的 30 秒等待循环，改为直接后台启动
- [x] 5.4 `entrypoint.sh` 更新 Fava 的 `main.bean` 路径为 `data/beancount/data/main.bean`

## 6. Nginx 配置修复

- [x] 6.1 `nginx.conf` CSP 头 `script-src` 加上 `https://cdn.tailwindcss.com`
- [x] 6.2 `nginx.conf` CSP 头 `style-src` 加上 `https://cdn.tailwindcss.com`

## 7. 前端引导页修复

- [x] 7.1 `setup.html` `getAllAccounts()` 增加遍历 `setupConfig.card_accounts` 的分支，将拼出的完整账户名加入列表

## 8. 前端配置页修复

- [x] 8.1 `config.html` 页面加载时调用 `/api/ledger/accounts` 获取账户列表
- [x] 8.2 `config.html` 通用账户（默认支出/收入）从 `<input type="text">` 改为 `<select>` + "新增"按钮
- [x] 8.3 `config.html` HSBC One/PULSE 账户从 `<input type="text">` 改为 `<select>` + "新增"按钮
- [x] 8.4 `config.html` 余额账户从纯文本输入改为下拉选择+新增模式
- [x] 8.5 `config.html` 实现 `getAllAccounts()` 和 `refreshAllSelects()` 逻辑
- [x] 8.6 `config.html` 实现新增账户弹窗（调用 POST /api/ledger/accounts 创建并刷新下拉）
- [x] 8.7 `config.html` `renderCardAccounts()` 调用 `addCardAccountRow()` 时对 `middleName` 做 `.replace(/:$/, '')` 去尾冒号

## 9. 项目 .gitignore 更新

- [x] 9.1 `.gitignore` 更新路径：`archive/*`/`data/*`/`rawdata/*` 改为 `data/beancount/`、`data/config.yaml`
- [x] 9.2 `.gitignore` 移除 `config.yaml` 和 `accounts.bean` 的根目录条目（已不在根目录）

## 10. Web 应用路径更新

- [x] 10.1 `web/app.py` `ensure_default_bean_files()` 中路径引用随 config 属性自动适配，验证无需改动
- [x] 10.2 `migrate.py` 清理或移除旧迁移逻辑（旧路径已不适用）
