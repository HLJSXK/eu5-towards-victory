# Diplomatic Alliance — Performance Review

Reviewer: Claude Sonnet 4.5
Date: 2026-05-08
Scope: Full performance audit of the diplomatic alliance system per `ai-notes/rules/eu5-performance-review.md`

---

## Summary

**Performance risk: LOW**

The implementation follows safe patterns throughout. No unconditional broad iterators in recurring logic, AI candidate lists are properly scoped, and GUI displays cached variables.

---

## Detailed Analysis

### 1. Monthly Pulse (`monthly_country_pulse` in `tv_diplomatic_alliance.txt`)

**Frequency:** Every month, for EVERY country in the game.

**Analysis:**
- The cohesion growth block is gated by:
  1. `exists = international_organization:tv_diplomatic_alliance` (cheap existence check)
  2. `is_leader_of_international_organization = ...` (cheap flag check)
- Only the **single leader country** passes both gates. All other countries (~200+) exit at step 1 or 2.
- Notification events are gated by `has_variable` + value checks + `NOT = { has_variable = flag }` — once fired, the flag permanently prevents re-evaluation.

**Verdict:** ✅ Safe. Cheap gates first, no iterators, 99.5% of countries exit after 1-2 condition checks.

### 2. Country Interaction AI Evaluation (`tv_seek_diplomatic_support`)

**Frequency:** `ai_tick = monthly`, `ai_tick_frequency = 60` (once every 60 months per AI country).

**Analysis:**
- `potential` gate: only countries with `tv_diplomatic_victory_points >= 50` AND (IO doesn't exist OR is leader). Very few countries pass.
- `ai_interaction_source_list`: uses `every_friendly_or_high_opinion_country` — a **scoped provider**, not `every_country`.
- `visible` filter: `NOT = { has_variable = tv_diplomatic_supporter_of }` — cheap variable check.
- `diplo_chance` + `accept`: simple math on existing values, no iterators.

**Verdict:** ✅ Safe. Conservative tick frequency (60 months), scoped candidate list, cheap filters.

### 3. M1 Grant Effect (`tv_grant_diplomatic_milestone_1`)

**Frequency:** Once per game, ever. Fires exactly one time when M1 is first reached.

**Analysis:**
- Contains `every_country = { limit = { has_variable ... } ... }` — a broad iterator.
- But this runs **only once** during IO creation (gated by `NOT = { exists = ... }`).
- After IO is created, this code path can never execute again.

**Verdict:** ✅ Safe. One-time setup, explicitly allowed by the performance rules.

### 4. `on_annex` Handler

**Frequency:** Fires only when a country is annexed (rare event).

**Analysis:**
- No iterators. Direct variable manipulation on two specific countries (the annexed target and whoever they supported).
- Gated by `has_variable = tv_diplomatic_supporter_of` (most countries don't have this).

**Verdict:** ✅ Safe. Rare event, no iterators, cheap checks.

### 5. Law `on_activate` Effects

**Frequency:** Only when a law vote passes (rare player-driven event).

**Analysis:**
- Simple variable math (`change_variable`, `set_variable`).
- `leader_country ?= { ... }` — scopes to a single entity.
- No iterators.

**Verdict:** ✅ Safe. Rare, minimal work.

### 6. GUI Panel (`tv_diplomatic_alliance.gui`)

**Frequency:** Continuously re-evaluated while the IO panel is open.

**Analysis:**
- 22 `GetVariable`/`MakeScope` expressions total across the panel.
- All display **pre-computed cached variables** (`tv_alliance_cohesion`, `tv_alliance_tier`, `tv_diplomatic_support_count`) — no expensive computation in GUI.
- No `datamodel`/`foreach` iterators — all content is static cards.
- `GetDataModelSize(...)` if valid is a simple count, not an iteration.
- Expandable cards use `GetVariableSystem.Exists(...)` for visibility — engine-native UI state, zero cost.

**Verdict:** ✅ Safe. Displays cached values only, no per-item iteration, no expensive derived computation.

### 7. Generated Effects (from `gen_victory.py`)

**Frequency:** Monthly check via `tv_check_diplomatic_milestones_effect`.

**Analysis:**
- Milestone checker: sequential `if` blocks with `var:tv_diplomatic_milestone < N` guard + scripted_trigger call.
- Scripted triggers check: `has_variable` + `var >= threshold` + `has_variable = tv_alliance_tier` + `var:tv_alliance_tier >= N`.
- All cheap variable comparisons. No iterators.

**Verdict:** ✅ Safe.

---

## Performance Section (per rule requirement)

```
Performance risk: LOW
Repeated execution paths:
  - monthly_country_pulse: runs for all countries but exits after 1-2 cheap checks for 99.5%
  - GUI expressions: 22 cached variable lookups while panel open
Broad iterators:
  - every_country in M1 grant (ONE-TIME only, never repeats)
  - every_friendly_or_high_opinion_country in AI source list (scoped, infrequent)
Caching/incremental update opportunities:
  - Support count: ✅ already incremental (add on support, subtract on annex)
  - Cohesion: ✅ already incremental (monthly add)
  - Alliance tier: ✅ already incremental (add on law activation)
  - All GUI values read from cached variables
Recommended follow-up: None. No performance issues found.
```

---

## Conclusion

All code paths follow the safe patterns defined in the performance rules:
- Monthly logic is gated by cheap checks before any work
- AI interactions use scoped candidate lists with conservative tick frequency
- One-time setup uses `every_country` (explicitly allowed)
- GUI displays only cached variables
- No nested broad iterators anywhere
- Incremental updates throughout (no monthly recalculation)

**No changes recommended.**
