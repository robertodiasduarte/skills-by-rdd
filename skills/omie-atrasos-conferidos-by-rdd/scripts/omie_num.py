#!/usr/bin/env python3
"""Totalizacao somente-leitura na API do Omie, com conferencia.

Derivado de consulta-omie-somente-leitura 1.0.0 (scripts/omie_consulta.py).
Diferencas em references/omie/FONTES_OMIE.md (ancora omie_num) na skill geradora.

Uso:
  omie_num.py totalizar --servico S --metodo M --param JSON --soma CAMPO [--agrupar CAMPO]

Garantias por codigo:
  - so chama metodo listado como leitura do servico em catalogo_leitura.json (ao lado
    deste script) E aprovado pela regra de nome de leitura (dupla barreira, as duas);
  - teto de 5 paginas e 100 registros por pagina;
  - so entrega total quando: a API informou a contagem, os registros lidos batem com
    ela, nada foi truncado, todo valor do campo somado e numerico e a soma direta bate
    com a soma por particao (grupo ou pagina). Qualquer falha: status divergente, sem total;
  - credenciais lidas do ambiente ou do .env, nunca impressas.

Saida (JSON no stdout): 0 ok · 2 divergente (sem total) · 3 configuracao ·
4 erro da API/rede · 5 bloqueado por politica · 64 uso incorreto.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

CATALOG_PATH = Path(__file__).resolve().parent / "catalogo_leitura.json"
DEFAULT_BASE = "https://app.omie.com.br/api/v1/"
HARD_MAX_PAGES = 5
MAX_PER_PAGE = 100
READ_PREFIX = ("Listar", "Consultar", "Consulta", "Pesquisar", "Obter", "Status",
               "GetUrl", "Verificar", "Cupons")
READ_EXACT = {"PosicaoEstoque", "MovimentoEstoque", "CalendarioTarefas"}
NEVER = {"ObterProximoLote", "GerarBoleto", "GerarPix", "GerarQrCodePix", "ProrrogarBoleto",
         "TotalizarPedido", "SimularImpostos", "FecharCaixa"}
PAGE_KEYS = [("pagina", "registros_por_pagina", "total_de_paginas", "total_de_registros"),
             ("nPagina", "nRegPorPagina", "nTotPaginas", "nTotRegistros")]
RETRY_WAITS = (2, 4, 8)
MAX_CONSECUTIVE_ERRORS = 5
NOTA = "Soma aritmetica dos valores retornados pela Omie; nao e analise contabil, tributaria ou financeira."


class PolicyError(Exception):
    """Pedido fora da politica somente-leitura."""


class ConfigError(Exception):
    """Credenciais ou configuracao ausentes."""


class ApiError(Exception):
    """Falha da API ou da rede."""


# ---------------------------------------------------------------- politica
def load_catalog(path: Path = CATALOG_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))["servicos"]


def normalize_service(servico: str) -> str:
    s = re.sub(r"^https?://[^/]+/api/v1/", "", servico.strip()).strip("/")
    if not re.fullmatch(r"[a-z]+/[a-z0-9-]+", s):
        raise PolicyError(f"Servico invalido: {servico!r}. Use modulo/servico, ex.: financas/pesquisartitulos")
    return s


def name_rule_allows(metodo: str) -> bool:
    if metodo in NEVER:
        return False
    return metodo in READ_EXACT or metodo.startswith(READ_PREFIX)


def check_allowed(catalog: dict, servico: str, metodo: str) -> str:
    s = normalize_service(servico)
    if s not in catalog:
        raise PolicyError(f"Servico {s}/ nao consta no catalogo de leitura.")
    entry = catalog[s]
    if metodo in entry.get("bloqueados", {}):
        raise PolicyError(f"Metodo {metodo} bloqueado ({entry['bloqueados'][metodo]}). Este script so le.")
    if metodo not in entry.get("leitura", []):
        raise PolicyError(f"Metodo {metodo} nao existe como leitura em {s}/.")
    if not name_rule_allows(metodo):
        raise PolicyError(f"Metodo {metodo} reprovado pela regra de nome de leitura.")
    return s


# ---------------------------------------------------------------- credenciais
def parse_env_file(path: Path) -> dict:
    out = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[7:]
        k, v = line.split("=", 1)
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
            v = v[1:-1]
        out[k.strip()] = v
    return out


def find_env_file(start: Path | None = None) -> Path | None:
    explicit = os.environ.get("OMIE_ENV_FILE")
    if explicit:
        p = Path(explicit).expanduser()
        return p if p.is_file() else None
    cur = (start or Path.cwd()).resolve()
    for d in [cur, *cur.parents]:
        if (d / ".env").is_file():
            return d / ".env"
    return None


def load_credentials() -> tuple[str, str]:
    key, secret = os.environ.get("OMIE_APP_KEY"), os.environ.get("OMIE_APP_SECRET")
    if not (key and secret):
        env = find_env_file()
        if env:
            vals = parse_env_file(env)
            key, secret = key or vals.get("OMIE_APP_KEY"), secret or vals.get("OMIE_APP_SECRET")
    if not (key and secret):
        raise ConfigError("Credenciais ausentes: defina OMIE_APP_KEY e OMIE_APP_SECRET no .env do projeto "
                          "(ou aponte OMIE_ENV_FILE para o arquivo).")
    return key, secret


def redact(text: str, secrets: tuple[str, ...]) -> str:
    for s in secrets:
        if s:
            text = text.replace(s, "***")
    return text


# ---------------------------------------------------------------- transporte
def base_url() -> str:
    url = os.environ.get("OMIE_BASE_URL", DEFAULT_BASE)
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" and parsed.hostname not in ("127.0.0.1", "localhost"):
        raise ConfigError("OMIE_BASE_URL precisa ser https (http so para localhost em testes).")
    return url if url.endswith("/") else url + "/"


class Client:
    def __init__(self, key: str, secret: str, pause: float = 0.3, waits=RETRY_WAITS):
        self.key, self.secret, self.pause, self.waits = key, secret, pause, waits
        self.calls = 0
        self.consecutive_errors = 0

    def call(self, servico: str, metodo: str, param: dict) -> dict:
        body = json.dumps({"call": metodo, "app_key": self.key, "app_secret": self.secret,
                           "param": [param]}).encode("utf-8")
        url = base_url() + servico + "/"
        last = None
        for attempt in range(len(self.waits) + 1):
            if self.consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                raise ApiError("Interrompido apos erros consecutivos para evitar o bloqueio de 30 minutos da Omie.")
            req = urllib.request.Request(url, data=body, method="POST",
                                         headers={"Content-Type": "application/json"})
            try:
                self.calls += 1
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                if isinstance(data, dict) and "faultstring" in data:
                    raise ApiError(str(data.get("faultstring")))
                self.consecutive_errors = 0
                time.sleep(self.pause)
                return data
            except urllib.error.HTTPError as e:
                self.consecutive_errors += 1
                fault = None
                try:
                    payload = json.loads(e.read().decode("utf-8"))
                    fault = payload.get("faultstring") if isinstance(payload, dict) else None
                    msg = str(fault or payload)
                except Exception:
                    msg = f"HTTP {e.code}"
                last = f"HTTP {e.code}: {msg}"
                if e.code == 425:
                    raise ApiError("Omie bloqueou temporariamente (HTTP 425, ~30 min). Aguarde antes de tentar de novo.")
                low = msg.lower()
                retriable = ("too many" in low or "proto_byebye" in low or e.code in (429, 502, 503, 504)
                             or (e.code == 500 and not fault))
                if not retriable or attempt == len(self.waits):
                    break
                time.sleep(self.waits[attempt])
            except ApiError as e:
                self.consecutive_errors += 1
                last = str(e)
                break
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                self.consecutive_errors += 1
                last = f"Falha de rede: {getattr(e, 'reason', e)}"
                if attempt == len(self.waits):
                    break
                time.sleep(self.waits[attempt])
        raise ApiError(redact(last or "erro desconhecido", (self.key, self.secret)))


# ---------------------------------------------------------------- respostas
def find_records(resp: dict) -> tuple[str | None, list]:
    best_key, best = None, []
    if not isinstance(resp, dict):
        return None, []
    for k, v in resp.items():
        if isinstance(v, list) and v and all(isinstance(x, dict) for x in v) and len(v) > len(best):
            best_key, best = k, v
    return best_key, best


def page_keys_for(param: dict, resp: dict | None = None):
    for keys in PAGE_KEYS:
        if keys[0] in param or (resp and keys[2] in resp):
            return keys
    return None


def get_path(rec, path: str):
    cur = rec
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def to_decimal(v) -> Decimal | None:
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        d = Decimal(str(v))
        return d if d.is_finite() else None
    if isinstance(v, str):
        s = v.strip()
        if re.fullmatch(r"-?\d{1,3}(\.\d{3})*,\d+", s):
            s = s.replace(".", "").replace(",", ".")
        try:
            d = Decimal(s)
        except InvalidOperation:
            return None
        return d if d.is_finite() else None
    return None


# ---------------------------------------------------------------- totalizar
def somar_particoes(particoes: list) -> Decimal:
    """Segundo caminho da soma: subtotais por grupo ou por pagina."""
    return sum(particoes, Decimal("0"))


def ler_paginas(client: Client, servico: str, metodo: str, param: dict):
    param = dict(param)
    keys = page_keys_for(param)
    if keys and keys[1] in param:
        param[keys[1]] = min(int(param[keys[1]]), MAX_PER_PAGE)
    first = client.call(servico, metodo, param)
    keys = keys or page_keys_for(param, first)
    rec_key, records = find_records(first)
    paginas = [list(records)]
    total_paginas = first.get(keys[2]) if keys else None
    informados = first.get(keys[3]) if keys else None
    truncado = False
    if keys and isinstance(total_paginas, int) and total_paginas > 1:
        start = int(param.get(keys[0], 1))
        last_page = min(total_paginas, start + HARD_MAX_PAGES - 1)
        for p in range(start + 1, last_page + 1):
            param[keys[0]] = p
            _, more = find_records(client.call(servico, metodo, param))
            paginas.append(list(more))
        truncado = last_page < total_paginas
    return paginas, informados, truncado, rec_key, param, keys


def totalizar(client: Client, catalog: dict, servico: str, metodo: str, param: dict,
              soma: str, agrupar: str | None = None) -> tuple[int, dict]:
    s = check_allowed(catalog, servico, metodo)
    paginas, informados, truncado, rec_key, param, keys = ler_paginas(client, s, metodo, param)
    registros = [r for pg in paginas for r in pg]
    mem = {
        "endpoint": base_url() + s + "/",
        "metodo": metodo,
        "param": {k: v for k, v in param.items() if not (keys and k == keys[0])},
        "paginas_lidas": len(paginas),
        "campo_registros": rec_key,
        "campo_somado": soma,
        "chamadas_api": client.calls,
        "consultado_em": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
    }
    conf = {"lidos": len(registros), "informados": informados,
            "particao": "grupo" if agrupar else "pagina"}

    def divergente(motivo: str, **extra) -> tuple[int, dict]:
        # Sem nenhum agregado do campo somado: so contagens, motivo, posicoes e memoria.
        base = {"lidos": conf["lidos"], "informados": conf["informados"]}
        return 2, {"status": "divergente", "motivo": motivo, "conferencia": base, "memoria": mem, **extra}

    nao_numericos = []
    valores = []
    for i, r in enumerate(registros):
        v = to_decimal(get_path(r, soma))
        if v is None:
            nao_numericos.append(i)
        valores.append(v)
    if nao_numericos:
        return divergente("valor_nao_numerico", registros=nao_numericos[:20],
                          quantidade=len(nao_numericos))
    if not isinstance(informados, int) or isinstance(informados, bool):
        return divergente("sem_contagem_informada")
    if truncado:
        return divergente("truncado")
    if len(registros) != informados:
        return divergente("contagem")

    soma_direta = sum(valores, Decimal("0"))
    grupos: dict[str, Decimal] = {}
    if agrupar:
        for r, v in zip(registros, valores):
            g = get_path(r, agrupar)
            chave = "(vazio)" if g in (None, "") else str(g)
            grupos[chave] = grupos.get(chave, Decimal("0")) + v
        particoes = list(grupos.values())
    else:
        particoes, i = [], 0
        for pg in paginas:
            particoes.append(sum(valores[i:i + len(pg)], Decimal("0")))
            i += len(pg)
    soma_particao = somar_particoes(particoes)
    if soma_direta != soma_particao:
        return divergente("consistencia")
    conf["soma_direta"] = str(soma_direta)
    conf["soma_por_particao"] = str(soma_particao)
    out = {"status": "ok", "total": str(soma_direta), "conferencia": conf, "memoria": mem, "nota": NOTA}
    if agrupar:
        out["grupos"] = {k: str(v) for k, v in sorted(grupos.items())}
    return 0, out


# ---------------------------------------------------------------- cli
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Totalizacao somente-leitura na API do Omie, com conferencia.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("totalizar")
    t.add_argument("--servico", required=True)
    t.add_argument("--metodo", required=True)
    t.add_argument("--param", required=True, help="JSON do param (objeto)")
    t.add_argument("--soma", required=True)
    t.add_argument("--agrupar")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 64
    secrets: tuple[str, ...] = ()
    try:
        param = json.loads(args.param)
        if not isinstance(param, dict):
            raise ValueError
    except ValueError:
        print(json.dumps({"erro_uso": "--param precisa ser um objeto JSON"}, ensure_ascii=False))
        return 64
    try:
        catalog = load_catalog()
        check_allowed(catalog, args.servico, args.metodo)
        key, secret = load_credentials()
        secrets = (key, secret)
        rc, out = totalizar(Client(key, secret), catalog, args.servico, args.metodo, param,
                            args.soma, args.agrupar)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return rc
    except PolicyError as e:
        print(json.dumps({"bloqueado": str(e)}, ensure_ascii=False))
        return 5
    except ConfigError as e:
        print(json.dumps({"erro_configuracao": str(e)}, ensure_ascii=False))
        return 3
    except ApiError as e:
        print(json.dumps({"erro_api": redact(str(e), secrets)}, ensure_ascii=False))
        return 4


if __name__ == "__main__":
    sys.exit(main())
