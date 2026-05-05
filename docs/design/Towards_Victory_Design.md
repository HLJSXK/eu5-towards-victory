# Towards Victory — Design Philosophy

## 1. Problem Statement

EU5 is the most complex game in the Europa Universalis series. Unlike previous entries, EU5 deliberately omits any concept of "winning" — players are free to set their own goals and play however they like. While this open-ended design is true to the series' spirit, EU5's complexity makes it harder for players to maintain direction, especially in the mid-to-late game when the initial "catch up" phase is over and no new goals suggest themselves.

The absence of a structured progress system has led many players to call for a return to EU4's national mission tree system. However, per-nation mission trees require enormous development effort to give meaningful coverage across EU5's hundreds of playable nations.

**Towards Victory** offers a different solution: a small set of universal, high-level victory paths that any nation can pursue, providing clear goals and staged rewards without requiring per-nation content. Civilization VI's victory system is the primary design reference.

---

## 2. Design Principles

1. **Compatibility-first** — All content is purely additive. No vanilla files are modified or overridden. All scripted identifiers use the `tv_` namespace prefix.

2. **Agency preserved** — All 6 victory paths are simultaneously available to every nation. Players self-select by playing naturally. No gating, no forced choice.

3. **Graduated difficulty** — Milestones 1–3 form an accessible arc; a major power should need 10+ years of focused play per milestone. Milestone 3 (Short-term Victory) is a meaningful achievement in its own right. Milestones 4 and 5 are significantly harder — thresholds are much higher and the Long-term Victory (Milestone 5) may require 60–80 years of sustained effort for a major power.

4. **Reward alignment** — Each milestone buff specifically eases the hardest challenge on that victory path. Conquest rewards reinforce military capability; Trade rewards merchant and commercial power; etc.

5. **No time-limited buffs** — All rewards are permanent static modifiers or one-shot scripted effects (gold, manpower, prestige). There are no temporary bonuses.

6. **Age 6 ceiling** — All final milestones are designed to be achievable before entering Age 6 (approximately 1700 CE). Age 6 content is explicitly out of scope.

7. **Buff scale** — Milestones 1–3 rewards are each approximately 1–2 Advances in power gain. Milestones 4 and 5 rewards are proportionally larger (2–3 Advances each) to match their difficulty. Cumulative rewards across all 5 milestones of one path must not break game balance.

8. **Additive only** — The mod reads vanilla state (locations count, tech count, trade income) but never modifies any vanilla game system.

---

## 3. Victory Types

Six victory paths, each reflecting a historically meaningful way a 15th–18th century state could demonstrate pre-eminence.

### 3.1 Conquest Victory (征服胜利)

**Representative nations:** Ottoman Empire, Muscovy, Ming China, Castile  
**Core metric:** Total owned locations count

**Rationale:** The most direct form of geopolitical dominance. Thresholds are absolute location counts, making this path harder for small nations (who must dramatically expand) and naturally achievable for great powers who maintain growth.

**Milestone structure:**

| Node | Label | Approx. threshold | Reward category |
|---|---|---|---|
| 1 | — | ~150 locations | Combat capability (manpower, army morale) |
| 2 | — | ~350 locations | Logistics (supply, attrition reduction) |
| 3 | Short-term Victory (短期胜利) | ~600 locations | Governance (admin efficiency, unrest) |
| 4 | — | ~1100 locations | Administration at scale (autonomy reduction, corruption) |
| 5 | Long-term Victory (长期胜利) | ~1600 locations | Grand legacy (prestige cap, manpower cap) |

---

### 3.2 Prosperity Victory (繁荣胜利)

**Representative nations:** Netherlands, Burgundy, England, any domestic-focused power  
**Core metric:** A composite domestic development score combining total population, average location prosperity, and total buildings constructed

**Rationale:** Rewards players who invest in their home territories rather than external expansion. The composite metric prevents single-dimension gaming.

**Milestone structure:**

| Node | Label | Trigger condition | Reward category |
|---|---|---|---|
| 1 | — | Composite threshold 1 | Domestic production bonus, tax income |
| 2 | — | Composite threshold 2 | Pop growth, building cost reduction |
| 3 | Short-term Victory (短期胜利) | Composite threshold 3 | Development cost reduction |
| 4 | — | Composite threshold 4 (high) | Construction speed, educated pop bonus |
| 5 | Long-term Victory (长期胜利) | Composite threshold 5 (very high) | Permanent construction speed + population cap bonus |

---

### 3.3 Trade Victory (贸易胜利)

**Representative nations:** Venice, Genoa, Portugal, Netherlands, England  
**Core metric:** Combination of trade income share, number of dominated trade nodes, and total merchants

**Rationale:** Reflects the historical reality that some states built their power entirely through commercial dominance. Venice — the archetype of a state that never needed territorial conquest to be a great power — is the design reference.

**Milestone structure:**

| Node | Label | Trigger condition | Reward category |
|---|---|---|---|
| 1 | — | Trade income share threshold | Merchant power, trade node influence |
| 2 | — | Dominating multiple nodes | Light ships, merchant count |
| 3 | Short-term Victory (短期胜利) | Major trade empire | Trade efficiency |
| 4 | — | Near-monopoly on key nodes | Trade steering bonus |
| 5 | Long-term Victory (长期胜利) | Trade hegemon | Permanent trade income multiplier, merchant count |

---

### 3.4 Diplomatic Victory (外交胜利)

**Representative nations:** Small nations, Holy Roman Empire members, Papacy  
**Core metric:** `tv_diplomatic_victory_points` (DVP) — a country variable accumulated permanently through diplomatic actions

**DVP sources (via on_action and events):**
- Forming a defensive alliance with a major power: +5 DVP
- Becoming guarantor of another nation: +2 DVP
- Successfully mediating a peace treaty: +10 DVP
- Winning a vote in an International Organization: +5 DVP
- Concluding a royal marriage with a ruling dynasty: +3 DVP
- Surviving a war as a weaker nation (favorable peace as defender): +5 DVP

**Rationale:** Specifically designed for players of smaller nations who prefer non-military playstyles. DVP accumulates permanently and cannot be lost, rewarding sustained diplomatic engagement.

**Milestone structure:**

| DVP threshold | Label | Reward category |
|---|---|---|
| 50 DVP | — | Diplomatic reputation, opinion bonus |
| 120 DVP | — | Alliance reliability, defensive bonuses |
| 220 DVP | Short-term Victory (短期胜利) | Diplomatic range, claim fabrication speed |
| 380 DVP | — | Diplomatic immunity, vassal bonuses |
| 580 DVP | Long-term Victory (长期胜利) | Permanent casus belli defense, prestige |

---

### 3.5 Cultural Victory (文化胜利)

**Representative nations:** Italian city-states (Florence, Venice, Milan), France, Burgundy  
**Core metric:** `tv_cultural_influence_points` (CIP) — accumulated through artifact ownership and cultural spread

**CIP sources:**
- Owning an artifact: +10 CIP (checked monthly; once per artifact)
- Being origin nation of a cultural spread event: +3 CIP per event
- Maintaining high court spending above threshold per era: +5 CIP per era

**Rationale:** The EU5 timeframe (1337–1821) directly encompasses the Renaissance, Reformation, and Enlightenment. Cultural victory rewards players who invest in court, art, and cultural prestige — with Italian city-states as the natural exemplar.

**Milestone structure:**

| CIP threshold | Label | Reward category |
|---|---|---|
| 50 CIP | — | Court attraction, ideas cost reduction |
| 120 CIP | — | Diplomat effectiveness, cultural prestige |
| 220 CIP | Short-term Victory (短期胜利) | Artifact find chance, court income |
| 380 CIP | — | Cultural spread multiplier, missionary strength |
| 580 CIP | Long-term Victory (长期胜利) | Permanent cultural spread multiplier, prestige cap |

---

### 3.6 Scientific Victory (科技胜利)

**Representative nations:** Western European powers from mid-game onward  
**Core metric:** `tv_science_score` — a weighted count of researched technologies, where Age 5 (steam-era) technologies carry maximum weight

**Technology weight by age:**
- Age 1–2 technologies: weight ×1
- Age 3 technologies: weight ×2
- Age 4 technologies: weight ×3
- Age 5 technologies (incl. steam engine, railways): weight ×5

**Rationale:** Early scientific leadership (broad research) unlocks early milestones. But scientific pre-eminence in this era is ultimately defined by the Industrial Revolution threshold — the final milestone requires engagement with Age 5 steam and industrial technologies, tying scientific victory to historical context.

**Milestone structure:**

| Score threshold | Label | Reward category |
|---|---|---|
| Age 1–2 era score | — | Research speed bonus |
| Age 3 era score | — | Technology spread, military effectiveness |
| Age 4 era score | Short-term Victory (短期胜利) | Institution spread speed, educated pop growth |
| High Age 4 score | — | Scientific institution bonus, production bonus |
| Age 5 score (steam/industrial) | Long-term Victory (长期胜利) | Permanent production bonus, army modernization |

---

## 4. Milestone Threshold Calibration

Exact thresholds require playtesting with real game data. The targets below are design intentions:

| Victory type | M1 pace (major power) | M3 pace / Short-term Victory | M5 pace / Long-term Victory |
|---|---|---|---|
| Conquest | ~10 years | ~30 years | ~70 years |
| Prosperity | ~10 years | ~25 years | ~60 years |
| Trade | ~15 years | ~35 years | ~70 years |
| Diplomatic | ~15 years | ~35 years | ~70 years |
| Cultural | ~15 years | ~35 years | ~70 years |
| Scientific | ~10 years | ~30 years | Requires Age 5 entry |

Milestones 4 and 5 are designed to be significantly harder than 1–3 — the threshold jump from M3 to M4 should feel noticeably larger. Minor powers should expect approximately 1.5–2× the time per milestone.

---

## 5. Technical Architecture

### 5.1 Situation panel

All six victory types share a single situation (`tv_victory_situation`). The situation panel shows simultaneous progress for every path, the current milestone reached on each, and which paths have reached Short-term or Long-term Victory.

Files: `src/in_game/common/situations/towards_victory_situations.txt` and `src/in_game/gui/panels/situation/towards_victory_situation.gui`

### 5.2 Milestone events

A monthly on_action (`towards_victory_yearly.txt`) checks all milestone triggers. When a milestone condition is first met, a country event fires to notify the player and grant the reward. A per-victory-type country variable tracks the highest milestone reached, preventing re-triggering.

Event namespace: `tv`  
Event IDs: `tv.conquest.1`–`tv.conquest.5`, `tv.prosperity.1`–`tv.prosperity.5`, etc. (5 events per path, 30 total)

### 5.3 Namespace

All identifiers use `tv_` prefix:
- Situation: `tv_victory_situation` (single shared situation for all six paths)
- Events: `tv.conquest.1`–`tv.conquest.5`, etc.
- Scripted triggers: `tv_conquest_milestone_1`, etc.
- Scripted effects: `tv_grant_conquest_milestone_1`, etc.
- Static modifiers: `tv_conquest_m1_bonus`, etc.
- Country variables: `tv_conquest_milestone`, `tv_diplomatic_victory_points`, etc.

### 5.4 Compatibility

The mod uses no `TRY_OVERRIDE` or file replacement. All files are additive. Location-scoped static modifiers use the `TRY_REPLACE` pattern in `src/main_menu/common/static_modifiers/` per EU5 engine requirements. The mod does not modify any vanilla on_actions files — new on_action entries are additive via the standard EU5 merge system.

---

## 6. Reward Balance Reference

Milestone rewards scale with difficulty.

| EU5 Advance (reference) | Approximate power gain |
|---|---|
| 1 Advance | A modest national modifier, e.g. +5% tax income or +0.1 manpower |
| 3 Advances | A meaningful national modifier, e.g. +10% manpower or +5% discipline |

| Milestone | Target reward size |
|---|---|
| 1 | ~1 Advance |
| 2 | ~1–2 Advances |
| 3 (Short-term Victory) | ~2 Advances |
| 4 | ~2–3 Advances |
| 5 (Long-term Victory) | ~3 Advances |

Cumulative reward across all 5 milestones of one path: ~10–11 Advances equivalent. This is meaningful but not game-breaking — comparable to having a strong set of national ideas plus a few extra Advances.

---

## 7. Out of Scope (v0.1.0)

- Per-nation mission trees or narrative content
- Age 6 milestones or post-industrial content
- UI changes outside of situation panels
- Modification of any vanilla game file
- Multiplayer-specific scoring
- Victory "screen" or end-game state (EU5 has no game-end concept)
