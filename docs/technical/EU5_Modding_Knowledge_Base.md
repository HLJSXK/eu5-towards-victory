# European Universalis 5 Modding Knowledge Base

**Author:** Manus AI
**Date:** Jan 22, 2026

> **Note:** Generated 2026-01-22 as a baseline reference. May not reflect recent patches. Treat as background reading, not authoritative syntax — use `reference_official_defines/` and `reference_game_files/` to verify.

## 1. Introduction

European Universalis 5 (EU5), released in November 2025, is a grand strategy game developed by Paradox Development Studio. Built upon an updated version of the Clausewitz Engine and featuring the Jomini scripting layer, EU5 offers a powerful and flexible platform for modding. This document provides a comprehensive overview of the EU5 modding landscape, covering everything from fundamental concepts to advanced techniques, to serve as a foundational knowledge base for your modding projects.

## 2. Game Architecture

Understanding the technical foundation of EU5 is crucial for effective modding. The game's architecture is composed of two primary components: the Clausewitz Engine and the Jomini scripting layer.

*   **Clausewitz Engine**: This is the core game engine that handles the underlying systems, rendering, and performance. The version used in EU5 features significant improvements over its predecessors, including better multi-core support, which addresses some of the performance bottlenecks present in earlier Paradox titles like EU4. [1]
*   **Jomini Scripting Layer**: Jomini serves as an intermediate layer between the Clausewitz Engine and the game's content. It provides a standardized set of scripting tools and a scripting language that is shared across several modern Paradox titles, including Crusader Kings 3 and Victoria 3. This shared foundation means that experience with modding these other games is often transferable to EU5. [2]

## 3. Getting Started with Modding

This section outlines the initial steps to set up your development environment and create your first mod.

### 3.1. Development Environment

A proper development environment can significantly streamline the modding process. The recommended setup involves a source code editor with support for Paradox scripting languages.

| Editor                  | Recommended Extensions         | Notes                                                                 |
| ----------------------- | ------------------------------ | --------------------------------------------------------------------- |
| **Visual Studio Code**  | CwTools, Paradox Highlight     | Free, powerful, and the most popular choice for Paradox modding.        |
| **IntelliJ IDEA**       | Paradox Language Support       | Community Edition is free and offers robust features.                 |
| **Notepad++**           | (Custom Language File)         | A lightweight alternative, suitable for minor edits.                  |

### 3.2. Creating a New Mod

All mods are located in the `Documents/Paradox Interactive/Europa Universalis V/mod` directory. Each mod must have its own subfolder, which serves as the mod's root directory.

### 3.3. Debugging and Console Commands

EU5 includes a robust debug mode that is indispensable for mod development. To enable it, add the `-debug_mode` launch option in Steam. This provides access to the in-game console and enables hot-reloading, which applies script changes without restarting the game.

Key console commands for modders include:

*   `script_docs`: Generates documentation for effects, triggers, and scopes.
*   `dump_data_types`: Generates documentation for GUI scripting.
*   `error.log`: The primary log file for identifying script errors, located in `Documents/Paradox Interactive/Europa Universalis V/logs`.

## 4. Practical Mod Anatomy: A Community-Based Analysis

To supplement the theoretical concepts, an analysis was conducted on a sample of 16 community mods from the Steam Workshop. This analysis revealed common structures and best practices that serve as a practical guide for new modders. [3]

### 4.1. Standard Directory Structure

The analysis shows a consistent top-level directory structure. While only the `.metadata` directory is strictly mandatory, a typical mod utilizes several other folders to organize its content.

```
/my_mod_name
├── .metadata/          # (Mandatory) Contains metadata.json for the launcher
├── in_game/            # (Optional) Core gameplay files (scripts, events, GUI)
├── main_menu/          # (Optional) Localization and main menu graphics
├── loading_screen/     # (Optional) Custom loading screen assets
└── thumbnail.png       # (Optional) Preview image for the launcher
```

### 4.2. The `metadata.json` File

This file, located in the `.metadata` directory, is essential for the game to recognize and load the mod. It contains key information that is displayed in the game launcher.

| Key                      | Type    | Description                                                               |
| ------------------------ | ------- | ------------------------------------------------------------------------- |
| `name`                   | String  | The display name of the mod.                                              |
| `id`                     | String  | A unique identifier, often in the format `author.modname`. Can be empty.  |
| `version`                | String  | The version number of the mod (e.g., "1.0.0").                            |
| `supported_game_version` | String  | The compatible game version (e.g., "1.0.7" or "1.*.*").                   |
| `short_description`      | String  | A brief description, which can include BBCode for formatting on Steam.    |
| `tags`                   | Array   | A list of strings categorizing the mod (e.g., "Gameplay", "Graphics").    |
| `relationships`          | Array   | A list of mod dependencies. Usually empty for standalone mods.            |
| `game_custom_data`       | Object  | Contains game-specific flags, such as `"multiplayer_synchronized": true`. |
| `picture` / `thumbnail`  | String  | The filename of the mod's preview image (e.g., "thumbnail.png").        |

### 4.3. Content Directory Deep Dive

The `in_game` and `main_menu` folders are the heart of most mods, containing the files that alter game content.

*   **/in_game/**: This folder mirrors the game's own file structure for core mechanics. The most frequently used subfolder is `common`, which houses scripts for a vast array of game features, from government reforms to unit types.
*   **/main_menu/**: This folder primarily contains `localization` files, which handle all in-game text, and `gfx` files for custom graphics and interface elements.

#### International Organization Icons

The shared IO UI calls `InternationalOrganization.GetIcon` in common organization panels and tooltips. For a mod-defined international organization, provide a DDS file at:

```
main_menu/gfx/interface/icons/international_organizations/<io_type>.dds
```

The filename should match the `common/international_organizations` type key, such as `tv_arts_exhibition.dds`. Without this matching texture, shared UI surfaces fall back to the generic international organization icon even if a custom organization panel displays another texture locally.

#### Country Interaction Potential Scope

In `common/country_interactions`, `potential` documents the acting country as `scope:actor`. Do not put country-scoped IO membership iterators directly under `potential`; wrap them in `scope:actor`:

```pdx
potential = {
    scope:actor = {
        any_international_organizations_member_of = {
            international_organization_type = international_organization_type:tv_diplomatic_alliance
            leader_country ?= scope:actor
        }
    }
}
```

Direct `any_international_organizations_member_of` under `potential` can evaluate from an invalid root and log inconsistent trigger scopes (`invalid vs. country`). Vanilla `bribe_voter_for_policy` uses `scope:actor = { any_international_organizations_member_of = { ... } }` in its country interaction potential.

#### International Organization Monthly Effects and Tooltips

The shared IO tooltip can render visible children of an IO type's `monthly_effect` block. For internal monthly maintenance such as state repair, variable smoothing, member cleanup, or cached GUI refreshes, wrap the logic in `hidden_effect`:

```pdx
monthly_effect = {
    hidden_effect = {
        # maintenance logic
    }
}
```

Vanilla IOs such as HRE and Union use this pattern. Keep `monthly_change` entries visible when the player should see an IO variable's monthly breakdown; use `hidden_effect` for non-player-facing `monthly_effect` logic.

`monthly_change` is evaluated from the IO variable's international-organization context. Do not reuse country-scoped scripted triggers there if they depend on `root.var:X`; nesting the call inside `leader_country ?= { ... }` does not make `root` become the country. Instead, keep country-state checks inside `leader_country ?= { ... }` and perform IO-variable comparisons from the IO scope, for example `var:stockpile >= leader_country.var:monthly_cost`.

#### International Organization Trigger Iterators

In scripted triggers, `any_international_organizations_member_of` is a trigger iterator. Put IO filters directly in the iterator block:

```pdx
any_international_organizations_member_of = {
    international_organization_type = international_organization_type:tv_arts_exhibition
    resolution_is_active = resolution:policy_vote
}
```

Do not add an effect-style `limit = { ... }` block here. The engine treats `limit` as a trigger clause in this context and logs `Unknown trigger type: limit`. Reserve `limit = {}` for effect iterators such as `every_international_organizations_member_of` when applying effects.

#### Random List Branch Filtering

Use `trigger = { ... }` inside weighted `random_list` branches when a branch should only be eligible under some condition:

```pdx
random_list = {
    1 = {
        trigger = { has_variable = candidate_a }
        set_variable = selected_a
    }
}
```

Do not use `modifier = { factor = 0 ... }` as the branch filter. Vanilla random-list examples use branch `trigger` blocks. For player-facing rerolls, exclude the current result inside the same trigger so repeated same-day clicks cannot visibly return the same option, e.g. `NOT = { var:current_demand ?= 12 }`.

#### International Organization Header Controls

The standard `organization_panel_default_header` shows the lower IO information row through `abilities_widget`, which vanilla overrides to `ios_information_header = {}`. When adding compact IO-specific status text or header action buttons, prefer the exposed `ios_information_header_content_extra_1`, `ios_information_header_content_extra_2`, or `ios_information_header_content_extra_3` blocks with `ios_header_content_extra_template`.

Do not rely on `blockoverride "country_header_extra"` for visible interactive controls in this standard IO header path. That slot sits outside the `country_government_character` / `ios_information_header` row and can be absent from the visible UI bounds or hidden behind the rendered character/header content. If replacing the whole lower row is necessary, override `abilities_widget` directly and preserve `ios_information_header` inside the replacement.

#### International Organization Custom Tab Scroll Areas

The shared organization panel's `organization_custom_content` slot is already inside an inner vbox with `margin_top = 5`, followed by an `expand` spacer. For dynamic custom tabs that can grow past the visible area, inject the `scrollarea` directly into `organization_custom_content` instead of wrapping it in another child vbox. Override the block's `margin_top`/`spacing` when the content must sit flush to the tab top. For a bounded viewport, give the scrollarea a fixed size such as `size = { 100% 430 }`; when the tab must consume the full IO pane instead of leaving the common trailing `expand` spacer to own the lower area, set the custom-content block itself to `layoutpolicy_vertical = expanding` and set the scrollarea to `using = layoutpolicy_expanding`. In both cases, let the `scrollwidget` content establish natural height with `layoutpolicy_vertical = fixed` and `ignoreinvisible = yes`. Avoid `autoresizescrollarea` for this pattern: when active state adds more cards, it can grow the viewport with the content, leaving no useful overflow and causing the scrollarea bounds to sit lower inside the wrapper. `margin_top` directly on `scrollarea` is ignored by the engine and logs an unsupported-property error.

#### International Organization Law Block Scopes

For policies under `type = international_organization` laws, scope depends on the policy sub-block. The law readme documents policy `allow` as country root, while `on_activate` / `on_deactivate` use the entity the policy applies to. In practice, IO policy execution blocks should treat the current scope as the IO when mutating IO variables or checking IO policies:

```pdx
allow = {
    international_organization_has_policy = policy:previous_level
    var:tv_alliance_cohesion >= 25
}

on_activate = {
    change_variable = { name = tv_alliance_cohesion add = -25 }
    leader_country = {
        change_variable = { name = tv_alliance_tier add = 1 }
    }
}
```

Do not wrap those checks/effects in `scope:recipient = { ... }` unless the specific block documents `scope:recipient`. Runtime errors such as `Undefined event target 'recipient'` and `Event target link 'scope' returned an unset scope` can be caused by generated IO policies that use `scope:recipient` inside policy `allow`, `on_activate`, or `on_deactivate`.

`scope:recipient` is documented for IO policy AI math blocks such as `wants_this_policy_bias`, `wants_propose_policy`, `wants_keep_policy`, `reasons_to_join`, and `diplomatic_capacity_cost`, where root is a country and recipient is the IO. In custom non-unique IO laws, the engine can still pre-evaluate these maths without a recipient event target. Guard direct recipient reads with `exists = scope:recipient` in the same `limit` block, or use optional `scope:recipient ?= { ... }` for trigger-only checks, before reading `scope:recipient.leader_country` or IO variables.

`generic_action_ai_lists` potentials use the evaluating country as root. Inside `any_international_organizations_member_of`, `this` is the iterated IO, so `leader_country = this` compares a country to an international organization and logs a type-mismatch error. Use `exists = leader_country` plus `leader_country = root` for leader-only action lists.

#### International Organization Law Votes and Special Status Power

For an IO law system that routes policy changes through the parliament UI, the parliament type and the laws are only part of the setup. `requires_vote = yes` on the law and `uses_parliament_for_law_votes = yes` on the parliament type start the policy vote flow, but vote eligibility is driven by special status power.

Create an entry under `common/international_organization_special_statuses`, list that status in the IO type's `special_statuses_implemented`, give the status a `special_status_power`, and enable a matching `<status>_can_participate_in_parliament = yes` modifier in the IO parliament type. The matching modifier type belongs in `main_menu/common/modifier_type_definitions` with `game_data = { category = internationalorganization }`.

Vanilla `policy_vote` checks `country_combined_special_status_power(scope:recipient) > 0` for IOs using parliament law votes. If no implemented special status supplies voting power, a law debate may begin but the IO parliament page has no voter group to display.

Custom IO parliament sessions also need at least one valid `common/parliament_agendas` entry for the participating special status. Define it with `type = international_organization` and `special_status = <status>`, with `potential`/`allow` that pass for the IO. Otherwise the parliament UI can report that no special status wants to propose an issue even when valid `parliament_issues` exist.

For single-member or founder-only IOs, do not use the vanilla `call_organization_parliament` issue picker for support-token meetings. Even with a leader/founder special status, the picker can still report that no special status wants to propose an issue, and `propose_parliament_issue` initializes support from the issue special status before marking the proposer as voting yes. Redesign the mechanic before enabling custom support meetings for a founder-only IO.

The shared IO panel does not expose a real `organization_parliament_tab_visible` override block. In `panels/organization/common.gui`, the parliament tab's `visible` property is bound directly to `InternationalOrganizationsView.GetInternationalOrganization.HasParliament`. To hide the parliament tab for an IO, set `has_parliament = no` on the IO type. Law `requires_vote` behavior is separate and should follow the mechanic's design.

### 4.4. Common File Types and Formats

Modders primarily work with a few text-based file formats:

| Extension | Purpose                                  | Notes                                       |
| --------- | ---------------------------------------- | ------------------------------------------- |
| `.json`   | Metadata                                 | Used for `metadata.json`.                   |
| `.txt`    | Game Scripts (Events, Decisions, etc.)   | The primary format for scripting game logic.  |
| `.yml`    | Localization                             | Must be saved with **UTF-8-BOM** encoding.  |
| `.gui`    | User Interface Layouts                   | Defines the structure and look of UI windows. |

### 4.5. Observed Best Practices

The community analysis highlighted several best practices for creating clean, compatible, and maintainable mods:

*   **Avoid Overwriting Vanilla Files**: Instead of editing game files directly, create new files with unique names. This prevents conflicts with other mods and game updates.
*   **Use Prefixes**: Prefixing filenames with a unique identifier (e.g., `my_mod_events.txt`) helps organize files and prevent name collisions.
*   **Isolate Content**: Keep all mod files within the mod's designated folder. Do not place files in the main game directory.
*   **Manage Load Order**: For files that must override others, use numbered prefixes (e.g., `00_`, `01_`) to control the order in which the game loads them.
*   **Use Version Control**: Employ tools like Git to track changes, collaborate with others, and revert to previous versions if needed.

## 5. Core Modding Concepts

EU5's scripting language revolves around a few core concepts: Triggers, Effects, and Scopes.

### 5.1. Triggers and Effects

*   **Triggers** are conditions that check the current game state. They are used to determine if an event can fire, an option is visible, or a decision can be taken. Triggers return a boolean value (true or false). [4]
*   **Effects** are commands that change the game state. They are used to apply modifiers, change country ownership, create characters, and more. [5]

Both triggers and effects can be *inline* (for simple operations) or *block* (for more complex logic) and are highly dependent on the current **scope**.

#### `construct_building` Cost Multipliers

When `construct_building` uses `cost_multiplier`, EU5 requires a localized reason key:

```pdx
construct_building = {
    building_type = building_type:theater
    instant = yes
    cost_multiplier = 0
    cost_multiplier_reason = "game_concept_event"
}
```

Omitting `cost_multiplier_reason` logs: `No reason given for the cost multiplier in construct_building effect`. Vanilla event-funded construction commonly uses `game_concept_event`, which is already localized.

#### Dynamic Event Gold Costs

For country event options that should scale with the country's economy, vanilla uses:

```pdx
change_gold_effect = { scale = -3.5 }
```

The helper wraps `add_gold` and scales the value with `capital_wealth` and `country_economical_base`, with clamps for positive and negative results. Use fixed `add_gold = -N` only when a flat cost is the design intent. Example: vanilla `laws.0005` offers a free `research_progress_weak_bonus` (+2.5) option and a paid `change_gold_effect = { scale = -3.5 }` + `research_progress_severe_bonus` (+10) option.

#### Price Definitions and Cost Modifiers

Mod-defined prices in `in_game/common/prices/` are not complete by themselves. For each price key, EU5 looks for a matching modifier type named `<price_key>_cost_modifier`.

```pdx
my_action_price = {
    scaled_gold = 3.5
}

my_action_price_cost_modifier = {
    color = bad
    percent = yes
    game_data = {
        category = country
    }
}
```

Define the modifier type in `main_menu/common/modifier_type_definitions/`, and localize all three keys in every supported language: `my_action_price`, `MODIFIER_TYPE_NAME_my_action_price_cost_modifier`, and `MODIFIER_TYPE_DESC_my_action_price_cost_modifier`. If the modifier type is missing, the engine logs `Missing modifier type for price. <price_key>_cost_modifier`.

#### Character Static Modifiers for Commander Effects

Character-scoped static modifiers can carry military leader effects. Vanilla examples include `general_mil` with `discipline` and `army_movement_speed`, and `horde_battle_plans` with `military_tactics` and `army_movement_speed`. General traits also use the same modifier types.

For an effect that should follow a specific appointed commander, define the static modifier with character game data and apply it in character scope:

```pdx
my_general_tactic = {
    game_data = {
        category = character
    }
    discipline = 0.05
    army_movement_speed = 0.10
}

var:my_general_char ?= {
    add_character_modifier = { modifier = my_general_tactic years = -1 mode = replace }
}
```

Use a country modifier only when the design intentionally grants the bonus country-wide and independently of the active commander.

Governor's House War Tent tactics are a documented exception. Their stored-general character modifier path did not make the combat bonuses take effect, so the feature intentionally applies `tv_govhouse_tactic_*` as country-scoped modifiers and comments that this is a gameplay approximation. Do not convert that specific system back to `add_character_modifier` unless a new active-commander implementation is verified at runtime.

### 5.2. Scopes and Scope Links

A **scope** refers to the specific game object (e.g., a country, a character, a location) that a script is currently focused on. **Scope links** are used to access data from or apply effects to other scopes. For example, `c:FRA.gold` would access the treasury of the country with the tag FRA.

#### `root` vs `prev` in reusable country triggers

Do not assume `root` is the country just because a scripted trigger is country-scoped. `root` stays the root scope of the caller. If a country trigger is called from a situation `every_country` block, the current country is `this`, but `root` can still be the situation.

Inside nested iterators such as `any_market_with_merchants`, use `prev` to refer back to the country being checked. This matters for target triggers such as:

```pdx
any_market_with_merchants = {
    most_powerful_merchant = prev
    count >= 5
}
```

The GUI can hide this bug: `ShowTriggerConditions('trigger_name', PlayerScope.Self)` evaluates with the player country as root, while the monthly situation checker may evaluate the same trigger with situation root. A milestone can therefore show all conditions green in the panel but never grant the node unless nested country references use `prev` or an explicit saved scope.

### 5.3. Script Values

Script values are used for mathematical calculations and creating dynamic numerical values. They can be defined as reusable named values in the `common/script_values/` folder or created inline within other scripts. They support a wide range of arithmetic and logical operators. [6]

#### Scope Navigation in Script Values — `location.` prefix rule

Script values always execute in the scope they are *called from*, not from the scope implied by their name prefix. The `location.` prefix is a **scope navigation link** that transitions from an outer scope (pop, character, market, etc.) *to* a location. This means:

- **Correct — pop-scope value calling a location-scope value:**
  ```
  sol_alcohol_demand_scale = {   # runs in pop scope
      add = location.local_nobles_alcohol_demand_scale   # navigate to location
  }
  ```
- **Correct — location-scope value referencing other location variables:**
  ```
  local_nobles_alcohol_demand_scale = {   # runs in location scope
      value = local_nobles_savings_pressure   # already in location scope — no prefix
      multiply = local_noble_gdp_per_capita_display
  }
  ```
- **WRONG — using `location.` inside a location-scope value:**
  ```
  local_nobles_alcohol_demand_scale = {
      value = location.local_nobles_savings_pressure   # ERROR: already in location scope
  }
  ```
  Engine error: `Event target link 'location' did not get a matching scope type. Expected 'character, pop, …', but got 'location'`

### 5.4. Generic Action `select_trigger` Pre-evaluation

When a generic action has multiple `select_trigger` steps, EU5 **pre-evaluates the `effect` block at each step** before the user finishes all selections:

- After step 1 completes, the first `target_flag` scope (e.g. `scope:target`) is set but subsequent ones (`scope:target_1`) are not.
- At step 2 display time, the engine may evaluate the effect with `scope:target` set to the selected character — but any variables that the effect itself would write (e.g. `tv_governed_region`) do not yet exist on that character.

**Required guards:**

1. Wrap the entire effect body in an existence check for all required named scopes:
   ```
   if = {
       limit = {
           exists = scope:target
           exists = scope:target_1
       }
       # ... actual effect body
   }
   ```
2. Within scripted effects called by the action effect, use `?=` on any variable access that may be absent on a freshly selected character:
   ```
   var:tv_governed_region ?= {   # silently skipped if character has no tv_governed_region yet
       every_location_in_region = { ... }
   }
   ```

The `exists = scope:<name>` trigger is the vanilla pattern for this (confirmed in `assign_governor.txt` and `assume_fort_command.txt`). The errors appear in `error.log` as "Undefined event target" or "Failed to fetch variable" but the effect still fires correctly once all selections are complete.

#### Generic Action AI Lists

Every generic action should be explicitly listed in `in_game/common/generic_action_ai_lists/`. Vanilla's readme says unlisted actions are put into the global list, and EU5 logs a performance warning such as `Action X is not explicitly listed in an ai list!`.

Use the AI list `potential` block to restrict evaluation to countries that can use the feature. Player-facing actions should still be listed; set restrictive AI behavior such as `ai_will_do = { add = -100 }` when the AI should never execute them.

#### Generic Action Message Types

Generic actions also need notification message types in `main_menu/gui/messagetypes.txt`. This project keeps those entries in `scripts/gen_messagetypes.py`; after adding a new generic action, add a `PERFORM_<action_id>_ACTION` block there and rerun the script.

Each message type should have matching localization keys in every supported language:

```yaml
PERFORM_my_action_ACTION_SETUP: "When this action is performed."
PERFORM_my_action_ACTION_LOG: "The action was performed."
PERFORM_my_action_ACTION_MAP: ""
```

If the message type block is missing, the engine logs `Failed to find message type: PERFORM_<action_id>_ACTION`.

### 5.5. Variable Arithmetic (`change_variable`)

EU5 does **not** have `multiply_variable` or `divide_variable` commands. All in-place variable arithmetic uses `change_variable` with a named operator:

```pdx
change_variable = { name = my_var multiply = 100 }        # literal number
change_variable = { name = my_var divide = var:other_var } # variable reference
change_variable = { name = my_var multiply = var:factor }  # variable reference
change_variable = { name = my_var add = country_tax_base } # country scope property
```

Confirmed: `multiply = var:X` and `divide = var:X` are both valid (verified `cmm_core_slider_setting_effects.txt:223`).

`change_variable` does not accept `value =`. Use `set_variable = { name = my_var value = 1 }` for absolute assignment, and use `change_variable = { name = my_var add = 1 }` (or `subtract`, `multiply`, `divide`) for arithmetic. Using `value =` inside `change_variable` logs `Failed to read 'value' for 'change_variable'`.

#### Cross-Scope Numeric Variables

Do not use `prev.var:X` as the numeric right-hand side of comparisons or arithmetic after entering another scope. It can work as a scope reference, but in numeric contexts it may log errors such as `Invalid right side during comparison 'var'` and make the condition fail.

For trigger comparisons, use `root.var:X` only when `root` is verified to be the original numeric owner:

```pdx
var:stockpile ?= {
    this >= root.var:monthly_cost
}
```

For effect iterators, capture the number before switching scope and use the local variable inside the iterator:

```pdx
set_local_variable = { name = monthly_cost value = var:monthly_cost }
every_international_organizations_member_of = {
    change_variable = { name = stockpile subtract = local_var:monthly_cost }
}
```

### 5.6. Ordered Global List Rebuilds

When using `ordered_in_global_list` to build rank 1..N outputs, treat the output variables as a fresh snapshot each time:

1. Clear all old rank variables before rebuilding.
2. Rebuild the pool and ensure every pool entry has the numeric variables used by `order_by`.
3. Guard rank N with `global_variable_list_size = { name = pool value > N-1 }` before running the ordered pass.

Do not rely only on `has_variable = previous_rank`. That may be a stale output from a previous rebuild. If the current pool has fewer candidates, a later ordered pass can execute with no selected item; `prev` becomes `none`, producing wrong-type errors when stored with `set_variable`, and adjacent `var:` reads may also log failed fetches.

### 5.7. Government Type Trigger

EU5 does **not** have the EU4 `government = monarchy` trigger. Use:

```pdx
government_type = government_type:monarchy       # in a trigger block
```

Valid government type IDs (source: `00_default.txt`):

| ID | Description |
|---|---|
| `monarchy` | All monarchy forms |
| `republic` | All republic forms |
| `theocracy` | All theocracy forms |
| `tribe` | Tribal nations |
| `steppe_horde` | Steppe horde nations |

Monthly government power variables (for use in `set_variable = { name = X value = legitimacy }` etc.):

| Government | Variable |
|---|---|
| monarchy | `legitimacy` |
| republic | `republican_tradition` |
| theocracy | `devotion` |
| tribe | `tribal_cohesion` |
| steppe_horde | `horde_unity` |

### 5.8. Optional Location Rank Checks In Selectors

Generic action selectors can repeatedly evaluate `visible` and called `effect` logic while the selection window is open. In that context, location iterators such as `any_neighbor_location` may visit objects that do not have a valid `location_rank`. A direct check such as:

```pdx
any_neighbor_location = {
    location_rank = location_rank:city
}
```

can log `Event target link 'location_rank' returned an invalid object`. Use optional rank comparisons instead:

```pdx
my_location_is_city_trigger = {
    location_rank ?= location_rank:city
}
```

Do not rely on `trigger_if = { limit = { is_land = yes } ... }` to protect a direct `location_rank = ...` read in selector/tooltip contexts; the evaluator may still prefetch the direct link.

## 6. Game Content Modding

This section covers the modding of specific game content types.

### 6.1. Events

Events are pop-up messages that present the player with information and choices. They are defined in `.txt` files within the `in_game/events/` folder. Unlike EU4, EU5 does not use `mean_time_to_happen` for events; all events must be fired explicitly through on_actions, decisions, or other scripts. [7]

#### Event Option Tooltips

When hovering over an option button, the tooltip is rendered by `ContextualTooltipType` (defined in `eventwindow.gui`). It has two parts:

- **Title line**: `EventOption.GetText` — returns the option's `name` field as a plain string, **not** resolved through the localization system in this context. In debug mode this shows the raw key (e.g., `my_event.1.option_a`). This is expected behavior; vanilla options behave identically.
- **Content**: `EventOption.GetTooltip` — shows the output of any `custom_tooltip` entries inside the option block.

To add meaningful hover content, use `custom_tooltip = <key>` explicitly inside the option block and define the key in the localization file. The `.tt` suffix (e.g., `my_event.1.a.tt`) is a community convention — it must be referenced via `custom_tooltip`, it is **not** picked up automatically.

```
# event file
option = {
    name = my_event.1.a
    custom_tooltip = my_event.1.a.tt
    ...
}

# localization file
my_event.1.a: "Option button text"
my_event.1.a.tt: "Tooltip description shown on hover."
```

Event options may also pre-evaluate their `effect` stack while building tooltips. Do not assume a `set_variable` earlier in the option or in a called helper is committed before a later visible helper reads that variable. If an option sets `X` and then calls code that compares `var:X`, wrap the state-changing/application sequence in `hidden_effect = { ... }`, or guard the reusable helper with `has_variable = X` before direct `var:X` comparisons. For option triggers that read optional variables, prefer `var:X ?= N`.

Generic action widgets can hit the same problem while the action card or tooltip is merely visible. If an action effect initializes variables and then calls a visible helper that compares those same variables, action hover pre-evaluation may read them before the initialization is committed. Hide action widgets until their prerequisite state exists, repeat important prerequisites inside the action effect, and write reusable helpers with `var:X ?= ...` or threshold-style comparisons instead of direct reads of values that are only set earlier in the same chain.

#### Scripted Effects That Change IO Variables

If a reusable `scripted_effect` changes an International Organization type variable and callers need to show the gain/loss in their option or action tooltip, do not leave the IO-scope `change_variable` bare inside the helper. Wrap the real effect in `custom_description` and register that `text` key under `in_game/common/effect_localization/`.

Vanilla uses this pattern for HRE, Middle Kingdom, and Catholic Church authority helpers:

```txt
custom_description = {
    text = change_imperial_authority_text
    value = $value$
    change_variable = {
        name = imperial_authority
        add = $value$
    }
}
```

The `effect_localization` entry maps the custom description to perspective-specific localization keys, including negative variants. The player-facing strings still live in `main_menu/localization`. This lets a scripted effect call display the signed IO variable change while executing the real `change_variable`.

For generic action or event hover contexts, keep the third-person effect localization strings self-contained. The GUI can pre-evaluate `custom_description` text before a `COUNTRY` promote target exists, so strings such as `[COUNTRY.GetName] gains ...` in `third` or `third_past` perspectives can spam `COUNTRY.GetName` data errors while the user hovers an action button. Prefer neutral strings such as `Gains $VALUE|+$ #Y $var$#!`.

#### Event-Created Artwork

For event-created named artworks, do not rely on `create_art` with only `artist` and `quality`. Vanilla named artworks specify both `type = work_of_art_type:<type>` and `key = <loc_key>` inside `create_art`, with the key localized in `main_menu/localization`. Without an explicit key, dynamically created works can end up unnamed; if the real `create_art` must branch by `artist_type`, use visible `if`/`else_if` branches so the actual creation effect appears in the option tooltip.

### 6.2. Countries

Countries are defined in two parts: a **country definition** file in `in_game/setup/countries/` that sets the tag, color, and culture, and a **country setup** file in `<top_folder>/setup/start/` that defines the starting situation, including owned provinces, capital, and ruler. [8]

### 6.3. Localization

All text displayed to the player is handled through the localization system. Localization files are in `.yml` format and must be encoded in **UTF-8-BOM**. Each language has its own subfolder and file naming convention (e.g., `_l_english.yml`). The system supports dynamic text, color formatting, and icons. [9]

Event localization scope variables can be read directly from script scopes such as `ROOT` and `THIS`:

```yaml
my_event.1.desc: "Current value: [ROOT.GetVariable('my_var').GetValue|0]"
```

Do not insert `MakeScope` after `ROOT` or `THIS` in event localization. `ROOT.MakeScope.GetVariable(...)` treats an already script-scoped object like a GUI object and can log `Could not find promote for 'MakeScope'` / `Failed converting statement`. Use `Country.MakeScope.GetVariable(...)`, `Location.MakeScope.GetVariable(...)`, and similar chains only when the starting object is a GUI-layer binding such as `Country`, `Location`, `Player`, or a typed view object.

#### Customizable Localization Database Keys

Customizable localization files under `in_game/common/customizable_localization/` are parsed as database entries keyed by the top-level block name. These keys are not additive merge blocks. For example, adding a second file with `character_title_prefix = { ... }` causes the engine to ignore the duplicate and log `Duplicated key character_title_prefix will not be created`.

To extend character title prefixes, generate or copy the full vanilla `character_title.txt` and insert custom `text = { ... }` entries into the existing `character_title_prefix` block instead of creating a separate same-key file.

## 7. Advanced Modding Topics

### 7.1. Interface (GUI) Modding

The user interface is highly moddable through `.gui` files. The system is modular, using templates and types to create reusable UI components. Creating new windows and widgets allows for the development of complex new game features. [10]

GUI `text = "KEY"` properties are localization lookups. If the key is missing from `main_menu/localization`, the engine logs `Unlocalized text 'KEY'` from `pdx_gui_localize.cpp`. Correct the key to one defined by the current data/localization set, add the key for all supported languages, or use `raw_text` only when the intended display is a literal string.

Custom game concepts require both localization and a definition in `main_menu/common/game_concepts/`. A localization pair such as `game_concept_tv_foo` / `game_concept_tv_foo_desc` does not create the concept by itself. If `[tv_foo|e]` is used before `tv_foo = { texture = "..." }` is registered, the localization parser treats `tv_foo` as a data-system function and logs `Could not find data system function 'tv_foo'`.

For ordinary localization keys such as building names, use `$key$` substitution instead of square-bracket game concept syntax. GUI-bound localized text can parse `[building_key|E]` as a data-system function when `building_key` is not registered as a game concept, producing `Could not find data system function '<key>'`.

GUI boolean helpers are arity-specific. `And()` and `Or()` take exactly two operands; for three operands use `And3()` / `Or3()` as vanilla GUI files do, and for larger expressions nest binary helpers. A three-argument `And(a, b, c)` logs `Function 'And' expected 2 arguments, got 3` and the widget statement fails conversion.

For fixed-position icon overlays, avoid percentage `position` values directly on `icon` widgets. In the Governor's House power-balance bar, `position = { 50% 0 }` on an `icon` rendered at the left edge instead of the midpoint. Use pixel positions when the parent has a fixed size, or position a `widget` wrapper with percentages and place the icon inside that wrapper. Vanilla percentage-position examples such as `progressbars.gui` use positioned `widget` wrappers.

The shared `situation_panel` template includes a default `situation_subheader_content` block with a 45px row. Custom situation panels that do not use a subheader should explicitly add `blockoverride "situation_subheader_content" {}` near the top of the panel. Vanilla situation panels such as `colonial_revolution.gui` and `council_of_trent.gui` use this empty override to avoid an unwanted blank band above the main content.

When a widget is a direct child of `hbox` or `vbox`, the box layout owns placement and sizing. Do not set `parentanchor` on those children, and do not use percentage components in their `size` values such as `size = { 97% 72 }`. Use `layoutpolicy_horizontal`, `layoutpolicy_vertical`, stretch factors, or non-percent fixed/min/max sizing instead. For `io_character_card` in an `organization_custom_content` block, vanilla panels rely on the type's built-in `layoutpolicy_expanding` rather than adding a percentage `size` or `parentanchor`.

Do not put paragraph-style localized text in an unconstrained `hbox` elastic column. A pattern like `hbox = { ... widget = { layoutpolicy_horizontal = expanding size = { -1 92 } text_single = { multiline = yes ... } } }` can let the text's natural width flow back into the row. In the Engineering Department IO, this made a child `vbox` expand to 548.3px while its parent card content was correctly bounded at 470px. Use a fixed-width text area, preferably a small card/container with `text_multi`, `max_width`, and `autoresize`:

```gui
widget = {
    size = { 368 92 }
    using = bg_text_mask_container_dark_blue
    vbox = {
        margin = { 8 8 }
        text_multi = {
            max_width = 352
            autoresize = yes
            text = "MY_PARAGRAPH_LOC_KEY"
            align = nobaseline|left
        }
    }
}
```

Vanilla IO header help text uses the same bounded `text_multi` pattern with `max_width` and `autoresize`.

Standalone `io_character_card` widgets inherit `character_entry` name sort highlights. Those highlights call `FilteredSortedList.IsKeyHoveredByWidgetName`, which only works when a `FilteredSortedList` datacontext exists. For cards shown in custom IO panels, situation panels, or other non-sortable contexts, override both inherited highlight blocks:

```gui
blockoverride "name_highlight" {}
blockoverride "character_entry_name_sort_by_highlight" {}
```

Vanilla `middle_kingdom.gui` applies these exact overrides with a comment that they block error log spam.

For GUI lists backed by a `datamodel`, each `item = { ... }` block is an item description, not a general layout container. It must contain exactly one top-level child widget and no direct properties. If a row needs both content and a divider, wrap both inside a single parent `vbox` or `widget`:

```gui
item = {
    vbox = {
        hbox = { }
        widget = { using = bg_divider_flavor_01 }
    }
}
```

Putting sibling widgets directly under `item` logs `Malformed item desc`, and can produce nearby text formatter noise while the list is rendered.

When embedding `RequirementsList` directly in a panel to show `ShowTriggerConditions(...)`, do not hide its title with an empty `blockoverride "block_title" {}`. The underlying list/header stack uses tooltip header text styling that reads `ExtraTooltipInfo.GetTintColor`; outside a real tooltip context, exposing that header can spam `No context supplied ... ExtraTooltipInfo.GetTintColor` while the panel is hovered. If the list should be titleless, preserve the nested title block and hide it explicitly:

```gui
blockoverride "block_title" {
    block "block_title" {
        visible = no
    }
}
```

### 7.2. Map Modding

EU5 includes a powerful map editor for modifying the game world. This tool allows for editing the heightmap, terrain textures, and location setup. However, it has high system requirements, recommending at least 32GB of RAM. [11]

### 7.3. Graphics Modding

Flags in EU5 are generated dynamically through a scripted coat of arms system, a significant change from the static `.tga` files of EU4. This allows for flags to change based on triggers and game conditions. [12]

## 8. Best Practices and Resources

*   **Float precision limit**: The EU5 engine reads float literals to a maximum of **5 decimal places**. Any digits beyond the 5th are silently truncated. Always round generated or hand-written values to ≤5 dp (e.g. `0.08477` not `0.084771`). This is particularly relevant for generated script_values such as budget shares and demand scales.
*   **Use a proper IDE**: Tools like VS Code with the CwTools extension can catch errors and improve readability.
*   **Avoid Overwriting Vanilla Files**: Create your own files and use the `replace_paths` feature or specific load orders to override game content. This improves mod compatibility.
*   **Use Version Control**: Git is an invaluable tool for tracking changes and collaborating with others.
*   **Consult Community Resources**: The official EU5 Wiki, the Paradox Forums, and community Discord servers are essential resources for any modder.

## 9. Conclusion

The modding architecture of European Universalis 5 represents a significant evolution from previous Paradox titles. With the power of the updated Clausewitz Engine and the flexible Jomini scripting layer, modders have an unprecedented ability to create new content and transform the game. While the learning curve can be steep, the extensive documentation and active community provide a strong foundation for success.

## 10. Building Types

### 10.1 Definition Structure

Buildings live in `in_game/common/building_types/`. Key fields verified against vanilla files (2026-05):

```
building_id = {
    is_foreign = no               # prevent foreign construction
    pop_type = clergy             # employment pop type
    max_levels = 1                # integer or scripted_int
    category = cultural_category  # see §10.2 for valid values
    expensive = yes               # UI flag only
    town = yes                    # location rank eligibility
    city = yes
    megalopolis = yes
    rural_settlement = no
    location_potential = { is_capital = yes }   # visibility filter; root = location
    country_potential = { ... }                 # country-level visibility; root = country
    allow = { ... }                             # construction conditions; root = location, scope:actor = building country
    build_time = large_capital_build_time       # time reference (NOT price = X)
    construction_demand = university_construction  # cost reference (NOT price = X)
    on_built = { ... }            # fires when construction completes; root = location
    on_destroyed = { ... }        # fires when building is removed
    remove_if = { ... }           # auto-destroy trigger; root = building
}
```

**Critical: EU5 uses `construction_demand = X`, NOT `price = X` (EU4 style).** Using `price =` is silently ignored.

**Modifier scope note:** `modifier` and `raw_modifier` are location effects. `capital_country_modifier` is a country modifier only when the building is built in the capital (verified in `reference_official_defines/types/building_types.txt`). For event-created buildings that may appear outside the capital, apply national effects separately with `add_country_modifier` and keep the building's own modifier local.

### 10.2 Valid Category Values

Confirmed from vanilla building definitions: `basic_industry_category`, `colonial_category`, `consumer_goods_category`, `cultural_category`, `defense_category`, `estate_category`, `government_category`, `infrastructure_category`, `military_category`, `naval_category`, `religious_category`, `rgo_building_category`, `trade_category`, `village_category`, `weapons_industry_category`.

For educational / scientific buildings: `cultural_category` (used by `university`, `library`, `art_school`).

### 10.3 Allow Block with custom_tooltip

The `allow` block uses `root = location`, `scope:actor = building country`. Custom tooltips wrap real triggers and display localized text when conditions pass (green) or fail (red):

```
allow = {
    custom_tooltip = {
        text = MY_TOOLTIP_KEY     # localization key
        scope:actor = { var:my_score_var ?= { this >= 100 } }
    }
    custom_tooltip = {
        text = MY_SECOND_TOOLTIP_KEY
        scope:actor = { var:my_prereq ?= { this >= 1 } }
    }
}
```

Multiple `custom_tooltip` blocks in `allow` are AND-combined. Each evaluates independently and shows its own green/red state. Source: `estate_buildings.txt`, `capital_buildings.txt`.

Do not use `has_variable = X` as a guard for `var:X = ...` inside generic action `allow` or tooltip logic. The UI evaluator may still fetch direct `var:` links from sibling trigger blocks while building tooltips. For nullable variables, use optional variable links (`var:X ?= ...`) so an absent variable returns false without logging an unset-scope error.

For custom generic-action buttons that call `construct_building`, do not rely on the building type's `max_levels` or a lone `can_build_building` check. Repeat the cap logic in a reusable trigger and call it from the action `allow`, any target picker `visible`/`enabled`, and the final effect guard. Country-wide caps should count queued construction with:

```
scope:actor = {
    total_building_levels_including_construction:my_building < 5
}
```

For one-per-location target pickers, also filter both existing and queued copies:

```
NOT = { has_building = building_type:my_building }
NOT = {
    any_buildings_in_location = {
        building_type = building_type:my_building
        building_levels_under_construction >= 1
    }
}
```

Otherwise the custom action can spend its scripted price while the final construction does nothing, especially from stale target lists or after the cap was reached by an in-progress level.

### 10.4 Actual Building Employment

`location_building_level(building_type:X)` reports completed levels, not current staffing. For mechanics that depend on actual workers, enter the building object from the location and read `building_employed_amount`:

```
scope:target_location = {
    ordered_buildings_in_location = {
        limit = { building_type = building_type:my_building }
        order_by = building_level
        max = 1
        scope:target_country = {
            set_variable = {
                name = my_actual_workers
                value = {
                    value = prev.building_employed_amount
                    multiply = 1000
                    floor = yes
                }
            }
        }
    }
}
```

`prev.building_employed_amount` is read from the building scope. Multiply by 1000 when the consuming mechanic stores people counts rather than pop-size units, as building `employment_size = 1` represents 1,000 workers in UI terms.

### 10.5 on_built Scope

`on_built` fires with root = location. Access the owning country via `location.owner = { ... }`. Source confirmed at `unique_buildings.txt:516-524` and `religion_buildings.txt:32-51`:

```
on_built = {
    hidden_effect = {
        location.owner = {
            set_variable = { name = my_var value = 1 }
            my_scripted_effect = yes
        }
    }
}
```

### 10.6 build_time References (verified)

| Reference | Context | Source |
|---|---|---|
| `large_capital_build_time` | Large government/capital buildings (royal court) | `capital_buildings.txt:15` |
| `guild_build_time` | Craft guilds | `common_buildings.txt:126` |
| `infrastructure_build_time` | Roads, irrigation | `common_buildings.txt:23` |
| `rural_build_time` | Rural production | `common_buildings.txt:218` |

### 10.7 construction_demand References (verified)

| Reference | Context | Source |
|---|---|---|
| `university_construction` | Universities, academies | `culture_buildings.txt:48` |
| `early_capital_building_construction` | Royal court, capital buildings | `capital_buildings.txt:56` |
| `village_construction` | Irrigation systems | `common_buildings.txt:32` |

## 11. Music

### 11.1 Music Player Tracks

EU5's exposed text-side music track database lives in `in_game/common/music_player_tracks/`.
The official type note and vanilla file both say new songs are first added in Wwise, then
registered by their Wwise event key. The text entry supports metadata only:

```
MusicPlayer_my_event_key = {
    composer = My_Composer_Key
    performer = My_Performer_Key
    soloist = My_Soloist_Key
}
```

Add matching `music_player_l_*.yml` localization for the track key, `<track>_flavour`,
and any composer/performer/soloist keys. The in-game music player GUI lists registered
track objects and plays them through `MusicPlayerTrack.Play`; current references do not
show EU4-style `songs.txt` trigger/chance rules for country, war, date, variable, or event
conditions.

Do not infer from this file that EU5 cannot trigger music. It can: vanilla GUI calls
`Audio_PlayEvent('mus_culture_track_start', 'music_manager')` when entering the game.
That is a Wwise/audio-manager event, not a `music_player_tracks` trigger rule. The
declare-war panel's visible button is a hardcoded `DeclareWarLateralView.GetDeclareWarAction`,
and `on_war_declared` is a hardcoded script hook with scopes for actor, recipient, and war.
If a mod needs conditional music, the verified routes are therefore:

- register the Wwise event key in `music_player_tracks` for player-visible metadata;
- trigger a Wwise music event from GUI with `Audio_PlayEvent(<event>, 'music_manager')`;
- use script hooks such as `on_war_declared` to set state or fire UI/events, then verify
  whether the desired audio event can be called from that context.

Current references still do not show a normal country/event effect that directly plays a
named music-player track by track key. The safe distinction is: `music_player_tracks`
registers tracks; Wwise/audio-manager events and hardcoded action hooks drive playback.

### 11.2 Audio Culture and Environment Tags

`main_menu/music/audio_culture_types/` defines audio culture archetypes such as
`european_sfx`, each with `priority` and `culture_tag`. Topography, vegetation, and some
climate definitions can provide `audio_tags`, which appear to feed ambient/environmental
audio selection rather than music-player song conditions.

## 12. References

[1] [Europa Universalis V - PC performance graphics benchmarks](https://en.gamegpu.com/test-gpu/rts-strategii/europa-universalis-v-test-gpu-cpu)
[2] [Grand Jomini Modding Information Manuscript](https://forum.paradoxplaza.com/forum/threads/grand-jomini-modding-information-manuscript.1170261/)
[3] Manus AI internal analysis of 16 EU5 mods from Steam Workshop, January 2026.
[4] [Mod structure - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Mod_structure)
[5] [Trigger - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Trigger)
[6] [Effect - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Effect)
[7] [Script value - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Script_value)
[8] [Event modding - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Event_modding)
[9] [Country modding - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Country_modding)
[10] [Localization - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Localization)
[11] [Interface modding guide - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Interface_modding_guide)
[12] [Map modding - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Map_modding)
[13] [Flag modding - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Flag_modding)
