# Research Mechanism Design Specification

**Mod:** Towards Victory (胜利条件), date-based `YYMMDD` versions
**Last updated:** 2026-05-10  
**Status:** Design locked — ready for Phase 2 implementation

---

## Overview

The Research Mechanism is the unique gameplay system for the Scientific Victory path. To unlock a **Frontier Technology** Advance node (otherwise permanently locked), a country must complete one full Research Cycle consisting of four sub-processes: three parallel prerequisite stages (A, B, C) followed by one sequential stage (D). One complete cycle unlocks exactly one locked Advance. The mechanism is hosted inside the **Academy of Sciences**, a per-country non-unique International Organization created when Phase I of the Academy of Sciences building is constructed.

---

## 四个子流程规格

### Sub-process A — 兴趣积累 (Interest Collection)

| Property | Detail |
|---|---|
| Concept | Historically, major scientific discoveries were often driven by personal curiosity of nobles and patrons. This sub-process captures that randomness. |
| Trigger | Monthly random event |
| Probability | Base rate modified by number of noble/aristocratic courtiers and courtiers with scholar traits in the royal court |
| Player action | Confirm event → `tv_research_interest += 1` |
| Completion condition | `tv_research_interest >= 5` |
| State variable | `tv_research_interest` (0–5) |
| Failure / interrupt | None. Interest accumulates additively; no loss on interruption. |

**Event format:**  
A member of the court has demonstrated unusual interest in the research topic (e.g., "Lord [Name] has become fascinated with [related field]..."). Player options: "Encourage the inquiry" (confirm, +1 interest) or "Dismiss it" (no effect, event closes without progress).

---

### Sub-process B — 技术前置 (Technology Prerequisites)

| Property | Detail |
|---|---|
| Concept | Major discoveries require supporting technology and dedicated infrastructure — no steam engine without metallurgy and a foundry. |
| Trigger | Passively evaluated; satisfied when both conditions are simultaneously met |
| Condition 1 | A specific prerequisite Advance has been researched by the country |
| Condition 2 | A specific unique building has been constructed at a designated location |
| Per-target binding | YES. Each locked Frontier Technology Advance has its own `required_advance` and `required_building`. |
| Completion condition | Both conditions true simultaneously |
| State variable | `tv_research_b_done` (0/1) |
| Failure / interrupt | None. Once both conditions are met, B is permanently satisfied for this cycle. |

**Data schema (per locked advance entry):**
```yaml
required_advance: [advance_id]        # must be researched before B is satisfied
required_building: [building_id]      # must be constructed at required_location
required_building_location: capital   # or specific region/province
```

**Note:** Specific `required_advance` and `required_building` values are defined per locked advance and will be specified in Phase 5 when the advance list is finalized.

---

### Sub-process C — 识字基础 (Literacy Foundation)

| Property | Detail |
|---|---|
| Concept | Major scientific breakthroughs depend on a literate, educated population capable of engaging with the ideas. |
| Trigger | Passive monthly pulse (on `monthly_country_pulse` or equivalent) |
| Progress formula | `tv_research_c_progress += national_literacy_rate * [calibration_factor]` per month |
| Completion condition | `tv_research_c_progress >= 100` |
| State variable | `tv_research_c_progress` (0–100) |
| Failure / interrupt | None. Progress persists; does not decay. Resets only after full cycle completion. |

**Calibration note (to determine in Phase 2):** At 50% literacy, completion should take approximately 3–4 years. At 20% literacy, approximately 8–10 years. At 80% literacy, approximately 2 years.

---

### Sub-process D — 集中研究 (Concentrated Research)

| Property | Detail |
|---|---|
| Concept | The final push — the country's finest scientific mind dedicates sustained effort to the breakthrough. |
| Availability | Only accessible after A, B, and C are all complete |
| Trigger | Player clicks "开展集中研究" button in Academy IO panel |
| Progress formula | `tv_research_d_progress += chief_scientist.admin_skill * [calibration_factor]` per month |
| Monthly cost | `gold -= f(chief_scientist.diplomacy + chief_scientist.martial)` per month |
| Completion condition | `tv_research_d_progress >= 100` → fires unlock event |
| State variable | `tv_research_d_progress` (0–100) |
| Interrupt | Allowed. Player may stop D; progress is preserved. Monthly costs stop immediately. |
| Chief Scientist | The IO leader character. Admin skill drives speed; diplomacy + martial drive cost. |

**Chief Scientist mechanic:**  
The IO leader must be a character (requires Step 2/3 verification). The player can change the IO leader via a "Change Chief Scientist" button in the IO panel. Higher admin = faster research. Higher diplomacy + martial = more expensive research (represents political leverage and logistical overhead required for major expeditions/experiments).

---

## 目标革新选择机制 (Target Advance Selection)

The player cannot freely choose which Frontier Technology to research. Instead, the Academy proposes candidates based on the nation's current era:

1. Player clicks **"申请研究目标"** in IO panel (disabled if cooldown active or target already set)
2. Game evaluates all currently locked Frontier Technology advances
3. Finds the **lowest historical era** among them
4. **Randomly selects one** advance from that era's locked set
5. Country event fires: *"Your Academy of Sciences has proposed a new avenue of research: [Advance Name]. Do you authorize the investigation?"*
   - **Authorize** → `tv_research_target = [advance_id]`; cycle begins
   - **Veto** → no target set; `tv_research_selection_cd = 12` (12-month cooldown)
6. Player may **abandon** a selected target at any time → clears target and all A/B/C/D progress → applies 12-month cooldown

**Cooldown variable:** `tv_research_selection_cd` counts down monthly. Any selection action (request or abandon) resets it to 12.

---

## 状态机说明 (Research Cycle State Machine)

```
┌─────────────────────────────────────────────────────┐
│  [IDLE]  No target selected                         │
│  tv_research_phase = 0                              │
└─────────────────┬───────────────────────────────────┘
                  │ Player requests target (CD = 0)
                  ▼
┌─────────────────────────────────────────────────────┐
│  [SELECTION EVENT]                                  │
│  Semi-random advance chosen from lowest era         │
└──────────┬──────────────────────────┬───────────────┘
           │ Player confirms          │ Player vetoes
           ▼                          ▼
┌──────────────────────┐    ┌──────────────────────────┐
│  [A/B/C IN PROGRESS] │    │  [IDLE + 12-month CD]    │
│  tv_research_phase=1 │    └──────────────────────────┘
│  A, B, C run in      │
│  parallel, any order │
└──────────┬───────────┘
           │ All three complete
           │ (interest=5, b_done=1, c_progress=100)
           ▼
┌─────────────────────────────────────────────────────┐
│  [D AVAILABLE]                                      │
│  Button "Start Concentrated Research" enabled       │
└──────────┬──────────────────────────────────────────┘
           │ Player clicks button
           ▼
┌─────────────────────────────────────────────────────┐
│  [D IN PROGRESS]                                    │
│  tv_research_phase = 2                              │
│  Monthly: progress += f(admin); gold -= f(dip+mil)  │
└──────────┬──────────────────────────────────────────┘
           │ tv_research_d_progress >= 100
           ▼
┌─────────────────────────────────────────────────────┐
│  [UNLOCK EVENT]                                     │
│  tv_frontier_[advance_id]_unlocked = 1              │
│  All state variables reset to 0/unset               │
└──────────┬──────────────────────────────────────────┘
           │ Auto-reset complete
           ▼
         [IDLE]  ← ready for next cycle
```

**Abandon path:** From [A/B/C IN PROGRESS] or [D IN PROGRESS] → player abandons → all progress cleared → [IDLE + 12-month CD]

---

## 锁定革新清单 (Locked Frontier Technology Advances)

**Status: Deferred to Phase 5.**

Locked advances represent genuine historical turning points (e.g., printing press, steam engine). The full list with specific advance IDs, era assignments, and per-advance B prerequisites (`required_advance`, `required_building`) will be finalized in Phase 5.

**Design constraints:**
- Total count: fewer than 10 nodes
- Distribution: spread across multiple historical eras
- Each entry requires: `advance_id`, `display_name_en`, `display_name_zh`, `era`, `required_advance`, `required_building`, `required_building_location`

**Unlock flag pattern:**  
`tv_frontier_[advance_id]_unlocked` (country script variable; 0 = locked, 1 = unlocked)

**Advance locking implementation** (requires Step 2/3 verification before Phase 2):  
Use `potential`/`allowed` trigger block in advance definition, checking for the unlock variable.

---

## 状态变量完整列表 (State Variables)

All variables are country-scoped script variables. All prefixed `tv_`.

| Variable | Type | Range | Purpose |
|---|---|---|---|
| `tv_research_interest` | integer | 0–5 | Sub-process A progress |
| `tv_research_b_done` | integer | 0/1 | Sub-process B completion flag |
| `tv_research_c_progress` | float | 0–100 | Sub-process C progress bar |
| `tv_research_d_progress` | float | 0–100 | Sub-process D progress bar |
| `tv_research_target` | string/id | unset or advance_id | Current selected target advance |
| `tv_research_selection_cd` | integer | 0–12 | Months remaining on selection cooldown |
| `tv_research_phase` | integer | 0/1/2 | 0=idle, 1=A/B/C active, 2=D active |
| `tv_frontier_[id]_unlocked` | integer | 0/1 | Per-advance unlock flag (one per locked advance) |

---

## UI 功能性要求 (Phase 3 Acceptance Criteria)

The Academy IO panel must meet the following **functional** requirements by end of Phase 3. Visual polish is explicitly out of scope for Phase 3.

### Display (required)

- Current research target: advance name + era, or "未选择研究目标 / No target selected"
- Sub-process A: interest counter displayed as `[tv_research_interest] / 5`
- Sub-process B: two condition indicators — prerequisite advance (researched ✓/✗) and building (constructed ✓/✗)
- Sub-process C: progress bar showing `tv_research_c_progress` as percentage
- Sub-process D: progress bar showing `tv_research_d_progress` as percentage and monthly progress rate
- Chief Scientist section: character name, admin / diplomacy / martial skills
- Cooldown indicator: months remaining on `tv_research_selection_cd` (hidden if 0)

### Buttons (required, with correct disabled states)

| Button | Label | Enabled when | Effect |
|---|---|---|---|
| Request Target | 申请研究目标 | No target set AND `tv_research_selection_cd = 0` | Triggers semi-random selection event |
| Abandon Target | 放弃研究目标 | Target is set | Clears target + all progress + sets CD=12 |
| Start Concentrated Research | 开展集中研究 | A+B+C all complete AND D not started | Begins D (monthly pulse activates) |
| Change Chief Scientist | 更换首席科学家 | Always | Triggers leader-change event |

### Non-requirements for Phase 3

- Animated transitions or particle effects
- Tooltips on progress bars
- Historical flavor text for each advance in the panel
- Mobile/compact layout variants

---

## Pre-implementation Verification Checklist

Before writing any EU5 script in Phase 2, the following MUST be verified via Step 2 (reference_official_defines) or Step 3 (reference_game_files / reference_mods):

1. **Advance locking:** Does EU5 support a `potential`, `allowed`, or `visible` trigger block in advance definitions gated on country script variables?  
   → Check `reference_game_files/game/in_game/common/advances/`

2. **IO character leader:** Can an IO's `leader` field reference a character (rather than a country)?  
   → Check `reference_game_files/game/main_menu/common/international_organizations/`

3. **Noble-count event probability:** What is the correct `mean_time_to_happen` / `trigger` syntax for event probability modified by the number of courtiers with a specific noble rank?  
   → Check `reference_game_files/game/in_game/events/`

Verification output must follow the project's Declarative Verification Requirement format before any code is written.
