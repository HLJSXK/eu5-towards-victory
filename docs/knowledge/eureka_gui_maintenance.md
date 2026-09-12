# Eureka GUI 维护经验

记录日期：2026-09-03

## 文件维护边界

Eureka 覆盖的完整 GUI 文件不应手工维护。原版文件位于
`reference_game_files/game/`，部署文件位于 `src_eureka/`；两者之间的差异由
`scripts_eureka/patch_gui_progress.py` 生成。

生成流程必须是：读取原版文件 → 对明确的 vanilla 锚点做局部替换 → 检查每个替换的
数量 → 写出完整副本。数量不匹配时应直接失败，不能猜测新布局或静默跳过。相关 GUI
生成应在 `build.bat` 中自动执行。

当前生成器负责：

- `technology_lateralview.gui`、`advances_lateralview.gui` 的 Eureka 进度显示与效果行过滤；
- `agenda_view.gui`、`hud_topbar.gui` 的当前研究 PieSlice；
- `technology_lateralview.gui` 的当前研究 Tooltip 进度行；
- `main_menu/gui/shared/advances_tooltips.gui` 的共享研究 Tooltip、PieSlice 和 Eureka 提示。

## 已验证的 GUI/Jomini 事实

1. GUI 表达式不能调用 scripted trigger；需要在脚本层把结果镜像到变量，再用
   `MakeScope.GetVariable('...').IsSet` 读取。
2. `AdvanceEffectItem.GetTitleEffect` 是可显示的本地化文本对象，不是可直接比较的
   CString。它与 `Localize(...)` 即使显示相同，`EqualTo_string` 仍可能返回 `N`；不要
   追加未经验证的 `.GetString`。
3. 研究速度效果行可用稳定的图标/键特征过滤，例如
   `StringContains(AdvanceEffectItem.GetIcon, 'research_speed')`，再叠加 Eureka 激活变量。
4. `AdvanceNode.GetItem.GetKey` 与 `AdvanceItem.GetKey` 可用于节点/列表上下文；全局
   `CurrentResearch` 组件没有经过验证的原始 advance-key accessor，因此现阶段使用
   `GetNameWithNoTooltip` 与 `Localize('guilds')` 做门控。
5. 进度 PieSlice 的视觉加值只应在目标 advance 且 Eureka 激活时生效；实际研究速度仍
   由脚本 modifier 提供，GUI 公式不是后端状态来源。

## 验证清单

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_eureka/patch_gui_progress.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts/validate.py --changed --fix --ai-report
git diff --check
```

Advance is a game concept, not a synonym for `advances_lateralview.gui`. Any
Advance/Eureka display change must audit all five GUI surfaces above before
implementation and explicitly justify each surface that remains unchanged.

生成器应可重复运行且输出稳定。游戏内仍需检查实际渲染和悬停 Tooltip，因为 GUI
表达式错误经常只在控件显示或悬停时进入 error.log。
