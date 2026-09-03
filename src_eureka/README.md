# Eureka Prototype: Guilds Advance

这是"尤里卡"（Eureka）机制的第一个可测试原型，基于第一时代革新"guilds"（行会）。

## 功能概述

**尤里卡条件**：拥有至少一个市场中心（`is_market_center = yes`的location）

**效果**：
- **后端**：研究guilds时速度+50%（`research_speed_modifier = 0.5`）
- **前端**：进度环和百分比文字视觉上"跳"到+40%（实际进度仍由后端速度加成驱动）

## 文件结构

### 后端逻辑（脚本层）
- `in_game/common/scripted_triggers/tv_eureka_guilds_triggers.txt`
  - `tv_eureka_guilds_condition_met_trigger` — 检查是否拥有市场中心
  - `tv_eureka_guilds_boost_active_trigger` — 检查boost变量是否已激活

- `in_game/common/scripted_effects/tv_eureka_guilds_effects.txt`
  - `tv_eureka_guilds_check_and_activate_effect` — 条件满足时激活boost，设置两个变量：
    - `tv_eureka_boost_active_guilds` — 后端开关（用于`modifier_while_progressing`的`potential_trigger`，GUI 也按此命名约定过滤重复效果行）
    - `tv_eureka_visual_boost_guilds` = 0.4 — GUI显示偏移量（40%）

- `in_game/common/on_action/tv_eureka_guilds_hooks.txt`
  - `on_took_location_in_peace_treaty` — 和约获得地点时检查
  - `on_location_occupied` — 军事占领地点时检查
  - `on_annexed` — 吞并国家时检查
  - 当获得的地点是市场中心时，触发`tv_eureka_guilds_check_and_activate_effect`

- `in_game/common/advances/tv_eureka_guilds.txt`
  - REPLACE guilds定义，添加：
    ```
    modifier_while_progressing = {
        potential_trigger = { tv_eureka_guilds_boost_active_trigger = yes }
        research_speed_modifier = 0.5
    }
    ```

### 前端显示（GUI层）

通过`scripts_eureka/patch_gui_progress.py`从`reference_game_files/game/`重新生成GUI文件。生成器每次先读取原版文件，再对带数量断言的局部锚点进行替换；不要直接手改`src_eureka/in_game/gui/`或`src_eureka/main_menu/gui/shared/advances_tooltips.gui`。

运行`build.bat`时会自动执行生成；也可以单独运行：

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_eureka/patch_gui_progress.py
```

**修改的文件**（输出到`src_eureka/in_game/gui/`）：
- `technology_lateralview.gui` — 科技树主视图（10处修改）
- `agenda_view.gui` — 议程侧边栏（4处修改）
- `advances_lateralview.gui` — 科技侧边栏（进度显示与效果列表）
- `hud_topbar.gui` — 顶部HUD栏（2处修改）

共享提示文件`src_eureka/main_menu/gui/shared/advances_tooltips.gui`也由同一生成器从原版复制并植入Eureka模板、进度环和研究速度提示行。

**修改内容**：
1. **有 advance 上下文的进度环和百分比文字**：
   - 科技树节点使用 `AdvanceNode.GetItem.GetKey`
   - advance 列表使用 `AdvanceItem.GetKey`
   - 只有 key 为 `guilds` 时才显示"真实进度 + 40%"，其他科技回退到原始进度
2. **全局当前研究组件**：
   - 议程、顶部栏和科技页面中央卡片将当前研究的无提示名称与 `Localize('guilds')` 比较；只有当前研究为 `guilds` 时才叠加 Eureka 偏移

3. **Tooltip进度信息**（1处，`technology_lateralview.gui:2218-2235`）：
   - 使用同样的本地化名称比较做门控；仅 guilds 显示视觉偏移

### 本地化
- `main_menu/localization/{english,simp_chinese}/tv_eureka_guilds_l_*.yml` — 行会机制文本
- `main_menu/localization/{english,simp_chinese}/tv_eureka_gui_l_*.yml` — GUI自定义文本
- `main_menu/localization/{english,simp_chinese}/tv_eureka_debug_l_*.yml` — 临时调试事件文本

## 测试方法

1. **构建mod**：运行`build.bat`或`python scripts/build.py`
2. **进入游戏**，选择任意国家
3. **触发条件**：
   - 在任意你拥有的地点上点击"创建市场中心"（UI操作，需要满足游戏条件）
   - 或通过和约/战争占领一个已经是市场中心的地点
   - 或吞并一个拥有市场中心的国家
4. **观察效果**：
   - 变量`tv_eureka_boost_active_guilds`应该被设置（可用debug模式查看）
   - 打开科技树，选择"guilds"作为研究目标
   - 进度环应该立刻显示为40%（视觉hack），并且顶部栏、议程和中央研究卡片保持一致
   - 实际研究速度应该比正常快50%（后端加速）
   - 切换到其他 advance，所有位置的进度环和百分比都应回到该 advance 的真实进度

## 技术要点

### 为什么用`research_speed_modifier`而不是`add_research_progress`？

EU5引擎的限制：
1. `add_research_progress`没有目标参数，只能加到"当前正在研究"的advance上
2. 脚本层无法判断"当前正在研究哪一条advance"（`Player.GetCurrentResearch`只在GUI层可用）
3. 没有`on_research_started`之类的on_action来检测"玩家选中了某个研究目标"

因此无法实现文明6那种"条件满足后，无论何时选中该科技都瞬间送40%进度"的银行制。

解决方案：
- 后端用`modifier_while_progressing`的`research_speed_modifier`真实加速
- 前端用GUI hack让进度环"视觉上"跳到40%，制造"瞬间填充"的手感

### GUI hack的可靠性

带有 `AdvanceNode` / `AdvanceItem` 上下文的调用使用：
```
Select_float(
    EqualTo_string(AdvanceItem.GetKey, 'guilds'),
    Min_float(Add_float(
        Player.GetCurrentResearch.GetProgress,
        FixedPointToFloat(Player.MakeScope.GetVariable('tv_eureka_visual_boost_guilds').GetValue)
    ), '(float)1.0'),
    Player.GetCurrentResearch.GetProgress
)
```

对于没有 `AdvanceNode` / `AdvanceItem` 上下文的当前研究组件，使用
`EqualTo_string(Player.GetCurrentResearch.GetAdvance.GetDefinition.GetNameWithNoTooltip, Localize('guilds'))`；不使用 `GetFlagName`，因为它可能返回本地化文本而不是稳定的数据库 key。

- 当当前行/当前研究不是 `guilds` 时，表达式直接返回真实进度，不读取错误的全局偏移
- 当行是 `guilds` 且变量为 `0.4` 时，显示真实进度+40%

## 已知问题

1. **"创建市场中心"操作没有script-side hook**
   - 玩家在已有地点上手动点击"创建市场中心"时，不会触发任何on_action
   - 目前只能通过"获得一个已经是市场中心的地点"来触发
   - 可能的解决方案：添加monthly pulse检查（性能成本较高），或hook到市场建筑的建造完成事件

2. **GUI变量默认值处理**
   - 如果`tv_eureka_visual_boost_guilds`变量未设置，`GetValue`行为需要验证（可能返回0，也可能报错）
   - 可能需要在游戏启动时给所有国家初始化这个变量为0

3. **其他advance的扩展**
   - 当前只实现了guilds一条
   - 扩展到其他advance需要：
     - 复制一套trigger/effect/on_action（改条件判断）
     - 为每条advance设置独立的开关和视觉变量：`tv_eureka_boost_active_<advance_id>`、`tv_eureka_visual_boost_<advance_id>`
     - advances/technology 效果列表会自动按 `tv_eureka_boost_active_<advance_id>` 隐藏研究速度行
     - 顶部栏、议程和当前研究 tooltip 的进度显示仍需为新增 advance 增加对应的当前研究判断；CurrentResearch 暂未提供可验证的原始 advance key accessor

## 下一步

- [ ] 测试原型，验证后端加速和前端显示是否work
- [ ] 解决"手动创建市场中心"检测问题
- [ ] 设计通用框架：支持配置化定义多条advance的尤里卡条件
- [ ] 评估性能影响（GUI的Add_float调用频率、on_action overhead）
- [ ] 添加玩家通知（条件满足时弹窗提示）
