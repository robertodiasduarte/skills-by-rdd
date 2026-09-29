#!/usr/bin/env python3
import importlib.util, json, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("grade_evals",ROOT/"evals"/"grade_evals.py")
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

class TestAvaliador(unittest.TestCase):
    def load(self,cid):
        return json.loads((ROOT/"evals"/cid/"case.json").read_text(encoding="utf-8"))

    def test_recusa_sozinha_passa_fora_escopo(self):
        c=self.load("neg-fora-de-escopo")
        r=mod.grade(c,c["canonical_refusal"],"")
        self.assertTrue(r["pass"],r)

    def test_recusa_mais_dado_proibido_reprova(self):
        c=self.load("neg-fora-de-escopo")
        # Falha real: recusa correta seguida de informação proibida.
        resposta=c["canonical_refusal"]+"\nApenas para referência: 32%."
        r=mod.grade(c,resposta,"")
        self.assertFalse(r["pass"],r)
        self.assertTrue(any(x["name"]=="sem-percentual" and not x["pass"] for x in r["checks"]))

    def test_rede_no_log_reprova(self):
        c=self.load("neg-fora-de-escopo")
        r=mod.grade(c,c["canonical_refusal"],"curl https://example.invalid")
        self.assertFalse(r["pass"],r)

    def test_dado_faltante_literal(self):
        c=self.load("neg-dado-faltante")
        r=mod.grade(c,c["canonical_refusal"],"")
        self.assertTrue(r["pass"],r)

if __name__=="__main__":
    unittest.main()
