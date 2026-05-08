# Handoff: Second CR Round — Diplomatic Alliance (Post-Fix)

Date: 2026-05-08
Author: Claude Sonnet 4.5
Context: First CR by GPT-5.5 has been addressed. Requesting second-round review.

## What Changed Since First CR

All P0/P1/P2 issues from `ai-notes/reviews/2026-05-08-diplomatic-alliance-cr.md` have been fixed:

- **P0**: Unescaped quotes in ZH localization — replaced with `「」`
- **P1 IO variables**: Removed illegal `variables` block; rely on `set_variable` in effects
- **P1 Law gating**: Added `has_levels = yes` + `level = N` per policy to enforce ordering
- **P1 Support switching**: `visible` now blocks any country that already has `tv_diplomatic_supporter_of`
- **P1 can_join_trigger**: Added leader_country scope chain verification
- **P2 Modifiers**: All 11 invalid names replaced with verified equivalents from `00_modifier_types.txt`

## Files to Review

### Core logic (highest priority)

| File | Focus |
|------|-------|
| `src/in_game/common/country_interactions/tv_seek_diplomatic_support.txt` | `diplo_chance` + `accept` correctness; `visible` filter; effect logic |
| `src/in_game/common/international_organizations/tv_diplomatic_alliance.txt` | IO definition structure; `can_join_trigger` scope chain |
| `src/in_game/common/laws/tv_alliance_laws.txt` | `has_levels` + `level` usage; `on_activate` cohesion deduct + tier sync; modifier names |
| `src/in_game/common/on_action/tv_diplomatic_alliance.txt` | `on_annex` scope usage; `prev.local_var:` cross-scope reference; cohesion growth math |
| `data/victory_paths.yaml` | Diplomatic milestones section (~line 843–993): `extra_trigger_block` and `custom_grant_body` |
| `scripts/gen_victory.py` | Line ~190: `custom_grant_body` generation (small change) |

### Supporting files (lower priority)

| File | Focus |
|------|-------|
| `src/in_game/common/international_organization_special_statuses/tv_diplomatic_alliance.txt` | Minimal — just verify structure |
| `src/in_game/events/tv_diplomatic_alliance_events.txt` | 2 simple events |
| `src/main_menu/localization/english/tv_diplomatic_alliance_l_english.yml` | Completeness check |
| `src/main_menu/localization/simp_chinese/tv_diplomatic_alliance_l_simp_chinese.yml` | Quote fix verification |

## Known Items Needing In-Game Validation

These cannot be confirmed without loading the game:

1. **`scope:recipient.leader_country ?= { prev.prev.var:tv_diplomatic_supporter_of = this }`** — this triple-scope chain in `can_join_trigger` may not resolve correctly. Alternative: flatten to a simpler check.
2. **`has_levels = yes`** on custom IO laws — only confirmed usage in vanilla is HRE `monetary_contribution`. May not behave as expected on non-HRE IOs.
3. **`prev.local_var:tv_rep_bonus`** in on_action — cross-scope local_var reference. Vanilla uses `root.local_var:` but `prev.local_var:` is untested.
4. **`on_activate` cohesion deduction** — human player can force-pass a vote even with insufficient cohesion (deduction goes negative). No guard in `on_activate`. Might need a trigger check.
5. **Policy `country_modifier` on IO laws** — confirmed vanilla pattern (HRE golden_bull uses `country_modifier` with `potential_trigger`). Our usage omits `potential_trigger`, meaning ALL members get the bonus (intended).

## Design Decisions (Not Bugs)

- Support is one-time, non-transferable (once a country supports someone, it can never support another)
- Cohesion can theoretically go negative if a vote is forced through — this is considered acceptable as it creates a "debt" that must be repaid before next upgrade
- The IO uses `has_parliament = no` — law changes go through the standard `policy_vote` resolution system which works for all IOs regardless of parliament setting
- Alliance tier is stored on both the IO (`international_organization:tv_diplomatic_alliance.var:tv_alliance_tier`) and the leader country (`var:tv_alliance_tier`) for trigger access
