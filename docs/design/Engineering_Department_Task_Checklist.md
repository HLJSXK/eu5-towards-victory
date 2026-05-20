# Engineering Department Task Checklist

Status key: `[ ]` pending, `[~]` in progress, `[x]` complete.

- [x] 0. Survey UI dynamically shows current scale/logistics/organization effects instead of fixed 1-6 / 200%-50% / 200%-50%.
  - Audit: the survey cards read `tv_wonder_scale_tier`, `tv_wonder_logistics_effect_percent`, and `tv_wonder_organization_effect_percent`.
- [x] 1. Construction-phase domestic support grants call the standard IO-variable effect so effect localization renders automatically.
  - Audit: all support grant sites call `tv_change_wonder_domestic_support_effect`, backed by `effect_localization/tv_engineering_department_effects.txt`.
- [x] 2. Construction UI colors only the active part yellow; non-active parts with progress render red.
  - Audit: yellow visibility is gated by both current unit and `tv_wonder_active_part`; red explicitly excludes that same active tuple.
- [x] 3. Finalized wonders build the matching local building at the site, level equals wonder level, wonder buildings cap at 6, and players cannot self-build them with reason "wonders can only be built through the Engineering Department"; national buffs remain IO-managed country modifiers.
  - Audit: final buildings use `max_levels = 6`, `country_potential = { always = no }`, `can_destroy = { always = no }`, and scripted finalization applies country modifiers separately.
- [x] 4. Finalized wonder buildings have three variants per wonder, mapped to their own ceremonies without mixed effects.
  - Audit: `tv_wonder_construct_final_building_effect` maps locked wonder/style pairs 101-703 to distinct building types.
- [x] 5. Finalization event displays the real effect text rather than hiding building construction.
  - Audit: event `tv_engineering_department.500` option calls visible `tv_wonder_complete_finalization_effect`.
- [x] 6. Finalization event has unique flavor text for every wonder.
  - Audit: `.500` has triggered desc branches for all seven wonders and all three ceremony styles.
- [x] 7. Finalization grants extra rewards scaled by remaining domestic support 0-200 into 0-10 stability, 0-10 legitimacy, and 0-20 prestige, with a leading custom tooltip mentioning the remaining support.
  - Audit: `tv_wonder_prepare_final_support_rewards_effect` clamps 0-200 and maps support to stability/legitimacy/prestige with a leading `tv_wonder_final_support_reward_tt`.
- [x] 8. Finalization clears all project variables so the next wonder starts from zero.
  - Audit: `tv_wonder_clear_project_state_effect` removes project variables, clears ceremony lists, destroys the depot, resets stage to 0, and resets IO progress variables.
- [x] 9. Debate estate agendas include extra currency-loss demands: 10 prestige, 7 stability, 5 legitimacy, 5% loyalty from each other estate, 2.5% inflation, one cabinet member, one artist, and one artwork. Shared destructive demands refresh matching agenda slots after execution.
  - Audit: demand IDs 5-12 exist for Nobles/Burghers/Clergy; demands 10-12 call matching-slot reroll after execution.
- [x] 10. Debate estate agendas do not exclude previously refuted or bribed agenda types, so they can never exhaust.
  - Audit: refute/bribe effects simply reroll estate demand variables; no rejected/bribed agenda exclusion variables are kept.
- [x] 11. Great Engineer proposals keep exclusion, but if refuting/bribing empties the feasible deck, immediately rebuild and roll a new feasible proposal instead of waiting for a new engineer.
  - Audit: `tv_wonder_reroll_proposal_after_rejection_effect` removes the current proposal, rolls, and rebuilds the feasible deck if the roll leaves no proposal.
- [x] 12. Add four new wonder types with site suitability, base modifiers, three ceremonies each, buildings, events, UI, actions, triggers, localization, and validation: Giant Necropolis Complex, Great Lighthouse, Hydraulic Workshop Complex, Mining City.
  - Audit: new proposal/site/ceremony/action/building/modifier/localization/game-concept entries are present for wonder IDs 4-7; `ruler_death_pulses.txt` is generated for Dynastic Burial.
