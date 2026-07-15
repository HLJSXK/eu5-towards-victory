from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import socket
import ssl
import sys
import time
import urllib.parse
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = REPO_ROOT / "data" / "unique_wonder_ritual_designs.yaml"
OUTPUT_FILE = REPO_ROOT / "data" / "unique_wonder_ritual_designs_zh.yaml"
GOOGLE_HOST = "translate.googleapis.com"
MAX_SEGMENT_CHARS = 2800
MAX_BATCH_CHARS = 3600
NON_TRANSLATED_RITUAL_FIELDS = {"mode", "listeners"}
IDENTIFIER_RE = re.compile(r"\b[a-z][a-z0-9]+(?:_[a-z0-9]+)+\b")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?;:])\s+")
SEPARATOR_RE = re.compile(r"<TVSEP\d+>")


class FoldedString(str):
    pass


def folded_string_representer(dumper: yaml.Dumper, data: FoldedString) -> yaml.Node:
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style=">")


yaml.SafeDumper.add_representer(FoldedString, folded_string_representer)


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"metadata": {}, "unique_wonders": []}
    payload = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a mapping")
    unique_wonders = payload.get("unique_wonders", [])
    if not isinstance(unique_wonders, list):
        raise TypeError(f"{path}.unique_wonders must be a list")
    return payload


def dump_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        yaml.safe_dump(
            data,
            allow_unicode=True,
            sort_keys=False,
            width=100,
            default_flow_style=False,
        ),
        encoding="utf-8",
    )


def parse_http_proxy(value: str) -> tuple[str, int]:
    parsed = urllib.parse.urlparse(value if "://" in value else f"http://{value}")
    if parsed.scheme != "http":
        raise ValueError("Only HTTP proxies are supported for Google Translate CONNECT requests")
    if not parsed.hostname or not parsed.port:
        raise ValueError(f"Proxy must include host and port: {value}")
    return parsed.hostname, int(parsed.port)


class GoogleTranslateClient:
    def __init__(self, proxy: str, *, timeout: float = 30.0, retries: int = 4, delay: float = 0.15) -> None:
        self.proxy_host, self.proxy_port = parse_http_proxy(proxy)
        self.timeout = timeout
        self.retries = retries
        self.delay = delay

    def translate_batch(self, texts: list[str]) -> list[str]:
        if not texts:
            return []
        if len(texts) == 1:
            return [self.translate_one(texts[0])]

        pieces: list[str] = []
        for index, text in enumerate(texts):
            if index:
                pieces.append(f"<TVSEP{index:04d}>")
            pieces.append(text)
        translated = self.translate_one("".join(pieces))
        split = SEPARATOR_RE.split(translated)
        if len(split) != len(texts):
            return [self.translate_one(text) for text in texts]
        return split

    def translate_one(self, text: str) -> str:
        text = text.strip()
        if not text:
            return ""
        params = urllib.parse.urlencode(
            {
                "client": "gtx",
                "sl": "en",
                "tl": "zh-CN",
                "dt": "t",
                "q": text,
            }
        )
        path = f"/translate_a/single?{params}"
        for attempt in range(1, self.retries + 1):
            try:
                body = self._get(path)
                payload = json.loads(body.decode("utf-8"))
                translated = "".join(part[0] for part in payload[0] if part and part[0])
                if self.delay:
                    time.sleep(self.delay)
                return translated
            except Exception:
                if attempt >= self.retries:
                    raise
                time.sleep(min(8.0, 0.75 * attempt * attempt))
        raise RuntimeError("unreachable translation retry state")

    def _get(self, path: str) -> bytes:
        raw_sock = socket.create_connection((self.proxy_host, self.proxy_port), timeout=self.timeout)
        try:
            connect = (
                f"CONNECT {GOOGLE_HOST}:443 HTTP/1.1\r\n"
                f"Host: {GOOGLE_HOST}:443\r\n"
                "Proxy-Connection: keep-alive\r\n"
                "\r\n"
            ).encode("ascii")
            raw_sock.sendall(connect)
            response_head = self._read_until_header_end(raw_sock)
            status_line = response_head.split(b"\r\n", 1)[0]
            if b" 200 " not in status_line:
                raise RuntimeError(f"Proxy CONNECT failed: {status_line.decode('latin-1', errors='replace')}")

            context = ssl.create_default_context()
            with context.wrap_socket(raw_sock, server_hostname=GOOGLE_HOST) as tls_sock:
                raw_sock = None
                request = (
                    f"GET {path} HTTP/1.1\r\n"
                    f"Host: {GOOGLE_HOST}\r\n"
                    "User-Agent: Mozilla/5.0\r\n"
                    "Accept: application/json,text/plain,*/*\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                ).encode("ascii")
                tls_sock.sendall(request)
                response = bytearray()
                while True:
                    chunk = tls_sock.recv(65536)
                    if not chunk:
                        break
                    response.extend(chunk)
        finally:
            if raw_sock is not None:
                raw_sock.close()

        head, _, body = bytes(response).partition(b"\r\n\r\n")
        status_line = head.split(b"\r\n", 1)[0]
        if b" 200 " not in status_line:
            raise RuntimeError(f"Google Translate failed: {status_line.decode('latin-1', errors='replace')}")
        headers = parse_headers(head)
        if headers.get("transfer-encoding", "").lower() == "chunked":
            body = decode_chunked_body(body)
        return body

    def _read_until_header_end(self, sock: socket.socket) -> bytes:
        response = bytearray()
        while b"\r\n\r\n" not in response:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response.extend(chunk)
            if len(response) > 65536:
                raise RuntimeError("Proxy response header too large")
        return bytes(response)


def parse_headers(head: bytes) -> dict[str, str]:
    headers: dict[str, str] = {}
    for line in head.split(b"\r\n")[1:]:
        if b":" not in line:
            continue
        key, value = line.split(b":", 1)
        headers[key.decode("latin-1").strip().lower()] = value.decode("latin-1").strip()
    return headers


def decode_chunked_body(body: bytes) -> bytes:
    decoded = bytearray()
    index = 0
    while index < len(body):
        line_end = body.find(b"\r\n", index)
        if line_end < 0:
            break
        size_line = body[index:line_end].split(b";", 1)[0]
        size = int(size_line.decode("ascii"), 16)
        index = line_end + 2
        if size == 0:
            break
        decoded.extend(body[index : index + size])
        index += size + 2
    return bytes(decoded)


def protect_identifiers(text: str) -> tuple[str, dict[str, str]]:
    replacements: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:
        original = match.group(0)
        marker = f"<TVID{len(replacements):04d}>"
        replacements[marker] = original
        return marker

    return IDENTIFIER_RE.sub(replace, text), replacements


def restore_identifiers(text: str, replacements: dict[str, str]) -> str:
    restored = text
    for marker, original in replacements.items():
        restored = restored.replace(marker, original)
    return restored


def sanitize_translation_text(text: str) -> str:
    return (
        text.replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
    )


def split_text(text: str) -> list[str]:
    text = str(text).strip()
    if len(text) <= MAX_SEGMENT_CHARS:
        return [text]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for sentence in SENTENCE_SPLIT_RE.split(text):
        if not sentence:
            continue
        if current and current_len + len(sentence) + 1 > MAX_SEGMENT_CHARS:
            chunks.append(" ".join(current).strip())
            current = []
            current_len = 0
        if len(sentence) > MAX_SEGMENT_CHARS:
            for index in range(0, len(sentence), MAX_SEGMENT_CHARS):
                piece = sentence[index : index + MAX_SEGMENT_CHARS].strip()
                if piece:
                    if current:
                        chunks.append(" ".join(current).strip())
                        current = []
                        current_len = 0
                    chunks.append(piece)
            continue
        current.append(sentence)
        current_len += len(sentence) + 1
    if current:
        chunks.append(" ".join(current).strip())
    return chunks


def should_fold(value: str) -> str:
    if len(value) > 80 or "\n" in value:
        return FoldedString(value.strip())
    return value.strip()


def translated_value_to_yaml(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: translated_value_to_yaml(nested) for key, nested in value.items()}
    if isinstance(value, list):
        return [translated_value_to_yaml(item) for item in value]
    if isinstance(value, str):
        return should_fold(value)
    return value


def iter_batches(items: list[tuple[int, str]], max_chars: int) -> list[list[tuple[int, str]]]:
    batches: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    current_len = 0
    for item in items:
        _, text = item
        extra = len(text) + (12 if current else 0)
        if current and current_len + extra > max_chars:
            batches.append(current)
            current = []
            current_len = 0
        current.append(item)
        current_len += extra
    if current:
        batches.append(current)
    return batches


def translate_strings(client: GoogleTranslateClient, strings: list[str]) -> list[str]:
    segment_records: list[dict[str, Any]] = []
    for string_index, text in enumerate(strings):
        for piece in split_text(text):
            protected, replacements = protect_identifiers(piece)
            segment_records.append(
                {
                    "string_index": string_index,
                    "text": protected,
                    "replacements": replacements,
                }
            )

    translated_segments: list[str] = [""] * len(segment_records)
    indexed_segments = [(index, record["text"]) for index, record in enumerate(segment_records)]
    for batch in iter_batches(indexed_segments, MAX_BATCH_CHARS):
        translations = client.translate_batch([text for _, text in batch])
        for (segment_index, _), translated in zip(batch, translations):
            replacements = segment_records[segment_index]["replacements"]
            translated_segments[segment_index] = sanitize_translation_text(
                restore_identifiers(translated, replacements)
            )

    by_string: list[list[str]] = [[] for _ in strings]
    for segment_index, translated in enumerate(translated_segments):
        string_index = int(segment_records[segment_index]["string_index"])
        by_string[string_index].append(translated)
    return ["".join(parts).strip() for parts in by_string]


def collect_translatable_strings(value: Any, field_key: str | None, strings: list[str], setters: list[Any]) -> Any:
    if isinstance(value, dict):
        return {
            key: collect_translatable_strings(nested, str(key), strings, setters)
            for key, nested in value.items()
        }
    if isinstance(value, list):
        if field_key in NON_TRANSLATED_RITUAL_FIELDS:
            return deepcopy(value)
        result: list[Any] = []
        for index, item in enumerate(value):
            result.append(collect_translatable_strings(item, field_key, strings, setters))
        return result
    if isinstance(value, str):
        if field_key in NON_TRANSLATED_RITUAL_FIELDS:
            return value
        placeholder = {"value": None}
        strings.append(value)
        setters.append(placeholder)
        return placeholder
    return deepcopy(value)


def fill_placeholders(value: Any) -> Any:
    if isinstance(value, dict):
        if set(value.keys()) == {"value"}:
            return translated_value_to_yaml(value["value"])
        return {key: fill_placeholders(nested) for key, nested in value.items()}
    if isinstance(value, list):
        return [fill_placeholders(item) for item in value]
    return translated_value_to_yaml(value)


def translate_ritual_design(client: GoogleTranslateClient, ritual_design: dict[str, Any]) -> dict[str, Any]:
    strings: list[str] = []
    placeholders: list[dict[str, Any]] = []
    shell = collect_translatable_strings(ritual_design, None, strings, placeholders)
    translations = translate_strings(client, strings)
    for placeholder, translation in zip(placeholders, translations):
        placeholder["value"] = translation
    return fill_placeholders(shell)


def build_existing_index(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for entry in data.get("unique_wonders", []):
        if not isinstance(entry, dict):
            continue
        key = str(entry.get("key", "")).strip()
        if key:
            index[key] = entry
    return index


def output_entry(source_entry: dict[str, Any], ritual_design_zh: dict[str, Any]) -> dict[str, Any]:
    entry: dict[str, Any] = {}
    for key in ("id", "key", "base_key", "location", "source_ritual_key", "status"):
        if key in source_entry:
            entry[key] = deepcopy(source_entry[key])
    entry["ritual_design_zh"] = ritual_design_zh
    return entry


def build_output_metadata(proxy: str) -> dict[str, Any]:
    return {
        "purpose": "Simplified Chinese translations for unique wonder ritual design prose.",
        "source_data": "data/unique_wonder_ritual_designs.yaml",
        "generated_game_code": False,
        "translation_provider": "Google Translate",
        "proxy": proxy,
        "generated_by": "scripts_engineering_department/translate_unique_wonder_ritual_designs_google.py",
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "translation_scope": "ritual_design -> ritual_design_zh",
        "preservation": (
            "The English ritual_design source remains in data/unique_wonder_ritual_designs.yaml. "
            "This sidecar can be regenerated or manually reviewed without changing the source design file."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proxy", default="http://127.0.0.1:7897")
    parser.add_argument("--source", type=Path, default=SOURCE_FILE)
    parser.add_argument("--output", type=Path, default=OUTPUT_FILE)
    parser.add_argument("--force", action="store_true", help="Retranslate entries already present in the output file")
    args = parser.parse_args()

    source = load_yaml(args.source)
    existing = load_yaml(args.output)
    existing_index = build_existing_index(existing)
    client = GoogleTranslateClient(args.proxy)
    output_entries: list[dict[str, Any]] = []

    source_entries = [entry for entry in source.get("unique_wonders", []) if isinstance(entry, dict)]
    total = len(source_entries)
    for index, source_entry in enumerate(source_entries, start=1):
        key = str(source_entry.get("key", "")).strip()
        existing_entry = existing_index.get(key)
        if (
            not args.force
            and existing_entry
            and isinstance(existing_entry.get("ritual_design_zh"), dict)
        ):
            output_entries.append(deepcopy(existing_entry))
            print(f"[{index:03d}/{total:03d}] reuse {key}")
            continue

        ritual_design = source_entry.get("ritual_design", {})
        if not isinstance(ritual_design, dict):
            raise TypeError(f"{key}.ritual_design must be a mapping")
        print(f"[{index:03d}/{total:03d}] translate {key}")
        ritual_design_zh = translate_ritual_design(client, ritual_design)
        output_entries.append(output_entry(source_entry, ritual_design_zh))
        partial = {
            "metadata": build_output_metadata(args.proxy),
            "unique_wonders": output_entries,
        }
        dump_yaml(args.output, partial)

    output = {
        "metadata": build_output_metadata(args.proxy),
        "unique_wonders": output_entries,
    }
    dump_yaml(args.output, output)
    print(f"[OK] Wrote {args.output.relative_to(REPO_ROOT)} ({len(output_entries)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
