#!/usr/bin/env python3
"""Núcleo determinístico do Simples Nacional, PA 2018-2026.

- Sem internet e sem dependências externas.
- Tabelas carregadas por competência anual de references/tabelas/<ano>/anexos.json.
- Segregação de receita com ISS retido para Anexos III, IV e V.
- Parsing de números em formatos brasileiro e internacional.

Fontes principais:
- Lei Complementar nº 123/2006 — Anexos I a V.
- Resolução CGSN nº 140/2018, art. 25, § 9º, II, e art. 27, VII.
"""
from __future__ import annotations
import math, re
from tables_loader import carregar_tabelas

LIMITE_FATOR_R = 0.28

def parse_numero(valor) -> float:
    """Aceita 1234.56, 1234,56, 1.234,56, R$ 1.234,56 e espaços."""
    if isinstance(valor, (int, float)):
        numero = float(valor)
    else:
        s = str(valor).strip()
        if not s:
            raise ValueError("Valor numérico vazio.")
        s = re.sub(r"(?i)\bR\$\s*", "", s).replace("\u00a0", "").replace(" ", "")
        s = re.sub(r"[^0-9,.\-+]", "", s)
        if not s or s in {"-", "+", ".", ","}:
            raise ValueError(f"Valor numérico inválido: {valor!r}")
        # Ambos separadores: o último é o decimal; os anteriores são milhares.
        if "," in s and "." in s:
            if s.rfind(",") > s.rfind("."):
                s = s.replace(".", "").replace(",", ".")
            else:
                s = s.replace(",", "")
        elif "," in s:
            # vírgula é decimal
            if s.count(",") > 1:
                raise ValueError(f"Valor ambíguo com múltiplas vírgulas: {valor!r}")
            s = s.replace(",", ".")
        elif s.count(".") > 1:
            # pontos múltiplos sem vírgula: tratar como milhar quando grupos finais têm 3 dígitos
            parts = s.split(".")
            if all(len(p) == 3 for p in parts[1:]):
                s = "".join(parts)
            else:
                raise ValueError(f"Valor ambíguo com múltiplos pontos: {valor!r}")
        try:
            numero = float(s)
        except ValueError as e:
            raise ValueError(f"Valor numérico inválido: {valor!r}") from e
    if not math.isfinite(numero):
        raise ValueError("Valor deve ser finito.")
    return numero

def parse_lista_numeros(texto: str) -> list[float]:
    """Lista monetária robusta.

    Preferir ';' para separar itens quando houver vírgula decimal:
    "10.000,00; 12.500,50; 8.000,00".

    Mantém compatibilidade com listas legadas de inteiros separadas por vírgula:
    "10000,12000,8000".
    """
    s = str(texto).strip()
    if not s:
        return []
    s = s.strip("[]()")
    if ";" in s:
        partes = [p.strip() for p in s.split(";") if p.strip()]
    elif "|" in s:
        partes = [p.strip() for p in s.split("|") if p.strip()]
    elif "\n" in s:
        partes = [p.strip() for p in s.splitlines() if p.strip()]
    else:
        # Um único valor brasileiro com vírgula decimal deve permanecer inteiro.
        if s.count(",") == 1 and ("." in s or len(s.split(",")[1]) in (1,2)):
            partes = [s]
        elif "," in s:
            partes = [p.strip() for p in s.split(",") if p.strip()]
        else:
            partes = [s]
    return [parse_numero(p) for p in partes]

def validar_valor(nome: str, valor: float, permitir_zero: bool = True) -> None:
    v = parse_numero(valor)
    if v < 0 or (not permitir_zero and v == 0):
        raise ValueError(f"{nome} deve ser um número {'positivo' if not permitir_zero else 'não negativo'}.")

def validar_ano(ano: int) -> None:
    carregar_tabelas(int(ano))  # fail-closed por disponibilidade de tabela

def identificar_faixa(rbt12: float, ano: int) -> int:
    rbt12 = parse_numero(rbt12)
    validar_valor("RBT12", rbt12, permitir_zero=False)
    limites = carregar_tabelas(ano)["limites_rbt12"]
    for idx, limite in enumerate(limites, 1):
        if rbt12 <= float(limite):
            return idx
    raise ValueError("RBT12 excede R$ 4.800.000,00; não calcular pelas faixas ordinárias deste motor.")

def aliquota_efetiva(anexo: str, rbt12: float, ano: int) -> tuple[int, float, float, float]:
    data = carregar_tabelas(int(ano))
    anexo = anexo.upper()
    if anexo not in data["anexos"]:
        raise ValueError("Anexo deve ser I, II, III, IV ou V.")
    rbt12 = parse_numero(rbt12)
    faixa = identificar_faixa(rbt12, int(ano))
    tab = data["anexos"][anexo]
    nominal_pct = float(tab["aliquotas"][faixa-1])
    deducao = float(tab["deducoes"][faixa-1])
    efetiva = ((rbt12 * (nominal_pct/100.0)) - deducao) / rbt12
    return faixa, nominal_pct, deducao, efetiva

def componentes_efetivos(anexo: str, faixa: int, efetiva: float, ano: int) -> dict[str, float]:
    """Percentuais efetivos como frações; aplica teto de ISS quando previsto."""
    data = carregar_tabelas(int(ano))
    anexo = anexo.upper()
    chave = f"{anexo}-{faixa}"
    alt = data.get("iss_redistribuicao", {}).get(chave)
    threshold = data.get("iss_thresholds", {}).get(chave)
    if alt and threshold is not None and efetiva > float(threshold):
        out = {k: (efetiva - 0.05) * (float(v)/100.0) for k, v in alt.items()}
        out["ISS"] = 0.05
        return out
    partilha = data["anexos"][anexo]["partilhas"][faixa-1]
    return {k: efetiva * (float(v)/100.0) for k, v in partilha.items()}

def calcular_anexo(anexo: str, rbt12: float, rpa: float, ano: int, receita_iss_retido: float = 0.0) -> dict:
    anexo = anexo.upper()
    rbt12 = parse_numero(rbt12)
    rpa = parse_numero(rpa)
    receita_iss_retido = parse_numero(receita_iss_retido)
    validar_valor("RPA", rpa)
    validar_valor("receita com ISS retido", receita_iss_retido)
    if receita_iss_retido > rpa + 1e-9:
        raise ValueError("A receita com ISS retido não pode exceder a RPA.")
    if receita_iss_retido and anexo not in {"III","IV","V"}:
        raise ValueError("Segregação de ISS retido deste motor é aplicável somente aos Anexos III, IV e V.")

    faixa, nominal, deducao, efetiva = aliquota_efetiva(anexo, rbt12, int(ano))
    comp_rates = componentes_efetivos(anexo, faixa, efetiva, int(ano))
    bases = {k: rpa for k in comp_rates}
    if "ISS" in bases:
        bases["ISS"] = rpa - receita_iss_retido
    valores = {k: bases[k] * taxa for k, taxa in comp_rates.items()}
    total = sum(valores.values())

    avisos = []
    if faixa == 6 and anexo in {"I","II"}:
        avisos.append("A 6ª faixa não contém ICMS na partilha. Avalie RBA/RBAA e sublimite.")
    if faixa == 6 and anexo in {"III","IV","V"}:
        avisos.append("A 6ª faixa não contém ISS na partilha. Avalie RBA/RBAA e sublimite.")
    if anexo == "IV":
        avisos.append("No Anexo IV, a CPP patronal não integra o DAS e não é calculada por este motor.")
    if receita_iss_retido > 0:
        avisos.append(
            "ISS retido: o percentual do ISS foi desconsiderado somente sobre a receita informada como sujeita à retenção; "
            "os demais tributos continuam incidindo sobre essa receita."
        )
    return {
        "periodo_regras": "2018-2026",
        "ano": int(ano),
        "anexo": anexo,
        "faixa": faixa,
        "rbt12": rbt12,
        "rpa": rpa,
        "receita_iss_retido": receita_iss_retido,
        "aliquota_nominal_pct": nominal,
        "parcela_deduzir": deducao,
        "aliquota_efetiva_pct": efetiva*100.0,
        "bases_por_tributo": bases,
        "percentuais_efetivos_pct": {k: v*100.0 for k,v in comp_rates.items()},
        "valores": valores,
        "total_das_calculado": total,
        "avisos": avisos,
    }

def truncar_duas_casas_sem_arredondar(valor: float) -> float:
    valor = parse_numero(valor)
    validar_valor("valor", valor)
    return math.floor((valor + 1e-12)*100.0)/100.0

def calcular_fator_r(fs12: float, rbt12: float, ano: int, mes: int=12) -> dict:
    carregar_tabelas(int(ano))
    fs12 = parse_numero(fs12)
    rbt12 = parse_numero(rbt12)
    validar_valor("FS12", fs12)
    validar_valor("RBT12", rbt12)
    if fs12 == 0:
        bruto = 0.01
    elif rbt12 == 0:
        bruto = 0.28
    else:
        bruto = fs12 / rbt12
    if int(ano) == 2018 and int(mes) <= 3:
        considerado = round(bruto + 1e-12, 2)
        criterio = "arredondamento a duas casas (PA 01/2018 a 03/2018)"
    else:
        considerado = truncar_duas_casas_sem_arredondar(bruto)
        criterio = "duas casas decimais sem arredondamento (PA a partir de 04/2018)"
    anexo = "III" if considerado >= LIMITE_FATOR_R else "V"
    return {
        "fs12": fs12,
        "rbt12": rbt12,
        "fator_r_bruto": bruto,
        "fator_r_considerado": considerado,
        "criterio": criterio,
        "anexo_sugerido": anexo,
        "premissa_nao_verificada": (
            "Este resultado pressupõe que a atividade está legalmente sujeita ao fator R. "
            "A sujeição deve ser confirmada pela atividade efetivamente exercida e pela base documental."
        ),
    }
