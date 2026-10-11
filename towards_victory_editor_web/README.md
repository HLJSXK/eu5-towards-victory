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

All five frontends use `fetchJson` from `static/api.js`, directly or through shared components. It returns
JSON on success and throws `ApiError` for HTTP errors, retaining `status`,
`detail`, `code`, `operation_id`, `operation`, `generation`, and `log_text`.
Its message combines shared guidance with the server diagnostic for `resource_busy`
and `resource_changed`; `detail` retains the raw diagnostic. The changed-input
guidance applies to both editors and media jobs. Non-JSON error bodies are read once.

`static/display.js` provides shared log/status views, tabs, HTML escaping and
operation/generation diagnostics. `static/editor_panel.js` owns the cost/reward,
Victory Tree and Wonder load/reload/save workflow. Save first calls the resource's
`/preview` and shows the server diff in a confirmation dialog; returning to edit
or pressing Escape keeps the draft and base. Editing stays frozen from preview
through confirmation and commit, and both requests use the same serialized body.
Field changes show their path, item, field and before/after values; the derived
Wonder source change in cost/reward is a file-hash row labeled as a file summary.
Commit success and errors render operation IDs and any generation/recovery report.

`static/wonder_editor.js` adapts that workflow to Wonder: it caches the current
page before freezing edits and adds `regenerate` and `current_wonder_id` to the
request. Bootstrap publishes the summary before loading the first detail;
reload publishes the summary and hydrated current detail together, retaining
the old base, details and all page drafts if either request fails. After a
successful commit, the new base and cleared drafts take effect immediately.
If loading the detail's option catalog then fails, the page reports that the
save succeeded and offers a detail-only retry without another commit.
`createLatestLogView` keeps the server log, latest operation report and latest
diagnostic separately; copying the log includes all three. Detail retries keep
the save report. Wonder's forms retain toast, dirty counts and keyboard shortcuts,
and now add an unsaved-edit unload guard.

`static/job_panel.js` owns media/cropper status, logs, polling Retry/Stop controls
and input/output reports; media cancellation uses the same panel. The pages
retain their own forms and resource edits. Operation prompts are Chinese, while technical IDs,
paths, field names and server diagnostics retain their original text. Common
buttons, logs, job styles and preview styles live in `static/shared.css`.

The default address is `http://127.0.0.1:8760/`. Use `--host`, `--port`, or
omit `--no-browser` when a browser tab should open automatically. The older
standalone cropper server and its port no longer exist. Crop settings use the
resource API; image reads use `/api/cropper/image/*`, and DDS rebuilds use the
shared job API.

Run the server checks without starting Uvicorn:

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe -m towards_victory_editor_web --check
```

`services/wonder_resource.py` exposes `WonderResourceService` and owns resource
loading, snapshots and validation. `wonder_preview.py` builds candidate source
bytes shared by preview and commit, and `wonder_commit.py` runs the existing
commit transaction and generation lifecycle. The Wonder domain lives in
`services/wonder/`; resource, preview and commit import its modules directly.
The former `services/wonder_localization.py` has been removed.

| Module | Responsibility |
| --- | --- |
| `sources.py` | Source paths, input groups, ritual design/Prompt loading and source validation |
| `values.py` | YAML and structured editor value conversions |
| `options.py` | Localized option catalogs and catalog references |
| `site_templates.py` | Site condition atoms, preference presets and template signatures |
| `site_rules.py` | Site trigger/preference parsing and rendering |
| `localization.py` | Canonical keys, validation and generated-output checks |
| `field_types.py` | Field specifications and API serialization |
| `fields.py` | Field construction with explicit source data and catalog arguments |
| `model.py` | Edit application and summary/detail/ritual queries |

`WonderModel` calls the field builders without owning their implementation.
The option catalog has one active implementation of each builder, using the
cost/reward database alongside the existing reference labels.

Wonder `/preview` compares parsed candidate bytes with the actual source files.
Its `diff` contains semantic rows with `wonder_id`, `wonder_key`, `scope`,
`language`, `field`, `value_kind`, `before`/`after` and presence flags. Values are
the normalized source values: multiline text/scripts preserve newlines, mapping
and sequence fields display as indented JSON, and absent fields are distinct
from empty strings or null. Editor option catalogs are excluded. A prototype
selection reports both written fields, `base_key` and `mechanic_key`.
`file_diff` separately lists changed source hashes. Preview does not run
generators; actual generated-artifact hashes and changes appear in the commit
report.

The Wonder preview API also includes a `generation_plan` with ordered steps, dependency
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
captured output in the log and skips the remaining steps. The full plan remains
available through the API. The Wonder page's shared log renders generation step
results, artifact changes and recovery diagnostics.

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
Staging starts as a copy of the existing outputs, so an optional output the
handler deletes in staging (for example a PNG with `keep_png: false`) is deleted
from its formal path when a successful job publishes; failed jobs publish nothing.

`media.wonder_crop` and `media.wonder_image` declare the `editor.wonder`,
`editor.wonder_crop`, and `editor.cost_reward` resource dependencies.
`media.dds_icon` declares `editor.wonder` and `editor.cost_reward`, because its
Wonder building batch reads those editors' source files. Other handlers declare files and formats but have no editor
resource dependency registered yet. Wonder rebuild resolves current generator
configuration and task data, PNG sources, and DDS-only sources; both full DDS
and PNG-backed cropped DDS variants are declared. Web rebuilding has one entry,
`media.wonder_crop`; the image generator no longer accepts the Web
`convert_existing_assets` option. The CLI rebuild flag calls the same resolved
conversion functions.

Jobs run under one media execution lock. Both Wonder jobs acquire the
`editor.wonder`, `editor.wonder_crop`, and `editor.cost_reward` resource locks.
Wonder commits always acquire `editor.wonder` and `editor.cost_reward`, including
commits with regeneration disabled, because they may still write shared sources. Crop commits
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
cost/reward, Wonder, and crop pages distinguish these cases and preserve unsaved edits.
`static/resource_state.js` owns each editor's saved data, draft, dirty flag, base,
request phase and error. Loading and saving freeze edits, selection and duplicate
requests; successful responses replace the draft and base together. Ritual Prompt
edits use the Wonder page's unified save and resource preview/commit;
there is no separate Prompt save API.
`ResourceState.replace` updates resource data and revision without ending a request;
`reset` explicitly invalidates a pending request when an external resource is selected.
`run` owns request completion and reports apply/render errors.
Media and cropper share cursor polling with transient-error retries, stale-response
isolation and visible job errors. A 404/410 stops tracking and unlocks the page while
retaining the job ID, logs and query error. Other query failures offer retry and
Stop tracking; stopping tracking does not cancel the server job or declare its outcome.
These locks coordinate this server process only. Media jobs compare declared
input snapshots before execution and after handler cleanup, including inputs
that are also declared outputs. Their generated replacements stay in staging
until publication.

Media generators write declared outputs to a job-local staging directory.
After execution and handler cleanup, declared formats and required outputs are
validated before the staged files are published to their formal paths. Existing formal files are
backed up so a failure during multi-file publication can restore them. Staged
writes are discarded on failure, cancellation, missing outputs, format errors,
or stale inputs; the job retains the attempted manifest and validation results.
Each formal file is checked against its snapshot immediately before replacement;
a conflict restores earlier replacements. Missing optional staged files leave
their formal files intact. A rollback failure retains the original diagnostic.
Only declared files are compared; their parent directories are not scanned.
Input changes cause a conflict. Changes to declared formal outputs outside
staging block publication and appear in `formal_output_changes`; their writer
is unknown, so the job leaves them for review instead of restoring a backup
over them. Arbitrary undeclared formal paths are not monitored; write auditing
is a separate TODO in the refactor status.

`staging_extra_files` lists intermediate files excluded from publication and
removed during normal staging cleanup. They do not trigger a partial-output
warning. `outputs_may_be_partial` is true for `formal_output_changes`,
publication rollback failure, or an interrupted operation that started running.
Cancellation takes precedence over stale-input diagnostics. Media studio shows
inputs, declared outputs, file changes, intermediate files, and validation
errors. If publication rollback itself fails, the job
sets `publication_rollback_failed`, preserves the backup directory, and reports
the files that could not be restored. A service interruption may leave formal
files partially published and backups under `.editor_state/media-*/.backup`;
the UI asks for manual review. Startup recovery and cleanup are not implemented
and are tracked separately in the refactor status TODOs.
This slice does not provide a complete resource DAG or cross-process locking.

The data editors and crop configuration editor are registered in the same tool
catalog as interactive tools. They use resource load/validate/preview/commit
operations for source changes; media generation remains an asynchronous job
with status, logs, cancellation, and artifact reports. Resource commits and
media jobs expose an `operation` payload containing the operation kind, resource
IDs, lifecycle status, bounded events, error/cancellation state, and timestamps.
Job lifecycle fields stay under `operation`; job-specific logs, cursors and
artifact reports remain at the top level. Commit responses and failures also
include an `operation_id` for convenient correlation.
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
`.editor_state/operations.sqlite3` (ignored by Git). Opening a persistent operation
store acquires an OS file lock;
a second owner is rejected before recovery can alter running records. Each lifespan
creates its own `JobManager`; a closed manager rejects submission. Shutdown cancels
queued futures and persists their cancelled state, requests cooperative cancellation
for running jobs, and waits for terminal persistence before closing the store.
Image generators check cancellation between tasks and requests; retry delays can
be interrupted. Crop conversion dispatches only enough work for its active workers
and stops dispatching on cancellation, waiting for active conversions before staging
cleanup. An already blocked request or conversion must still return; image request
timeouts default to 180 seconds, so shutdown has no fixed time limit.
`create_app()` without an explicit store uses an in-memory store, while tests and embedded callers can
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
