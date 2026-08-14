#!/usr/bin/env python3
"""Записать измеренную задержку от коммита исходного сайта до публикации."""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
DEFAULT_SOURCE = REPO / ".src"
OUT = REPO / "status" / "delivery.json"


def git(source: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(source), *args], text=True, capture_output=True)
    if result.returncode:
        raise SystemExit(f"record-delivery: git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def main() -> int:
    source = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_SOURCE
    if not (source / ".git").exists():
        raise SystemExit(f"record-delivery: checkout источника не найден: {source}")

    source_commit = git(source, "rev-parse", "HEAD")
    source_time = dt.datetime.fromisoformat(git(source, "log", "-1", "--format=%cI"))
    published_at = dt.datetime.now(dt.timezone.utc)
    delay = max(0.0, (published_at - source_time).total_seconds() / 60)

    history: list[dict] = []
    if OUT.is_file():
        try:
            existing = json.loads(OUT.read_text(encoding="utf-8"))
            history = existing.get("entries", []) if isinstance(existing, dict) else []
            if not isinstance(history, list):
                raise ValueError("entries не список")
        except (ValueError, json.JSONDecodeError) as exc:
            raise SystemExit(f"record-delivery: {OUT} повреждён: {exc}")

    history.append(
        {
            "source_commit": source_commit,
            "source_committed_at": source_time.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
            "published_at": published_at.isoformat().replace("+00:00", "Z"),
            "delay_minutes": round(delay, 1),
        }
    )
    payload = {
        "entries": history[-50:],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "delivery: "
        f"{payload['entries'][-1]['source_commit'][:12]} → "
        f"{payload['entries'][-1]['delay_minutes']} мин."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
