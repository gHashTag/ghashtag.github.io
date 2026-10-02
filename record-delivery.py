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


def merge(history: list[dict], entry: dict) -> list[dict]:
    """Одна запись на исходный коммит: доставка -- это первая публикация коммита.

    Раньше сюда дописывался каждый запуск публикатора. Публикатор срабатывает и
    по крону, и по каждому мержу в trinity, и повторная публикация того же
    коммита записывалась как новая доставка -- с задержкой, которая росла с
    каждым запуском. На 2026-10-02 в окне из 50 записей было 16 коммитов и 34
    повтора (f172d3dc -- девять раз), а повторы вытесняли настоящую историю.
    Повторы старой истории сворачиваются к первой записи коммита."""
    seen: set[str] = set()
    out: list[dict] = []
    for e in [*history, entry]:
        sha = e.get("source_commit") if isinstance(e, dict) else None
        if sha in seen:
            continue
        if sha:
            seen.add(sha)
        out.append(e)
    return out[-50:]


def self_test() -> int:
    a = {"source_commit": "a", "delay_minutes": 1.0}
    b = {"source_commit": "b", "delay_minutes": 2.0}
    late_a = {"source_commit": "a", "delay_minutes": 99.0}
    ok = merge([a], b) == [a, b]
    ok = ok and merge([a, b], late_a) == [a, b]            # повтор -- не доставка
    ok = ok and merge([a, late_a, b], b) == [a, b]          # старые повторы свёрнуты к первой
    ok = ok and len(merge([{"source_commit": str(i)} for i in range(60)], b)) == 50
    print("record-delivery self-test: " + ("ok" if ok else "FAILED"))
    return 0 if ok else 1


def main() -> int:
    if sys.argv[1:] == ["--self-test"]:
        return self_test()
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

    entry = {
        "source_commit": source_commit,
        "source_committed_at": source_time.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "published_at": published_at.isoformat().replace("+00:00", "Z"),
        "delay_minutes": round(delay, 1),
    }
    entries = merge(history, entry)
    if entries[-1] is not entry:
        print(f"delivery: {source_commit[:12]} уже доставлен -- повторная публикация не записывается")
    if entries == history:
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"entries": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if entries[-1] is entry:
        print(f"delivery: {source_commit[:12]} → {entry['delay_minutes']} мин.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
