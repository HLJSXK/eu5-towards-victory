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
return codes, cancellation, artifact manifests, and output-format validation at
`/api/jobs/{job_id}`. Every runnable tool implements the same `ToolHandler`
contract (`validate`, `roots`, `run`) and runs in-process through the shared
`JobManager`; the command-line entry points are thin adapters over the same
generator `run(options)` APIs. There is one option schema for the Web forms,
one execution lock for image writers, and one artifact snapshot/validation
path for PNG, DDS, JPEG, and JSON outputs.

The data editors and crop configuration editor are registered in the same tool
catalog as interactive tools. They use resource load/validate/preview/commit
operations for source changes; media generation remains an asynchronous job
with status, logs, cancellation, and artifact reports.

The image styling tool requires the packages in `requirements-image.txt`.
Generation tools that call an image API still require the API key configured
by their existing JSON configuration or environment variables.
