from __future__ import annotations

import os


DEFAULT_BROWSER_EMAIL = os.getenv(
    "ADMIN_BROWSER_DEFAULT_EMAIL",
    "default.test.mail@example.com",
).strip()

DEFAULT_BROWSER_PASSWORD = os.getenv(
    "ADMIN_BROWSER_DEFAULT_PASSWORD",
    "default_password",
).strip()

GMAIL_SIGNIN_URL = os.getenv(
    "ADMIN_BROWSER_GMAIL_SIGNIN_URL",
    "https://accounts.google.com",
).strip()

GMAIL_FALLBACK_RECOVERY_URL = os.getenv(
    "ADMIN_BROWSER_GMAIL_RECOVERY_URL",
    "https://accounts.google.com/signin/usernamerecovery",
).strip()