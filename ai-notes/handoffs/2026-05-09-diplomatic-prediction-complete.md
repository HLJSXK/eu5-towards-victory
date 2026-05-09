# Handoff: Diplomatic Prediction Mechanic — MVP Complete

Date: 2026-05-09
Author: Claude Sonnet 4.5 (CR) + GPT-5.5 (Implementation)

## Summary

Added a prediction mechanic to the Diplomatic Victory path. Players can predict outcomes of major vanilla situations and earn DVP for correct predictions.

## Implemented Candidates

| Prediction | Category | Score | Resolution Method |
|-----------|----------|-------|-------------------|
| Western Schism winner | Major (church-wide) | 30 DVP | Country-scope variables copied by vanilla `on_ended` |
| Rise of the Ottomans leader | Regional | 20 DVP | Situation-scope variables read while `end_trigger = yes` (before cleanup) |

## Architecture

- `monthly_country_pulse` with `is_human = yes` gate (runs for 1 country/month only)
- Scripted triggers for: can_offer / ready_to_resolve / is_correct
- Events for: prediction offer (with decline option) / correct result / incorrect result
- Country variables for: choice, declined, resolved flags, prediction_score

## Files Added

| File | Purpose |
|------|---------|
| `src/in_game/common/scripted_triggers/tv_diplomatic_prediction_triggers.txt` | Offer/resolve/correctness triggers |
| `src/in_game/common/scripted_effects/tv_diplomatic_prediction_effects.txt` | Award/resolve/monthly dispatcher effects |
| `src/in_game/common/on_action/tv_diplomatic_prediction.txt` | Monthly pulse hook |
| `src/in_game/events/tv_diplomatic_prediction_events.txt` | 6 events (2 offers + 2 correct + 2 incorrect) |
| `src/main_menu/localization/english/tv_diplomatic_prediction_l_english.yml` | EN localization |
| `src/main_menu/localization/simp_chinese/tv_diplomatic_prediction_l_simp_chinese.yml` | ZH localization |

## CR Applied

CR by Claude identified P1 timing issues with situation cleanup:
- `situation_has_ended = yes` removed from resolution triggers (situation scope invalid post-cleanup)
- Western Schism correctness simplified to country-scope only (vanilla copies vars in `on_ended`)
- Rise of Ottomans resolves at `end_trigger = yes` (situation still alive)

## Remaining In-Game Validation

- [ ] Confirm `rise_of_the_ottomans_end_trigger = yes` is caught by monthly pulse before vanilla fires `end_situation`
- [ ] Confirm `situation:western_schism = { situation_is_active = yes }` doesn't error when situation hasn't started yet
- [ ] Confirm country-scope `western_schism_pope_score` is actually readable after vanilla `on_ended` copies it
- [ ] Confirm `situation:rise_of_the_ottomans.var:strongest_beylik_variable` comparison against a stored country variable works

## Next Steps

- Add `treaty_of_tordesillas` prediction (conservative "treaty longevity" design)
- Add `war_of_religions` prediction (needs instrumentation for Catholic/Protestant victory detection)
- Consider dedicated prediction UI panel (current MVP is event-only)
- Balance scoring: 30/20 DVP may be too generous if predictions are easy; playtest needed
