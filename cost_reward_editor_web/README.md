# Reward & Modifier Unit Editor Web

一个独立的本地 Web 工具，用于编辑 `data/cost_reward_units.yaml` 与 `data/task_pool.yaml`
—— 两套**独立于任何具体机制**的底层数据目录，对应 `docs/design/Cost_Reward_Unit_Concepts.md`
的设计概念（第 1-5 节 / 第 6 节）。这是项目的**底层数据**：奇观建设随机事件
（`data/wonder_construction_events.yaml`）与奇观自身的 modifier 数据
（`data/wonder_base_modifiers.yaml`、`data/wonder_final_buildings.yaml`）是 `cost_reward_units.yaml`
的最初灵感来源，也用到了其中一部分数值，但这些文件之间**没有一一对应关系、也没有代码层面的引用
关系**——奇观维护自己独立的数值，本工具管理的两套目录是给未来项目中其他系统（尚未实现）查表使用的
通用基础数据。

界面按七个标签页分类，前五个对应 `cost_reward_units.yaml`，后两个对应 `task_pool.yaml`：

- **国家级奖励** (`country_reward`) / **本地级奖励** (`local_reward`) /
  **角色级奖励** (`character_reward`) —— 一次性数值变化
- **国家级 Modifier（每级）** (`country_modifier`) / **本地级 Modifier（每级）** (`local_modifier`)
  —— 持续性、随等级累加的 modifier 增量，`value` 表示每提升一级增加的数值，而非一次性数值
- **on_action 型任务** (`on_action_task`) —— 通过挂钩真实 EU5 on_action 检测完成状态的任务；
  可编辑字段为 `wired`（该 on_action 是否已在 `data/pulse_registry.yaml` 中桥接——勾选状态仅记录，
  不会自动改写注册表）和 `completion_note`（如何从裸的 on_action 触发收窄为“此任务已完成”的补充说明）
- **Trigger 型任务** (`trigger_task`) —— 通过每月轮询真实 EU5 trigger 检测“是否达到某状态”的任务；
  可编辑字段为 `comparison`（`gte`/`lte`/`boolean`）和 `representative_threshold`（示意性起始阈值，
  `comparison` 为 `boolean` 时必须留空）

两个任务类别都**不存奖励**：只记录任务如何被检测到，把任务与奖励配对留给未来消费它的具体机制决定。

**目录不单独存代价（cost）行。** 需要代价时，取对应奖励行的 `value` 取相反数即可——
`government_power` 奖励是 `+5`，需要代价效果时直接用 `-5`。唯一的例外是 `country_reward.inflation`：
它的方向是反的，奖励=降低通胀（用负数），代价=提高通胀（用正数）。

国家级条目（gold、`government_power`——即自动适配 legitimacy/republican_tradition/devotion/
horde_unity/tribal_cohesion 五种政府类型的 `add_government_power`、stability、prestige、四个阶层
满意度、research_progress、army_tradition、navy_tradition、manpower、sailors、inflation）与本地级
条目（development、prosperity、laborers）都是一次性效果，`value` 恒为正数（inflation 除外）。
角色级条目（adm、dip、mil、artist_skill）是全 mod 中复现频率最高的一次性效果模式——横跨学院哲学
辩论、艺术展览、科研机制、工程部门、总督府等多个系统，比任何单一国家级数值都更常见。

后两个 modifier 类别是**真正的 EU5 modifier key**，不是一次性效果，也不复用前三类的
gold/government_power 词汇——`clergy_estate_max_tax` 这样的 modifier key 没有对应的一次性效果，
反过来 `government_power` 也不是合法的 modifier key。这两个类别是**穷举提取**的结果：
`country_modifier`（40 条）覆盖了 `data/wonder_base_modifiers.yaml` 中全部约 51 个通用奇观机制里
出现过的每一个数值 modifier key（19 种不同的 `monthly_towards_*` 价值观倾向轴合并为一条
`monthly_towards_axis`），`local_modifier`（43 条）覆盖了 `data/wonder_final_buildings.yaml` 各
机制 `final_local` 中出现过的每一个数值 modifier key，外加每座最终奇观建筑都携带的
`local_cultural_tradition`/`local_cultural_influence` 基线——不是随手挑的一小撮示例。`value`
表示每提升一级增加的持续 modifier 数值，**可以为负数**（例如花费类修正在数值为负时才是有益效果）。

本工具对 `cost_reward_units.yaml` 的五个类别只编辑每个条目的 `value`；对 `task_pool.yaml` 的两个
任务类别只编辑 `wired`/`completion_note`（on_action 型）或 `comparison`/`representative_threshold`
（Trigger 型）。所有类别的 `id`、`loc` 均只读；新增/删除条目、重命名 `id`、新增 `on_action`/`trigger`
名称都需要直接编辑对应的 YAML 文件。`cost_reward_units.yaml` 目前共 104 条（奖励三类各 14/3/4 条，
modifier 两类共 83 条）；`task_pool.yaml` 目前共 96 条（`on_action_task`/`trigger_task` 各 48 条，
含首轮 24 条 + 更大胆的第二轮 24 条，第二轮新增 `requires_target`/`verify_in_game` 两个可选字段，
本工具暂不编辑这两个字段，需直接改 YAML）。

## 安装依赖

```powershell
conda run --no-capture-output -n eu5 python -m pip install -r cost_reward_editor_web/requirements.txt
```

## 启动

```powershell
conda run --no-capture-output -n eu5 python scripts/cost_reward_editor.py
# 或
conda run --no-capture-output -n eu5 python -m cost_reward_editor_web
```

默认监听 `127.0.0.1:8766`（比奇观编辑器的 `8765` 高一位，避免同时运行时端口冲突）。常用参数：

```powershell
conda run --no-capture-output -n eu5 python scripts/cost_reward_editor.py --host 127.0.0.1 --port 8766 --no-browser
conda run --no-capture-output -n eu5 python scripts/cost_reward_editor.py --check
```

`--check` 只做无头数据校验，不启动服务器：`cost_reward_units.yaml` 奖励三个类别要求 `value` 为
正数、modifier 两个类别只要求非零（允许负数）；`task_pool.yaml` 的 `on_action_task` 要求 `wired`
为布尔值且 `completion_note` 非空，`trigger_task` 要求 `comparison` 属于 `gte`/`lte`/`boolean`
且 `representative_threshold` 与 `comparison` 保持一致（`boolean` 时必须为空，否则必须有数值）。

## 保存行为

点击"保存"后，工具会先校验所有本次编辑过的字段（规则同上），只有全部通过才会写盘：涉及
`cost_reward_units.yaml` 五个类别的编辑会整体重写该文件，涉及 `task_pool.yaml` 两个任务类别的
编辑会整体重写该文件（两者各自保留文件顶部的说明注释，互不影响；只有实际被编辑的那个文件会被
重写）。由于这两套都是底层数据，目前没有任何生成脚本消费它们，保存后**不会**触发任何代码生成；
未来当某个系统开始读取其中一套目录时，才需要在那个系统自己的生成脚本里接入。
