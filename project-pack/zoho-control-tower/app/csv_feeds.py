from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response

from app.auth import require_feed_token
from app.db import get_engine
from generator.outlets import OUTLETS
from loaders.db import query_to_csv_text, query_to_csv_text_filtered
from loaders.schema import ALL_FEED_TABLES, OPERATIONAL_TABLES


router = APIRouter()
OUTLETS_BY_CODE = {outlet["outlet_code"]: outlet for outlet in OUTLETS}


def csv_response(report_name: str) -> Response:
    config = ALL_FEED_TABLES[report_name]
    csv_text = query_to_csv_text(get_engine(), config["table"], config["columns"], config.get("order_by"))
    return Response(
        content=csv_text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'inline; filename="{report_name}.csv"'},
    )


def outlet_csv_response(report_name: str, outlet_code: str) -> Response:
    outlet_code = outlet_code.upper()
    if report_name not in OPERATIONAL_TABLES:
        raise HTTPException(status_code=404, detail="Outlet-specific feeds exist only for operational reports")
    outlet = OUTLETS_BY_CODE.get(outlet_code)
    if outlet is None:
        raise HTTPException(status_code=404, detail=f"Unknown outlet code: {outlet_code}")

    config = OPERATIONAL_TABLES[report_name]
    csv_text = query_to_csv_text_filtered(
        get_engine(),
        config["table"],
        config["columns"],
        {config["outlet_column"]: outlet["outlet_name"]},
        config.get("order_by"),
    )
    filename = f"{report_name}_{outlet_code}.csv"
    return Response(
        content=csv_text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


def make_feed_endpoint(report_name: str):
    def endpoint(_: None = Depends(require_feed_token)) -> Response:
        return csv_response(report_name)

    endpoint.__name__ = f"feed_{report_name}"
    return endpoint


def make_outlet_feed_endpoint(report_name: str, outlet_code: str):
    def endpoint(_: None = Depends(require_feed_token)) -> Response:
        return outlet_csv_response(report_name, outlet_code)

    endpoint.__name__ = f"feed_{report_name}_{outlet_code.lower()}"
    return endpoint


for _report_name in ALL_FEED_TABLES:
    router.add_api_route(
        f"/zoho/{_report_name}.csv",
        make_feed_endpoint(_report_name),
        methods=["GET"],
        summary=f"CSV feed for {_report_name}",
    )


for _report_name in OPERATIONAL_TABLES:
    for _outlet in OUTLETS:
        _outlet_code = _outlet["outlet_code"]
        _endpoint = make_outlet_feed_endpoint(_report_name, _outlet_code)
        router.add_api_route(
            f"/zoho/{_report_name}_{_outlet_code}.csv",
            _endpoint,
            methods=["GET"],
            summary=f"CSV feed for {_report_name} at {_outlet_code}",
        )
        router.add_api_route(
            f"/zoho/{_outlet_code}/{_report_name}.csv",
            _endpoint,
            methods=["GET"],
            summary=f"CSV feed for {_report_name} at {_outlet_code}",
        )
