# Diplomatic Alliance CR

Reviewer: GPT-5.5
Date: 2026-05-08
Scope: Claude implementation of the diplomatic alliance system

## Verdict

Do not merge yet. Several issues are likely to cause load failures or broken gameplay logic.

## P0

- `src/main_menu/localization/simp_chinese/tv_diplomatic_alliance_l_simp_chinese.yml`
  - YAML string has unescaped quotes:
  - `tv_diplo_alliance_support_unlocked_tt: "现在可以对友好国家使用"寻求外交支持"行动。"`
  - Fix by escaping inner quotes or replacing them with Chinese quotation marks.

## P1

- `src/in_game/common/international_organizations/tv_diplomatic_alliance.txt`
  - `variables` uses `initial_value = 0`, but vanilla examples use `start = 0`.
  - Change to `start = 0`; consider adding `min`, `max`, and `change_format`.

- `src/in_game/common/laws/tv_alliance_laws.txt`
  - Cohesion requirements are only in `wants_propose_policy`, so they affect AI preference but do not block activation.
  - Add real `allow` or `locked` checks for each policy level.

- `src/in_game/common/country_interactions/tv_seek_diplomatic_support.txt`
  - A country can switch support from one actor to another without decrementing the previous actor's support count.
  - Once the unique IO exists, any actor's new supporter can be added to the same global alliance.
  - `can_join_trigger` should verify supporter relationship to the alliance leader, not only `has_variable`.

## P2

- Verify modifier names against `modifier_type_definitions`.
  - Not found during CR: `legitimacy_gain_mult`, `diplomatic_range_mult`, `exploration_range_mult`, `counter_spy_network_construction`, `colonist_placement_chance`, `colonization_range_mult`, `colonization_growth_speed_modifier`.
  - Found during CR: `monthly_diplomats`, `diplomatic_capacity_modifier`, `diplomatic_spending_cost`, `diplomatic_range`, `monthly_prestige`, `spy_network_construction`, `diplomatic_reputation`.
  - `spy_network_construction = 10` may mean +1000% if it is a percent modifier.

## Notes

- `diplo_chance + accept` is supported by vanilla examples.
- `scope:recipient` inside IO law appears to refer to the international organization, consistent with vanilla usage.
- `set_variable = { name = tv_diplomatic_supporter_of value = scope:actor }` and `var:tv_diplomatic_supporter_of = scope:actor` have vanilla-style precedent for scope-valued variables.
- No files were modified by reviewer during CR.
- No in-game load validation was run.
