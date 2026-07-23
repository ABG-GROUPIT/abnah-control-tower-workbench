from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import Header, HTTPException, Query, status

from loaders.db import ROOT_DIR


def _env_value(name: str) -> str:
    load_dotenv(ROOT_DIR / ".env")
    return os.getenv(name, "").strip()


def require_feed_token(
    token: str | None = Query(default=None),
    x_feed_token: str | None = Header(default=None, alias="X-Feed-Token"),
) -> None:
    expected = _env_value("FEED_TOKEN")
    if not expected:
        return
    supplied = token or x_feed_token
    if supplied != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing feed token")


def require_admin_token(x_admin_token: str | None = Header(default=None, alias="X-Admin-Token")) -> None:
    expected = _env_value("ADMIN_TOKEN")
    if not expected:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="ADMIN_TOKEN is not configured")
    if x_admin_token != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing admin token")

