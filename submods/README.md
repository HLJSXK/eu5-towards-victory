# Compatibility Submods

`submods/` contains optional compatibility mods for named external mods. The
main `src/` mod stays canonical and does not carry external-mod compatibility
branches.

Management rules:

- Use one folder per external mod or tightly coupled external mod set.
- Include `.metadata/metadata.json` with dependencies on Towards Victory and
  the external mod.
- Only override files with a confirmed conflict. Do not copy an entire mod.
- Prefer generated conflict files for GUI and other whole-file overrides.
- Keep generated outputs registered in `data/generated_files.yaml`.
- Rebuild and validate a submod whenever either Towards Victory or the external
  mod updates the same overridden file.
- Submods may depend on assets, localization, and scripts from their declared
  dependencies; do not duplicate those resources unless they are themselves the
  conflicting file.

Current submods:

- `tv_meiou_and_taxes_compat`: compatibility for MEIOU and Taxes
  (`reference_mods/3735059838`, mod id `meiou_and_taxes`). It contains one game
  override, `in_game/gui/location_window.gui`, generated from the M&T file with
  the wonder location overlay injected. Since the wonder overlay is owned by
  the standalone `src_engineering_department/` mod (see repo root), this
  submod declares a dependency on `hades.towards_victory.great_project`,
  not on the main `hades.towards_victory` mod — main `src/` no longer touches
  `location_window.gui` at all.
- `tv_standard_of_living_compat`: compatibility for Standard of Living
  (`reference_mods/3698931463`, mod id `hades.sol`). Same shape as the M&T
  submod: one override, `in_game/gui/location_window.gui`, generated from
  Standard of Living's file with the wonder location overlay injected.
  Depends on `hades.towards_victory.great_project` and `hades.sol`.
- `tv_prosper_or_perish_compat`: compatibility for Prosper or Perish
  (`reference_mods/3613232232`, no declared mod id — its own metadata has
  `"id": ""`, so it cannot be declared as a formal dependency relationship;
  the submod's short description names it by Workshop id instead). It
  contains one override, `in_game/gui/encyclopedia_lateralview.gui`. Both TV
  and Prosper or Perish add their own Europedia sidebar tab via the same
  `GetVariableSystem`-toggle pattern (see `docs/knowledge/risk_cards/
  europedia.md`), each keyed on its own single-mod boolean variable
  (`tv_encyclopedia_active` / `pp_encyclopedia_active`); a plain "take one
  file whole" merge like the location_window.gui submods can't work here
  because both mods patch the *same* shared vanilla nav buttons. Instead
  `scripts/compat/gen_tv_prosper_or_perish_encyclopedia_lateralview.py`
  rewrites both tabs onto one shared variable
  (`tveu_compat_encyclopedia_active`) with distinct values (`'tv'`/`'pp'`),
  so the shared vanilla nav buttons only ever need a single `Clear(...)` and
  a single `Not(GetVariableSystem.Exists(...))` mutual-exclusion check.
  Depends on `hades.towards_victory.great_project`.
