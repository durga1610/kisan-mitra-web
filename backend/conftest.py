"""
conftest.py — pytest configuration for the Kisan Mitra backend test suite.

This module overrides the FastAPI `verify_token` dependency at module-level
so that ALL TestClient instances (including module-level ones in test files)
are automatically authenticated. The override is applied before any test
module is imported/executed.

Without this override, every test that hits a protected endpoint would receive
HTTP 403 after F-01 (authentication) is enforced in main.py.
"""

import pytest
from fastapi.testclient import TestClient

# Import the app and the real dependency function we want to override
import os
# Enable filename bypass so tests that rely on filename-based disease
# matching (e.g. apple_scab.jpg) continue to work (F-09 gate is off
# by default in production; tests run in development mode).
os.environ.setdefault("KISAN_ALLOW_FILENAME_BYPASS", "1")
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("TESTING", "1")

from setup_database import init_db
init_db()

from main import app, verify_token


# ── Fake decoded Firebase token ───────────────────────────────────────────
FAKE_TOKEN_PAYLOAD = {
    "uid": "test_user_uid",
    "email": "testfarmer@example.com",
    "name": "Test Farmer",
}


def _fake_verify_token():
    """Stub that skips real Firebase verification and returns a fake payload."""
    return FAKE_TOKEN_PAYLOAD


# ── Apply the override at module level ────────────────────────────────────
# This runs when pytest collects conftest.py — before any test module is
# imported. All TestClient(app) instances (including module-level ones in
# test files) therefore see the override automatically.
app.dependency_overrides[verify_token] = _fake_verify_token


# ── Optional session-scoped fixture for tests that want injection ─────────
@pytest.fixture(scope="session")
def client():
    """
    A pre-configured TestClient with auth already bypassed.
    Tests can either use the module-level `client = TestClient(app)` from
    their own file, or inject this fixture — both work identically.
    """
    with TestClient(app) as c:
        yield c
