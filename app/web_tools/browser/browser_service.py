from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from app.system_support.runtime_jsonl import append_jsonl, read_new_runtime_jsonl_lines
from app.web_tools.browser.navigation import open_url
from app.web_tools.browser.playwright_manager import PlaywrightManager, PlaywrightSession
from app.web_tools.browser.screenshots import capture_page_screenshot
from app.web_tools.browser.semantic_actions import (
    click_by_semantics,
    press_key,
    type_into_focused_or_first_textbox,
)


APP_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = APP_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
BROWSER_RUNTIME_DIR = RUNTIME_DIR / "browser"
BROWSER_QUEUES_DIR = RUNTIME_DIR / "queues" / "browser"
BROWSER_STATUS_DIR = RUNTIME_DIR / "status" / "browser"
BROWSER_REQUEST_QUEUE_JSONL = BROWSER_QUEUES_DIR / "request_queue.jsonl"
BROWSER_RESULT_QUEUE_JSONL = BROWSER_QUEUES_DIR / "result_queue.jsonl"
BROWSER_STATUS_JSON = BROWSER_STATUS_DIR / "status.json"
BROWSER_LATEST_SAVED_TEXT_CONTEXT_JSON = BROWSER_RUNTIME_DIR / "latest_saved_text_context.json"

BROWSER_SERVICE_NAME = "browser_service"
BROWSER_SERVICE_POLL_SECONDS = 0.20


def ensure_browser_runtime_dirs() -> None:
    BROWSER_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    BROWSER_QUEUES_DIR.mkdir(parents=True, exist_ok=True)
    BROWSER_STATUS_DIR.mkdir(parents=True, exist_ok=True)
    for path in (BROWSER_REQUEST_QUEUE_JSONL, BROWSER_RESULT_QUEUE_JSONL):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def reset_browser_runtime_queues() -> None:
    ensure_browser_runtime_dirs()
    BROWSER_REQUEST_QUEUE_JSONL.write_text("", encoding="utf-8")
    BROWSER_RESULT_QUEUE_JSONL.write_text("", encoding="utf-8")
    if BROWSER_STATUS_JSON.exists():
        BROWSER_STATUS_JSON.unlink()
    if BROWSER_LATEST_SAVED_TEXT_CONTEXT_JSON.exists():
        BROWSER_LATEST_SAVED_TEXT_CONTEXT_JSON.unlink()


def write_latest_saved_text_context(payload: dict[str, Any]) -> None:
    ensure_browser_runtime_dirs()
    BROWSER_LATEST_SAVED_TEXT_CONTEXT_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def load_browser_status() -> dict[str, Any]:
    if not BROWSER_STATUS_JSON.exists():
        return {}
    try:
        payload = json.loads(BROWSER_STATUS_JSON.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:
        pass
    return {}


def write_browser_status(state: str, **extra: Any) -> None:
    ensure_browser_runtime_dirs()
    current = load_browser_status()
    payload: dict[str, Any] = {
        "ok": state != "error",
        "state": state,
        "service": BROWSER_SERVICE_NAME,
        "updated_at": time.time(),
        "last_processed_line_number": int(current.get("last_processed_line_number", 0) or 0),
        "last_processed_byte_offset": int(current.get("last_processed_byte_offset", 0) or 0),
    }
    payload.update(extra)
    BROWSER_STATUS_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


class BrowserService:
    def __init__(self) -> None:
        self.manager = PlaywrightManager()
        self._running = False
        self._status_cache: dict[str, Any] | None = None

    def _load_status_cache(self) -> dict[str, Any]:
        if self._status_cache is None:
            self._status_cache = load_browser_status()
        return self._status_cache

    def _update_status(self, state: str, **extra: Any) -> None:
        status = self._load_status_cache()
        status["ok"] = state != "error"
        status["state"] = state
        status["service"] = BROWSER_SERVICE_NAME
        status["updated_at"] = time.time()
        status["last_processed_line_number"] = int(status.get("last_processed_line_number", 0) or 0)
        status["last_processed_byte_offset"] = int(status.get("last_processed_byte_offset", 0) or 0)
        status.update(extra)

    def _flush_status(self) -> None:
        ensure_browser_runtime_dirs()
        BROWSER_STATUS_JSON.write_text(
            json.dumps(self._load_status_cache(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _active_session(self, *, create: bool, bring_to_front: bool = True) -> tuple[str, PlaywrightSession]:
        return self.manager.get_active_persistent_session(create=create, bring_to_front=bring_to_front)

    def _session_payload(self, session_id: str, session: PlaywrightSession) -> dict[str, Any]:
        return {
            "session_id": session_id,
            "url": session.page.url,
            "title": session.page.title(),
        }

    def process_request(self, request: dict[str, Any]) -> dict[str, Any]:
        request_id = str(request.get("request_id") or "").strip()
        action = str(request.get("action") or "").strip()
        payload = request.get("payload", {}) if isinstance(request.get("payload", {}), dict) else {}

        result: dict[str, Any] = {
            "request_id": request_id,
            "action": action,
            "ok": False,
            "executed_via": BROWSER_SERVICE_NAME,
        }

        try:
            if action == "open_browser":
                existing = bool(self.manager.list_persistent_sessions())
                session_id, session = self._active_session(create=True, bring_to_front=True)
                result.update({"ok": True, "used_existing_session": existing, **self._session_payload(session_id, session)})
                return result

            if action == "open_url":
                url = str(payload.get("url") or "").strip()
                if not url:
                    result["error"] = "missing_url_payload"
                    return result
                existing = bool(self.manager.list_persistent_sessions())
                session_id, session = self._active_session(create=True, bring_to_front=True)
                opened = open_url(session.page, url=url)
                result.update(
                    {
                        "ok": bool(opened.get("ok", True)),
                        "used_existing_session": existing,
                        "payload_text": url,
                        "data": opened,
                        **self._session_payload(session_id, session),
                    }
                )
                return result

            if action == "browser_screenshot":
                url = str(payload.get("url") or "").strip()
                session_id, session = self._active_session(create=True, bring_to_front=True)
                if url:
                    open_url(session.page, url=url)
                capture = capture_page_screenshot(
                    session.page,
                    name_prefix=str(payload.get("name_prefix") or "browser_service_capture"),
                    full_page=bool(payload.get("full_page", True)),
                )
                result.update({"ok": bool(capture.get("ok", False)), "data": capture, **self._session_payload(session_id, session)})
                return result

            if action == "look_for":
                query = str(payload.get("query") or "").strip()
                if not query:
                    result["error"] = "missing_search_payload"
                    return result

                existing = bool(self.manager.list_persistent_sessions())
                session_id, session = self._active_session(create=True, bring_to_front=True)
                open_url(session.page, url="https://duckduckgo.com/")

                search_box = session.page.locator("input[name=q], textarea[name=q]")
                search_box.first.click(timeout=2500)
                search_box.first.fill(query, timeout=2500)

                press_result = press_key(session.page, "Enter", timeout_ms=1200)
                result.update(
                    {
                        "ok": bool(press_result.get("ok", False)),
                        "used_existing_session": existing,
                        "payload_text": query,
                        "payload_raw": str(payload.get("raw_query") or query).strip(),
                        "payload_clean": query,
                        "data": press_result,
                        **self._session_payload(session_id, session),
                    }
                )
                return result

            if action == "browser_click":
                target_text = str(payload.get("target_text") or "").strip()
                if not target_text:
                    result["error"] = "empty_target"
                    return result

                session_id, session = self._active_session(create=False, bring_to_front=True)
                click_result = click_by_semantics(session.page, target_text)
                result.update(
                    {
                        "ok": bool(click_result.get("ok", False)),
                        "payload_text": target_text,
                        "data": click_result,
                        **self._session_payload(session_id, session),
                    }
                )
                return result

            if action == "browser_type":
                text = str(payload.get("text") or "")
                if not text:
                    result["error"] = "empty_text"
                    return result

                session_id, session = self._active_session(create=False, bring_to_front=True)
                type_result = type_into_focused_or_first_textbox(session.page, text)
                result.update(
                    {
                        "ok": bool(type_result.get("ok", False)),
                        "payload_text": text,
                        "data": type_result,
                        **self._session_payload(session_id, session),
                    }
                )
                return result

            if action == "browser_refresh":
                existing = bool(self.manager.list_persistent_sessions())
                session_id, session = self._active_session(create=True, bring_to_front=True)
                response = session.page.reload(wait_until="domcontentloaded")
                result.update(
                    {
                        "ok": True,
                        "used_existing_session": existing,
                        "status": response.status if response is not None else None,
                        **self._session_payload(session_id, session),
                    }
                )
                return result

            if action == "browser_back":
                session_id, session = self._active_session(create=False, bring_to_front=True)
                response = session.page.go_back(wait_until="domcontentloaded")
                result.update(
                    {
                        "ok": True,
                        "status": response.status if response is not None else None,
                        "had_history": response is not None,
                        **self._session_payload(session_id, session),
                    }
                )
                return result

            if action == "browser_forward":
                session_id, session = self._active_session(create=False, bring_to_front=True)
                response = session.page.go_forward(wait_until="domcontentloaded")
                result.update(
                    {
                        "ok": True,
                        "status": response.status if response is not None else None,
                        "had_history": response is not None,
                        **self._session_payload(session_id, session),
                    }
                )
                return result

            if action == "browser_scroll_down":
                session_id, session = self._active_session(create=False, bring_to_front=True)
                session.page.mouse.wheel(0, int(payload.get("delta_y", 900) or 900))
                result.update({"ok": True, **self._session_payload(session_id, session)})
                return result

            if action == "browser_scroll_up":
                session_id, session = self._active_session(create=False, bring_to_front=True)
                session.page.mouse.wheel(0, -abs(int(payload.get("delta_y", 900) or 900)))
                result.update({"ok": True, **self._session_payload(session_id, session)})
                return result

            if action == "browser_scroll_top":
                session_id, session = self._active_session(create=False, bring_to_front=True)
                session.page.evaluate("window.scrollTo(0, 0)")
                result.update({"ok": True, **self._session_payload(session_id, session)})
                return result

            if action in {"browser_save_visible_text", "browser_save_full_page_text"}:
                timeout_ms = 3000 if action == "browser_save_visible_text" else 5000
                output_path = Path(str(payload.get("output_path") or "")).expanduser()
                if not str(output_path).strip():
                    result["error"] = "missing_output_path"
                    return result

                session_id, session = self._active_session(create=False, bring_to_front=True)
                text = session.page.locator("body").inner_text(timeout=timeout_ms)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(text, encoding="utf-8")
                result.update(
                    {
                        "ok": True,
                        "saved_path": str(output_path),
                        "filename": output_path.name,
                        "chars": len(text),
                        **self._session_payload(session_id, session),
                    }
                )
                write_latest_saved_text_context(
                    {
                        "ok": True,
                        "kind": "browser_saved_text_context",
                        "saved_path": str(output_path),
                        "filename": output_path.name,
                        "chars": len(text),
                        "url": session.page.url,
                        "title": session.page.title(),
                        "source_action": action,
                        "created_at": time.time(),
                    }
                )
                return result

            if action == "session_info":
                session_id, session = self._active_session(create=False, bring_to_front=False)
                result.update({"ok": True, **self._session_payload(session_id, session)})
                return result

            result["error"] = "unsupported_browser_service_action"
            return result

        except KeyError:
            result["error"] = "no_active_browser_session"
            return result
        except Exception as exc:
            result["error"] = f"{type(exc).__name__}: {exc}"
            return result

    def run_forever(self) -> None:
        reset_browser_runtime_queues()
        self.manager.close_all_persistent_sessions()
        self._status_cache = None
        self._running = True
        self._update_status("starting")
        self._flush_status()

        current_line_number = 0
        current_byte_offset = 0

        try:
            self._update_status("running")
            self._flush_status()

            while self._running:
                new_lines = read_new_runtime_jsonl_lines(
                    BROWSER_REQUEST_QUEUE_JSONL,
                    current_byte_offset,
                    bom_at_start=True,
                )
                if not new_lines:
                    time.sleep(BROWSER_SERVICE_POLL_SECONDS)
                    continue

                for raw_line, line_end_offset in new_lines:
                    current_line_number += 1
                    current_byte_offset = line_end_offset
                    try:
                        request = json.loads(raw_line.lstrip("\ufeff").strip())
                    except Exception:
                        request = {}

                    if not isinstance(request, dict):
                        request = {}

                    result = self.process_request(request)
                    append_jsonl(BROWSER_RESULT_QUEUE_JSONL, result)
                    self._update_status(
                        "running",
                        last_processed_line_number=current_line_number,
                        last_processed_byte_offset=current_byte_offset,
                        last_request_id=str(result.get("request_id") or "").strip(),
                        last_action=str(result.get("action") or "").strip(),
                        last_result_ok=bool(result.get("ok", False)),
                    )
                    self._flush_status()
                    print(json.dumps(result, ensure_ascii=False), flush=True)

                time.sleep(BROWSER_SERVICE_POLL_SECONDS)

        except KeyboardInterrupt:
            self._update_status("stopped", reason="keyboard_interrupt")
            self._flush_status()
        except Exception as exc:
            self._update_status("error", error=f"{type(exc).__name__}: {exc}")
            self._flush_status()
            raise
        finally:
            self._update_status("stopped")
            self._flush_status()

    def stop(self) -> None:
        self._running = False


if __name__ == "__main__":
    BrowserService().run_forever()



