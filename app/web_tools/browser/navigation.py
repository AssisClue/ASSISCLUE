from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus, urlparse

from playwright.sync_api import Page


_DEFAULT_SEARCH_PREFIX = "https://duckduckgo.com/?q="


def _as_search_url(query: str) -> str:
    return f"{_DEFAULT_SEARCH_PREFIX}{quote_plus(str(query or '').strip())}"


def _looks_like_host(text: str) -> bool:
    clean = str(text or "").strip().lower()
    if not clean:
        return False
    if clean == "localhost" or clean.startswith("localhost:"):
        return True
    if clean.startswith("[") and "]" in clean:
        return True  # ipv6-ish
    if "." in clean:
        return True
    return False


def coerce_to_navigable_url(text: str) -> dict[str, Any]:
    raw = str(text or "").strip()
    if not raw:
        return {"ok": False, "error": "empty_input", "input": raw}

    lower = raw.lower()
    for prefix in ("search ", "search for ", "search web for ", "find ", "find on web "):
        if lower.startswith(prefix) and raw[len(prefix):].strip():
            query = raw[len(prefix):].strip()
            return {"ok": True, "input": raw, "url": _as_search_url(query), "coerced_to": "search", "query": query}

    if any(ch.isspace() for ch in raw):
        return {"ok": True, "input": raw, "url": _as_search_url(raw), "coerced_to": "search", "query": raw}

    parsed = urlparse(raw)
    if lower.startswith(("about:", "file:", "data:")):
        return {"ok": True, "input": raw, "url": raw, "coerced_to": "url"}

    if parsed.scheme and lower.startswith(f"{parsed.scheme.lower()}://"):
        return {"ok": True, "input": raw, "url": raw, "coerced_to": "url"}

    if _looks_like_host(raw):
        return {"ok": True, "input": raw, "url": f"https://{raw}", "coerced_to": "https"}

    return {"ok": True, "input": raw, "url": _as_search_url(raw), "coerced_to": "search", "query": raw}


def open_url(page: Page, *, url: str) -> dict[str, Any]:
    coerced = coerce_to_navigable_url(url)
    if not coerced.get("ok", False):
        return {"ok": False, "error": str(coerced.get("error") or "invalid_url"), "input": coerced.get("input")}

    requested_url = str(coerced.get("url") or "").strip()
    if not requested_url:
        return {"ok": False, "error": "empty_url", "input": str(url or "").strip()}

    try:
        response = page.goto(requested_url, wait_until="domcontentloaded")
        return {
            "ok": True,
            "url": page.url,
            "requested_url": requested_url,
            "title": page.title(),
            "status": response.status if response is not None else None,
            "coerced_to": coerced.get("coerced_to"),
            "query": coerced.get("query"),
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": "goto_failed",
            "requested_url": requested_url,
            "input": str(url or "").strip(),
            "exception_type": type(exc).__name__,
            "exception": str(exc),
            "coerced_to": coerced.get("coerced_to"),
            "query": coerced.get("query"),
        }


def reload_page(page: Page) -> dict[str, Any]:
    response = page.reload(wait_until="domcontentloaded")
    return {
        "ok": True,
        "url": page.url,
        "title": page.title(),
        "status": response.status if response is not None else None,
    }


def go_back(page: Page) -> dict[str, Any]:
    response = page.go_back(wait_until="domcontentloaded")
    return {
        "ok": True,
        "url": page.url,
        "title": page.title(),
        "status": response.status if response is not None else None,
        "had_history": response is not None,
    }


def wait_ms(page: Page, *, timeout_ms: int) -> dict[str, Any]:
    clean_timeout_ms = max(0, int(timeout_ms or 0))
    page.wait_for_timeout(clean_timeout_ms)
    return {
        "ok": True,
        "waited_ms": clean_timeout_ms,
        "url": page.url,
        "title": page.title(),
    }


def click_locator(page: Page, *, selector: str) -> dict[str, Any]:
    clean_selector = str(selector or "").strip()
    if not clean_selector:
        return {
            "ok": False,
            "error": "empty_selector",
            "selector": clean_selector,
        }

    locator = page.locator(clean_selector).first
    locator.click()

    return {
        "ok": True,
        "selector": clean_selector,
        "url": page.url,
        "title": page.title(),
    }


def type_into_locator(
    page: Page,
    *,
    selector: str,
    text: str,
    clear_first: bool = True,
) -> dict[str, Any]:
    clean_selector = str(selector or "").strip()
    if not clean_selector:
        return {
            "ok": False,
            "error": "empty_selector",
            "selector": clean_selector,
        }

    clean_text = str(text or "")

    locator = page.locator(clean_selector).first
    if clear_first:
        locator.fill(clean_text)
    else:
        locator.type(clean_text)

    return {
        "ok": True,
        "selector": clean_selector,
        "typed_text": clean_text,
        "clear_first": bool(clear_first),
        "url": page.url,
        "title": page.title(),
    }


def press_key(page: Page, *, key: str) -> dict[str, Any]:
    clean_key = str(key or "").strip()
    if not clean_key:
        return {
            "ok": False,
            "error": "empty_key",
            "key": clean_key,
        }

    page.keyboard.press(clean_key)

    return {
        "ok": True,
        "key": clean_key,
        "url": page.url,
        "title": page.title(),
    }
