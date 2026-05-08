# Handoff: Third CR Round — Diplomatic Alliance (Post GPT-5.5 Fix)

Date: 2026-05-08
Author: GPT-5.5
Context: Follow-up implementation after second-round CR.

## What Changed

- `src/in_game/common/country_interactions/tv_seek_diplomatic_support.txt`
  - If `tv_diplomatic_alliance` already exists, only its leader can use `Seek Diplomatic Support`.
  - Existing IO membership add now checks that `scope:actor` is the current alliance leader before adding the supporter.

- `src/in_game/common/international_organizations/tv_diplomatic_alliance.txt`
  - Replaced fragile `prev.prev.var:tv_diplomatic_supporter_of = this` with a flatter check:
    `var:tv_diplomatic_supporter_of = scope:recipient.leader_country`.

- `src/in_game/common/laws/tv_alliance_laws.txt`
  - Added hard `allow` blocks to every level 2/3/4 policy.
  - Each upgrade now requires:
    - current policy is the previous level in the same law category;
    - `tv_alliance_cohesion` exists;
    - cohesion is at least 25/50/75.

- `data/victory_paths.yaml`
  - M1 diplomatic milestone now requires either no existing `tv_diplomatic_alliance` or the country already being the current alliance leader.
  - M1 grant now initializes IO cohesion/tier only inside the IO creation branch, avoiding reset of an existing alliance.

- Generated outputs updated by running `python scripts/gen_victory.py`.

## Validation Run

- `python scripts/gen_victory.py` succeeded.
- `python scripts/validate.py` succeeded with:
  - `[OK] Validated 33 file(s) -- no issues found.`

## Suggested CR Focus

1. Confirm `var:tv_diplomatic_supporter_of = scope:recipient.leader_country` is valid in `can_join_trigger`.
2. Confirm policy-level `allow` blocks execute in IO scope and correctly read `tv_alliance_cohesion`.
3. Confirm requiring the previous policy with `international_organization_has_policy = policy:*` is sufficient to prevent skipping levels.
4. Confirm the design choice that once the unique diplomatic alliance exists, non-leaders cannot continue diplomatic-victory M1 progression.
