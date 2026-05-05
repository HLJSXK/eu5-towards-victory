# Towards Victory — Claude Instructions

## Session Start

For any non-trivial task, read `docs/knowledge/BRIEF.md` first. It is a compact summary of all known EU5 gotchas, valid enums, and scope rules. This avoids re-exploring docs for patterns already discovered.

## Project Identity

- **Mod Name:** Towards Victory (胜利条件)
- **Mod ID:** `eu5mp.towards_victory`
- **Version:** 0.1.0 | Target: EU5 `1.*.*`
- **Status:** In Development
- **Mod source:** `src/` (single mod; files at `src/in_game/`, `src/main_menu/`)
- **Namespace prefix:** `tv_` — all mod-defined identifiers (situations, triggers, effects, modifiers, variables, events) must use this prefix

## EU5 Syntax Rules

EU5 uses the Jomini engine. Do NOT assume EU4 syntax works.

## The 3-Step Resolution Rule

When writing or modifying EU5 scripts, follow this sequence:

1. **Direct Edit** — only if you are 100% certain about the syntax.
2. **Consult Docs** — read `reference_official_defines/` first if unsure.
3. **Consult Source** — search `reference_game_files/` and `reference_mods/` if Step 2 is insufficient.

## Mandatory Reference Categories (Step 1 FORBIDDEN)

For the categories below, you MUST go to Step 2 or 3 before writing any code. No exceptions.

- `blockoverride` block names and their allowed child properties
- `custom_tooltip` key formats (dotted suffixes, etc.)
- `situation_card_common` / `card_common` GUI template structure
- `location_rank:*` enum values
- Any `static_modifier`, `country_modifier`, `location_modifier` name
- Any `scripted_trigger` or `scripted_effect` not defined in this mod
- Localization YAML encoding and quote character rules
- GUI expression syntax (`GetVariable`, `.IsSet`, `MakeScope`, etc.)
- Any GUI icon display — check `reference_game_files/game/main_menu/gui/shared/font_icons.gui`
  for `@xxx!` inline syntax **before** using icon widgets or custom solutions

## Critical EU5 Gotchas

- **Location `auto_modifiers` are NON-FUNCTIONAL** — use `TRY_REPLACE` in `src/main_menu/common/static_modifiers/` with `game_data = { category = location }` instead
- **`location_rank` enum** — only 3 valid values: `rural_settlement`, `town`, `city` (EU4 names like `village` cause silent failures)
- **Localization YAML** — must be UTF-8 BOM (not plain UTF-8); only straight ASCII double-quotes `"` are valid
- **`custom_tooltip`** — never remove it; dotted suffix format IS valid in event options; verify key format before changing
- **Pre-test validation** — run `python scripts/validate.py --changed` before launching the game

## GUI Icon Display Rule

When displaying an icon in the UI, follow this exact priority order and stop at the first tier that works:

1. **`@icon_name!` inline syntax** — Check `reference_game_files/game/main_menu/gui/shared/font_icons.gui`
   for the icon name. Use in `raw_text` / `text` GUI fields and localization YAML values.
   Requires zero new code and no widget overhead.
2. **Icon widget** — Use `icon = { texture = "..." }` or equivalent widget when the display context
   cannot use inline text (e.g. standalone widget placement), or when the icon is not in `font_icons.gui`.
3. **From scratch** — Only if tiers 1 and 2 both fail: define a new `texticon` block in a `.gui` file
   or create a new sprite. This is the most expensive option and requires explicit justification.

Before using tier 2 or 3, you MUST output a verification line confirming the icon is absent from `font_icons.gui`.

## Declarative Verification Requirement

Before writing code that falls under the above categories, output this line first:

> **Verification** — Step [2/3], Reference: `[file:line]`, Quote: `"[exact text from source]"`

If no reference is found:

> **Verification** — FAILED. Cannot verify `[syntax]`. Asking user before proceeding.

Then stop. Do not guess.

## Bug Fix Rule

When a script/GUI pattern causes a bug: verify and replace with correct syntax. Do NOT remove the feature. Removal is only allowed if Steps 2 and 3 both fail to find any reference, and the user is explicitly told.

## Early Development: Ask-First Policy

This mod is in early development (v0.1.0). When in doubt about design intent, **ask the user before implementing**.

Ask before proceeding whenever:
- A design document leaves a specific threshold, weight, or value unspecified
- Two or more valid EU5 approaches could implement the same mechanic and the choice has gameplay consequences
- A design decision requires assumptions about player interaction not covered by `docs/design/Towards_Victory_Design.md`
- The scope of a requested change could be interpreted narrowly or broadly
- Any requirement in the design document is ambiguous or contradictory

Do NOT resolve ambiguity by picking the "most reasonable" interpretation and proceeding silently.

## Python Script Requirements

Every new Python script in `scripts/` **must** include the following block immediately after the stdlib imports, before any module-level code:

```python
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
```

`import sys` must also be present (add it if not already there).

Also, always run scripts via `conda run -n eu5 python scripts/...` — never bare `python`.

## Victory Condition Design Workflow

When asked to design or implement a victory condition component (situation, event, modifier, trigger, effect), follow these steps in order.

### Step 1: Read knowledge documents
```
Read docs/knowledge/BRIEF.md
Read docs/design/Towards_Victory_Design.md
```

### Step 2: Analyse the component
Determine the EU5 script type required (situation, event, scripted_trigger, scripted_effect, static_modifier, on_action).
Check `data/index/static_modifiers.txt` for reusable modifiers and `data/index/scripted_triggers.txt` for reusable triggers.
For new static modifiers, verify modifier effect names against `reference_game_files/game/main_menu/common/modifier_type_definitions/00_modifier_types.txt` before writing.

### Step 3: Write EU5 scripts directly
Create files in `src/in_game/common/` (triggers, effects, modifiers, situations, on_action) or `src/in_game/events/` (events).
All mod-defined identifiers must use the `tv_` namespace prefix.
For location-scoped static modifiers, write them using `TRY_REPLACE` in `src/main_menu/common/static_modifiers/`.
Perform 3-step verification for any syntax in Mandatory Reference Categories before writing.

### Step 4: Add localization
Add keys to `src/main_menu/localization/english/towards_victory_l_english.yml` (UTF-8 BOM, straight ASCII double-quotes).
Add matching keys to `src/main_menu/localization/simp_chinese/towards_victory_l_simp_chinese.yml`.

### Step 5: Validate
```
conda run -n eu5 python scripts/validate.py --changed
```
Expected: 0 errors, 0 warnings.

### Step 6: Knowledge capture + docs update
If any new EU5 pattern was discovered during this session, execute the standard Knowledge Capture protocol (see below). Then:
```
conda run -n eu5 python scripts/gen_brief.py
```

---

## Path Mapping

- `src/` — mod source (Towards Victory)
  - `src/in_game/common/` — victory triggers, effects, situations, modifiers, on_action
  - `src/in_game/events/` — milestone notification events (`towards_victory_events.txt`)
  - `src/in_game/gui/` — situation panel GUI (manually maintained)
  - `src/main_menu/localization/` — hand-written strings (`towards_victory_l_*.yml`)
- `docs/knowledge/` — `BRIEF.md` (auto-generated), `PROJECT_OVERVIEW.md`, `anti_patterns.yaml`, `valid_enums.yaml`
- `docs/guides/AI_Tool_Workflow_Prompt.md` — full 3-step rule and violation history
- `docs/design/Towards_Victory_Design.md` — victory conditions design philosophy
- `docs/technical/` — EU5 modding reference
- `scripts/` — `gen_brief.py`, `gen_index.py`, `gen_scaffold.py`, `validate.py`, `check_overview.py`
- `data/index/` — symbol lookup tables (auto-generated by gen_index.py)
- `reference_official_defines/` — official EU5 define/type reference files
- `reference_game_files/` — vanilla EU5 script sources (Step 3 verification)
- `reference_mods/` — community mod examples (Step 3 verification)

## Knowledge Capture

Knowledge capture is triggered by **either** of the following:

- You used Step 2 or Step 3 verification and discovered a new pattern.
- You fixed a runtime engine error (from `error.log` or in-game logs) that revealed an undocumented EU5 engine behavior — regardless of whether Steps 2/3 were consulted.

When triggered, do ALL of:

1. Add an entry to `docs/knowledge/anti_patterns.yaml` (copy the format of existing entries).
2. Add a row to the "Documented Violations" table in `docs/guides/AI_Tool_Workflow_Prompt.md`.
3. Update `docs/technical/EU5_Modding_Knowledge_Base.md` if the pattern is broadly applicable.
4. Run `python scripts/gen_brief.py` to regenerate `docs/knowledge/BRIEF.md`.

For minor discoveries (single modifier name, single typo fix), steps 1 and 4 only.

**Do not wait for the user to ask.** Knowledge capture must happen in the same response as the fix, before the task is marked complete.

## Project Overview Update Protocol

After completing any task you MUST read `docs/knowledge/PROJECT_OVERVIEW.md` and decide whether an update is needed.

### When to update

Update when any of the following are true for this session:
- A new gameplay system, feature, or mechanic was added or significantly changed in `src/`
- A directory was created, renamed, or deleted anywhere in `src/`
- A new Python script was added to `scripts/`, or an existing script's purpose or output changed

### When NOT to update

Do NOT update for:
- Changes confined to `docs/`, `reference_*/`, or other non-mod support files
- Localization text edits (wording changes, not feature existence)
- Bug fixes that correct behavior without adding or removing features
- Style or formatting changes with no functional effect

### What to write

`PROJECT_OVERVIEW.md` describes the **complete current project state**, not the changes made this session.

### After updating

Run `conda run -n eu5 python scripts/gen_brief.py` to regenerate `docs/knowledge/BRIEF.md`.
