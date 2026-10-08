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

## 当前焦点：待指定

前端共享请求层切片已完成并提交；下一切片由用户指定。

## 已完成切片：前端共享请求层（2026-10-08）

- `static/api.js` 提供唯一的 `fetchJson` 和统一 `ApiError`，保留 `status`、`detail`、
  `code`、`operation_id`、`operation`、`generation`、`log_text`；非 JSON 错误响应只读取一次 body。
- 五个前端通过 ES module 导入共享函数，已删除各自副本；共享模块由 import 加载，无需单独的 script 标签。
- `resource_busy` / `resource_changed` 的 `message` 同时包含统一提示与服务端诊断，界面可见资源 ID 或文件路径；
  原始诊断仍保留在 `detail`，文件变化提示不再假设调用方有未保存草稿，适用于编辑器与媒体 job。
  Wonder 已区分两者并改为读取 `error.log_text`，两个 POST 调用显式保留 JSON 请求头。
- 新增 `tests/api.cjs` 覆盖两种 409、带 generation/log_text 的 500、非 JSON 错误和成功响应，
  并覆盖未知 409 与结构化校验详情；原媒体轮询、cropper/Wonder 状态测试已接入共享请求层。
  409 用例断言 `message` 包含资源/路径诊断，cropper 用例核对状态栏及日志保留诊断；测试顶部注明正则加载器的限制。
- 后端 API、响应结构和各页面状态模型未改动；共享 store、dirty/loading 协议、公共组件与报告展示仍属后续任务。

## 已完成切片：媒体 job 产物的暂存发布与失败恢复（2026-10-08）

- 已删除目录递归扫描，只核对声明输入/输出文件；输入变化报冲突，正式输出在 staging 外的变化通过 `formal_output_changes` 报告并阻止发布，不推断写入者。
- staging 中间文件单列 `staging_extra_files`，不计入正式写入冲突；`outputs_may_be_partial` 仅由正式输出在 staging 外的变化、发布恢复失败或已开始运行的 interrupted 操作触发。
- 已修复 historical_style JSON 指向 staging、Wonder 已有 PNG 补全与新生成混跑失败，并为首次生成创建 staging 输出父目录。
- 已删除直接写正式路径的旧 handler 兼容分支和吞掉路径错误的回退。
- 进程中断按用户确认的 A 处理：已开始运行的 interrupted job 提示可能部分发布、备份需人工核对；排队中被中断的 job 不提示。启动恢复另列待办。
- 已将产物校验和输入复核移到 handler 清理后；发布失败只恢复实际替换的文件，只清理本 job 创建的临时文件；恢复失败继续处理其他文件、保留备份并持久化需核对状态。
- 五个 handler 的成功用例与直接运行脚本逐字节比对通过；图片 API 使用固定响应，historical_style 使用真实图片处理流程。普通发布回滚和恢复受文件锁阻止的回归通过。

本切片不处理操作层的其他设计、跨进程锁、前端共享 store 或 Wonder DAG 依赖细化。

## 已关闭阶段：统一操作层（2026-10-05 至 10-08）

对应原后续任务 1 的持久化与查询部分，已完成并关闭：

- 四个编辑器 commit 与媒体 job 共用 `services/platform.py` 的 `OperationLog` 和
  `run_operation`：统一非阻塞资源锁、生命周期、取消和终态判定。
- `services/operation_store.py` 将操作快照和媒体 job 详情写入
  `.editor_state/operations.sqlite3`；`GET /api/operations`、`GET /api/operations/{id}`
  和 `GET /api/jobs/{job_id}` 可在重启后查询；未终结记录在启动时标记为 interrupted；
  终态记录保留 30 天。
- 媒体日志按 `after_line` 游标轮询；工具 options 和结果在发布前检查 JSON 契约。
- 错误响应区分 `resource_busy` 与 `resource_changed`，前端已通过共享请求层统一提示。

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

- 第二个服务进程启动时，`OperationStore` 会把第一个进程仍在运行的操作标记为 interrupted。
- Victory Tree 后端保存失败时不写 `[error]` 日志，与其他三个编辑器不一致；前端已有错误提示。
- `server.py` lifespan 结束时关闭自有 `OperationStore` 但不调用 `jobs.shutdown()`；关闭时仍在运行的 job 无法写入终态，下次启动被标记为 interrupted。
- 媒体取消请求与 cropper 定时器中的后续轮询没有异常处理；请求失败可能不显示错误，cropper 重建按钮仍禁用，另列后续修复。

## 待议事项

需要决定是否处理、何时处理；未经确认不要动手：

- 是否把编辑器同步提交与媒体异步调度统一为一个调度器（原任务 1 剩余部分）。
- `JobManager._prune_expired_locked` 每次轮询都复制所有内存 job 的完整操作快照；
  内存 job 保留 30 天，数量大时开销线性增长。
- 仓库根目录残留不可读的 `.pt-*-1008/` 测试目录（未被 `/.pytest-*/` 忽略规则覆盖）及 `.pytest-review-*` 目录；由 Codex 沙箱用户创建，当前账户无删除权限，需手动清理。
- 本轮 `.pytest-api-1008/`、`.pytest-api-browser-1008/` 已完成验证、待清理；删除操作因自动审批服务审核模型不可用（404）未执行，两个目录均已被 Git 忽略。
- 任意未声明正式路径的写入检测与可靠归属尚未实现；本轮按确认的 A 仅核对声明文件，写入审计另行决定。
- 中断后的 staging/备份启动恢复与清理尚未实现；本轮按确认的 A 准确提示人工核对，另行决定自动恢复。
- `ToolContext.formalize_json_paths` 只替换整值等于暂存文件路径的 JSON 字符串；目录路径或嵌入更长字符串的 staging 路径会漏入正式产物。现有 5 个 handler 有逐字节比对兜底，新增 handler 时需确认。

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

1. 迁移前端共享 store、dirty/loading/error 状态协议和公共组件；展示
   generation/artifact 报告（请求层已完成，下一切片范围待用户指定）。
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

最近一次核对：2026-10-09，Windows + eu5 Python 3.11.15 + Node 22.19.0。审阅修复后，四个 Node 测试文件
共 23 项通过；409 断言确认提示包含资源/路径诊断，cropper 状态栏和日志均保留诊断。
`--check` 通过（9 个注册工具、5 个可运行、196 张裁剪图）；`scripts/validate.py --changed --ai-report`
通过（2 个适用文件、无错误或警告）；`fetch()` 仍仅出现在 `static/api.js`，`git diff --check` 通过。
本次未重跑全量 pytest 与浏览器验收；下列完整验证结果沿用 2026-10-08 的记录。

最近一次完整验证：2026-10-08，Windows + eu5 Python 3.11.15 + Node 22.19.0 + 本机 Chrome headless；eu5 环境已按 `requirements-image.txt`
安装 scikit-image 0.26.0，historical_style 字节比对用例不再跳过。

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m towards_victory_editor_web --check
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m pytest tests -q --basetemp .pytest-<短名>
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\validate.py --changed --ai-report
node --test tests/api.cjs tests/media_job_polling.cjs tests/cropper_resource_state.cjs tests/wonder_resource_state.cjs
rg -n 'fetch\(' towards_victory_editor_web/static -g '*.js'
git diff --check
```

结果：全量 `pytest tests` 214 passed、无跳过（523.31 秒）；包含五个 handler 的成功字节比对、
失败恢复、清理后校验、未扫描无关文件及文件冲突分类回归。警告来自既有 FastAPI/httpx 接口及
style 脚本的 `binary_dilation` 弃用提示。Node 共 23 项通过（共享请求层 8 项、媒体轮询 5 项、
cropper 状态 4 项、Wonder 状态 6 项）；`fetch()` 仅出现在 `static/api.js`。`--check` 通过
（9 个注册工具，5 个可运行，196 张裁剪图）；`scripts/validate.py --changed --ai-report` 通过
（2 个适用文件，无错误或警告）；`git diff --check` 通过。

浏览器验收以 Chrome DevTools 自动驱动真实页面完成：四个编辑器提交过期 base 均收到真实
`resource_changed`；独立测试服务中的受控媒体 job 持有四个资源锁时，四个编辑器均收到真实
`resource_busy`，提示一致且草稿保留。该 job 通过真实 `/api/jobs` 提交、游标轮询到成功并显示
日志与产物，输出仅写入测试目录；媒体提交的两种 HTTP 409 提示另用模拟响应验证。无页面未捕获异常。
浏览器使用隔离 profile 与本机 headless 模式；沙箱内启动需 `--no-sandbox`，未使用真实图片 API。
`--basetemp` 使用仓库内新建短名目录，避免 Windows 临时目录权限和深路径问题，用完删除。

## 子代理启动顺序

涉及工具整合或 Web 重构时，先读：

1. 根目录 `CLAUDE.md`
2. `docs/knowledge/BRIEF.md`
3. 本文（先读“使用规则”和“当前焦点”）
4. `towards_victory_editor_web/README.md`
5. 需要架构背景时再读 `Towards_Victory_Editor_Web_Assessment.md`

然后运行 `scripts/ai_context.py --files <目标文件>`，检查生成文件归属和相关风险卡。
