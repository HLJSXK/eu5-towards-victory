# Editor/Web 工具整合重构状态

本文是工具整合与 Web 重构的当前状态入口；[架构评估](Towards_Victory_Editor_Web_Assessment.md) 保留基线和理由，详细过程查 git 历史。

## 使用规则（worker 必读）

- **选题、分工、契约与验收以[改进分工工作文档](Editor_Web_Work_Plan.md)为准。** 按其工作包（WP）、依赖图与
  第 2 章共享文件合并顺序领取；依赖已满足、文件集不重叠的 WP 可并行，不再只推进单一焦点。
  批次顺序与派单形态见[批次交接](Editor_Web_Handoff_2026-10-12.md)。
- **已关闭阶段只修缺陷。** 仅当发现会导致错误结果、数据丢失或测试失败的问题时才修改；
  性能、整洁度和边界说明类改进不在范围内。
- **越界即停。** 需要改动工作文档第 6 章契约、跨 WP 重构或触及第 9 章“不做”清单时，停下并报告，等待确认。
- **新问题只登记在[独立待办](Editor_Web_Refactor_TODO.md)**（缺陷或待议，每条一行）；本文件的“已知缺陷”“待议事项”
  两节只保留指向该文档的摘要，不扩写“已接受限制”。
- 完成一个 WP 后在本文“验证记录”按既有格式补充命令与结果；不要写成按提交排列的历史日志。


## 当前焦点：按工作文档并行执行工作包（2026-10-12）

选题以[Editor/Web 改进分工工作文档](Editor_Web_Work_Plan.md)为准，本节只给入口：P0 为 WP-00～WP-03，
P1 为 WP-04～WP-11，P2/P3 为 WP-12～WP-14；依赖与验收标准见该文档第 2–7 章，评估证据见其附录 A。

用户已确认的决策（2026-10-12）：胜利树保持当前定位（只修标注）；`task_pool.yaml` 继续维护；后端走逐域资源化；
原“后续任务 2/3”关闭（见下方“后续任务”）。验证统一使用 `scripts/run_editor_tests.py`。

进度（批次见[交接](Editor_Web_Handoff_2026-10-12.md)）：**批次 A（WP-00～WP-04）、批次 B（WP-05、WP-06、WP-08）已收口**，
独立验收通过；批次 C 进行中：WP-10 → WP-07 → WP-09（`index.html` 串行），WP-09 已合并。

## 已完成切片：测试提速（2026-10-12）

用户授权自行决定方案。默认层（`scripts/run_editor_tests.py`）从约 18 分钟串行降到 **48 秒**，完整层 `--full` **90 秒**。

- 热点是 Wonder 服务加载（每次约 18 秒）：`wonder_localization_lib` 与 `sources.py` 的 YAML 改用 libyaml `CSafeLoader`（保留重复键检查）；
  `expand/collapse_wonder_localization_data` 只加载一次机制数据并传给 11 个派生键函数（原每个各加载一次）。加载降到约 3.4 秒，
  全部奇观详情、摘要、本地化与机制数据的序列化哈希与修改前一致。libyaml dumper 在两个数据文件上换行折叠不同，写出端不改。
- `platform.record_file_inputs` 用审计钩子记录一次加载打开的文件和扫描的目录（含参考游戏本地化，约 1,070 个文件），
  `GET editor.wonder` 只在其中某项 stat 变化时重新解析（未变化 0.06 秒）；commit 与 cost/reward 回调仍强制 reload。
  Chrome 验收中这一项原占 373/483 秒。
- `server.py` 不再在导入时构建默认应用（原每个 xdist worker 导入即多一次完整加载并打开默认操作库）；启动器改用
  `create_default_app` 工厂，已实测启动并返回资源。
- 测试：安装 `pytest-xdist` 3.6.1，`--dist worksteal`；不调用 Wonder 路由的 8 个 HTTP 测试经 `tests/conftest.py` 的
  `without_wonder_service` 跳过加载；真实 41 个生成器逐字节比对标记 `slow`（`pytest.ini` 注册），只在完整层运行。
  Node、pytest、Web check 并行，输出写文件避免管道阻塞。图片修复用例因 handler 校验返回尺寸无法缩小，保留在默认层。
- 何时跑完整层：改生成器、生成 DAG、Wonder 源数据或前端编辑器后，提交前运行 `--full`。

## 已完成切片：Wonder 提交后同步 cost/reward base（2026-10-12）

- Wonder commit 返回 `written_paths`（实际写入的源文件）；“写入路径与 base 相交 → 空闲后保留草稿刷新”由 `editor_panel.js`
  的 `refreshKeepingDrafts` 选项统一负责，Wonder 适配层删除自有监听与待刷新标记，改为提供刷新函数并在详情加载后调用 `panel.sync()`。
- cost/reward 接入：重新读取资源、替换 base/saved，按 token 重套 edits；原值变化列入日志并保留草稿，条目已删除的草稿丢弃并告警；
  读取失败保留原状态与草稿。Victory Tree、cropper 不写共享源文件，不接入。

## 已完成切片：收尾整合（2026-10-12）

- cost/reward 提交返回实际写入源路径并派发 `resource-committed`；Wonder 在请求结束后同步相交资源的 base、saved、摘要与详情，保留并重套全部 `pageDrafts`，逐字段报告原值冲突；失败保留旧状态，手动 reload 仍丢弃草稿。
- 修复删除当前奇观后的 reload、数字字符串 YAML 预览及结构标量 yes/no 类型、`on_error` 覆盖原始异常，以及首次加载/保存后渲染/取消后渲染错误文案、cropper 日志顺序、媒体失败日志。
- 删除 ritual specs 的虚假 Prompt 输入声明；三个 Node 测试迁至原生 ES module，cropper 页面 VM 测试注明保留；旧 Playwright 场景并入 Chrome，删除旧脚本。
- 状态文档压缩至 250 行内；按本次用户要求不扩写已接受限制，待议项和关闭决定归入[独立待办](Editor_Web_Refactor_TODO.md)，同步/异步统一调度并入后续任务 3。

## 已完成切片：Wonder 列表、图片与元信息面板（2026-10-12）

- `wonder_panels.js` 通过 getter/回调管理类型筛选、搜索、列表、元信息和图片。
- 页面保留名称/等级预览、render 编排与详情水合；Node 与 Chrome 覆盖筛选、转义、选择和图片状态。

## 已完成切片：Wonder 草稿与修改追踪（2026-10-12）

- `wonder_drafts.js` 持有纯数据草稿增删、脏页统计、名称/等级键与详情回填；恢复原值会删除草稿。
- 字段和 Prompt 直接更新对应草稿，结构值回填恢复 editor options；移除全页 DOM 采集。

## 已完成切片：仪式设计与 Prompt（2026-10-11）

- `wonder_rituals.js` 工厂持有目录、详情缓存、请求去重、失效代次和面板 DOM；页面持有资源状态及 Prompt 草稿。
- 目录按标签、详情按展开加载；reload 丢弃旧响应，目录渲染保留 Prompt 节点、焦点和光标。

## 已完成切片：结构化字段与可搜索下拉框（2026-10-11）

- `wonder_fields.js` 工厂管理六类字段、可搜索选项、预设与 Code State；通过回调传递字段变化、原型跳转、等级预览。
- 页面持有草稿和导航；模块无页面反向依赖，Chrome 覆盖真实字段/目录和多实例隔离。

## 已完成切片：Wonder 前端结构值编解码（2026-10-11）

- `wonder_values.js` 负责规范化、editor option 剥离/恢复、行编解码、仪式/典礼 payload、选址脚本与 YAML 预览。
- 模块无 DOM/页面状态依赖；Node 调用真实后端交叉核对规范化结果，Chrome 验证字段预览。

## 已完成切片：清理（2026-10-11）

- 删除不可达分支与无调用入口；job 生命周期字段只保留在 `operation`，Web `--check` 失败退出码为 1。
- Wonder commit 使用 mixin，即使 `regenerate=false` 也锁定 Wonder 与 cost/reward；补齐领域风险卡路由。

## 已完成切片：Wonder 后端领域模块（2026-10-11）

- `services/wonder/` 按源文件、值、目录、选址模板/规则、本地化、字段类型/构建、模型划分职责，调用方直接导入。
- 原单体和重复定义已删除；全体详情、摘要、目录与拆分前一致，完整生成链逐字节回归通过。

## 已完成切片：Wonder 保存/加载/预览（2026-10-11）

- `wonder_resource.py`、`wonder_preview.py`、`wonder_commit.py` 分别负责加载/校验、候选字节/字段 diff、事务/生成；前端适配层使用共享 preview→确认→commit。
- 首屏先列表后详情；reload 整体替换；提交成功接受新 base 并清草稿，详情失败提供只读重试；日志保留操作/生成/恢复报告。

## 已完成切片：审计缺陷修复（2026-10-11）

- 修复隐藏工具内预览模态框、dds_icon 缺少资源锁、取消掩盖回滚诊断、终态残留取消错误及 Wonder 错误不可复制。
- 五项回归均确认撤掉修复会失败；关闭阶段只修会导致错误结果的缺陷。

## 已完成切片：前端共享展示层（2026-10-10）

- `display.js`、`editor_panel.js` 统一转义、日志/状态、标签、生成/恢复报告与保存前预览；预览确认和提交共用冻结请求体。
- `job_panel.js` 统一媒体/cropper 状态、轮询、取消和产物报告；通用样式位于 `shared.css`，提示中文、技术标识保留原文。

## 已完成切片：重构审计缺陷修复（2026-10-10）

- 成功发布同步删除 handler 在 staging 删除的可选输出，避免旧 PNG 重新覆盖 DDS；失败不发布。
- 轮询先安排下一次查询再渲染，渲染异常正常上报，避免活动作业永久冻结。

## 已完成切片：提交前审计收尾（2026-10-10）

- 404/410 解除本地跟踪，其他查询失败允许重试/停止跟踪；停止跟踪后媒体任务仍可取消，旧响应失效。
- lifespan 独占 JobManager；关闭取消排队任务并等待运行任务、终态持久化；图片请求/重试及裁剪调度支持协作取消。
- 修正失败产物/回滚报告；ResourceState 分开请求代次与资源 revision，replace 不结束请求，reset 明确放弃在途请求。

## 已完成切片：资源状态层与审计修复（2026-10-09 至 10-10）

- 四编辑器共用 ResourceState，媒体/cropper 共用 JobPoller；请求期间冻结，失败保留草稿，Prompt 纳入 Wonder 统一保存。
- 发布前逐文件复核，失败恢复并保留恢复错误；操作库打开前取得 OS 文件锁，拒绝第二个持有者。

## 已完成切片：前端共享请求层（2026-10-08）

- `api.js` 是生产 fetch 的唯一入口，ApiError 保留状态码、服务端诊断、操作与生成报告；非 JSON body 只读一次。
- 五个前端共用错误分类，区分 resource_busy 与 resource_changed，提示包含真实资源或路径。

## 已完成切片：媒体暂存发布与失败恢复（2026-10-08）

- 五个 handler 只核对声明输入/输出，在 staging 执行，清理后校验，再逐文件发布；失败、取消和输入冲突不发布。
- 正式路径外部变化与中间文件分开报告；发布回滚失败保留备份，中断提示人工核对；与直接运行产物逐字节比较通过。

## 已关闭阶段：统一操作层（2026-10-05 至 10-08）

- `run_operation` 共用资源锁、生命周期与取消判定；OperationStore 持久化操作和媒体详情，可在重启后查询，终态保留 30 天。
- 中断操作标记失败且不重放；日志按游标读取，options/result 检查 JSON 契约；调度统一留待后续任务 3。

## 更早完成的基础

- 四编辑器使用资源 load/validate/preview/commit，SHA-256 base、字段预览和失败恢复；Wonder 详情、仪式与目录按需加载。
- Wonder 声明式 DAG 含 41 个脚本、40 个产物，按输入组选择根；共享产物检查，9 个工具/5 个可运行 handler，统一启动入口与 `--check`。

## 已知缺陷

当前无未解决条目；本焦点修复与保留事项见[独立待办](Editor_Web_Refactor_TODO.md)。新发现问题只在该文档登记。

## 待议事项

保留四项：既有产物未重写检测、cost/reward 派生字段 diff、中断 staging/备份恢复、JobManager 执行闭包拆分；原文见[独立待办](Editor_Web_Refactor_TODO.md)。

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


## 后续任务

1. **已完成：Wonder 单体拆分。** 当前页面剩余 render 编排、名称编辑器和详情水合保留。
2. **已关闭（用户 2026-10-12 决定）：** 跨资源 `ChangeSet`、完整输入依赖图、领域产物语义校验和跨资源预览。
   单用户本地工具中跨资源同步已由 `written_paths` + 保留草稿刷新覆盖，收益不抵设计成本。
3. **已关闭（用户 2026-10-12 决定）：** 跨进程持久锁与状态存储、同步提交与异步调度统一。
   工具只服务单进程本地使用，现有进程内锁与 OperationStore 已足够。

后续工作以[改进分工工作文档](Editor_Web_Work_Plan.md)的工作包为准。

## 当前架构边界

- 资源契约和执行位于 `services/platform.py`；OperationStore 持久化，HTTP 同步提交与 JobManager 线程池分别调度。
- Wonder DAG/命令执行位于 `services/generation.py`；产物清单与格式检查位于 `services/artifacts.py`。
- 媒体注册/计划/作业位于 `services/tooling.py`，领域 handler 位于 media_plans/media_tools/cropper；API、锁与输入组详见 [README](../../towards_victory_editor_web/README.md)。

## 验证记录

### WP-11 前端：胜利路径标签页（2026-10-13）

`b6d0b8e9`。实现者 Codex 写完代码后在自验前被系统内存回收终止，未产出报告；调度方补跑验证后提交（非实现者自验，但仍非独立验收者）。

- `node --test tests/victory_paths.cjs` → **21 passed / 0 fail**，覆盖字段取值与命名、按路径分组、草稿写入与 rebase、
  请求构造、奖励引用缺失检测、预览与生成计划文本、控制器与面板。
- `node tests/resource_state_browser.cjs` 全量通过，新增行：
  `Victory paths acceptance passed: lazy live GET, grouped fields and three runtime slots, eight usable tabs,
  intercepted preview names milestone threshold, cancel keeps draft/base, frozen commit body, 409 draft-preserving
  refresh, unresolved rewards block saving; no business writes.` 其余 11 个子场景（含 WP-07/09/10/12 的）同时全绿。
- 交付：`static/victory_paths.js`（新标签页"胜利路径"）、`victory_paths.css`、`index.html` 标签与 section、
  `shared.css` 追加段、`tests/victory_paths.cjs`、`tests/victory_paths_browser.cjs`（在 `resource_state_browser.cjs` 挂载）。
  奖励引用失效时禁止保存；预览命名被改字段；取消保留草稿与 base；409 后刷新保留草稿；不调用生成器执行端点。
- 标签栏增至 **8 个标签**（WP-13 需据此做窄屏与令牌统一）。
- 遗留：本 WP 无独立验收者复跑（原实现者的自验未完成），验收强度低于前几个 WP；若需同等强度可另行复跑。

### WP-07：本地化编辑器页面（2026-10-13）

`608a90b5`。实现者因 API 余额中断、代码留在工作区未自验，由验收 agent 验证并修缺陷（未重写实现）。

- 默认层 **471 passed**，Node / web-check / Chrome 全绿（140.2 秒）；changed validation 0 errors（7 条既有索引头告警）。
- 交付：双列 EN/ZH、缺译高亮、过滤（全部/仅缺译/仅已改动）、搜索、Ctrl+S、预览→确认→提交走
  `editor_panel` 既有流程；生成物分组只读并给出 data 源；`localization_text.js` 在模块头与 README 写明支持/不支持范围
  （不支持 `@icon!` 贴图、自定义 loc 函数展开、字体排版）；`editor_panel.js` 仅让 diff 行多带 `item.key`。
- Chrome 场景断言真实只读资源、编辑后页内徽标与标签栏脏点、预览命名被改键且请求体冻结、409 保留草稿、还原后脏点消失。
- 反向验证 2 条承重：撤缺译高亮 → 4 项失败；撤"新增键必须双语言" → 1 项失败。
- 修掉一处真缺陷：`tests/localization.cjs` 末尾测试体被整段复制，Node 报 8 条而实际 7 条。

### WP-10、WP-12（2026-10-13）

同一环境。WP-10 与 WP-12 由 Claude Code / Codex 实现，验收由另一个 agent 在仓库外 worktree 复跑。

- **WP-10（全局壳层）**：`088e8be7`。默认层 **413 passed**、`--full` **415 passed**（四层全绿）。标签栏脏点、操作面板
  （轮询既有 `GET /api/operations`，展开走 `display.formatOperationReport`）、`beforeunload` 仅在脏状态阻止；
  `editor_panel.js` 文案参数化后 cost/reward 与 Wonder 文案与改前逐字一致，胜利树不再出现"重新生成"；补了
  `tool-activated` 的独立 Node 单测。反向验证 4 条均承重（撤 `onDirtyChange`、撤 `beforeunload`、撤胜利树 `copy`、
  撤 `tool-activated` dispatch 各失败一次）。验收发现两处缺陷并已返工（`e9b6272c`）：
  ① 作业指示取排序后首个 `resource_id`，使 Wonder 本地化保存 / 生成器运行 / 媒体作业三类多资源操作一律标到花费/奖励标签
  （6 个真实发出点中 3 个错误）——改为 kind 决定性时用 kind，否则标出全部持有资源的标签；
  ② 轮询刷新后首次点击无法展开详情。
- **WP-12（cost/reward 可用性）**：`72b88a47`。行级脏点与"已改动 N 行"、id/loc 过滤、"仅显示已改动"、
  `scope`/`completion_note` 长文本展开与复制。395 行首屏渲染由约 2.5 秒降至 **10.2 ms**（改为 DOM 行隐藏，断言上限 2500 ms）。
  `value` 列单位只取 `data/cost_reward_units.yaml` 头注释及三处具名特例，未逐一标注的留空、未编造。
  Node 4/4、独立 Chrome 场景通过；反向验证撤 dirty 集合后用例失败。Chrome 场景独立存放，
  未占用 `tests/resource_state_browser.cjs`（该文件本批次由 WP-07 占用）。

### WP-11 后端：victory paths / tasks 资源化（2026-10-13）

`03e37f74` 实现，`35c46fee` 返工。契约 6.4 纯追加。生成根由注册表 `data_inputs` 求交集推导（**17 个生成器 / 32 个去重产物**，
未硬编码脚本元组或产物清单）；写入边界为 BOM、头注释块与换行保留，正文分节注释与未编辑键序不保留（已写入 6.4，未假装保留）；
奖励引用只读、不新增跨资源事务。独立验收在仓库外 worktree 端到端复现两处缺陷并已修：
① 生成器在源文件写入**之前**运行，导致产物永久落后源一拍（源 `threshold: 207` 而产物仍 `>= 200`）——改为同一
`file_transaction` 内先写源、再在事务内跑生成器；② `written_paths` 谎报 34 条而实际只改 5 个文件——改为只列实际变化的源与
`artifacts.changed` 产物。验收另核出 `--full` 下的既有 flaky 超时用例、`6.4` 拆解句算术笔误等，登记于独立待办。

### WP-14 后端：court positions 资源化（2026-10-13）

后端实现完成，独立验收待另派；前端未实现。Windows + eu5 Python 3.11.15，直接解释器运行，未派发子 agent、未提交。
工作文档纯追加 6.5 契约；新增服务、四个端点、测试注册和 `--check` 节，不改 platform、README、static 或真实业务源/产物。
注册表 `data_inputs` 与 `data/court_positions.yaml` 求交集，实际 10 个生成器、10 个唯一产物，均属 `src_court_positions`。

- 定向 pytest **45 passed**（56.02 秒）；最终快测 **43 passed / 2 deselected**（70.74 秒），slow **2 passed / 43 deselected**（13.81 秒）。
  真实生成器仅在临时副本运行，两副本产物逐字节相等；原工作树两份本地化仅 CRLF/LF 不同，基线比较只归一化换行。
- 默认层 `scripts/run_editor_tests.py --workers 2`：**465 passed**（195.66 秒），Node **130 passed**，web-check 通过，总计 197.8 秒。
  auto 首轮 460 passed、Node/check 全过；最终数据集 auto 复跑两条既有短超时断言受并行负载影响失败，不改其实现，以 workers=2 全绿收尾。
- `python -m towards_victory_editor_web --check` 新节：6 positions、引用已解析、10 generators / 10 outputs；最终 changed validation 通过，8 文件、0 errors、7 条既有索引头告警。
- 反向验证：仅在进程内撤引用校验或 artifacts.changed 过滤，对应断言各失败一次；磁盘实现不变。补测 source/generator/reload、产物非法/越界/额外写入的回滚。
- `git diff --check` 通过；清理本次 `.pytest-wp14-*`，runner 自清理其临时目录，其他任务的 `.pytest-*` 不动。详情见 `.editor_state/handoff/WP-14-backend.md`。

### 批次 B / C 前半：WP-05、WP-06、WP-08、WP-09（2026-10-12）

同一环境（Windows 10、eu5 Python 3.11.15、Node 22.19.0、本机 Chrome headless，未用 `conda run`）。
实现：WP-05、WP-09 由 Claude Code，WP-06、WP-08 由 Codex；验收由另一个 Claude Code agent 在提交后于**仓库外 worktree** 独立复跑。

- 复跑：默认层 **413 passed**（126.7 秒）、`--full` **415 passed**（106.5 秒，四层全绿），
  差值 2 项为 `slow` 标记的真实生成器用例；changed validation 通过；`git diff --check` 通过。
- WP-05（校验面板）：三态渲染、按 `rule` 分组与条数、可复制 `file:line`；保存成功派发一次 `resource-saved` → 一次
  `changed:true` 校验；取消预览与 409 冲突均不触发；400/500/504 渲染为"校验未完成"而非通过。
  反向：撤掉派发行 → Node 4 项中 1 项失败，Chrome 面板不再出现结果。
- WP-06（`editor.localization`）：12 个手写双语组 / 24 个 EN/ZH 物理文件（独立枚举一致）；生成物配对文件整体只读并给出
  `source_data`；新增键必须齐备双语、`key:null` 成对删除、缺译拒绝提交、重复键拒绝、BOM 与换行保留、
  base 冲突 409、写入失败恢复；真实副本提交后真实仓库 SHA 未变。返工 R1：写入器原会丢弃 `key:0` 版本后缀并整文件重排
  （875 行文件单值编辑产生 139 行 diff），现改为逐键保留后缀、未改动条目复用原行，单值编辑语义 diff 降为 2 行。
- WP-08（生成器接口）：`--check` 报 115 个可运行生成器 / 50 组，独立解析 `data/generated_files.yaml`（149 行 → 115 脚本）
  复算吻合；未知脚本、请求内输出相交、未登记产物、缺失输出均 400 且拒绝后无写入；超时 504、锁冲突 409；
  `dry_run` 产出 `skipped` 步骤且不写文件；临时副本中真实生成器逐字节比对通过。
  登记 `gen_index.py` 的 7 个输出后 `validate.py` 多出 7 条 `autogen_header` warning（已登记独立待办）。
- WP-09（生成器页）：新增独立标签页，按 root/domain 分组、按勾选顺序多选、组头全选与 indeterminate、运行中锁定且不重复排队、
  常驻"顺序执行、无依赖图"说明、`dry_run` 路径；报告确证复用 `display.formatOperationReport` / `formatJobFiles`
  （面板内零格式化代码）。Chrome 场景走真实只读目录、POST 全被拦截，并断言 `kind=generator_run` 操作数前后不变。
- 上述四项的越界、冲突与遗留登记于[独立待办](Editor_Web_Refactor_TODO.md)；状态文档"当前焦点"进度行同步更新。

### 批次 A：WP-00～WP-04（2026-10-12）

Windows 10 + eu5 Python 3.11.15 + Node 22.19.0 + 本机 Chrome headless；未使用 `conda run`。实现：WP-00～03 Claude Code，
WP-04 Codex；验收由另一个 Claude Code agent 在提交后独立复跑（含仓库外 worktree 中的反向验证与基线对照）。

- 默认层 **316 passed**（58.4 秒，总计 59.9 秒）；`--full` **317 passed**，Node/web-check/Chrome 全部通过（总计 99.1 秒）。
  WP-04 返工 R1 后默认层 **321 passed**（77.7 秒）。changed validation 通过；`git diff --check 0a204b33 HEAD` 通过。
- WP-00：旧“不要从后续任务自选”规则两种引号形式均无匹配；状态文档、工作文档、`CLAUDE.md` 互链可达；未改 `docs/knowledge/`。
- WP-01：新 Chrome 场景 `cropper_canvas_browser.cjs`，首次切标签画布 689×689、中心像素非背景色。反向：只撤 `tool-activated`
  监听或只撤 `ResizeObserver` 仍通过（两者互为覆盖），两者都撤后失败（`sized on activation: null`）。
- WP-02：`wonder_meta_browser.cjs` 在 1600/1000 px 下检查最长 key 不溢出、不交叠；修复前 1000 px 有 4 张卡片溢出（如 `338>176`）。
- WP-03：`misleading_copy_browser.cjs` 断言胜利树设计稿说明与“保存坐标”、2 个 task_pool 分类说明、3 付费/2 本地徽标；
  三个前端文件逐一还原后断言均失败。`--check` 输出在基线与 HEAD 逐字一致。徽标来自新增 `ToolSpec.cost_hint`。
- WP-04：`tests/test_validation_api.py` 70 项；临时副本重复键/缺 zh 文件/缺译均返回 200、`pass:false`、`[LOC]` 前缀。
  手工 curl `{"changed":true}` 200 + `pass:true`（API 1.37 秒 / CLI 1.11 秒）；`../`、`docs/`、绝对路径、`data/../.git` 均 400；
  非布尔 `fix` 422、跨源 `fix:true` 400。反向：撤解析后路径检查、504、`[LOC]` 归一化、fix 本机限制各自对应断言失败。
- 遗留登记于[独立待办](Editor_Web_Refactor_TODO.md)；胜利树保存中途的“重新生成”文案（共享 `editor_panel.js`）交 WP-10。

### 测试提速（2026-10-12）

Windows + eu5 Python 3.11.15 + Node 22.19.0 + Chrome headless + pytest-xdist 3.6.1（12 核）。今后的标准验证命令：

```powershell
C:/Users/Hades/anaconda3/envs/eu5/python.exe scripts/run_editor_tests.py          # 默认层
C:/Users/Hades/anaconda3/envs/eu5/python.exe scripts/run_editor_tests.py --full   # 加 slow 与 Chrome
C:/Users/Hades/anaconda3/envs/eu5/python.exe scripts/validate.py --changed --fix --ai-report
git diff --check
```

- 默认层 48.4 秒：pytest 251 passed（47.4 秒）、Node 90 项、Web check 通过。完整层 89.8 秒：pytest 252 passed、Chrome 验收通过。
- 修改前基线：pytest 串行 560 秒、Chrome 448–483 秒。只换 libyaml 后 pytest 串行 362 秒；加一次加载机制数据后 219 秒。
- changed validation 14 个文件通过；修改前后 Wonder 服务输出哈希一致；`python -m towards_victory_editor_web` 实际启动并返回 `editor.wonder`。
- xdist 下每个 worker 重复报告已有的 FastAPI/httpx 与 `binary_dilation` 弃用警告（14 条），无新增警告类型。

### Wonder → cost/reward 同步修复（2026-10-12）

同一环境。新增 Python 回归 `test_wonder_commit_then_cost_reward_refresh_and_category_save`（真实临时源文件：Wonder 改初始等级写
`unique_wonders.yaml` → cost/reward 旧 base 保存 `ConflictError` → 刷新后分类保存成功且保留 Wonder 写入），与原正向用例共享
`cost_editor` 夹具，两项 passed；新增 Node 用例覆盖“相交路径才刷新、自身/无关路径忽略、请求进行中延后且只刷新一次、草稿不变”；
Chrome closeout 子验收新增“cost/reward 有草稿 → Wonder 保存 → cost/reward 状态已同步、草稿保留、预览用新 base”，撤掉
cost/reward 接入时该场景超时失败。cost/reward 原值冲突/条目删除分支仅代码审查，未单独测试（Wonder 不写 token 文件，实际不可达）。
修复后全量复跑：Node 10 文件 **90 项通过**；12 文件 pytest **252 passed**（572 秒，仓库内 basetemp，3 条已有警告）；Chrome 完整验收通过；Web `--check` 无 FAIL；changed validation 12 个文件通过；`git diff --check` 通过；临时 `.pytest-*` 目录已清理。

### 收尾整合审计（2026-10-12，只读，未提交工作区）

同一环境独立重跑：Node 10 文件 **89 项通过**；Chrome 完整验收（含新增 closeout 子验收）通过；Web `--check` 通过；
12 文件 pytest **251 passed**（首次以仓库外 `--basetemp` 运行时 `test_prompt_save_keeps_detail_without_returning_catalog`
因临时路径不在仓库下而失败，改用仓库内 basetemp 单独重跑通过；属测试对 basetemp 位置的既有假设）；changed validation 11 个文件无错误，
`git diff --check` 通过。逐项复核 A–D 实现与焦点一致；`parseNumberMaybe` 的 yes/no、`+`、下划线数字规则与后端 `parse_editor_scalar` 一致。
新发现反方向同步缺陷一条，登记于“已知缺陷”。关闭项按“不扩写已接受限制”写入独立待办，偏离原焦点“移入已接受限制”的写法但结论一致。

### 收尾整合完整验收（2026-10-12）

环境：Windows、eu5 Python 3.11.15、Node 22.19.0、本机 Chrome headless。修改前已运行 task-scoped ai_context 并阅读 Wonder 风险卡。

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m pytest --basetemp .pytest-closeout-1012 tests/test_cost_reward_resource_contract.py tests/test_victory_tree_resource_contract.py tests/test_wonder_resource_contract.py tests/test_wonder_field_preview.py tests/test_wonder_payload_loading.py tests/test_cropper_resource_contract.py tests/test_media_job_contract.py tests/test_media_cancellation.py tests/test_media_plans.py tests/test_operation_log_contract.py tests/test_editor_file_transactions.py tests/test_generation_plan.py -q
node --test tests/api.cjs tests/resource_state.cjs tests/media_job_polling.cjs tests/cropper_resource_state.cjs tests/wonder_resource_state.cjs tests/shared_display.cjs tests/wonder_values.cjs tests/wonder_rituals.cjs tests/wonder_drafts.cjs tests/wonder_panels.cjs
node tests/resource_state_browser.cjs
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m towards_victory_editor_web --check
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts/validate.py --changed --fix --ai-report
git diff --check
```

- Python 12 文件一次全量 **251 passed**（542.81 秒）；新增真实临时源文件的 cost/reward → Wonder 新 base 连续提交回归，保留 41 个生成器/40 个产物逐字节回归。4 条警告为已有 FastAPI/httpx、binary_dilation 弃用提示和本机 `.pytest_cache` 写权限提示。
- Node 10 文件 **89 项通过**，14 个改动/新增 JS 文件语法检查通过；覆盖保留草稿同步、隐藏页冲突、忙碌延后、刷新失败、删除回落、准确错误日志及前后端源值类型一致。
- Chrome 完整验收通过，无未捕获页面异常；新增连续保存/冲突/失败场景及旧 Playwright 遗留场景。使用真实 GET/只读 preview，源版本变化与 commit 响应由浏览器拦截模拟；真实文件写入由 Python 临时副本测试覆盖，未写业务源文件或调用图片 API。
- Web `--check` 通过（192 个奇观、7,534 个本地化键、9 个工具/5 个可运行、196 张裁剪图）；changed validation 通过（11 个适用文件，无错误/警告），`git diff --check` 通过。验证后已清理仓库根目录全部四个 `.pytest-*` 临时目录。

### 历史切片验收摘要

详细命令、调试过程和提交前重跑见 git 历史；未另迁文档。

- 2026-10-12 面板：Node 79 项，Chrome、Web check、changed validation 通过。
- 2026-10-12 草稿追踪：Node 74 项，Chrome、Web check、changed validation 通过。
- 2026-10-11 仪式/Prompt：Node 71 项，Chrome、Web check、changed validation 通过。
- 2026-10-11 字段编辑器：Node 70 项，Chrome、Web check、changed validation 通过。
- 2026-10-11 结构值编解码：Python 65 项、Node 70 项，Chrome 和前后端交叉核对通过。
- 2026-10-11 清理：Python 250 项、Node 58 项，Chrome、Web check、changed validation 通过。
- 2026-10-11 后端领域：Python 250 项、Node 58 项，序列化哈希与生成产物回归通过。
- 2026-10-11 保存/加载/预览：Python 250 项、Node 58 项，Chrome、完整生成回归通过。
- 2026-10-11 五项审计缺陷：Python 243 项、Node 51 项，Chrome 与反向回归通过。
- 2026-10-11 共享展示提交前收尾：Python 241 项、Node 48 项，Chrome 通过。
- 2026-10-10 共享展示：Python 241 项、Node 47 项，Chrome 与生成回归通过。
- 2026-10-10 可选删除/轮询修复：Python 110 项、Node 37 项，通过。
- 2026-10-10 提交前收尾：Python 分批覆盖 110 项、Node 36 项，Chrome 通过。
- 2026-10-09 至 10-10 状态层：Python 分批覆盖 222 项、Node 30 项，Chrome 通过。
- 2026-10-08 及以前的请求层、暂存发布、统一操作层：本快照无独立计数，后续全量回归已覆盖。
- 2026-10-11 至 10-12 独立审计：后端全量 250 项，前端最终 79 项及 Chrome，通过且无遗留缺陷。

## 接手顺序

阅读 `CLAUDE.md` → `docs/knowledge/BRIEF.md` → 本文 → [改进分工工作文档](Editor_Web_Work_Plan.md) → Web README；
需要背景时再读架构评估。修改前运行 `scripts/ai_context.py --files <目标文件>`，检查生成文件归属及风险卡；按工作文档领取工作包。
