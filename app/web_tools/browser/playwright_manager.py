from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
from uuid import uuid4

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from app.web_tools.config import WebToolsConfig


BrowserName = Literal["chromium", "firefox", "webkit"]


@dataclass(slots=True)
class PlaywrightSession:
    playwright: Playwright
    browser: Browser
    context: BrowserContext
    page: Page


@dataclass(slots=True)
class PlaywrightManager:
    """
    Local Playwright lifecycle manager.

    Important behavior:
    - Keep one Playwright engine alive in-process
    - Reopen browser/context/page when needed
    - Allow manual browser close + reopen without restarting the whole engine
    """

    config: WebToolsConfig = field(default_factory=WebToolsConfig)
    _sessions: dict[str, PlaywrightSession] = field(default_factory=dict)
    _playwright: Playwright | None = None
    _active_session_id: str = ""

    def _ensure_playwright(self) -> Playwright:
        if self._playwright is None:
            self._playwright = sync_playwright().start()
        return self._playwright

    def start_session(self) -> PlaywrightSession:
        playwright = self._ensure_playwright()

        browser_type = self._resolve_browser_type(playwright, self.config.browser_name)
        browser = browser_type.launch(
            headless=self.config.headless,
            slow_mo=self.config.slow_mo_ms,
        )

        context = browser.new_context()
        context.set_default_timeout(self.config.action_timeout_ms)
        context.set_default_navigation_timeout(self.config.navigation_timeout_ms)

        page = context.new_page()

        return PlaywrightSession(
            playwright=playwright,
            browser=browser,
            context=context,
            page=page,
        )

    def stop_session(self, session: PlaywrightSession) -> None:
        try:
            try:
                session.context.close()
            except Exception:
                pass
        finally:
            try:
                session.browser.close()
            except Exception:
                pass

    def shutdown(self) -> None:
        closed_count = self.close_all_persistent_sessions()
        _ = closed_count

        if self._playwright is not None:
            try:
                self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

    def create_persistent_session(self) -> tuple[str, PlaywrightSession]:
        session_id = f"web_{uuid4().hex[:12]}"
        session = self.start_session()
        self._sessions[session_id] = session
        self._active_session_id = session_id
        return session_id, session

    def has_persistent_session(self, session_id: str) -> bool:
        clean_session_id = str(session_id or "").strip()
        return clean_session_id in self._sessions

    def get_persistent_session(self, session_id: str) -> PlaywrightSession:
        clean_session_id = str(session_id or "").strip()
        session = self._sessions.get(clean_session_id)
        if session is None:
            raise KeyError(f"Unknown web session: {clean_session_id}")
        self._active_session_id = clean_session_id
        return session

    def get_active_persistent_session(self, *, create: bool = True, bring_to_front: bool = False) -> tuple[str, PlaywrightSession]:
        if self._active_session_id:
            session = self._sessions.get(self._active_session_id)
            if self._session_is_alive(session):
                if bring_to_front:
                    self.bring_session_to_front(session)
                return self._active_session_id, session
            self._sessions.pop(self._active_session_id, None)
            self._active_session_id = ""

        for session_id, session in list(self._sessions.items()):
            if self._session_is_alive(session):
                self._active_session_id = session_id
                if bring_to_front:
                    self.bring_session_to_front(session)
                return session_id, session
            self._sessions.pop(session_id, None)

        if not create:
            raise KeyError("No active web session")

        session_id, session = self.create_persistent_session()
        if bring_to_front:
            self.bring_session_to_front(session)
        return session_id, session

    def close_persistent_session(self, session_id: str) -> bool:
        clean_session_id = str(session_id or "").strip()
        session = self._sessions.pop(clean_session_id, None)
        if session is None:
            return False

        if self._active_session_id == clean_session_id:
            self._active_session_id = ""

        self.stop_session(session)
        return True

    def list_persistent_sessions(self) -> list[str]:
        return list(self._sessions.keys())

    def close_all_persistent_sessions(self) -> int:
        session_ids = list(self._sessions.keys())
        closed_count = 0

        for session_id in session_ids:
            if self.close_persistent_session(session_id):
                closed_count += 1

        return closed_count

    @staticmethod
    def bring_session_to_front(session: PlaywrightSession | None) -> bool:
        if session is None:
            return False
        try:
            session.page.bring_to_front()
            return True
        except Exception:
            return False

    @staticmethod
    def _session_is_alive(session: PlaywrightSession | None) -> bool:
        if session is None:
            return False
        try:
            _ = session.page.url
            _ = session.page.title()
            return True
        except Exception:
            return False

    @staticmethod
    def _resolve_browser_type(playwright: Playwright, browser_name: str):
        clean_name = str(browser_name or "chromium").strip().lower()

        if clean_name == "chromium":
            return playwright.chromium
        if clean_name == "firefox":
            return playwright.firefox
        if clean_name == "webkit":
            return playwright.webkit

        raise ValueError(f"Unsupported browser_name: {clean_name}")


_SHARED_PLAYWRIGHT_MANAGER: PlaywrightManager | None = None


def get_shared_playwright_manager() -> PlaywrightManager:
    global _SHARED_PLAYWRIGHT_MANAGER
    if _SHARED_PLAYWRIGHT_MANAGER is None:
        _SHARED_PLAYWRIGHT_MANAGER = PlaywrightManager()
    return _SHARED_PLAYWRIGHT_MANAGER
