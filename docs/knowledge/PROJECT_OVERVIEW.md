# Towards Victory — Project Overview

## Mod Identity

- **Mod Name:** Towards Victory (胜利条件)
- **Mod ID:** `eu5mp.towards_victory`
- **Version:** 0.1.0
- **Target:** EU5 `1.*.*`
- **Status:** In Development — All 6 Victory paths fully implemented: Conquest, Prosperity, Trade, Diplomatic, Cultural, and Scientific
- **Language:** English + Simplified Chinese

## Summary

Towards Victory adds 6 generalized victory paths to EU5: Conquest, Prosperity, Trade, Diplomatic, Cultural, and Scientific. Each path has 5 milestone nodes that grant permanent buffs when reached. Progress is displayed via situation panels; milestones trigger popup events that notify the player and deliver the reward.

The **Conquest Victory** path (征服胜利) is fully implemented: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = direct locations + 0.5 × subject-or-below locations; thresholds at 150 / 300 / 500 / 1000 / 2000.

The **Prosperity Victory** path (繁荣胜利) is fully implemented: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = (total_population + Σdev + country_tax_base) × 100 / (N + 100) × (1 + stability/100) × (gov_power/100), where N = num_owned_locations and gov_power = legitimacy/republican_tradition/devotion/tribal_cohesion/horde_unity by government type. The N/(N+100) term provides diminishing returns on scale. Updated yearly; thresholds at 5,000 / 8,000 / 12,000 / 18,000 / 25,000 (provisional, calibrate after playtesting).

The **Trade Victory** path (贸易胜利) is fully implemented: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = monthly_trade_income (snapshot taken monthly by tv_update_trade_score_effect); thresholds at 100 / 200 / 400 / 1000 / 2000 (provisional, calibrate after playtesting).

The **Diplomatic Victory** path (外交胜利) is fully implemented: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = `tv_diplomatic_victory_points` accumulated permanently via `on_royal_marriage` (+3 DVP per party) and `on_winning_war` (+5 DVP to winner); thresholds at 50 / 120 / 220 / 380 / 580 (provisional, calibrate after playtesting). **Diplomatic Alliance IO** (`tv_diplomatic_alliance`): non-unique IO using the same character-leader-with-appointment pattern as the Arts Exhibition and Academy of Sciences IOs (`tv_diplomatic_alliance_leader_char` country variable; `leader_change_trigger_type = none`; leader titled Advocator). Unlike the other two IOs, this IO has a custom `organization_panel` with HRE-style header (tier piechart at 220,60; cohesion piechart at 294,60; leader country flag), a parliament tab (`tv_alliance_assembly` parliament type, `uses_parliament_for_law_votes = yes`) for the 5-law system, and two IO-native variables: `tv_alliance_tier` (max 15, incremented by law reforms) and `tv_alliance_cohesion` (max 100, `monthly_change` driven by base +0.1 and `leader_country.modifier:diplomatic_reputation × 0.05`).

The **Cultural Victory** path (文化胜利) is fully implemented with an Arts Exhibition layer: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = `tv_cultural_influence_points` (CIP) accumulated via `on_work_of_art_created` (+10 CIP, scope `root.owner`) and `monthly_country_pulse` (+1 CIP per month); thresholds at 50 / 120 / 220 / 380 / 580. M2–M5 also require `tv_arts_intl_influence` ≥ 25 / 50 / 75 / 100 respectively. **Arts Exhibition IO** (`tv_arts_exhibition`): non-unique IO; each country creates its own instance at M1 via `create_international_organization` with `set_leader_country = prev`. `tv_arts_intl_influence` (International Influence) is an **IO type variable** (`variables = { }` block) with `min = 0 / max = 100 / start = 0`, automatic `monthly_change` decay of −0.05/month (shown in the IO panel's standard `ios_information_header` piechart with `IOVariableTooltip` monthly breakdown). All effect sites modify it via `every_international_organizations_member_of = { limit = { international_organization_type = international_organization_type:tv_arts_exhibition } change_variable = { ... } }`. M2–M5 milestone triggers use `any_international_organizations_member_of = { ... var:tv_arts_intl_influence >= N }` from country scope. **IO leader = a court artist** (`leader_type = character`, manually appointed via Appoint/Remove/Change Leader actions in `tv_io_leader_actions.txt`; leader character stored on leader_country as `tv_arts_exhibition_leader_char`; IO `leader = { leader_country ?= { var:tv_arts_exhibition_leader_char ?= { add_to_list = leaders } } }` with `leader_change_trigger_type = none`). The appointed leader's `artist_skill × 0.002` is added to `tv_arts_intl_influence.monthly_change` (via `leader_country.var:tv_arts_exhibition_leader_char.artist_skill` chained access). Three further generic actions: "Send Artist Abroad" (200 ducats, 3-step selection: artist → country → location; 1–10 year tour with `yearly_country_pulse` timer and `on_character_death` hook), "Host Domestic Exhibition" (1000 ducats, +0.1 per owned artwork). The IO panel header shows the leader character automatically (standard vanilla character-leader IO header); no custom portrait slot is needed. Touring artists generate monthly events (~8% per artist per month, skill-weighted): unremarkable (+0.1), great success (+0.5), terrible (−0.1), artist hired (+1.0 permanently), artistic inspiration (+10% artist_skill_level_gain for 10 years). Character modifier: `tv_artistic_inspiration_modifier`. **Dispatch constraints (added):** Each dispatched artist reduces the home country's `num_possible_artists` cap by 1 via a pre-defined country modifier (`tv_touring_penalty_N`, where N = current dispatch count; managed by `tv_update_tour_capacity_effect`). The home country tracks the count in `tv_dispatched_artists_count` (initialized to 0 in IO `on_creation`, updated on dispatch/return/death). A marker variable `tv_has_visiting_artist` is set on the target country when an artist arrives and cleared when they return or die; Step 2 of the dispatch selection filters out countries that already carry this marker so at most one artist from any IO member can tour each country at a time. The IO panel displays the current dispatched count via a `TV_ARTS_DISPATCHED_COUNT_LABEL` / `GetValue|0` widget.

The **Scientific Victory** path (科技胜利) is fully implemented with a unique Academy of Sciences building gate: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = `num_of_advances_researched` (snapshot taken monthly by tv_update_science_score_effect); thresholds at 100 / 150 / 200 / 300 / 400 (provisional, calibrate after playtesting). Rewards: M1 research speed, M2 institution spread/discipline, M3 institution spread/pop growth, M4 institution embrace cost/production, M5 production/discipline. **Unique mechanic:** Each milestone only fires after the corresponding **Academy of Sciences** building phase is manually constructed in the capital. The building chain (Phases I–V) is visible from game start; each phase requires the previous phase plus the corresponding score threshold (`tv_academy_of_sciences_level` variable). Construction conditions use `custom_tooltip` (score variable is not auto-parseable). **Academy of Sciences IO** (`tv_academy_of_sciences`): non-unique IO created when Phase I building (`tv_academy_of_sciences_1`) is built — fires event `tv_academy.1` which sets country variable `tv_academy_io_member = 1` and calls `create_international_organization`. **IO leader = an appointed character** (Chief Scientist), set manually via Appoint/Remove/Change Leader actions in `tv_io_leader_actions.txt`; leader character stored on leader_country as `tv_academy_leader_char`; IO `leader = { leader_country ?= { var:tv_academy_leader_char ?= { add_to_list = leaders } } }` with `leader_change_trigger_type = none`. **Research Mechanism (frontier-tech shortcut):** Four sub-processes complete one full cycle, which auto-researches one chosen Frontier advance via `research_advance = advance_type:X` (these advances remain normally researchable via the vanilla research tab — the Research Mechanism is an *extra* unlock route, not a gate). Sub-process A (Interest Collection): monthly random event (`tv_research.1`, ~20% base chance) adds +1 to `tv_research_interest`; completes at 5. Sub-process B (Prerequisites, Phase 4 stub = `always`): auto-completes on first monthly tick in phase 1. Sub-process C (Literacy Foundation): **IO variable** `tv_research_c_progress` accumulates `average_country_literacy × 0.05` per month; completes at 100 (~40 months at 50% literacy). Sub-process D (Concentrated Research): **IO variable** `tv_research_d_progress` accumulates `appointed_leader.adm × 1.0` per month (via `leader_country.var:tv_academy_leader_char.adm`); completes at 100 (~17 months at adm=6). D halts when no leader appointed. Monthly gold cost during D: `(appointed_leader.dip + appointed_leader.mil) × −0.5`. **Target selection:** Player clicks "Request Research Topic" → strict-earliest-age random proposal (each candidate is excluded if `has_advance = vanilla_id` is true OR if any earlier-age Frontier advance is still unresearched) → event `tv_research.10` for confirmation; abandoned targets set 12-month cooldown. **10 Frontier advances:** 1=printing_press_advance(A3), 2=iron_working(A1), 3=anatomy_advance(A2), 4=gunpowder_advance(A2), 5=blast_furnace(A3), 6=scientific_experimentation(A4), 7=scientific_revolution_advance(A5), 8=manufactories_advance(A5), 9=industrialization_advance(A6), 10=vaccination_advance(A6). Each is listed in `data/locked_advances.yaml`; `tv_unlock_advance_<id>_effect` is generated by `scripts/gen_locked_advances.py` and called by `tv_research_concentrated_complete_effect` on cycle D completion. **Cycle phases:** 0=idle, 1=A/B/C running, 2=D concentrated research. State variables: `tv_research_phase`, `tv_research_target`, `tv_research_interest`, `tv_research_b_done`, `tv_research_selection_cd`; display vars: `tv_rm_subprocess_a/b/c`, `tv_rm_subprocess_d_ready`. IO panel (`tv_academy_of_sciences.gui`) shows target, CD, Chief Scientist name (from appointed character), subprocess A/B/C/D status, three research action buttons, and three leader-management action buttons. Victory situation panel Section 2 Academy sub-block shows the same subprocess status and target advance name.

The mod is additive-only and uses the `tv_` namespace prefix throughout.

## Core Features

1. **6 Victory Situations** — One situation (`tv_victory_situation`) displays all 6 victory paths in a single panel with a flavor text introduction (Section 1), per-path progress bars and milestone circles (Section 2), and a global leaderboard (Section 3).
2. **Milestone Events** — Popup country events per milestone. All 30 events implemented across 6 paths: Conquest (`tv.conquest.1`–`5`), Prosperity (`tv.prosperity.1`–`5`), Trade (`tv.trade.1`–`5`), Diplomatic (`tv.diplomatic.1`–`5`), Cultural (`tv.cultural.1`–`5`), and Scientific (`tv.science.1`–`5`).
3. **Permanent Rewards** — All 30 milestone rewards are permanent static modifiers (`days = -1`); no time-limited buffs. All 6 paths fully implemented.
4. **Diplomatic Victory Points** (`tv_diplomatic_victory_points`) — Permanently accumulated via `on_royal_marriage` (+3 DVP each party) and `on_winning_war` (+5 DVP to winner).
5. **Cultural Influence Points** (`tv_cultural_influence_points`) — Accumulated via `on_work_of_art_created` (+10 CIP to `root.owner`) and `monthly_country_pulse` (+1 CIP/month).
6. **Scientific Technology Score** (`tv_science_score`) — Monthly snapshot of `num_of_advances_researched`; thresholds 100 / 150 / 200 / 300 / 400.
7. **Academy of Sciences Building Chain** — Five capital buildings (`tv_academy_of_sciences_1`–`5`) gate Scientific Victory milestones. Each requires the previous phase built and the corresponding score threshold; `on_built` immediately triggers `tv_check_science_milestones_effect`. Building category: `cultural_category`; visible in all capitals from game start. Phase I `on_built` also fires event `tv_academy.1` which creates the **Academy of Sciences IO** (`tv_academy_of_sciences`), a non-unique character-leader IO with manual leader appointment. Membership flag: `tv_academy_io_member` (country variable set to 1 on join). IO leader (Chief Scientist) = appointed character stored on leader_country as `tv_academy_leader_char`; managed via the Appoint/Remove/Change Leader actions in `tv_io_leader_actions.txt`. `leader_change_trigger_type = none`; `international_organization_chooses_new_leader` is deliberately NOT called — it triggers the vanilla leader-election process, violating the no-elections design.
8. **Research Mechanism (Frontier-Tech Shortcut)** — Full four-subprocess cycle that auto-researches one of 10 Frontier advances via `research_advance` on cycle completion. The 10 advances remain normally researchable via the vanilla tech tree — the Research Mechanism is an *extra* unlock path, not a gate. Sub-process A: monthly random interest events (5 needed; event namespace `tv_research`). Sub-process B: passive prerequisite check (Phase 4 stub = `always`). Sub-process C: IO variable `tv_research_c_progress` auto-accumulates via `monthly_change`; completed by `monthly_effect`. Sub-process D: IO variable `tv_research_d_progress` auto-accumulates via the appointed leader's `adm`; costs gold monthly (leader's `dip + mil`); triggers unlock on completion. Three research generic actions: `tv_request_research_target`, `tv_abandon_research_target`, `tv_start_concentrated_research`. Lifecycle managed by scripted effects in `tv_research_subprocess_effects.txt`; conditions in `tv_research_subprocess_triggers.txt`. **10 Frontier advances:** 1=printing_press(A3), 2=iron_working(A1), 3=anatomy(A2), 4=gunpowder(A2), 5=blast_furnace(A3), 6=scientific_experimentation(A4), 7=scientific_revolution(A5), 8=manufactories(A5), 9=industrialization(A6), 10=vaccination(A6). Each is listed in `data/locked_advances.yaml` with `vanilla_advance_id` and `age` fields; the `tv_unlock_advance_<id>_effect` (set_variable + `research_advance = advance_type:<vanilla_id>`) is generated by `scripts/gen_locked_advances.py`. Target proposal uses strict-earliest-age priority: each candidate is excluded if `has_advance = vanilla_id` is true OR if any earlier-age Frontier advance is still unresearched.
9. **IO Leader Management** — Unified character-leader pattern across all three IOs (Arts Exhibition, Diplomatic Alliance, Academy of Sciences). Each IO uses `leader_type = character` + `leader_change_trigger_type = none` + `leader_change_method = none` + a `leader = { leader_country ?= { var:tv_<io>_leader_char ?= { add_to_list = leaders } } }` block. Nine generic actions (3 per IO × 3 IOs) in `tv_io_leader_actions.txt`: Appoint, Remove, Change. Each action sets or clears the country variable only — `international_organization_chooses_new_leader` is deliberately NOT called (it triggers the vanilla leader-election process, violating the no-elections design). All three IOs have `unique = no`; never use `international_organization:type_name` syntax for them — use `every_international_organizations_member_of = { limit = { international_organization_type = international_organization_type:<io_type> } ... }` instead. Arts Exhibition filters candidates by `is_artist = yes`; the other two IOs accept any non-ruler/heir/consort alive character.
8. **Global Victory Leaderboard** — Monthly ranking of the top 5 countries by their best single-path progress (0–100 bar value). Per-country: `tv_best_path` (0–5), `tv_best_progress_pct`, `tv_best_milestone`, `tv_best_score` computed via `tv_update_best_path_effect` in `monthly_country_pulse`. Situation stores rank-1..5 country references (`tv_rank_1_country`–`tv_rank_5_country`) via `ordered_in_global_list` cascading-exclusion pattern. Displayed in Section 3 with flag, country name, leading-path circle icon, milestone count, and score text.

## IO Architecture Design Decisions

The three TV IOs (`tv_arts_exhibition`, `tv_diplomatic_alliance`, `tv_academy_of_sciences`) share invariants that must never be broken.

### 1. leader_country = founding country, locked at creation

`on_creation = { set_leader_country = scope:actor }` runs once when the IO is created. `leader_country` is never reassigned afterward. It controls IO permissions, `is_leader_of_international_organization` trigger, and `leader_country.modifier:` chained access in `monthly_change` scripted values.

### 2. No elections — leader_change_trigger_type = none is mandatory

All three IO type definitions keep `leader_change_trigger_type = none` and `leader_change_method = none`. These prevent the engine from reassigning `leader_country` automatically. `international_organization_chooses_new_leader` is **globally banned** from all TV IO-related code — this effect triggers the vanilla election process. Any call to it violates the no-elections design and risks silently reassigning `leader_country` to a different country.

### 3. Great person characters are independent country variables, not the vanilla ruler

The character displayed in the IO header is stored as a country variable on the `leader_country`:
- Arts Exhibition: `tv_arts_exhibition_leader_char`
- Diplomatic Alliance: `tv_diplomatic_alliance_leader_char`
- Academy of Sciences: `tv_academy_leader_char`

These are set/cleared exclusively by the nine generic actions in `tv_io_leader_actions.txt`. The vanilla `leader_country.GetGovernment.GetRuler` and `appointed_leader.*` are different concepts and must not be used in TV IO calculations.

### 4. IO variable monthly_change uses chained character attribute access

All IO variable `monthly_change` scripted values that depend on the appointed great person must use `leader_country.var:tv_xxx_leader_char.attribute` chained access — never `appointed_leader.attribute`. Examples:
- CORRECT: `value = leader_country.var:tv_academy_leader_char.adm`
- FORBIDDEN: `value = appointed_leader.adm`

### 5. Header display uses blockoverride

All three IO panels use `blockoverride` on their header template to display the appointed character (read from the country variable via `GetPlayer.MakeScope.GetVariable('tv_xxx_leader_char').GetCharacter`). Never use the vanilla `GetLeaderCountry.GetGovernment.GetRulerOrRegent` accessor chain.

### 6. All three IOs have unique = no

Each country pursuing the relevant victory path creates its own independent IO instance. The `international_organization:type_name` scope link is **invalid** for non-unique types. Always use `every_international_organizations_member_of = { limit = { international_organization_type = international_organization_type:<io_type> } ... }`.

## Directory Structure

```
src/
├── .metadata/metadata.json                mod ID, version, target game version
├── in_game/
│   ├── common/
│   │   ├── situations/                    towards_victory_situations.txt  [GENERATED]
│   │   ├── scripted_triggers/             towards_victory_triggers.txt  [GENERATED]
│   │   │                                  tv_research_subprocess_triggers.txt  [MANUAL — Research Mechanism conditions + Frontier-tech availability gate]
│   │   ├── scripted_effects/              towards_victory_effects.txt  [GENERATED]
│   │   │                                  towards_victory_leaderboard.txt  [MANUAL — leaderboard effects]
│   │   │                                  tv_advance_unlock_effects.txt  [GENERATED — tv_unlock_advance_<id>_effect (set_variable + research_advance)]
│   │   │                                  tv_research_subprocess_effects.txt  [MANUAL — Research Mechanism lifecycle effects; strict-earliest-age target proposal]
│   │   ├── static_modifiers/              towards_victory_modifiers.txt  [GENERATED]
│   │   ├── building_types/                towards_victory_buildings.txt  [GENERATED — Academy of Sciences building chain tiers 1–5]
│   │   ├── generic_actions/               tv_arts_exhibition_actions.txt  [MANUAL — Send Artist Abroad / Host Domestic Exhibition]
│   │   │                                  tv_io_leader_actions.txt  [GENERATED — 9 IO leader Appoint/Remove/Change actions (3 per IO × 3 IOs)]
│   │   ├── laws/                          tv_alliance_laws.txt  [GENERATED — 5 law categories × 4 policy levels for the Diplomatic Alliance IO]
│   │   │                                  tv_research_actions.txt  [MANUAL — Research Mechanism IO panel actions]
│   │   ├── generic_action_ai_lists/       tv_arts_exhibition_list.txt  [MANUAL]
│   │   │                                  tv_diplomatic_alliance_list.txt  [MANUAL]
│   │   │                                  tv_research_actions_list.txt  [MANUAL]
│   │   ├── international_organizations/   tv_diplomatic_alliance.txt  [MANUAL — character leader via tv_diplomatic_alliance_leader_char]
│   │   │                                  tv_arts_exhibition.txt  [MANUAL — character leader (artist) via tv_arts_exhibition_leader_char]
│   │   │                                  tv_academy_of_sciences.txt  [MANUAL — character leader via tv_academy_leader_char; C/D IO variables; D uses leader.adm]
│   │   ├── parliament_types/              tv_alliance_parliament.txt  [MANUAL — tv_alliance_assembly IO parliament type]
│   │   └── on_action/                     towards_victory_yearly.txt  [GENERATED]
│   │                                      towards_victory_leaderboard.txt  [MANUAL — monthly_country_pulse hooks]
│   │                                      tv_research_on_action.txt  [MANUAL — B check, CD countdown, A random event]
│   ├── events/                            towards_victory_{conquest,prosperity,trade,diplomatic,cultural,science}_events.txt (one namespace per category — EU5 event IDs must be `<ns>.<int>` with exactly one dot)
│   │                                      tv_academy_join_events.txt  [MANUAL — namespace tv_academy; tv_academy.1 creates IO on Phase I built]
│   │                                      tv_research_events.txt  [MANUAL — namespace tv_research; events .1/.10/.11/.20/.30]
│   └── gui/
│       ├── panels/situation/              tv_victory_situation.gui  [MANUAL]
│       └── panels/organization/           tv_diplomatic_alliance.gui  [MANUAL — custom HRE-style IO panel; 3 leader-management buttons]
│                                          tv_arts_exhibition.gui  [MANUAL — 2 cultural action buttons + 3 leader-management buttons]
│                                          tv_academy_of_sciences.gui  [GENERATED — Research Mechanism IO panel; 3 research + 3 leader-management buttons]
└── main_menu/localization/
    ├── english/                           towards_victory_l_english.yml  [GENERATED]
    │                                      towards_victory_leaderboard_l_english.yml  [MANUAL]
    │                                      tv_diplomatic_alliance_l_english.yml  [MANUAL]
    │                                      tv_research_l_english.yml  [MANUAL — Research Mechanism keys + events]
    └── simp_chinese/                      towards_victory_l_simp_chinese.yml  [GENERATED]
                                           towards_victory_leaderboard_l_simp_chinese.yml  [MANUAL]
                                           tv_diplomatic_alliance_l_simp_chinese.yml  [MANUAL]
                                           tv_research_l_simp_chinese.yml  [MANUAL — Research Mechanism CN keys + events]
```

## Script Reference

| Script | Input(s) | Output(s) | When to run |
|---|---|---|---|
| `scripts/validate.py --changed` | src/ mod files + data/generated_files.yaml | Console report (exit 0/1) | Before launching game |
| `scripts/gen_brief.py` | anti_patterns.yaml + valid_enums.yaml + PROJECT_OVERVIEW.md | docs/knowledge/BRIEF.md | After editing any knowledge YAML |
| `scripts/gen_index.py` | reference_game_files + src/ | data/index/*.txt | Run by gen_brief.py automatically |
| `scripts/gen_scaffold.py --type X --name Y` | --type argument | Scaffold .txt/.yml file | When creating a new EU5 file |
| `scripts/gen_messagetypes.py` | reference_game_files vanilla messagetypes.txt + TV_ENTRIES block | src/main_menu/gui/messagetypes.txt | After adding a new generic action |
| `scripts/gen_victory.py` | data/victory_paths.yaml | 13 generated files (triggers, effects, modifiers, situations, yearly, 6× events, 2× loc) | After editing data/victory_paths.yaml |
| `scripts/in_game/common/generic_actions/gen_tv_io_leader_actions.py` | data/io_leaders.yaml | src/in_game/common/generic_actions/tv_io_leader_actions.txt | After adding/changing an IO or its leader actions |
| `scripts/in_game/common/building_types/gen_towards_victory_buildings.py` | data/academy_buildings.yaml | src/in_game/common/building_types/towards_victory_buildings.txt | After changing Academy of Sciences building tiers |
| `scripts/in_game/gui/panels/organization/gen_tv_academy_of_sciences_gui.py` | data/locked_advances.yaml | src/in_game/gui/panels/organization/tv_academy_of_sciences.gui | After adding/removing Frontier advance targets |
| `scripts/in_game/common/laws/gen_tv_alliance_laws.py` | data/alliance_laws.yaml | src/in_game/common/laws/tv_alliance_laws.txt | After editing Diplomatic Alliance law categories or policies |
