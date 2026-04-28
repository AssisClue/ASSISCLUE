from __future__ import annotations

from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup
from playwright.sync_api import Page

from app.web_tools.runtime.web_runtime_paths import ensure_web_runtime_dirs, pages_root


def _timestamp_for_filename() -> str:
    return datetime.now().strftime("%Y-%m-%d__%H-%M-%S")


def _clean_name_prefix(name_prefix: str, *, fallback: str) -> str:
    clean = str(name_prefix or "").strip().replace(" ", "_")
    return clean or fallback


def _extract_visible_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "noscript", "svg", "canvas", "meta", "link", "head"]):
        tag.decompose()

    text = soup.get_text("\n", strip=True)
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]

    return "\n".join(lines)


def get_page_title(page: Page) -> dict[str, Any]:
    return {
        "ok": True,
        "title": page.title(),
        "url": page.url,
    }


def get_page_html(page: Page) -> dict[str, Any]:
    html = page.content()
    return {
        "ok": True,
        "url": page.url,
        "title": page.title(),
        "html": html,
        "length": len(html),
    }


def get_page_text(page: Page) -> dict[str, Any]:
    html = page.content()
    text = _extract_visible_text_from_html(html)

    return {
        "ok": True,
        "url": page.url,
        "title": page.title(),
        "text": text,
        "length": len(text),
        "line_count": len(text.splitlines()) if text else 0,
    }


def save_page_html(page: Page, *, name_prefix: str = "page") -> dict[str, Any]:
    ensure_web_runtime_dirs()

    clean_prefix = _clean_name_prefix(name_prefix, fallback="page")
    filename = f"{clean_prefix}_{_timestamp_for_filename()}.html"
    path = pages_root() / filename

    html = page.content()
    path.write_text(html, encoding="utf-8")

    return {
        "ok": True,
        "kind": "html",
        "url": page.url,
        "title": page.title(),
        "path": str(path),
        "filename": filename,
        "length": len(html),
    }


def save_page_text(page: Page, *, name_prefix: str = "page") -> dict[str, Any]:
    ensure_web_runtime_dirs()

    clean_prefix = _clean_name_prefix(name_prefix, fallback="page")
    filename = f"{clean_prefix}_{_timestamp_for_filename()}.txt"
    path = pages_root() / filename

    html = page.content()
    text = _extract_visible_text_from_html(html)
    path.write_text(text, encoding="utf-8")

    return {
        "ok": True,
        "kind": "text",
        "url": page.url,
        "title": page.title(),
        "path": str(path),
        "filename": filename,
        "length": len(text),
        "line_count": len(text.splitlines()) if text else 0,
    }