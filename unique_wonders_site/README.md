# Unique Wonders Map Site

Static atlas for Towards Victory unique wonders.

The site reads the mod's authored wonder data and the map assets from
`reference_mods/national_destinies_site`, then writes a deployable static bundle
under `unique_wonders_site/dist`.

## Build

Run from the repository root:

```powershell
conda run --no-capture-output -n eu5 python unique_wonders_site/scripts/build/build_site.py
```

The first build copies the reference map tile pyramid into `dist/tiles`, then
generates `dist/data/locations_index.json` and `dist/data/unique_wonders.json`.

## Preview

```powershell
cd unique_wonders_site/dist
conda run --no-capture-output -n eu5 python -m http.server 8790
```

Then open `http://127.0.0.1:8790/`.

