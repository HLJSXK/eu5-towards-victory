# Editor/Web 工具整合重构状态

本文是给 Codex、Claude 子代理和其他开发工具的当前状态入口，不替代详细的
[架构评估](Towards_Victory_Editor_Web_Assessment.md)。评估文档保留迁移前基线、设计
理由和验证证据；本文只回答“现在已经做到什么、还缺什么、从哪里开始”。

## 状态基准

- 核对日期：2026-10-05
- 基准提交：`448eb992`（2026-10-02，按变更源文件组选择 Wonder 生成根节点）
- 基准工作区：核对前干净；本文之后的入口文档变更不属于业务代码切片
- 当前判断：统一资源协议已经完成首个可运行切片，编辑器提交和媒体作业仍是两条执行生命周期，整个平台重构尚未完成

## 已完成

- `cost/reward`、`victory tree`、Wonder 和 Wonder crop 配置已接入资源级
  `load/validate/preview/commit` 协议。
- 资源接口已有源文件 SHA-256 base、draft、字段级预览 diff、冲突检测和失败恢复；
  Wonder、cost/reward 和 cropper 的旧 bootstrap/save 路由已删除。
- Wonder 首屏摘要、仪式设计和共享选项目录已按需加载；大选项目录通过版本引用共享。
- Wonder 生成链已有声明式 DAG：完整计划为 41 个脚本、40 个不同产物，按实际变更的
  输入组选择根步骤，并返回步骤状态、超时、日志和产物清单。
- 编辑器和媒体共用产物清单及文件级格式检查；媒体目录有 9 个注册工具，其中 5 个
  可运行 handler 已实现 `prepare`、输入快照和输出声明，Wonder 相关 job 已接入资源锁。
- 四个编辑器已使用统一资源接口，Web 工具已有统一启动入口和 `--check` 检查。

## 部分完成和明确边界

- Wonder DAG 按源文件组选择步骤，但还不是字段级依赖图；Python 导入、间接读取、未
  登记副作用和领域语义校验仍需补齐。
- 编辑器保存是同步资源提交，媒体生成是异步 job/artifact；两者已统一 `OperationLog`
  和错误/取消状态字段，但仍没有统一的执行器、持久化日志或跨操作查询接口。
- `OperationLog` 包含 operation ID、资源、状态、事件、错误、取消请求和时间戳；四个资源
  commit 与媒体 job 都返回该协议。commit 错误响应从本次异常携带的操作记录中返回，
  Wonder/cost_reward 的 generation 报告沿用本次 operation ID；操作记录目前仅驻留内存。
  媒体 job 取得执行锁和资源锁后才从 queued 进入 running；资源忙时直接失败且不设置
  started_at。终态不能被后续启动、完成、失败或取消调用覆盖。
- Victory Tree 保存使用非阻塞资源锁，并发保存从原先排队改为忙时返回 HTTP 409。
  错误码区分 `resource_busy` 和 `resource_changed`；Victory Tree、cost/reward 和裁剪
  页面分别提示稍后重试或核对修改后重新加载。
- Wonder 操作事件只记录本次提交的生成日志和错误；资源忙失败只记录一次错误。
  媒体 job 的生成日志只写入 job lines，operation 事件只记录生命周期和错误。
  `/api/jobs/{job_id}` 支持 `after_line` 游标，轮询只返回新增行；游标超出保留窗口时
  返回最近 300 行并标记 `lines_reset`，媒体工作台与裁剪页均按此协议更新日志。
- 媒体 handler 只有首个资源依赖切片；媒体仍直接写正式产物，没有暂存发布、回滚事务
  或未登记写入恢复。现有 PNG/DDS/JPEG/JSON 检查是文件级检查，不是完整图片或领域 schema 校验。
- `atomic_write_files` 能逐文件暂存和恢复，但跨资源 change set 和全局多文件原子替换
  尚未实现。锁只协调当前服务进程，尚未覆盖多进程或多 worker 的持久状态。
- 前端共享的只是工作区外壳和少量样式；共享 store、请求层、dirty/loading/error 状态、
  统一组件和生成报告展示仍未完成。
- 保存仍整体重写 YAML：文件头注释、BOM 和换行符可保留，但正文分节注释和字符串引号
  不保证保留。这是现有限制，不应在本轮重构中误报为已解决。

## 下一阶段任务

按优先级建议从以下任务中选取，并在任务描述中写明涉及的资源和验证范围：

1. 在现有 `OperationLog` 协议上统一编辑器 commit 与媒体 job 的执行器，补充持久化日志
   和操作查询，并减少媒体轮询的重复日志传输。
2. 建立跨资源 `ChangeSet`、完整输入依赖图、领域产物语义校验和跨资源预览。
3. 为媒体生成增加暂存发布和回滚，并恢复未登记的生成器副作用。
4. 迁移前端共享 store、请求层、状态协议和公共组件；同时展示 generation/artifact 报告。
5. 设计跨进程持久锁和状态存储，再删除旧领域 service 拼接层。

## 当前架构边界

- 编辑器资源：`ResourceDescriptor` + draft + `validate/preview/commit`，主要实现位于
  `towards_victory_editor_web/services/platform.py` 及各领域 service。
- Wonder 生成：`services/generation.py` 负责 DAG 和命令执行，`services/artifacts.py`
  负责编辑器和媒体共用的产物清单与格式校验。
- 媒体作业：`ToolRegistry`、`ToolPlan`、`JobManager` 和 `/api/jobs`，仍是异步生命周期。
- 详细 API、锁、输入组和已知限制以
  [Web 工具 README](../../towards_victory_editor_web/README.md) 和
  [详细评估](Towards_Victory_Editor_Web_Assessment.md) 为准。

## 验证和环境前提

当前核对通过的检查：

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m towards_victory_editor_web --check
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\validate.py --changed --ai-report
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m compileall -q towards_victory_editor_web
node --check <各前端 .js 文件>
node --test tests/media_job_polling.cjs
git diff --check
```

`eu5` 环境已安装 pytest 9.1.1（含 pluggy 1.6.0、iniconfig 2.3.0，2026-10-04 装入 eu5
site-packages）。本机用 eu5 Python 3.11 运行 `python -m pytest tests -q`。本轮托管沙箱的
默认 pytest 临时目录不可访问，因此使用
`python -m pytest tests -q --basetemp .pytest-codex-20261005`；沙箱应选当前用户可写的新目录，
不要复用归属其他用户的 `.pytest-sandbox/`。`tests/` 下 164 个用例通过（另有 1 个
FastAPI/httpx 弃用警告）。覆盖排队/取消、并发请求
错误归属、commit/generation ID 一致性、终态保护，以及媒体日志游标和保留窗口重置。
`node --test tests/media_job_polling.cjs` 覆盖取消后迟到轮询和新旧 job 响应串号。
`--check`、`validate.py --changed --ai-report`、`compileall`、改动的两个 JS 文件
`node --check` 和 `git diff --check` 通过；系统 Python 3.9 不满足本项目的运行条件。

## 子代理启动顺序

涉及工具整合或 Web 重构时，先读：

1. 根目录 `CLAUDE.md`
2. `docs/knowledge/BRIEF.md`
3. 本文
4. `towards_victory_editor_web/README.md`
5. 需要架构背景时再读 `Towards_Victory_Editor_Web_Assessment.md`

然后运行 `scripts/ai_context.py --files <目标文件>`，检查生成文件归属和相关风险卡。
完成一个切片后，在本文更新对应状态和验证前提；不要把本文扩展成按提交排列的历史日志。
