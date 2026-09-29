#!/usr/bin/env python3
"""Consulta offline a tabela CNAE × Anexo.

Busca por:
- CNAE exato;
- termos normalizados;
- radicais simples em português;
- sinônimos controlados.

A tabela é somente triagem; nunca substitui a classificação jurídica da atividade.
"""
from __future__ import annotations
import argparse, csv, json, re, unicodedata
from pathlib import Path

STOPWORDS={"de","da","do","das","dos","e","em","para","por","com","sem","a","o","as","os","um","uma","atividades","atividade"}

SYNONYM_GROUPS = [
    {"programacao","programador","programa","programas","software","sistemas","desenvolvimento"},
    {"contabilidade","contabil","contador","contadores","servicos contabeis"},
    {"advocacia","advogado","advogados","juridico","juridica"},
    {"odontologia","odontologico","dentista","dentaria","dentario"},
    {"medicina","medico","medica","clinica","clinicas"},
    {"informatica","computador","computadores","tecnologia da informacao","ti"},
    {"publicidade","propaganda","marketing"},
]

def norm(s: str) -> str:
    s=unicodedata.normalize("NFKD",str(s))
    s="".join(c for c in s if not unicodedata.combining(c))
    s=re.sub(r"[^a-zA-Z0-9]+"," ",s.lower())
    return re.sub(r"\s+"," ",s).strip()

def stem(token: str) -> str:
    """Stemmer leve e determinístico, suficiente para busca de triagem."""
    t=norm(token).replace(" ","")
    if len(t)<=4:
        return t
    suffixes=[
        "amentos","imentos","adoras","adores","acoes","icoes","mente","idades",
        "amento","imento","adora","ador","acao","icao","idade",
        "icos","icas","ico","ica","istas","ista","arios","arias","ario","aria",
        "coes","cao","s"
    ]
    for suf in suffixes:
        if t.endswith(suf) and len(t)-len(suf)>=4:
            return t[:-len(suf)]
    return t

def tokenize(text: str) -> list[str]:
    return [t for t in norm(text).split() if len(t)>2 and t not in STOPWORDS]

def synonym_terms(query: str) -> set[str]:
    qn=norm(query)
    qtokens=set(tokenize(qn))
    qstems={stem(t) for t in qtokens}
    out=set(qtokens)
    for group in SYNONYM_GROUPS:
        normalized={norm(x) for x in group}
        group_tokens=set()
        for item in normalized:
            group_tokens.update(tokenize(item))
        group_stems={stem(t) for t in group_tokens}
        if qtokens & group_tokens or qstems & group_stems:
            out.update(group_tokens)
    return out

def score_description(query: str, description: str) -> tuple[int, dict]:
    qtokens=tokenize(query)
    expanded=synonym_terms(query)
    dtokens=tokenize(description)
    dset=set(dtokens)
    dstems={stem(t) for t in dtokens}
    exact=sum(1 for t in qtokens if t in dset)
    radical=sum(1 for t in qtokens if stem(t) in dstems and t not in dset)
    synonym=sum(1 for t in expanded if (t in dset or stem(t) in dstems) and t not in qtokens)
    phrase=1 if norm(query) and norm(query) in norm(description) else 0
    score=exact*8+radical*5+synonym*2+phrase*12
    # Desambiguação controlada: em contexto CNAE, "programação" deve alcançar
    # desenvolvimento de programas/software, sem deixar "programadoras" de TV dominar.
    qn=norm(query)
    dn=norm(description)
    software_boost=0
    if "programacao" in qn or "programador" in qn:
        if "desenvolvimento" in dn and ("programas de computador" in dn or "software" in dn):
            software_boost=24
        elif "programadoras" in dn and "televis" in dn:
            software_boost=-4
    score += software_boost
    return score,{"exactos":exact,"radicais":radical,"sinonimos":synonym,"frase":phrase,"contexto_software":software_boost}

def carregar_rows() -> list[dict]:
    path=Path(__file__).resolve().parents[1]/"references"/"CNAEANEXO.csv"
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def consultar_cnae(cnae: str, rows: list[dict]|None=None) -> list[dict]:
    rows=rows or carregar_rows()
    digits=re.sub(r"\D","",str(cnae)).zfill(7)
    return [r for r in rows if r["CNAE"]==digits]

def buscar_texto(texto: str, max_results: int=20, rows: list[dict]|None=None) -> list[dict]:
    rows=rows or carregar_rows()
    scored=[]
    for r in rows:
        score,why=score_description(texto,r["Descrição"])
        if score>0:
            item=dict(r)
            item["_score"]=score
            item["_match"]=why
            scored.append(item)
    scored.sort(key=lambda r:(-r["_score"],r["CNAE"],r["Anexo"]))
    return scored[:max(1,max_results)]

def main() -> int:
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--cnae")
    g.add_argument("--texto")
    ap.add_argument("--max-results",type=int,default=20)
    args=ap.parse_args()
    if args.cnae:
        found=consultar_cnae(args.cnae); query=re.sub(r"\D","",args.cnae).zfill(7)
    else:
        found=buscar_texto(args.texto,args.max_results); query=args.texto
    print(json.dumps({
        "consulta":query,
        "resultados":found,
        "procedencia":"tabela derivada interna CNAE × Anexo",
        "nivel_hierarquico":"D",
        "aviso":"Triagem apenas. Confirme a atividade efetivamente exercida, a norma aplicável e o fator R quando cabível."
    },ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
