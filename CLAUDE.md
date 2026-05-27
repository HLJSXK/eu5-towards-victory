# Towards Victory — Claude Instructions

## Session Start

For any non-trivial task, read `docs/knowledge/BRIEF.md` first. It is a compact summary of all known EU5 gotchas, valid enums, and scope rules. This avoids re-exploring docs for patterns already discovered.

Before editing files, build a task-scoped AI context:

```
conda run --no-capture-output -n eu5 python scripts/ai_context.py --changed
```

or, when target files are known:

```
conda run --no-capture-output -n eu5 python scripts/ai_context.py --files <path> [<path> ...]
```

Read every risk card listed by the script. This is mandatory for high-risk domains such as `generic_actions`, where tooltip and selection pre-evaluation can execute unsafe reads before the player confirms an action. The Events risk card is routed for event files because option tooltips can pre-evaluate visible effect chains before the player confirms a choice. The IO risk card is also routed for IO definitions, IO laws, and country interactions that find or mutate TV international organizations.
`src/in_game/common/laws/` is routed to the `international_organizations` risk card because IO policy scopes and AI math pre-evaluation have recurring runtime traps.

## Resume / Handoff Discipline

When a turn includes a handoff summary, compaction summary, or explicit prior-agent progress, treat it as the current task state, not as background reading.

- Trust the summary's "already read", "already verified", "already changed", and "remaining next steps" unless local evidence contradicts it.
- First actions after a handoff should be limited to `git diff`, `git status`, reading the named target files, or running the exact validation/check command listed as next. Do not restart the normal session bootstrap just because a new model is continuing the work.
- Do not rerun `ai_context.py`, reread broad docs, or re-verify references named in the handoff unless the summary is internally inconsistent, the target files changed since the handoff, or a validation/runtime error points directly at that area.
- Search narrowly. In a continuation, broad `rg` over `reference_game_files`, `reference_mods`, or the whole repo requires a specific missing fact and a stated pattern; prefer file-scoped searches and the references already recorded in the handoff.
- If code was already modified before the handoff, run validation before opening a new investigation path. Let concrete errors guide any further exploration.
- Before resuming substantial work, restate the continuation checkpoint in one or two sentences: what is already done, what the next blocking step is, and which local check will be performed first.

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
- **`location_rank` enum** — valid values: `rural_settlement`, `town`, `city`, `megalopolis` (EU4 names like `village` cause silent failures)
- **Localization YAML** — must be UTF-8 BOM (not plain UTF-8); only straight ASCII double-quotes `"` are valid
- **`custom_tooltip`** — never remove it; dotted suffix format IS valid in event options; verify key format before changing
- **Pre-test validation** — run `conda run --no-capture-output -n eu5 python scripts/validate.py --changed --fix` before launching the game
- **`select_trigger` pre-evaluation** — EU5 pre-evaluates a generic action's `effect` block at each selection step before the user confirms: after step 1 only the first `target_flag` scope is set; after step 2 the character is set but any variables that would be written by the effect itself (e.g. `tv_governed_area`) do not yet exist on the character. Guard multi-step effects with `if = { limit = { exists = scope:target  exists = scope:target_1 } }` and use `?=` on any variable access that may be absent on a freshly selected character.
- **Wonder/building effect split** — EU5 building `modifier` and `raw_modifier` are local; `capital_country_modifier` only applies country effects when the building is in the capital. Engineering Department wonders may be outside the capital, so put designed local effects on final/helper buildings (`modifier` for per-level local effects, `raw_modifier` for flat local ceremony effects) and apply all national/global wonder effects through permanent country modifiers during finalization. Never put global effects directly on wonder buildings.

## IO Architecture Invariants

The three TV IOs (`tv_arts_exhibition`, `tv_diplomatic_alliance`, `tv_academy_of_sciences`) enforce these rules with no exceptions:

1. **`international_organization_chooses_new_leader` is globally banned** on all TV IO-related code — this triggers the vanilla election process and violates the no-elections design. The code correctly omits it everywhere.

2. **`unique = no` — never add `unique = yes`.** All three are non-unique. Use `every_international_organizations_member_of = { limit = { international_organization_type = international_organization_type:<io_type> } ... }` to scope to them; never `international_organization:type_name`.

3. **`leader_change_trigger_type = none` — never change it.** Any other value allows automatic `leader_country` reassignment, breaking the founding-country lock.

4. **Great person characters are country variables on the `leader_country`, not the vanilla ruler.** Monthly_change blocks must use `leader_country.var:tv_xxx_leader_char.attribute` — never `appointed_leader.attribute`.

5. **IO header uses `blockoverride` to display the appointed character variable** — not the vanilla `GetRuler` or `GetLeaderCountry.GetGovernment.GetRulerOrRegent` accessor.

## Milestone Trigger Tooltip Pattern

All milestone scripted_triggers **must** use one `custom_tooltip` block per condition group so the engine displays each condition on its own tooltip line with an independent pass/fail indicator.

**Correct pattern** (separate `custom_tooltip` blocks; implicit AND at top level):
```
tv_example_milestone_1 = {
    custom_tooltip = {
        text = TV_EXAMPLE_M1_TRIGGER_DESC
        has_variable = tv_example_score
        var:tv_example_score >= 100
    }
    custom_tooltip = {
        text = TV_EXAMPLE_M1_EXTRA_TRIGGER_DESC
        has_variable = tv_example_extra_var
        var:tv_example_extra_var >= 1
    }
}
```

**Anti-pattern** (do not use — collapses all conditions into one tooltip line):
```
tv_example_milestone_1 = {
    custom_description = {
        text = TV_EXAMPLE_M1_TRIGGER_DESC
        has_variable = tv_example_score
        var:tv_example_score >= 100
        has_variable = tv_example_extra_var
        var:tv_example_extra_var >= 1
    }
}
```

**YAML data rule:** The `extra_trigger_block` field in `victory_paths.yaml` must always be `null` or a **complete `custom_tooltip = { ... }` block**. Raw condition lines are no longer valid. Add a matching `extra_trigger_desc` key under `loc` for the new tooltip's localization.

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

Also, always run scripts via `conda run --no-capture-output -n eu5 python scripts/...` — never bare `python`.

## Script System

### When to Script a File

| Condition | Decision |
|---|---|
| File >200 lines AND ≥3 repeated structural units (or >60% structural boilerplate) | **Must script** |
| File 100–200 lines AND ≥3 repeated structural units | **Should script** |
| File 50–100 lines with visible repetition | **Consider scripting** |
| File <100 lines with mostly unique content per block | **Manual OK** |
| File generated by gen_victory.py (victory path core) | **Already scripted — edit `data/victory_paths.yaml`** |

When inserting new content would push a manual file past the "must script" threshold, convert it to script management first.

When creating a new file, check if it will be repetitive — if so, create the script and data file instead of writing the src file directly.

### @Generated Header (mandatory in every generated file)

```
# @Generated by scripts/<relative-path-from-repo-root>
#   Data:    data/<data-file>
#   Regen:   conda run --no-capture-output -n eu5 python scripts/<relative-path>
# Do not edit directly — modify the data file and re-run the generator.
```

For `.gui` files place these `#` comment lines at the very top, before the first widget.

### Script Directory Layout

Infrastructure scripts stay at `scripts/` root:
`validate.py`, `ai_context.py`, `gen_brief.py`, `gen_index.py`, `gen_scaffold.py`, `gen_victory.py`, `gen_messagetypes.py`, `gen_locked_advances.py`, `check_overview.py`

One-off asset helpers also stay at repository/script root. `scripts/generate_dds_icon.py` reads `generate_dds_icon_config.json` plus optional `generate_dds_icon.local.json`, selects one target (`trade_good_icon` or `trade_good_illustration`), can refine a short prompt, uploads that target's same-type style-reference DDS/PNG files, and writes one configured DDS target with enforced dimensions/file-size limits. Use the `conda run --no-capture-output -n eu5 python scripts/generate_dds_icon.py` form when running it.

**1:1 feature scripts** live under `scripts/` mirroring `src/`, named `gen_<target_filename_without_extension>.py`:
```
scripts/
├── in_game/
│   ├── common/
│   │   ├── building_types/gen_towards_victory_buildings.py
│   │   ├── generic_actions/gen_tv_io_leader_actions.py
│   │   └── laws/gen_tv_alliance_laws.py
│   └── gui/panels/organization/gen_tv_academy_of_sciences_gui.py
└── ...
```

To find whether a src file has a generator: look for `scripts/<same-relative-path>/gen_<filename>.py`.

### gen_victory.py Exception (multi-output)

`gen_victory.py` generates 13 tightly-coupled files from `data/victory_paths.yaml`. These are grandfathered as a multi-output exception. Edit `data/victory_paths.yaml` and re-run `gen_victory.py` for any change to those 13 files.

### Current Generated Files

| Generated file (in src/) | Data source | Script |
|---|---|---|
| `scripted_triggers/towards_victory_triggers.txt` | `data/victory_paths.yaml` | `scripts/gen_victory.py` |
| `scripted_effects/towards_victory_effects.txt` | `data/victory_paths.yaml` | `scripts/gen_victory.py` |
| `static_modifiers/towards_victory_modifiers.txt` | `data/victory_paths.yaml` | `scripts/gen_victory.py` |
| `situations/towards_victory_situations.txt` | `data/victory_paths.yaml` | `scripts/gen_victory.py` |
| `on_action/towards_victory_yearly.txt` | `data/victory_paths.yaml` | `scripts/gen_victory.py` |
| `events/towards_victory_*_events.txt` (×6) | `data/victory_paths.yaml` | `scripts/gen_victory.py` |
| `localization/*/towards_victory_l_*.yml` (×2) | `data/victory_paths.yaml` | `scripts/gen_victory.py` |
| `scripted_effects/tv_advance_unlock_effects.txt` | `data/locked_advances.yaml` | `scripts/gen_locked_advances.py` |
| `building_types/towards_victory_buildings.txt` | `data/academy_buildings.yaml` | `scripts/in_game/common/building_types/gen_towards_victory_buildings.py` |
| `generic_actions/tv_io_leader_actions.txt` | `data/io_leaders.yaml` | `scripts/in_game/common/generic_actions/gen_tv_io_leader_actions.py` |
| `laws/tv_alliance_laws.txt` | `data/alliance_laws.yaml` | `scripts/in_game/common/laws/gen_tv_alliance_laws.py` |
| `gui/panels/organization/tv_academy_of_sciences.gui` | `data/locked_advances.yaml` | `scripts/in_game/gui/panels/organization/gen_tv_academy_of_sciences_gui.py` |

### Before Editing Any src File

Check whether `data/generated_files.yaml` lists it as script-managed. If it does, edit the data YAML and re-run the generator instead of editing the src file.

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

### Step 2.5: Check if change is data-driven

**First:** check `data/generated_files.yaml` to see if the target file is script-managed. If it is, edit the data YAML and re-run the generator — do not touch the src file directly.

If the change affects an **existing victory path** (threshold, modifier value, event text, localization)
or **adds a new path** following the existing 6-path pattern:

1. Edit `data/victory_paths.yaml` only — **do NOT hand-edit the generated files**
2. Run the generator:
   ```
   conda run --no-capture-output -n eu5 python scripts/gen_victory.py
   ```
3. Skip to Step 5 (validate).

**1对1原则**: Each field in `victory_paths.yaml` maps directly to one piece of generated output.
Complex EU5 script bodies (score updaters, progress pct blocks, on_action effects) are stored as
verbatim strings in the YAML; the generator inserts them unchanged. The generator is a template
filler, not a code reasoner.

**Files generated by gen_victory.py — do not hand-edit:**
- `towards_victory_triggers.txt`, `towards_victory_effects.txt`, `towards_victory_modifiers.txt`
- `towards_victory_situations.txt`, `towards_victory_yearly.txt`
- `towards_victory_{conquest/prosperity/trade/diplomatic/cultural/science}_events.txt`
- `towards_victory_l_english.yml`, `towards_victory_l_simp_chinese.yml`

If adding a mechanic with no template in gen_victory.py (e.g. a new field type), continue to Step 3,
then extend the generator and YAML schema to cover it before hand-editing generated files.

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
conda run --no-capture-output -n eu5 python scripts/validate.py --changed --fix
```
Expected: 0 errors, 0 warnings (`[FIXED]` BOM lines are not errors).

### Step 6: Knowledge capture + docs update
If any new EU5 pattern was discovered during this session, execute the standard Knowledge Capture protocol (see below). Then:
```
conda run --no-capture-output -n eu5 python scripts/gen_brief.py
```

---

## Path Mapping

- `src/` — mod source (Towards Victory)
  - `src/in_game/common/` — victory triggers, effects, situations, modifiers, on_action
  - `src/in_game/events/` — milestone notification events (`towards_victory_events.txt`)
  - `src/in_game/gui/` — situation panel GUI (manually maintained)
  - `src/main_menu/localization/` — hand-written strings (`towards_victory_l_*.yml`)
- `docs/knowledge/` — `BRIEF.md` (auto-generated), `PROJECT_OVERVIEW.md`, `anti_patterns.yaml`, `valid_enums.yaml`, `risk_cards/`
- `docs/guides/AI_Tool_Workflow_Prompt.md` — full 3-step rule and violation history
- `docs/design/Towards_Victory_Design.md` — victory conditions design philosophy
- `docs/technical/` — EU5 modding reference
- `scripts/` — infrastructure: `ai_context.py`, `gen_brief.py`, `gen_index.py`, `gen_scaffold.py`, `validate.py`, `check_overview.py`, `gen_victory.py`, `gen_locked_advances.py`, `gen_messagetypes.py`
- `scripts/in_game/` — 1:1 feature generators mirroring `src/in_game/` (see Script System section)
- `data/` — YAML sources for generated files; `data/generated_files.yaml` is the authoritative registry
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
   Set `detectability`:
   - `lint` only when the pattern is narrow, path-scoped, and safe for `validate.py` to run automatically.
   - `needs_parser` when the rule needs brace-aware, scope-aware, or semantic analysis.
   - `advisory` when it is a human/AI warning rather than an automated check.
2. Update the relevant `docs/knowledge/risk_cards/*.md` file when the discovery belongs to a task domain that already has a card, especially `generic_actions`.
   If the discovery creates a new high-risk task domain, create a short risk card and register it in `scripts/ai_context.py` `DOMAIN_RULES`.
3. Add a row to the "Documented Violations" table in `docs/guides/AI_Tool_Workflow_Prompt.md`.
4. Update `docs/technical/EU5_Modding_Knowledge_Base.md` if the pattern is broadly applicable.
5. If a `needs_parser` rule is recurring or high-impact, extend `scripts/validate.py` with a narrow parser/check so future AI runs see it automatically.
6. Run `conda run --no-capture-output -n eu5 python scripts/gen_brief.py` to regenerate `docs/knowledge/BRIEF.md`.

For minor discoveries (single modifier name, single typo fix), steps 1 and 6 only.

**Do not wait for the user to ask.** Knowledge capture must happen in the same response as the fix, before the task is marked complete.

## AI Workflow Maintenance Protocol

The project assumes humans do not maintain code or AI workflow files manually. AI agents must maintain the workflow whenever they change it:

- If `docs/knowledge/risk_cards/` changes, ensure the card is listed by `scripts/ai_context.py` when its domain is touched.
- If `scripts/ai_context.py` domain coverage or output changes, update `CLAUDE.md`, `docs/guides/AI_Tool_Workflow_Prompt.md`, and the script table in `docs/knowledge/PROJECT_OVERVIEW.md`.
- If `scripts/validate.py` gains a reliable checker for a previous `needs_parser` rule, update the corresponding `anti_patterns.yaml` entry to `detectability: lint`.
- If a `detectability: lint` regex is added or changed, add/update fixtures under `tests/fixtures/anti_patterns/<rule_id>/` and run `conda run --no-capture-output -n eu5 python scripts/test_lint_rules.py`.
- If `scripts/validate.py` reports a new warning, fix it unless the warning is intentionally accepted. Accepted warnings must be added to `data/validation_baseline.yaml` with a rationale; never baseline a warning just to make validation pass.
- If a new warning domain appears repeatedly in runtime logs, prefer a risk card plus `ai_context.py` domain routing over adding more long-form prose to `BRIEF.md`.
- After any change to `anti_patterns.yaml`, `valid_enums.yaml`, `PROJECT_OVERVIEW.md`, or `risk_cards/`, regenerate `BRIEF.md`.
- Before finishing, run `conda run --no-capture-output -n eu5 python scripts/validate.py --changed --fix --ai-report`; explain any baselined warnings that remain.

## Project Overview Update Protocol

After completing any task you MUST read `docs/knowledge/PROJECT_OVERVIEW.md` and decide whether an update is needed.

### When to update

Update when any of the following are true for this session:
- A new gameplay system, feature, or mechanic was added or significantly changed in `src/`
- A directory was created, renamed, or deleted anywhere in `src/`
- A new Python script was added to `scripts/`, or an existing script's purpose or output changed
- A new AI workflow domain, risk card, or `ai_context.py` routing rule was added or significantly changed
- Validation baseline or lint fixture policy changed in a way that affects AI workflow behavior

### When NOT to update

Do NOT update for:
- Changes confined to `docs/`, `reference_*/`, or other non-mod support files
- Localization text edits (wording changes, not feature existence)
- Bug fixes that correct behavior without adding or removing features
- Style or formatting changes with no functional effect

### What to write

`PROJECT_OVERVIEW.md` describes the **complete current project state**, not the changes made this session.

### After updating

Run `conda run --no-capture-output -n eu5 python scripts/gen_brief.py` to regenerate `docs/knowledge/BRIEF.md`.
