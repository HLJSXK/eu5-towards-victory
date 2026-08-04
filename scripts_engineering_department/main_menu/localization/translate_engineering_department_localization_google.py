from __future__ import annotations

import argparse
import ast
import html
import json
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = (
    REPO_ROOT
    / "src_engineering_department"
    / "main_menu"
    / "localization"
    / "english"
)
OUTPUT_ROOT = (
    REPO_ROOT
    / "src_engineering_department"
    / "main_menu"
    / "localization"
)
SCRIPT_REL = (
    "scripts_engineering_department/main_menu/localization/"
    "translate_engineering_department_localization_google.py"
)

GOOGLE_URL = "https://translate.googleapis.com/translate_a/single"
GOOGLE_MOBILE_URL = "https://translate.google.com/m"
MYMEMORY_URL = "https://api.mymemory.translated.net/get"
DEFAULT_PROXY = "http://127.0.0.1:7897"
DEFAULT_CACHE = (
    Path(tempfile.gettempdir())
    / "tv_engineering_department_localization_translate_cache.json"
)

LANGUAGE_TO_GOOGLE = {
    "braz_por": "pt",
    "french": "fr",
    "german": "de",
    "japanese": "ja",
    "korean": "ko",
    "polish": "pl",
    "russian": "ru",
    "spanish": "es",
    "turkish": "tr",
}
LANGUAGE_TO_MYMEMORY = {
    "braz_por": "pt",
    "french": "fr",
    "german": "de",
    "japanese": "ja",
    "korean": "ko",
    "polish": "pl",
    "russian": "ru",
    "spanish": "es",
    "turkish": "tr",
}
DEFAULT_TARGETS = (
    "german",
    "spanish",
    "japanese",
    "korean",
    "polish",
    "braz_por",
    "russian",
    "turkish",
)

LOCALIZATION_LINE_RE = re.compile(
    r'^(?P<indent>\s*)(?P<key>[A-Za-z0-9_.-]+):(?P<version>0)?\s+'
    r'(?P<value>"(?:[^"\\]|\\.)*")\s*$'
)
LOCALIZATION_HEADER_RE = re.compile(r"^l_[A-Za-z_]+:\s*$")
MARKER_KINDS_RE = "SEP|NL|LIT|SCP|VAR|ICO|ID|TAG|END"
SEPARATOR_RE = re.compile(r"QXSEP\d{4}QX")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?;:])\s+")

LITERAL_NEWLINE_RE = re.compile(r"\\n")
BRACKET_TOKEN_RE = re.compile(r"\[[^\[\]]+\]")
DOLLAR_TOKEN_RE = re.compile(r"\$[^$\n]+\$")
ICON_TOKEN_RE = re.compile(r"@[A-Za-z0-9_]+!")
IDENTIFIER_TOKEN_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9]+(?:_[A-Za-z0-9]+)+\b")
OPEN_TAG_RE = re.compile(r"#[^#!\s]+(?:\s+)?")
CLOSE_TAG_RE = re.compile(r"#!")
PROTECTED_MARKER_RE = re.compile(rf"QX(?:{MARKER_KINDS_RE})\d{{4}}QX")
PROTECTED_MARKER_VARIANT_RE = re.compile(
    rf"Q\s*X\s*({MARKER_KINDS_RE})\s*(\d{{4}})\s*Q\s*X",
    re.IGNORECASE,
)
FORMAT_TAG_TOKEN_RE = re.compile(r"#!|#[^#!\s]+(?:\s*)")
SMART_QUOTE_RE = re.compile("[\u2018\u2019\u201c\u201d]")
BAD_TARGETED_SCANS = (
    (
        re.compile(r"#(?:Y|G|R|high|weak|F)[^\s#!]"),
        "format tag is adjacent to text",
    ),
    (
        re.compile(r"[A-Za-zÀ-ž]\["),
        "scope token is adjacent to translated text",
    ),
)


@dataclass(frozen=True)
class ProviderDefaults:
    max_single_text_chars: int
    max_batch_chars: int
    delay: float


PROVIDER_DEFAULTS = {
    "google": ProviderDefaults(
        max_single_text_chars=6000,
        max_batch_chars=12000,
        delay=0.08,
    ),
    "google_mobile": ProviderDefaults(
        max_single_text_chars=1500,
        max_batch_chars=4600,
        delay=0.25,
    ),
    # MyMemory rejects long q= payloads. Keep a little margin below the
    # documented 500-character ceiling so separator markers and URL decoding
    # quirks cannot push a request over the edge.
    "mymemory": ProviderDefaults(
        max_single_text_chars=420,
        max_batch_chars=420,
        delay=0.12,
    ),
}


def make_marker(prefix: str, index: int) -> str:
    return f"QX{prefix}{index:04d}QX"


def parse_localization_value(raw: str) -> str:
    value = ast.literal_eval(raw)
    if not isinstance(value, str):
        raise ValueError(f"Localization value is not a string literal: {raw}")
    return value


def escape_localization_value(value: str) -> str:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    return (
        normalized.replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace('"', '\\"')
    )


def load_cache(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON mapping")
    return {
        str(language): {
            str(source): str(target)
            for source, target in translations.items()
        }
        for language, translations in payload.items()
        if isinstance(translations, dict)
    }


def save_cache(path: Path, cache: dict[str, dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build_opener(proxy: str) -> urllib.request.OpenerDirector:
    proxy = proxy.strip()
    if not proxy or proxy.lower() in {"direct", "none", "off"}:
        return urllib.request.build_opener()
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy, "https": proxy})
    )


def parse_google_mobile_translation(raw_html: str) -> str:
    match = re.search(
        r'<div class="result-container">(.*?)</div>',
        raw_html,
        re.DOTALL | re.IGNORECASE,
    )
    if match is None:
        raise RuntimeError("Google mobile response did not contain result-container")
    body = re.sub(r"<br\s*/?>", "\n", match.group(1), flags=re.IGNORECASE)
    body = re.sub(r"<[^>]+>", "", body)
    return html.unescape(body).strip()


class GoogleTranslateClient:
    def __init__(
        self,
        target_language: str,
        *,
        proxy: str,
        timeout: float = 35.0,
        retries: int = 4,
        delay: float = 0.08,
    ) -> None:
        self.target_language = target_language
        self.opener = build_opener(proxy)
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
                pieces.append(f"\n{make_marker('SEP', index)}\n")
            pieces.append(text)
        try:
            translated = html.unescape(self.translate_one("".join(pieces)))
        except Exception:
            if len(texts) <= 2:
                return [self.translate_one(text) for text in texts]
            midpoint = len(texts) // 2
            return (
                self.translate_batch(texts[:midpoint])
                + self.translate_batch(texts[midpoint:])
            )
        split = SEPARATOR_RE.split(translated)
        if len(split) != len(texts):
            if len(texts) <= 2:
                return [self.translate_one(text) for text in texts]
            midpoint = len(texts) // 2
            return (
                self.translate_batch(texts[:midpoint])
                + self.translate_batch(texts[midpoint:])
            )
        return [part.strip() for part in split]

    def translate_one(self, text: str) -> str:
        source = text.strip()
        if not source:
            return ""
        data = urllib.parse.urlencode(
            {
                "client": "gtx",
                "sl": "en",
                "tl": self.target_language,
                "dt": "t",
                "q": source,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            GOOGLE_URL,
            data=data,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json,text/plain,*/*",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        for attempt in range(1, self.retries + 1):
            try:
                with self.opener.open(request, timeout=self.timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                translated = "".join(part[0] for part in payload[0] if part and part[0])
                if self.delay:
                    time.sleep(self.delay)
                return translated
            except urllib.error.HTTPError as exc:
                if exc.code == 429 and attempt < self.retries:
                    wait = min(180.0, 20.0 * attempt * attempt)
                    print(f"[WARN] Google Translate 429; sleeping {wait:.0f}s", file=sys.stderr)
                    time.sleep(wait)
                    continue
                if attempt >= self.retries:
                    raise
                time.sleep(min(8.0, 0.65 * attempt * attempt))
            except Exception:
                if attempt >= self.retries:
                    raise
                time.sleep(min(8.0, 0.65 * attempt * attempt))
        raise RuntimeError("unreachable translation retry state")


class GoogleMobileTranslateClient:
    def __init__(
        self,
        target_language: str,
        *,
        proxy: str,
        timeout: float = 35.0,
        retries: int = 4,
        delay: float = 0.25,
    ) -> None:
        self.target_language = target_language
        self.opener = build_opener(proxy)
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
                pieces.append(f"\n{make_marker('SEP', index)}\n")
            pieces.append(text)
        try:
            translated = html.unescape(self.translate_one("".join(pieces)))
        except Exception:
            if len(texts) <= 2:
                return [self.translate_one(text) for text in texts]
            midpoint = len(texts) // 2
            return (
                self.translate_batch(texts[:midpoint])
                + self.translate_batch(texts[midpoint:])
            )
        split = SEPARATOR_RE.split(translated)
        if len(split) != len(texts):
            if len(texts) <= 2:
                return [self.translate_one(text) for text in texts]
            midpoint = len(texts) // 2
            return (
                self.translate_batch(texts[:midpoint])
                + self.translate_batch(texts[midpoint:])
            )
        return [part.strip() for part in split]

    def translate_one(self, text: str) -> str:
        source = text.strip()
        if not source:
            return ""
        params = urllib.parse.urlencode(
            {
                "sl": "en",
                "tl": self.target_language,
                "hl": self.target_language,
                "ie": "UTF-8",
                "prev": "_m",
                "q": source,
            }
        )
        request = urllib.request.Request(
            f"{GOOGLE_MOBILE_URL}?{params}",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        for attempt in range(1, self.retries + 1):
            try:
                with self.opener.open(request, timeout=self.timeout) as response:
                    raw = response.read().decode("utf-8", errors="replace")
                translated = parse_google_mobile_translation(raw)
                if self.delay:
                    time.sleep(self.delay)
                return translated
            except urllib.error.HTTPError as exc:
                if exc.code == 429 and attempt < self.retries:
                    wait = min(180.0, 20.0 * attempt * attempt)
                    print(f"[WARN] Google mobile 429; sleeping {wait:.0f}s", file=sys.stderr)
                    time.sleep(wait)
                    continue
                if attempt >= self.retries:
                    raise
                time.sleep(min(8.0, 0.65 * attempt * attempt))
            except Exception:
                if attempt >= self.retries:
                    raise
                time.sleep(min(8.0, 0.65 * attempt * attempt))
        raise RuntimeError("unreachable translation retry state")


class MyMemoryTranslateClient:
    def __init__(
        self,
        target_language: str,
        *,
        proxy: str,
        timeout: float = 35.0,
        retries: int = 4,
        delay: float = 0.12,
    ) -> None:
        self.target_language = target_language
        self.opener = build_opener(proxy)
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
                pieces.append(f"\n{make_marker('SEP', index)}\n")
            pieces.append(text)
        translated = html.unescape(self.translate_one("".join(pieces)))
        split = SEPARATOR_RE.split(translated)
        if len(split) != len(texts):
            if len(texts) <= 2:
                return [self.translate_one(text) for text in texts]
            midpoint = len(texts) // 2
            return (
                self.translate_batch(texts[:midpoint])
                + self.translate_batch(texts[midpoint:])
            )
        return [part.strip() for part in split]

    def translate_one(self, text: str) -> str:
        source = text.strip()
        if not source:
            return ""
        params = urllib.parse.urlencode(
            {
                "q": source,
                "langpair": f"en|{self.target_language}",
            }
        )
        request = urllib.request.Request(
            f"{MYMEMORY_URL}?{params}",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json,text/plain,*/*",
            },
        )
        for attempt in range(1, self.retries + 1):
            try:
                with self.opener.open(request, timeout=self.timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                status = payload.get("responseStatus")
                response_data = payload.get("responseData") or {}
                translated = response_data.get("translatedText")
                if status != 200 or translated is None:
                    details = payload.get("responseDetails") or payload
                    raise RuntimeError(f"MyMemory failed ({status}): {details}")
                if self.delay:
                    time.sleep(self.delay)
                return str(translated)
            except urllib.error.HTTPError as exc:
                if exc.code == 429 and attempt < self.retries:
                    wait = min(180.0, 20.0 * attempt * attempt)
                    print(f"[WARN] MyMemory 429; sleeping {wait:.0f}s", file=sys.stderr)
                    time.sleep(wait)
                    continue
                if attempt >= self.retries:
                    raise
                time.sleep(min(8.0, 0.65 * attempt * attempt))
            except Exception:
                if attempt >= self.retries:
                    raise
                time.sleep(min(8.0, 0.65 * attempt * attempt))
        raise RuntimeError("unreachable translation retry state")


def protect_with_pattern(
    text: str,
    pattern: re.Pattern[str],
    prefix: str,
) -> tuple[str, list[tuple[str, str]]]:
    replacements: list[tuple[str, str]] = []

    def replace(match: re.Match[str]) -> str:
        marker = make_marker(prefix, len(replacements))
        replacements.append((marker, match.group(0)))
        return marker

    return pattern.sub(replace, text), replacements


def protect_newlines(text: str) -> tuple[str, list[tuple[str, str]]]:
    replacements: list[tuple[str, str]] = []

    def replace(match: re.Match[str]) -> str:
        marker = make_marker("NL", len(replacements))
        replacements.append((marker, match.group(0)))
        return marker

    return re.sub(r"\n", replace, text), replacements


def protect_text(text: str) -> tuple[str, list[list[tuple[str, str]]]]:
    current = text
    stages: list[list[tuple[str, str]]] = []

    current, replacements = protect_newlines(current)
    stages.append(replacements)

    for prefix, pattern in (
        ("LIT", LITERAL_NEWLINE_RE),
        ("SCP", BRACKET_TOKEN_RE),
        ("VAR", DOLLAR_TOKEN_RE),
        ("ICO", ICON_TOKEN_RE),
        ("ID", IDENTIFIER_TOKEN_RE),
        ("TAG", OPEN_TAG_RE),
        ("END", CLOSE_TAG_RE),
    ):
        current, replacements = protect_with_pattern(current, pattern, prefix)
        stages.append(replacements)

    return current, stages


def restore_text(text: str, stages: list[list[tuple[str, str]]]) -> str:
    restored = text
    for replacements in reversed(stages):
        for marker, original in replacements:
            restored = restored.replace(marker, original)
    return restored


def sanitize_translation_text(text: str) -> str:
    sanitized = html.unescape(text)
    sanitized = (
        sanitized.replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u201e", '"')
        .replace("\u00ab", '"')
        .replace("\u00bb", '"')
        .replace("\u200b", "")
        .replace("\ufeff", "")
    )
    sanitized = sanitized.replace("\r\n", "\n").replace("\r", "\n")
    sanitized = re.sub(r"[ \t]{2,}", " ", sanitized)
    return sanitized.strip()


def normalize_protected_markers(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        return make_marker(match.group(1).upper(), int(match.group(2)))

    return PROTECTED_MARKER_VARIANT_RE.sub(replace, text)


def split_long_text(text: str, max_chars: int) -> list[str]:
    stripped = text.strip()
    if len(stripped) <= max_chars:
        return [stripped]

    chunks: list[str] = []
    remaining = stripped
    while remaining:
        if len(remaining) <= max_chars:
            chunks.append(remaining.strip())
            break

        split_at = 0
        sentence_matches = list(SENTENCE_SPLIT_RE.finditer(remaining[: max_chars + 1]))
        for match in reversed(sentence_matches):
            if match.end() <= max_chars and match.end() >= max(80, int(max_chars * 0.35)):
                split_at = match.end()
                break

        if split_at == 0:
            whitespace_matches = [
                match.end()
                for match in re.finditer(r"\s+", remaining[: max_chars + 1])
                if match.end() <= max_chars
            ]
            if whitespace_matches and whitespace_matches[-1] >= max(80, int(max_chars * 0.35)):
                split_at = whitespace_matches[-1]

        if split_at == 0:
            split_at = max_chars

        split_at = min(split_at, len(remaining))
        marker_overlap = next(
            (
                match
                for match in PROTECTED_MARKER_RE.finditer(remaining)
                if match.start() < split_at < match.end()
            ),
            None,
        )
        if marker_overlap is not None:
            split_at = marker_overlap.start() or marker_overlap.end()
            if split_at <= 0:
                split_at = min(marker_overlap.end(), len(remaining))

        piece = remaining[:split_at].strip()
        if piece:
            chunks.append(piece)
        remaining = remaining[split_at:].strip()

    return chunks


def iter_batches(items: list[tuple[int, str]], max_batch_chars: int) -> list[list[tuple[int, str]]]:
    batches: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    current_len = 0
    for item in items:
        _, text = item
        extra = len(text) + (12 if current else 0)
        if current and current_len + extra > max_batch_chars:
            batches.append(current)
            current = []
            current_len = 0
        current.append(item)
        current_len += extra
    if current:
        batches.append(current)
    return batches


def translate_values(
    client: GoogleTranslateClient | GoogleMobileTranslateClient | MyMemoryTranslateClient,
    language: str,
    values: list[str],
    cache: dict[str, dict[str, str]],
    *,
    cache_path: Path,
    force: bool,
    max_single_text_chars: int,
    max_batch_chars: int,
    cache_key: str,
) -> dict[str, str]:
    language_cache = cache.setdefault(cache_key, {})
    unique_values = list(dict.fromkeys(value for value in values if value.strip()))
    missing = [
        value
        for value in unique_values
        if force or value not in language_cache
    ]
    if not missing:
        print(f"[{language}] reuse {len(unique_values)} cached translations")
        return {value: language_cache.get(value, value) for value in unique_values}

    records: list[dict[str, object]] = []
    part_counts_by_value: list[int] = [0] * len(missing)
    for value_index, value in enumerate(missing):
        protected, stages = protect_text(value)
        parts = split_long_text(protected, max_single_text_chars)
        part_counts_by_value[value_index] = len(parts)
        for part_index, part in enumerate(parts):
            records.append(
                {
                    "value_index": value_index,
                    "part_index": part_index,
                    "text": part,
                    "stages": stages,
                }
            )

    print(
        f"[{language}] translate {len(missing)} values "
        f"({len(records)} request segment(s))"
    )

    translated_parts_by_value: list[list[str | None]] = [
        [None] * count for count in part_counts_by_value
    ]
    completed_values: set[int] = set()
    indexed = [(index, str(record["text"])) for index, record in enumerate(records)]
    batches = iter_batches(indexed, max_batch_chars)
    for batch_index, batch in enumerate(batches, start=1):
        translated_batch = client.translate_batch([text for _, text in batch])
        for (record_index, _), translated in zip(batch, translated_batch):
            record = records[record_index]
            normalized = normalize_protected_markers(html.unescape(str(translated)))
            restored = restore_text(normalized, record["stages"])  # type: ignore[arg-type]
            value_index = int(record["value_index"])
            part_index = int(record["part_index"])
            translated_parts_by_value[value_index][part_index] = sanitize_translation_text(restored)

            if value_index in completed_values:
                continue
            value_parts = translated_parts_by_value[value_index]
            if all(part is not None for part in value_parts):
                joiner = " " if len(value_parts) > 1 else ""
                source_value = missing[value_index]
                translated_value = joiner.join(part or "" for part in value_parts).strip()
                language_cache[source_value] = coerce_safe_translation(
                    source_value,
                    translated_value,
                )
                completed_values.add(value_index)

        if batch_index % 10 == 0:
            save_cache(cache_path, cache)
        if batch_index % 25 == 0 or batch_index == len(batches):
            print(f"[{language}] batch {batch_index}/{len(batches)}")

    incomplete = [
        missing[index]
        for index, value_parts in enumerate(translated_parts_by_value)
        if any(part is None for part in value_parts)
    ]
    if incomplete:
        raise RuntimeError(f"Missing translated parts for {len(incomplete)} value(s)")
    save_cache(cache_path, cache)

    return {value: language_cache.get(value, value) for value in unique_values}


def verify_translation_value(
    source_file: Path,
    line_number: int,
    key: str,
    source: str,
    translated: str,
) -> None:
    checks = (
        ("bracket token", BRACKET_TOKEN_RE),
        ("dollar token", DOLLAR_TOKEN_RE),
        ("icon token", ICON_TOKEN_RE),
        ("identifier token", IDENTIFIER_TOKEN_RE),
        ("format tag", FORMAT_TAG_TOKEN_RE),
    )
    for label, pattern in checks:
        source_tokens = pattern.findall(source)
        translated_tokens = pattern.findall(translated)
        if source_tokens != translated_tokens:
            raise ValueError(
                f"{source_file}:{line_number} {key}: {label} mismatch; "
                f"source={source_tokens!r} translated={translated_tokens!r}"
            )

    if PROTECTED_MARKER_RE.search(translated) or PROTECTED_MARKER_VARIANT_RE.search(translated):
        raise ValueError(f"{source_file}:{line_number} {key}: protected marker residue detected")
    if SMART_QUOTE_RE.search(translated):
        raise ValueError(f"{source_file}:{line_number} {key}: smart quote residue detected")
    for pattern, message in BAD_TARGETED_SCANS:
        if pattern.search(translated):
            raise ValueError(f"{source_file}:{line_number} {key}: {message}")


def is_translation_structure_safe(source: str, translated: str) -> bool:
    candidate = resync_tokens_to_source_order(source, translated)
    checks = (
        BRACKET_TOKEN_RE,
        DOLLAR_TOKEN_RE,
        ICON_TOKEN_RE,
        IDENTIFIER_TOKEN_RE,
        FORMAT_TAG_TOKEN_RE,
    )
    for pattern in checks:
        if pattern.findall(source) != pattern.findall(candidate):
            return False
    if PROTECTED_MARKER_RE.search(candidate) or PROTECTED_MARKER_VARIANT_RE.search(candidate):
        return False
    if SMART_QUOTE_RE.search(candidate):
        return False
    for pattern, _ in BAD_TARGETED_SCANS:
        if pattern.search(candidate):
            return False
    return True


def coerce_safe_translation(source: str, translated: str) -> str:
    candidate = resync_tokens_to_source_order(source, translated)
    if not is_translation_structure_safe(source, candidate):
        return source
    return candidate


def resync_tokens_to_source_order(source: str, translated: str) -> str:
    current = translated
    for pattern in (BRACKET_TOKEN_RE, DOLLAR_TOKEN_RE, ICON_TOKEN_RE):
        source_tokens = pattern.findall(source)
        translated_tokens = pattern.findall(current)
        if not source_tokens or len(source_tokens) != len(translated_tokens):
            continue
        token_iter = iter(source_tokens)
        current = pattern.sub(lambda _match: next(token_iter), current)
    return current


def parse_source_file_filters(raw_filters: list[str]) -> list[str]:
    filters: list[str] = []
    for raw in raw_filters:
        filters.extend(part.strip() for part in raw.split(",") if part.strip())
    return list(dict.fromkeys(filters))


def collect_source_files(source_file_filters: list[str]) -> list[Path]:
    files = sorted(SOURCE_DIR.glob("*_l_english.yml"))
    if not files:
        raise FileNotFoundError(f"No English localization files under {SOURCE_DIR}")
    if not source_file_filters:
        return files

    selected: list[Path] = []
    missing = set(source_file_filters)
    matched_filters: set[str] = set()
    for source_file in files:
        candidates = (
            source_file.name,
            source_file.stem,
            source_file.stem.removesuffix("_l_english"),
        )
        matched = {
            raw
            for raw in missing
            if any(candidate == raw or candidate.startswith(raw) for candidate in candidates)
        }
        if matched:
            selected.append(source_file)
            matched_filters |= matched
    missing -= matched_filters
    if missing:
        known = ", ".join(file.name for file in files)
        raise ValueError(
            "Unknown source file filter(s): "
            + ", ".join(sorted(missing))
            + ". Known: "
            + known
        )
    return selected


def collect_values(source_files: list[Path]) -> list[str]:
    values: list[str] = []
    for path in source_files:
        for line_number, raw_line in enumerate(
            path.read_text(encoding="utf-8-sig").splitlines(),
            start=1,
        ):
            match = LOCALIZATION_LINE_RE.match(raw_line)
            if match is None:
                continue
            try:
                values.append(parse_localization_value(match.group("value")))
            except ValueError as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
    return values


def translated_file_name(source_file: Path, language: str) -> str:
    stem = source_file.stem
    if not stem.endswith("_l_english"):
        raise ValueError(f"Unexpected English localization filename: {source_file}")
    return f"{stem[:-len('_l_english')]}_l_{language}.yml"


def generated_header(language: str, source_file: Path, provider: str) -> list[str]:
    source_rel = source_file.relative_to(REPO_ROOT).as_posix()
    return [
        f"l_{language}:",
        f" # @Generated by {SCRIPT_REL}",
        f" #   Source:  {source_rel}",
        (
            " #   Regen:   "
            f"C:\\Users\\Hades\\anaconda3\\envs\\eu5\\python.exe {SCRIPT_REL} "
            f"--language {language} --provider {provider}"
        ),
        " # Do not edit directly - re-run the translation script from the English source.",
        " ",
    ]


def render_file(
    source_file: Path,
    language: str,
    translations: dict[str, str],
    *,
    provider: str,
) -> str:
    output_lines: list[str] = []
    header_written = False
    skip_old_generated_header = False

    for line_number, raw_line in enumerate(
        source_file.read_text(encoding="utf-8-sig").splitlines(),
        start=1,
    ):
        if not header_written:
            if not LOCALIZATION_HEADER_RE.match(raw_line):
                raise ValueError(f"{source_file}:{line_number}: missing localization header")
            output_lines.extend(generated_header(language, source_file, provider))
            header_written = True
            skip_old_generated_header = True
            continue

        if skip_old_generated_header:
            stripped = raw_line.strip()
            if not stripped:
                skip_old_generated_header = False
                continue
            if stripped.startswith("#"):
                continue
            skip_old_generated_header = False

        match = LOCALIZATION_LINE_RE.match(raw_line)
        if match is None:
            output_lines.append(raw_line.rstrip("\r"))
            continue

        value = parse_localization_value(match.group("value"))
        translated = translations.get(value, value)
        translated = coerce_safe_translation(value, translated)
        try:
            verify_translation_value(
                source_file,
                line_number,
                match.group("key"),
                value,
                translated,
            )
        except ValueError as exc:
            print(f"[WARN] {exc}; falling back to English", file=sys.stderr)
            translated = value
            verify_translation_value(
                source_file,
                line_number,
                match.group("key"),
                value,
                translated,
            )
        output_lines.append(
            f"{match.group('indent')}{match.group('key')}:"
            f"{match.group('version') or ''} "
            f"\"{escape_localization_value(translated)}\""
        )

    return "\n".join(output_lines).rstrip() + "\n"


def write_language_files(
    language: str,
    source_files: list[Path],
    translations: dict[str, str],
    *,
    provider: str,
) -> None:
    output_dir = OUTPUT_ROOT / language
    output_dir.mkdir(parents=True, exist_ok=True)
    for source_file in source_files:
        output_file = output_dir / translated_file_name(source_file, language)
        output_file.write_text(
            render_file(source_file, language, translations, provider=provider),
            encoding="utf-8-sig",
        )
        print(f"[{language}] wrote {output_file.relative_to(REPO_ROOT)}")


def parse_languages(raw_languages: list[str]) -> list[str]:
    if not raw_languages:
        return list(DEFAULT_TARGETS)
    languages: list[str] = []
    for raw in raw_languages:
        parts = [part.strip() for part in raw.split(",") if part.strip()]
        languages.extend(parts)
    unknown = sorted(set(languages) - set(LANGUAGE_TO_GOOGLE))
    if unknown:
        raise ValueError(
            "Unsupported language(s): "
            + ", ".join(unknown)
            + ". Known: "
            + ", ".join(sorted(LANGUAGE_TO_GOOGLE))
        )
    return list(dict.fromkeys(languages))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Translate Engineering Department English localization files into "
            "EU5 locale directories with token-safe Google Translate output."
        )
    )
    parser.add_argument(
        "--language",
        "--languages",
        action="append",
        default=[],
        help=(
            "Target language id(s), comma-separated or repeated. Defaults to the "
            "remaining EU5 languages not already present as English/French/Chinese."
        ),
    )
    parser.add_argument(
        "--source-file",
        action="append",
        default=[],
        help=(
            "Restrict generation to one or more English source files. "
            "Accepts file names or stems, and can be repeated or comma-separated."
        ),
    )
    parser.add_argument("--proxy", default=DEFAULT_PROXY)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument(
        "--provider",
        choices=("google", "google_mobile", "mymemory"),
        default="mymemory",
        help=(
            "Translation backend. MyMemory remains the conservative default; "
            "google_mobile uses the Google Translate mobile page when the JSON API throttles."
        ),
    )
    parser.add_argument("--force", action="store_true", help="Retranslate cached values")
    parser.add_argument("--timeout", type=float, default=None)
    parser.add_argument("--retries", type=int, default=None)
    parser.add_argument("--delay", type=float, default=None)
    parser.add_argument("--max-single-text-chars", type=int, default=None)
    parser.add_argument("--max-batch-chars", type=int, default=None)
    args = parser.parse_args()

    languages = parse_languages(args.language)
    source_files = collect_source_files(parse_source_file_filters(args.source_file))
    values = collect_values(source_files)
    cache = load_cache(args.cache)
    provider_defaults = PROVIDER_DEFAULTS[args.provider]
    max_single_text_chars = args.max_single_text_chars or provider_defaults.max_single_text_chars
    max_batch_chars = args.max_batch_chars or provider_defaults.max_batch_chars
    timeout = args.timeout or 35.0
    retries = args.retries or 4
    delay = provider_defaults.delay if args.delay is None else args.delay

    print(
        f"source files: {len(source_files)}; values: {len(values)}; "
        f"unique: {len(set(values))}"
    )
    for language in languages:
        if args.provider == "google":
            provider_language = LANGUAGE_TO_GOOGLE[language]
            client = GoogleTranslateClient(
                provider_language,
                proxy=args.proxy,
                timeout=timeout,
                retries=retries,
                delay=delay,
            )
        elif args.provider == "google_mobile":
            provider_language = LANGUAGE_TO_GOOGLE[language]
            client = GoogleMobileTranslateClient(
                provider_language,
                proxy=args.proxy,
                timeout=timeout,
                retries=retries,
                delay=delay,
            )
        else:
            provider_language = LANGUAGE_TO_MYMEMORY[language]
            client = MyMemoryTranslateClient(
                provider_language,
                proxy=args.proxy,
                timeout=timeout,
                retries=retries,
                delay=delay,
            )
        print(f"[{language}] provider: {args.provider}; target language: {provider_language}")
        translations = translate_values(
            client,
            language,
            values,
            cache,
            cache_path=args.cache,
            force=args.force,
            max_single_text_chars=max_single_text_chars,
            max_batch_chars=max_batch_chars,
            cache_key=f"{args.provider}:{language}",
        )
        write_language_files(language, source_files, translations, provider=args.provider)
        save_cache(args.cache, cache)

    print("[OK] Translation generation complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
