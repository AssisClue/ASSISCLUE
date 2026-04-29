from __future__ import annotations

import asyncio
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from app.ui_local import app as ui_app


class ControlButtonTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        ui_app.CONTROL_STATE.update(
            {
                "busy": False,
                "action": "",
                "status": "idle",
                "message": "ready",
                "last_code": None,
                "last_stdout": "",
                "last_stderr": "",
            }
        )

    async def test_start_runs_start_script(self) -> None:
        calls = []

        def fake_run(args, **_kwargs):
            calls.append(args)
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="STARTED", stderr="")

        with patch.object(ui_app.subprocess, "run", fake_run):
            result = await ui_app._run_control_action("start")

        self.assertTrue(result["ok"])
        self.assertEqual(Path(calls[0][1]).name, "start_main_stack.py")

    async def test_stop_runs_stop_script(self) -> None:
        calls = []

        def fake_run(args, **_kwargs):
            calls.append(args)
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="STOPPED", stderr="")

        with patch.object(ui_app.subprocess, "run", fake_run):
            result = await ui_app._run_control_action("stop")

        self.assertTrue(result["ok"])
        self.assertEqual(Path(calls[0][1]).name, "stop_main_stack.py")

    async def test_second_click_is_blocked_while_busy(self) -> None:
        started = asyncio.Event()
        release = asyncio.Event()

        async def fake_action(action: str):
            started.set()
            await release.wait()
            return {"ok": True, "action": action, "code": 0, "stdout": "", "stderr": ""}

        with patch.object(ui_app, "_run_control_action", fake_action):
            first = asyncio.create_task(ui_app.api_control_start())
            await started.wait()
            second = await ui_app.api_control_stop()
            release.set()
            first_result = await first

        self.assertTrue(first_result["ok"])
        self.assertFalse(second["ok"])
        self.assertEqual(second["message"], "control already busy")

    async def test_restart_action_is_not_allowed(self) -> None:
        with self.assertRaises(ValueError):
            await ui_app._run_control_action("restart")

    async def test_start_endpoint_sets_final_running_status(self) -> None:
        async def fake_action(_action: str):
            return {"ok": True, "action": "start", "code": 0, "stdout": "ok", "stderr": "", "message": "ok"}

        with patch.object(ui_app, "_run_control_action", fake_action):
            result = await ui_app.api_control_start()

        self.assertTrue(result["ok"])
        self.assertEqual(ui_app.CONTROL_STATE["status"], "running")
        self.assertEqual(ui_app.CONTROL_STATE["message"], "started")

    async def test_stop_endpoint_sets_final_stopped_status(self) -> None:
        async def fake_action(_action: str):
            return {"ok": True, "action": "stop", "code": 0, "stdout": "ok", "stderr": "", "message": "ok"}

        with patch.object(ui_app, "_run_control_action", fake_action):
            result = await ui_app.api_control_stop()

        self.assertTrue(result["ok"])
        self.assertEqual(ui_app.CONTROL_STATE["status"], "stopped")
        self.assertEqual(ui_app.CONTROL_STATE["message"], "stopped")

    async def test_stop_failure_sets_error_status(self) -> None:
        async def fake_action(_action: str):
            return {"ok": False, "action": "stop", "code": 1, "stdout": "", "stderr": "boom", "message": "failed"}

        with patch.object(ui_app, "_run_control_action", fake_action):
            result = await ui_app.api_control_stop()

        self.assertFalse(result["ok"])
        self.assertEqual(ui_app.CONTROL_STATE["status"], "error")
        self.assertEqual(ui_app.CONTROL_STATE["message"], "stop failed")

    async def test_shutdown_endpoint_launches_shutdown(self) -> None:
        called = {"count": 0}

        def fake_launch():
            called["count"] += 1

        with patch.object(ui_app, "_launch_shutdown_action", fake_launch):
            result = await ui_app.api_control_shutdown()

        self.assertTrue(result["ok"])
        self.assertEqual(called["count"], 1)
        self.assertEqual(ui_app.CONTROL_STATE["status"], "shutdown")
        self.assertEqual(ui_app.CONTROL_STATE["message"], "shutting down")

    def test_shutdown_launcher_uses_full_stop_script(self) -> None:
        calls = []

        def fake_popen(args, **kwargs):
            calls.append((args, kwargs))
            class DummyProc:
                pass
            return DummyProc()

        with patch.object(ui_app.subprocess, "Popen", fake_popen):
            ui_app._launch_shutdown_action()

        self.assertEqual(Path(calls[0][0][1]).name, "stop_main_stack.py")
        self.assertNotIn("--backend-only", calls[0][0])

    def test_restart_button_removed_from_template(self) -> None:
        html = (Path(ui_app.TEMPLATES_DIR) / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("btn-restart", html)
        self.assertNotIn("/api/control/restart", html)
        self.assertNotIn("RESTART", html)

    def test_shutdown_button_exists_in_template(self) -> None:
        html = (Path(ui_app.TEMPLATES_DIR) / "index.html").read_text(encoding="utf-8")
        self.assertIn("btn-shutdown", html)
        self.assertIn("SHUTDOWN", html)


if __name__ == "__main__":
    unittest.main()
