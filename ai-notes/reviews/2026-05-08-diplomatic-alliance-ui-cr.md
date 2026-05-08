# Diplomatic Alliance UI — CR

Reviewer: Claude Sonnet 4.5
Date: 2026-05-08
Scope: GPT-5.5 first UI pass for Diplomatic Alliance IO panel

## Verdict

Approve with notes. The file follows correct vanilla patterns and will likely load. Two P2 concerns flagged for in-game validation.

## Analysis

### 1. Panel Attachment — ✅ Correct

The file `tv_diplomatic_alliance.gui` uses `organization_geodiplomatic_theme = { ... }` as the top-level declaration. This matches the vanilla pattern where:
- The filename corresponds to the IO type name (e.g. `high_kingship.gui` → `high_kingship` IO)
- The engine uses filename matching to apply the correct GUI overrides per IO type
- Multiple files can declare the same theme without conflicting because only the matching file's overrides are applied at runtime

Our filename `tv_diplomatic_alliance.gui` correctly matches IO type `tv_diplomatic_alliance`.

### 2. GUI Expressions — ⚠️ P2 (needs in-game validation)

| Expression | Assessment |
|-----------|-----------|
| `InternationalOrganizationsView.GetInternationalOrganization.MakeScope.GetVariable('tv_alliance_cohesion').GetValue\|1` | Pattern matches vanilla situation panel usage (`SituationView.GetActiveSituation.GetSituation.MakeScope.GetVariable`). **However**, vanilla IO panels use `GetVariableText(Tag)` with engine-managed variables rather than `MakeScope.GetVariable` for script variables. May fail if the IO scope doesn't support `MakeScope`. |
| `InternationalOrganizationsView.GetInternationalOrganization.GetLeaderCountry.GetName` | Likely valid — `GetLeaderCountry` is used in vanilla `high_kingship.gui` context |
| `GetDataModelSize(InternationalOrganizationsView.GetInternationalOrganization.GetMembers)` | No vanilla precedent found for `GetDataModelSize()` function. Vanilla counts members by iterating. May not exist. |
| `country_flag_small` with IO leader datacontext | Reasonable pattern but no direct vanilla precedent for this specific combination |

**Recommendation:** If `MakeScope.GetVariable` fails on IO scope, the fallback is to store display values on the leader country and access them via `GetLeaderCountry.MakeScope.GetVariable(...)`. If `GetDataModelSize` fails, simply remove the member count display (it's non-essential).

### 3. Block Override Correctness — ✅ Correct

| Blockoverride | Exists in `common.gui` | Used by competing IO files? |
|--------------|----------------------|---------------------------|
| `organization_panel_left_header` | ✅ line 94 as `block` | HRE only (different theme: `organization_panel`) |
| `organization_panel_right_header` | ✅ line 119 as `block` | hindu_branch, sect (different theme: `organization_religious_theme`) |
| `organization_panel_extra_item` | ✅ line 183 as `block` | hindu_branch, sect (different theme) |
| `organization_overview_list_custom_top_extra` | ✅ (used in `high_kingship.gui`) | high_kingship, japanese_shogunate (same theme but different filename=different IO) |
| `organization_laws_tab_text` | ✅ (used in `japanese_shogunate.gui`, `swiss_confederation.gui`) | Same theme, different filename — no conflict |

No conflicts. All block names are valid template insertion points.

### 4. Information Completeness — ✅ Excellent

The 4 expandable cards cover all essential information:
1. **Alliance Status** — shows supporter count, cohesion, tier
2. **How to Progress** — explains cohesion growth, law costs
3. **Law Groups** — describes all 5 categories
4. **Victory Requirements** — lists M1-M5 conditions

This gives the player everything they need without overwhelming the panel.

### 5. Localization Quality — ✅

- English text is clear and concise
- Chinese text uses appropriate game terminology
- No key collisions (all keys use `TV_ALLIANCE_` prefix)
- All keys referenced in the GUI exist in both locale files

## P2 Items (in-game validation needed)

| # | Concern | How to test | Fallback |
|---|---------|-------------|----------|
| 1 | `MakeScope.GetVariable(...)` on IO scope | Load game with IO created; check if values display | Move values to leader country, use `GetLeaderCountry.MakeScope.GetVariable(...)` |
| 2 | `GetDataModelSize(...)` existence | Load game; check member count renders | Remove member count widget or use a hardcoded tooltip |

## Minor Suggestions (non-blocking)

- The `parentanchor = vcenter` on `hbox` inside `organization_panel_left_header` — per the known anti-pattern in BRIEF.md, `parentanchor` on hbox/vbox children may be ignored. Since this is the hbox itself (not a child of hbox), it should be fine, but verify in-game that the header aligns vertically as expected.
- Consider adding a `tooltip` to the cohesion/tier values showing growth rate or next threshold.

## Summary

**Approved.** The implementation follows vanilla patterns correctly, uses the right theme and filename convention, provides comprehensive player information, and has complete localization. The two P2 concerns are GUI expression validity questions that can only be resolved by loading the game.
