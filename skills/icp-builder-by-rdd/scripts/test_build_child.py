#!/usr/bin/env python3
"""Behavioral checks for generation, provenance, portability and preservation."""

import copy
import json
import re
import tempfile
import unittest
from pathlib import Path

from build_child import ACTIVITIES, build, validate

ROOT = Path(__file__).resolve().parents[1]


class BuildChildTests(unittest.TestCase):
    def setUp(self):
        self.profile = json.loads((ROOT / "assets/exemplo-beatriz.json").read_text(encoding="utf-8"))

    def test_complete_portable_skill_preserves_provenance(self):
        with tempfile.TemporaryDirectory() as temporary:
            child = build(self.profile, temporary)
            self.assertEqual(json.loads((child / "references/perfil.json").read_text()), self.profile)
            skill = (child / "SKILL.md").read_text()
            self.assertIn("**draft**", skill)
            self.assertIn("Beatriz", skill)
            self.assertNotIn(str(ROOT), skill)
            self.assertNotRegex(skill, r"\$\{[A-Za-z_]+\}")
            evidence = (child / "references/evidencias.md").read_text()
            self.assertIn("| E03 |", evidence)
            self.assertIn("| exemplo |", evidence)
            self.assertIn("| H01 |", evidence)
            self.assertIn("| hipotese |", evidence)
            for activity in ACTIVITIES:
                self.assertTrue((child / f"references/metodos/{activity}.md").is_file())
            # Every local Markdown reference is usable after moving the child away from the mother.
            for document in child.rglob("*.md"):
                for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", document.read_text()):
                    if not target.startswith(("http://", "https://", "#")):
                        self.assertTrue((document.parent / target.split("#")[0]).exists(),
                                        f"Broken reference: {document} -> {target}")

    def test_existing_customization_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            child = build(self.profile, temporary)
            custom = child / "SKILL.md"
            custom.write_text("Personalização existente", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Destino já existe"):
                build(self.profile, temporary)
            self.assertEqual(custom.read_text(), "Personalização existente")

    def test_example_cannot_be_promoted_to_ready_without_evidence(self):
        self.profile["status"] = "ready"
        with self.assertRaisesRegex(ValueError, "somente em exemplos"):
            validate(self.profile)

    def test_ready_requires_coverage_but_not_invented_emotions(self):
        self.profile["status"] = "ready"
        self.profile["evidence"][0]["status"] = "relatado"
        self.profile["evidence"][0]["source"] = "Relato ilustrativo para teste do contrato"
        validate(self.profile)
        self.profile["priorities"] = [p for p in self.profile["priorities"] if p["activity"] != "eventos"]
        with self.assertRaisesRegex(ValueError, "sete atividades"):
            validate(self.profile)

    def test_missing_evidence_and_invalid_transition_are_rejected(self):
        broken = copy.deepcopy(self.profile)
        broken["journey"][0]["evidence_ids"] = ["NAO_EXISTE"]
        with self.assertRaisesRegex(ValueError, "evidência inexistente"):
            validate(broken)
        broken = copy.deepcopy(self.profile)
        broken["journey"][0]["transitions"][0]["to"] = "fase-inexistente"
        with self.assertRaisesRegex(ValueError, "Transição para fase inexistente"):
            validate(broken)

    def test_synthetic_quote_cannot_claim_hypothetical_provenance(self):
        self.profile["voice"]["quotes"] = [{"text": "Frase inventada", "evidence_id": "H01"}]
        with self.assertRaisesRegex(ValueError, "origem hipotética"):
            validate(self.profile)

    def test_invalid_name_cannot_escape_output_directory(self):
        self.profile["skill"]["name"] = "../outra-pasta"
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "Nome inválido"):
                build(self.profile, temporary)
            self.assertEqual(list(Path(temporary).iterdir()), [])

    def test_profile_text_is_data_not_execution_or_html(self):
        with tempfile.TemporaryDirectory() as temporary:
            marker = Path(temporary) / "executed"
            payload = f"${{name}} $(touch '{marker}') <script>unsafe</script>"
            self.profile["company"]["name"] = payload
            child = build(self.profile, temporary)
            self.assertFalse(marker.exists())
            document = (child / "references/perfil.md").read_text()
            self.assertNotIn("<script>", document)
            self.assertIn("&lt;script&gt;", document)
            self.assertEqual(json.loads((child / "references/perfil.json").read_text())["company"]["name"], payload)

    def test_failed_build_does_not_leave_a_partial_skill(self):
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as source:
            source_root = Path(source)
            (source_root / "assets").mkdir()
            (source_root / "assets/skill-filha.md").write_text((ROOT / "assets/skill-filha.md").read_text())
            with self.assertRaises(FileNotFoundError):
                build(self.profile, temporary, source_root)
            self.assertEqual(list(Path(temporary).iterdir()), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
