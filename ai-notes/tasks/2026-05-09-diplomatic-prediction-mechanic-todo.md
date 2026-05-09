# TODO: Diplomatic Victory Prediction Mechanic

Date: 2026-05-09
Author: GPT-5.5
Status: Analysis only; no implementation yet.

## Goal

Add a future Diplomatic Victory mechanic based on predicting outcomes of major predefined game events.

The player should be able to make a prediction when a relevant situation, international organization, disaster, or major event chain is active or about to resolve. If the predicted outcome later occurs, the player gains prediction score. That score can then contribute to Diplomatic Victory.

This TODO is only about research and design preparation:

- extract relevant vanilla content;
- identify major event/situation candidates;
- define when each prediction becomes available;
- define when each prediction is resolved;
- define trigger conditions for correct and incorrect predictions.

Do not implement the gameplay system until the extraction and trigger map are reviewed.

## Source Content To Extract

Primary vanilla folders:

- `reference_game_files/game/in_game/common/situations/`
- `reference_game_files/game/in_game/events/situations/`
- `reference_game_files/game/in_game/common/international_organizations/`
- `reference_game_files/game/in_game/common/on_action/`
- `reference_game_files/game/in_game/events/`

Secondary folders to inspect when candidates point there:

- `reference_game_files/game/in_game/common/disasters/`
- `reference_game_files/game/in_game/events/disaster/`
- `reference_game_files/game/in_game/common/scripted_triggers/`
- `reference_game_files/game/in_game/common/scripted_effects/`
- `reference_game_files/game/in_game/common/resolutions/`

## Candidate Content Types

Prioritize content that is:

- historically significant;
- visible to the player;
- has multiple plausible outcomes;
- has script-visible state variables or final events;
- can be predicted before the result is known;
- not too frequent or too minor.

Likely high-value candidates:

- major situations, such as religious wars, treaty systems, large rebellions, schisms, regional conflicts;
- unique international organizations, especially those with elections, leadership changes, authority variables, or policy/resolution outcomes;
- disasters with clear success/failure endings;
- event chains with visible branching outcomes.

Avoid low-value candidates:

- purely flavor events with no meaningful branching;
- high-frequency random events;
- events whose result is immediate and cannot be predicted in advance;
- outcomes that require expensive global scans to evaluate.

## Required Extraction Table

For each candidate, produce a structured entry with:

| Field | Meaning |
|---|---|
| `id` | Stable mod-side prediction id |
| `vanilla_source` | File path and vanilla object/event ids |
| `display_name` | Player-facing name |
| `category` | Situation / IO / disaster / event chain |
| `historical_context` | Short explanation of why this is a major event |
| `prediction_window_trigger` | Trigger for when prediction can be offered |
| `prediction_options` | List of possible predictions |
| `resolution_trigger` | Trigger for when the prediction should be checked |
| `correctness_trigger` | Trigger for each option being correct |
| `failure_or_expiry_trigger` | Trigger for no longer valid / event ended without matching |
| `recommended_score` | Suggested score reward |
| `performance_notes` | Whether triggers are cheap and how often they run |
| `open_questions` | Anything needing game validation |

## Trigger Design Principles

Each prediction should have three separate trigger layers.

### 1. Prediction Window Trigger

This determines when the player is allowed to predict.

Good trigger examples:

- situation is active;
- international organization exists;
- disaster is active;
- country can see the situation;
- country is involved, nearby, or diplomatically relevant;
- a vanilla variable indicates the event is in a pre-resolution phase.

Bad trigger examples:

- broad `every_country` scans;
- triggers that only become true after the result is already known;
- triggers depending on hidden or unstable temporary scopes.

### 2. Resolution Trigger

This determines when the prediction should be checked.

Good trigger examples:

- final event in a chain fired;
- situation phase variable reaches final phase;
- disaster ended;
- IO leader/policy/result changed;
- explicit vanilla variable indicates outcome has been decided.

Resolution should be event-driven where possible, not checked by global monthly scans.

### 3. Correctness Trigger

This determines whether the chosen prediction was correct.

Good trigger examples:

- final winner country/tag matches prediction;
- situation variable points to expected outcome;
- IO leader country matches predicted side;
- disaster outcome modifier or variable exists;
- final event option set a stable variable.

If vanilla does not expose a stable final state, the candidate should be marked as requiring instrumentation before implementation.

## Performance Requirements

Follow `ai-notes/rules/eu5-performance-review.md`.

Specific requirements for this mechanic:

- Prefer event-driven checks over recurring pulse checks.
- Do not evaluate all prediction candidates every month for every country.
- Cache active predictions on the predicting country.
- Store prediction choice as a country variable or list item, then resolve only when the related vanilla event/situation changes state.
- Use cheap existence/phase variables before any broad search.
- Avoid GUI lists that recompute candidate eligibility with heavy triggers per row.

## Suggested Data Model

No code yet, but future implementation can likely use:

- country variable/list for active predictions;
- country variable for accumulated prediction score;
- scripted triggers per prediction candidate;
- scripted effects for offering, resolving, rewarding, and clearing predictions;
- notification events to ask the player to choose predictions;
- localization entries for prediction descriptions and outcome explanations.

Potential variable naming:

- `tv_prediction_score`
- `tv_prediction_active_<id>`
- `tv_prediction_choice_<id>`
- `tv_prediction_resolved_<id>`

## Work Plan

- [ ] T01: Inventory all vanilla situations and record ids, files, phases, variables, and end conditions. Pilot sample completed for 4 major situations; full inventory still pending.
- [ ] T02: Inventory all unique international organizations and record leader, variable, policy, and resolution mechanics.
- [ ] T03: Scan major disaster and situation event files for final outcome events and stable result variables.
- [ ] T04: Select the first batch of high-confidence prediction candidates.
- [ ] T05: For each selected candidate, define prediction window, resolution, and correctness triggers.
- [ ] T06: Mark candidates that require vanilla instrumentation or game validation.
- [ ] T07: Estimate scoring values and how prediction score contributes to Diplomatic Victory.
- [ ] T08: Write a CR handoff asking another AI to review trigger validity and performance risk.

## Initial Design Recommendation

Start with a small curated set rather than all possible events.

Recommended first batch size: 5-10 candidates.

Reasoning:

- easier to validate in game;
- avoids building a huge prediction UI before the trigger model is proven;
- reduces performance risk;
- lets the scoring model be tuned before expanding.

The first batch should prefer major situations and IOs with clear script state, because they are more likely to expose stable variables and end conditions.

## Open Questions

- Should predictions be available to all countries, only great powers, or only countries with enough Diplomatic Victory progress?
- Should a country need diplomatic range, visibility, or relation to the event region?
- Should wrong predictions impose a penalty, or simply give no score?
- Should prediction score be a separate Diplomatic Victory point source, or a gate like Alliance Tier?
- Should predictions be one-time per event, or can the player revise before the resolution phase?

## T01 Pilot Inventory: Major Situations

Date: 2026-05-09

Purpose: Validate whether the prediction mechanic can be designed from vanilla situation/event state before doing a full inventory.

Pilot sample:

- `war_of_religions`
- `western_schism`
- `treaty_of_tordesillas`
- `rise_of_the_ottomans`

### Summary

The pilot is promising. Vanilla situation files often expose enough state to define prediction windows and resolution points. The strongest candidates are those that already store outcome variables or fire final events.

Best first-batch candidates:

- `western_schism`: very strong candidate. Has explicit score variables and final events.
- `rise_of_the_ottomans`: strong candidate. Has a live `strongest_beylik_variable` and clear end trigger.
- `treaty_of_tordesillas`: medium candidate. Good phase triggers, but prediction options should stay simple.
- `war_of_religions`: medium/high candidate, but likely needs instrumentation for clean outcome typing.

### Candidate: Western Schism

| Field | Notes |
|---|---|
| `id` | `tv_predict_western_schism_winner` |
| `vanilla_source` | `common/situations/western_schism.txt`; `events/situations/western_schism.txt`; `common/scripted_triggers/situation_triggers.txt` |
| `category` | Situation / IO resolution |
| `historical_context` | Catholic world split between papal claimants; outcome is diplomatically significant. |
| `prediction_window_trigger` | `situation:western_schism = { situation_is_active = yes }`, visible/relevant countries likely `religion = religion:catholic`. |
| `prediction_options` | Papal States claimant wins; schism opponent wins. |
| `resolution_trigger` | `situation:western_schism = { situation_has_ended = yes }` or final event flow around `western_schism.2000`, `western_schism.2100`, `western_schism.2200`. |
| `correctness_trigger` | Papal side: `situation:western_schism.var:western_schism_pope_score >= 2`; opponent side: `situation:western_schism.var:western_schism_anti_pope_score >= 2`. |
| `failure_or_expiry_trigger` | Catholic Church no longer exists, PAP no longer exists, PAP has no cardinals, or situation ended without score reaching either threshold. |
| `recommended_score` | High, because it is a rare major church-wide event. |
| `performance_notes` | Good. Triggers are variable checks and situation state checks. No broad scans needed for prediction resolution. |
| `open_questions` | `on_ended` copies result variables to each Catholic country before removing situation variables. Implementation should resolve before those variables are removed, or store/copy the outcome in a mod variable. |

Relevant vanilla state:

- `western_schism_pope_score`
- `western_schism_anti_pope_score`
- `schism_opponent_country`
- `western_schism_ended_by_event`
- `western_schism_resolution`

Assessment: Use this as one of the first implementation candidates.

### Candidate: Rise of the Ottomans

| Field | Notes |
|---|---|
| `id` | `tv_predict_rise_of_ottomans_leader` |
| `vanilla_source` | `common/situations/rise_of_the_ottomans.txt`; `events/situations/rise_of_the_ottomans.txt`; `common/scripted_triggers/situation_triggers.txt` |
| `category` | Situation |
| `historical_context` | Competing Anatolian beyliks and the emergence of a dominant Turkish power. |
| `prediction_window_trigger` | `situation:rise_of_the_ottomans = { situation_is_active = yes has_variable = strongest_beylik_variable }`; player should probably have visibility/relevance in Anatolia/Balkans or know the strongest beylik. |
| `prediction_options` | Current strongest beylik remains dominant; Ottomans/TUR become dominant; another beylik overtakes. |
| `resolution_trigger` | `situation:rise_of_the_ottomans = { situation_has_ended = yes }`; end trigger includes year > 1565, no beyliks left, strongest beylik becoming large/independent, or strongest beylik shrinking after 1400. |
| `correctness_trigger` | At resolution, compare stored prediction to `situation:rise_of_the_ottomans.var:strongest_beylik_variable`; for TUR option use `var:strongest_beylik_variable = c:TUR`; for “other” use predicted country scope if stored. |
| `failure_or_expiry_trigger` | Situation ends with no valid `strongest_beylik_variable`, or predicted country no longer exists. |
| `recommended_score` | Medium/high. Long-running regional power prediction. |
| `performance_notes` | Good if prediction stores the chosen country once. Do not recompute rankings; vanilla already maintains top variables. |
| `open_questions` | Vanilla recalculates top 3 monthly. Need confirm `strongest_beylik_variable` is still readable at `on_ended`, or copy it before cleanup. |

Relevant vanilla state:

- `strongest_beylik_variable`
- `second_strongest_strongest_beylik_variable`
- `third_strongest_strongest_beylik_variable`
- `rise_of_the_ottomans_winner_variable`
- `leader_of_the_turks`

Assessment: Strong candidate if final outcome can be captured before situation cleanup.

### Candidate: Treaty of Tordesillas

| Field | Notes |
|---|---|
| `id` | `tv_predict_tordesillas_ratification` |
| `vanilla_source` | `common/situations/treaty_of_tordesillas.txt`; `events/situations/treaty_of_tordesillas.txt`; `common/generic_actions/treaty_of_tordesillas.txt`; `_hardcoded.txt` |
| `category` | Situation |
| `historical_context` | Catholic colonial powers negotiate and enforce a world division line. |
| `prediction_window_trigger` | `situation:treaty_of_tordesillas = { situation_is_active = yes var:var_treaty_phase = 1.0 }`; probably only for Catholic countries or countries that can see the situation. |
| `prediction_options` | Treaty ratifies; treaty fails/expires before ratification; optional later prediction: treaty remains relevant for N years after phase 2. |
| `resolution_trigger` | Ratified when `var_treaty_phase = 2.0` or event `treaty_of_tordesillas.3` fires; expired when situation ends via `var_treaty_phase = 2.0` and `var_treaty_progress <= 0.0`. |
| `correctness_trigger` | Ratification prediction correct if `var_treaty_phase = 2.0`; expiry prediction correct if situation ends without reaching phase 2, if that is possible. |
| `failure_or_expiry_trigger` | Situation ended, or signatory variables become invalid. |
| `recommended_score` | Medium. Major event but prediction options should be conservative. |
| `performance_notes` | Good. Uses simple phase/progress variables. |
| `open_questions` | Need confirm whether phase 1 can actually fail before ratification. If not, this candidate should predict phase 2 longevity or whether treaty relevance survives past a target year instead. |

Relevant vanilla state:

- `var_treaty_phase`
- `var_treaty_progress`
- `var_west_country`
- `var_east_country`
- `var_line_location`
- events `treaty_of_tordesillas.3` and `treaty_of_tordesillas.4`

Assessment: Use cautiously. Best initial prediction may be “will the treaty still be relevant after X years” rather than “will it ratify”.

### Candidate: War of Religions

| Field | Notes |
|---|---|
| `id` | `tv_predict_war_of_religions_outcome` |
| `vanilla_source` | `common/situations/war_of_religions.txt`; `events/situations/war_of_religions.txt`; `common/scripted_triggers/situation_triggers.txt`; `common/peace_treaties/religious_supremacy.txt`; `_hardcoded.txt` |
| `category` | Situation / war outcome |
| `historical_context` | Confessional struggle involving HRE, Catholic League, Protestant Union, and Peace of Westphalia. |
| `prediction_window_trigger` | `situation:war_of_religions = { situation_is_active = yes }`; stronger trigger after `has_variable = war_of_religion_current_war`. |
| `prediction_options` | Catholic side prevails; Protestant side prevails; Peace of Westphalia / negotiated settlement. |
| `resolution_trigger` | Situation ends. Vanilla explicitly ends via `end_situation = this` in `war_of_religions.1300` for Peace of Westphalia, and likely via religious supremacy peace treaty for side victory. |
| `correctness_trigger` | Peace of Westphalia: event `war_of_religions.1300` fired. Catholic/Protestant victory: needs inspection/instrumentation around `peace_treaties/religious_supremacy.txt`, because common situation cleanup destroys league IOs and does not expose a simple winner variable. |
| `failure_or_expiry_trigger` | Situation ends without stored outcome; league IOs destroyed; religious war variable removed. |
| `recommended_score` | High, but only after outcome capture is reliable. |
| `performance_notes` | Prediction checks can be cheap if event-driven. Avoid polling war participants monthly; vanilla already does expensive monthly participant tracking. |
| `open_questions` | Need identify or add a stable mod variable when religious supremacy peace treaty is enforced. Without instrumentation, correctness for Catholic/Protestant victory may be ambiguous. |

Relevant vanilla state:

- `war_of_religion_current_war`
- `war_of_religions_peace_demands_ratio`
- `war_of_religions.1300` Peace of Westphalia event
- `protestant_union`
- `catholic_league`
- `religious_supremacy` peace treaty

Assessment: Good thematic candidate, but not the first implementation candidate unless instrumentation is allowed.

### Pilot Conclusion

Proceed with a small first batch instead of full coverage.

Recommended initial implementation candidates after this pilot:

1. `western_schism`
2. `rise_of_the_ottomans`
3. `treaty_of_tordesillas` with conservative options

Hold for later:

- `war_of_religions`, pending reliable winner instrumentation.

Implementation implication:

- The prediction system should support both pure vanilla-state candidates and candidates requiring lightweight mod instrumentation.
- For situation outcomes, prefer resolving predictions in or near `on_ending`/final event hooks before vanilla cleanup removes variables.
- The full T01 inventory should mark each situation as:
  - `ready`: clear window/resolution/correctness triggers;
  - `needs_instrumentation`: major but no stable final variable;
  - `not_suitable`: no meaningful prediction window or result.

## MVP Implementation Note

Date: 2026-05-09

Implemented first non-invasive MVP for two candidates:

- `western_schism`
- `rise_of_the_ottomans`

New manual files:

- `src/in_game/common/scripted_triggers/tv_diplomatic_prediction_triggers.txt`
- `src/in_game/common/scripted_effects/tv_diplomatic_prediction_effects.txt`
- `src/in_game/common/on_action/tv_diplomatic_prediction.txt`
- `src/in_game/events/tv_diplomatic_prediction_events.txt`
- `src/main_menu/localization/english/tv_diplomatic_prediction_l_english.yml`
- `src/main_menu/localization/simp_chinese/tv_diplomatic_prediction_l_simp_chinese.yml`

Implementation shape:

- Uses `monthly_country_pulse` with an `is_human = yes` top-level guard.
- Offers predictions only when the relevant vanilla situation is active and the player has not already chosen/declined/resolved that prediction.
- Stores choices as country variables:
  - `tv_pred_western_schism_choice`
  - `tv_pred_rise_ottomans_choice`
  - `tv_pred_rise_ottomans_country`
- Stores total prediction points in `tv_prediction_score`.
- Correct predictions also add the same amount to `tv_diplomatic_victory_points`.
- Current rewards:
  - Western Schism: 30 prediction score / 30 DVP.
  - Rise of the Ottomans: 20 prediction score / 20 DVP.

Intentionally not implemented yet:

- `treaty_of_tordesillas`, because the ratification option may be too deterministic. It should be redesigned as a conservative “treaty relevance/longevity” prediction before implementation.
- `war_of_religions`, because Catholic/Protestant victory needs a stable result variable or lightweight instrumentation around the religious supremacy peace treaty.
- Dedicated UI. The MVP is event-driven only.

Validation:

- `python scripts/validate.py --changed` passed for the 6 new mod files.

CR focus for another AI:

- Confirm whether the vanilla situation variables are still readable at the monthly resolution point, especially near `on_ended` cleanup.
- Confirm that comparing a stored country variable against `situation:rise_of_the_ottomans.var:strongest_beylik_variable` is valid in EU5 script.
- Confirm whether `monthly_country_pulse` duplicate definitions merge as expected in this project, consistent with existing mod files.
- Confirm whether rewards should directly add `tv_diplomatic_victory_points`, or remain only in `tv_prediction_score` until a later balancing pass.

## Post-CR Fix Note

Date: 2026-05-09

Applied fixes from `ai-notes/reviews/2026-05-09-diplomatic-prediction-cr.md`:

- Removed `situation_has_ended = yes` from the Western Schism resolution trigger to avoid accessing a cleaned-up situation scope.
- Simplified Western Schism correctness checks to use only the country-scope variables that vanilla copies during `on_ended`.
- Removed `situation_has_ended = yes` from the Rise of the Ottomans resolution trigger, so it resolves only while `rise_of_the_ottomans_end_trigger = yes` and the situation variables should still be readable.

Remaining validation point:

- Game-test whether `rise_of_the_ottomans_end_trigger = yes` is caught reliably by `monthly_country_pulse` before vanilla ends the situation. If not, this candidate needs lightweight instrumentation in a vanilla-adjacent end path.
