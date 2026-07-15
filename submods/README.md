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
  submod declares a dependency on `hades.towards_victory.engineering_department`,
  not on the main `hades.towards_victory` mod — main `src/` no longer touches
  `location_window.gui` at all.
