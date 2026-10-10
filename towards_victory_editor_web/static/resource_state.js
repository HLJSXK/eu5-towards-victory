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

export class ResourceState {
  constructor({ base = {}, saved = {}, draft = saved, isDirty = (saved, draft) => !equal(saved, draft), onChange = () => {} } = {}) {
    this.isDirty = isDirty;
    this.onChange = onChange;
    this.base = copy(base);
    this.saved = copy(saved);
    this.draft = copy(draft);
    this.dirty = this.isDirty(this.saved, this.draft);
    this.phase = "idle";
    this.error = null;
    this.generation = 0;
    this.revision = 0;
  }

  get busy() {
    return this.phase !== "idle";
  }

  replace({ base = this.base, saved = {}, draft = saved } = {}) {
    this.revision += 1;
    this.base = copy(base);
    this.saved = copy(saved);
    this.draft = copy(draft);
    this.dirty = this.isDirty(this.saved, this.draft);
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
    this.dirty = this.isDirty(this.saved, this.draft);
    this.onChange(this);
    return true;
  }

  mutate(change) {
    if (this.busy) return false;
    const draft = copy(this.draft);
    change(draft);
    this.draft = draft;
    this.dirty = this.isDirty(this.saved, this.draft);
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
    this.jobId = job.id;
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
    if (!this.isCurrent(job.id, generation) || job.line_cursor < this.cursor) return false;
    if (this.timer !== null) this.cancel(this.timer);
    this.timer = null;
    this.lines = (job.lines_reset ? job.lines : [...this.lines, ...job.lines]).slice(-300);
    this.cursor = job.line_cursor;
    this.error = job.error || null;
    this.revision += 1;
    this.active = ["queued", "running", "cancelling"].includes(job.status);
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
