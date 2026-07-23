from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_admin_token
from loaders.db import get_engine
from loaders.delete_month import delete_month
from loaders.load_month import load_month
from loaders.status import loaded_months, raw_row_counts, registry_counts
from manage_demo import reset_month_1, reset_to_month


router = APIRouter(prefix="/admin", dependencies=[Depends(require_admin_token)])


@router.post("/reset-month-1")
def admin_reset_month_1() -> dict[str, str]:
    reset_month_1()
    return {"status": "complete", "state": "month_01"}


@router.post("/load-month/{month}")
def admin_load_month(month: int) -> dict:
    if month not in {2, 3}:
        raise HTTPException(status_code=400, detail="Only Month 2 or Month 3 can be loaded incrementally")
    counts = load_month(get_engine(), month, notes=f"Admin API load Month {month}")
    return {"status": "complete", "month": month, "counts": counts}


@router.post("/delete-month/{month}")
def admin_delete_month(month: int) -> dict:
    if month not in {2, 3}:
        raise HTTPException(status_code=400, detail="Only Month 2 or Month 3 can be deleted through this endpoint")
    counts = delete_month(get_engine(), month)
    return {"status": "complete", "month": month, "deleted": counts}


@router.post("/reset-to-month/{month}")
def admin_reset_to_month(month: int) -> dict[str, str | int]:
    if month not in {1, 2}:
        raise HTTPException(status_code=400, detail="Reset target must be Month 1 or Month 2")
    reset_to_month(month)
    return {"status": "complete", "state_month": month}


@router.get("/status")
def admin_status() -> dict:
    engine = get_engine()
    return {
        "loaded_months": loaded_months(engine),
        "raw_row_counts": raw_row_counts(engine),
        "registry_counts": registry_counts(engine),
    }

