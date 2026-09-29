#!/usr/bin/env python3
"""Lint bloqueante do bundle V4.1."""
from __future__ import annotations
import ast, json, re, sys
from pathlib import Path
from ingest_guard import scan_pii, scan_secret

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT/"SKILL.md"

def links_from(text: str):
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)

def rel_target(base: Path, target: str):
    if target.startswith(("http://","https://","#","mailto:")):
        return None
    return (base/target).resolve()

def check_frontmatter(text, errors):
    if not text.startswith("---\n"):
        errors.append("SKILL.md sem frontmatter inicial.")
        return
    end=text.find("\n---\n",4)
    if end<0:
        errors.append("Frontmatter não fechado.")
        return
    fm=text[4:end]
    if not re.search(r"^name:\s*consultor-simples-nacional-by-rdd\s*$",fm,re.M):
        errors.append("name inválido.")
    m=re.search(r'^description:\s*"([^"]*)"\s*$',fm,re.M)
    if not m or not (0 < len(m.group(1)) <= 1024):
        errors.append("description inválida ou >1024.")
    if not re.search(r"^allowed-tools:\s*Read,\s*Bash\s*$",fm,re.M):
        errors.append("allowed-tools Read, Bash ausente.")
    if re.search(r"^version:",fm,re.M):
        errors.append("Campo version não permitido no frontmatter.")

def check_links(file: Path, errors):
    text=file.read_text(encoding="utf-8")
    for target in links_from(text):
        resolved=rel_target(file.parent,target)
        if resolved is not None and not resolved.exists():
            errors.append(f"Link quebrado em {file.relative_to(ROOT)}: {target}")

def check_all_directly_cited(skill_text, errors):
    links=set()
    for target in links_from(skill_text):
        if target.startswith(("http://","https://","#","mailto:")):
            continue
        p=(ROOT/target).resolve()
        try:
            rel=p.relative_to(ROOT).as_posix()
        except ValueError:
            continue
        links.add(rel)
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if "__pycache__" in p.parts or p.suffix==".pyc" or p==SKILL:
            continue
        rel=p.relative_to(ROOT).as_posix()
        if rel not in links:
            errors.append(f"Arquivo não citado diretamente no SKILL.md: {rel}")

def check_reference_summaries(errors):
    for p in (ROOT/"references").rglob("*.md"):
        lines=p.read_text(encoding="utf-8").splitlines()
        if len(lines)>100 and "Sumário de navegação" not in "\n".join(lines[:25]):
            errors.append(f"Referência >100 linhas sem sumário no topo: {p.relative_to(ROOT)}")

def check_graph(errors):
    p=ROOT/"references"/"graph.yaml"
    try:
        g=json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"graph.yaml inválido: {e}")
        return
    comm={x["id"] for x in g.get("communities",[])}
    nodes={x["id"]:x for x in g.get("nodes",[])}
    for nid,n in nodes.items():
        if n.get("community") not in comm:
            errors.append(f"Nó {nid} em community inexistente.")
    allowed={"substitui","exclui","expande","restringe","nao_aplica","condiciona","precede","regime_proprio","aplica"}
    for e in g.get("edges",[]):
        if e.get("from") not in nodes or e.get("to") not in nodes:
            errors.append(f"Aresta órfã: {e}")
        if e.get("relation") not in allowed:
            errors.append(f"Relação não documentada: {e.get('relation')}")
        if not e.get("nota"):
            errors.append(f"Aresta sem nota: {e}")
    for q in g.get("queries",[]):
        for nid in q.get("navegacao",[]):
            if nid not in nodes:
                errors.append(f"Query aponta nó inexistente: {nid}")

def check_verify(errors):
    p=ROOT/"scripts"/"verify.py"
    if not p.exists():
        errors.append("verify.py ausente.")
        return
    tree=ast.parse(p.read_text(encoding="utf-8"))
    imported=set()
    for n in ast.walk(tree):
        if isinstance(n,ast.Import):
            imported.update(a.name.split(".")[0] for a in n.names)
        if isinstance(n,ast.ImportFrom) and n.module:
            imported.add(n.module.split(".")[0])
    if "engine" in imported or "simples_core" in imported:
        errors.append("verify.py reutiliza engine/simples_core; independência quebrada.")
    como=(ROOT/"references"/"COMO_FUNCIONA.md").read_text(encoding="utf-8")
    como_lower=como.lower()
    if "mesma tabela" not in como_lower or "independ" not in como_lower or "implementa" not in como_lower:
        errors.append("COMO_FUNCIONA não declara honestamente o tipo/limite da independência.")
    if "segunda fonte" not in como_lower:
        errors.append("COMO_FUNCIONA precisa declarar que verify não constitui segunda fonte normativa.")
    ap=(ROOT/"scripts"/"apurar_verificado.py").read_text(encoding="utf-8")
    if "DIVERGENCIA_ENGINE_VERIFY" not in ap or "entrega_bloqueada" not in ap:
        errors.append("Hard-stop engine/verify não identificado.")

def check_goldens(errors):
    p=ROOT/"references"/"goldens"/"official_examples.json"
    data=json.loads(p.read_text(encoding="utf-8"))
    for c in data.get("cases",[]):
        source=c.get("source")
        if (not c.get("conferido_por") or not c.get("fonte_do_gabarito")
            or not isinstance(source,dict) or not source.get("document")
            or not source.get("locator") or not source.get("evidence")):
            errors.append(f"Golden sem fonte/conferência/procedência completa: {c.get('id')}")

def check_evals(errors):
    required=["neg-fora-de-escopo","neg-corte-temporal","neg-dado-faltante","pos-conceitual-2027"]
    for cid in required:
        if not (ROOT/"evals"/cid/"case.json").exists():
            errors.append(f"Eval obrigatório ausente: {cid}")
    # O próprio teste unitário deve conter o cenário falho recusa+dado.
    test=(ROOT/"tests"/"test_evals.py").read_text(encoding="utf-8")
    if "recusa" not in test.lower() or "proib" not in test.lower():
        errors.append("Teste do avaliador não demonstra recusa + dado proibido.")

def check_python3_and_paths(errors):
    scan_ext={".md",".json",".yaml",".yml",".py"}
    abs_pat=re.compile(r'(?<![\w$])/(?:home|Users|mnt|tmp)/[A-Za-z0-9_.\-~/]+')
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix not in scan_ext:
            continue
        text=p.read_text(encoding="utf-8",errors="replace")
        if re.search(r"\bpython\s+(?:scripts/|\"\$SKILL_ROOT)",text):
            errors.append(f"Comando python sem python3: {p.relative_to(ROOT)}")
        if re.search(r"\bpython3\s+(?:\./)?scripts/",text):
            errors.append(f"Comando depende do diretório atual: {p.relative_to(ROOT)}")
        # Regex escapado em JSON/Markdown pode conter barras invertidas legitimamente.
        # Reprovar apenas padrões típicos de path Windows/UNC.
        if p.name != "lint_bundle.py" and re.search(r"(?:[A-Za-z]:\\\\|\\\\\\\\[^\\s]+)", text):
            errors.append(f"Path com barra invertida detectado: {p.relative_to(ROOT)}")
        if abs_pat.search(text):
            errors.append(f"Caminho absoluto de máquina encontrado: {p.relative_to(ROOT)}")


def check_runtime_claims(errors):
    runtime=(ROOT/"references"/"RUNTIME_COMPATIBILITY.md").read_text(encoding="utf-8").lower()
    skill=SKILL.read_text(encoding="utf-8").lower()
    if "não um firewall" not in runtime and "nao um firewall" not in runtime:
        errors.append("RUNTIME_COMPATIBILITY deve declarar que allowed-tools não é firewall.")
    if "bash" not in runtime or "egress" not in runtime:
        errors.append("RUNTIME_COMPATIBILITY deve registrar risco de egress via Bash.")
    misleading=[
        "allowed-tools bloqueia internet",
        "allowed-tools bloqueia a internet",
        "frontmatter bloqueia internet",
        "frontmatter bloqueia a internet",
        "internet normativa é bloqueada por padrão"
    ]
    active=skill+"\n"+runtime
    for phrase in misleading:
        if phrase in active:
            errors.append(f"Alegação enganosa de isolamento de rede encontrada: {phrase}")

def check_release_semantics(errors):
    ap=(ROOT/"scripts"/"apurar_verificado.py").read_text(encoding="utf-8")
    if re.search(r"[\"\']PASS[\"\']", ap):
        errors.append("apurar_verificado contém status genérico PASS.")
    if not (ROOT/"evals"/"pos-conceitual-2027"/"case.json").exists():
        errors.append("Eval positivo conceitual 2027 ausente.")

def check_pii_secrets(errors):
    for p in ROOT.rglob("*"):
        if not p.is_file() or "__pycache__" in p.parts or p.suffix==".pyc":
            continue
        if p.suffix.lower() not in {".md",".txt",".json",".csv",".yaml",".yml",".py"}:
            continue
        text=p.read_text(encoding="utf-8",errors="replace")
        pii=scan_pii(text)
        if pii["found"]:
            errors.append(f"Dado pessoal com DV válido detectado em {p.relative_to(ROOT)}; tipos={','.join(pii['types'])}")
        # Não classificar código dos próprios detectores como segredo.
        if p.name not in {"ingest_guard.py","lint_bundle.py"} and scan_secret(p.name,text):
            errors.append(f"Padrão de segredo detectado em {p.relative_to(ROOT)}")

def check_nested_root(errors):
    if (ROOT/ROOT.name).exists():
        errors.append("Pasta raiz duplicada dentro da própria Skill.")

def main():
    errors=[]
    skill=SKILL.read_text(encoding="utf-8")
    check_frontmatter(skill,errors)
    if len(skill.splitlines())>=500:
        errors.append(f"SKILL.md tem {len(skill.splitlines())} linhas (limite <500).")
    for p in [SKILL, ROOT/"references"/"router.md", ROOT/"references"/"INDEX.md"]:
        check_links(p,errors)
    check_all_directly_cited(skill,errors)
    check_reference_summaries(errors)
    check_graph(errors)
    check_verify(errors)
    check_goldens(errors)
    check_evals(errors)
    check_python3_and_paths(errors)
    check_runtime_claims(errors)
    check_release_semantics(errors)
    check_pii_secrets(errors)
    check_nested_root(errors)
    result={"pass":not errors,"errors":errors}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if not errors else 1

if __name__=="__main__":
    raise SystemExit(main())
