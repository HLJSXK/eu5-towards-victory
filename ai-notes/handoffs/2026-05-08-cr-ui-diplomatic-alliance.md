# Handoff: CR — Diplomatic Alliance UI

Date: 2026-05-08
Author: GPT-5.5
Scope: First dedicated UI pass for the Diplomatic Alliance international organization.

## What Changed

- Added `src/in_game/gui/panels/organization/tv_diplomatic_alliance.gui`
  - Uses `organization_geodiplomatic_theme`.
  - Adds a dedicated Diplomatic Alliance organization panel override.
  - Shows the advocator country in the subheader.
  - Shows key values in the subheader:
    - Alliance Cohesion: `tv_alliance_cohesion`
    - Alliance Tier: `tv_alliance_tier`
    - member count via `GetDataModelSize(InternationalOrganizationsView.GetInternationalOrganization.GetMembers)`
  - Adds overview cards explaining:
    - current alliance status;
    - how cohesion grows;
    - how law upgrades spend cohesion;
    - the five law groups;
    - Diplomatic Victory requirements from M1 to M5.
  - Reuses vanilla IO tabs and law/member/vote UI rather than rewriting the law vote system.

- Updated localization:
  - `src/main_menu/localization/english/tv_diplomatic_alliance_l_english.yml`
  - `src/main_menu/localization/simp_chinese/tv_diplomatic_alliance_l_simp_chinese.yml`
  - Added UI labels and explanatory text for the dedicated IO panel.

## Validation Run

- `python scripts/validate.py`
  - Result: `[OK] Validated 34 file(s) -- no issues found.`
- IDE lints reported no diagnostics for the edited GUI/localization files.

## CR Focus

Please review the UI from a game-loading and usability perspective.

1. **Panel attachment**
   - Confirm `src/in_game/gui/panels/organization/tv_diplomatic_alliance.gui` will be picked up for IO type `tv_diplomatic_alliance`.
   - Check whether `organization_geodiplomatic_theme = { ... }` is the correct top-level pattern for this custom IO type.

2. **GUI expression validity**
   - Check these expressions for engine support:
     - `InternationalOrganizationsView.GetInternationalOrganization.MakeScope.GetVariable('tv_alliance_cohesion').GetValue|1`
     - `InternationalOrganizationsView.GetInternationalOrganization.MakeScope.GetVariable('tv_alliance_tier').GetValue|0`
     - `InternationalOrganizationsView.GetInternationalOrganization.GetLeaderCountry.MakeScope.GetVariable('tv_diplomatic_support_count').GetValue|0`
     - `GetDataModelSize(InternationalOrganizationsView.GetInternationalOrganization.GetMembers)`
   - Confirm `country_flag_small` works with `datacontext = "[InternationalOrganizationsView.GetInternationalOrganization.GetLeaderCountry]"`.

3. **Block override correctness**
   - Confirm the following overrides exist and are appropriate for `organization_geodiplomatic_theme` / `organization_panel`:
     - `organization_panel_left_header`
     - `organization_panel_right_header`
     - `organization_panel_extra_item`
     - `organization_overview_list_custom_top_extra`
     - `organization_laws_tab_text`
   - Confirm multiple `card_expandable` entries in `organization_overview_list_custom_top_extra` render correctly.

4. **Information completeness**
   - Check whether the UI gives enough essential guidance:
     - how to gain cohesion;
     - how much each law level costs;
     - how law upgrades affect Alliance Tier;
     - how Alliance Tier gates Diplomatic Victory milestones;
     - what the five law groups represent.

5. **Localization quality**
   - Check English and Simplified Chinese text for clarity, consistency, and line length.
   - Confirm no localization key collisions or missing keys.

## Known Limits

- This pass intentionally does not add decorative assets or a full HRE-style reform map.
- The law UI is still the vanilla IO law tab. Dedicated law-route visualization can be a later enhancement if needed.
- In-game validation is still required to confirm the panel actually attaches and expressions render at runtime.
