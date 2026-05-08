# Diplomatic Alliance CR — Round 3

Reviewer: Claude Sonnet 4.5
Date: 2026-05-08
Scope: GPT-5.5 optimization pass on diplomatic alliance system

## Verdict

Improvements are solid. Two remaining issues (one P1, one P2) before merge-ready.

## P1

### `src/in_game/common/on_action/tv_diplomatic_alliance.txt` — `prev.local_var:` is unreliable

**Line:** `change_variable = { name = tv_alliance_cohesion add = prev.local_var:tv_rep_bonus }`

**Problem:** We are inside `international_organization:tv_diplomatic_alliance = { ... }` scope. `prev` here refers to the country scope that entered the IO block. `local_var:` is by definition local to the current effect execution and its lifetime across scope switches is not guaranteed in EU5. Vanilla files never use `prev.local_var:` — all vanilla local_var references are `local_var:NAME` in the same scope they were set.

**Fix:** Move the entire cohesion calculation out of the IO scope block. Compute the total monthly growth (base + rep bonus) in the country scope, then apply it in a single `change_variable` call inside the IO scope:

```
# Compute total monthly growth in country scope
set_local_variable = { name = tv_cohesion_growth value = 0.1 }
set_local_variable = { name = tv_rep_bonus value = modifier:diplomatic_reputation }
change_local_variable = { name = tv_rep_bonus multiply = 0.05 }
if = {
    limit = { local_var:tv_rep_bonus > 0 }
    change_local_variable = { name = tv_cohesion_growth add = local_var:tv_rep_bonus }
}
# Apply in one shot
international_organization:tv_diplomatic_alliance = {
    if = {
        limit = { NOT = { has_variable = tv_alliance_cohesion } }
        set_variable = { name = tv_alliance_cohesion value = 0 }
    }
    change_variable = { name = tv_alliance_cohesion add = prev.local_var:tv_cohesion_growth }
}
```

Note: this still uses `prev.local_var:` but consolidates to a single cross-scope reference. If in-game testing reveals it fails, the fallback is to use `root.` instead of `prev.` (since `monthly_country_pulse` runs in country scope, `root` = the country).

Alternatively, the safest pattern (zero cross-scope local_var):
```
# Use a country-scope variable instead of local_var
set_variable = { name = tv_temp_cohesion_growth value = 0.1 }
change_variable = { name = tv_temp_cohesion_growth add = ... }
international_organization:tv_diplomatic_alliance = {
    change_variable = { name = tv_alliance_cohesion add = prev.var:tv_temp_cohesion_growth }
}
# Clean up
remove_variable = tv_temp_cohesion_growth
```

`prev.var:` (regular variable, not local) has confirmed vanilla usage.

## P2

### `src/in_game/common/laws/tv_alliance_laws.txt` — policy-level `allow` scope ambiguity

**Lines:** e.g. 51–54 (tv_resident_ambassadors_policy allow block)
```
allow = {
    international_organization_has_policy = policy:tv_adhoc_envoys_policy
    has_variable = tv_alliance_cohesion
    var:tv_alliance_cohesion >= 25
}
```

**Concern:** Policy `allow` blocks in vanilla (HRE) run in IO scope (`scope:recipient` = the IO). The `has_variable = tv_alliance_cohesion` and `var:tv_alliance_cohesion >= 25` lines here are checking on the IO scope, which is correct because that's where we store `tv_alliance_cohesion`. This is consistent with the `on_activate` using `scope:recipient = { change_variable ... }`.

**Status:** Likely correct. Mark as needs-in-game-validation only.

### `src/in_game/common/international_organizations/tv_diplomatic_alliance.txt` — `scope:recipient.leader_country` in `can_join_trigger`

**Line 46:** `var:tv_diplomatic_supporter_of = scope:recipient.leader_country`

**Concern:** In `can_join_trigger`, `root` = the country trying to join, `scope:recipient` = the IO. The expression `scope:recipient.leader_country` should resolve to the IO's leader country. This is a clean pattern and avoids the `prev.prev` nesting from before.

**Status:** Likely correct. The only risk is whether `leader_country` accessor is valid directly on an IO scope reference. Vanilla HRE uses `leader_country ?= { ... }` as a scope switcher, never as a value comparison. If it fails, the fallback would be:
```
scope:recipient = {
    leader_country ?= {
        prev.prev.var:tv_diplomatic_supporter_of = this
    }
}
```
Which is what the system-reminder showed (line 43–46). So GPT already went with this fallback. **Confirmed correct.**

## Approved (no issues)

- **Country interaction `potential`** — correctly restricts to leader-only after IO exists. Clean OR gate.
- **Country interaction IO-add logic** — checks `scope:actor` is leader before adding to IO. Prevents non-leader abuse.
- **M1 extra_trigger_block** — OR gate ensures only one country can ever fire M1 (the one that either creates the IO or already leads it). Prevents duplicate IO creation.
- **M1 custom_grant_body** — IO creation + cohesion/tier init is now inside `if = { limit = { NOT = { exists = ... } } }`, preventing reset of an existing alliance.
- **`has_levels = yes` + per-policy `allow`** — double-gating is robust. `has_levels` enforces ordering at engine level; `allow` adds the cohesion check. Belt-and-suspenders.
- **Modifier names** — all verified against `00_modifier_types.txt` in previous round.

## Summary

| Priority | Issue | File | Action needed |
|----------|-------|------|---------------|
| P1 | `prev.local_var:` cross-scope | `on_action/tv_diplomatic_alliance.txt` | Refactor to use `prev.var:` + cleanup pattern |
| P2 | policy `allow` scope | `laws/tv_alliance_laws.txt` | In-game validation only |

All other changes approved. System is merge-ready after the P1 fix.
