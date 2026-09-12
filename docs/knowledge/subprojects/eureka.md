# Eureka Subproject

## Scope

`src_eureka/` is a standalone mod for Eureka conditions attached to EU5
research projects (Advances). The current tested prototype is the `guilds`
Advance: a market-center condition activates a backend research-speed modifier
and a GUI progress visualization. `scripts_eureka/` owns GUI generation and
encoding helpers.

## Advance Feature Boundary

An Advance is represented across multiple surfaces, not only
`advances_lateralview.gui`: `technology_lateralview.gui`,
`advances_lateralview.gui`, `agenda_view.gui`, `hud_topbar.gui`, and shared
`advances_tooltips.gui`. Backend files under `src_eureka/in_game/common/advances/`,
scripted triggers/effects, and on-actions are part of the same feature.
Any Advance/Eureka display change must audit all listed surfaces before narrowing
the implementation and explicitly justify unchanged surfaces.

## Generator Ownership

`scripts_eureka/patch_gui_progress.py` reads vanilla GUI files, applies checked
anchored replacements, and writes the Eureka overrides. Regenerate it instead of
hand-editing generated GUI outputs. The complete verified surface map is in
`docs/knowledge/eureka_gui_maintenance.md` and the focused route card.

## Known Limits

The prototype currently implements `guilds`; manual creation of a market center
has no script-side hook, and CurrentResearch has no verified raw Advance-key
accessor for every GUI context. Treat these as confirmed limitations, not design
assumptions for unrelated advances.

## Validation

Run `scripts_eureka/patch_gui_progress.py`, then
`scripts/validate.py --changed --fix --ai-report` and `git diff --check`.
