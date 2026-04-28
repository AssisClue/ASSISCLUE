from __future__ import annotations

import re
from typing import Any

from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError


_FIRST_RESULT_ALIASES = {
    "first result",
    "first link",
    "first website",
    "first page",
}


def _normalize_text(text: str) -> str:
    return " ".join(str(text or "").strip().lower().split())


def _regex_from_text(text: str) -> re.Pattern[str]:
    return re.compile(re.escape(str(text or "").strip()), re.IGNORECASE)


def _exact_regex_from_text(text: str) -> re.Pattern[str]:
    clean = str(text or "").strip()
    return re.compile(rf"^{re.escape(clean)}$", re.IGNORECASE)


def _first_clickable(locator: Locator, *, timeout_ms: int) -> bool:
    try:
        count = locator.count()
    except Exception:
        return False

    if count < 1:
        return False

    max_checks = min(count, 25)
    for idx in range(max_checks):
        item = locator.nth(idx)
        try:
            if not item.is_visible():
                continue
        except Exception:
            continue

        try:
            try:
                item.scroll_into_view_if_needed(timeout=timeout_ms)
            except Exception:
                pass
            item.click(timeout=timeout_ms)
            return True
        except Exception:
            try:
                item.click(timeout=timeout_ms, force=True)
                return True
            except Exception:
                continue

    return False


def _first_fill(locator: Locator, value: str, *, timeout_ms: int) -> bool:
    try:
        count = locator.count()
    except Exception:
        return False

    if count < 1:
        return False

    try:
        locator.first.click(timeout=timeout_ms)
    except Exception:
        pass

    try:
        locator.first.fill(value, timeout=timeout_ms)
        return True
    except Exception:
        return False


def click_by_semantics(page: Page, target_text: str, *, timeout_ms: int = 2500) -> dict[str, Any]:
    clean_target = str(target_text or "").strip()
    if not clean_target:
        return {"ok": False, "error": "empty_target"}

    normalized_target = _normalize_text(clean_target)

    if normalized_target in _FIRST_RESULT_ALIASES:
        first_result_attempts: list[tuple[str, Locator]] = [
            ("duckduckgo_result_title", page.locator('a[data-testid="result-title-a"]')),
            ("main_links", page.locator("main a[href]")),
            ("generic_links", page.locator("a[href]")),
        ]
        for strategy, locator in first_result_attempts:
            if _first_clickable(locator, timeout_ms=timeout_ms):
                return {
                    "ok": True,
                    "strategy": strategy,
                    "target_text": clean_target,
                    "url": page.url,
                    "title": page.title(),
            }

    exact_rx = _exact_regex_from_text(clean_target)
    rx = _regex_from_text(clean_target)

    attempts: list[tuple[str, Locator]] = [
        ("role_link_exact", page.get_by_role("link", name=clean_target, exact=True)),
        ("role_button_exact", page.get_by_role("button", name=clean_target, exact=True)),
        ("role_tab_exact", page.get_by_role("tab", name=clean_target, exact=True)),
        ("css_link_exact_text", page.locator("a").filter(has_text=exact_rx)),
        ("css_button_exact_text", page.locator("button").filter(has_text=exact_rx)),
        ("role_button", page.get_by_role("button", name=rx)),
        ("role_link", page.get_by_role("link", name=rx)),
        ("role_tab", page.get_by_role("tab", name=rx)),
        ("text_exact", page.get_by_text(clean_target, exact=True)),
        ("text", page.get_by_text(rx)),
        ("title", page.get_by_title(rx)),
        ("alt_text", page.get_by_alt_text(rx)),
    ]

    text_first = page.get_by_text(rx).first
    attempts.extend(
        [
            ("text_ancestor_link", text_first.locator("xpath=ancestor-or-self::a[1]")),
            ("text_ancestor_button", text_first.locator("xpath=ancestor-or-self::button[1]")),
            ("text_ancestor_role_button", text_first.locator("xpath=ancestor-or-self::*[@role='button'][1]")),
            ("text_ancestor_role_link", text_first.locator("xpath=ancestor-or-self::*[@role='link'][1]")),
        ]
    )

    for strategy, locator in attempts:
        if _first_clickable(locator, timeout_ms=timeout_ms):
            return {
                "ok": True,
                "strategy": strategy,
                "target_text": clean_target,
                "url": page.url,
                "title": page.title(),
            }

    return {
        "ok": False,
        "error": "target_not_found",
        "target_text": clean_target,
        "url": page.url,
        "title": page.title(),
    }


def fill_by_semantics(
    page: Page,
    field_hint: str,
    value: str,
    *,
    timeout_ms: int = 2500,
) -> dict[str, Any]:
    clean_hint = str(field_hint or "").strip()
    clean_value = str(value or "")
    if not clean_hint:
        return {"ok": False, "error": "empty_field_hint"}

    rx = _regex_from_text(clean_hint)

    attempts: list[tuple[str, Locator]] = [
        ("label", page.get_by_label(rx)),
        ("placeholder", page.get_by_placeholder(rx)),
        ("role_textbox", page.get_by_role("textbox", name=rx)),
    ]

    for strategy, locator in attempts:
        if _first_fill(locator, clean_value, timeout_ms=timeout_ms):
            return {
                "ok": True,
                "strategy": strategy,
                "field_hint": clean_hint,
                "typed_value": clean_value,
                "url": page.url,
                "title": page.title(),
            }

    try:
        fallback = page.get_by_role("textbox")
        if _first_fill(fallback, clean_value, timeout_ms=timeout_ms):
            return {
                "ok": True,
                "strategy": "role_textbox_first_fallback",
                "field_hint": clean_hint,
                "typed_value": clean_value,
                "url": page.url,
                "title": page.title(),
            }
    except Exception:
        pass

    return {
        "ok": False,
        "error": "field_not_found",
        "field_hint": clean_hint,
        "url": page.url,
        "title": page.title(),
    }


def type_into_focused_or_first_textbox(
    page: Page,
    text: str,
    *,
    timeout_ms: int = 2500,
) -> dict[str, Any]:
    clean_text = str(text or "")
    if not clean_text:
        return {"ok": False, "error": "empty_text"}

    attempts: list[tuple[str, Locator]] = [
        ("focused", page.locator(":focus")),
        ("role_textbox_first", page.get_by_role("textbox")),
        ("input_or_textarea_first", page.locator("input, textarea")),
    ]

    for strategy, locator in attempts:
        if _first_fill(locator, clean_text, timeout_ms=timeout_ms):
            return {
                "ok": True,
                "strategy": strategy,
                "typed_value": clean_text,
                "url": page.url,
                "title": page.title(),
            }

    return {
        "ok": False,
        "error": "textbox_not_found",
        "typed_value": clean_text,
        "url": page.url,
        "title": page.title(),
    }


def press_key(page: Page, key: str, *, timeout_ms: int = 1200) -> dict[str, Any]:
    clean_key = str(key or "").strip()
    if not clean_key:
        return {"ok": False, "error": "empty_key"}

    try:
        page.keyboard.press(clean_key)
        page.wait_for_timeout(timeout_ms)
        return {
            "ok": True,
            "key": clean_key,
            "url": page.url,
            "title": page.title(),
        }
    except PlaywrightTimeoutError:
        return {
            "ok": False,
            "error": "press_timeout",
            "key": clean_key,
            "url": page.url,
            "title": page.title(),
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "key": clean_key,
            "url": page.url,
            "title": page.title(),
        }
