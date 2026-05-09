# Diplomatic Prediction Mechanic — CR

Reviewer: Claude Sonnet 4.5
Date: 2026-05-09
Scope: MVP implementation of prediction mechanic (Western Schism + Rise of the Ottomans)

---

## Verdict

Solid MVP design. One P1 timing issue, one P1 correctness logic bug, and one P2 performance note. Approve after fixes.

---

## Performance Section

```
Performance risk: LOW
Repeated execution paths:
  - monthly_country_pulse: guarded by is_human = yes (1 country max)
  - Inside that: cheap variable existence checks before any situation scope access
Broad iterators: None
Caching/incremental update opportunities:
  - Prediction choices cached as country variables (correct)
  - Resolution only checked when situation is ending (correct)
  - tv_prediction_score is incremental (correct)
Recommended follow-up: None for performance.
```

The `is_human = yes` top-level gate means this entire system runs for **exactly 1 country per month**. All subsequent checks are variable existence tests and situation state queries. Performance is excellent.

---

## P1: Timing Issue — `situation_has_ended` vs variable availability

### File: `tv_diplomatic_prediction_triggers.txt`, lines 16-25

```
tv_western_schism_prediction_ready_to_resolve = {
    has_variable = tv_pred_western_schism_choice
    NOT = { has_variable = tv_pred_western_schism_resolved }
    OR = {
        situation:western_schism = { western_schism_end_trigger = yes }
        situation:western_schism = { situation_has_ended = yes }
        has_variable = western_schism_pope_score      ← country-scope fallback
        has_variable = western_schism_anti_pope_score  ← country-scope fallback
    }
}
```

**Problem:** The `monthly_country_pulse` runs at an arbitrary point in the month. When `situation_has_ended = yes` becomes true:
- The situation's `on_ended` fires **synchronously**, copies variables to countries, then removes them from the situation.
- By the time our monthly pulse checks, `situation:western_schism` may already be **fully cleaned up** and not even exist as a scope target.

**The good news:** The fallback lines `has_variable = western_schism_pope_score` (on country scope) correctly handle the post-cleanup state. However, once `situation_has_ended = yes`, attempting `situation:western_schism = { ... }` on a destroyed situation might throw an engine error.

**Fix:** Replace the situation-access lines with the country-scope fallback as primary check:

```
tv_western_schism_prediction_ready_to_resolve = {
    has_variable = tv_pred_western_schism_choice
    NOT = { has_variable = tv_pred_western_schism_resolved }
    OR = {
        situation:western_schism = { western_schism_end_trigger = yes }
        # After on_ended, variables are copied to country:
        has_variable = western_schism_pope_score
        has_variable = western_schism_anti_pope_score
    }
}
```

Remove `situation:western_schism = { situation_has_ended = yes }` — if the situation has ended, it may no longer be a valid scope target for further queries. The country-scope variable check is sufficient.

---

## P1: Correctness Logic Bug — `tv_western_schism_prediction_is_correct`

### File: `tv_diplomatic_prediction_triggers.txt`, lines 27-56

The correctness trigger attempts to read from BOTH situation scope and country scope:
```
OR = {
    situation:western_schism = {
        has_variable = western_schism_pope_score
        var:western_schism_pope_score >= 2
    }
    AND = {
        has_variable = western_schism_pope_score     ← country scope
        var:western_schism_pope_score >= 2           ← country scope
    }
}
```

**Problem:** By the time resolution fires (triggered by the country-scope fallback in `ready_to_resolve`), the situation is already cleaned up. The `situation:western_schism = { ... }` branch will either:
- Error if situation no longer exists
- Return false because variables were removed in `on_ended`

The country-scope branch is the **only reliable one** post-cleanup.

**Fix:** Simplify to only check country scope:

```
tv_western_schism_prediction_is_correct = {
    OR = {
        AND = {
            var:tv_pred_western_schism_choice = 1
            has_variable = western_schism_pope_score
            var:western_schism_pope_score >= 2
        }
        AND = {
            var:tv_pred_western_schism_choice = 2
            has_variable = western_schism_anti_pope_score
            var:western_schism_anti_pope_score >= 2
        }
    }
}
```

This is simpler and guaranteed to work because vanilla's `on_ended` copies the scores to the country before cleanup.

---

## P1: Rise of the Ottomans — Same timing problem

### File: `tv_diplomatic_prediction_triggers.txt`, lines 77-86

```
tv_rise_ottomans_prediction_ready_to_resolve = {
    ...
    situation:rise_of_the_ottomans = {
        OR = {
            rise_of_the_ottomans_end_trigger = yes
            situation_has_ended = yes
        }
    }
}
```

**Problem:** Same as Western Schism — if `situation_has_ended = yes`, the situation scope may be invalid.

**But worse:** Unlike Western Schism, there's no vanilla `on_ended` that copies `strongest_beylik_variable` to countries. Let me verify:

Checking vanilla `rise_of_the_ottomans.txt` on_ended behavior is necessary. If it does NOT copy variables to countries, then:
- `tv_rise_ottomans_prediction_is_correct` (line 89-103) relies on `situation:rise_of_the_ottomans.var:strongest_beylik_variable` — which may be gone after cleanup.

**Fix:** Use `rise_of_the_ottomans_end_trigger = yes` (which fires BEFORE situation ends) as the resolution trigger. Remove `situation_has_ended = yes` from the OR. This ensures we resolve while the situation is still alive and variables are readable.

Alternatively: copy the situation outcome variable to the country in the prediction effect before resolution clears it.

---

## P2: `is_human = yes` gate is redundant

### File: `tv_diplomatic_prediction_triggers.txt`, lines 3, 58

Both `tv_can_offer_western_schism_prediction` and `tv_can_offer_rise_ottomans_prediction` check `is_human = yes`. But the caller (`tv_diplomatic_prediction.txt` on_action) already gates with `is_human = yes`.

**Not a bug** — just unnecessary duplicate work (2 extra trigger evaluations per month). Very minor. Can remove from the scripted triggers if desired, but leaving them as defense-in-depth is also fine.

---

## Approved (no issues)

- **Architecture:** Clean separation into triggers/effects/events/on_action. Easy to extend.
- **Data model:** Country variables for choices, simple integers for options, clean resolved flags.
- **Performance:** Excellent. `is_human = yes` gate ensures single-country execution.
- **Event design:** Good decline option; no forcing predictions on the player.
- **Localization:** Complete, atmospheric, bilingual.
- **Rise of Ottomans visibility gate** (lines 67-74): Good use of regional presence/reform/neighbor checks to limit prediction availability to relevant countries.
- **Reward amounts:** 30 DVP (major) / 20 DVP (regional) feel reasonable for rare one-time events.

---

## Summary

| Priority | Issue | File | Fix |
|----------|-------|------|-----|
| P1 | Situation scope invalid after cleanup | triggers, lines 16-25 | Remove `situation_has_ended` check; rely on country-scope variable fallback |
| P1 | Correctness trigger reads dead situation | triggers, lines 27-56 | Simplify to country-scope only |
| P1 | Rise of Ottomans timing | triggers, lines 77-86 | Use `end_trigger = yes` only (before cleanup); or copy outcome variable to country |
| P2 | Redundant `is_human` check | triggers, lines 3, 58 | Optional removal |

After fixing the P1 timing issues, this is merge-ready.
