# AI Tool Workflow Prompt (EU5)

Use the following prompt for AI coding tools in this project:

```text
You are an expert Europa Universalis 5 (EU5) modder. EU5 uses an updated Jomini engine. Do not assume EU4 syntax works.

### Workflow: The 3-Step Resolution Rule
When proposing code edits or generating new scripts, you must evaluate your knowledge and follow this exact sequence:

1. **Direct Edit**: If you are 100% certain about the EU5 syntax (e.g., standard Jomini logic), write the script directly.
2. **Consult Docs**: If you are unsure about a specific `script_value`, `data_type`, trigger, or effect, you MUST read the reference files in the `reference_official_defines/` workspace folder first.
3. **Consult Source Files**: If the answer is not in `reference_official_defines/`, search the `reference_game_files/` and `reference_mods/` workspace folder for real-world implementations before writing the code.

### Mandatory Reference Categories (Step 1 is FORBIDDEN)

For the following syntax categories, you are **never** allowed to rely on memory or inference alone.
You MUST go directly to Step 2 or Step 3 before writing or modifying any code:

| Category | Why Step 1 is forbidden |
|---|---|
| `blockoverride` block names and their allowed child properties | Block names are template-specific; accepted property types differ per block |
| `custom_tooltip` key formats (e.g. dotted suffixes like `.tooltip`) | Suffix rules are not documented; guessing caused a feature to be incorrectly removed |
| `situation_card_common` / `card_common` template structure | Inner block rules are invisible without reading `cards.gui` |
| `location_rank:*` enum values | Enum values are engine-defined; wrong values (e.g. `village`) produce silent failures |
| Any `static_modifier`, `country_modifier`, `location_modifier` name | Modifier names must exist in defines; typos cause silent no-ops |
| Any `scripted_trigger` or `scripted_effect` not defined in this mod | Vanilla names change between patches |
| Localization key format rules (YAML encoding, quote characters) | PDX parser rejects non-ASCII quotes; encoding errors cascade silently |
| GUI expression syntax (`GetVariable`, `.IsSet`, `MakeScope`, etc.) | Expression language is undocumented; wrong patterns produce no visible error |
| Any GUI icon display | Must check `font_icons.gui` for `@xxx!` inline texticon before using widget or custom approach |

### Declarative Verification Requirement

Before writing or modifying any code that falls under the Mandatory Reference Categories above,
you MUST output a verification line in this exact format:

> **Verification** — Step [2/3], Reference: `[file path]:[line number]`, Quote: `"[exact text from source]"`

This line must appear **before** the code block. No code may be written without it.

If you cannot locate a suitable reference, output:

> **Verification** — FAILED. Cannot verify `[syntax in question]`. Reporting to user before proceeding.

Then stop and ask the user for guidance. Do NOT guess.

### Constraints
- NEVER hallucinate or guess Paradox script syntax.
- If you cannot verify a command using the steps above, explicitly tell the user: "I cannot verify this syntax, please check the official wiki or logs."
- If a syntax pattern causes bugs, do NOT remove the feature as a first response. You MUST follow the 3-step rule in order (Direct Edit -> reference_official_defines/ -> reference_game_files/) and replace it with a verified working syntax.

### Early Development: Ask-First Policy

This mod is in early development (v0.1.0). The design is still being refined. **When in doubt, ask the user before implementing.**

Ask the user before proceeding whenever:
- A design document leaves a specific threshold, weight, or value unspecified (e.g. "composite threshold 1" with no number given)
- Two or more valid EU5 approaches could implement the same mechanic and the choice has gameplay consequences
- A design decision requires assumptions about how the player interacts with the system (e.g. what happens if two victory paths reach Short-term Victory simultaneously)
- The scope of a requested change could be interpreted narrowly or broadly
- Any requirement in `docs/design/Towards_Victory_Design.md` is ambiguous or contradictory

Do NOT resolve ambiguity by picking the "most reasonable" interpretation and proceeding silently. The cost of asking once is always lower than implementing the wrong thing and rewriting it.
```

## Path Mapping In This Repository

- `docs/` -> project docs and technical notes
- `reference_official_defines/` -> official define/type reference files
- `reference_game_files/` -> vanilla script source files
- `reference_mods/` -> some representative community mods

## Required Behavior For Bug Fixing

- When a previously implemented script/GUI expression fails, the default action is **syntax replacement based on verification**, not feature removal.
- Removal or fallback simplification is only allowed when:
  - the syntax cannot be verified in `reference_official_defines/`, `reference_game_files/` and `reference_mods/`, and
  - the tool explicitly reports this uncertainty to the user.

## GUI Icon Display Priority

When displaying an icon in any UI context, AI tools MUST follow this priority and stop at the first applicable tier:

| Tier | Method | When to use |
|---|---|---|
| 1 | `@icon_name!` inline syntax | Icon exists in `font_icons.gui`; context is `raw_text`/`text`/localization YAML |
| 2 | Icon widget (`icon = { texture = "..." }`) | Standalone widget needed, or icon absent from `font_icons.gui` |
| 3 | From scratch (new `texticon` / new sprite) | Tiers 1 and 2 both inapplicable; must justify explicitly |

Authoritative icon list: `reference_game_files/game/main_menu/gui/shared/font_icons.gui` (180+ entries)

## Documented Violations (Learning Record)

The following violations occurred and informed the Mandatory Reference Categories above:

| Date | Violation | Root cause | Correct behavior |
|---|---|---|---|
| 2026-03 | Removed `custom_tooltip` from event options | Guessed dotted key format was invalid; skipped Steps 2/3 | Read `reference_game_files/`; `ali_qushji_settles.tooltip` confirms dotted keys are valid |
| 2026-03 | Used `location_rank:village` | Guessed enum value; did not check defines | Read `reference_official_defines/`; valid values are `rural_settlement`, `town`, `city` |
| 2026-03 | Placed child `text_single` inside `blockoverride "common_header_text"` | Guessed block accepted child widgets; skipped reading `cards.gui` | Read `cards.gui:1084`; block overrides a `text` property, not a widget container |
| 2026-04 | Used `value = location.local_*` inside a location-scope script value | Assumed `location.` prefix was always required for location variables | `location.` is a navigation link from another scope; inside a location-scope value, reference variables directly without the prefix |
| 2026-04 | Generated script_values with 6-decimal float literals (e.g. `0.084771`) | No awareness of EU5 engine's 5dp precision limit | Round all float literals to ≤5 decimal places in generated and hand-written mod files; engine silently truncates anything beyond the 5th digit |
| 2026-04 | Proposed `datamodel = "[GoodsView.GetGoods]"` inside ContextualTooltipType to filter by key and obtain a Goods datacontext | Assumed GoodsView is a globally accessible object; it is panel-scoped only | No all-goods datamodel exists in tooltip scope; GoodsView is only in goods_overview.gui; no GetGoods('key') string lookup exists anywhere in EU5 GUI |
| 2026-05 | Proposed `multiply_global_variable = { name = X value = 0.95 }` to scale a global variable in-place | Assumed EU5 has a multiply variant analogous to `change_global_variable` | No `multiply_global_variable` effect exists; use hardcoded `set_global_variable` values per case (idempotent) or compute in a local_variable first |
| 2026-05 | Generated `limit = { capital = { prosperity >= var:dm_prosperity_target } }` inside `dm_tick_all_missions` | Assumed `var:X` always reads from country scope; inside `capital = {}` the scope is location, so `var:X` reads the location variable store (wrong value) | Use the literal integer from the spec (e.g. `prosperity >= 75`) instead of `var:` inside location-scope blocks; set `dm_prosperity_target` for GUI display only |
| 2026-05 | Wrote 30 events as `tv.conquest.1 = { ... }` etc. under `namespace = tv` | Assumed event IDs accept arbitrary multi-dot keys; engine actually splits on the first dot only | Event ID must be `<namespace>.<integer>`; split into 6 files (one namespace per category, IDs `tv_conquest.1..5`, etc.). Loc-key dotted suffixes (`tv_conquest.1.t`) are still valid because they aren't event IDs themselves |
| 2026-05 | Set `parentanchor = vcenter` on widgets that were direct children of an `hbox` (36 sites in tv_victory_situation.gui) | Did not internalize that hbox/vbox auto-arrange children on the cross-axis, so child anchors are rejected | Remove `parentanchor` from any widget directly inside `hbox = { ... }` or `vbox = { ... }`; keep it on children of plain `widget`/`window`/etc. |
| 2026-05 | Saved `towards_victory_location_modifiers.txt` and `towards_victory_situations.txt` without UTF-8 BOM | Assumed BOM was only required for localization YAML; engine actually requires it on common/ .txt scripts as well | Always save common/ scripts with UTF-8 BOM (`utf-8-sig`); validate with `head -c 3 <file> \| xxd` -> `ef bb bf` |
| 2026-05 | Stored progress_pct as `score ÷ threshold` (e.g. `160 ÷ 2000`) expecting a float [0,1]; GUI progressbar showed 0% for all paths except science | `change_variable { divide }` is FLOOR integer division — `160÷2000=0`; progressbar default max=1, so integer 1 = 100% and integer 0 = 0% | Use integer scale [0,100]: divide by `threshold÷100` when threshold is divisible by 100, otherwise `multiply=100; divide=threshold`. Always set `max = 100` explicitly on the progressbar widget. |
| 2026-05 | Used `#Y[Country.MakeScope.GetVariable(...).GetValue\|0]#!` to gold-highlight an inline scripted variable in a localization string | Assumed `#Y` is a self-contained tag; when the variable resolves to a digit (e.g. 64), the engine reads `#Y64` as the tag name — `Unknown formatting tag 'y64!'` | Use plain `[variable_expression]` without color, OR add a space separator: `#Y [variable_expression]#!` (leading space becomes visible content). Never put `[` directly after a color tag. |
| 2026-05 | Used `text = TV_CONQUEST_M1_TRIGGER_DESC` in `custom_description` trigger blocks with only a YAML localization entry | Assumed a YAML key suffices for `custom_description`'s `text`; engine actually validates against `common/trigger_localization/` at load | Create an entry in `src/in_game/common/trigger_localization/`: `KEY = { global = KEY }`. The YAML key remains; trigger_localization is the bridge the engine requires. Error: `'No trigger loc KEY'` at startup. |
