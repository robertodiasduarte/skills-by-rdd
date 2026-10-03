#!/usr/bin/env python3
"""Calcula janela diária ou semanal da newsletter. Python 3.10+, biblioteca padrão."""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def parse_now(raw: str | None, tz: ZoneInfo) -> datetime:
    if raw is None:
        return datetime.now(tz)
    value = datetime.fromisoformat(raw)
    if value.tzinfo is None:
        value = value.replace(tzinfo=tz)
    return value.astimezone(tz)


def calculate(cadence: str, now: datetime) -> tuple[datetime, datetime]:
    days = {"daily": 1, "weekly": 7}[cadence]
    return now - timedelta(days=days), now


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cadence", choices=["daily", "weekly"], required=True)
    parser.add_argument("--timezone", default="America/Sao_Paulo")
    parser.add_argument("--now")
    args = parser.parse_args()
    tz = ZoneInfo(args.timezone)
    end = parse_now(args.now, tz)
    start, end = calculate(args.cadence, end)
    print(json.dumps({
        "cadence": args.cadence,
        "timezone": args.timezone,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "publication_date_rule": "start <= published_at <= end"
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
