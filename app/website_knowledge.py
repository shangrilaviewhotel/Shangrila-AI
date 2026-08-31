"""Live knowledge bridge for the public Shangri-La View Hotel website.

The AI reads the current public website repository directly from GitHub instead of
requiring the hotel information to be copied into prompts manually. A short cache is
used to avoid downloading the site on every request, and the repository tree SHA is
checked so committed website changes are picked up automatically.
"""

from __future__ import annotations

import html
import json
import re
import threading
import time
from html.parser import HTMLParser
from typing import Any
from urllib.request import Request, urlopen


GITHUB_API = "https://api.github.com/repos/shangrilaviewhotel/shangrilaviewhotel.github.io"
CACHE_SECONDS = 300
MAX_FILES = 80
MAX_CHARS_PER_PAGE = 12000
MAX_TOTAL_CHARS = 90000

# Public-facing content only. Administrative pages/configuration are deliberately
# excluded so the AI does not ingest internal controls or secrets.
EXCLUDED_NAMES = {
    "admin.html",
    "admin-login.html",
    "login.html",
}
EXCLUDED_PREFIXES = ("admin-", "firebase", "service-account", ".github/")
INCLUDED_EXTENSIONS = {".html", ".md", ".json"}

_cache: dict[str, Any] = {"at": 0.0, "tree_sha": None, "knowledge": ""}
_lock = threading.Lock()


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            text = html.unescape(data)
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                self.parts.append(text)


def _get_json(url: str) -> Any:
    req = Request(url, headers={"User-Agent": "Shangrila-AI/1.0"})
    with urlopen(req, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": "Shangrila-AI/1.0"})
    with urlopen(req, timeout=12) as response:
        return response.read().decode("utf-8", errors="replace")


def _visible_text(path: str, raw: str) -> str:
    if path.lower().endswith(".html"):
        parser = _VisibleTextParser()
        parser.feed(raw)
        text = " | ".join(parser.parts)
        title = re.search(r"<title[^>]*>(.*?)</title>", raw, re.I | re.S)
        if title:
            title_text = re.sub(r"\s+", " ", html.unescape(title.group(1))).strip()
            text = f"TITLE: {title_text} | {text}"
        return text

    if path.lower().endswith(".json"):
        try:
            return json.dumps(json.loads(raw), ensure_ascii=False, indent=2)
        except Exception:
            return raw

    return raw


def _select_files(tree: list[dict[str, Any]]) -> list[str]:
    paths: list[str] = []
    for item in tree:
        if item.get("type") != "blob":
            continue
        path = str(item.get("path", ""))
        name = path.rsplit("/", 1)[-1].lower()
        lower = path.lower()
        if name in {n.lower() for n in EXCLUDED_NAMES}:
            continue
        if any(lower.startswith(prefix) or f"/{prefix}" in lower for prefix in EXCLUDED_PREFIXES):
            continue
        if any(lower.endswith(ext) for ext in INCLUDED_EXTENSIONS):
            paths.append(path)

    # Put the main customer-facing pages first, then the rest alphabetically.
    priority = {"index.html": 0, "booking.html": 1, "about.html": 2, "contact.html": 3}
    paths.sort(key=lambda p: (priority.get(p.lower(), 50), p.lower()))
    return paths[:MAX_FILES]


def _build_knowledge() -> tuple[str, str]:
    tree_data = _get_json(f"{GITHUB_API}/git/trees/main?recursive=1")
    tree_sha = str(tree_data.get("sha", ""))
    paths = _select_files(tree_data.get("tree", []))

    sections: list[str] = [
        "SOURCE: Public Shangri-La View Hotel website repository",
        "REPOSITORY: shangrilaviewhotel/shangrilaviewhotel.github.io",
        f"COMMIT TREE: {tree_sha}",
        "RULE: Treat this as the current public website content. Do not invent details that are not present here or in live hotel data.",
    ]
    total = sum(len(s) for s in sections)

    for path in paths:
        if total >= MAX_TOTAL_CHARS:
            break
        try:
            raw = _get_text(f"https://raw.githubusercontent.com/shangrilaviewhotel/shangrilaviewhotel.github.io/main/{path}")
            text = _visible_text(path, raw)
            text = re.sub(r"\s+", " ", text).strip()
            if not text:
                continue
            text = text[:MAX_CHARS_PER_PAGE]
            section = f"\n\n=== {path} ===\n{text}"
            if total + len(section) > MAX_TOTAL_CHARS:
                section = section[: max(0, MAX_TOTAL_CHARS - total)]
            sections.append(section)
            total += len(section)
        except Exception:
            # One broken/large public file should never stop the AI from answering.
            continue

    return tree_sha, "".join(sections)


def get_website_knowledge(force: bool = False) -> str:
    """Return current public website knowledge, refreshed automatically."""
    now = time.time()
    if not force and _cache["knowledge"] and now - float(_cache["at"]) < CACHE_SECONDS:
        return str(_cache["knowledge"])

    with _lock:
        now = time.time()
        if not force and _cache["knowledge"] and now - float(_cache["at"]) < CACHE_SECONDS:
            return str(_cache["knowledge"])
        try:
            tree_sha, knowledge = _build_knowledge()
            _cache.update({"at": now, "tree_sha": tree_sha, "knowledge": knowledge})
            return knowledge
        except Exception as exc:
            # Keep the last good snapshot if GitHub is temporarily unavailable.
            if _cache["knowledge"]:
                return str(_cache["knowledge"])
            return f"Website knowledge is temporarily unavailable: {exc}"
