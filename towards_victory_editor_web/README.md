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
The full Wonder plan is 41 scripts / 40 outputs. Wonder saves select roots
from the source files that actually changed; a cost/reward catalog change that
leaves `unique_wonders.yaml` unchanged runs six generators, including the editor
catalog, while a localization-only edit runs six generators / outputs. `regenerate: false` skips plan resolution and
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
complete transitive data/Python dependency graph. Semantic input groups select
roots from changed Wonder sources; the plan then includes required upstream and
downstream generators.

`tests/test_generation_plan.py` runs all 41 Wonder generators in a temporary
repository copy and compares the 40 outputs byte-for-byte with the working-tree
outputs, including BOM, so generated files must be current with their data. This
regression requires the local reference game/mod inputs used by the generators
to be available.

Media jobs are submitted through `/api/jobs` and expose status, bounded logs,
return codes, cancellation, artifact manifests, source snapshots, and output
validation at `/api/jobs/{job_id}`. All five runnable handlers implement
`validate` and `prepare`; preparation resolves configuration and tasks once
into a `ToolPlan` with input snapshots, required/optional output paths, and an
execution callback. CLI and Web use the same generator execution functions.

Handler-normalized options and `ToolResult` fields must be JSON serializable,
with finite numeric values. The job manager validates and detaches options before
creating a job, and validates and detaches results before publishing their fields.
Invalid results fail with a tool-specific diagnostic while still collecting actual
output artifacts and persisting the failed lifecycle and detail snapshots. Handler
cleanup cannot mutate the published result through references to nested metadata.

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
Wonder save does not make them conflict. A busy commit returns HTTP 409 with
`code: resource_busy`, and a job that encounters a busy resource fails before
writing. Victory Tree saves now also acquire `editor.victory_tree` without
waiting; concurrent saves receive HTTP 409 instead of queuing on the service
lock. Stale source snapshots return `code: resource_changed`. The Victory Tree,
cost/reward, and crop pages distinguish these cases and preserve unsaved edits.
These locks coordinate this server process only. External edits are detected by comparing input
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
with status, logs, cancellation, and artifact reports. Both resource commits
and media jobs expose the same `operation_id` and `operation` payload. The
payload contains the operation kind, resource IDs, lifecycle status, bounded
events, error/cancellation state, and timestamps. Commit failures carry their
own operation snapshot on the exception used to build the HTTP response.
Wonder and cost/reward generation reports use the commit's operation ID.
Jobs waiting for the media execution lock remain queued with no started_at;
busy resources fail before the operation starts. Terminal lifecycle states
cannot be overwritten by later start, completion, failure, or cancellation calls.
Both commits and jobs run through `platform.run_operation`, which owns resource
locking, lifecycle transitions and exception operation snapshots. Domain
callbacks retain validation, file transactions and cleanup; success is published
only after the callback and its cleanup finish. Media jobs still use the thread
pool and media execution lock, while commits remain synchronous. The production
module-level app opens its operation store during the FastAPI lifespan; the path
comes from `TV_EDITOR_OPERATION_STORE` or defaults to
`.editor_state/operations.sqlite3` (ignored by Git). `create_app()` without an
explicit store uses an in-memory store, while tests and embedded callers can
inject `OperationStore(<temporary path>)`. `GET /api/operations?limit=25&kind=media_job&status=failed` lists recent
operation summaries, and `GET /api/operations/{operation_id}` returns the full
snapshot, including lifecycle events. The list limit is 1–100; filters are optional.
Terminal operation snapshots are retained for 30 days from `finished_at`; active
operations are never pruned. Expired snapshots return 404 and no longer appear in
the recent list.
The media generator's separate `lines` log and job/artifact payload remain available
through `/api/jobs/{job_id}` after restart as well. Completed media jobs persist their
tool, options, bounded log lines, input snapshots, declared outputs, artifacts and
validation metadata alongside the operation snapshot, using the same 30-day terminal
retention policy. A restarted server can query these terminal details but does not
recreate handlers, resume execution or provide cancellation for archived jobs. The
in-memory job manager still owns live execution and cancellation; media job details
are unavailable for records written before this persistence slice.

Ordinary generator output events are persisted in batches no more often than every
0.5 seconds or 50 events. Lifecycle transitions and terminal diagnostics always
flush immediately, so a completed or failed operation has its final snapshot before
the response is published.

On startup, persisted operations left queued, running or cancelling are marked
failed with a restart-interruption diagnostic. This records uncertainty; it does
not replay work or roll back files. Inspect generated outputs before retrying.
If SQLite becomes unavailable during an operation, the live response includes
`persistence_error` and the file operation keeps its real outcome. The archive
is local to this workspace and does not provide cross-process locks or job recovery.

Media status, error, return code and timestamps derive from one operation
snapshot. Cancellation and completion are synchronized; repeated cancellation
requests are idempotent, queued cancellation is checked before acquiring resource
locks, and cancellation during handler cleanup still takes effect. Failure logs
are recorded before publishing the terminal state so polling receives the final
diagnostics. The failed/cancelled outcome is decided before the error callback
runs; a cancellation request arriving during the callback leaves the outcome
failed with cancel_requested set. A failing callback still publishes the
terminal state. Each operation can be executed only once.

Media job `operation.events` contain
lifecycle events; generator output is carried only in `lines`. Poll
`/api/jobs/{job_id}?after_line=<line_cursor>` to receive only new lines. Each
response includes `line_cursor` and `lines_reset`; when a cursor falls behind
the bounded log buffer, `lines_reset` is true and `lines` contains the latest
300 lines for replacement. Omitting `after_line` also returns the latest 300.

The image styling tool requires the packages in `requirements-image.txt`.
Generation tools that call an image API still require the API key configured
by their existing JSON configuration or environment variables.
