#!/usr/bin/env python3
"""Ingestão local fail-closed para material textual adicional.

Ordem: extensão/tamanho -> segredo -> dado pessoal -> cota -> extração -> barreira -> serialização -> barreira.
Não acessa rede, não instala pacotes e não ecoa dado sensível detectado.
"""
from __future__ import annotations
import argparse, csv, io, json, re, sys, unicodedata
from pathlib import Path
from safe_facts import barrier

ALLOWED_EXTS = {".md", ".txt", ".json", ".csv", ".yaml", ".yml"}
MAX_FILE_BYTES = 2_000_000
MAX_FACTS = 400
MAX_FACT_TEXT_BYTES = 3000

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
    re.compile(r"\b(?:api[_-]?key|access[_-]?token|secret[_-]?key|password)\s*[:=]\s*\S+", re.I),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
]
SECRET_NAME = re.compile(r"(?:secret|token|password|private[_-]?key|credential)", re.I)

DIGITISH = re.compile(r"(?<!\d)(?:\d[\s.\-\/]*){11,14}(?!\d)")

def digits(s: str) -> str:
    return re.sub(r"\D", "", s)

def cpf_valid(d: str) -> bool:
    if len(d) != 11 or len(set(d)) == 1:
        return False
    nums = list(map(int, d))
    s1 = sum(nums[i] * (10 - i) for i in range(9))
    c1 = 0 if (s1 * 10) % 11 == 10 else (s1 * 10) % 11
    if c1 != nums[9]:
        return False
    s2 = sum(nums[i] * (11 - i) for i in range(10))
    c2 = 0 if (s2 * 10) % 11 == 10 else (s2 * 10) % 11
    return c2 == nums[10]

def cnpj_valid(d: str) -> bool:
    if len(d) != 14 or len(set(d)) == 1:
        return False
    nums = list(map(int, d))
    w1 = [5,4,3,2,9,8,7,6,5,4,3,2]
    w2 = [6,5,4,3,2,9,8,7,6,5,4,3,2]
    def dv(vals, weights):
        rem = sum(v*w for v,w in zip(vals,weights)) % 11
        return 0 if rem < 2 else 11 - rem
    return dv(nums[:12], w1) == nums[12] and dv(nums[:13], w2) == nums[13]

def scan_pii(text: str) -> dict:
    kinds = set()
    for m in DIGITISH.finditer(text):
        d = digits(m.group(0))
        if len(d) == 11 and cpf_valid(d):
            kinds.add("CPF")
        if len(d) == 14 and cnpj_valid(d):
            kinds.add("CNPJ")
    return {"found": bool(kinds), "types": sorted(kinds)}

def scan_secret(name: str, text: str) -> bool:
    if SECRET_NAME.search(name):
        return True
    return any(p.search(text) for p in SECRET_PATTERNS)

def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = "".join(ch for ch in text if ch in "\n\t" or ord(ch) >= 32)
    return text.replace("\r\n", "\n").replace("\r", "\n")

def extract_facts(path: Path, text: str) -> list[dict]:
    facts = []
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        payload = json.dumps(data, ensure_ascii=False, sort_keys=True)
        facts.append({"source": path.name, "kind": "json", "text": payload[:12000]})
    elif path.suffix.lower() == ".csv":
        reader = csv.reader(io.StringIO(text))
        for idx, row in enumerate(reader, 1):
            if idx > MAX_FACTS:
                break
            facts.append({"source": path.name, "line": idx, "kind": "csv_row", "fields": row[:32]})
    else:
        for idx, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            facts.append({"source": path.name, "line": idx, "kind": "text_line", "text": line})
            if len(facts) >= MAX_FACTS:
                break
    return facts

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    args = ap.parse_args()
    path = Path(args.path)
    try:
        if path.suffix.lower() not in ALLOWED_EXTS:
            raise ValueError("Extensão não aceita para ingestão textual.")
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            raise ValueError("Arquivo excede limite de tamanho.")
        raw = path.read_text(encoding="utf-8-sig", errors="strict")
        text = normalize_text(raw)
        if scan_secret(path.name, text):
            raise ValueError("Material recusado: padrão de segredo detectado.")
        pii = scan_pii(text)
        if pii["found"]:
            raise ValueError("Material recusado: dado pessoal detectado do tipo " + ", ".join(pii["types"]) + ".")
        facts = extract_facts(path, text)
        if len(facts) > MAX_FACTS:
            raise ValueError("Quantidade de fatos excede cota.")
        first = barrier({"source": path.name, "facts": facts})
        serialized = json.dumps(first, ensure_ascii=False)
        second = barrier(json.loads(serialized))
        print(json.dumps({"status": "OK", "bytes": size, "fact_count": len(facts), "payload": second}, ensure_ascii=False))
        return 0
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as e:
        print(json.dumps({"status": "RECUSADO", "erro": str(e)}, ensure_ascii=False))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
