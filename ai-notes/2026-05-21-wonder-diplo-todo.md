# 2026-05-21 Wonder / Diplomatic / Research Todo

Persistent progress file for the current multi-system task. Update this after each meaningful step so work can resume after context compaction.

## Source Design Anchors

- `docs/design/Original_Design.md:101-132` wonder definitions and baseline effects.
- `docs/design/Original_Design.md:137-186` wonder proposal, debate, and survey flow.
- `docs/design/Original_Design.md:187-201` organization/logistics guidance and buildings.
- `docs/design/Original_Design.md:219-296` ceremony definitions.
- `docs/design/Original_Design.md:301-323` diplomatic victory route.
- `docs/design/Original_Design.md:341-384` concentrated research events.

## Todo

- [x] 1. Align Diplomatic Victory route with Original_Design L301+; document design wins over current code where they conflict.
- [x] 2. Change concentrated research subprocess A/monthly event request into a single `random_list`: existing gold-for-progress branch 5%, new token-loss branches 1% each for 10 prestige, 10% clergy satisfaction, 10% burghers satisfaction, 7 stability, and 5 legitimacy, each with unique flavor text.
- [x] 3. Fix Great Engineer guidance so after debate ends it no longer says the player still needs to win the debate.
- [x] 4. Fire an event after declaring debate complete, guiding the player to begin survey.
- [x] 5. Strengthen Organization/Logistics card guidance with three explicit paragraphs explaining labor camps, material depots, and dispatch points.
- [x] 6. On wonder inauguration, add +5 ADM/DIP/MIL to the current ruler and +10 ADM/DIP/MIL to the current Great Engineer.
- [x] 7. Replace ceremony style button labels like "Ritual 1/2/3" with the actual ceremony names.
- [x] 8. Compare wonder definitions from Original_Design L101+ and fix implemented wonder effects that diverge.
- [x] 9. Implement Giant Astronomical Observatory and Palace of Nations for the Engineering Department.

## Working Notes

- Read `CLAUDE.md`; generated files must be edited through data/generators where registered.
- Read `docs/knowledge/BRIEF.md`; Engineering Department and Diplomatic Alliance are already large systems with several risk-card-adjacent gotchas.
- `data/generated_files.yaml` says victory path core, IO leader actions, alliance laws, pulse registry, academy GUI, and research D events are generated.
- Ran `ai_context.py --changed`; required risk cards were generic actions, GUI, international organizations, and on_action.

## Verification Log

- Diplomatic Victory now uses Original_Design thresholds `1/50/500/2500/15000` and rewards `monthly_diplomats=0.10`, `diplomatic_reputation=2`, `diplomatic_range=1000`, `improve_relation_impact=0.50`, `diplomatic_reputation=10`.
- Removed DVP from royal marriage and war win on_actions; `on_winning_war` only preserves the Engineering Department war-ceremony hook.
- Second diplomatic support now founds the alliance and grants first DVP; alliance tier monthly IO maintenance grants DVP thereafter.
- Diplomatic Alliance cohesion now uses base +0.1, leader dip rep * 0.01, and internal peace +0.05.
- Alliance law AI weights adjusted to design: bases 0/-100/-200/-300; opinion and diplomatic reputation scaling increase by reform level.
- Added member management: invite country interaction and expel-member generic action, both reachable from the Diplomatic Alliance panel.
- Research A monthly pulse now uses one `random_list` with 90% no event, 5% gold-for-interest, and five 1% token-loss interest events; added unique EN/ZH localizations for events `tv_research.2`-`.6`.
- Great Engineer locked-wonder guidance now separates locked-wonder display from stage guidance; after debate it tells the player to start survey instead of to keep winning debate.
- `tv_wonder_end_debate_effect` now sets stage 2 and fires `tv_engineering_department.203`, a survey-start guidance event.
- Organization/Logistics UI now shows three explicit help paragraphs for labor camps, material depots, and dispatch points.
- Wonder finalization now calls `tv_wonder_reward_current_ruler_and_engineer_effect`: current ruler gets +5 ADM/DIP/MIL and current Great Engineer gets +10 ADM/DIP/MIL.
- Ceremony toggle buttons now use the locked wonder's actual ceremony names across all 27 ceremony branches.
- Original_Design wonder alignment fixes include Giant Necropolis national rebel-threshold sign, Mining City raw-material output at 10%, Deep Shaft extra local production at 5%, Palace branch `local_proximity_source = 5`, and Palace of Nations base levels adding `global_distance_from_capital_speed_propagation`.
- Giant Astronomical Observatory and Palace of Nations are implemented across proposal/lock/survey/finalization logic, actions, triggers, buildings, modifiers, events, game concepts, GUI labels, and EN/ZH localization.
- Generators run: `scripts/gen_messagetypes.py`, `scripts/gen_victory.py`, `scripts/in_game/common/laws/gen_tv_alliance_laws.py`.
- Validation passed: `conda run --no-capture-output -n eu5 python scripts/validate.py --changed --fix --ai-report`.
