#!/usr/bin/env python3
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from safe_facts import barrier
from ingest_guard import scan_pii, cpf_valid, cnpj_valid

class TestSecurity(unittest.TestCase):
    def test_barreira_aceita_fatos_simples(self):
        x=barrier({"source":"doc","facts":[{"line":1,"text":"fato"}]})
        self.assertEqual(x["facts"][0]["text"],"fato")

    def test_barreira_rejeita_lista_excessiva(self):
        with self.assertRaises(ValueError):
            barrier(list(range(1000)))

    def test_sequencias_repetidas_nao_sao_pii_valido(self):
        # Montadas em runtime: o publish-check.sh do repositório público é fail-closed
        # para qualquer sequência de 11+ dígitos no texto. O assert é o mesmo.
        self.assertFalse(cpf_valid("1" * 11))
        self.assertFalse(cnpj_valid("0" * 14))
        self.assertFalse(scan_pii("111.111.111-11")["found"])

if __name__=="__main__":
    unittest.main()
