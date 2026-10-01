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

The Wonder preview API includes a `generation_plan` with ordered steps, dependency
edges, declared outputs and per-step timeouts. Commit runs this prepared DAG using
`sys.executable`, validates each step and the final artifact set, and returns a `generation` report
with an operation ID, step status/return code/duration, hashes and file changes.
The existing scope is 23 scripts / 22 outputs for mechanics changes, 22 scripts
for a cost/reward catalog change that leaves `unique_wonders.yaml` unchanged, or
two localization scripts / outputs. `regenerate: false` skips plan resolution and
artifact checks. GUI merges explicitly depend on their fragments and serialize
writes to the shared organization panel. A plan adds the upstream dependencies of
its roots and every downstream generator that depends on a planned step or reads
one of its outputs, so a partial plan cannot leave a merge step stale.

Each generator has a 120-second timeout by default; a timeout terminates and
waits for the child process before recovery, marks the step `timed_out`, retains
captured output in the log and skips the remaining steps. The plan and generation
report are currently exposed through the API only; the Wonder page does not render them.

The shared artifact module validates media headers and generated text formats.
TXT/GUI checks cover UTF-8, nonempty content and balanced strings/braces, and
require BOM under `common/`, `events/` and `gui/`. Intermediate files under
`data/generated_fragments/` need not have BOM;
localization YML checks include BOM, language header, quoted physical lines and
duplicate keys, allowing the literal interior quotes used by the game.
These checks do not validate all Jomini semantics or references.
Missing or invalid outputs fail the commit and trigger source/output recovery.
An HTTP 500 generation failure includes the attempted artifact report and a
separate `rollback` status/errors field; artifacts in that report describe the
attempt before rollback. The DAG declares direct GUI file dependencies, not the
complete transitive data/Python dependency graph; roots are selected per
change source (localization, cost/reward catalog, or full mechanics).

`tests/test_generation_plan.py` runs all 23 Wonder generators in a temporary
repository copy and compares the 22 outputs byte-for-byte with the working-tree
outputs, including BOM, so generated files must be current with their data. This
regression requires the local reference game/mod inputs used by the generators
to be available.

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

`media.wonder_crop` and `media.wonder_image` declare the `editor.wonder`,
`editor.wonder_crop`, and `editor.cost_reward` resource dependencies. Other handlers declare files and formats but have no editor
resource dependency registered yet. Wonder rebuild resolves current generator
configuration and task data, PNG sources, and DDS-only sources; both full DDS
and PNG-backed cropped DDS variants are declared. Web rebuilding has one entry,
`media.wonder_crop`; the image generator no longer accepts the Web
`convert_existing_assets` option. The CLI rebuild flag calls the same resolved
conversion functions.

Jobs run under one media execution lock. Both Wonder jobs acquire the
`editor.wonder`, `editor.wonder_crop`, and `editor.cost_reward` resource locks.
Wonder commits that regenerate acquire `editor.wonder` and `editor.cost_reward`;
commits with regeneration disabled acquire only `editor.wonder`. Crop commits
acquire `editor.wonder_crop`. Cost/reward commits that edit catalog categories
acquire `editor.cost_reward` and `editor.wonder`; task-pool-only commits acquire
only `editor.cost_reward`. Cost/reward saves also rewrite the
derived ceremony values in `data/unique_wonders.yaml` and regenerate the
affected Wonder outputs in the same recovery transaction, then refresh the
resident Wonder service catalog. The rewrite is re-parsed and checked against
the candidate catalog before anything is written. Category saves check the base
of all three files; task-pool-only saves ignore `unique_wonders.yaml`, so a
Wonder save does not make them conflict. A busy commit
returns HTTP 409, and a job that encounters a busy resource fails before
writing. These locks coordinate
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
