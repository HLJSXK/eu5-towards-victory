# EU5 IO Leader 逻辑技术文档

> 研究目的：厘清 `leader_type = character` 与 `leader_country` 的关系，解释为何两者可以同时存在。
> 参考来源：`reference_game_files/game/in_game/common/international_organizations/` + GUI 面板文件 + 本 mod 实现。

---

## 一、核心结论（先读这里）

**`leader_country` 和 `leader_type = character` 是完全独立的两个系统，不互斥。**

| 属性 | 作用层 | 含义 |
|---|---|---|
| `has_leader_country = yes` | **功能层** | IO 存在一个"领导国"，该国拥有功能性权力（投票、modifier 加成等） |
| `leader_type = character` | **显示层** | UI 面板显示一个角色肖像，而非国家旗帜 |
| `leader = { }` | **填充层** | 定义向"领导者列表"中添加哪些角色对象供 GUI 读取 |

原版 HRE、天主教会、日本幕府、高王权等所有主要 IO **同时拥有三者**。  
`leader_country` 提供功能控制，`leader_type = character` 决定 UI 显示模式，`leader = {}` 从 `leader_country` 的君主/摄政处提取具体角色。

---

## 二、各属性详解

### 2.1 `has_leader_country = yes / no`

声明该 IO 是否存在一个功能性"领导国"概念。

- 设为 `yes`：IO 有一个领导国；领导国可以发起投票、获得 `leader_modifier`、被 `is_leader_of_international_organization` 触发器识别
- 设为 `no`：IO 没有领导国概念（如 Coalition、Crusade 等）

```
# HRE — 有领导国
has_leader_country = yes
```

### 2.2 `leader_type`

控制 IO 面板 UI 中领导者区域的**显示模式**，与 `leader_country` 是否存在无关。

| 值 | 显示内容 |
|---|---|
| `character` | 角色肖像（全身或半身像，显示角色名、称号、技能） |
| `country` | 国家旗帜/徽章（显示国名、国家数据） |
| `none` | 不显示领导者区域 |

原版示例：
- `leader_type = character`：HRE（皇帝），天主教会（教皇），幕府（将军）
- `leader_type = country`：Coalition（联盟），Crusade（十字军），Italian League（意大利联盟）

### 2.3 `leader = { }` 块

这是**填充层**：它定义一段脚本，每当引擎需要刷新 IO 领导者列表时执行，向内部的 `leaders` 列表中添加角色对象。GUI 通过 `GetLeaderScopeObjectAtIndex('(int32)N').GetCharacter` 读取该列表。

**原版 HRE 写法**（从 `leader_country` 的君主处提取）：
```
leader = {
    leader_country ?= {
        if = {
            limit = { has_regent = yes  has_heir = yes }
            heir ?= { add_to_list = leaders }
        }
        else_if = {
            limit = { has_ruler = yes  ruler ?= { is_alive = yes } }
            ruler ?= { add_to_list = leaders }
        }
    }
}
```

**本 mod 写法**（从 `leader_country` 的自定义变量处提取）：
```
leader = {
    leader_country ?= {
        var:tv_arts_exhibition_leader_char ?= {
            add_to_list = leaders
        }
    }
}
```

关键差异：原版直接读 ruler/heir；mod 读一个存在 `leader_country` 上的 **country variable**，该变量指向手动指定的角色。

### 2.4 `leader_change_trigger_type`

控制何种游戏事件会**自动触发**领导者重选流程。

| 值 | 触发时机 |
|---|---|
| `rulerchange` | 领导国君主更换时（HRE 默认） |
| `none` | 永不自动触发（需手动调用 `international_organization_chooses_new_leader`） |

### 2.5 `leader_change_method`

控制自动重选时的**选举方式**。

| 值 | 方式 |
|---|---|
| `vote` | 议会投票（如 HRE 皇帝选举） |
| `none` | 无自动选举 |

本 mod 所有 IO 均使用 `leader_change_trigger_type = none` + `leader_change_method = none`，彻底禁用自动机制，改由玩家通过 generic actions 手动管理。

### 2.6 `disband_if_no_leader`

```
disband_if_no_leader = no   # HRE 和本 mod 均使用此设置
```

HRE 注释：`#can have no leader while there's a power battle to get enough votes`。  
本 mod：同样允许暂时没有指定角色（玩家可能尚未 Appoint）。

---

## 三、效果与触发器

### 3.1 `set_leader_country = <country_scope>`

将指定国家设为 IO 的 `leader_country`。

```
# 本 mod on_creation 模式：创建者自动成为领导国
on_creation = {
    if = {
        limit = { exists = scope:actor }
        set_leader_country = scope:actor
    }
}
```

- 一旦设置，该国获得领导国的所有功能权力
- `leader = {}` 块会以 `leader_country` 为起点导航到具体角色

### 3.2 `international_organization_chooses_new_leader`

官方说明（`readme.txt:172`）：**"organization chooses a new leader according to its own process"**

该效果按 IO 定义的 `leader_change_method` 流程**选出新的 leader_country**，而非仅刷新显示列表。

| `leader_change_method` | 实际行为 |
|---|---|
| `vote` | 触发选帝侯/选举流程，选举结束后改变 `leader_country`（HRE 选举即此路径） |
| 其他方法 | 按该方法的评分逻辑选出新领导国并调用 `set_leader_country` |
| `none` | 无选举流程；ref 中无直接说明，但对 `none` 方法而言推测退化为仅刷新 `leader = {}` 显示块而不改变 `leader_country` |

原版 ref 中的典型用法：
- `high_kingship_overthrow.txt:56`：确认当前 `leader_country = scope:loser` 后调用此效果，令高王权选出新领导国（明确是换 `leader_country`）
- `_hardcoded.txt:2896`：HRE 领导国君主死亡时调用，触发选帝侯选举，换领导国
- `war_of_religions.txt:595`：宗教战争情境结束时对 HRE 调用，重置领导国

**本 mod 的用法**：三组 IO leader actions（Appoint/Remove/Change）执行后均调用此效果。由于 mod 所有 IO 均设 `leader_change_method = none`，该效果在 mod 语境下不应改变 `leader_country`（on_creation 中由 `set_leader_country` 固定，永不更换）。其实际作用为通知引擎重新评估 `leader = {}` 块，使新设置的 country variable 反映到 leaders 列表及 GUI 显示中。

- 对于非 unique IO：`every_international_organizations_member_of = { limit = { type = ... } international_organization_chooses_new_leader = this }`
- 对于 unique IO（如 DA）：`international_organization:tv_diplomatic_alliance → international_organization_chooses_new_leader`

### 3.3 `international_organization_has_leader`（触发器）

检查 IO 当前是否有领导者（即 leaders 列表非空）。  
本 mod 用于 `leader = {}` 的 monthly_change 条件和 GUI 可见性判断。

### 3.4 `is_leader_of_international_organization`（触发器）

从国家作用域检查该国是否是某 IO 的领导国（`leader_country`）。  
这是**功能层**概念，与显示的角色无关。

---

## 四、原版 IO 分类总览

### 类型 A：既有 `leader_country` 又有 character leader（最常见）

| IO | 文件 | leader_change_trigger_type | leader = {} 来源 |
|---|---|---|---|
| HRE | hre.txt | rulerchange | leader_country 的 ruler/heir |
| Catholic Church | catholic_church.txt | rulerchange | leader_country 的 ruler |
| High Kingship | high_kingship.txt | rulerchange | leader_country 的 ruler |
| Japanese Shogunate | japanese_shogunate.txt | rulerchange | leader_country 的 ruler |
| Ilkhanate | ilkhanate.txt | rulerchange | leader_country 的 ruler |
| Middle Kingdom | middle_kingdom.txt | rulerchange | leader_country 的 ruler |

**共同规律**：`leader_country` 由游戏机制动态确定（投票/战争）；character 显示的就是该领导国的现任君主；两者自然绑定。

### 类型 B：仅有 character leader，无 `leader_country`

| IO | 文件 | 特点 |
|---|---|---|
| Union | union.txt | 显示两个君主（双人肖像标题） |
| Marriage Union | marriage_union.txt | 显示联姻双方 |

GUI 读取方式：`GetLeaderScopeObjectAtIndex('(int32)0').GetCharacter` 和 `GetLeaderScopeObjectAtIndex('(int32)1').GetCharacter`，直接从 leaders 列表按索引读取。

### 类型 C：本 mod 自定义模式（手动角色任命）

| IO | leader_country 来源 | character 来源 |
|---|---|---|
| tv_arts_exhibition | on_creation 设为创建者，永不改变 | leader_country 上的 `tv_arts_exhibition_leader_char` 变量 |
| tv_diplomatic_alliance | on_creation 设为创建者，永不改变 | leader_country 上的 `tv_diplomatic_alliance_leader_char` 变量 |
| tv_academy_of_sciences | on_creation 设为创建者，永不改变 | leader_country 上的 `tv_academy_leader_char` 变量 |

**本 mod 的创新点**：打破了"character 必须是 leader_country 的 ruler/heir"的假设。通过在 `leader = {}` 块里读取 country variable，可以将**任意在职角色**（廷臣、艺术家、学者）指定为 IO 的显示角色，而 leader_country 仍然是创建者国家。

---

## 五、GUI 显示层

### 5.1 `has_leader_country = yes` + `leader_type = character`（标准模式，如 HRE）

使用 `organization_panel_default_header`（`common_header.gui`）：
- `visible = "[InternationalOrganizationsView.GetInternationalOrganization.IsLeaderCountryInPlace]"`
- `datacontext = "[InternationalOrganizationsView.GetInternationalOrganization.GetLeaderCountry]"`
- 在 country 上下文中：`Country.GetGovernment.GetRulerOrRegent` → 显示领导国君主的肖像
- 同时显示：国家徽章、角色名、称号、技能

**注意**：标准 common_header 读的是 `GetLeaderCountry.GetGovernment.GetRulerOrRegent`，即领导国的现任君主，**不是** `leader = {}` 块填充的 leaders 列表。对于原版 IO 而言两者是同一人，但本 mod 中两者不同（`leader_country` 的 ruler ≠ 手动指定的角色）。

### 5.2 仅有 character leader 无 leader_country（Union 模式）

使用 `union_header.gui`（`two_characters_header_fancy`）：
- `GetLeaderScopeObjectAtIndex('(int32)0').GetCharacter` → 第一个角色
- `GetLeaderScopeObjectAtIndex('(int32)1').GetCharacter` → 第二个角色
- 直接从 `leader = {}` 块填充的 leaders 列表按索引读取

### 5.3 本 mod 的自定义 IO 面板

本 mod 的 IO GUI 文件（`tv_arts_exhibition.gui`、`tv_academy_of_sciences.gui`）使用：
- `IsLeaderCountryInPlace` 检查 leader_country 是否存在（已由 on_creation 设定，始终为 yes）
- 标准 country_header 通过 `GetLeaderCountry.GetGovernment.GetRuler` 自动显示领导国君主

---

## 六、完整数据流图

```
创建 IO
  └─ on_creation: set_leader_country = scope:actor
       └─ leader_country = [创建者国家]（永久不变）

玩家触发 "Appoint Leader" generic action
  └─ 玩家从候选列表选择角色
  └─ effect:
       set_variable = { name = tv_arts_exhibition_leader_char  value = scope:target }
       every_international_organizations_member_of = { ...
           international_organization_chooses_new_leader = this  ← 触发刷新
       }
           └─ 引擎重新执行 leader = {} 块：
                leader_country ?= {                  ← leader_country = 创建者国家 ✓
                    var:tv_arts_exhibition_leader_char ?= {   ← 读到新指定的角色 ✓
                        add_to_list = leaders         ← leaders 列表 = [该角色]
                    }
                }

monthly_change (IO 变量 tv_arts_intl_influence):
  if = {
      limit = { international_organization_has_leader = yes   ← leaders 列表非空？
                leader_country = { has_variable = tv_arts_exhibition_leader_char } }
      add = { value = leader_country.var:tv_arts_exhibition_leader_char.artist_skill
              multiply = 0.002 }                              ← 链式访问角色技能
  }

GUI 面板显示:
  IsLeaderCountryInPlace ← leader_country 存在？→ yes（始终存在）
  GetLeaderCountry → [创建者国家]
  Country.GetGovernment.GetRulerOrRegent → 显示创建者国家的 ruler 肖像
  （注：标准 header 显示的是 ruler，非手动指定的 artist）
```

---

## 七、FAQ

**Q：设置了 `leader_type = character`，但 IO 还有 `leader_country`，这是 bug 吗？**

A：不是 bug。这是正常的设计。`leader_country` 是功能性控制层，`leader_type` 是 UI 显示层，两者独立存在。原版 HRE、教皇等所有角色领导 IO 都同时拥有两者。

**Q：`leader_country` 会自动变化吗？**

A：原版 IO 中会（HRE 通过选举更换领导国）。本 mod 设置了 `leader_change_trigger_type = none`，因此 `leader_country` 始终是 on_creation 时通过 `set_leader_country` 设定的创建者国家，不会自动更换。

**Q：`international_organization_chooses_new_leader` 是在换 `leader_country` 吗？**

A：**是的，这是它的主要用途**——按 IO 的 `leader_change_method` 流程选出新 `leader_country`（ref：`readme.txt:172`、`high_kingship_overthrow.txt:56`、`_hardcoded.txt:2896`）。对于 `leader_change_method = vote` 的 IO（如 HRE），调用后触发选举并改变 `leader_country`。

本 mod 的 IO 设为 `leader_change_method = none`，没有选举流程，推测该效果在此情况下退化为仅刷新 `leader = {}` 显示块而不改变 `leader_country`。`leader_country` 由 on_creation 固定，不会被此效果意外替换。

**Q：手动指定的角色（如 artist）和 leader_country 之间的关系？**

A：被指定的角色仍然属于原来的国家（不会 move_country）。该角色的引用被存储为 leader_country 上的一个 country variable（`var:tv_arts_exhibition_leader_char`）。每次需要读取该角色时，通过 `leader_country.var:tv_arts_exhibition_leader_char` 链式访问。

**Q：为什么 mod 的 IO 不直接用原版的 ruler 作为 character，而要搞一套手动指定的系统？**

A：因为 mod 的领导者是特殊角色（艺术家、学者、外交官），不是该国的君主。设计上需要玩家从廷臣中选择一位具有特定技能的角色担任 IO 的代表，而不是默认使用君主。

---

## 八、关键文件位置

| 文件 | 说明 |
|---|---|
| `reference_game_files/game/in_game/common/international_organizations/hre.txt` | 最完整的 character+leader_country IO 原版示例 |
| `reference_game_files/game/in_game/common/international_organizations/catholic_church.txt` | 简洁的 character+leader_country 示例 |
| `reference_game_files/game/in_game/gui/panels/organization/common_header.gui` | 标准 IO header GUI（IsLeaderCountryInPlace / GetLeaderCountry） |
| `reference_game_files/game/in_game/gui/panels/organization/union_header.gui` | Union 双角色 header（GetLeaderScopeObjectAtIndex） |
| `src/in_game/common/international_organizations/tv_arts_exhibition.txt` | 本 mod 手动指定角色模式的参考实现 |
| `data/io_leaders.yaml` | 本 mod IO leader actions 的数据源 |
| `src/in_game/common/generic_actions/tv_io_leader_actions.txt` | 生成的 9 个 IO leader 管理 action |
