#!/usr/bin/env python3
import ast, importlib.util, json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/"scripts"
sys.path.insert(0,str(SCRIPTS))

from simples_core import parse_numero, parse_lista_numeros, calcular_anexo, calcular_fator_r
from calcular_rbt12p import calcular_rbt12p
from lookup_cnae import buscar_texto
from tables_loader import carregar_tabelas
from validate_goldens import run_all
from engine import executar as engine_exec
from verify import executar as verify_exec
from apurar_verificado import comparar_resultados

ORDINARY_FLAGS={
    "exportacao":False,"sublimite":False,"icms_st":False,
    "monofasico_pis_cofins":False,"inicio_atividade":False,
}

def write_input(td, **kw):
    payload={
        "competencia":"2026-08","modo":"ordinario","anexo":"III","rbt12":500000,"rpa":50000,
        "receita_iss_retido":0,"qualificacoes":dict(ORDINARY_FLAGS)
    }
    payload.update(kw)
    p=Path(td)/"apuracao.json"
    p.write_text(json.dumps(payload,ensure_ascii=False),encoding="utf-8")
    return p,payload

class TestParsingBrasileiro(unittest.TestCase):
    def test_numero_brasileiro(self):
        self.assertAlmostEqual(parse_numero("R$ 1.234.567,89"),1234567.89,places=6)
        self.assertAlmostEqual(parse_numero("1234,56"),1234.56,places=6)

    def test_lista_brasileira(self):
        self.assertEqual(parse_lista_numeros("10.000,00; 12.500,50; 8.000,00"),[10000.0,12500.5,8000.0])

class TestGoldensOficiais(unittest.TestCase):
    def test_baseline_engine_e_verify(self):
        r=run_all()
        self.assertTrue(r["pass"],r)
        self.assertGreaterEqual(len(r["cases"]),5)

    def test_anexo_iii_publicado(self):
        r=calcular_anexo("III",500000,10000,2018)
        self.assertAlmostEqual(r["aliquota_efetiva_pct"],9.972,places=6)
        self.assertAlmostEqual(r["total_das_calculado"],997.20,places=2)

    def test_anexo_v_publicado(self):
        r=calcular_anexo("V",500000,10000,2018)
        self.assertAlmostEqual(r["total_das_calculado"],1752.00,places=2)

class TestFronteiras(unittest.TestCase):
    def test_faixa_exata_e_logo_acima(self):
        a=calcular_anexo("III",180000,1000,2026)
        b=calcular_anexo("III",180000.01,1000,2026)
        self.assertEqual(a["faixa"],1)
        self.assertEqual(b["faixa"],2)

    def test_fator_r_028_inclusivo(self):
        r=calcular_fator_r(140000,500000,2026,8)
        self.assertEqual(r["fator_r_considerado"],0.28)
        self.assertEqual(r["anexo_sugerido"],"III")
        self.assertIn("premissa_nao_verificada",r)

class TestRBT12p(unittest.TestCase):
    def test_primeiro_mes_oficial(self):
        r=calcular_rbt12p("10.000,00","",2018)
        self.assertAlmostEqual(r["rbt12p"],120000.0,places=2)

    def test_media_meses_anteriores(self):
        r=calcular_rbt12p("20.000,00","10.000,00; 12.500,50; 8.000,00",2026)
        self.assertAlmostEqual(r["rbt12p"],(10000+12500.5+8000)/3*12,places=6)

class TestISSRetido(unittest.TestCase):
    def test_so_base_iss_reduzida(self):
        normal=calcular_anexo("III",500000,50000,2026)
        ret=calcular_anexo("III",500000,50000,2026,receita_iss_retido=10000)
        self.assertAlmostEqual(ret["bases_por_tributo"]["ISS"],40000.0,places=8)
        for tributo,base in ret["bases_por_tributo"].items():
            if tributo!="ISS":
                self.assertAlmostEqual(base,50000.0,places=8)
        iss_rate=normal["percentuais_efetivos_pct"]["ISS"]/100
        self.assertAlmostEqual(normal["total_das_calculado"]-ret["total_das_calculado"],10000*iss_rate,places=6)

class TestVerifyIndependencia(unittest.TestCase):
    def test_verify_nao_importa_engine_nem_core(self):
        tree=ast.parse((SCRIPTS/"verify.py").read_text(encoding="utf-8"))
        imported=set()
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):
                imported.update(x.name.split(".")[0] for x in n.names)
            elif isinstance(n,ast.ImportFrom) and n.module:
                imported.add(n.module.split(".")[0])
        self.assertNotIn("engine",imported)
        self.assertNotIn("simples_core",imported)

    def test_engine_verify_concordam(self):
        with tempfile.TemporaryDirectory() as td:
            p,_=write_input(td,receita_iss_retido=10000)
            e=engine_exec(str(p)); v=verify_exec(str(p))
            self.assertEqual(comparar_resultados(e,v),[])

    def test_sabotagem_engine_aciona_hard_stop(self):
        with tempfile.TemporaryDirectory() as td:
            p,_=write_input(td)
            e=engine_exec(str(p)); v=verify_exec(str(p))
            sabotado=json.loads(json.dumps(e))
            sabotado["total_das_calculado"] += 10.00
            diffs=comparar_resultados(sabotado,v)
            self.assertTrue(any(d["campo"]=="total_das_calculado" for d in diffs))

class TestApurador(unittest.TestCase):
    def run_apurar(self,payload):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"apuracao.json"
            p.write_text(json.dumps(payload,ensure_ascii=False),encoding="utf-8")
            proc=subprocess.run([sys.executable,str(SCRIPTS/"apurar_verificado.py"),str(p)],capture_output=True,text=True)
            return proc,json.loads(proc.stdout)

    def test_golden_exato(self):
        payload={"competencia":"2018-07","modo":"ordinario","anexo":"III","rbt12":500000,"rpa":10000,
                 "receita_iss_retido":0,"qualificacoes":dict(ORDINARY_FLAGS)}
        proc,out=self.run_apurar(payload)
        self.assertEqual(proc.returncode,0,out)
        self.assertEqual(out["status"],"GABARITO_OFICIAL_CONFERIDO")

    def test_arbitrario_verificado_sem_golden(self):
        payload={"competencia":"2026-08","modo":"ordinario","anexo":"III","rbt12":500000,"rpa":50000,
                 "receita_iss_retido":10000,"qualificacoes":dict(ORDINARY_FLAGS)}
        proc,out=self.run_apurar(payload)
        self.assertEqual(proc.returncode,0,out)
        self.assertEqual(out["status"],"CALCULO_DETERMINISTICO_SEM_GABARITO_ESPECIFICO")
        self.assertFalse(out["validacao"]["validacao_normativa_especifica"])

    def test_exportacao_sublimite_bloqueados(self):
        flags=dict(ORDINARY_FLAGS); flags["exportacao"]=True; flags["sublimite"]=True
        payload={"competencia":"2018-01","modo":"ordinario","anexo":"I","rbt12":4000000,"rpa":100000,
                 "receita_iss_retido":0,"qualificacoes":flags}
        proc,out=self.run_apurar(payload)
        self.assertNotEqual(proc.returncode,0)
        self.assertTrue(out["entrega_bloqueada"])


    def test_exemplo6_exportacao_golden_oficial(self):
        payload={
            "competencia":"2018-01","modo":"exportacao_anexo_i","anexo":"I",
            "rbt12_interno":2000000,"rbt12_externo":1000000,
            "rpa_interno":100000,"rpa_externo":50000,
            "rba_interno":100000,"rba_externo":50000,"sublimite":3600000,
            "qualificacoes":{"exportacao":True,"sublimite":False,"icms_st":False,
                              "monofasico_pis_cofins":False,"inicio_atividade":False}
        }
        proc,out=self.run_apurar(payload)
        self.assertEqual(proc.returncode,0,out)
        self.assertEqual(out["status"],"GABARITO_OFICIAL_CONFERIDO")
        self.assertEqual(out["validacao"]["golden_id"],"PGDAS-EX6-ANEXO-I-EXPORTACAO")
        self.assertAlmostEqual(out["resultado"]["mercado_interno"]["total"],9935.02,places=2)
        self.assertAlmostEqual(out["resultado"]["mercado_externo"]["total"],2154.76,places=2)
        self.assertAlmostEqual(out["resultado"]["total_das_calculado"],12089.78,places=2)

    def test_nao_emite_pass_generico(self):
        fonte=(SCRIPTS/"apurar_verificado.py").read_text(encoding="utf-8")
        self.assertNotIn('"PASS"',fonte)
        self.assertNotIn("'PASS'",fonte)


class TestGovernancaV41(unittest.TestCase):
    def test_todos_goldens_tem_fonte_e_conferencia(self):
        data=json.loads((ROOT/"references"/"goldens"/"official_examples.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(data["cases"]),5)
        for c in data["cases"]:
            self.assertTrue(c.get("conferido_por"),c)
            self.assertTrue(c.get("fonte_do_gabarito"),c)
            src=c.get("source")
            self.assertIsInstance(src,dict,c)
            self.assertTrue(src.get("document"),c)
            self.assertTrue(src.get("locator"),c)
            self.assertTrue(src.get("evidence"),c)

    def test_comandos_documentados_nao_dependem_do_cwd(self):
        for p in ROOT.rglob("*"):
            if not p.is_file() or p.suffix not in {".md",".json",".yaml",".yml",".py"}:
                continue
            text=p.read_text(encoding="utf-8",errors="replace")
            self.assertNotRegex(text,r"\bpython3\s+(?:\./)?scripts/",str(p.relative_to(ROOT)))

    def test_runtime_nao_trata_allowed_tools_como_firewall(self):
        text=(ROOT/"references"/"RUNTIME_COMPATIBILITY.md").read_text(encoding="utf-8").lower()
        self.assertIn("não um firewall",text)
        self.assertIn("bash",text)
        self.assertIn("egress",text)

    def test_eval_conceitual_2027_existe(self):
        c=json.loads((ROOT/"evals"/"pos-conceitual-2027"/"case.json").read_text(encoding="utf-8"))
        self.assertEqual(c["id"],"pos-conceitual-2027")
        self.assertIn("2027",c["required_strings"])

class TestVigencia(unittest.TestCase):
    def test_2027_sem_tabela(self):
        with self.assertRaises(ValueError):
            carregar_tabelas(2027)

class TestCNAE(unittest.TestCase):
    def test_programacao_encontra_desenvolvimento(self):
        r=buscar_texto("programação",10)
        self.assertTrue(any(x["CNAE"]=="6201501" for x in r),r)

if __name__=="__main__":
    unittest.main()
