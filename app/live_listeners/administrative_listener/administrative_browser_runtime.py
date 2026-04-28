from __future__ import annotations

from dataclasses import dataclass

from app.web_tools.browser.navigation import open_url
from app.web_tools.browser.playwright_manager import (
    PlaywrightManager,
    PlaywrightSession,
    get_shared_playwright_manager,
)


def _session_is_alive(session: PlaywrightSession | None) -> bool:
    if session is None:
        return False

    try:
        _ = session.page.url
        _ = session.page.title()
        return True
    except Exception:
        return False


@dataclass(slots=True)
class AdministrativeBrowserRuntime:
    manager: PlaywrightManager
    session: PlaywrightSession | None = None
    session_id: str = ""

    def _adopt_existing_session(self) -> bool:
        try:
            self.session_id, self.session = self.manager.get_active_persistent_session(create=False)
            return True
        except Exception:
            return False

    def ensure_session(self, *, url: str = "") -> tuple[PlaywrightSession, bool]:
        created = False

        if not _session_is_alive(self.session):
            self.session = None
            self.session_id = ""

        if self.session is None:
            if not self._adopt_existing_session():
                self.session_id, self.session = self.manager.get_active_persistent_session(bring_to_front=True)
                created = True

        self.manager.bring_session_to_front(self.session)

        if url:
            open_url(self.session.page, url=url)

        return self.session, created

    def get_session(self) -> PlaywrightSession | None:
        if not _session_is_alive(self.session):
            self.session = None
            self.session_id = ""
            self._adopt_existing_session()
        return self.session

    def close_session(self) -> bool:
        if self.session is None:
            return False

        if self.session_id:
            self.manager.close_persistent_session(self.session_id)
        else:
            try:
                self.manager.stop_session(self.session)
            except Exception:
                pass

        self.session = None
        self.session_id = ""
        return True


_RUNTIME: AdministrativeBrowserRuntime | None = None


def get_administrative_browser_runtime() -> AdministrativeBrowserRuntime:
    global _RUNTIME
    if _RUNTIME is None:
        _RUNTIME = AdministrativeBrowserRuntime(manager=get_shared_playwright_manager())
    return _RUNTIME
