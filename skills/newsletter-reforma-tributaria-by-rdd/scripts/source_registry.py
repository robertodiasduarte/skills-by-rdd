#!/usr/bin/env python3
"""Cadastro local de fontes confiáveis; não acessa rede nem autentica aprovações."""
from __future__ import annotations
import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ALLOWED_CATEGORIES = {"official_primary", "institutional", "private_specialized", "private_general", "specialist"}


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        raise ValueError("STATE_INVALID")
    return data


def normalize_url(raw: str) -> str:
    parts = urlsplit(raw.strip())
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError("URL_INVALID")
    path = parts.path or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path.rstrip("/") or "/", "", ""))


def atomic_write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(payload)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def cmd_init(args) -> dict:
    if args.state.exists() and not args.force:
        raise ValueError("STATE_ALREADY_EXISTS")
    seed = load(args.seed)
    atomic_write(args.state, seed)
    return {"status": "initialized", "count": len(seed["sources"])}


def cmd_list(args) -> dict:
    data = load(args.state)
    rows = [s for s in data["sources"] if args.all or s.get("active", True)]
    return {"status": "ok", "sources": rows}


def cmd_add(args) -> dict:
    if not args.confirmed or not args.approval_note.strip():
        raise ValueError("USER_CONFIRMATION_REQUIRED")
    if args.category not in ALLOWED_CATEGORIES:
        raise ValueError("CATEGORY_INVALID")
    data = load(args.state)
    url = normalize_url(args.url)
    if any(normalize_url(s["url"]) == url for s in data["sources"]):
        raise ValueError("SOURCE_ALREADY_EXISTS")
    source = {
        "id": args.id or f"user-{len(data['sources'])+1}",
        "name": args.name.strip(),
        "url": url,
        "category": args.category,
        "active": True,
        "approved": True,
        "approved_at": args.approved_at or datetime.now(timezone.utc).isoformat(),
        "approval_note": args.approval_note.strip(),
        "notes": args.notes.strip(),
    }
    if not source["name"]:
        raise ValueError("NAME_REQUIRED")
    data["sources"].append(source)
    data["updated_at"] = source["approved_at"]
    atomic_write(args.state, data)
    return {"status": "added", "source": source}


def cmd_disable(args) -> dict:
    if not args.confirmed:
        raise ValueError("USER_CONFIRMATION_REQUIRED")
    data = load(args.state)
    matches = [s for s in data["sources"] if s.get("id") == args.id]
    if len(matches) != 1:
        raise ValueError("SOURCE_NOT_FOUND")
    matches[0]["active"] = False
    matches[0]["disabled_note"] = args.note.strip()
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    atomic_write(args.state, data)
    return {"status": "disabled", "id": args.id}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init")
    p.add_argument("--state", type=Path, required=True)
    p.add_argument("--seed", type=Path, required=True)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("list")
    p.add_argument("--state", type=Path, required=True)
    p.add_argument("--all", action="store_true")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("add")
    p.add_argument("--state", type=Path, required=True)
    p.add_argument("--id")
    p.add_argument("--name", required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--category", required=True)
    p.add_argument("--confirmed", action="store_true")
    p.add_argument("--approval-note", required=True)
    p.add_argument("--approved-at")
    p.add_argument("--notes", default="")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("disable")
    p.add_argument("--state", type=Path, required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--confirmed", action="store_true")
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_disable)

    args = parser.parse_args()
    try:
        result = args.func(args)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
