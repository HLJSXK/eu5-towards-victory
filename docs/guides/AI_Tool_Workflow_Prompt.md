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
| 2026-05 | Used `text = "TV_RM_TARGET_STEAM_ENGINE"` in a GUI file without a matching localization key | Hard-coded an obsolete research-target key instead of deriving it from the current data/localization set | GUI `text = "KEY"` values are localized; verify the key exists in supported localization files, correct it to the data-backed key, or use `raw_text` only for literal strings. |
| 2026-05 | Added `tv_appoint_governor` and `tv_remove_governor` generic actions but did not list them in any `generic_action_ai_lists` file | Assumed `ai_will_do` and high `ai_tick_frequency` were sufficient for player-facing actions | Every generic action must be explicitly listed in at least one AI list. Use list `potential` to limit evaluation and keep player-only actions listed with restrictive AI behavior. |
| 2026-05 | Used `construct_building = { ... cost_multiplier = 0 instant = yes }` without `cost_multiplier_reason` | Assumed a zero multiplier did not need a cost reason because the building was event-created | Any `construct_building` with `cost_multiplier` must also include `cost_multiplier_reason = <loc key>`. For event-funded construction, vanilla uses `cost_multiplier_reason = "game_concept_event"`. |
| 2026-05 | Left mod-defined IOs without matching `international_organizations/<io_type>.dds` textures | Assumed custom organization panels could provide all visible IO icons | Shared IO UI uses `InternationalOrganization.GetIcon`; provide `main_menu/gfx/interface/icons/international_organizations/<io_type>.dds` matching the IO type key, or shared title/list/tooltips fall back to the generic IO icon. |
| 2026-05 | Added custom `game_concept_tv_*` localization and used `[tv_*\|e]` without registering the concept ID | Assumed `game_concept_*` localization alone creates a concept | Define every custom concept in `src/main_menu/common/game_concepts/tv_game_concepts.txt` with at least a `texture`, or reuse an existing registered concept. Otherwise square-bracket links are parsed as data-system functions and render `ERROR:<concept>`. |
| 2026-05 | Used `multiply_variable = { name = X value = Y }` to scale a variable in-place | Assumed EU4-style multiply_variable exists in EU5 | Use `change_variable = { name = X multiply = Y }`. EU5 has no multiply_variable or divide_variable — all variable math uses change_variable with multiply/divide keys. |
| 2026-05 | Attempted `GetVariable('tv_governed_area').GetArea.GetName` to display an area name stored in a character variable | Assumed `.GetArea` exists as a GUI accessor symmetrically with `.GetCharacter` | `.GetArea` does not exist in EU5 GUI. Pre-compute numeric display values as character variables and read them via `GetVariable('name').GetValue\|0`. Area names stored as scope variables cannot be displayed in GUI. |
| 2026-05 | Used standalone `io_character_card` widgets without overriding inherited sort-highlight blocks | Missed that `io_character_card` reuses `character_entry`, whose name highlight widgets call `FilteredSortedList.IsKeyHoveredByWidgetName` | For `io_character_card` outside a sortable `FilteredSortedList`, add `blockoverride "name_highlight" {}` and `blockoverride "character_entry_name_sort_by_highlight" {}`. Vanilla `middle_kingdom.gui` documents this as blocking error log spam. |
| 2026-05 | Put two top-level children inside a datamodel `item = { ... }` (`vbox` row plus sibling divider `widget`) | Treated an item block like a normal layout container | A datamodel `item` description must contain exactly one child and no properties. Wrap the row and divider inside one parent `vbox`/`widget`. Runtime error: `Malformed item desc`, and it can coincide with text formatter noise while the list renders. |
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
| 2026-05 | Set `size = { 97% 72 }` on `io_character_card` widgets directly under `organization_custom_content` | Treated percentage sizing as independent of the parent layout; hbox/vbox children cannot use percentage `size` components | Remove percentage `size` from hbox/vbox children and drive them with layout policies, stretch factors, or non-percent fixed/min/max sizing. Vanilla `io_character_card` already uses `layoutpolicy_expanding`. |
| 2026-05 | Saved `towards_victory_location_modifiers.txt` and `towards_victory_situations.txt` without UTF-8 BOM | Assumed BOM was only required for localization YAML; engine actually requires it on common/ .txt scripts as well | Always save common/ scripts with UTF-8 BOM (`utf-8-sig`); validate with `head -c 3 <file> \| xxd` -> `ef bb bf` |
| 2026-05 | Stored progress_pct as `score ÷ threshold` (e.g. `160 ÷ 2000`) expecting a float [0,1]; GUI progressbar showed 0% for all paths except science | `change_variable { divide }` is FLOOR integer division — `160÷2000=0`; progressbar default max=1, so integer 1 = 100% and integer 0 = 0% | Use integer scale [0,100]: divide by `threshold÷100` when threshold is divisible by 100, otherwise `multiply=100; divide=threshold`. Always set `max = 100` explicitly on the progressbar widget. |
| 2026-05 | Used `#Y[Country.MakeScope.GetVariable(...).GetValue\|0]#!` to gold-highlight an inline scripted variable in a localization string | Assumed `#Y` is a self-contained tag; when the variable resolves to a digit (e.g. 64), the engine reads `#Y64` as the tag name — `Unknown formatting tag 'y64!'` | Use plain `[variable_expression]` without color, OR add a space separator: `#Y [variable_expression]#!` (leading space becomes visible content). Never put `[` directly after a color tag. |
| 2026-05 | Proposed `INJECT:printing_press_advance = { allow = { has_variable = tv_advance_printing_press_unlocked } }` to gate a vanilla advance | Assumed INJECT could add a second allow block; vanilla advances support only ONE allow block | When vanilla advance already has an allow block, use `REPLACE:advance_name = { <full vanilla properties> allow = { OR = { <mod condition> <original condition> } } }`. Use INJECT only when the advance has no existing allow block. |
| 2026-05 | Used `text = TV_CONQUEST_M1_TRIGGER_DESC` in `custom_description` trigger blocks with only a YAML localization entry | Assumed a YAML key suffices for `custom_description`'s `text`; engine actually validates against `common/trigger_localization/` at load | Create an entry in `src/in_game/common/trigger_localization/`: `KEY = { global = KEY }`. The YAML key remains; trigger_localization is the bridge the engine requires. Error: `'No trigger loc KEY'` at startup. |
| 2026-05 | Wrote trigger_localization entries as `KEY = { global = KEY }` only, for milestones whose trigger has `custom_tooltip` nested inside `custom_description` | Assumed `global` alone was sufficient; engine also requires `first` (and `none`, `third`) perspectives when nested `custom_tooltip` is present | Use all four perspectives: `KEY = { none = KEY  global = KEY  first = KEY  third = KEY }`. Use this form for every trigger_localization entry as a safe default. Error: `'(BUG: KEY missing perspective. Could not find parameters for PROMOUN first Negative required false)'` at runtime. |
| 2026-05 | Used `value = leader_country.var:tv_arts_exhibition_leader_char.artist_skill  multiply = 0.002` assuming `artist_skill` was an integer 0–100 | Design doc assumed raw integer skill; engine actually normalizes `artist_skill` to a 0.0–1.0 float before exposing it to scripted values | Treat `artist_skill` as a 0–1 float in all scripted value math. Scale multipliers accordingly: the old design-intent `skill × 0.002` (for 0-100) becomes `skill × 0.2` (for 0-1). Then balance as needed. |
| 2026-05 | Would have used `artist_skill_modifier` as a character modifier key for boosting artist skill | Guessed modifier name by analogy; `artist_skill_modifier` does not exist in modifier_type_definitions | Step 3 verified: use `artist_skill_level_gain = X` (`already_percent = yes`). Source: `00_modifier_types.txt`, `03_artist.txt`. |
| 2026-05 | Proposed `multiply_variable = { name = X value = Y }` and `divide_variable = { name = X value = Y }` | Guessed EU5 has separate multiply/divide variable commands by analogy | Neither command exists; use `change_variable = { name = X multiply = Y }` / `divide = Y`. Both accept `var:Z` references. Verified in `cmm_core_slider_setting_effects.txt:223`. |
| 2026-05 | Would have written `government = monarchy` in a trigger | EU4 carry-over; `government` trigger does not exist in EU5 | Correct syntax: `government_type = government_type:monarchy`. Government type IDs: `monarchy`, `republic`, `theocracy`, `tribe`, `steppe_horde`. Source: `00_default.txt`. |
| 2026-05 | Used `add_treasury = -200` to deduct gold in a generic action effect | EU4 carry-over; `add_treasury` does not exist in EU5 | Use `add_gold = -200` (literal) or `add_gold = { value = script_value multiply = N }`. Trigger: `gold >= 200` (literal integer) is valid. Error: `Unknown effect add_treasury`. |
| 2026-05 | Used `trigger_event = { id = X }` in scripted_effects / on_action files | Assumed `trigger_event` is the universal event-fire effect; it does not exist outside event `option = { }` blocks | Use `trigger_event_non_silently = { id = X }` (shows popup to player) or `trigger_event_silently = X` (background). Engine error: `jomini_effect.cpp:556: Unknown effect trigger_event`. Source: `on_action_effects.txt:39`, `character_death_pulses.txt:57`. |
| 2026-05 | Used `datacontext = "[InternationalOrganizationsView.GetPlayer]"` inside `action_button_diamond` in IO organization panels; used `Country.MakeScope.GetVariable(...)` in visible expressions | Assumed `datacontext` was needed to give `Country` a country scope for variable lookup; did not check vanilla IO GUI patterns | Vanilla never sets `datacontext` on `action_button_diamond` in org panels — doing so breaks tooltip generation entirely (empty tooltip, button permanently grayed). Use `Player.MakeScope.GetVariable(...).IsSet` in visible expressions; `Player` is a global GUI binding that never requires a datacontext. Source: `defensive_league.gui:128`; `Player.MakeScope` verified at `religious_doctrine.gui:1831`. |
| 2026-05 | Used `can_start = { game_is_initialized = yes }` on `tv_victory_situation` | `game_is_initialized` = `current_date > 1337.5.1` (strict); EU5 starts on exactly 1337.5.x so the month-1 check fails; situation spawns in month 2 and becomes visible in month 3 | Use `can_start = { always = yes }` for permanent, non-popup situations with `monthly_spawn_chance_unique`. Source: `game_triggers.txt:58-60`. |
| 2026-05 | `ordered_in_global_list` ranks 2-5 in `tv_update_leaderboard_effect` accessed `situation:X.var:tv_rank_N_country` in `limit` without `has_variable` guards | pool was empty at `on_start`, rank-1 body never ran, `tv_rank_1_country` was unset; every pool entry in ranks 2-5 triggered a script error | Wrap each rank 2-5 pass in `if = { limit = { has_variable = tv_rank_{N-1}_country } ... }` so unset prerequisite ranks are skipped entirely. |
| 2026-05 | Rebuilt leaderboard ranks without clearing old `tv_rank_N_country` variables, then used `has_variable = previous_rank` as the only later-rank gate | stale rank variables survived after the current pool shrank; a later `ordered_in_global_list` pass could select no item, making `prev = none` and producing wrong-type/failed-var errors | Clear all rank variables at the start of each rebuild, ensure pool entries have numeric order_by variables, and guard rank N with `global_variable_list_size value > N-1`. |
| 2026-05 | Used `has_variable = tv_conquest_general_char` in `tv_govhouse_actions` allow, then read `var:tv_conquest_general_char = { is_alive = yes }` in a sibling `scope:actor` block | Assumed sibling trigger blocks in generic action `allow` would short-circuit; the UI evaluator still fetched the direct `var:` link and spammed errors when no Grand General existed | Use optional variable links for nullable variable reads: `var:X ?= { ... }`, `var:X ?= 1`, or `var:X ?= { this >= N }`. Move conditions to `potential` only when hiding the action is intended. |
| 2026-05 | Added a separate `tv_character_titles.txt` containing another `character_title_prefix = { ... }` block | Assumed customizable localization blocks merge additively across files; engine treats the top-level key as unique and ignores duplicates | Generate a full `character_title.txt` from vanilla and insert mod title entries into the original `character_title_prefix` block. Runtime log: `Duplicated key character_title_prefix will not be created`. Source: `character_title.txt:1`. |
| 2026-05 | Added `unique = yes` to `tv_arts_exhibition` IO type and used `international_organization:tv_arts_exhibition` + `is_member_of_international_organization = tv_arts_exhibition` in scripts | Assumed non-unique IO can be referenced by type name as a scope link; `tv_arts_exhibition` must NOT be unique because each country creates its own independent IO instance | NEVER add `unique = yes` to `tv_arts_exhibition`. Use `on_creation = { set_leader_country = scope:actor }` in the IO type for leader init. Use `every_international_organization = { limit = { type = X } }` to scope at runtime. Errors: `'key X does not lead to a unique international organization'`, `'Failed to find a valid event target link'`. |
| 2026-05 | Applied Chief Artist bonus to IO typed variable via `change_variable` in `monthly_country_pulse` on_action; bonus never appeared in the IO variable tooltip | IO typed-variable `monthly_change` is a scripted value that drives the tooltip; external `change_variable` calls are invisible to it | Put the contribution in `monthly_change` using `leader_country.var:X` chain (`value = leader_country.var:tv_chief_artist_monthly_bonus`). Store the computed value on the country in on_action for GUI display only. Set `leader_type = country` and call `set_leader_country` in `on_creation`/creation block. Source: `red_turban_rebellions.txt:3371` (root.var:X), `christian_tenets.txt:359` (leader_country.modifier:X). |
| 2026-05 | Used `var:tv_chief_artist ?= { set_local_variable { name = ca value = artist_skill } ... prev = { set_variable { value = local_var:ca } } }` to read a character's skill and store it on the country | `local_var` is not reliably propagated across `var:X ?= {}` / `prev = {}` scope switches — the value remains 0 | Use chained access from country scope: `set_variable = { name = tv_chief_artist_monthly_bonus  value = { value = var:tv_chief_artist.artist_skill  multiply = 0.002 } }`. Check liveness in the limit: `var:tv_chief_artist = { is_alive = yes }`. Source: `invite_artist.txt:129` (`add = scope:target.artist_skill`). |
