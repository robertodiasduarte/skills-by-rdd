#!/usr/bin/env python3
"""Testes do publicador, não dos extratores DOCX/PDF ou de decisões jurídicas."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from datetime import datetime
from zoneinfo import ZoneInfo

import finalizar_entrega as target


def fixture_report() -> dict:
    return {
        "tipo": "TXT",
        "metodo_extracao": "Leitura UTF-8 de fixture sintética.",
        "diagnosticos": {key: f"Diagnóstico sintético: {label}."
                        for key, label in target.DIAGNOSTICOS.items()},
        "correcoes": [],
        "vigencia": {
            "metodo": "TXT: marcadores explícitos; nenhuma exclusão na fixture.",
            "blocos_removidos": 0,
            "linhas_removidas": 0,
            "trechos_removidos": 0,
            "contagem_aproximada": False,
            "ocorrencias": [],
            "ambiguidades": []
        },
        "pendencias": [],
        "verificacoes": {key: True for key in target.VERIFICACOES}
    }


class PublisherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "Ação 14.973.txt"
        self.source.write_text("Ação\n\nPrazo: 15 dias.\n", encoding="utf-8")
        self.md = self.root / "revisado.md"
        self.md.write_text("# Ação\n\nPrazo: 15 dias.\n", encoding="utf-8")
        self.report_path = self.root / "relatorio.json"
        self.report = fixture_report()
        self.save_report()
        self.dest = self.root / "entrega"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def save_report(self) -> None:
        self.report_path.write_text(json.dumps(self.report, ensure_ascii=False), encoding="utf-8")

    def publish(self, **kwargs):
        self.save_report()
        return target.publish(
            self.source, self.md, self.report_path, self.dest,
            reference_date="2026-09-20", **kwargs
        )

    def assert_no_delivery(self) -> None:
        self.assertFalse(self.dest.exists())

    def test_default_names_and_exactly_two_files(self):
        md, txt = self.publish()
        self.assertEqual(md.name, "UF-XX_Acao-14973_Texto-Ajustado_ate-2026-09-20.md")
        self.assertEqual(txt.name, "UF-XX_Acao-14973_README_ate-2026-09-20.txt")
        self.assertEqual({p.name for p in self.dest.iterdir()}, {md.name, txt.name})

    def test_uf_and_original_display_name(self):
        md, _ = self.publish(uf="sp", original_name="Lei nº 14.973.txt")
        self.assertEqual(md.name, "UF-SP_Lei-no-14973_Texto-Ajustado_ate-2026-09-20.md")

    def test_windows_style_basename(self):
        names = target.output_names(r"C:\docs\Lei ação.txt", "UF-RJ", "2026-09-20")
        self.assertEqual(names[0], "UF-RJ_Lei-acao_Texto-Ajustado_ate-2026-09-20.md")

    def test_invalid_uf_rejected(self):
        with self.assertRaises(ValueError):
            self.publish(uf="../../SP")
        self.assert_no_delivery()

    def test_invalid_dates_rejected(self):
        for bad in ("2026-02-30", "20/09/2026", "20260920", "2026-9-2"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                target.resolve_date(bad, "America/Sao_Paulo")

    def test_default_date_uses_timezone(self):
        expected = datetime.now(ZoneInfo("America/Sao_Paulo")).date().isoformat()
        self.assertEqual(target.resolve_date(None, "America/Sao_Paulo"), expected)

    def test_missing_timezone_does_not_silently_use_utc(self):
        with self.assertRaises(ValueError):
            target.resolve_date(None, "Missing/Timezone")

    def test_non_normalizable_name_rejected(self):
        with self.assertRaises(ValueError):
            target.output_names("!!!.txt", None, "2026-09-20")

    def test_source_and_markdown_preserved(self):
        before = self.source.read_bytes()
        original_sha = target.file_hash(self.source)
        md, txt = self.publish()
        self.assertEqual(self.source.read_bytes(), before)
        self.assertEqual(md.read_text(encoding="utf-8"), self.md.read_text(encoding="utf-8"))
        self.assertIn(original_sha, txt.read_text(encoding="utf-8"))
        self.assertIn(target.file_hash(md), txt.read_text(encoding="utf-8"))

    def test_output_utf8_lf_and_unicode_not_compatibility_normalized(self):
        self.md.write_bytes("# Ação\r\n\r\nÁrea: 5 m²; item ①.\r\n".encode("utf-8"))
        md, txt = self.publish()
        self.assertNotIn(b"\r", md.read_bytes())
        self.assertNotIn(b"\r", txt.read_bytes())
        self.assertIn("m²; item ①", md.read_text(encoding="utf-8"))
        self.assertFalse(md.read_bytes().startswith(b"\xef\xbb\xbf"))

    def test_final_newline_added(self):
        self.md.write_text("# Ação", encoding="utf-8")
        md, _ = self.publish()
        self.assertEqual(md.read_bytes(), "# Ação\n".encode("utf-8"))

    def test_readme_has_fixed_sections_without_markdown_headings(self):
        _, txt = self.publish()
        body = txt.read_text(encoding="utf-8")
        for section in ("01 IDENTIFICACAO", "02 EXTRACAO E DIAGNOSTICOS",
                        "03 CORRECOES APLICADAS", "04 TACHADO E NAO VIGENCIA DOCUMENTAL",
                        "05 ESTRUTURA PARA CHUNKING", "06 PENDENCIAS",
                        "07 VERIFICACOES", "08 LIMITACOES E RECOMENDACOES"):
            self.assertIn(section, body)
        self.assertFalse(any(line.lstrip().startswith("#") for line in body.splitlines()))
        self.assertNotIn("```", body)
        self.assertNotIn("<OUTPUT>", body)

    def test_pending_status(self):
        self.report["pendencias"] = ["Linha 4: referência indireta ambígua; mantida."]
        _, txt = self.publish()
        self.assertIn("Status: CONCLUIDO COM PENDENCIAS", txt.read_text(encoding="utf-8"))

    def test_vigencia_ambiguity_also_sets_pending_status(self):
        self.report["vigencia"]["ambiguidades"] = ["Linhas 3 a 5: versões mantidas por dúvida."]
        _, txt = self.publish()
        self.assertIn("CONCLUIDO COM PENDENCIAS", txt.read_text(encoding="utf-8"))

    def test_unmeasured_not_misreported_as_zero(self):
        self.report["vigencia"]["linhas_removidas"] = None
        _, txt = self.publish()
        self.assertIn("Linhas de origem afetadas: Nao mensurado", txt.read_text(encoding="utf-8"))

    def test_empty_markdown_blocked_by_default(self):
        self.md.write_text("  \n", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.publish()
        self.assert_no_delivery()

    def test_empty_original_blocked(self):
        self.source.write_bytes(b"")
        with self.assertRaises(ValueError):
            self.publish()
        self.assert_no_delivery()

    def test_negative_or_boolean_counts_blocked(self):
        for bad in (-1, True, "2"):
            self.report["vigencia"]["blocos_removidos"] = bad
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.publish()
            self.assert_no_delivery()

    def test_exclusion_without_evidence_blocked(self):
        self.report["vigencia"]["trechos_removidos"] = 1
        with self.assertRaises(ValueError):
            self.publish()
        self.assert_no_delivery()

    def test_exclusion_evidence_without_any_count_blocked(self):
        self.report["vigencia"]["ocorrencias"] = [
            {"local": "Linha 1", "evidencia": "Marcador explícito.", "acao": "Retirado o trecho."}
        ]
        with self.assertRaises(ValueError):
            self.publish()
        self.assert_no_delivery()

    def test_incomplete_review_blocked(self):
        self.report["verificacoes"]["sem_ocr"] = False
        with self.assertRaises(ValueError):
            self.publish()
        self.assert_no_delivery()

    def test_missing_diagnostic_blocked(self):
        del self.report["diagnosticos"]["imagens"]
        with self.assertRaises(ValueError):
            self.publish()
        self.assert_no_delivery()

    def test_unknown_format_and_type_mismatch_blocked(self):
        self.report["tipo"] = "PDF"
        with self.assertRaises(ValueError):
            self.publish()
        self.assert_no_delivery()

    def test_full_objective_exclusion_can_publish_empty_markdown(self):
        self.md.write_text("", encoding="utf-8")
        self.report["conteudo_integralmente_excluido"] = True
        self.report["vigencia"]["blocos_removidos"] = 1
        self.report["vigencia"]["trechos_removidos"] = 1
        self.report["vigencia"]["ocorrencias"] = [{
            "local": "Único bloco da fixture",
            "evidencia": "Marcador de exclusão explícito e abrangente na fixture.",
            "acao": "Excluído integralmente o único bloco."
        }]
        md, txt = self.publish()
        self.assertEqual(md.read_bytes(), b"")
        self.assertIn("SEM TEXTO MANTIDO", txt.read_text(encoding="utf-8"))

    def test_false_declaration_of_full_exclusion_blocked(self):
        self.report["conteudo_integralmente_excluido"] = True
        with self.assertRaises(ValueError):
            self.publish()
        self.assert_no_delivery()

    def test_existing_destination_not_overwritten(self):
        self.publish()
        files_before = {p.name: p.read_bytes() for p in self.dest.iterdir()}
        with self.assertRaises(ValueError):
            self.publish()
        self.assertEqual({p.name: p.read_bytes() for p in self.dest.iterdir()}, files_before)

    def test_invalid_json_does_not_publish(self):
        self.report_path.write_text("{not json", encoding="utf-8")
        with self.assertRaises(ValueError):
            target.publish(self.source, self.md, self.report_path, self.dest,
                           reference_date="2026-09-20")
        self.assert_no_delivery()

    def test_missing_source_does_not_publish(self):
        self.source.unlink()
        with self.assertRaises(ValueError):
            self.publish()
        self.assert_no_delivery()

    def test_nul_text_is_blocked(self):
        self.md.write_text("Texto\x00corrompido", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.publish()
        self.assert_no_delivery()

    def test_markdown_heading_counts_ignore_code_fences(self):
        text = "# Título\n\n## Seção\n\n```txt\n# Não é título\n```\n\n### Sub\n\n"
        stats = target.markdown_stats(text)
        self.assertEqual((stats["H1"], stats["H2"], stats["H3"]), (1, 1, 1))

    def test_deterministic_output_for_same_inputs_and_date(self):
        md1, txt1 = self.publish()
        self.dest = self.root / "outra-entrega"
        md2, txt2 = self.publish()
        self.assertEqual(md1.read_bytes(), md2.read_bytes())
        self.assertEqual(txt1.read_bytes(), txt2.read_bytes())

    def test_partial_write_failure_cleans_created_files(self):
        real_open = Path.open

        def failing_open(path, *args, **kwargs):
            if "_README_" in path.name and args and args[0] == "xb":
                raise OSError("Falha de escrita simulada.")
            return real_open(path, *args, **kwargs)

        with patch.object(Path, "open", new=failing_open):
            with self.assertRaises(OSError):
                self.publish()
        self.assert_no_delivery()


if __name__ == "__main__":
    unittest.main()
