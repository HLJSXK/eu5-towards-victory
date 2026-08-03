# Wonders / Engineering Department Risk Card

Load this top-level card before editing files whose names contain `wonder` or
`engineering_department`. Use the narrower routed cards when the touched object
or file type matches them.

## Current Architecture

- The Engineering Department / Wonder Construction subsystem is a standalone mod
  root at `src_engineering_department/`, mirrored by `scripts_engineering_department/`.
  It depends on CMF 2.x, not on the main `src/` mod.
- The main Towards Victory mod depends on Engineering Department because
  Prosperity Victory calls `tv_engineering_department_create_effect`.
- Wonder data remains in repo-root `data/`; generated source is emitted under
  `src_engineering_department/`.
- Shared singleton copies such as `character_title.txt` and `messagetypes.txt`
  are generated as full vanilla copies per deployable root. Do not hand-edit them.

## Always-Apply Rules

1. Keep local and national effects separate.
   Final/helper building `modifier` and `raw_modifier` entries are local. National
   or global wonder effects must be applied through country modifiers or
   generated country-auto paths, not through noncapital building modifiers.

2. Treat generated outputs as read-only.
   Check `data/generated_files.yaml` first. If a wonder source file is generated,
   edit the listed data file or generator and rerun the generator.

3. Keep the standalone root standalone.
   Engineering Department files must not rely on keys, trigger localization, message
   types, or helper definitions that exist only in the main `src/` root unless the
   dependency is explicit and guaranteed.

4. Keep CMF integration centralized.
   Missing-Great-Engineer alerts, Wonder Control CMM registration, callbacks, GUI
   bridges, and action-log calls belong to the Engineering Department root. Do not
   move them back into the main mod.

5. Avoid read-path repair fallbacks.
   This project is unreleased. Fix lifecycle initialization and generator state
   directly; do not add old-schema rebuilds, `*_if_needed` routers, or compatibility
   probes to GUI, tooltip, selection, monthly read, or cache refresh paths.

## Routed Detail Cards

- `docs/knowledge/risk_cards/object_on_built.md`: any `on_built` hook.
- `docs/knowledge/risk_cards/wonder_buildings.md`: building types, prices,
  modifier types, auto modifiers, construction completion, labor/input reads.
- `docs/knowledge/risk_cards/wonder_gui.md`: location window, Engineering
  Department panel, Europedia cards, tooltip/layout/icon routing.
- `docs/knowledge/risk_cards/wonder_ceremony.md`: shared ceremony stages, costs,
  option text, hidden scheduler, effect localization.
- `docs/knowledge/risk_cards/wonder_unique_rituals.md`: bespoke Pharos/Hagia
  ritual implementation and future unique-ritual authoring/audits.

## Validation

Run the generated-file owner first, then:

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\validate.py --changed --fix --ai-report
```

When changing scale-based wonder trigger/effect/building generators, also run:

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\test_wonder_mechanics_rules.py
```
