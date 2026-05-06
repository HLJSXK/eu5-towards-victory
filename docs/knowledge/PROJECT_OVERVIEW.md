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

The **Conquest Victory** path (征服胜利) is fully implemented: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = direct locations + 0.5 × subject-or-below locations; thresholds at 150 / 350 / 600 / 1100 / 1600.

The **Prosperity Victory** path (繁荣胜利) is fully implemented: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = total_population + Σ(prosperity per owned location); updated yearly via every_owned_location iteration; thresholds at 5,000 / 8,000 / 12,000 / 18,000 / 25,000 (provisional, calibrate after playtesting).

The **Trade Victory** path (贸易胜利) is fully implemented: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = monthly_trade_income (snapshot taken monthly by tv_update_trade_score_effect); thresholds at 10 / 25 / 50 / 80 / 120 (provisional, calibrate after playtesting).

The **Diplomatic Victory** path (外交胜利) is fully implemented: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = `tv_diplomatic_victory_points` accumulated permanently via `on_royal_marriage` (+3 DVP per party) and `on_winning_war` (+5 DVP to winner); thresholds at 50 / 120 / 220 / 380 / 580 (provisional, calibrate after playtesting).

The **Cultural Victory** path (文化胜利) is fully implemented: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = `tv_cultural_influence_points` (CIP) accumulated via `on_work_of_art_created` (+10 CIP, scope `root.owner`) and `monthly_country_pulse` (+1 CIP per month); thresholds at 50 / 120 / 220 / 380 / 580. Rewards: M1 artist skill/cost, M2 diplomacy/prestige, M3 prestige/tradition, M4 cultural influence/missionary, M5 cultural influence/prestige decay.

The **Scientific Victory** path (科技胜利) is fully implemented: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = `num_of_advances_researched` (snapshot taken monthly by tv_update_science_score_effect); thresholds at 30 / 80 / 140 / 200 / 270 (provisional, calibrate after playtesting). Rewards: M1 research speed, M2 institution spread/discipline, M3 institution spread/pop growth, M4 institution embrace cost/production, M5 production/discipline.

The mod is additive-only and uses the `tv_` namespace prefix throughout.

## Core Features

1. **6 Victory Situations** — One situation per victory type, showing milestone progress and current rewards earned.
2. **Milestone Events** — Popup country events per milestone. All 30 events implemented across 6 paths: Conquest (`tv.conquest.1`–`5`), Prosperity (`tv.prosperity.1`–`5`), Trade (`tv.trade.1`–`5`), Diplomatic (`tv.diplomatic.1`–`5`), Cultural (`tv.cultural.1`–`5`), and Scientific (`tv.science.1`–`5`).
3. **Permanent Rewards** — All 30 milestone rewards are permanent static modifiers (`days = -1`); no time-limited buffs. All 6 paths fully implemented.
4. **Diplomatic Victory Points** (`tv_diplomatic_victory_points`) — Permanently accumulated via `on_royal_marriage` (+3 DVP each party) and `on_winning_war` (+5 DVP to winner).
5. **Cultural Influence Points** (`tv_cultural_influence_points`) — Accumulated via `on_work_of_art_created` (+10 CIP to `root.owner`) and `monthly_country_pulse` (+1 CIP/month).
6. **Scientific Technology Score** (`tv_science_score`) — Monthly snapshot of `num_of_advances_researched`; thresholds 30 / 80 / 140 / 200 / 270.

## Directory Structure

```
src/
├── .metadata/metadata.json                mod ID, version, target game version
├── in_game/
│   ├── common/
│   │   ├── situations/                    towards_victory_situations.txt
│   │   ├── scripted_triggers/             towards_victory_triggers.txt
│   │   ├── scripted_effects/              towards_victory_effects.txt
│   │   ├── static_modifiers/              towards_victory_modifiers.txt
│   │   └── on_action/                     towards_victory_yearly.txt
│   ├── events/                            towards_victory_{conquest,prosperity,trade,diplomatic,cultural,science}_events.txt (one namespace per category — EU5 event IDs must be `<ns>.<int>` with exactly one dot)
│   └── gui/panels/situation/              towards_victory_situation.gui
└── main_menu/localization/
    ├── english/                           towards_victory_l_english.yml
    └── simp_chinese/                      towards_victory_l_simp_chinese.yml
```

## Script Reference

| Script | Input(s) | Output(s) | When to run |
|---|---|---|---|
| `scripts/validate.py --changed` | src/ mod files | Console report (exit 0/1) | Before launching game |
| `scripts/gen_brief.py` | anti_patterns.yaml + valid_enums.yaml + PROJECT_OVERVIEW.md | docs/knowledge/BRIEF.md | After editing any knowledge YAML |
| `scripts/gen_index.py` | reference_game_files + src/ | data/index/*.txt | Run by gen_brief.py automatically |
| `scripts/gen_scaffold.py --type X --name Y` | --type argument | Scaffold .txt/.yml file | When creating a new EU5 file |
