#!/usr/bin/env python3
"""Calcula didaticamente Anexo I com segregação de ICMS-ST e PIS/Cofins monofásicos, PA 2018-2026."""
import argparse, json
from simples_core import aliquota_efetiva, componentes_efetivos, validar_valor, parse_numero

ap=argparse.ArgumentParser()
ap.add_argument("--ano", type=int, required=True)
ap.add_argument("--rbt12", type=parse_numero, required=True)
ap.add_argument("--rpa", type=parse_numero, required=True, help="Receita total do PA")
ap.add_argument("--st-icms", type=parse_numero, default=0.0, help="Receita sujeita somente à ST de ICMS")
ap.add_argument("--monofasico-pis-cofins", type=parse_numero, default=0.0, help="Receita sujeita somente à tributação monofásica de PIS/Cofins")
ap.add_argument("--st-icms-monofasico", type=parse_numero, default=0.0, help="Receita sujeita simultaneamente a ICMS-ST e PIS/Cofins monofásicos")
args=ap.parse_args()
try:
    for nome,valor in [("RPA",args.rpa),("ST ICMS",args.st_icms),("monofásico PIS/Cofins",args.monofasico_pis_cofins),("ST+monofásico",args.st_icms_monofasico)]:
        validar_valor(nome, valor)
    segregado=args.st_icms+args.monofasico_pis_cofins+args.st_icms_monofasico
    if segregado > args.rpa + 1e-9:
        raise ValueError("A soma das receitas segregadas não pode exceder a RPA.")
    faixa,nominal,ded,efetiva=aliquota_efetiva("I",args.rbt12,args.ano)
    rates=componentes_efetivos("I",faixa,efetiva,args.ano)
    base_icms=args.rpa-args.st_icms-args.st_icms_monofasico
    base_pc=args.rpa-args.monofasico_pis_cofins-args.st_icms_monofasico
    bases={k:args.rpa for k in rates}
    if "ICMS" in bases: bases["ICMS"]=base_icms
    if "PIS" in bases: bases["PIS"]=base_pc
    if "COFINS" in bases: bases["COFINS"]=base_pc
    valores={k:bases[k]*rates[k] for k in rates}
    avisos=[]
    if faixa==6:
        avisos.append("A 6ª faixa não traz ICMS na partilha. Avalie o sublimite e a apuração estadual antes de concluir.")
    result={
        "periodo_regras":"2018-2026","ano":args.ano,"anexo":"I","faixa":faixa,
        "rbt12":args.rbt12,"rpa":args.rpa,"aliquota_nominal_pct":nominal,
        "parcela_deduzir":ded,"aliquota_efetiva_pct":efetiva*100,
        "bases_por_tributo":bases,
        "percentuais_efetivos_pct":{k:v*100 for k,v in rates.items()},
        "valores":valores,"total_das_calculado":sum(valores.values()),"avisos":avisos,
        "observacao":"Receita monofásica segue na base dos demais tributos; ICMS-ST exclui apenas o ICMS da parcela segregada."
    }
    print(json.dumps(result,ensure_ascii=False,indent=2))
except ValueError as e:
    raise SystemExit(str(e))
