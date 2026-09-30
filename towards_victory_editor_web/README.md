# Towards Victory Web Workspace

The repository has one local web server for project editing and media work:

- cost/reward data editor;
- victory tree planner;
- wonder localization and mechanics editor;
- DDS icon generator;
- wonder image generator and DDS rebuild;
- deterministic historical image styling;
- configured historical image API batch;
- 27:11 wonder image cropper and DDS rebuild.

Start it with the managed project interpreter:

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m towards_victory_editor_web --no-browser
```

The default address is `http://127.0.0.1:8760/`. Use `--host`, `--port`, or
omit `--no-browser` when a browser tab should open automatically. The older
standalone cropper server and its port no longer exist. Crop settings use the
resource API; image reads use `/api/cropper/image/*`, and DDS rebuilds use the
shared job API.

Run the server checks without starting Uvicorn:

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m towards_victory_editor_web --check
```

Media jobs are submitted through `/api/jobs` and expose status, bounded logs,
return codes, cancellation, artifact manifests, source snapshots, and output
validation at `/api/jobs/{job_id}`. All five runnable handlers implement
`validate` and `prepare`; preparation resolves configuration and tasks once
into a `ToolPlan` with input snapshots, required/optional output paths, and an
execution callback. CLI and Web use the same generator execution functions.

Required inputs must exist during preparation, required outputs must exist
after execution, and declared outputs are checked for PNG/DDS/JPEG headers or
valid JSON. This is a file-level check, not full image decoding or domain schema
validation. Artifact collection only visits declared paths, including icon
metadata under `data/generated_icons`; unrelated directory changes are ignored.
Outputs that already exist are reported with `changed: false` when unchanged.

`media.wonder_crop` and `media.wonder_image` declare the `editor.wonder` and
`editor.wonder_crop` resource dependencies. Other handlers declare files and formats but have no editor
resource dependency registered yet. Wonder rebuild resolves current generator
configuration and task data, PNG sources, and DDS-only sources; both full DDS
and PNG-backed cropped DDS variants are declared. Web rebuilding has one entry,
`media.wonder_crop`; the image generator no longer accepts the Web
`convert_existing_assets` option. The CLI rebuild flag calls the same resolved
conversion functions.

Jobs run under one media execution lock. Both Wonder jobs also acquire the
`editor.wonder` and `editor.wonder_crop` resource locks, which Wonder and crop
commits take as well; a busy commit returns HTTP 409, and a job that encounters
a busy resource fails before writing. `data/cost_reward_units.yaml` is a
declared Wonder input but is not locked against cost/reward commits; a change is
reported as a stale input after execution. These locks coordinate
this server process only. External edits are detected by comparing input
snapshots before and after execution; in-place inputs (DDS conversion and icon
metadata updates) are checked before execution only.

Media generators write directly to their destinations. Failure, cancellation,
missing outputs, or stale inputs do not roll files back: the job retains the
manifest and validation results, lists `missing_outputs`, and sets
`outputs_may_be_partial` when planned output files changed. Cancellation takes
precedence over stale-input diagnostics. Media studio shows inputs, declared
outputs, file changes, and validation errors. Optional intermediate PNG files
are recorded if present after a failure; files created and removed within a run
are not retained. This slice does not provide a complete resource DAG, staged
publication, cross-process locking, or recovery of undeclared generator writes.

The data editors and crop configuration editor are registered in the same tool
catalog as interactive tools. They use resource load/validate/preview/commit
operations for source changes; media generation remains an asynchronous job
with status, logs, cancellation, and artifact reports.

The image styling tool requires the packages in `requirements-image.txt`.
Generation tools that call an image API still require the API key configured
by their existing JSON configuration or environment variables.
