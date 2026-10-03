#!/usr/bin/env python3
"""Histórico local para deduplicar notícias entre edições. Sem acesso à rede."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING = {"fbclid", "gclid", "mc_cid", "mc_eid"}


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise ValueError("STATE_INVALID")
    return data


def atomic_write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def normalize_url(raw: str) -> str:
    parts = urlsplit(raw.strip())
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError("URL_INVALID")
    query = []
    for k, v in parse_qsl(parts.query, keep_blank_values=True):
        if k.lower().startswith("utm_") or k.lower() in TRACKING:
            continue
        query.append((k, v))
    path = re.sub(r"/+", "/", parts.path or "/")
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, urlencode(query), ""))


def title_key(title: str, source: str) -> str:
    text = re.sub(r"\s+", " ", f"{source} {title}".strip().casefold())
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def find_matches(data: dict, url: str, title: str, source: str) -> list[dict]:
    nurl = normalize_url(url)
    tkey = title_key(title, source)
    return [i for i in data["items"] if i.get("normalized_url") == nurl or i.get("title_key") == tkey]


def cmd_init(args) -> dict:
    if args.state.exists() and not args.force:
        raise ValueError("STATE_ALREADY_EXISTS")
    seed = load(args.seed)
    atomic_write(args.state, seed)
    return {"status": "initialized", "count": len(seed["items"])}


def cmd_check(args) -> dict:
    data = load(args.state)
    matches = find_matches(data, args.url, args.title, args.source_name)
    return {"status": "ok", "duplicate": bool(matches), "matches": matches}


def cmd_record(args) -> dict:
    data = load(args.state)
    matches = find_matches(data, args.url, args.title, args.source_name)
    if matches and not args.new_fact_note.strip():
        raise ValueError("DUPLICATE_REQUIRES_NEW_FACT_NOTE")
    nurl = normalize_url(args.url)
    item = {
        "id": hashlib.sha256(f"{nurl}|{args.edition_at}|{args.title}".encode("utf-8")).hexdigest()[:16],
        "url": args.url,
        "normalized_url": nurl,
        "title": args.title.strip(),
        "source_name": args.source_name.strip(),
        "title_key": title_key(args.title, args.source_name),
        "published_at": args.published_at,
        "edition_at": args.edition_at,
        "new_fact_note": args.new_fact_note.strip(),
        "supersedes": [m.get("id") for m in matches] if matches else [],
    }
    if not item["title"] or not item["source_name"]:
        raise ValueError("TITLE_AND_SOURCE_REQUIRED")
    data["items"].append(item)
    atomic_write(args.state, data)
    return {"status": "recorded", "item": item}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init")
    p.add_argument("--state", type=Path, required=True)
    p.add_argument("--seed", type=Path, required=True)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("check")
    p.add_argument("--state", type=Path, required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--source-name", required=True)
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("record")
    p.add_argument("--state", type=Path, required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--source-name", required=True)
    p.add_argument("--published-at", required=True)
    p.add_argument("--edition-at", required=True)
    p.add_argument("--new-fact-note", default="")
    p.set_defaults(func=cmd_record)

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
