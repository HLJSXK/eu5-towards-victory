// Localization text renderer (WP-07). Shared by the localization editor; no DOM state, no page state.
//
// SUPPORTED — an approximate in-game preview of a localization value:
//   * `#tag content#!` color and style tags from the EU5 text-format tag catalog, nested, with the
//     single-letter colors, the named styles, the tabular column tags and the trigger pass/fail tags.
//     The tag name is read as everything up to the first non-alphanumeric character, which is what the
//     engine does; one separator space after the name is consumed as the delimiter.
//   * `$name$` variable placeholders, including the `$VALUE|+$` shaped ones.
//   * `[scope|command]` and `[expression]` localization function calls.
//   * `\n` (backslash + n, the only legal way to write a line break in a loc value) and a physical
//     newline, both drawn as a line break.
//
// NOT SUPPORTED — deliberately rendered as a neutral placeholder or as literal text, never faked:
//   * `@icon_name!` inline text icons. The real glyph comes from the engine's `font_icons.gui`
//     textures, and each icon carries its own native size, offset and fontsize scaling, so no faithful
//     preview is possible here. Icons render as a labeled chip instead of a bitmap.
//   * Custom localization function expansion. `[ShowBuildingTypeName('x')]`, `[army|e]`,
//     `Custom('block_name')` and `$var$` keep their literal form: resolving any of them needs a live
//     scope, a datacontext and trigger evaluation, none of which exist in this editor.
//   * Font, weight and layout fidelity. The preview uses the workspace font stack; tag colors are
//     approximations of the engine palette; tabular tags are not laid out in real columns;
//     `#TOOLTIP:$TAG$` breakdowns are not hoverable; `#indent_newline:N` marks the indent without
//     reproducing the engine's spacing.
//   * Anything gameplay-dependent. Nothing here evaluates triggers or picks a
//     `customizable_localization` block; the raw markup is what is shown.

import { escapeHtml } from "./display.js";

// The tag catalog from docs/technical/EU5_Modding_Knowledge_Base.md section 6.3 "Text Format Tag
// Catalog". `className` is the preview class; the keys are the exact tag names after `#`.
export const LOCALIZATION_TAGS = {
  R: { className: "loc-r", kind: "color" },
  G: { className: "loc-g", kind: "color" },
  Y: { className: "loc-y", kind: "color" },
  W: { className: "loc-w", kind: "color" },
  V: { className: "loc-v", kind: "color" },
  L: { className: "loc-l", kind: "color" },
  P: { className: "loc-p", kind: "color" },
  N: { className: "loc-n", kind: "color" },
  X: { className: "loc-x", kind: "color" },
  D: { className: "loc-d", kind: "color" },
  F: { className: "loc-f", kind: "color" },
  r: { className: "loc-r loc-lower", kind: "color" },
  g: { className: "loc-g loc-lower", kind: "color" },
  y: { className: "loc-y loc-lower", kind: "color" },
  bold: { className: "loc-bold", kind: "style" },
  italic: { className: "loc-italic", kind: "style" },
  weak: { className: "loc-weak", kind: "style" },
  high: { className: "loc-high", kind: "style" },
  T: { className: "loc-t", kind: "style" },
  subtle_name: { className: "loc-subtle-name", kind: "style" },
  col: { className: "loc-col", kind: "column" },
  col_t: { className: "loc-col loc-col-t", kind: "column" },
  col_m: { className: "loc-col loc-col-m", kind: "column" },
  trigger_pass: { className: "loc-pass", kind: "condition" },
  trigger_fail: { className: "loc-fail", kind: "condition" },
  indent_newline: { className: "loc-indent", kind: "layout" },
  TOOLTIP: { className: "loc-tooltip", kind: "tooltip" },
};

const NAME_CHAR = /[A-Za-z0-9_]/;
const PARAMETER_CHAR = /[^\s#!]/;

function isNameChar(ch) {
  return ch !== undefined && NAME_CHAR.test(ch);
}

function isParameterChar(ch) {
  return ch !== undefined && PARAMETER_CHAR.test(ch);
}

/**
 * Tokenize a localization value into flat segments plus degradation warnings.
 *
 * Supported: `#tag …#!` (nested), `$var$`, `[scope|command]`, `@icon!`, the literal `\n` escape and a
 * physical newline. Unsupported markup is never expanded — it becomes a placeholder segment or literal
 * text plus a warning. Unclosed markers degrade instead of throwing: the affected region runs to the
 * end of the value, the marker is reported through `warnings`, and the renderer still closes its markup.
 *
 * @param {string} text raw localization value (never contains a physical newline in a valid file)
 * @returns {{segments: Array<object>, warnings: Array<{type: string, index: number, raw: string}>}}
 */
export function parseLocalizationText(text) {
  const source = typeof text === "string" ? text : "";
  const segments = [];
  const warnings = [];
  let index = 0;
  let buffer = "";
  const flush = () => {
    if (buffer) {
      segments.push({ type: "text", text: buffer });
      buffer = "";
    }
  };
  const warn = (type, at, raw) => warnings.push({ type, index: at, raw });

  while (index < source.length) {
    const ch = source[index];
    if (ch === "\n" || ch === "\r") {
      flush();
      segments.push({ type: "newline" });
      index += 1;
      continue;
    }
    if (ch === "\\") {
      if (source[index + 1] === "n") {
        flush();
        segments.push({ type: "newline" });
        index += 2;
        continue;
      }
      buffer += ch;
      index += 1;
      continue;
    }
    if (ch === "#") {
      if (source[index + 1] === "!") {
        flush();
        segments.push({ type: "tag_close", raw: "#!", index });
        index += 2;
        continue;
      }
      let cursor = index + 1;
      let name = "";
      while (isNameChar(source[cursor])) {
        name += source[cursor];
        cursor += 1;
      }
      if (!name) {
        buffer += ch;
        index += 1;
        continue;
      }
      let parameter = "";
      // Only a colon followed by a real parameter starts one, so `#Y: 5` keeps its colon as content.
      if (source[cursor] === ":" && isParameterChar(source[cursor + 1])) {
        const start = cursor;
        cursor += 1;
        while (isParameterChar(source[cursor])) cursor += 1;
        parameter = source.slice(start, cursor);
      }
      const known = Object.hasOwn(LOCALIZATION_TAGS, name);
      if (!known) warn("unknown_tag", index, `#${name}${parameter}`);
      flush();
      segments.push({ type: "tag_open", name, parameter, known, raw: `#${name}${parameter}`, index });
      index = cursor;
      if (source[index] === " ") index += 1; // the separator space is the tag delimiter, not content
      continue;
    }
    if (ch === "$") {
      const end = source.indexOf("$", index + 1);
      if (end < 0) {
        flush();
        warn("unclosed_variable", index, source.slice(index));
        buffer += source.slice(index);
        index = source.length;
        continue;
      }
      const name = source.slice(index + 1, end);
      flush();
      segments.push(name
        ? { type: "variable", name, raw: source.slice(index, end + 1) }
        : { type: "text", text: "$$" });
      index = end + 1;
      continue;
    }
    if (ch === "[") {
      const end = source.indexOf("]", index + 1);
      if (end < 0) {
        flush();
        warn("unclosed_function", index, source.slice(index));
        buffer += source.slice(index);
        index = source.length;
        continue;
      }
      const inner = source.slice(index + 1, end);
      flush();
      const parts = inner.split("|");
      const command = parts.length > 1 ? parts.pop() : "";
      segments.push({ type: "function", scope: parts.join("|"), command, raw: source.slice(index, end + 1) });
      index = end + 1;
      continue;
    }
    if (ch === "@") {
      let cursor = index + 1;
      let name = "";
      while (isNameChar(source[cursor])) {
        name += source[cursor];
        cursor += 1;
      }
      if (name && source[cursor] === "!") {
        flush();
        segments.push({ type: "icon", name, raw: source.slice(index, cursor + 1) });
        index = cursor + 1;
        continue;
      }
      buffer += ch;
      index += 1;
      continue;
    }
    buffer += ch;
    index += 1;
  }
  flush();

  // Pair the open/close markers so an unclosed or stray tag is reported, not silently swallowed.
  const stack = [];
  for (const segment of segments) {
    if (segment.type === "tag_open") stack.push(segment);
    else if (segment.type === "tag_close") {
      if (stack.length) stack.pop();
      else warn("unmatched_close", segment.index, "#!");
    }
  }
  for (const open of stack) warn("unclosed_tag", open.index, `#${open.name}`);
  return { segments, warnings };
}

/**
 * Render a localization value to HTML for the editor preview.
 *
 * Every text run is escaped and only the preview's own wrapper spans are emitted, so a loc value can
 * never inject markup. Known tags become nested spans; an unknown tag is shown as its literal token so
 * a missing separator (`#Gfoo#!`, where the engine absorbs `foo` into the tag name) is visible instead
 * of silently dropping the text. A tag left open at the end of the value is closed here and marked
 * `loc-unclosed`. See the file header for the supported/unsupported scope.
 *
 * @param {string} text raw localization value
 * @returns {string} HTML string safe to assign to `element.innerHTML`
 */
export function renderLocalizationText(text) {
  const { segments } = parseLocalizationText(text);
  const parts = [];
  const stack = [];
  for (const segment of segments) {
    if (segment.type === "text") {
      parts.push(escapeHtml(segment.text));
    } else if (segment.type === "newline") {
      parts.push("<br>");
    } else if (segment.type === "tag_open") {
      if (!segment.known) {
        parts.push(`<span class="loc-unknown-tag" title="未知文本标记（会被引擎当作标记名的一部分）">${escapeHtml(segment.raw)}</span>`);
        stack.push({ span: false, name: segment.name });
      } else {
        const tag = LOCALIZATION_TAGS[segment.name];
        parts.push(`<span class="loc-tag ${tag.className}" data-tag="${escapeHtml(segment.raw.slice(1))}">`);
        stack.push({ span: true, name: segment.name, position: parts.length - 1, className: tag.className });
      }
    } else if (segment.type === "tag_close") {
      const open = stack.pop();
      if (open?.span) parts.push("</span>");
    } else if (segment.type === "variable") {
      parts.push(`<span class="loc-variable" title="运行时变量，预览不展开">$${escapeHtml(segment.name)}$</span>`);
    } else if (segment.type === "function") {
      parts.push(`<span class="loc-function" title="本地化函数，预览不展开">${escapeHtml(segment.raw)}</span>`);
    } else if (segment.type === "icon") {
      parts.push(`<span class="loc-icon" title="内联贴图，预览不渲染">@${escapeHtml(segment.name)}!</span>`);
    }
  }
  while (stack.length) {
    const open = stack.pop();
    if (!open.span) continue;
    parts.push("</span>");
    parts[open.position] = parts[open.position].replace('class="loc-tag ', 'class="loc-tag loc-unclosed ');
  }
  return parts.join("");
}

/**
 * Degradation warnings for one value, for the editor's inline diagnostics.
 *
 * @param {string} text raw localization value
 * @returns {Array<{type: string, index: number, raw: string}>} warning list, empty when the value is
 *   clean; a value using only supported markup always returns an empty list
 */
export function localizationTextWarnings(text) {
  return parseLocalizationText(text).warnings;
}

/**
 * Flatten a localization value to plain text (tags removed, `\n` kept as a real newline).
 *
 * Unsupported markup keeps its literal form here as well; use it for copy/paste and tooltips, not as a
 * faithful in-game string.
 *
 * @param {string} text raw localization value
 * @returns {string} plain text with no markup
 */
export function localizationTextPlainText(text) {
  return parseLocalizationText(text).segments.map((segment) => {
    if (segment.type === "text") return segment.text;
    if (segment.type === "newline") return "\n";
    if (segment.type === "tag_close") return "";
    if (segment.type === "tag_open") return segment.known ? "" : segment.raw;
    return segment.raw;
  }).join("");
}
