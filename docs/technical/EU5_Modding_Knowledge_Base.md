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

### 5.2. Scopes and Scope Links

A **scope** refers to the specific game object (e.g., a country, a character, a location) that a script is currently focused on. **Scope links** are used to access data from or apply effects to other scopes. For example, `c:FRA.gold` would access the treasury of the country with the tag FRA.

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

### 5.4. Variable Arithmetic (`change_variable`)

EU5 does **not** have `multiply_variable` or `divide_variable` commands. All in-place variable arithmetic uses `change_variable` with a named operator:

```pdx
change_variable = { name = my_var multiply = 100 }        # literal number
change_variable = { name = my_var divide = var:other_var } # variable reference
change_variable = { name = my_var multiply = var:factor }  # variable reference
change_variable = { name = my_var add = country_tax_base } # country scope property
```

Confirmed: `multiply = var:X` and `divide = var:X` are both valid (verified `cmm_core_slider_setting_effects.txt:223`).

### 5.5. Government Type Trigger

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

### 6.2. Countries

Countries are defined in two parts: a **country definition** file in `in_game/setup/countries/` that sets the tag, color, and culture, and a **country setup** file in `<top_folder>/setup/start/` that defines the starting situation, including owned provinces, capital, and ruler. [8]

### 6.3. Localization

All text displayed to the player is handled through the localization system. Localization files are in `.yml` format and must be encoded in **UTF-8-BOM**. Each language has its own subfolder and file naming convention (e.g., `_l_english.yml`). The system supports dynamic text, color formatting, and icons. [9]

#### Customizable Localization Database Keys

Customizable localization files under `in_game/common/customizable_localization/` are parsed as database entries keyed by the top-level block name. These keys are not additive merge blocks. For example, adding a second file with `character_title_prefix = { ... }` causes the engine to ignore the duplicate and log `Duplicated key character_title_prefix will not be created`.

To extend character title prefixes, generate or copy the full vanilla `character_title.txt` and insert custom `text = { ... }` entries into the existing `character_title_prefix` block instead of creating a separate same-key file.

## 7. Advanced Modding Topics

### 7.1. Interface (GUI) Modding

The user interface is highly moddable through `.gui` files. The system is modular, using templates and types to create reusable UI components. Creating new windows and widgets allows for the development of complex new game features. [10]

Custom game concepts require both localization and a definition in `main_menu/common/game_concepts/`. A localization pair such as `game_concept_tv_foo` / `game_concept_tv_foo_desc` does not create the concept by itself. If `[tv_foo|e]` is used before `tv_foo = { texture = "..." }` is registered, the localization parser treats `tv_foo` as a data-system function and logs `Could not find data system function 'tv_foo'`.

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

### 10.2 Valid Category Values

Confirmed from vanilla building definitions: `basic_industry_category`, `colonial_category`, `consumer_goods_category`, `cultural_category`, `defense_category`, `estate_category`, `government_category`, `infrastructure_category`, `military_category`, `naval_category`, `religious_category`, `rgo_building_category`, `trade_category`, `village_category`, `weapons_industry_category`.

For educational / scientific buildings: `cultural_category` (used by `university`, `library`, `art_school`).

### 10.3 Allow Block with custom_tooltip

The `allow` block uses `root = location`, `scope:actor = building country`. Custom tooltips wrap real triggers and display localized text when conditions pass (green) or fail (red):

```
allow = {
    custom_tooltip = {
        text = MY_TOOLTIP_KEY     # localization key
        scope:actor = {
            has_variable = my_score_var
            var:my_score_var >= 100
        }
    }
    custom_tooltip = {
        text = MY_SECOND_TOOLTIP_KEY
        scope:actor = { has_variable = my_prereq; var:my_prereq >= 1 }
    }
}
```

Multiple `custom_tooltip` blocks in `allow` are AND-combined. Each evaluates independently and shows its own green/red state. Source: `estate_buildings.txt`, `capital_buildings.txt`.

### 10.4 on_built Scope

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

### 10.5 build_time References (verified)

| Reference | Context | Source |
|---|---|---|
| `large_capital_build_time` | Large government/capital buildings (royal court) | `capital_buildings.txt:15` |
| `guild_build_time` | Craft guilds | `common_buildings.txt:126` |
| `infrastructure_build_time` | Roads, irrigation | `common_buildings.txt:23` |
| `rural_build_time` | Rural production | `common_buildings.txt:218` |

### 10.6 construction_demand References (verified)

| Reference | Context | Source |
|---|---|---|
| `university_construction` | Universities, academies | `culture_buildings.txt:48` |
| `early_capital_building_construction` | Royal court, capital buildings | `capital_buildings.txt:56` |
| `village_construction` | Irrigation systems | `common_buildings.txt:32` |

## 11. References

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
