# Historical Image-to-Image Styling Pipeline

## Goal

Use a real historical image as the source image, then stylize that same image into
cartoon-like game art. The source composition, architecture, perspective, and period
details remain the authority. The pipeline does not ask an image model to invent a
replacement building or scene, so the result keeps historical weight while gaining a
clear illustration language.

The implementation in `scripts/style_historical_image.py` is deterministic and local.
This makes it suitable for asset review and regeneration without an API token. A fixed
seed controls only the subtle paper grain; the same input and options produce the same
output.

## Processing stages

1. Resize the long edge to 1920 px by default and normalize the 1.2/99.2 percentile
   range. This gives the source a usable tonal range without changing its crop.
2. Apply edge-aware smoothing so photographic noise is reduced across flat areas while
   architectural silhouettes and important lines remain legible.
3. Apply a warm ivory highlight and cool blue-black shadow split, a gentle S-curve, and
   a restrained saturation lift. This supplies the historical, painted tonal register.
4. Reduce the image to a compact 56-color palette. Broad color masses read as designed
   art instead of a photo with a filter.
5. Apply nine cel-shaded luminance bands and dark blue ink contours around broad forms.
   Small photographic texture is softened rather than outlined.
6. Add weak highlight bloom, very light paper grain, and a 10% edge vignette. These
   finish the asset without adding scene content.

## Run

Install the image-only dependencies once:

```bash
python -m pip install -r requirements-image.txt
```

Process both test photographs in one reproducible run:

```bash
python scripts/style_historical_image.py \
  assets/historical/Taj-Mahal.jpg \
  assets/historical/Bordeaux_-_Le_port_et_colonnes_rostrales.jpg \
  --output-dir assets/historical/processed \
  --keep-intermediates \
  --seed 17
```

For a single source, pass one path. `--max-size` controls the long edge and should be
set to the target texture budget. Keep the same `--seed` when comparing style changes.

For API image-to-image styling, use the dedicated batch entry point. It uploads
each source image to the configured edits endpoint and keeps every result in the
historical asset directory:

```bash
python scripts/generate_historical_images.py
```

The root `generate_dds_icon_config.json` is the only configuration entry point.
The `historical_images` section contains the two source/output mappings, the edit
endpoint, model, API key setting, and `overwrite`. Set `overwrite` to `true` to
regenerate existing files; otherwise existing output files are skipped. This
workflow does not create DDS files or modify project resources.

Each source produces:

- `<stem>_cartoon.png`: the stylized image, preserving the source aspect ratio.
- `<stem>_cartoon_comparison.jpg`: source and named processing stages in a contact sheet.
- `<stem>_cartoon_evaluation.json`: source hash, image statistics, literal pixel SSIM,
  and a low-frequency structural similarity guardrail.
- `<stem>_01_*.jpg` through `<stem>_06_*.jpg`: optional intermediate stages.

## Acceptance criteria

Review the comparison sheet and report together. A passing asset should satisfy all of
the following:

- The primary monument, skyline, waterway or harbor geometry remains recognizable.
- The source perspective and major historical forms are preserved; no invented scene
  content appears.
- Large value and color planes are easier to read at game-thumbnail size.
- The palette and contours look illustrated, while warm stone, aged paper, or other
  period materials retain their visual weight.
- `structure_similarity` is at least `0.60` for this strong cartoon profile. It compares
  smoothed, reduced images so captions and decorative frames do not dominate the score.
  `pixel_similarity` is retained for diagnosing aggressive changes, but is not the
  acceptance gate. Neither metric replaces visual inspection.

The checked-in test reports are generated from the two files under `assets/historical/`.
The Taj Mahal result retains the dome, four minarets, reflecting pool, and garden axis.
The Bordeaux result retains the river, quays, ships, rostral columns, period buildings,
and the source engraving's historical presentation.

If a future source has a poor crop or distracting frame, add a hand-authored crop or mask
before increasing global stylization. Global filters cannot reliably decide which
historical details are important.
