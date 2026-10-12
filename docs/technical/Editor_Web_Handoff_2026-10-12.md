# Editor/Web 分批交接（2026-10-12）

> 交接快照，不是规则来源。**工作内容以
> [Editor_Web_Work_Plan.md](Editor_Web_Work_Plan.md) 为准**（工作包定义、接口契约、验收标准）；
> 本文件只负责"按什么顺序、用什么命令、谁验收"。跨工具调用形态见工作文档第 10 章。

## 0. 这份文件怎么用

新开一个 session（Claude Code 或 Codex 均可）作为**调度方**，把下面这段原样作为开场：

```text
读 docs/technical/Editor_Web_Handoff_2026-10-12.md 与 docs/technical/Editor_Web_Work_Plan.md。
你是本批次的调度方，不要自己实现任何工作包。按交接文件的批次表推进：
每批派单给子 agent（见第 3 节的命令形态），子 agent 完成后按第 4 节派另一个 agent 复跑验收，
验收不通过则退回同一 WP 重做。每批结束后更新 docs/technical/Editor_Web_Refactor_Status.md 的验证记录。
遇到第 5 节任一停止条件时停下来问我，并附上已收集的证据。
```

调度方**不写实现代码**——它只派单、收报告、判定批次是否收口。实现和验收分别由不同子 agent 承担。

## 1. 权威来源与不变量

- 工作包定义、依赖图、共享文件合并顺序、接口契约、验收标准：工作文档第 2–7 章。
- 启动阅读顺序：`CLAUDE.md` → `docs/knowledge/BRIEF.md` → 状态文档 → 工作文档。
- 每个子 agent 动手前必须跑 `scripts/ai_context.py --files <目标文件>`。
- 测试环境：Windows + `C:\Users\Hades\anaconda3\envs\eu5\python.exe` + Node 22 + 本机 Chrome。
  **不允许 `conda run -n eu5`**（在本机受管沙箱里会挂起）；用上面的直接解释器。
- 用户已确认的四项决策（不得推翻）：胜利树保持当前定位、`task_pool.yaml` 继续维护、
  后端逐域资源化、原"后续任务 2/3"关闭。

## 2. 批次表

批次按"文件集互不重叠"划分，同批内可并行；跨批必须等前一批收口（依赖见图）。

| 批次 | 工作包 | 文件占用 | 串行点 | 完成判据 |
| --- | --- | --- | --- | --- |
| **A** | WP-00、WP-01、WP-02、WP-03、WP-04 | 文档；`cropper.js`+`shared.js`；`wonder_localization.css`；`index.html`；`validation.py`(新)+`server.py` | 无（文件集不重叠，可全并行） | 5 个 WP 各自验收通过；`--check` 与默认层测试仍绿 |
| **B** | WP-05、WP-06、WP-08 | `index.html`+`shared.css`；`localization_editor.py`(新)+`server.py`；`generator_runs.py`(新)+`server.py`+`generated_files.yaml` | **`server.py` 串行：WP-06 → WP-08**（或用 worktree 各自改后按此顺序合并） | 三包验收通过；新增 pytest/Node 文件已注册进 `run_editor_tests.py` |
| **C** | WP-10、WP-07、WP-09 | `shared.js`+`resource_state.js`+`index.html`+`shared.css`；`localization.js`(新)+`index.html`；`generators.js`(新)+`index.html` | **`index.html` 串行：WP-10 → WP-07 → WP-09**；WP-10 先做（它独占 `shared.js`/`resource_state.js`） | 三包验收通过；标签栏可容纳全部新标签页 |
| **D** | WP-11、WP-12 | `victory_paths.py`(新)+前端；`cost_reward.js`+`cost_reward.css` | 无重叠，但**先出 WP-11 的前置设计**再动代码 | WP-11 前置设计经用户确认；两包验收通过 |
| **E** | WP-13、WP-14 | 全部 CSS；`court_positions.py`(新)+前端 | WP-13 最后做（需前面所有页面已就位） | 截图矩阵通过；WP-14 验收通过 |

**并行前提**：同批内文件集不重叠才可在同一工作树并行。任何触碰第 2 章"共享文件"清单的 WP，
并行时**必须各自开 worktree**（Codex：`codex exec --worktree`；Claude：让子 agent 在 worktree 中工作），
由调度方按上表串行点顺序合并。

## 3. 派单命令形态

派给 Claude Code（实现者）：

```bash
claude -p "实现 docs/technical/Editor_Web_Work_Plan.md 的 WP-0X。只改该包的接触文件，不得顺手重构。
按第 6 章契约（后端先写契约）与第 7 章验收标准自验，给出反向验证证据。
完成后把实现摘要、验收命令与原始输出摘要写入 .editor_state/handoff/WP-0X.md。" \
  --allowedTools "Read,Edit,Write,Grep,Glob,Bash" --add-dir .
```

派给 Codex（实现者）：

```bash
codex exec -C . --sandbox workspace-write \
  --output-last-message .editor_state/handoff/WP-0X.md \
  "实现 docs/technical/Editor_Web_Work_Plan.md 的 WP-0X。只改该包的接触文件，不得顺手重构。
按第 6 章契约（后端先写契约）与第 7 章验收标准自验，给出反向验证证据。"
```

**建议分工**：批量后端工作（WP-04/06/08/11/14）交 Codex，前端与文档（WP-00/01/02/03/05/07/09/10/12/13）交 Claude Code；
哪个方向都行，但**实现者与验收者必须是不同的 agent**。报告目录 `.editor_state/handoff/` 已被 Git 忽略，
不污染 `git status`；首次使用由子 agent 创建。

## 4. 验收派单

每批实现完成后，**换一个 agent** 复跑该批全部 WP 的验收：

```bash
claude -p "独立复跑 docs/technical/Editor_Web_Work_Plan.md 中 WP-0X…WP-0Y 的验收命令（第 7 章），
不要采信 .editor_state/handoff/ 里的自评结论，自己执行并给原始输出。
逐项判定 pass/fail，列出与实现者结论不一致之处，写入 .editor_state/handoff/accept-<批次>.md。" \
  --allowedTools "Read,Grep,Glob,Bash" --add-dir .
```

验收必跑（第 7 章）：

```powershell
C:/Users/Hades/anaconda3/envs/eu5/python.exe scripts/run_editor_tests.py
C:/Users/Hades/anaconda3/envs/eu5/python.exe scripts/run_editor_tests.py --full   # 改生成器/前端后必跑
C:/Users/Hades/anaconda3/envs/eu5/python.exe scripts/validate.py --changed --fix --ai-report
git diff --check
```

判定规则：
- 验收 agent 的结论优先于实现者自评；两者冲突时以复跑输出为准，并把冲突记进报告。
- **任何 agent 自述"通过"都不构成用户批准**，也不构成批次收口；调度方按验收报告判定。
- 反向验证缺证据 = 该 WP 未完成（P0 与涉及并发/恢复的 WP 硬性要求）。
- Chrome 场景不得写真实业务源文件；真实写入只允许在临时仓库副本中（WP-08 的 pytest 已如此设计）。

## 5. 停止条件（必须回到用户）

1. 需要改动工作文档第 6 章的接口契约。
2. 需要触碰第 9 章"明确不做"清单（含重做平台层、跨资源 ChangeSet、跨进程锁、引入前端框架/构建步骤）。
3. 发现附录 A 的基线事实与实际不符（说明评估已过时，需重新定范围）。
4. 基线测试不绿：先在干净工作区查出原因并报告，不要在红基线上继续叠加实现。
5. 需要付费图片 API、外部网络写入，或需要覆盖/删除仓库中已存在的业务产物。
6. 某个 WP 需要超出自己接触范围的改动（跨 WP 顺手重构一律先问）。

## 6. 批次收口动作（调度方）

1. 确认该批全部 WP 的验收报告存在且判定为通过。
2. 更新 `docs/technical/Editor_Web_Refactor_Status.md`：焦点进度 + 验证记录小节
   （沿用现有格式：环境、实际命令、通过数与耗时摘要；不要写成按提交排列的历史日志）。
3. 改过前端或生成器则同步 `towards_victory_editor_web/README.md`；
   改过 `docs/knowledge/` 下被引用的文件则按 `CLAUDE.md` 重新生成 `BRIEF.md`。
4. 清理仓库根目录的 `.pytest-*` 临时目录与 worktree。
5. 报告下一批的起点与依赖是否满足。

## 7. 当前状态（2026-10-12，供接手核对）

- 工作区只有三份文档的改动：新增本文件与工作文档，修改状态文档、独立待办；**未提交**。
  接手前先确认这批文档改动是否要先行提交（建议先提交，避免与实现 WP 的改动混在一起）。
- 已完成切片（不要重做）：Wonder 单体拆分、共享请求层、资源状态层、统一操作层、
  Wonder 提交后 cost/reward 同步、测试提速（默认层 48 秒 / 完整层 90 秒）。
- 已验证的协作通道：`codex exec`（读到了 `CLAUDE.md`）与 `claude -p` 双向可用；
  `codex` 无服务端 MCP 子命令，MCP 形态只能单向（Codex 挂载 Claude）。
