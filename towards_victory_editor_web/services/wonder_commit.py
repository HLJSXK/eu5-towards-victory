from __future__ import annotations

from typing import Any

from .generation import GenerationError, run_generation
from .platform import (
    OperationLog,
    RollbackError,
    atomic_write_files,
    file_transaction,
    repo_relative_path,
    run_operation,
)
from .wonder import sources
from .wonder_generation import wonder_generation_plan


class WonderCommit:
    def commit_resource(
        self,
        drafts_by_wonder_id: dict[int, dict[str, Any]],
        base: dict[str, str] | None = None,
        *,
        current_wonder_id: int | None = None,
        regenerate: bool = True,
    ) -> dict[str, Any]:
        resource_ids = ("editor.wonder", "editor.cost_reward")
        operation = OperationLog("resource_commit", resource_ids, store=self.operation_store)

        def log(text: str) -> None:
            self._append_log(text)
            if text.strip():
                operation.event(text.strip())

        def commit() -> dict[str, Any]:
            # The executor acquires shared resources before this service lock.
            with self._lock:
                self._assert_base(base)
                target_wonder_id = current_wonder_id
                if target_wonder_id is None and drafts_by_wonder_id:
                    target_wonder_id = int(next(iter(drafts_by_wonder_id)))
                if target_wonder_id is not None:
                    self._get_wonder(target_wonder_id)
                changed, files, changed_wonder_ids = self._candidate_for_drafts(drafts_by_wonder_id)
                if not files:
                    payload = self.get_wonder_payload(target_wonder_id)
                    result = {**self._resource_payload(), "status": "No changes", "changed_files": [], "written_paths": [],
                              "changed_wonder_ids": [], "wonder": payload, "wonders": self.list_wonders(),
                              "generation": None,
                              "log_text": self.log_text}
                    return result

                groups = sources.wonder_input_groups(files)
                plan = wonder_generation_plan(
                    changed, repo_root=sources.REPO_ROOT, regenerate=regenerate,
                    input_groups=groups,
                )
                changed_files = [repo_relative_path(path, sources.REPO_ROOT) for path in files]
                # Candidate serialization and registry lookup may take time; recheck
                # the loaded base immediately before snapshotting and writing.
                self._assert_base(base)
                generation = None
                with file_transaction((*files, *plan.outputs), reload=self.reload_from_disk):
                    atomic_write_files(files)
                    if plan.steps:
                        generation = run_generation(plan, log=log, operation_id=operation.id)
                    self.reload_from_disk()
                    payload = self.get_wonder_payload(target_wonder_id)
                    status = f"Saved {len(changed_wonder_ids)} page{'s' if len(changed_wonder_ids) != 1 else ''}: {', '.join(changed_files)}"
                    if payload is not None:
                        payload["status"] = status
                    result = {
                        **self._resource_payload(),
                        "status": status,
                        "changed_files": changed_files,
                        "written_paths": changed_files,
                        "changed_wonder_ids": changed_wonder_ids,
                        "wonders": self.list_wonders(),
                        "wonder": payload,
                        "generation": generation,
                        "log_text": self.log_text,
                    }
                    return result

        try:
            result = run_operation(operation, commit)
            return {**result, "operation_id": operation.id, "operation": operation.payload()}
        except Exception as exc:
            original = exc.original if isinstance(exc, RollbackError) else exc
            if isinstance(original, GenerationError):
                original.report["rollback"] = {
                    "status": "incomplete" if isinstance(exc, RollbackError) else "succeeded",
                    "errors": exc.errors if isinstance(exc, RollbackError) else [],
                }
            self._append_log(f"[error] {exc}\n")
            raise
