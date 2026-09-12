# Great Project 唯一 Buff 修改方案

## Modifier 分层规范（先于唯一化执行）

### 四类 modifier 的定义

| 层级 | 作用域 | 数据/生成入口 | 适用仪式样式 |
|---|---|---|---|
| 基础本地 modifier | 工程所在地点 | 最终建筑的 `modifier` | 无 |
| 基础国家 modifier | 工程所有者国家 | `tv_wonder_auto_<mechanic>`，由 `tv_wonder_auto_level_by_wonder_id` 按等级缩放 | 无 |
| 仪式本地 modifier | 工程所在地点 | 风格 2 的 ritual annex；unique ritual 的 step 4 | generic style 2 / unique step 4 |
| 仪式国家 modifier | 工程所有者国家 | 风格 1 的 blessing；unique ritual 的 step 8，完成时 `add_country_modifier` | generic style 1 / unique step 8 |

仪式国家 modifier 是永久国家 modifier：完成入口统一调用
`tv_wonder_mechanics_apply_selected_ritual_static_modifier_effect`，使用
`years = -1 mode = add_and_extend`；失去工程所有权时由 ownership-loss event 移除。仪式本地
modifier 来自 annex 建筑，随 annex 存在于地点范围内。

### 尺寸规则

规范目标是按尺寸决定基础层的存在性：

| 工程尺寸 | 基础国家 | 基础本地 |
|---|---:|---:|
| small | 不施加 | 施加 |
| medium | 施加 | 不施加 |
| large | 施加 | 施加 |

small 的尺寸规则应严格禁止任何基础国家 modifier，包括 `value_movement_*`；现有
`validate_wonder_size_base_country_modifier_rules` 仍把这类 key 当作例外，需要收紧为无条件空集合。
最终建筑生成器把 `wonder_base_country_modifiers` 合并进建筑 `modifier` 只是为了地点窗口的
`ShowModifierEffect` 显示；根据 [Cost_Reward_Unit_Concepts.md] 的 display-only 约定和
`wonders.md` 的作用域规则，这些国家级镜像不会在游戏中作为本地效果生效。实际基础本地效果只来自
`authored_final_building_local_modifiers`，medium 是否为空应按 `final_local` 数据逐项审计。large
同时具备 auto 国家层和最终建筑层。尺寸规则落地需要收紧 small 校验、审计 medium 的 authored local
数据，并为三种尺寸补充显式测试。

### 强度标定

仪式 modifier 的设计强度约等于两个等级的基础 modifier。比较时统一使用同一 modifier 的“等级 1 基础单位”：generic 工程按 2 个基础等级折算，unique 工程的 `base_effect_multiplier = 2` 已使其基础单位翻倍。范围、容量、月度资源、衰减和布尔解锁分别按各自 value kind 标定，不能把数值大小直接跨 kind 比较。

### 扩建叠加语义

- 基础国家 modifier：由 auto modifier 读取国家缓存的工程等级；扩建刷新
  `tv_wonder_auto_level_by_wonder_id` 后按新等级缩放，因此同一工程的基础国家效果随等级累积。
- 基础本地 modifier：最终建筑等级由 `change_building_level_in_location`/同步逻辑维护；建筑
  `modifier` 的数值按建筑等级生效，因此扩建会累积本地效果。尺寸层拆分完成后，只有允许该尺寸的
  基础本地层才可进入最终建筑。
- 仪式本地 modifier 由 annex 建筑提供，建筑等级提升时会按 `modifier` 的原生等级缩放，因此扩建会
  叠加地点效果。仪式国家 modifier 完成时写入固定名称并使用 `add_and_extend`；同名国家 modifier
  不会叠加数值，而是刷新同一条 modifier。当前仪式重复发放/完成 gate 存在独立缺陷，留待单独子任务
  修复，不作为本轮 buff 唯一化的前置改动。若工程被转移，先移除旧所有者的 modifier，再由新所有者
  重新完成仪式。

### 当前状态判定

四类作用域和仪式施加/移除链路已经存在。需要修正或审计的尺寸项只有两类：small 基础国家 modifier
必须严格为空，medium 的 authored `final_local` 必须逐项确认是否为空；最终建筑中用于显示的国家级镜像
不计入本地效果。仪式重复发放是已知独立缺陷，暂不在本方案修复。特别是 unique 工程带 `ceremony`
时，`ritual_plan_for_style()` 当前会用 generic style 1 覆盖自身 `ritual.country_modifier`；必须改为
unique 值优先，否则 YAML 中的唯一 key 不会进入最终产物。

## 目标与现状

本方案针对 Engineering Department 的 136 个历史 Great Project（ID 101–236）。站点汇总显示，当前 ritual country modifier 只有 46 个不同 key；跨 base、final local、ritual 三层共有 151 个重复 key、826 次使用，重复最多的是 monthly_towards_spiritualist（26 次）、local_crown_estate_power（17 次）和 local_max_control/local_defensive（各 13 次）。

“唯一”按 (scope, modifier_key) 判定：同一作用域中，一个正向永久 buff 只能归属于一个工程。第一阶段锁定作者直接控制的 ritual.country_modifier；通用 base/local 继承层维持现状，避免一次改动造成 192 个项目的平衡跃迁。成本、临时 burden、一次性 reward、建筑属性和纯解锁/布尔门槛不计入 buff 唯一性。

## 分配规则

- 每个历史工程只保留一个 ritual 国家 buff；同一 ritual 中的重复 key（例如法罗斯灯塔的 trade_range）删除。由于带 `ceremony` 的 unique 工程会走 generic style 1 覆盖，必须同时调整 `ritual_plan_for_style()` 使 unique 工程优先使用自身 `ritual.country_modifier`。
- key 按工程语义分组分配：港口/航海优先 naval 池，城堡/城墙优先 military 池，宗教建筑优先 religion/culture 池，宫殿/学校优先 admin 池，市场/工坊/矿山优先 economy 池，其余使用 infrastructure 池；池内不重复。
- 下表 key 均来自 data/wonder_editor_catalog.yaml 的 country catalog；落地前再用 data/index/modifier_localization.json 核对名称、正负号和数值类型。
- 数值是首轮平衡带：普通比例 0.05，范围 50–100，容量/上限 1，月度资源 0.05/月；decay/maintenance/food_decay 类按 -0.05。特殊高影响 key 需模拟后再定稿。

## Ritual 国家 Buff 的实际施加链路

- `data/unique_wonders.yaml` 中的 `ritual.country_modifier` 由 `gen_tv_engineering_department_wonder_mechanics_modifiers.py` 生成为独立静态 modifier，名称格式为 `tv_wonder_<wonder_key>_ceremony_modifier`。例如法罗斯灯塔当前生成的 modifier 同时包含 `naval_range = 300` 和 `trade_range = 100`。但当前 `ritual_plan_for_style()` 对带 `ceremony` 的 unique 工程会改用 generic style 1 的国家 modifier，这一步必须移除或改为仅在 unique 自身 modifier 为空时回退。
- 玩家完成仪式后，`tv_wonder_mechanics_apply_selected_ritual_static_modifier_effect` 根据 `tv_wonder_selected_ritual_id`（公式为 `wonder_id * 100 + style`，历史工程 style 1 即 `10101`、`10201`……）分派，并在当前国家 scope 执行 `add_country_modifier = { modifier = ... years = -1 mode = add_and_extend }`。因此这是永久国家 buff，不是地点 local modifier。
- 完成入口包括自动满足条件的 `tv_wonder_mechanics_maybe_complete_active_ritual_effect`、强制完成和跳过仪式路径；这些路径都会调用同一个 static modifier dispatcher，避免只在某一种完成方式下发放。
- 失去工程所有权时，`gen_tv_wonder_ownership_events.py` 生成的 ownership loss event 在 owner scope 执行 `remove_country_modifier`，并清除 `tv_wonder_unique_ritual_completed` 中对应工程 ID。若判定为同一工程的所有权保留，则跳过移除。
- 通用工程的 style 1 不读取 `ritual.country_modifier`，而是读取 `wonder_generic_rituals.yaml` 的 style 1 并生成 `tv_wonder_<mechanic>_ritual_blessing_modifier`；style 2 是地点 annex，style 3 是一次性 reward。最终建筑的等级成长国家 buff 另由 `tv_wonder_auto_<mechanic>` auto modifier 和 `tv_wonder_auto_level_by_wonder_id` map 驱动。

这意味着本方案的 ritual 唯一化阶段需要同时完成两项改动：将 136 个 unique ritual 的
`country_modifier` 写入 `data/unique_wonders.yaml`，并修改 `ritual_plan_for_style()` 的覆盖规则使
这些值真正进入生成链路；随后重生成静态 modifier 和 ritual dispatcher。尺寸规则是独立的校验修正：
收紧 small 的基础国家校验，审计 medium 的 authored `final_local`，并补齐三种尺寸的测试。最终建筑
中用于 tooltip 的国家级镜像无需删除；auto modifier 的等级缩放和 ownership 清理逻辑应保持现有职责。
仪式重复发放问题另行处理。当前仓库生成物仍是旧映射，文档中的 136 项表格尚未写回
`data/unique_wonders.yaml`。

## 136 个工程的首轮映射

| ID | 工程 | 建议唯一 ritual key | 建议值 |
|---:|---|---|---:|
| 101 | 法罗斯灯塔 | naval_range | 100 |
| 102 | 圣索菲亚大教堂 | tolerance_own | 0.05 |
| 103 | 岩石圆顶圣殿 | tolerance_heretic | 0.05 |
| 104 | 吴哥窟 | global_monthly_literacy | 0.05/月 |
| 105 | 波塔拉宫 | country_cabinet_efficiency | 0.05 |
| 106 | 阿尔罕布拉宫 | diplomatic_capacity | 1 |
| 107 | 马丘比丘 | global_monthly_prosperity | 0.05/月 |
| 108 | 姬路城 | global_population_capacity_modifier | 1 |
| 109 | 泰姬陵 | global_population_growth | 0.05 |
| 110 | 紫禁城 | global_road_building_time | 0.05 |
| 111 | 托普卡帕宫 | diplomatic_capacity_modifier | 1 |
| 112 | 圣亚彼得大教堂 | tolerance_heathen | 0.05 |
| 113 | 拉利贝拉岩石教堂群 | cultural_influence | 0.05 |
| 114 | 威尼斯军港 | trade_range | 50 |
| 115 | 马六甲港 | trade_range_modifier | 50 |
| 116 | 德里红堡 | aggressiveness_modifier | 0.05 |
| 117 | 凡尔赛宫 | diplomatic_range | 50 |
| 118 | 特诺奇蒂特兰堤道 | global_rural_build_buildings_efficiency | 0.05 |
| 119 | 阿姆斯特丹运河圈 | trade_sea_efficiency | 0.05 |
| 120 | 麦加禁寺扩建 | cultural_influence_modifier | 0.05 |
| 121 | 长城九边 | rural_migration_attraction | 0.05 |
| 122 | 圣乔治银行 | global_food_capacity | 1 |
| 123 | 卡霍基亚土丘城 | non_rural_migration_attraction | 0.05 |
| 124 | 大津巴布韦石城 | global_food_decay | -0.05 |
| 125 | 伊斯法罕王家广场 | diplomatic_range_modifier | 50 |
| 126 | 京杭大运河 | trade_land_efficiency | 0.05 |
| 127 | 印加皇家道路网 | irrigant_cap_level | 1 |
| 128 | 罗马引水道 | antagonism_breaking_truce_giving_modifier | 0.05 |
| 129 | 苏伊士古运河尝试 | ship_build_speed | 0.05 |
| 130 | 莫斯科克里姆林宫 | diplomatic_reputation | 0.05 |
| 131 | 特奥蒂瓦坎圣城 | cultural_tradition | 0.05 |
| 132 | 吴哥水利工程 | antagonism_declared_war_no_cb_giving_modifier | 0.05 |
| 133 | 荷兰围海工程 | artist_salary_modifier | 0.05 |
| 134 | 马丘比丘梯田 | burghers_estate_allowed_leading_military | yes |
| 135 | 皇家海军船坞 | ship_capture_chance | 0.05 |
| 136 | 西班牙白银舰队 | navy_tradition_from_battle | 0.05 |
| 137 | 奥斯曼朝觐道路 | burghers_estate_levy_size | 0.05 |
| 138 | 坎儿井 | burghers_estate_max_tax | 1 |
| 139 | 明龙江船厂 | navy_tradition_decay | -0.05 |
| 140 | 耶路撒冷圣城 | cultural_tradition_modifier | 0.05 |
| 141 | 巨石阵 | cultures_capacity | 1 |
| 142 | 伦敦塔 | burghers_estate_min_tax | 0.05 |
| 143 | 巴黎圣母院 | burghers_estate_satisfaction_decay | -0.05 |
| 144 | 圣瓦西里大教堂 | cultures_capacity_modifier | 1 |
| 145 | 三一修道院 | global_pop_conversion_speed | 0.05 |
| 146 | 冬宫 | legislative_efficiency | 0.05 |
| 147 | 景福宫 | government_reform_slots | 1 |
| 148 | 长白山祭坛 | global_pop_conversion_speed_modifier | 0.05 |
| 149 | 贝尔格莱德要塞 | antagonism_monthly_change_modifier | 0.05/月 |
| 150 | 梅黛奥拉修道院 | global_pop_assimilation_speed | 0.05 |
| 151 | 贝伦塔 | burghers_estate_satisfaction_recovery | 0.05 |
| 152 | 伊比利亚宗教裁判所 | global_pop_assimilation_speed_modifier | 0.05 |
| 153 | 圣母百花大教堂 | global_heretic_pop_conversion_speed_modifier | 0.05 |
| 154 | 比萨斜塔 | burghers_estate_target_satisfaction | 0.05 |
| 155 | 米兰大教堂 | global_institution_growth_modifier | 0.05 |
| 156 | 梵蒂冈档案馆 | government_size | 1 |
| 157 | 天坛 | monthly_devotion | 0.05/月 |
| 158 | 都江堰 | clergy_estate_levy_size | 0.05 |
| 159 | 大报恩寺琉璃塔 | monthly_religious_influence | 0.05/月 |
| 160 | 景德镇官窑 | global_food_capacity_modifier | 1 |
| 161 | 莫高窟 | clergy_estate_max_tax | 1 |
| 162 | 广州十三行 | clergy_estate_min_tax | 0.05 |
| 163 | 达达尼尔海峡要塞 | global_sailors_modifier | 0.05 |
| 164 | 埃斯科里亚尔修道院 | religious_icon_power_modifier | 0.05 |
| 165 | 托莱多兵工厂 | antagonism_received_modifier | 0.05 |
| 166 | 圣地亚哥朝圣路 | clergy_estate_satisfaction_decay | -0.05 |
| 167 | 萨格里什航海学校 | max_sailors | 1 |
| 168 | 米兰兵工厂 | army_tradition_from_battle | 0.05 |
| 169 | 博洛尼亚大学 | global_max_bureaucracy_slots | 1 |
| 170 | 卡拉拉大理石矿 | global_lumber_output_modifier | 0.05 |
| 171 | 东印度公司 | clergy_estate_satisfaction_recovery | 0.05 |
| 172 | 孔雀王座 | clergy_estate_target_satisfaction | 0.05 |
| 173 | 瓦拉纳西河坛群 | colonial_maintenance_efficiency | -0.05 |
| 174 | 布里哈迪希瓦拉神庙 | maximum_religious_influence | 0.05 |
| 175 | 科纳克太阳神庙 | global_monthly_art_start_chance | 0.05/月 |
| 176 | 法塔赫布尔西格里 | colonial_migration_size_modifier | 0.05 |
| 177 | 卡利卡特港市 | global_naval_supplies_output_modifier | 0.05 |
| 178 | 维利奇卡盐矿 | global_pottery_output_modifier | 0.05 |
| 179 | 瓦维尔城堡 | army_tradition_decay | -0.05 |
| 180 | 扎莫希奇理想城市 | colonial_range | 50 |
| 181 | 格但斯克港 | global_maritime_presence_decay | -0.05 |
| 182 | 马尔堡城堡 | artillery_bonus_vs_fort | 0.05 |
| 183 | 布列斯特犹太会堂区 | colonial_range_modifier | 50 |
| 184 | 维尔纽斯大学 | global_bureaucracy_entrenchment_speed_modifier | 0.05 |
| 185 | 洞窟修道院 | merchant_power_from_maritime_modifier | 0.05 |
| 186 | 扎波罗热塞契 | cossacks_estate_levy_size | 0.05 |
| 187 | 雷吉斯坦广场 | cossacks_estate_max_tax | 1 |
| 188 | 希瓦古城 | cossacks_estate_satisfaction_decay | -0.05 |
| 189 | 布哈拉卡兰宣礼塔 | cossacks_estate_satisfaction_recovery | 0.05 |
| 190 | 费尔干纳王宫 | global_max_control | 1 |
| 191 | 塔什干老城集市 | cossacks_estate_target_satisfaction | 0.05 |
| 192 | 卢浮宫 | global_monthly_control | 0.05/月 |
| 193 | 枫丹白露宫 | counter_espionage | 0.05 |
| 194 | 波尔多港 | global_merchant_power | 0.05 |
| 195 | 马赛旧港 | global_merchant_capacity_modifier | 1 |
| 196 | 里昂丝绸工坊区 | global_production_efficiency | 0.05 |
| 197 | 圣米歇尔山 | country_child_education | 0.05 |
| 198 | 巴士底狱 | expected_army_size_modifier | 0.05 |
| 199 | 卡尔卡松城堡 | fort_limit | 1 |
| 200 | 布列斯特海军港 | merchant_maintenance_efficiency | -0.05 |
| 201 | 科尔马旧城 | crown_power_from_population | 0.05 |
| 202 | 智慧宫 | spy_network_construction | 0.05 |
| 203 | 埃奇米阿津主教座堂 | dhimmi_estate_levy_size | 0.05 |
| 204 | 纳里卡拉要塞 | fort_limit_modifier | 1 |
| 205 | 巴库火神庙 | exploration_mission_speed | 0.05 |
| 206 | 萨那古城 | dhimmi_estate_max_tax | 1 |
| 207 | 美泉宫 | improve_relation_impact | 0.05 |
| 208 | 选帝会议殿 | max_diplomats | 1 |
| 209 | 亚琛大教堂 | exploration_mission_speed_modifier | 0.05 |
| 210 | 纽伦堡帝国城堡 | fort_maintenance_efficiency | -0.05 |
| 211 | 奥格斯堡银行 | global_defensive | 0.05 |
| 212 | 科隆大教堂 | exploration_preparation_time_modifier | 0.05 |
| 213 | 汉萨商会 | dhimmi_estate_satisfaction_decay | -0.05 |
| 214 | 汉萨城市厅 | dhimmi_estate_satisfaction_recovery | 0.05 |
| 215 | 德累斯顿艺术馆 | dhimmi_estate_target_satisfaction | 0.05 |
| 216 | 慕尼黑皇家啤酒厂 | global_raw_material_output | 0.05 |
| 217 | 海德堡大学 | global_garrison_growth | 0.05 |
| 218 | 非斯古城 | diplomacy_importance_modifier | 0.05 |
| 219 | 凯鲁万圣城 | global_garrison_size_modifier | 0.05 |
| 220 | 阿尔及尔海盗港 | global_hostile_attrition | 0.05 |
| 221 | 桑科雷大学 | monthly_diplomats | 0.05/月 |
| 222 | 杰内大清真寺 | global_manpower_modifier | 0.05 |
| 223 | 贝宁城墙 | global_levy_recruitment_speed_modifier | 0.05 |
| 224 | 苏州古典园林 | estate_power_from_cabinet | 0.05 |
| 225 | 芬恩花园 | expected_navy_size_modifier | 0.05 |
| 226 | 江南贡院 | exploration_maintenance_efficiency | -0.05 |
| 227 | 升龙文庙国子监 | global_burghers_city_desired_pop_scaled | 0.05 |
| 228 | 马拉盖天文台 | global_burghers_desired_pop_scaled | 0.05 |
| 229 | 西安钟鼓楼 | global_burghers_estate_power | 0.05 |
| 230 | 贝希斯敦铭文 | annexation_speed_modifier | 0.05 |
| 231 | 北京皇家粮仓群 | global_silk_output_modifier | 0.05 |
| 232 | 布尔萨皇家铸币所 | global_silver_output_modifier | 0.05 |
| 233 | 恩德伦宫廷学校 | casus_belli_creation_speed_modifier | 0.05 |
| 234 | 阿瑜陀耶外国使馆区 | bank_interest | 0.05 |
| 235 | 云南卫所屯田带 | global_levy_size_modifier | 0.05 |
| 236 | 舟山烽火台网 | global_supply_limit_modifier | 1 |

表中顺序固定为 ID 101 到 236；实现时按 ID 读取，禁止按名称排序后再分配。若某 key 的官方 value kind 不是比例/整数，按 localization 索引的 kind 转换，不能静默改变类型。

## 分阶段落地

1. 在 data/unique_wonders.yaml 将每个 ritual 的 country_modifier 改为单 key，并按本表写值；保留 ritual 的事件、建筑和奖励逻辑。
2. 运行生成器，检查生成的 modifier 文本，不直接编辑 src_engineering_department/ 下的产物。
3. 审计 ritual_country_modifier：行数应为 136，distinct key 应为 136，重复集合为空；再检查全局正向 key 的跨层重复，列为第二阶段 backlog。
4. 若要达到所有层都唯一，给 unique wonder 增加 per-wonder base/local override（或拆分共享层），再把同一审计扩展到 base_modifiers、final_local 和 ritual；每次迁移一个 archetype 并做战役存档回归。

## 验收标准

- jq 汇总的 136 个 ritual 项目全部存在且每项只有一个 country modifier。
- sort | uniq -d 对 key 无输出；所有 key 都能在 editor catalog 和 localization index 找到。
- 普通比例值绝对值不超过 0.10，范围值不超过 300，月度值不超过 0.10/月。
- 本地 modifier 仍只通过 final building 作用于工程所在地点，国家 modifier 不写入建筑 local scope。
- 完成生成后执行：

```sh
python3 scripts/validate.py --changed --fix --ai-report
python3 scripts_engineering_department/test_wonder_mechanics_rules.py
```
