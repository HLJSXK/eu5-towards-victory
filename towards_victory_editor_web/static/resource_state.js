function copy(value) {
  if (value === undefined) return undefined;
  if (typeof structuredClone === "function") return structuredClone(value);
  return JSON.parse(JSON.stringify(value));
}

function equal(left, right) {
  return JSON.stringify(left) === JSON.stringify(right);
}

export function resourceBase(payload) {
  return Object.fromEntries(payload.change_set.base.map(({ path, sha256 }) => [path, sha256]));
}

const disabledControls = new WeakMap();
export function setControlsBusy(controls, busy) {
  for (const control of controls) {
    if (busy) {
      if (!disabledControls.has(control)) disabledControls.set(control, control.disabled);
      control.disabled = true;
    } else if (disabledControls.has(control)) {
      control.disabled = disabledControls.get(control);
      disabledControls.delete(control);
    }
  }
}

// --- Shared tool indicators (WP-10) -------------------------------------------------------------
// DOM-free registry for the tab-bar dirty dot and running-job marker. It lives in this module rather
// than shared.js because the cropper editor registers its dirty transitions from a VM test that loads
// only this file; shared.js paints the dots from these values.
const toolIndicators = new Map();
const indicatorListeners = new Set();

function ensureIndicator(tool) {
  let indicator = toolIndicators.get(tool);
  if (!indicator) {
    indicator = { dirty: false, jobs: 0 };
    toolIndicators.set(tool, indicator);
  }
  return indicator;
}

// An entry exists only while it has something to show, so "add" and "remove" are observable.
function pruneIndicator(tool, indicator) {
  if (!indicator.dirty && indicator.jobs === 0) toolIndicators.delete(tool);
}

function notifyIndicator(tool) {
  for (const listener of indicatorListeners) listener(tool, toolIndicator(tool));
}

export function toolIndicator(tool) {
  return toolIndicators.get(tool) || { dirty: false, jobs: 0 };
}

export function setToolDirty(tool, dirty) {
  const indicator = ensureIndicator(tool);
  const next = dirty === true;
  if (indicator.dirty === next) return false;
  indicator.dirty = next;
  pruneIndicator(tool, indicator);
  notifyIndicator(tool);
  return true;
}

export function setToolJobs(tool, jobs) {
  const indicator = ensureIndicator(tool);
  const next = Math.max(0, Number(jobs) || 0);
  if (indicator.jobs === next) return false;
  indicator.jobs = next;
  pruneIndicator(tool, indicator);
  notifyIndicator(tool);
  return true;
}

export function dirtyToolNames() {
  return [...toolIndicators].filter(([, indicator]) => indicator.dirty).map(([tool]) => tool).sort();
}

export function runningToolNames() {
  return [...toolIndicators].filter(([, indicator]) => indicator.jobs > 0).map(([tool]) => tool).sort();
}

export function subscribeToolIndicators(listener) {
  indicatorListeners.add(listener);
  return () => indicatorListeners.delete(listener);
}

export function resetToolIndicators() {
  const tools = [...toolIndicators.keys()];
  toolIndicators.clear();
  for (const tool of tools) notifyIndicator(tool);
}

export class ResourceState {
  constructor({ base = {}, saved = {}, draft = saved, isDirty = (saved, draft) => !equal(saved, draft),
    onChange = () => {}, onDirtyChange = () => {} } = {}) {
    this.isDirty = isDirty;
    this.onChange = onChange;
    this.onDirtyChange = onDirtyChange;
    this.base = copy(base);
    this.saved = copy(saved);
    this.draft = copy(draft);
    // The initial value is reported through the constructor, never as a transition: callers pass
    // onDirtyChange inline while the surrounding object literal may still be unassigned.
    this.dirty = this.isDirty(this.saved, this.draft);
    this.phase = "idle";
    this.error = null;
    this.generation = 0;
    this.revision = 0;
  }

  get busy() {
    return this.phase !== "idle";
  }

  // Only a real transition notifies, so repeated edits cannot flood the indicator registry.
  _setDirty(dirty) {
    if (this.dirty === dirty) return false;
    this.dirty = dirty;
    this.onDirtyChange(dirty, this);
    return true;
  }

  replace({ base = this.base, saved = {}, draft = saved } = {}) {
    this.revision += 1;
    this.base = copy(base);
    this.saved = copy(saved);
    this.draft = copy(draft);
    this._setDirty(this.isDirty(this.saved, this.draft));
    this.onChange(this);
  }

  reset(resource) {
    // Abandons any in-flight request (its result is ignored) and installs a resource.
    // Unlike replace(), this also returns the state to idle.
    this.generation += 1;
    this.phase = "idle";
    this.error = null;
    this.replace(resource);
  }

  setDraft(draft) {
    if (this.busy) return false;
    this.draft = copy(draft);
    this._setDirty(this.isDirty(this.saved, this.draft));
    this.onChange(this);
    return true;
  }

  mutate(change) {
    if (this.busy) return false;
    const draft = copy(this.draft);
    change(draft);
    this.draft = draft;
    this._setDirty(this.isDirty(this.saved, this.draft));
    this.onChange(this);
    return true;
  }

  async run(phase, operation, { apply } = {}) {
    if (this.busy) return undefined;
    const generation = ++this.generation;
    const revision = this.revision;
    this.phase = phase;
    this.error = null;
    try {
      this.onChange(this);
      let result;
      try {
        result = await operation();
      } catch (error) {
        if (generation !== this.generation || revision !== this.revision) return undefined;
        throw error;
      }
      if (generation !== this.generation || revision !== this.revision) return undefined;
      if (apply) apply(result);
      return result;
    } catch (error) {
      if (generation !== this.generation) return undefined;
      this.error = error;
      throw error;
    } finally {
      if (generation === this.generation) {
        this.phase = "idle";
        this.onChange(this);
      }
    }
  }
}

export class JobPoller {
  constructor({ fetchJob, onUpdate, onError, delay = 700, schedule = (callback, ms) => globalThis.setTimeout(callback, ms), cancel = (timer) => globalThis.clearTimeout(timer) }) {
    this.fetchJob = fetchJob;
    this.onUpdate = onUpdate;
    this.onError = onError;
    this.delay = delay;
    this.schedule = schedule;
    this.cancel = cancel;
    this.jobId = null;
    this.cursor = 0;
    this.lines = [];
    this.error = null;
    this.timer = null;
    this.generation = 0;
    this.revision = 0;
    this.active = false;
  }

  start(job) {
    this.stop();
    this.jobId = job.operation.id;
    this.cursor = 0;
    this.lines = [];
    this.error = null;
    const generation = ++this.generation;
    this.accept(job, generation);
  }

  stop() {
    if (this.timer !== null) this.cancel(this.timer);
    this.timer = null;
    this.generation += 1;
    this.active = false;
  }

  isCurrent(jobId, generation) {
    return this.jobId === jobId && this.generation === generation;
  }

  accept(job, generation = this.generation) {
    const operation = job.operation;
    if (!this.isCurrent(operation.id, generation) || job.line_cursor < this.cursor) return false;
    if (this.timer !== null) this.cancel(this.timer);
    this.timer = null;
    this.lines = (job.lines_reset ? job.lines : [...this.lines, ...job.lines]).slice(-300);
    this.cursor = job.line_cursor;
    this.error = operation.error || null;
    this.revision += 1;
    this.active = ["queued", "running", "cancelling"].includes(operation.status);
    // Schedule before rendering so a render exception cannot strand an active job.
    if (this.active) this.schedulePoll(generation);
    this.onUpdate({ ...job, lines: this.lines });
    return true;
  }

  schedulePoll(generation = this.generation) {
    if (this.timer !== null) this.cancel(this.timer);
    this.timer = this.schedule(() => { void this.poll(generation); }, this.delay);
  }

  async poll(generation = this.generation) {
    const jobId = this.jobId;
    const cursor = this.cursor;
    const revision = this.revision;
    if (!jobId || !this.active || !this.isCurrent(jobId, generation)) return;
    if (this.timer !== null) this.cancel(this.timer);
    this.timer = null;
    let job;
    try {
      job = await this.fetchJob(jobId, cursor);
    } catch (error) {
      if (!this.isCurrent(jobId, generation) || this.revision !== revision) return;
      this.error = error;
      const retrying = !error.status || error.status >= 500 || [408, 429].includes(error.status);
      if ([404, 410].includes(error.status)) this.stop();
      this.onError(error, retrying);
      if (retrying) this.schedulePoll(generation);
      return;
    }
    if (!this.isCurrent(jobId, generation) || this.revision !== revision) return;
    try {
      this.accept(job, generation);
    } catch (error) {
      // onUpdate failed after the job was accepted; surface it instead of dropping it.
      this.error = error;
      this.onError(error, this.active);
    }
  }
}
