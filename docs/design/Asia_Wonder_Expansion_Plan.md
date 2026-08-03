# 亚洲区奇观扩展改进计划

> 依据 `CLAUDE.md`、`docs/knowledge/BRIEF.md` 和现有奇观数据整理。  
> 目标是在不改 schema、不写 bespoke ritual / 专用 GUI / 新后端的前提下，补齐 2 个通用原型、13 座亚洲独特奇观，并清空 9 个零采用原型。

## 已核对基线

- 扩展前基线：通用原型 54 个，本计划使用空位 ID 55、56。
- 扩展前基线：独特奇观 123 座，本计划从空位 ID 224 开始追加。
- 本计划落地后的当前总量：通用原型 56 个、独特奇观 136 座。
- 零采用原型共有 9 个：
  `giant_observatory`、`royal_granary_system`、`frontier_colonization_belt`、`coastal_beacon_network`、`war_college_system`、`great_clock_bell_system`、`world_embassy_quarter`、`law_code_stele_project`、`royal_mint_system`。
- 目标 13 座独特奇观的静态站点预检已按现有地图事实核对为 `PASS`。
- `audit_unique_wonder_site_requirements.py` 对 `has_river` / `is_adjacent_to_lake` 只能报 `UNKNOWN`，所以这类条件只能放在 `preference_script`，不能放成硬站点门槛。

## 目标收口

### 通用原型

1. `grand_garden_complex`
   - 定位：园林群，文化类，`pop_type: nobles`
   - `data/wonders.yaml`：ID 55，`size: medium`，`category: cultural_category`，`maintenance: tv_wonder_module_maintenance`
   - 基础国家效果：`cultural_tradition_modifier`、`monthly_towards_humanist`
   - 最终本地效果：`local_monthly_prosperity`、`local_migration_attraction`
   - 三个分支：皇家苑囿、文人山水园、植物交流园
   - 分支落点：`skill_of_new_artists`、`local_cultural_tradition`、`cultural_tradition` + `site_prosperity`
   - 选址规则：`trigger_script: NOT = { location_rank ?= location_rank:rural_settlement }`
   - 选址偏好：城市/大都会、发展度、水道/湖泊/港口加成只写在 `preference_script`，不要进硬门槛

2. `state_examination_complex`
   - 定位：考试院，政府类，`pop_type: burghers`
   - `data/wonders.yaml`：ID 56，`size: medium`，`category: government_category`，`maintenance: tv_wonder_module_maintenance`
   - 基础国家效果：`country_cabinet_efficiency`、`global_pop_promotion_speed`、`monthly_towards_jurisprudence`
   - 最终本地效果：`local_max_literacy`、`local_pop_promotion_speed_modifier`
   - 三个分支：经义取士、开放贡举、经世致用
   - 分支落点：`country_cabinet_efficiency`、`local_max_literacy`、`government_power`
   - 硬门槛只保留“非乡村”；首都/城市/大都会/识字率/发展度写入偏好

### 13 座独特奇观

| ID | 名称 | key | 原型 | location | 初始等级 |
|---:|---|---|---|---|---:|
| 224 | 苏州古典园林 | `unique_suzhou_classical_gardens` | 园林群 | `wuxian` | 1 |
| 225 | 芬恩花园 | `unique_fin_garden` | 园林群 | `kashan` | 0 |
| 226 | 江南贡院 | `unique_jiangnan_examination_hall` | 考试院 | `shangyuan` | 1 |
| 227 | 升龙文庙国子监 | `unique_thang_long_temple_of_literature` | 考试院 | `thang_long` | 1 |
| 228 | 马拉盖天文台 | `unique_maragheh_observatory` | `giant_observatory` | `maragheh` | 1 |
| 229 | 西安钟鼓楼 | `unique_xian_bell_and_drum_towers` | `great_clock_bell_system` | `jingzhao` | 0 |
| 230 | 贝希斯敦铭文 | `unique_behistun_inscription` | `law_code_stele_project` | `bisotun` | 1 |
| 231 | 北京皇家粮仓群 | `unique_beijing_imperial_granaries` | `royal_granary_system` | `dadu` | 0 |
| 232 | 布尔萨皇家铸币所 | `unique_bursa_imperial_mint` | `royal_mint_system` | `bursa` | 1 |
| 233 | 恩德伦宫廷学校 | `unique_enderun_palace_school` | `war_college_system` | `constantinople` | 0 |
| 234 | 阿瑜陀耶外国使馆区 | `unique_ayutthaya_foreign_quarters` | `world_embassy_quarter` | `ayodhya` | 0 |
| 235 | 云南卫所屯田带 | `unique_yunnan_weisuo_colonies` | `frontier_colonization_belt` | `songming` | 0 |
| 236 | 舟山烽火台网 | `unique_zhoushan_beacon_network` | `coastal_beacon_network` | `dinghai` | 0 |

## 实施顺序

### 1. 先补通用原型

需要同步改这些源数据：

- `data/wonders.yaml`
- `data/wonder_base_modifiers.yaml`
- `data/wonder_final_buildings.yaml`
- `data/wonder_generic_rituals.yaml`
- `data/wonder_site_rules.yaml`
- `data/wonder_design_notes.yaml`
- `data/wonder_image_prompts.yaml`
- `data/wonder_localization.yaml`

### 2. 再补 13 座独特奇观

需要同步改这些源数据：

- `data/unique_wonders.yaml`
- `data/unique_wonder_ritual_designs.yaml`
- `data/unique_wonder_ritual_designs_zh.yaml`
- `data/unique_wonder_ritual_prompts.yaml`
- `data/wonder_localization.yaml`

统一约束：

- `base_effect_multiplier: 2`
- 单一最终建筑：`1: tv_wonder_<unique_key>_inaugurated`，保留 `unique_` 前缀
- `ritual.mode: immediate`
- `listeners: [monthly]`
- `runtime_variables: []`
- `country_modifier: {}`
- `ceremony` 保持 8 个阶段
- 不引入 bespoke ritual、专用 GUI 或新 schema

建议先按这个壳复制，逐项替换 `key` / 文案 / 阶段内容：

```yaml
ritual:
  key: <short_theme_key>
  mode: immediate
  cost_type: prestige
  listeners:
  - monthly
  runtime_variables: []
  country_modifier: {}
  reward: []
  confirmation_trigger_script: ''
  start_effect_script: ''
  snapshot_effect_script: ''
  progress_effect_script: tv_wonder_ceremony_monthly_tick_effect = yes
  completion_trigger_script: |-
    has_variable = tv_wonder_ceremony_stage
    var:tv_wonder_ceremony_stage ?= 8
  completion_effect_script: ''
  timed:
    years: 1
    burden_modifier: {}
    blessing_modifier: {}
  auxiliary_building:
    local_modifier: {}
    maintenance: null
    build_time: null
    construction_demand: null
    price: null
    attributes: {}
    max_levels: 6
ceremony:
 stages:
  - title_en: <stage 1 title>
    icon: <vanilla_font_icon>
    icon_rationale: "<why this icon fits>"
    title_zh: <阶段 1 标题>
    desc_en: <stage prose>
    desc_zh: <阶段描述>
    cost:
    - catalog: country_reward
      type: prestige
      value: -10
    option_pay_en: <accept text>
    option_pay_zh: <接受文本>
    option_decline_en: <decline text>
    option_decline_zh: <拒绝文本>
```

注意两层 cost 不要混淆：

- `ritual.cost_type` 只能是 `null`、`artwork`、`scaled_gold`、`prestige` 之一；这是启动壳字段。
- `ceremony.stages[].cost` 每阶段必须且只能 1 条，格式为 `{catalog, type, value}`。
- `catalog` 只能来自 `country_reward`、`local_reward`、`character_reward`、`country_modifier`、`local_modifier`。
- `value` 必须等于代码计算值：奇数阶段是 catalog 基础值的负数，偶数阶段是 2 倍负数；`country_reward.inflation` 方向相反，能不用就不用。
- 禁用作阶段 cost 的条目：`country_modifier.allow_open_sea_exploration`、`country_modifier.gender_equality`、`country_modifier.monthly_towards_axis`、`local_reward.laborers`。

可直接复用的阶段 cost 模板；表内用 `catalog.type` 速记，写 YAML 时仍拆成 `catalog` / `type` 两个字段：

| 用途 | 奇数阶段示例 | 偶数阶段示例 |
|---|---|---|
| 国力/政治成本 | `country_reward.prestige = -10`、`country_reward.government_power = -5` | `country_reward.prestige = -20`、`country_reward.government_power = -10` |
| 人力/阶层成本 | `country_reward.manpower = -50`、`country_reward.burghers_satisfaction = -0.1` | `country_reward.manpower = -100`、`country_reward.burghers_satisfaction = -0.2` |
| 本地建设成本 | `local_reward.development = -0.25`、`local_reward.prosperity = -0.2` | `local_reward.development = -0.5`、`local_reward.prosperity = -0.4` |
| 角色/专家成本 | `character_reward.adm = -3`、`character_reward.dip = -3`、`character_reward.mil = -3`、`character_reward.artist_skill = -0.05` | `character_reward.adm = -6`、`character_reward.dip = -6`、`character_reward.mil = -6`、`character_reward.artist_skill = -0.1` |
| 持续修正成本 | `country_modifier.country_cabinet_efficiency = -0.1`、`local_modifier.local_monthly_prosperity = -0.001` | `country_modifier.country_cabinet_efficiency = -0.2`、`local_modifier.local_monthly_prosperity = -0.002` |

13 座独特奇观的 ceremony 题材分工：

| key | 8 阶段主题建议 | cost 池建议 |
|---|---|---|
| `unique_suzhou_classical_gardens` | 买地、理水、叠山、营亭、植栽、题咏、雅集、名园落成 | `character_reward.artist_skill`、`country_reward.nobles_satisfaction`、`local_reward.prosperity`、`local_modifier.local_monthly_prosperity` |
| `unique_fin_garden` | 水源、渠道、墙院、树荫、浴池、凉亭、朝觐接待、花园落成 | `country_reward.scaled_gold`、`local_reward.development`、`local_reward.prosperity`、`local_modifier.local_migration_attraction` |
| `unique_jiangnan_examination_hall` | 贡院令、号舍排布、试卷保密、考官入闱、放榜、阅卷争议、士子秩序、贡院落成 | `character_reward.adm`、`country_reward.burghers_satisfaction`、`local_modifier.local_max_literacy`、`country_modifier.country_cabinet_efficiency` |
| `unique_thang_long_temple_of_literature` | 祭孔、国子监扩建、碑刻、讲席、试场、儒臣议礼、生员登记、文庙落成 | `character_reward.adm`、`character_reward.dip`、`country_reward.clergy_satisfaction`、`local_modifier.local_max_literacy` |
| `unique_maragheh_observatory` | 招募学者、铸造仪器、校准星表、建观测台、整理书库、赞助争论、呈递历法、天文台落成 | `country_reward.research_progress`、`character_reward.adm`、`character_reward.artist_skill`、`local_modifier.local_max_literacy` |
| `unique_xian_bell_and_drum_towers` | 定鼓令、铸钟、建楼、校时、夜禁、街市报时、城门联动、钟鼓楼落成 | `country_reward.prestige`、`country_reward.government_power`、`local_reward.development`、`local_modifier.local_monthly_development_modifier` |
| `unique_behistun_inscription` | 清理崖壁、拓印铭文、译读旧王诏、道路护卫、书记校订、王权宣示、学者传播、铭文落成 | `country_reward.prestige`、`character_reward.dip`、`country_reward.government_power`、`local_modifier.local_cultural_tradition` |
| `unique_beijing_imperial_granaries` | 仓址、漕粮账册、仓廒修筑、粮船交割、防火防鼠、赈济规程、京师储备、粮仓落成 | `country_reward.scaled_gold`、`country_reward.manpower`、`country_reward.peasants_satisfaction`、`country_modifier.global_food_capacity_modifier` |
| `unique_bursa_imperial_mint` | 铸币令、银铜供给、模具、钱样验收、税吏审计、商人兑换、铸币争议、铸币所落成 | `country_reward.scaled_gold`、`country_reward.burghers_satisfaction`、`country_reward.government_power`、`country_modifier.minting_income_factor` |
| `unique_enderun_palace_school` | 选拔侍从、宫廷课程、礼仪训练、军政演练、师傅任命、晋升考试、派任文武、学校落成 | `character_reward.adm`、`character_reward.dip`、`character_reward.mil`、`country_reward.nobles_satisfaction` |
| `unique_ayutthaya_foreign_quarters` | 划定坊区、仓栈、译员、商约、宗教争议、治安巡逻、使节宴会、使馆区落成 | `character_reward.dip`、`country_reward.burghers_satisfaction`、`country_modifier.diplomatic_reputation`、`country_modifier.global_merchant_power` |
| `unique_yunnan_weisuo_colonies` | 勘界、屯军、垦田、驿路、粮册、土司协商、边防整编、屯田带落成 | `country_reward.manpower`、`character_reward.mil`、`local_reward.development`、`local_modifier.local_migration_attraction` |
| `unique_zhoushan_beacon_network` | 选岛、修烽台、备柴薪、哨兵轮值、海盗警报、港口传讯、舰队联动、烽火网落成 | `country_reward.sailors`、`country_reward.manpower`、`local_modifier.local_maritime_presence`、`country_reward.navy_tradition` |

### 3. 生成链路

- 统一使用解释器：`C:\Users\Hades\anaconda3\envs\eu5\python.exe`
- 先更新设计源，再跑 `scripts_engineering_department/gen_unique_wonder_ritual_specs.py --preserve-existing`
- 不手改 `data/unique_wonder_ritual_specs.yaml`
- 奇观主图只对这 15 个 key 开批次：2 个通用原型 + 13 座独特奇观
- 最终建筑 Icon 需要补齐 19 个 DDS：2 个通用原型各 3 个分支，共 6 个；13 座独特奇观各 1 个
- 建筑 Icon prompt 写入 `generate_dds_icon_config.json` 的 `wonder_building_icons.overrides`
- 生成完要恢复 `scripts_engineering_department/generate_wonder_image_config.json` 的选择配置，别把仓库默认选择留成窄批次

命令顺序：

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\gen_unique_wonder_ritual_specs.py --preserve-existing
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\in_game\common\building_types\gen_tv_wonder_module_buildings.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\in_game\common\building_types\gen_tv_engineering_department_wonder_mechanics_buildings.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\in_game\common\static_modifiers\gen_tv_engineering_department_wonder_mechanics_modifiers.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\in_game\common\generic_actions\gen_tv_engineering_department_wonder_mechanics_actions.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\in_game\common\scripted_triggers\gen_tv_engineering_department_wonder_mechanics_triggers.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\in_game\common\scripted_effects\gen_tv_wonder_module_effects.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\in_game\common\scripted_effects\gen_tv_engineering_department_wonder_mechanics_effects.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\in_game\common\scripted_effects\gen_tv_wonder_ritual_effects.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\main_menu\common\game_concepts\gen_tv_engineering_department_wonder_mechanics_concepts.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\main_menu\localization\english\gen_tv_engineering_department_wonder_mechanics_l_english.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\main_menu\localization\simp_chinese\gen_tv_engineering_department_wonder_mechanics_l_simp_chinese.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\in_game\gui\panels\organization\gen_tv_engineering_department_wonder_mechanics_gui.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\in_game\gui\panels\organization\merge_tv_engineering_department_wonder_mechanics_gui.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\in_game\common\customizable_localization\gen_tv_wonder_ceremony_options.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\main_menu\common\static_modifiers\gen_tv_wonder_ceremony_cost_country_modifiers.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\main_menu\common\static_modifiers\gen_tv_wonder_ceremony_cost_local_modifiers.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\in_game\common\scripted_effects\gen_tv_wonder_ceremony_effects.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\in_game\events\gen_tv_wonder_ceremony_events.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\main_menu\localization\english\gen_tv_wonder_ceremony_l_english.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\main_menu\localization\simp_chinese\gen_tv_wonder_ceremony_l_simp_chinese.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\in_game\gui\panels\organization\gen_tv_wonder_ceremony_cards_gui.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\in_game\gui\panels\organization\merge_tv_wonder_ceremony_cards_gui.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\in_game\gui\gen_location_window.py
```

奇观主图流程：

1. 通用 prompt 写 `data/wonder_image_prompts.yaml`，独特 prompt 写 `data/unique_wonders.yaml` 的 `prompt`。
2. 临时把 `scripts_engineering_department/generate_wonder_image_config.json` 的 `selection.only_keys` 改成 15 个 key，`include_generic/include_unique` 保持 `true`，`overwrite` 默认 `false`。
3. 执行 `C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\generate_wonder_image.py`。
4. 如需人工裁切，运行 `C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\wonder_image_cropper.py`；确认后用 `--apply` 写 DDS 裁切结果。
5. 恢复 `selection.only_keys: []`，避免后续编辑器默认只处理亚洲区批次。

最终建筑 Icon 流程：

1. 为 6 个通用分支建筑和 13 个独特奇观落成建筑，在 `generate_dds_icon_config.json` 的 `wonder_building_icons.overrides` 中分别写入 `icon_prompt`。
2. 先执行 `C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\generate_dds_icon.py --target wonder_building_icons --dry-run`，检查最终拼接 prompt、参考图和请求参数，不调用图片 API。
3. 再执行 `C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\generate_dds_icon.py --target wonder_building_icons`，生成 PNG 和 `src_engineering_department/main_menu/gfx/interface/icons/buildings/*.dds`。
4. 保持 `output.overwrite: false`；生成器会跳过已有建筑 Icon，只处理本批次缺失的 19 个 DDS。

### 4. 测试与验证

落地前预检：

- 检查新 ID 区间仍空闲：通用 `55-56`，独特 `224-236`。
- 先单独跑站点审计，确认新增 13 座没有 `FAIL`；如果出现 `UNKNOWN`，优先检查是否把水文或宗教条件放进了硬 `trigger_script`。
- 检查 9 个零采用原型在新增独特奇观后 adoption count 都至少为 1。

落地后命令：

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\audit_unique_wonder_rituals.py --fail-on-coverage-debt
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\audit_unique_wonder_site_requirements.py --fail-on-fail
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\test_wonder_mechanics_rules.py
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\validate.py --changed --fix --ai-report
```

## 测试补强点

- 已落地于 `scripts_engineering_department/test_wonder_mechanics_rules.py` 的
  `validate_asia_wonder_expansion_coverage`：
  - 断言通用原型总数为 56（含 ID 55、56）。
  - 断言独特奇观总数为 136（含 ID 224–236）。
  - 断言 9 个零采用原型全部至少被采用 1 次。
  - 断言 13 个新独特奇观都通过站点审计。
- 断言所有新独特奇观都是 8 阶段、倍率 2、共享 immediate ceremony。
- 断言 ID、建筑 key、仪式 key 不碰撞。

## 交付标准

- 没有新增零采用原型。
- 没有新增 schema。
- 没有新增 bespoke ritual 后端或专用 GUI。
- 生成物只来自现有生成器链，不直接编辑生成产物。
- 现有工作树里的其他改动保持原样，不回滚不相干内容。
