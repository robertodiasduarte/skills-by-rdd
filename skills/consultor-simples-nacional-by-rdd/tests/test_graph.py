#!/usr/bin/env python3
import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class TestGraph(unittest.TestCase):
    def test_sem_arestas_orfas(self):
        g=json.loads((ROOT/"references"/"graph.yaml").read_text(encoding="utf-8"))
        comm={c["id"] for c in g["communities"]}
        nodes={n["id"]:n for n in g["nodes"]}
        self.assertTrue(all(n["community"] in comm for n in nodes.values()))
        for e in g["edges"]:
            self.assertIn(e["from"],nodes)
            self.assertIn(e["to"],nodes)
        for q in g["queries"]:
            for nid in q["navegacao"]:
                self.assertIn(nid,nodes)

if __name__=="__main__":
    unittest.main()
