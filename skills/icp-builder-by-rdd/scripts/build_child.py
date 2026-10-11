#!/usr/bin/env python3
"""Build a self-contained ICP skill from a reviewed profile. Standard library only."""

import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path
from string import Template

ACTIVITIES = {"digital", "relacionamento", "funil", "eventos", "produtos", "vendas", "objecoes"}
STATUSES = {"observado", "relatado", "hipotese", "desconhecido", "exemplo"}
CONFIDENCE = {"alta", "media", "baixa", "nao_avaliada"}
LABELS = {
    "name": "Nome", "context": "Contexto", "offers": "Ofertas informadas",
    "differentiators": "Diferenciais", "delivery_limits": "Limites de entrega",
    "commercial_context": "Contexto comercial", "label": "Recorte",
    "persona_name": "Nome da persona", "kind": "Tipo", "fit_criteria": "Critérios de aderência",
    "exclusion_criteria": "Fora do recorte", "roles": "Papéis de decisão",
    "terms": "Linguagem registrada", "avoid": "Evitar", "quotes": "Falas com fonte",
    "synthetic_examples": "Propostas de linguagem — simulações",
    "alternatives": "Alternativas", "criteria": "Critérios de escolha",
    "forces": "Forças de mudança", "push": "Incômodo atual", "pull": "Atração pelo resultado",
    "anxiety": "Ansiedade com a mudança", "habit": "Conforto ou hábito atual",
    "objections": "Objeções informadas ou hipotéticas", "statement": "Fala",
    "underlying_concern": "Preocupação", "evidence_ids": "Evidências",
    "evidence_id": "Evidência", "activity": "Atividade", "stage_id": "Fase",
    "opportunity": "Oportunidade proposta", "actions": "Ações", "thinking": "Pensamentos",
    "emotions": "Emoções", "jobs": "Resultados desejados", "functional": "Funcional",
    "emotional": "Emocional", "social": "Social", "trigger": "Gatilho",
    "barriers": "Atritos", "touchpoints": "Pontos de contato", "success": "Sucesso esperado",
    "transitions": "Transições", "to": "Destino", "when": "Condição", "text": "Texto",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def obj(value, fields, path):
    need(isinstance(value, dict), f"{path}: esperado objeto")
    need(set(fields) <= set(value), f"{path}: faltam campos {sorted(set(fields) - set(value))}")


def string(value, path):
    need(isinstance(value, str) and bool(value.strip()), f"{path}: esperado texto não vazio")


def strings(value, path, nonempty=False):
    need(isinstance(value, list), f"{path}: esperada lista")
    need(not nonempty or bool(value), f"{path}: lista não pode ser vazia")
    for item in value:
        string(item, path)


def records(value, path, nonempty=False):
    need(isinstance(value, list), f"{path}: esperada lista")
    need(not nonempty or bool(value), f"{path}: lista não pode ser vazia")
    for item in value:
        need(isinstance(item, dict), f"{path}: esperado registro")


def identifier(value, path):
    string(value, path)
    need(re.fullmatch(r"[A-Za-z0-9_-]+", value) is not None, f"{path}: ID inválido")


def validate(profile):
    obj(profile, ["schema_version", "status", "skill", "company", "icp", "evidence", "voice",
                  "journey", "decisions", "priorities", "research_gaps"], "perfil")
    need(type(profile["schema_version"]) is int and profile["schema_version"] == 1, "Versão não suportada")
    need(profile["status"] in ("draft", "ready"), "status deve ser draft ou ready")
    skill = profile["skill"]
    obj(skill, ["name", "display_name", "short_description"], "skill")
    for key in ("name", "display_name", "short_description"):
        string(skill[key], f"skill.{key}")
        need("\n" not in skill[key] and "\r" not in skill[key], f"skill.{key}: use uma linha")
    need(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill["name"]) is not None and
         len(skill["name"]) <= 64, "Nome inválido: use slug minúsculo até 64 caracteres")
    need(25 <= len(skill["short_description"]) <= 64, "Descrição de interface deve ter 25–64 caracteres")

    for section, text_fields, list_fields in [
        ("company", ["name", "context", "commercial_context"], ["offers", "differentiators", "delivery_limits"]),
        ("icp", ["label", "persona_name", "kind"], ["fit_criteria", "exclusion_criteria", "roles"]),
    ]:
        obj(profile[section], text_fields + list_fields, section)
        for key in text_fields:
            string(profile[section][key], f"{section}.{key}")
        for key in list_fields:
            strings(profile[section][key], f"{section}.{key}")
    need(profile["icp"]["kind"] in ("b2b", "b2c", "hibrido"), "icp.kind inválido")

    records(profile["evidence"], "evidence", nonempty=True)
    evidence = {}
    for record in profile["evidence"]:
        obj(record, ["id", "claim", "status", "source", "confidence"], "evidence")
        identifier(record["id"], "evidence.id")
        need(record["id"] not in evidence, "ID de evidência repetido")
        for key in ("claim", "status", "source", "confidence"):
            string(record[key], f"evidence.{key}")
        need(record["status"] in STATUSES, "Status de evidência inválido")
        need(record["confidence"] in CONFIDENCE, "Confiança inválida")
        evidence[record["id"]] = record

    def refs(ids, path):
        strings(ids, path, nonempty=True)
        need(set(ids) <= set(evidence), f"{path}: evidência inexistente")

    voice = profile["voice"]
    obj(voice, ["terms", "avoid", "quotes", "synthetic_examples"], "voice")
    for key in ("terms", "avoid", "synthetic_examples"):
        strings(voice[key], f"voice.{key}")
    records(voice["quotes"], "voice.quotes")
    for quote in voice["quotes"]:
        obj(quote, ["text", "evidence_id"], "quote")
        string(quote["text"], "quote.text")
        string(quote["evidence_id"], "quote.evidence_id")
        refs([quote["evidence_id"]], "quote.evidence_id")
        need(evidence[quote["evidence_id"]]["status"] in {"observado", "relatado", "exemplo"},
             "Uma fala literal não pode ter origem hipotética/desconhecida")

    stages = profile["journey"]
    records(stages, "journey", nonempty=True)
    stage_ids = set()
    for stage in stages:
        obj(stage, ["id", "label", "context", "actions", "thinking", "emotions", "jobs", "trigger",
                    "barriers", "touchpoints", "success", "transitions", "evidence_ids"], "journey")
        identifier(stage["id"], "journey.id")
        need(stage["id"] not in stage_ids, "ID de fase repetido")
        stage_ids.add(stage["id"])
        for key in ("label", "context", "trigger", "success"):
            string(stage[key], f"journey.{key}")
        for key in ("actions", "thinking", "emotions", "barriers", "touchpoints"):
            strings(stage[key], f"journey.{key}")
        obj(stage["jobs"], ["functional", "emotional", "social"], "journey.jobs")
        for key in ("functional", "emotional", "social"):
            strings(stage["jobs"][key], f"journey.jobs.{key}")
        refs(stage["evidence_ids"], "journey.evidence_ids")
        records(stage["transitions"], "journey.transitions")
    for stage in stages:
        for transition in stage["transitions"]:
            obj(transition, ["to", "when"], "transition")
            string(transition["to"], "transition.to")
            need(transition["to"] in stage_ids, "Transição para fase inexistente")
            string(transition["when"], "transition.when")

    decisions = profile["decisions"]
    obj(decisions, ["alternatives", "criteria", "forces", "objections"], "decisions")
    for key in ("alternatives", "criteria"):
        strings(decisions[key], f"decisions.{key}")
    obj(decisions["forces"], ["push", "pull", "anxiety", "habit"], "decisions.forces")
    for key in ("push", "pull", "anxiety", "habit"):
        strings(decisions["forces"][key], f"decisions.forces.{key}")
    records(decisions["objections"], "decisions.objections")
    for objection in decisions["objections"]:
        obj(objection, ["statement", "underlying_concern", "evidence_ids"], "objection")
        string(objection["statement"], "objection.statement")
        string(objection["underlying_concern"], "objection.underlying_concern")
        refs(objection["evidence_ids"], "objection.evidence_ids")

    records(profile["priorities"], "priorities")
    activities = set()
    for priority in profile["priorities"]:
        obj(priority, ["activity", "stage_id", "opportunity", "evidence_ids"], "priority")
        string(priority["activity"], "priority.activity")
        string(priority["stage_id"], "priority.stage_id")
        need(priority["activity"] in ACTIVITIES, "Atividade inválida")
        need(priority["stage_id"] in stage_ids, "Prioridade refere fase inexistente")
        string(priority["opportunity"], "priority.opportunity")
        refs(priority["evidence_ids"], "priority.evidence_ids")
        activities.add(priority["activity"])
    strings(profile["research_gaps"], "research_gaps")
    if profile["status"] == "ready":
        need(activities == ACTIVITIES, "ready exige oportunidades nas sete atividades")
        need(bool(profile["icp"]["fit_criteria"]) and bool(decisions["alternatives"]),
             "ready exige critérios de aderência e alternativas")
        need(any(item["status"] in {"observado", "relatado"} for item in evidence.values()),
             "ready não pode se basear somente em exemplos, hipóteses ou desconhecimento")


def md_text(value):
    # Keep supplied data from becoming raw HTML or headings in generated documents.
    value = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    for char in ("\\", "`", "*", "_", "[", "]", "#", "|", "$"):
        value = value.replace(char, "\\" + char)
    return " ".join(value.splitlines())


def render(value, depth=0):
    lines = []
    indent = "  " * depth
    if isinstance(value, dict):
        for key, item in value.items():
            label = md_text(LABELS.get(key, key))
            if isinstance(item, (dict, list)):
                lines.append(f"{indent}- **{label}:**")
                lines.extend(render(item, depth + 1))
            else:
                lines.append(f"{indent}- **{label}:** {md_text(item)}")
    elif isinstance(value, list):
        if not value:
            lines.append(f"{indent}- Sem registro; não inferir.")
        for item in value:
            if isinstance(item, dict):
                lines.append(f"{indent}- Registro:")
                lines.extend(render(item, depth + 1))
            else:
                lines.append(f"{indent}- {md_text(item)}")
    return lines


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def build(profile, output_root, source_root=None):
    validate(profile)
    source_root = Path(source_root or Path(__file__).resolve().parents[1])
    output_root = Path(output_root).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    destination = output_root / profile["skill"]["name"]
    need(not destination.exists(), f"Destino já existe; versão preservada: {destination}")
    template = Template((source_root / "assets/skill-filha.md").read_text(encoding="utf-8"))
    # Names enter YAML through JSON quoting; no supplied value is interpreted as a template.
    description = (
        f"Personifica o ICP {profile['icp']['label']} de {profile['company']['name']} e usa sua jornada "
        "para orientar marketing, relacionamento, funil, eventos, produtos, vendas e objeções."
    ).replace("<", "(").replace(">", ")")
    need(len(description) <= 1024, "Descrição gerada excede limite; reduza nome/recorte")
    metadata = {"name": profile["skill"]["name"], "status": profile["status"],
                "description_yaml": json.dumps(description, ensure_ascii=False)}
    for key, value in [("display_name", profile["skill"]["display_name"]),
                       ("icp_label", profile["icp"]["label"]), ("company_name", profile["company"]["name"]),
                       ("persona_name", profile["icp"]["persona_name"])]:
        metadata[key] = md_text(value)
    with tempfile.TemporaryDirectory(prefix=".icp-build-", dir=output_root) as temporary:
        folder = Path(temporary) / profile["skill"]["name"]
        write(folder / "SKILL.md", template.substitute(metadata))
        interface = {
            "display_name": profile["skill"]["display_name"],
            "short_description": profile["skill"]["short_description"],
            "default_prompt": f"Use ${profile['skill']['name']} para orientar esta decisão conforme o ICP e sua fase da jornada.",
        }
        write(folder / "agents/openai.yaml", "interface:\n" + "\n".join(
            f"  {key}: {json.dumps(value, ensure_ascii=False)}" for key, value in interface.items()))
        ref = folder / "references"
        warning = (f"Estado: **{profile['status']}**. Evidências e hipóteses têm naturezas distintas. "
                   "Exemplos e simulações não são pesquisa validada.\n")
        sections = [("Empresa", profile["company"]), ("ICP e atores", profile["icp"]),
                    ("Voz", profile["voice"]), ("Decisões", profile["decisions"]),
                    ("Oportunidades por atividade", profile["priorities"]),
                    ("Lacunas prioritárias", profile["research_gaps"])]
        parts = ["# Perfil da empresa e do ICP", warning]
        for title, content in sections:
            parts.append(f"## {title}\n\n" + "\n".join(render(content)))
        write(ref / "perfil.md", "\n\n".join(parts))
        parts = ["# Jornada do ICP", warning,
                 "Fases pertencem ao contexto descrito. Transições podem incluir pausas, retornos e alternativas."]
        for stage in profile["journey"]:
            parts.append(f"## {md_text(stage['id'])} — {md_text(stage['label'])}\n\n" +
                         "\n".join(render({key: value for key, value in stage.items() if key not in {"id", "label"}})))
        write(ref / "jornada.md", "\n\n".join(parts))
        parts = ["# Registro de evidências", warning,
                 "Confiança qualifica a sustentação do registro; não muda seu status. "
                 "Fontes metodológicas não validam características deste ICP.",
                 "| ID | Afirmação | Status | Fonte | Confiança |\n| --- | --- | --- | --- | --- |"]
        for evidence in profile["evidence"]:
            parts.append("| " + " | ".join(md_text(evidence[key]) for key in
                         ("id", "claim", "status", "source", "confidence")) + " |")
        write(ref / "evidencias.md", "\n\n".join(parts[:3]) + "\n\n" + "\n".join(parts[3:]))
        write(ref / "perfil.json", json.dumps(profile, ensure_ascii=False, indent=2))
        shutil.copytree(source_root / "references/metodos", ref / "metodos")
        folder.rename(destination)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        profile = json.loads(args.profile.read_text(encoding="utf-8"))
        destination = build(profile, args.output_root)
    except (ValueError, TypeError, KeyError, OSError) as error:
        parser.exit(1, f"Não foi possível gerar a filha: {error}\n")
    print(f"Skill filha criada: {destination}")


if __name__ == "__main__":
    main()
