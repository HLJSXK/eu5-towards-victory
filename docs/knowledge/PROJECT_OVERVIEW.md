# Towards Victory — Project Overview

## Mod Identity

- **Mod Name:** Towards Victory (胜利条件)
- **Mod ID:** `eu5mp.towards_victory`
- **Version:** 0.1.0
- **Target:** EU5 `1.*.*`
- **Status:** In Development — Conquest, Prosperity, and Trade Victory paths fully implemented; other 3 paths are skeleton/stub
- **Language:** English + Simplified Chinese

## Summary

Towards Victory adds 6 generalized victory paths to EU5: Conquest, Prosperity, Trade, Diplomatic, Cultural, and Scientific. Each path has 5 milestone nodes that grant permanent buffs when reached. Progress is displayed via situation panels; milestones trigger popup events that notify the player and deliver the reward.

The **Conquest Victory** path (征服胜利) is fully implemented: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = direct locations + 0.5 × subject-or-below locations; thresholds at 150 / 350 / 600 / 1100 / 1600.

The **Prosperity Victory** path (繁荣胜利) is fully implemented: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = total_population + Σ(prosperity per owned location); updated yearly via every_owned_location iteration; thresholds at 5,000 / 8,000 / 12,000 / 18,000 / 25,000 (provisional, calibrate after playtesting).

The **Trade Victory** path (贸易胜利) is fully implemented: 5 triggers, 5 reward modifiers, 5 events, and localization in English and Simplified Chinese. Score = monthly_trade_income (snapshot taken monthly by tv_update_trade_score_effect); thresholds at 10 / 25 / 50 / 80 / 120 (provisional, calibrate after playtesting).

The other 3 paths (Diplomatic, Cultural, Scientific) remain as stubs.

The mod is additive-only and uses the `tv_` namespace prefix throughout.

## Core Features

1. **6 Victory Situations** — One situation per victory type, showing milestone progress and current rewards earned.
2. **Milestone Events** — Popup country events per milestone. **Conquest** (`tv.conquest.1`–`tv.conquest.5`), **Prosperity** (`tv.prosperity.1`–`tv.prosperity.5`), and **Trade** (`tv.trade.1`–`tv.trade.5`) fully implemented; other paths are stubs.
3. **Permanent Rewards** — All milestone rewards are permanent static modifiers (`days = -1`); no time-limited buffs. **Conquest** (`tv_conquest_m1_bonus`–`tv_conquest_m5_bonus`), **Prosperity** (`tv_prosperity_m1_bonus`–`tv_prosperity_m5_bonus`), and **Trade** (`tv_trade_m1_bonus`–`tv_trade_m5_bonus`) rewards implemented.
4. **Diplomatic Victory Points** (`tv_diplomatic_victory_points`) — Country variable accumulated via diplomacy-related on_actions.
5. **Cultural Influence Points** (`tv_cultural_influence_points`) — Country variable accumulated via artifact ownership and cultural spread.
6. **Scientific Technology Score** (`tv_science_score`) — Weighted technology count with Age 5 steam-era emphasis.

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
│   ├── events/                            towards_victory_events.txt
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
