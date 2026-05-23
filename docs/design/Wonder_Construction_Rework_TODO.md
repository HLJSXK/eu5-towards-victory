# Wonder Construction Rework TODO

> Working document for the large wonder-construction rework requested on 2026-05-23.
> Future agents must resume from this file after compact/handoff and must not skip, shrink, or silently reinterpret any item.

## Status Legend

- [ ] Not started
- [~] In progress
- [x] Done and locally validated
- [!] Blocked or needs explicit design decision

## Mandatory Workflow

- [x] Read `CLAUDE.md`.
- [x] Read `docs/knowledge/BRIEF.md`.
- [x] Run initial AI context command (`conda run --no-capture-output -n eu5 python scripts/ai_context.py --changed`).
- [x] Identify all generated and manual wonder files before editing.
- [x] Run task-scoped AI context once target files are known.
- [x] Keep this TODO updated after each substantial implementation step.
- [x] Run generators for script-managed wonder module files.
- [x] Run `conda run --no-capture-output -n eu5 python scripts/gen_index.py` after scripted effect/localization changes.
- [x] Run `conda run --no-capture-output -n eu5 python scripts/validate.py --changed --fix` after GUI/localization changes.
- [x] Read `docs/knowledge/PROJECT_OVERVIEW.md` and update it if required.
- [x] Regenerate `docs/knowledge/BRIEF.md` if project overview or knowledge files change.

## Requested Gameplay Changes

1. Construction Progress As IO Variable
   - [x] Replace direct construction progress tracking with IO variable `tv_wonder_construction_progress`.
   - [x] Show active construction progress under the Engineering Department header.
   - [x] Use IO variable `monthly_change` for construction progress and material cost deltas so tooltips auto-parse.
   - [x] Preserve existing material stockpile monthly-change behavior.
   - [x] Remove the old per-part progress advancement effects from active code paths.

2. Progress Bar Extra Text
   - [x] Under the progress bar, add left text: "按照当前速度，我们预计当前奇观单元的建设还需xx年xx月".
   - [x] Under the progress bar, add right text: "xx%/100%".
   - [x] Ensure the estimate uses current speed and current unit remaining progress.
   - [x] Ensure UI remains aligned and readable in the existing 500px IO panel layout.

3. Wonder Modules As Buildings
   - [x] For every wonder type, define four module buildings, each max level 6.
   - [x] Module buildings must never be manually built or destroyed.
   - [x] Module buildings use small construction-material upkeep through `tv_wonder_module_maintenance`.
   - [x] Module buildings provide placeholder `+0.1` local culture tradition.
   - [x] Whenever a location has all four modules for a level, destroy those modules and create/raise a helper building named after the wonder.
   - [x] Helper/base wonder building max level 6, never manually built/destroyed.
   - [x] Helper/base wonder building uses the same material upkeep and provides only `+0.4` local culture tradition, not strong wonder effects.
   - [x] Preserve completed partial construction through module/helper buildings if construction is interrupted.

4. Save Compatibility / Reinitialize Mod
   - [x] Locate the reinitialize-mod button/effect in `tv_reinitialize_actions.txt`.
   - [x] Add compatibility logic that checks current player wonder state.
   - [x] Grant appropriate module/helper buildings for existing in-progress or completed wonder state.
   - [x] Also run the compatibility effect when the Engineering Department IO is created.

5. Wonder Sizes And Concepts
   - [x] Classify wonders as small, medium, or large.
   - [x] Palace of Nations and Great Port are medium.
   - [x] Assign all other current universal wonders to sizes.
   - [x] Add game concepts for wonder sizes.
   - [x] Concept text explains that small wonders are generally easier to build but have more complex ceremonies.
   - [x] Concept text explains that large wonders are harder and require stronger economy/mobilization but give richer rewards.
   - [x] Change per-unit progress requirement from 300000 for all wonders to 100000/200000/300000 for small/medium/large.
   - [x] In the initial Great Engineer proposal, explicitly show the proposed wonder's size.

6. Wonder Effect Balance
   - [x] Great Port final buildings gain `+0.1` local harbor capacity/suitability.
   - [x] Giant Necropolis Complex changes population-join-rebel-threshold effect from `-1%` per level to `-2%` per level.
   - [x] All final wonder buildings additionally provide `+0.5` local culture tradition and `+0.5` local culture influence as base effects.

7. Stronger Completion Rewards
   - [x] Add national buff "全国欢庆奇观落成".
   - [x] National buff scales per completed wonder level: `+5%` raw materials production efficiency, `+5%` production efficiency, `-5%` population-join-rebel threshold, `+0.1%` monthly prosperity growth.
   - [x] National buff duration: one year per wonder level.
   - [x] Add local buff "欢庆奇观落成".
   - [x] Local buff scales per completed wonder level: `+5%` local raw materials production efficiency, `+5%` local production efficiency, `-5%` local unrest, `+0.1%` monthly prosperity growth.
   - [x] Local buff duration: five years per wonder level.
   - [x] Completed site immediately gains prosperity: `+15%` per wonder level.
   - [x] Completion reward text starts with: "由于我们建成了一个等级为x的奇观，我们获得了如下额外效果".
   - [x] Rewards are independent of whether the wonder was built in one pass or through expansions.

8. Domestic Support Fallback
   - [x] If domestic support reaches 0 and wonder level is at least 1, do not fail.
   - [x] Instead automatically enter ceremony stage via `tv_wonder_finish_construction_effect`.

9. No Global Uniqueness For Universal Wonders
   - [x] Verify universal wonders are not globally unique.
   - [x] Remove/avoid any uniqueness restriction in the current implementation.

10. Resume/Expand Unfinished Wonders
   - [x] Great Engineer agendas prioritize eligible leftover module/helper-building cases unless the player refutes/bribes the proposal.
   - [x] Case A: wonder not yet completed, but module buildings remain.
   - [x] Case B: wonder completed, but extra module buildings remain.
   - [x] Case C: wonder completed below the stored site suitability/cap and can be expanded.
   - [x] Use special proposal text for "完成造了一半的xx奇观".
   - [x] Use special proposal text for "扩建xx奇观".
   - [x] Starting a resumed project correctly reads completed survey data and module states.
   - [x] Continuing from level 1 to 2 marks four level-1 modules complete without firing completion events again.
   - [x] If expanding an already completed wonder, lock ceremony to the previous ceremony/building variant instead of offering three choices.
   - [x] Add top-panel hint in construction/ceremony UI: players can build a low-level wonder first and expand later with less time pressure and no reward loss.
   - [x] Ensure repeated expansions can claim completion rewards each time.

11. Auto-Advance Module Selection
   - [x] When the active module completes, switch construction to the next module rather than the next unit of the same module.
   - [x] This lets unattended construction complete one full wonder level in the intended order.

## Validation Notes

- [x] Validate generated headers for new generated files.
- [x] Validate localization encoding after localization edits.
- [x] Confirm no unrelated user changes are reverted.
- [x] Current validation: `conda run --no-capture-output -n eu5 python scripts/validate.py --changed --fix` passed after GUI/localization/generator work; it fixed BOM on two generated files.
- [x] Final validation after project overview/brief check.
