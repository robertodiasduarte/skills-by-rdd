#!/usr/bin/env python3
"""Barreira determinística para fatos estruturados.

Aceita apenas escalares JSON e coleções com limites explícitos.
Conta bytes UTF-8. Não interpreta instruções contidas no texto.
"""
from __future__ import annotations
import json, unicodedata

MAX_DEPTH = 6
MAX_LIST_ITEMS = 64
MAX_DICT_KEYS = 32
MAX_STRING_BYTES = 4096
MAX_TOTAL_BYTES = 32768

def _norm_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", str(value))
    text = "".join(ch for ch in text if ch in "\n\t" or ord(ch) >= 32)
    data = text.encode("utf-8")
    if len(data) > MAX_STRING_BYTES:
        data = data[:MAX_STRING_BYTES]
        while True:
            try:
                text = data.decode("utf-8")
                break
            except UnicodeDecodeError:
                data = data[:-1]
    return text

def _rebuild(obj, depth=0):
    if depth > MAX_DEPTH:
        raise ValueError("Estrutura excede profundidade máxima.")
    if obj is None or isinstance(obj, (bool, int, float)):
        return obj
    if isinstance(obj, str):
        return _norm_text(obj)
    if isinstance(obj, list):
        if len(obj) > MAX_LIST_ITEMS:
            raise ValueError("Lista excede cota de itens.")
        return [_rebuild(x, depth + 1) for x in obj]
    if isinstance(obj, dict):
        if len(obj) > MAX_DICT_KEYS:
            raise ValueError("Objeto excede cota de chaves.")
        out = {}
        for k, v in obj.items():
            key = _norm_text(str(k))
            out[key] = _rebuild(v, depth + 1)
        return out
    raise ValueError(f"Tipo não permitido na barreira: {type(obj).__name__}")

def barrier(obj):
    rebuilt = _rebuild(obj)
    payload = json.dumps(rebuilt, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(payload) > MAX_TOTAL_BYTES:
        raise ValueError("Estrutura excede cota total de bytes UTF-8.")
    # Segunda reconstrução após serialização: consumo repete a barreira.
    return _rebuild(json.loads(payload.decode("utf-8")))

def fact_record(**kwargs):
    return barrier(kwargs)
