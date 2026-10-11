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

## 当前焦点：待用户指定（2026-10-11）

已完成用户确认的方案 A：Wonder 后端领域模块拆分。下一项由用户指定，不自动推进其余 Wonder UI 拆分或跨资源 ChangeSet。

## 已完成切片：Wonder 后端领域模块拆分（2026-10-11）

- 原 3699 行 `services/wonder_localization.py` 已删除，领域实现迁入 `services/wonder/` 九个模块，包入口不做兼容转发。
- `sources.py` 集中源路径、输入组、仪式设计/Prompt 读取与源数据校验；`values.py` 负责 YAML/结构值及 modifier/reward/ritual/ceremony 行编解码；`options.py` 负责选项目录及目录引用。
- 选址条件与偏好模板数据位于 `site_templates.py`，解析、匹配与渲染位于 `site_rules.py`；`localization.py` 负责本地化键计算、校验和 `build_check_report`。
- `field_types.py` 持有字段类型与 API 序列化；`fields.py` 显式接收数据和目录构建字段，不依赖服务对象；`model.py` 的 `WonderModel` 只保留编辑应用与查询。最大模块 `fields.py` 为 674 行，其余均低于 600 行。
- 四个曾被末尾覆盖的选项函数只保留生效实现；目录构建入口命名为 `modifier_option_catalog`。资源、预览、提交、服务器、CLI 与 `tests/` 均直接导入所属模块；`scripts_engineering_department/test_wonder_mechanics_rules.py` 的旧模块导入在提交前审计中发现并已改按归属模块导入，迁出模型方法无残留调用。
- 全部 192 个奇观详情、摘要、选项目录与仪式目录的序列化哈希与拆分前一致，Web `--check` 输出一致；验收结果与环境见“验证记录”。前端、事务与跨资源同步行为保持原样。

## 已完成切片：Wonder 保存/加载/预览拆分（2026-10-11）

- 后端入口改为 `services/wonder_resource.py` 的 `WonderResourceService`；资源加载/base/校验、候选源文件与 preview、commit 事务分别位于 `wonder_resource.py`、`wonder_preview.py`、`wonder_commit.py`。领域字段、规范化和详情模型已进一步迁入上方 `services/wonder/` 包；已删除原单体及旧类入口。
- Wonder `/preview` 的 `diff` 按实际候选 YAML 与磁盘源文件比较，包含奇观 ID/key、语言、字段、类型、前后值和存在标记；使用规范化后将要写入的值，结构字段整体展示，不带选项目录。原型切换同时报告 `base_key` 与 `mechanic_key`。源文件 SHA-256 单列 `file_diff`；preview 只给生成计划，实际生成产物哈希仍在 commit 后报告。
- 前端 `static/wonder_editor.js` 负责 Wonder 草稿缓存、请求字段、多段加载和保存后的详情补加载；共享 `editor_panel.js` 执行 preview → 确认 → 同一序列化请求体 commit。共享对话框支持多行文本/脚本、缩进结构值及不存在标记，挂载于工具面板之外。两个试点编辑器沿用原行为。
- 首次加载先显示摘要列表，再加载详情；reload 只有资源、详情与选项目录全部成功才替换页面。保存成功立即接受新 base 并清空已提交草稿；随后详情加载失败明确提示“已保存，但详情加载失败”，提供只读重试。返回编辑/Escape、409 与生成失败保留草稿及诊断。
- 共享 `createLatestLogView` 分别保存服务日志、最近一次操作报告和当前诊断；详情重试保留保存报告，复制日志包含报告。Wonder 保留 toast、dirty 计数和快捷键，并新增未保存编辑的离开页面保护。原单体中的加载/保存/预览编排已删除。

仪式设计、选项目录、图片面板等其余 Wonder UI 拆分仍在后续任务 1；cost/reward 提交后 Wonder base 不同步仍单列待议。验收结果与环境见“验证记录”。

## 已完成切片：2026-10-11 审计缺陷修复

对 324e6d48..5c0b379e 的审计发现 5 个未登记缺陷，均已修复，每条回归用例在撤掉对应修复时失败：

- 预览对话框挂载点 `#cr-preview`/`#vt-preview` 移到工具面板之外：此前保存期间切走顶层标签，`showModal()` 在 display:none 面板内打开不可见模态框，整页 inert、资源停在 saving。Chrome 验收新增“预览在途时切到 Wonder，对话框仍可见可取消”。
- `media.dds_icon` 声明 `editor.wonder`、`editor.cost_reward`：Wonder 批量目标读取两者的源文件，此前编辑器保存不报 `resource_busy`，job 在输入复核时作废已付费图片。新测试按资源源文件与任务输入的交集推导所需锁。
- 有取消请求时，`run_operation` 对 `RollbackError` 保留诊断：终态仍为 cancelled，但 `operation.error`、job 日志和持久化记录包含原始错误与恢复错误。`PublicationRecoveryError` 已删除，媒体发布改用 `platform.RollbackError`。
- `job_panel.js` 在 job 进入终态时清空 `cancelError`：取消失败后正常完成的 job 不再显示为错误。
- Wonder 加载、切换、保存、重新加载失败统一报告：状态栏与可复制日志都包含 `error.message`（资源 ID/文件路径），toast 只是重复；实现现已迁入 Wonder 适配层。

## 已完成切片：前端共享展示层（2026-10-10）

已按用户确认的方案完成：ES module 导出函数、保存前预览确认、操作提示统一中文，字段名、路径及服务端诊断保留原文。

- `static/display.js` 统一日志/状态、标签渲染、HTML 转义及操作/生成报告；cost/reward 与 Victory Tree 已删除各自的日志、标签 DOM 与 load/save/reload 样板，统一使用 `static/editor_panel.js`。
- 两个试点编辑器保存先请求资源 `/preview`，展示服务端文件/条目/字段及原值→新值；确认后提交相同的序列化请求。预览、确认与提交期间冻结编辑，返回编辑或 Escape 保留 draft/base，不提交。派生文件的哈希差异单列“文件摘要”。
- `static/job_panel.js` 统一媒体与 cropper 的作业状态/日志、轮询错误、Retry/Stop 和输入/输出报告；媒体取消与停止跟踪后的可取消状态也由组件持有。`index.html` 只保留挂载位置，重复作业按钮和报告标记已删除；cropper 同样显示产物变化、缺失/校验错误、中间文件与发布恢复失败提示。
- Wonder 的共享日志/状态、操作/生成报告及转义接入已进一步扩展为上述保存/加载/预览切片；媒体工具标签、cropper 文件路径及 Victory Tree 节点标签的 HTML 写入已转义。日志显示 `operation_id`、生成步骤与产物和独立的恢复结果，保留服务端诊断；操作报告单独保存，只显示最近一次保存的报告，复制日志包含该报告。
- 重复按钮、actions 与日志样式，以及媒体 `.job-*` 基础样式移入 `shared.css`，按钮及其禁用样式只作用于两个试点编辑器、作业面板和预览对话框；组件提示统一中文。共享标签使用已有控件冻结机制，加载期间新建的标签在请求结束后恢复可用。

共享展示测试以原生 ES module 导入；Chrome 验收使用真实 DOM 和服务端只读 preview，覆盖试点、媒体/cropper 和 Wonder 接入。完整结果与环境见“验证记录”。

## 已完成切片：重构审计缺陷修复（2026-10-10）

对 324e6d48..85e9a086 的审计发现两个未登记缺陷，均已修复：

- 可选产物删除：staging 预先复制全部已有产物，handler 在 staging 删除的可选输出（`keep_png: false` 的 PNG）
  现在在成功发布时同步删除正式文件，删除前同样复核正式快照，失败时由备份恢复；失败 job 不发布。此前旧 PNG
  会留在新 DDS 旁，后续裁剪重建优先读取 PNG，用旧图覆盖新生成的 DDS。修正了上一切片“缺失可选 PNG 不再删除
  正式 PNG”对成功运行的错误推广；Wonder 图片与 DDS 图标两个 handler 同时受益。
- 轮询渲染异常：`JobPoller.accept` 改为先安排下一次轮询再调用 `onUpdate`；轮询路径中的渲染异常经 `onError`
  显示，不再因 revision 已变化被静默丢弃。此前渲染抛错会让 job 停在 active 且没有定时器，cropper 与媒体页
  控件永久禁用、无任何提示。终态 job 的渲染异常经 `onError(error, false)` 显示为停止跟踪提示，文案不精确但可见。

## 已完成切片：提交前审计缺陷收尾（2026-10-10）

- 轮询遇到 404/410 自动停止跟踪、解除页面冻结，保留 job ID、日志和查询错误；其他不可自动重试的 4xx 提供重试和 Stop tracking。停止跟踪只解除本地跟踪，不改判服务端 job 结果，也不发送取消请求；迟到响应失效。媒体页停止跟踪后 Cancel 仍可用，取消响应作为完整快照恢复跟踪。
- 每个 lifespan 创建并持有自己的 `JobManager`；删除模块级 jobs 单例及私有 `_shutdown` 检查。关闭、登记和提交受同一锁保护，关闭后拒绝提交；完成的 future 由回调移出登记表；取消尚未运行的 futures，给排队 job 持久化 cancelled 终态，运行 job 协作取消，全部退出后才关闭操作库。
- 三个图片 API 生成器补齐任务间、请求间和重试等待的取消检查；cropper 子进程池按工作进程数量提交转换，取消后停止补交并等待正在转换的图片退出，再清理 staging。正在阻塞的请求或计算仍需返回；图片请求默认超时 180 秒，不承诺固定退出时限，符合已确认的关闭方案。
- 失败产物清单只比较实际存在的暂存产物，正式保留的 PNG 不再误报 deleted；必需输出缺失仍由 `missing_outputs` 报告。发布冲突保存检测到的确切路径，回滚失败的包装异常也保留该诊断，不把本 job 未恢复的写入误记为外部冲突。
- `ResourceState` 分开请求 generation 与资源 revision；`replace` 只更新资源数据，`reset` 放弃在途请求并回到 idle（当前仅测试夹具用于放弃模块加载时的 bootstrap 请求），`run` 统一结束请求阶段。当前 apply/render 异常正常上报，旧响应仍被隔离。

验收覆盖媒体与 cropper 解锁、迟到响应隔离、apply 异常、提交与关闭竞态、运行/等待/排队三类任务的取消与终态持久化、批内请求及重试取消、裁剪转换停止补交，以及失败产物和回滚冲突诊断。网络及阻塞点均由测试控制，未调用真实图片 API。

## 已完成切片：审计缺陷修复 + 前端资源状态层（2026-10-09 至 10-10）

已按用户确认的方案完成：

- `static/resource_state.js` 统一持有 base、saved、draft、dirty、请求阶段和 error；四个编辑器接入资源状态，媒体提交接入请求生命周期。请求在途冻结编辑、资源内切换、reload 和重复提交；成功同步更新 draft/base，失败保留草稿，旧响应不覆盖新资源。
- Prompt 加入 Wonder 页面草稿、dirty、预览与统一提交；清空也是草稿编辑。Prompt 文件参与 base、资源锁和多文件恢复事务，独立 Prompt 路由和保存按钮已删除。
- 媒体与 cropper 共用 `JobPoller`：瞬时网络/服务端错误自动重试，其他查询错误提供手动重试；保留 job ID、游标、日志，隔离迟到响应，显示 `job.error`。取消请求失败保留活动任务并恢复按钮。
- cropper 的 409 提示使用英文并明确裁剪草稿已保留；共享请求层对空 detail 回退原始响应，保留服务端诊断。
- 发布只替换声明且 staging 中实际存在的文件（成功 job 中 handler 删除的可选输出现在同步删除，见重构审计缺陷修复）；每个文件替换前复核正式快照，冲突恢复已替换文件并保留外部修改。回滚失败同时保留原始错误和恢复错误；staging 校验拒绝缺少映射的产物。
- 操作库打开前取得 OS 文件锁；同一库的第二个持有者明确报错退出，不触发恢复逻辑、不污染首进程的运行记录。服务关闭时先取消 jobs 并等待终态持久化，再关闭操作库（关闭策略见本次审计收尾）。
- Victory Tree 保存失败补齐 `[error]` 日志。相关测试同时核对文件、base 和节点草稿不变。

验收已覆盖 Prompt 的 HTTP validate/preview/commit、清空、资源锁、base 冲突与多文件回滚，
以及逐文件发布冲突、PNG 保留、第二进程拒绝和关闭时终态持久化。前端 Node 回归与真实 Chrome
页面验收通过；详细命令、结果和验证方式见“验证记录”。公共展示组件及 generation/artifact
报告展示已由“前端共享展示层”切片完成。

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
- 该切片完成了共享请求层；资源状态迁移已由本次切片完成，公共组件与报告展示已由“前端共享展示层”切片完成。

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

- 四个编辑器的资源 commit 与媒体 job 共用 `services/platform.py` 的 `OperationLog` 和
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

2026-10-10 与 2026-10-11 审计发现的缺陷均已修复，见对应已完成切片；当前无未解决条目。

## 待议事项

需要决定是否处理、何时处理；未经确认不要动手：

- 审计 7：cropper 与 Victory Tree 每次拖拽事件、Wonder 每次输入（`refreshDirtyState` → `cacheCurrentWonderDraft`）都复制并比较整份 draft；现有规模可用，性能优化另行决定。
- `missing_outputs` 只能发现首次生成的必需输出缺失：staging 预填已有产物，handler 未重写既有输出时仍报成功（`changed: false`）。
- `run_operation` 中 `on_error` 自身抛错会取代原始错误；当前只有 job 传入且会吞掉异常，属潜在问题。
- 后端简化：`require_overrides` 不可能触发、`OperationLog.start` 的 `cancelling` 分支不可达、生产中必有的 store 到处判空、
  `job_payload` 顶层与 `operation` 内重复字段、`OperationLog.operation_id`/`CapturedOutput.stream_name`/`ToolRegistry.all()` 无调用者。
  与“不保留防御分支”规则不符，是否开简化切片待定（已关闭阶段默认只修缺陷）。
- 部分既有 Node 测试以正则去掉 import/export 后在 sloppy-mode `vm` 中运行；Wonder 与共享展示组件测试已用原生 ES module，cost/reward 与 Victory Tree 页面接入由 Chrome 覆盖，是否迁移其余测试待定。
- cost/reward 的 preview 对派生 `unique_wonders.yaml` 只返回文件 SHA-256 差异，没有字段级 diff；本切片标注为文件摘要，是否细化后端报告另行决定。
- 提交审计小项：`editor_panel.js` 首次加载失败也提示“草稿已保留”；作业面板取消请求中的渲染异常会显示为“取消失败”；cropper 错误先写操作报告再追加错误信息，媒体页提交/引导失败只写状态栏不写日志。均不影响数据，是否整理另行决定。
- 审计 8：`OperationStore` 文件锁异常路径通过捕获 `UnboundLocalError` 处理未赋值 handle，待整理为显式初始化。
- 审计 8：`api.js` 使用 `return Promise.reject(error)` 替代 throw，行为相同，风格整理另行决定。
- 审计 8：Wonder 保存/加载错误路径减少了 `console.error` 堆栈记录，复制日志按钮缺少请求期间的忙碌处理，待决定是否恢复。
- 审计 8：`tests/wonder_payload_browser.cjs` 自动接受所有对话框，可能漏掉意外 confirm；应按场景断言对话框，本轮尚未运行该脚本。
- 是否把编辑器同步提交与媒体异步调度统一为一个调度器（原任务 1 剩余部分）。
- `JobManager._prune_expired_locked` 每次轮询都复制所有内存 job 的完整操作快照；
  内存 job 保留 30 天，数量大时开销线性增长。
- 仓库根目录累积约 90 个历史 `.pytest-*/` 验证目录（已被 Git 忽略，可一次性删除）；另有不可读的 `.pt-*-1008/` 目录（未被忽略规则覆盖），由 Codex 沙箱用户创建，当前账户无删除权限，需手动清理。
- 任意未声明正式路径的写入检测与可靠归属尚未实现；本轮按确认的 A 仅核对声明文件，写入审计另行决定。
- 中断后的 staging/备份启动恢复与清理尚未实现；本轮按确认的 A 准确提示人工核对，另行决定自动恢复。
- `ToolContext.formalize_json_paths` 只替换整值等于暂存文件路径的 JSON 字符串；目录路径或嵌入更长字符串的 staging 路径会漏入正式产物。现有 5 个 handler 有逐字节比对兜底，新增 handler 时需确认。
- ritual specs 生成清单声明 Prompt 输入，但实际生成路径不读取它（审计工具读取）；该依赖声明与实际读取不一致，待单独决定是否整理。
- 媒体 job 的 `redirect_stdout/stderr` 替换进程全局流，job 运行期间其他请求线程的警告会写入该 job 日志并持久化；只影响诊断归属。
- cost/reward 提交改写 `unique_wonders.yaml` 后，前端 Wonder 的 base 不更新，下次 Wonder 保存必然 409，只能整体 reload 并丢弃页面草稿；与后续任务 2 的跨资源 ChangeSet 相关。
- Web `--check` 在子检查打印 `[FAIL]` 时仍退出 0；本切片发现并记录，后续需让自动化检查能通过退出码判断失败。
- 提交审计：Wonder reload 固定请求当前奇观详情；该奇观若已从磁盘删除，reload 每次 404 失败且页面不替换，只能刷新浏览器。正常编辑流程不删除奇观。
- 提交审计：`WonderResourceService` 以 `commit_resource = commit_resource` 挂载模块函数，与 `WonderPreview` 的 mixin 写法不一致，风格整理另行决定。
- Wonder 领域包使用 `fields.py`、`values.py` 等通用文件名后，`ai_context.py --files` 未自动命中 Wonder 风险卡；待调整 `context_routes.yaml` 的路径匹配，本次已手动读取相关卡片。

## 已接受限制

本阶段不处理，不要据此开新切片：

- 锁和操作库只协调当前服务进程，不是跨进程状态协调；重启不恢复执行，interrupted
  记录需人工核对产物。
- 操作库写入失败不会把已完成的提交改判为失败，只在响应中带 `persistence_error`。
- `create_app` 重叠的 lifespan 可能互相覆盖 `cropper` 单例的 store 引用。
- `atomic_write_files` 逐文件暂存和恢复，不是全局多文件原子替换。
- 保存会整体重写 YAML：文件头注释、BOM 和换行符保留，正文分节注释和字符串引号不保证保留。
- Wonder DAG 按源文件组选择步骤，不是字段级依赖图。
- PNG/DDS/JPEG/JSON 检查是文件级检查，不是完整图片或领域 schema 校验。

## 后续任务（按顺序，当前焦点完成后由用户指定下一项）

1. 继续拆分 Wonder 剩余前端单体：保存/加载/预览与后端领域模块已完成，仪式设计、选项目录与图片面板等前端职责的下一切片由用户指定，复用已产出的共享组件。
2. 建立跨资源 `ChangeSet`、完整输入依赖图、领域产物语义校验和跨资源预览（Wonder 拆分后再评估必要性）。
3. 设计跨进程持久锁和状态存储，再删除旧领域 service 拼接层（单用户本地工具收益低，建议降级，是否删除待用户确认）。

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

Wonder 后端领域模块拆分：2026-10-11，Windows + eu5 Python 3.11.15 + Node 22.19.0。修改前已运行 task-scoped `ai_context.py` 并读取 Wonder 风险卡。

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m pytest --basetemp .pytest-wonder-domain-1011 tests/test_cost_reward_resource_contract.py tests/test_victory_tree_resource_contract.py tests/test_wonder_resource_contract.py tests/test_wonder_field_preview.py tests/test_wonder_payload_loading.py tests/test_cropper_resource_contract.py tests/test_media_job_contract.py tests/test_media_cancellation.py tests/test_media_plans.py tests/test_operation_log_contract.py tests/test_editor_file_transactions.py tests/test_generation_plan.py -q
node --test tests/api.cjs tests/resource_state.cjs tests/media_job_polling.cjs tests/cropper_resource_state.cjs tests/wonder_resource_state.cjs tests/shared_display.cjs
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m towards_victory_editor_web --check
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts/validate.py --changed --fix --ai-report
git diff --check
```

- Python 12 文件一次全量 **250 passed**（581.33 秒），3 条已有 FastAPI/httpx 与 `binary_dilation` 弃用警告；包含资源事务、临时源文件预览/提交、payload 加载及完整生成链产物逐字节比较。现有测试只调整导入、路径替换位置和迁出函数调用。
- Node **58 项通过**；新包及三个调用模块通过 `compileall`。本次未重跑 Chrome，前端文件未修改。
- 拆分前后按同一 JSON 序列化方式比较全部 192 个奇观详情、首页摘要、选项目录（含版本）和仪式目录的 SHA-256，全部一致；Web `--check` 前后输出一致（192 个奇观、7,534 个本地化键、9 个工具、5 个可运行、196 张裁剪图）。
- 80 个迁出顶层函数在归一化导入和名称后与原生效实现的 AST 一致；新包无重复定义、未定义全局引用或循环导入，所有模块小于 800 行。被覆盖定义及迁出模型方法无残留调用，临时拆分辅助文件已清理。提交前审计按文件复核 147 个顶层定义，确认无遗漏、无新残件，被覆盖的选项函数只保留生效实现。
- changed validation 通过（21 个适用文件，无错误或警告）；`git diff --check` 通过，新文件另行核对无行尾空白。风险卡自动路由未命中新目录通用文件名，已单列待议，未扩写边界。

Wonder 保存/加载/预览拆分：2026-10-11，Windows + eu5 Python 3.11.15 + Node 22.19.0 + 本机 Chrome headless。修改前已运行 task-scoped `ai_context.py`。

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m pytest --basetemp .pytest-wonder-final-1011 tests/test_cost_reward_resource_contract.py tests/test_victory_tree_resource_contract.py tests/test_wonder_resource_contract.py tests/test_wonder_field_preview.py tests/test_wonder_payload_loading.py tests/test_cropper_resource_contract.py tests/test_media_job_contract.py tests/test_media_cancellation.py tests/test_media_plans.py tests/test_operation_log_contract.py tests/test_editor_file_transactions.py tests/test_generation_plan.py -q
node --test tests/api.cjs tests/resource_state.cjs tests/media_job_polling.cjs tests/cropper_resource_state.cjs tests/wonder_resource_state.cjs tests/shared_display.cjs
node tests/resource_state_browser.cjs
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m towards_victory_editor_web --check
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts/validate.py --changed --fix --ai-report
git diff --check
```

- Python 12 文件一次全量 **250 passed**，3 条已有 FastAPI/httpx 与 `binary_dilation` 弃用警告；保留资源事务、payload 加载、完整生成链回归。新增 7 项使用真实领域模型与临时源文件验证字段归属、双语规范化、结构值、原型联动、Prompt 多行/删除、无变化预览及 preview 与实际 commit 字节一致。
- Node **58 项通过**；Wonder 的 15 项与共享展示的 11 项使用原生 ES module，覆盖首次详情失败仍显示列表、reload 整体发布、预览取消、完整请求体一致、错误诊断、保存成功后详情失败及只读重试。5 个改动/新增前端模块通过 `node --check`，5 个相关 Python 模块通过语法检查。
- Chrome 验收通过：三个编辑器的真实只读 preview 与可见 diff、返回编辑、预览期间切走工具仍可操作对话框、相同 preview/commit 请求体、409/生成失败保留草稿与诊断，以及 Wonder 提交成功后目录加载失败、新 base 保留、详情重试不再提交。继续覆盖四编辑器状态及媒体/cropper 报告和轮询；无页面未捕获异常。GET/preview 使用真实本地服务，commit 和错误由浏览器拦截；实际 commit 写入由 Python 临时文件测试验证，未改动业务源文件或调用图片 API。
- Web `--check` 各检查均输出通过（192 个奇观、7,534 个本地化键、9 个注册工具、5 个可运行、196 张裁剪图）。changed validation 通过（15 个适用文件，无错误或警告），`git diff --check` 通过。拆分辅助脚本已删除；`WonderLocalizationService` 与原前端保存/加载编排无残留入口。
- 提交前审计（2026-10-11，同一环境）：重跑上述全部命令，Python 250 passed、Node 58 项、Chrome 验收、Web `--check`、changed validation（15 个文件）与 `git diff --check` 均通过；未发现缺陷，两条待议小项已登记，离开页面保护的文档措辞改为“新增”。

2026-10-11 审计缺陷修复：Windows + eu5 Python 3.11.15 + Node 22.19.0 + 本机 Chrome headless。修改前运行 task-scoped `ai_context.py`；命令同下方共享展示层验收。Python 11 文件一次全量 243 passed（新增回滚诊断与 dds_icon 资源锁 2 项），3 条已有弃用警告。Node 51 项通过（新增取消错误清空、Wonder 保存/重新加载诊断 3 项），修改的前端模块 `node --check` 通过；Chrome 验收通过，含新增的切走标签后预览可见用例。Web `--check` 通过（9 个注册工具、5 个可运行、196 张裁剪图）；changed validation 通过（6 个适用文件，无错误或警告），`git diff --check` 通过。五条回归用例逐一在撤掉对应修复后确认失败。

提交前审计收尾：2026-10-11，Windows + eu5 Python 3.11.15 + Node 22.19.0 + 本机 Chrome headless。审计时重跑下方共享展示层全部命令：Python 241 passed、Node 47 项、Chrome 验收、Web `--check` 与 `git diff --check` 均通过。修复禁用按钮样式外溢和 Wonder 报告累积后，Node 48 项（新增报告不累积用例）与 Chrome 验收通过。

前端共享展示层验收：2026-10-10，Windows + eu5 Python 3.11.15 + Node 22.19.0 + 本机 Chrome headless。修改前运行 task-scoped `ai_context.py`。

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m pytest --basetemp .pytest-shared-display-1010 tests/test_cost_reward_resource_contract.py tests/test_victory_tree_resource_contract.py tests/test_wonder_resource_contract.py tests/test_wonder_payload_loading.py tests/test_cropper_resource_contract.py tests/test_media_job_contract.py tests/test_media_cancellation.py tests/test_media_plans.py tests/test_operation_log_contract.py tests/test_editor_file_transactions.py tests/test_generation_plan.py -q
node --test tests/api.cjs tests/resource_state.cjs tests/media_job_polling.cjs tests/cropper_resource_state.cjs tests/wonder_resource_state.cjs tests/shared_display.cjs
node tests/resource_state_browser.cjs
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m towards_victory_editor_web --check
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts/validate.py --changed --fix --ai-report
git diff --check
```

- Python 11 文件一次全量 241 passed，3 条已有 FastAPI/httpx 与 `binary_dilation` 弃用警告；包含临时副本中的完整 Wonder 生成链及产物逐字节比对。
- Node 47 项通过，其中共享展示组件 10 项用原生 ES module；覆盖同一预览/提交体、请求冻结与重复提交、返回编辑/Escape、失败保留 draft/base、生成/恢复报告、共享作业文件报告及转义。8 个改动/新增前端模块 `node --check` 通过。
- Chrome 使用真实 ES module、DOM、GET 和两个编辑器的服务端只读 preview，验证可见 diff、取消后继续编辑、确认提交体一致、409/生成失败后的草稿与诊断、四编辑器状态、媒体/cropper 共享报告、轮询恢复/取消失败/404 解锁/422 停止跟踪，以及 HTML 数据转义；无页面未捕获异常。写请求和网络错误由浏览器拦截，未写业务文件或调用图片 API。
- Web `--check` 通过：9 个注册工具、5 个可运行、196 张裁剪图；changed validation 通过（4 个适用文件，无错误或警告），`git diff --check` 通过。重复日志样板已删除，`escapeHtml`/`renderTabs`/作业按钮标记/`new JobPoller` 均只有共享实现；生产 `fetch()` 仍仅位于 `api.js`。

重构审计缺陷修复验收：2026-10-10，Windows + eu5 Python 3.11.15 + Node 22.19.0。修改前运行 task-scoped `ai_context.py`。

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m pytest --basetemp .pytest-claude-fix tests/test_media_job_contract.py tests/test_media_cancellation.py tests/test_media_plans.py tests/test_operation_log_contract.py tests/test_cropper_resource_contract.py -q
node --test tests/api.cjs tests/resource_state.cjs tests/media_job_polling.cjs tests/cropper_resource_state.cjs tests/wonder_resource_state.cjs
```

- 审计前基线：11 个编辑器/媒体测试文件一次全量 241 passed；Node 36 项、Web `--check` 通过。
- 修复后：五个媒体/操作/cropper 测试文件 110 passed；Node 37 项通过。两个新回归用例在撤掉对应修复时失败。
  未重跑 Chrome 验收。

本次审计收尾验收：2026-10-10，Windows + eu5 Python 3.11.15 + Node 22.19.0 + 本机 Chrome headless。修改前运行 task-scoped `ai_context.py`。

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m pytest --basetemp .pytest-audit-final tests/test_media_cancellation.py tests/test_media_job_contract.py tests/test_media_plans.py tests/test_operation_log_contract.py -q
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m pytest --basetemp .pytest-audit-crop tests/test_media_cancellation.py::test_crop_conversion_stops_dispatch_and_waits_for_active_workers tests/test_media_cancellation.py::test_crop_conversion_dispatches_all_jobs_on_success -q
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m pytest --basetemp .pytest-audit-crop-contract tests/test_cropper_resource_contract.py -q
node --test tests/api.cjs tests/resource_state.cjs tests/media_job_polling.cjs tests/cropper_resource_state.cjs tests/wonder_resource_state.cjs
node tests/resource_state_browser.cjs
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m towards_victory_editor_web --check
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts/validate.py --changed --fix --ai-report
git diff --check
```

- Python 分批通过 110 项：四文件 104 passed，随后新增的裁剪调度 2 项通过，cropper 资源契约 4 项通过。保留已有 FastAPI/httpx 和 `binary_dilation` 弃用警告。
- Node 35 项通过，修改的三个前端模块通过语法检查；Python 修改文件通过编译检查。
- Chrome 验收通过四编辑器状态恢复、统一 Prompt、轮询恢复、取消失败及 job 错误；新增媒体/cropper 的 404 自动解锁、422 手动停止跟踪和日志保留，无页面未捕获异常。真实 GET，写请求与网络错误由浏览器拦截，未写项目业务文件。
- Web `--check` 通过：9 个注册工具、5 个可运行、196 张裁剪图；changed validation 通过（22 个适用文件、无错误或警告），`git diff --check` 通过。
- 提交前收尾（媒体停止跟踪后可取消、future 登记清理、待议事项整理）：Node 36 项通过，前端模块 `node --check` 通过；媒体、操作库与 cropper 契约五文件 pytest 110 passed；Web `--check`、changed validation（22 个文件、无错误或警告）与 `git diff --check` 通过。本轮未重跑 Chrome 验收。

上一切片验收：2026-10-09 至 10-10，Windows + eu5 Python 3.11.15 + Node 22.19.0 + 本机 Chrome headless。
pytest 使用仓库内新的 `--basetemp` 目录，避免 Windows 临时目录权限和深路径问题。

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m pytest --basetemp .pytest-tmp-final tests/test_operation_log_contract.py tests/test_media_job_contract.py tests/test_media_plans.py tests/test_wonder_resource_contract.py tests/test_wonder_payload_loading.py -q
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m pytest --basetemp .pytest-prompt-final tests/test_wonder_resource_contract.py tests/test_media_job_contract.py -q
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m pytest --basetemp .pytest-other-final tests/test_cost_reward_resource_contract.py tests/test_victory_tree_resource_contract.py tests/test_cropper_resource_contract.py tests/test_editor_file_transactions.py tests/test_generation_plan.py -q
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m pytest --basetemp .pytest-vt-final tests/test_victory_tree_resource_contract.py::test_failed_write_keeps_disk_and_cached_draft -q
node --test tests/api.cjs tests/resource_state.cjs tests/media_job_polling.cjs tests/cropper_resource_state.cjs tests/wonder_resource_state.cjs
node tests/resource_state_browser.cjs
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m towards_victory_editor_web --check
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts/validate.py --changed --fix --ai-report
git diff --check
```

- Python 分批覆盖当时全部 222 项：首批 141 passed；新增 Prompt/关闭测试后相关两文件 96 passed；其余五文件 76 passed、1 failed（旧断言把新错误日志算作草稿变化），更新为分别核对节点、base 与日志后该项 1 passed。最终没有未解决失败或跳过；并非一次全量运行。既有警告来自 FastAPI/httpx 与 style 脚本的 `binary_dilation` 弃用提示。
- Node 30 项全部通过；七个前端模块的 `node --check` 通过。覆盖请求期间冻结、失败保留 draft/base、重复请求、轮询恢复、取消失败、终态与旧响应隔离。
- Chrome 通过 CDP 驱动真实 ES module 和 DOM：四编辑器保存期间冻结、cost/reward 与 Victory Tree reload 期间冻结、409 后草稿保留、Prompt 统一提交/reload 丢弃草稿、英文 cropper 提示、轮询自动恢复、取消失败后可重试、job 错误显示；无页面未捕获异常。读取使用本地真实服务，写请求与网络失败由浏览器拦截模拟，未写入项目业务文件或调用图片 API。
- 本次 Chrome 使用隔离 profile 与 `--no-sandbox`，由 `tests/resource_state_browser.cjs` 复现。旧 `wonder_payload_browser.cjs` 的 Playwright 场景本次未执行（环境无 Playwright）；已适配 Prompt 草稿纳入 reload 确认的对话框处理。
- Web `--check` 通过：9 个注册工具、5 个可运行、196 张裁剪图；changed validation 通过（13 个适用文件、无错误或警告），`git diff --check` 通过。生产代码的 `fetch()` 仍仅位于 `static/api.js`，独立 Prompt 路由及旧保存函数已删除。

## 子代理启动顺序

涉及工具整合或 Web 重构时，先读：

1. 根目录 `CLAUDE.md`
2. `docs/knowledge/BRIEF.md`
3. 本文（先读“使用规则”和“当前焦点”）
4. `towards_victory_editor_web/README.md`
5. 需要架构背景时再读 `Towards_Victory_Editor_Web_Assessment.md`

然后运行 `scripts/ai_context.py --files <目标文件>`，检查生成文件归属和相关风险卡。
