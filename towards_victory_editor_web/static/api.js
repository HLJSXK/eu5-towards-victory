function errorMessage(detail, code) {
  const diagnostic = typeof detail === "string" ? detail : JSON.stringify(detail);
  if (code === "resource_busy") {
    return `资源正在保存或生成中。请稍后重试。（${diagnostic}）`;
  }
  if (code === "resource_changed") {
    return `源文件已变化。请核对最新内容后重试。（${diagnostic}）`;
  }
  return diagnostic;
}

export class ApiError extends Error {
  constructor(status, payload, fallback) {
    const detail = payload?.detail ?? fallback;
    super(errorMessage(detail, payload?.code));
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
    this.code = payload?.code;
    this.operation_id = payload?.operation_id;
    this.operation = payload?.operation;
    this.generation = payload?.generation;
    this.log_text = payload?.log_text;
  }
}

export async function fetchJson(url, options) {
  const response = await fetch(url, options);
  if (response.ok) return response.json();

  // Read once so a non-JSON response keeps its original diagnostic.
  const text = await response.text();
  let payload;
  try {
    payload = JSON.parse(text);
  } catch {
    // Proxies and unhandled server errors can return plain text or HTML.
  }
  throw new ApiError(response.status, payload, text || response.statusText || `HTTP ${response.status}`);
}
