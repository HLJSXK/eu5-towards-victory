# Editor/Web 工具整合重构状态

本文是给 Codex、Claude 子代理和其他开发工具的当前状态入口，不替代详细的
[架构评估](Towards_Victory_Editor_Web_Assessment.md)。评估文档保留迁移前基线、设计
理由和验证证据；本文只回答“当前焦点是什么、已经做到什么、还缺什么”。

## 使用规则（worker 必读）

- **只推进“当前焦点”一项。** 不要从“后续任务”中自选，也不要回到已关闭的阶段继续加固。
- **已关闭阶段只修缺陷。** 仅当发现会导致错误结果、数据丢失或测试失败的问题时才修改，
  并登记到“已知缺陷”；性能、整洁度和边界说明类改进不在范围内。
- **需要设计决策时先停下。** 当前焦点若涉及目录布局、事务模型、状态模型等取舍，
  先给出方案、取舍和验收方式，等待确认；不要自行选择保守的增量替代。
- **不要扩写“已接受限制”。** 新发现的问题写入“已知缺陷”（会导致错误结果）或
  “待议事项”（需要决定是否处理），每条一行。
- 完成一个切片后更新本文的焦点进度和验证记录；不要写成按提交排列的历史日志。

## 当前焦点：媒体 job 产物的原子发布与失败恢复

对应原后续任务 3。目标是让媒体 job 失败或取消时不再留下半成品正式产物。

- **现状**：5 个可运行 handler（`media.dds_icon`、`media.wonder_image`、
  `media.historical_style`、`media.historical_api`、`media.wonder_crop`）由生成脚本
  自行计算路径并直接写入正式产物；`ToolPlan` 已声明 `outputs` / `optional_outputs`，
  失败时只报告 `outputs_may_be_partial`，不回滚。
- **第一步（需确认后再实现）**：提交设计方案，至少比较以下两种做法并给出推荐：
  1. 暂存发布：handler 写入 staging 根目录，校验通过后替换正式产物；
     需要说明各生成脚本如何改写输出根目录。
  2. 快照恢复：执行前快照已声明产物，失败/取消时恢复；需要说明大图片快照的
     内存/磁盘成本，以及如何检测未声明的写入。
- **退出条件**：
  - 5 个可运行 handler 失败或取消后，已声明的正式产物与执行前逐字节一致；
  - 成功路径的产物与当前实现逐字节一致；
  - 未声明的写入至少能被检测并在 job 详情中报告；
  - job 详情中 `outputs_may_be_partial` 的语义随之更新，前端提示同步调整；
  - 每个 handler 至少一个失败恢复测试，全量 `pytest tests` 通过。
- **不在范围内**：操作层（`OperationLog`、`run_operation`、`OperationStore`）的加固、
  跨进程锁、前端共享 store、Wonder DAG 依赖细化。

## 已关闭阶段：统一操作层（2026-10-05 至 10-08）

对应原后续任务 1 的持久化与查询部分，已完成并关闭：

- 四个编辑器 commit 与媒体 job 共用 `services/platform.py` 的 `OperationLog` 和
  `run_operation`：统一非阻塞资源锁、生命周期、取消和终态判定。
- `services/operation_store.py` 将操作快照和媒体 job 详情写入
  `.editor_state/operations.sqlite3`；`GET /api/operations`、`GET /api/operations/{id}`
  和 `GET /api/jobs/{job_id}` 可在重启后查询；未终结记录在启动时标记为 interrupted；
  终态记录保留 30 天。
- 媒体日志按 `after_line` 游标轮询；工具 options 和结果在发布前检查 JSON 契约。
- 错误响应区分 `resource_busy` 与 `resource_changed`，前端分别提示。

“统一同步提交与异步调度”和“领域事务统一”**不在本阶段继续推进**，转为待议事项。

## 更早完成的基础

- `cost/reward`、`victory tree`、Wonder 和 Wonder crop 配置已接入资源级
  `load/validate/preview/commit` 协议：SHA-256 base、draft、字段级预览 diff、冲突检测和
  失败恢复；旧 bootstrap/save 路由已删除。
- Wonder 首屏摘要、仪式设计和共享选项目录按需加载；大选项目录通过版本引用共享。
- Wonder 生成链有声明式 DAG（41 个脚本、40 个产物），按变更的输入组选择根步骤。
- `services/artifacts.py` 提供编辑器和媒体共用的产物清单及文件级格式检查；媒体目录有
  9 个注册工具，其中 5 个可运行 handler 已实现 `prepare`、输入快照和输出声明。
- Web 工具有统一启动入口和 `--check` 检查。

## 已知缺陷

会导致错误结果或误导性状态的问题。已关闭阶段允许修复这些问题：

- `run_operation` 在 `execute()` 成功返回后仍检查取消：工作已完成、产物已校验的媒体 job
  会被记为 `cancelled`（returncode 130、`outputs_may_be_partial=true`），与磁盘实际不符。
- 第二个服务进程启动时，`OperationStore` 会把第一个进程仍在运行的操作标记为 interrupted。
- Victory Tree 保存失败时不写 `[error]` 日志，与其他三个编辑器不一致。

## 待议事项

需要决定是否处理、何时处理；未经确认不要动手：

- 是否把编辑器同步提交与媒体异步调度统一为一个调度器（原任务 1 剩余部分）。
- `JobManager._prune_expired_locked` 每次轮询都复制所有内存 job 的完整操作快照；
  内存 job 保留 30 天，数量大时开销线性增长。
- 仓库根目录残留不可读的 `.pt-*-1008/` 测试目录，未被 `/.pytest-*/` 忽略规则覆盖。

## 已接受限制

本阶段不处理，不要据此开新切片：

- 锁和操作库只协调当前服务进程，不是跨进程状态协调；重启不恢复执行，interrupted
  记录需人工核对产物。
- 操作库写入失败不会把已完成的提交改判为失败，只在响应中带 `persistence_error`。
- `create_app` 重叠的 lifespan 可能互相覆盖 `cropper`、`jobs` 单例的 store 引用。
- `atomic_write_files` 逐文件暂存和恢复，不是全局多文件原子替换。
- 保存会整体重写 YAML：文件头注释、BOM 和换行符保留，正文分节注释和字符串引号不保证保留。
- Wonder DAG 按源文件组选择步骤，不是字段级依赖图。
- PNG/DDS/JPEG/JSON 检查是文件级检查，不是完整图片或领域 schema 校验。

## 后续任务（按顺序，当前焦点完成后由用户指定下一项）

1. 迁移前端共享 store、请求层、dirty/loading/error 状态协议和公共组件；展示
   generation/artifact 报告。
2. 建立跨资源 `ChangeSet`、完整输入依赖图、领域产物语义校验和跨资源预览。
3. 设计跨进程持久锁和状态存储，再删除旧领域 service 拼接层。

## 当前架构边界

- 编辑器资源：`ResourceDescriptor` + draft + `validate/preview/commit`，位于
  `towards_victory_editor_web/services/platform.py` 及各领域 service。
- 操作执行：`run_operation` 负责共享生命周期与资源锁，`OperationStore` 负责持久化查询；
  HTTP 同步响应与 `JobManager` 线程池调度各自负责。
- Wonder 生成：`services/generation.py` 负责 DAG 和命令执行，`services/artifacts.py`
  负责产物清单与格式校验。
- 媒体作业：`ToolRegistry`、`ToolPlan`、`JobManager`（`services/tooling.py`）、
  handler 计划（`services/media_plans.py`、`services/media_tools.py`、`services/cropper.py`）
  和 `/api/jobs`。
- 详细 API、锁、输入组和已知限制以
  [Web 工具 README](../../towards_victory_editor_web/README.md) 和
  [详细评估](Towards_Victory_Editor_Web_Assessment.md) 为准。

## 验证记录

最近一次核对：2026-10-08，基准提交 `99bfa27a`，Windows + eu5 Python 3.11.15。

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m towards_victory_editor_web --check
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m pytest tests -q --basetemp .pytest-<短名>
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\validate.py --changed --ai-report
node --test tests/media_job_polling.cjs
git diff --check
```

结果：`pytest tests` 192 passed（1 个既有 FastAPI/httpx 弃用警告，约 5.5 分钟）；
`media_job_polling.cjs` 2 项通过；`--check` 通过（9 个注册工具，5 个可运行，196 张裁剪图）。
`--basetemp` 使用仓库内新建短名目录，避免 Windows 临时目录权限和深路径问题，用完删除。

## 子代理启动顺序

涉及工具整合或 Web 重构时，先读：

1. 根目录 `CLAUDE.md`
2. `docs/knowledge/BRIEF.md`
3. 本文（先读“使用规则”和“当前焦点”）
4. `towards_victory_editor_web/README.md`
5. 需要架构背景时再读 `Towards_Victory_Editor_Web_Assessment.md`

然后运行 `scripts/ai_context.py --files <目标文件>`，检查生成文件归属和相关风险卡。
