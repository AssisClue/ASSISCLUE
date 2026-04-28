from __future__ import annotations

from typing import Any

from app.live_listeners.administrative_listener.administrative_browser_runtime import (
    get_administrative_browser_runtime,
)
from app.web_tools.browser.navigation import open_url
from app.web_tools.browser.browser_service_client import call_browser_service
from app.web_tools.browser.semantic_actions import (
    click_by_semantics,
    press_key,
)

from .administrative_command_payload_cleaner import (
    build_temp_text_path,
    clean_filename_payload,
    clean_search_payload,
)


def run_administrative_browser_command(command: dict[str, Any]) -> dict[str, Any]:
    action_name = str(command.get("action_name") or "").strip()
    payload_text_raw = str(command.get("payload_text") or "").strip()
    payload_text = payload_text_raw

    if action_name == "open_url":
        if not payload_text:
            return {
                "ok": False,
                "action_name": action_name,
                "error": "missing_url_payload",
            }
        result = call_browser_service("open_url", {"url": payload_text})
        result["action_name"] = action_name
        return result

    service_actions = {
        "open_browser",
        "browser_refresh",
        "browser_back",
        "browser_forward",
        "browser_scroll_down",
        "browser_scroll_up",
        "browser_scroll_top",
        "browser_screenshot",
    }
    if action_name in service_actions:
        payload: dict[str, Any] = {}
        if action_name == "browser_screenshot":
            payload = {"full_page": True, "name_prefix": "admin_browser_capture"}
        result = call_browser_service(action_name, payload)
        result["action_name"] = action_name
        return result

    if action_name in {"browser_save_visible_text", "browser_save_full_page_text"}:
        filename = clean_filename_payload(payload_text)
        output_path = build_temp_text_path(filename)
        result = call_browser_service(action_name, {"output_path": str(output_path)})
        result["action_name"] = action_name
        return result

    if action_name == "look_for":
        search_text = clean_search_payload(payload_text)
        if not search_text:
            return {
                "ok": False,
                "action_name": action_name,
                "error": "missing_search_payload",
                "payload_raw": payload_text_raw,
                "payload_clean": search_text,
            }

        result = call_browser_service("look_for", {"query": search_text, "raw_query": payload_text_raw})
        result["action_name"] = action_name
        return result

    if action_name == "browser_click":
        result = call_browser_service("browser_click", {"target_text": payload_text})
        result["action_name"] = action_name
        return result

    if action_name == "browser_type":
        result = call_browser_service("browser_type", {"text": payload_text})
        result["action_name"] = action_name
        return result

    runtime = get_administrative_browser_runtime()

    if action_name == "browser_new_tab":
        session, created = runtime.ensure_session()
        new_page = session.context.new_page()
        session.page = new_page

        opened = ""
        if payload_text:
            opened = payload_text
            open_url(new_page, url=payload_text)

        try:
            new_page.bring_to_front()
        except Exception:
            pass

        return {
            "ok": True,
            "action_name": action_name,
            "executed_via": "administrative_browser_runtime",
            "used_existing_session": not created,
            "opened_url": opened,
            "url": new_page.url,
            "title": new_page.title(),
        }

    if action_name == "browser_close_tab":
        session = runtime.get_session()
        if session is None:
            return {
                "ok": False,
                "action_name": action_name,
                "error": "no_active_browser_session",
            }

        pages = list(session.context.pages)
        is_last = len(pages) <= 1

        try:
            session.page.close()
        except Exception as exc:
            return {
                "ok": False,
                "action_name": action_name,
                "error": f"{type(exc).__name__}: {exc}",
            }

        if is_last:
            new_page = session.context.new_page()
            session.page = new_page
            try:
                new_page.bring_to_front()
            except Exception:
                pass

            return {
                "ok": True,
                "action_name": action_name,
                "executed_via": "administrative_browser_runtime",
                "closed_last_tab": True,
                "url": new_page.url,
                "title": new_page.title(),
            }

        remaining = list(session.context.pages)
        session.page = remaining[0] if remaining else session.context.new_page()
        try:
            session.page.bring_to_front()
        except Exception:
            pass

        return {
            "ok": True,
            "action_name": action_name,
            "executed_via": "administrative_browser_runtime",
            "closed_last_tab": False,
            "url": session.page.url,
            "title": session.page.title(),
        }

    if action_name == "browser_switch_tab_next":
        session = runtime.get_session()
        if session is None:
            return {
                "ok": False,
                "action_name": action_name,
                "error": "no_active_browser_session",
            }

        pages = list(session.context.pages)
        if not pages:
            session.page = session.context.new_page()
            return {
                "ok": True,
                "action_name": action_name,
                "executed_via": "administrative_browser_runtime",
                "tab_index": 0,
                "tab_count": 1,
                "url": session.page.url,
                "title": session.page.title(),
            }

        try:
            current_index = pages.index(session.page)
        except Exception:
            current_index = 0

        next_index = (current_index + 1) % len(pages)
        next_page = pages[next_index]
        session.page = next_page

        try:
            next_page.bring_to_front()
        except Exception:
            pass

        return {
            "ok": True,
            "action_name": action_name,
            "executed_via": "administrative_browser_runtime",
            "tab_index": next_index,
            "tab_count": len(pages),
            "url": next_page.url,
            "title": next_page.title(),
        }

    if action_name == "browser_click_text":
        session = runtime.get_session()
        if session is None:
            return {
                "ok": False,
                "action_name": action_name,
                "error": "no_active_browser_session",
            }

        click_result = click_by_semantics(session.page, payload_text)
        return {
            "ok": bool(click_result.get("ok", False)),
            "action_name": action_name,
            "executed_via": "administrative_browser_runtime",
            "payload_text": payload_text,
            "data": click_result,
        }

    if action_name == "browser_press":
        session = runtime.get_session()
        if session is None:
            return {
                "ok": False,
                "action_name": action_name,
                "error": "no_active_browser_session",
            }

        press_result = press_key(session.page, payload_text or "Enter", timeout_ms=1200)
        return {
            "ok": bool(press_result.get("ok", False)),
            "action_name": action_name,
            "executed_via": "administrative_browser_runtime",
            "payload_text": payload_text,
            "data": press_result,
        }

    return {
        "ok": False,
        "action_name": action_name,
        "error": "unsupported_browser_action",
        "payload_text": payload_text,
    }
