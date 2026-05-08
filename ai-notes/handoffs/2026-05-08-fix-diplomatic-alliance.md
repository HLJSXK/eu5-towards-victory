# Handoff: Fix Diplomatic Alliance CR Issues

Please read `ai-notes/reviews/2026-05-08-diplomatic-alliance-cr.md` and fix the diplomatic alliance implementation.

## Priority

1. Fix P0 localization load failure.
2. Fix P1 issues that can break IO variables, policy gating, and supporter/IO ownership logic.
3. Verify or replace P2 modifier names against vanilla `modifier_type_definitions`.

## Expected Output

- Explain how each CR item was handled.
- List any remaining items that require in-game validation.
- If generated victory files need to change, update the YAML/source and regenerate through the project generator rather than hand-editing generated outputs.

## Files Likely In Scope

- `src/main_menu/localization/simp_chinese/tv_diplomatic_alliance_l_simp_chinese.yml`
- `src/in_game/common/international_organizations/tv_diplomatic_alliance.txt`
- `src/in_game/common/laws/tv_alliance_laws.txt`
- `src/in_game/common/country_interactions/tv_seek_diplomatic_support.txt`
- `src/in_game/common/on_action/tv_diplomatic_alliance.txt`
- `data/victory_paths.yaml`
- `scripts/gen_victory.py`
