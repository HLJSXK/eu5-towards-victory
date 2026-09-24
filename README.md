# Towards Victory (胜利条件)

A mod for Europa Universalis V that adds generalized victory conditions — giving players clear goals and staged rewards without requiring per-nation content.

## Overview

EU5 intentionally omits any "winning" concept. While this preserves open-ended play, EU5's complexity makes it harder to maintain direction, especially in the mid-to-late game. This mod adds 6 universal victory paths:

| Path | Core metric | Example nations |
|---|---|---|
| **Conquest** | Total owned locations | Ottoman, Muscovy, Castile |
| **Prosperity** | Domestic development composite | Netherlands, Burgundy, England |
| **Trade** | Trade income share + node dominance | Venice, Portugal, Netherlands |
| **Diplomatic** | Accumulated diplomatic victory points | Small powers, HRE members |
| **Cultural** | Cultural influence points (artifacts, spread) | Italian city-states, France |
| **Scientific** | Weighted technology score (Age 5 emphasis) | Western European powers |

Each path has 4 milestones. Reaching a milestone triggers a popup event that grants a permanent reward (~1–3 Advances equivalent).

## Design Principles

- **Compatibility-first** — additive only; no vanilla files modified
- **All paths open** — every nation can pursue any path simultaneously
- **No time-limited buffs** — all rewards are permanent
- **Age 6 ceiling** — designed for completion before ~1700 CE

## Installation

1. Place the mod folder in your EU5 mods directory.
2. Enable `eu5mp.towards_victory` in the launcher.

## Development

This mod uses an AI coding infrastructure with knowledge docs and validation tooling.

**Before editing source files:**
```
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\validate.py --changed
```

**After editing knowledge files:**
```
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\gen_brief.py
```

Use `conda run --no-capture-output -n eu5 python ...` only from a normal user
terminal. Managed AI sandboxes should use the direct interpreter path above.

## Historical Image Assets

Historical illustrations start from a real source photograph or engraving. The
local post-processing pipeline keeps the source composition and applies a warm,
cool-shadow cartoon treatment with broad value planes, ink contours, and light
paper texture:

```bash
python -m pip install -r requirements-image.txt
python scripts/style_historical_image.py \
  assets/historical/Taj-Mahal.jpg \
  assets/historical/Bordeaux_-_Le_port_et_colonnes_rostrales.jpg \
  --output-dir assets/historical/processed \
  --keep-intermediates
```

For API image-to-image styling, run the dedicated batch entry point:

```bash
python scripts/generate_historical_images.py
```

The script always processes the two configured source images and writes
`*_ai_cartoon.png` files under `assets/historical/processed/`. Its only runtime
configuration is the `historical_images` section in the repository-root
`generate_dds_icon_config.json`: change the edit endpoint, API key setting, or
`overwrite`. Existing outputs are skipped while `overwrite` is `false`.
See [the historical image pipeline](docs/design/Historical_Image_Postprocessing_Pipeline.md)
for stages, review criteria, and generated evaluation reports.

**Mod ID:** `eu5mp.towards_victory` | **Version:** build date (`YYMMDD`) | **Target:** EU5 `1.*.*`
