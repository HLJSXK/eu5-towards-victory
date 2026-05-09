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

The **Diplomatic Victory** path (外交胜利) is fully implemented: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = `tv_diplomatic_victory_points` accumulated permanently via `on_royal_marriage` (+3 DVP per party) and `on_winning_war` (+5 DVP to winner); thresholds at 50 / 120 / 220 / 380 / 580 (provisional, calibrate after playtesting). **Diplomatic Alliance IO** (`tv_diplomatic_alliance`): custom `organization_panel` with HRE-style header (tier piechart at 220,60; cohesion at 294,60; leader country flag). IO native `variables` block manages `tv_alliance_tier` (max 15, incremented by law reforms) and `tv_alliance_cohesion` (max 100, monthly_change driven by base +0.1 and leader's diplomatic_reputation × 0.05). Parliament tab uses `tv_alliance_assembly` parliament type (`uses_parliament_for_law_votes = yes`), routing the existing 5-law system through the HRE-style voting/bribery interface.

The **Cultural Victory** path (文化胜利) is fully implemented with an Arts Exhibition layer: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = `tv_cultural_influence_points` (CIP) accumulated via `on_work_of_art_created` (+10 CIP, scope `root.owner`) and `monthly_country_pulse` (+1 CIP per month); thresholds at 50 / 120 / 220 / 380 / 580. M2–M5 also require `tv_arts_intl_influence` ≥ 25 / 50 / 75 / 100 respectively. **Arts Exhibition IO** (`tv_arts_exhibition`): countries join automatically at M1. Per-country `tv_arts_intl_influence` (International Influence) decays −0.05/month. Three generic actions: "Send Artist Abroad" (200 ducats, 3-step selection: artist → country → location; 1–10 year tour with `yearly_country_pulse` timer and `on_character_death` hook), "Host Domestic Exhibition" (1000 ducats, +0.1 per owned artwork), and "Appoint Chief Artist" (free; designates one court artist as Chief Artist). **Chief Artist** (`tv_chief_artist` country variable): the appointed artist passively adds `artist_skill × 0.002` International Influence per month (max +0.2/month at skill 1.0); bonus stored in `tv_chief_artist_monthly_bonus` for GUI display. Character carries `tv_is_chief_artist` and `tv_chief_artist_country` variables; `on_character_death` hook clears the country slot automatically. The Arts Exhibition panel shows a portrait slot at the top: empty slot is a clickable button that opens the appointment action; filled slot shows the character portrait via `character_frame_small` with character name and monthly bonus. Touring artists generate monthly events (~8% per artist per month, skill-weighted): unremarkable (+0.1), great success (+0.5), terrible (−0.1), artist hired (+1.0 permanently), artistic inspiration (+10% artist_skill_level_gain for 10 years). Character modifier: `tv_artistic_inspiration_modifier`.

The **Scientific Victory** path (科技胜利) is fully implemented with a unique building gate: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = `num_of_advances_researched` (snapshot taken monthly by tv_update_science_score_effect); thresholds at 100 / 150 / 200 / 300 / 400 (provisional, calibrate after playtesting). Rewards: M1 research speed, M2 institution spread/discipline, M3 institution spread/pop growth, M4 institution embrace cost/production, M5 production/discipline. **Unique mechanic:** Each milestone only fires after the corresponding **Academy of Sciences** building phase is manually constructed in the capital. The building chain (Phases I–V) is visible from game start; each phase requires the previous phase plus the corresponding score threshold (`tv_academy_of_sciences_level` variable). Construction conditions use `custom_tooltip` (score variable is not auto-parseable).

The mod is additive-only and uses the `tv_` namespace prefix throughout.

## Core Features

1. **6 Victory Situations** — One situation (`tv_victory_situation`) displays all 6 victory paths in a single panel with a flavor text introduction (Section 1), per-path progress bars and milestone circles (Section 2), and a global leaderboard (Section 3).
2. **Milestone Events** — Popup country events per milestone. All 30 events implemented across 6 paths: Conquest (`tv.conquest.1`–`5`), Prosperity (`tv.prosperity.1`–`5`), Trade (`tv.trade.1`–`5`), Diplomatic (`tv.diplomatic.1`–`5`), Cultural (`tv.cultural.1`–`5`), and Scientific (`tv.science.1`–`5`).
3. **Permanent Rewards** — All 30 milestone rewards are permanent static modifiers (`days = -1`); no time-limited buffs. All 6 paths fully implemented.
4. **Diplomatic Victory Points** (`tv_diplomatic_victory_points`) — Permanently accumulated via `on_royal_marriage` (+3 DVP each party) and `on_winning_war` (+5 DVP to winner).
5. **Cultural Influence Points** (`tv_cultural_influence_points`) — Accumulated via `on_work_of_art_created` (+10 CIP to `root.owner`) and `monthly_country_pulse` (+1 CIP/month).
6. **Scientific Technology Score** (`tv_science_score`) — Monthly snapshot of `num_of_advances_researched`; thresholds 100 / 150 / 200 / 300 / 400.
7. **Academy of Sciences Building Chain** — Five capital buildings (`tv_academy_of_sciences_1`–`5`) gate Scientific Victory milestones. Each requires the previous phase built and the corresponding score threshold; `on_built` immediately triggers `tv_check_science_milestones_effect`. Building category: `cultural_category`; visible in all capitals from game start.
8. **Global Victory Leaderboard** — Monthly ranking of the top 5 countries by their best single-path progress (0–100 bar value). Per-country: `tv_best_path` (0–5), `tv_best_progress_pct`, `tv_best_milestone`, `tv_best_score` computed via `tv_update_best_path_effect` in `monthly_country_pulse`. Situation stores rank-1..5 country references (`tv_rank_1_country`–`tv_rank_5_country`) via `ordered_in_global_list` cascading-exclusion pattern. Displayed in Section 3 with flag, country name, leading-path circle icon, milestone count, and score text.

## Directory Structure

```
src/
├── .metadata/metadata.json                mod ID, version, target game version
├── in_game/
│   ├── common/
│   │   ├── situations/                    towards_victory_situations.txt  [GENERATED]
│   │   ├── scripted_triggers/             towards_victory_triggers.txt  [GENERATED]
│   │   ├── scripted_effects/              towards_victory_effects.txt  [GENERATED]
│   │   │                                  towards_victory_leaderboard.txt  [MANUAL — leaderboard effects]
│   │   ├── static_modifiers/              towards_victory_modifiers.txt  [GENERATED]
│   │   ├── building_types/                towards_victory_buildings.txt (Academy of Sciences chain)
│   │   ├── generic_actions/               tv_arts_exhibition_actions.txt  [MANUAL]
│   │   │                                  tv_chief_artist_actions.txt  [MANUAL — Appoint Chief Artist action]
│   │   ├── international_organizations/   tv_diplomatic_alliance.txt  [MANUAL]
│   │   │                                  tv_arts_exhibition.txt  [MANUAL]
│   │   ├── parliament_types/              tv_alliance_parliament.txt  [MANUAL — tv_alliance_assembly IO parliament type]
│   │   └── on_action/                     towards_victory_yearly.txt  [GENERATED]
│   │                                      towards_victory_leaderboard.txt  [MANUAL — monthly_country_pulse hooks]
│   ├── events/                            towards_victory_{conquest,prosperity,trade,diplomatic,cultural,science}_events.txt (one namespace per category — EU5 event IDs must be `<ns>.<int>` with exactly one dot)
│   └── gui/
│       ├── panels/situation/              tv_victory_situation.gui  [MANUAL]
│       └── panels/organization/           tv_diplomatic_alliance.gui  [MANUAL — custom HRE-style IO panel]
│                                          tv_arts_exhibition.gui  [MANUAL — Arts Exhibition IO panel with Chief Artist slot]
└── main_menu/localization/
    ├── english/                           towards_victory_l_english.yml  [GENERATED]
    │                                      towards_victory_leaderboard_l_english.yml  [MANUAL]
    │                                      tv_diplomatic_alliance_l_english.yml  [MANUAL]
    └── simp_chinese/                      towards_victory_l_simp_chinese.yml  [GENERATED]
                                           towards_victory_leaderboard_l_simp_chinese.yml  [MANUAL]
                                           tv_diplomatic_alliance_l_simp_chinese.yml  [MANUAL]
```

## Script Reference

| Script | Input(s) | Output(s) | When to run |
|---|---|---|---|
| `scripts/validate.py --changed` | src/ mod files | Console report (exit 0/1) | Before launching game |
| `scripts/gen_brief.py` | anti_patterns.yaml + valid_enums.yaml + PROJECT_OVERVIEW.md | docs/knowledge/BRIEF.md | After editing any knowledge YAML |
| `scripts/gen_index.py` | reference_game_files + src/ | data/index/*.txt | Run by gen_brief.py automatically |
| `scripts/gen_scaffold.py --type X --name Y` | --type argument | Scaffold .txt/.yml file | When creating a new EU5 file |
