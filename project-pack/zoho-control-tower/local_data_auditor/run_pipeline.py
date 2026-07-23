#!/usr/bin/env python3
"""Run the complete local ABNAH CSV audit, LLM review and Codex packet workflow."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from audit import (
    audit_file,
    collect_csvs,
    load_contracts,
    match_contract,
    write_outputs,
)
from llm_review import OllamaClient, review_groups
from packet_builder import build_packet
from profiler import profile_file, unmatched_identity, write_profiles


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Profile local Restroworks CSVs, run two-pass Ollama review, and build a Codex packet."
    )
    parser.add_argument("--input", type=Path, default=root / "input", help="CSV file or folder")
    parser.add_argument("--output", type=Path, default=None, help="Run output folder")
    parser.add_argument("--contracts", type=Path, default=root / "contracts")
    parser.add_argument(
        "--model",
        default=os.environ.get("ABNAH_OLLAMA_MODEL", "qwen3:14b"),
        help="Local Ollama analyst model",
    )
    parser.add_argument("--verifier-model", default="", help="Defaults to --model")
    parser.add_argument(
        "--ollama-url",
        default="http://127.0.0.1:11434",
        help="Localhost Ollama base URL",
    )
    parser.add_argument(
        "--num-ctx",
        type=int,
        default=int(os.environ.get("ABNAH_OLLAMA_NUM_CTX", "32768")),
        help="Ollama context window; use 24576 for the 3050 laptop fallback",
    )
    parser.add_argument(
        "--keep-alive",
        default=os.environ.get("ABNAH_OLLAMA_KEEP_ALIVE", "0"),
        help="Ollama model retention; 0 unloads between passes to reduce memory pressure",
    )
    parser.add_argument("--skip-llm", action="store_true", help="Testing only: deterministic packet")
    parser.add_argument(
        "--only-report",
        action="append",
        default=[],
        help="Limit processing to report ID/name substring; repeatable",
    )
    parser.add_argument("--fail-on-audit-errors", action="store_true")
    args = parser.parse_args()

    run_id = datetime.now().strftime("run_%Y%m%d_%H%M%S")
    output_dir = args.output or root / "output" / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    local_dir = output_dir / "LOCAL_EVIDENCE_DO_NOT_UPLOAD"
    deterministic_dir = local_dir / "deterministic_audit"
    packet_dir = output_dir / "CODEX_PACKET"

    contracts = load_contracts(args.contracts)
    csv_files = collect_csvs(args.input)
    if not csv_files:
        print(f"No CSV files found under {args.input}", file=sys.stderr)
        return 2

    results = []
    unmatched = []
    profiles = []
    selected_files = []
    for path in csv_files:
        contract = match_contract(path, contracts)
        if contract:
            display = contract["display_name"]
            report_id = contract["report_id"]
        else:
            report_id, display = unmatched_identity(path)
        if args.only_report and not any(
            token.lower() in f"{report_id} {display}".lower() for token in args.only_report
        ):
            continue
        selected_files.append(path)
        print(f"Deterministic profile: {path.name}")
        profile = profile_file(path, contract)
        profiles.append(profile)
        if contract:
            results.append(audit_file(path, contract, deterministic_dir / "normalized"))
        else:
            unmatched.append(path)

    if not selected_files:
        print("No CSV files matched --only-report filters.", file=sys.stderr)
        return 2

    write_outputs(deterministic_dir, results, unmatched)
    write_profiles(local_dir / "full_profiles_with_local_samples.json", profiles)

    reviews = []
    llm_enabled = not args.skip_llm
    llm_error = ""
    if llm_enabled:
        try:
            client = OllamaClient(
                args.ollama_url,
                num_ctx=args.num_ctx,
                keep_alive=args.keep_alive,
            )
            reviews = review_groups(
                profiles,
                contracts,
                client,
                args.model,
                args.verifier_model or args.model,
                checkpoint_dir=root / "output" / "_local_llm_checkpoints",
            )
            write_json(local_dir / "full_local_llm_reviews.json", reviews)
        except Exception as exc:  # The deterministic evidence and packet remain usable.
            llm_error = str(exc)
            llm_enabled = False
            write_json(local_dir / "local_llm_error.json", {"error": llm_error})

    archive = build_packet(
        packet_dir,
        run_id,
        profiles,
        contracts,
        reviews,
        llm_enabled=llm_enabled,
        llm_requested=not args.skip_llm,
    )
    audit_errors = sum(result.counts().get("error", 0) for result in results)
    run_manifest = {
        "run_id": run_id,
        "input": str(args.input.resolve()),
        "selected_files": [str(path.resolve()) for path in selected_files],
        "matched_files": len(results),
        "unmatched_files": len(unmatched),
        "audit_error_count": audit_errors,
        "local_llm_requested": not args.skip_llm,
        "local_llm_completed": llm_enabled,
        "local_llm_error": llm_error,
        "analyst_model": args.model if not args.skip_llm else "",
        "verifier_model": (args.verifier_model or args.model) if not args.skip_llm else "",
        "ollama_num_ctx": args.num_ctx if not args.skip_llm else 0,
        "ollama_keep_alive": args.keep_alive if not args.skip_llm else "",
        "local_evidence_dir": str(local_dir.resolve()),
        "codex_packet_dir": str(packet_dir.resolve()),
        "codex_packet_zip": str(archive.resolve()),
    }
    write_json(output_dir / "run_manifest.json", run_manifest)

    print("")
    print(f"Processed {len(selected_files)} CSV file(s): {len(results)} matched, {len(unmatched)} unmatched.")
    print(f"Deterministic audit errors: {audit_errors}")
    print(f"Local LLM completed: {'yes' if llm_enabled else 'no'}")
    if llm_error:
        print(f"Local LLM error: {llm_error}")
    print(f"Local evidence (do not upload): {local_dir.resolve()}")
    print(f"Codex packet: {archive.resolve()}")

    if llm_error:
        return 3
    if args.fail_on_audit_errors and audit_errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
