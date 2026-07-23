from __future__ import annotations

from fastapi import FastAPI

from app.admin_routes import router as admin_router
from app.csv_feeds import router as csv_router


app = FastAPI(title="ABNAH Cafe Intelligence CSV Feed API")
app.include_router(csv_router)
app.include_router(admin_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

