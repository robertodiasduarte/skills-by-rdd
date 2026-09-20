"""Synthetic protocol tests. No real approval, PII, laws or domain goldens."""
from __future__ import annotations
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import scope_gate as gate
import lint_bundle as lintmod

def base_scope() -> dict:
    value = json.loads((ROOT / "assets/escopo.template.json").read_text(encoding="utf-8"))
    value.update({
        "nome": "organizando-documentos", "tema": "Organização documental",
        "objetivo": "Organizar os documentos conforme o processo aprovado.",
        "publico": "Equipe interna", "jurisdicao": "Brasil; rotina interna sem conclusão normativa",
        "cobre": ["Organização de documentos"], "recusa": ["Cálculo de tributos"],
        "periodo_consulta": "nao aplicavel", "entradas": ["Documentos anonimizados"],
        "saidas": ["Checklist de organização"], "revisao_humana": "Responsável pelo processo",
        "criterios_aceite": ["Pedir documento faltante"], "restricoes": ["Não transmitir dados"],
    })
    return value

def approval(scope: dict) -> dict:
    return {
        "origem": "usuario", "escopo_id": scope["id"], "revisao": scope["revisao"],
        "sha256_escopo": gate.digest(scope), "texto": gate.confirmation_text(scope),
        "apos_apresentacao": True, "mensagem_id": "MENSAGEM_SINTETICA_DE_TESTE",
    }

def minimal_skill(name: str = "exemplo") -> str:
    body = "\n\n".join([f"# {name}"] + [
        f"{heading}\nConteúdo ilustrativo." for heading in lintmod.REQUIRED_HEADINGS
    ])
    return (f'---\nname: {name}\ndescription: "Organiza exemplos. Use quando houver teste."\n---\n\n'
            + body + "\n")

class ScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.scope = base_scope()

    def add_material(self, slot: str, filename: str = "material.md") -> dict:
        path = self.folder / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Material sintético\nProcesso de organização.\n", encoding="utf-8")
        m = {
            "id": f"M{len(self.scope['materiais']) + 1}", "slot": slot,
            "path": filename, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "status": "utilizavel", "titulo": "Material sintético",
            "fonte": "Fixture de teste, sem validade normativa", "localizador": "Seção única",
            "periodo": "nao aplicavel", "papel": "teste",
            "conferido_por": "nao disponivel", "fonte_do_gabarito": "nao disponivel",
        }
        self.scope["materiais"].append(m)
        return m

    def test_prepare_does_not_authorize(self):
        result = gate.challenge(self.scope)
        self.assertFalse(result["geracao_autorizada"])
        self.assertEqual(result["status"], "AGUARDANDO_CONFIRMACAO")

    def test_exact_approval_authorizes(self):
        self.assertTrue(gate.check_approval(self.scope, approval(self.scope))["geracao_autorizada"])

    def test_ok_is_not_approval(self):
        a = approval(self.scope); a["texto"] = "ok"
        with self.assertRaisesRegex(gate.GateError, "TEXTO_CONFIRMACAO_INVALIDO"):
            gate.check_approval(self.scope, a)

    def test_document_is_not_user(self):
        a = approval(self.scope); a["origem"] = "documento"
        with self.assertRaisesRegex(gate.GateError, "ORIGEM_NAO_USUARIO"):
            gate.check_approval(self.scope, a)

    def test_prior_approval_is_blocked(self):
        a = approval(self.scope); a["apos_apresentacao"] = False
        with self.assertRaisesRegex(gate.GateError, "ANTERIOR_AO_RESUMO"):
            gate.check_approval(self.scope, a)

    def test_missing_message_evidence(self):
        a = approval(self.scope); a["mensagem_id"] = "nao disponivel"
        with self.assertRaisesRegex(gate.GateError, "EVIDENCIA_MENSAGEM_AUSENTE"):
            gate.check_approval(self.scope, a)

    def test_changed_scope_invalidates_hash(self):
        a = approval(self.scope)
        self.scope["saidas"].append("Relatório adicional")
        with self.assertRaisesRegex(gate.GateError, "ESCOPO_ALTERADO"):
            gate.check_approval(self.scope, a)

    def test_revision_invalidates_approval(self):
        a = approval(self.scope); self.scope["revisao"] = 2
        with self.assertRaisesRegex(gate.GateError, "VERSAO_NAO_CONFIRMADA"):
            gate.check_approval(self.scope, a)

    def test_unknown_field_is_blocked(self):
        self.scope["campo_extra"] = "injetado"
        with self.assertRaisesRegex(gate.GateError, "CAMPOS_ESCOPO_INVALIDOS"):
            gate.challenge(self.scope)

    def test_boolean_is_not_revision(self):
        self.scope["revisao"] = True
        with self.assertRaisesRegex(gate.GateError, "REVISAO_INVALIDA"):
            gate.challenge(self.scope)

    def test_missing_objective_is_blocked(self):
        self.scope["objetivo"] = "nao disponivel"
        with self.assertRaisesRegex(gate.GateError, "DEFINICAO_ESSENCIAL_AUSENTE"):
            gate.challenge(self.scope)

    def test_no_negative_boundary_is_blocked(self):
        self.scope["recusa"] = []
        with self.assertRaisesRegex(gate.GateError, "LISTA_ESSENCIAL_VAZIA"):
            gate.challenge(self.scope)

    def test_profile_matrix(self):
        for request in ["operacional", "consulta", "calcula", "ambas"]:
            for has_base, has_normative in [(False, False), (True, False), (False, True), (True, True)]:
                with self.subTest(request=request, base=has_base, normative=has_normative):
                    s = base_scope()
                    s["perfil_pedido"] = request
                    s["processo_normativo"] = True
                    if has_base:
                        s["materiais"].append({"slot": "base", "status": "utilizavel"})
                    if has_normative:
                        s["materiais"].append({"slot": "norma", "status": "utilizavel"})
                    expected = {
                        "operacional": "C",
                        "consulta": "B" if has_base else "C",
                        "calcula": "A" if has_normative else "C",
                        "ambas": "AB" if has_base and has_normative else
                                 ("A" if has_normative else ("B" if has_base else "C")),
                    }[request]
                    self.assertEqual(gate.derive_profile(s), expected)

    def test_normative_double_trigger(self):
        self.add_material("norma")
        self.scope["perfil_pedido"] = "calcula"
        self.scope["processo_normativo"] = False
        self.assertEqual(gate.derive_profile(self.scope), "C")

    def test_pending_material_gives_no_capability(self):
        self.scope["perfil_pedido"] = "consulta"
        m = self.add_material("base")
        m["status"] = "pendente"
        self.assertEqual(gate.derive_profile(self.scope), "C")

    def test_valid_base_profile_b(self):
        self.add_material("base")
        self.scope.update(perfil_pedido="consulta", perfil_efetivo="B", periodo_consulta="2026")
        gate.validate_scope(self.scope, self.folder)

    def test_declared_profile_mismatch(self):
        self.scope["perfil_efetivo"] = "A"
        with self.assertRaisesRegex(gate.GateError, "PERFIL_DIVERGENTE"):
            gate.validate_scope(self.scope)

    def test_base_requires_markdown(self):
        self.add_material("base", "material.txt")
        with self.assertRaisesRegex(gate.GateError, "BASE_EXIGE_MARKDOWN"):
            gate.validate_scope(self.scope, self.folder)

    def test_file_content_change_invalidates_approval(self):
        self.add_material("base")
        a = approval(self.scope)
        (self.folder / "material.md").write_text("Alterado.", encoding="utf-8")
        with self.assertRaisesRegex(gate.GateError, "MATERIAL_ALTERADO"):
            gate.check_approval(self.scope, a, self.folder)

    def test_registered_source_hash_change_invalidates_scope(self):
        m = self.add_material("base")
        a = approval(self.scope)
        path = self.folder / m["path"]
        path.write_text("Nova versão.", encoding="utf-8")
        m["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        with self.assertRaisesRegex(gate.GateError, "ESCOPO_ALTERADO"):
            gate.check_approval(self.scope, a, self.folder)

    def test_empty_source_rejected(self):
        m = self.add_material("base")
        path = self.folder / m["path"]; path.write_bytes(b"")
        m["sha256"] = hashlib.sha256(b"").hexdigest()
        with self.assertRaisesRegex(gate.GateError, "MATERIAL_VAZIO"):
            gate.validate_scope(self.scope, self.folder)

    def test_traversal_rejected(self):
        m = self.add_material("base"); m["path"] = "../fora.md"
        with self.assertRaisesRegex(gate.GateError, "CAMINHO_INSEGURO"):
            gate.validate_scope(self.scope, self.folder)

    def test_symlink_rejected(self):
        m = self.add_material("base")
        link = self.folder / "link.md"
        try:
            link.symlink_to(self.folder / m["path"])
        except OSError:
            self.skipTest("Host não permite symlink")
        m["path"] = "link.md"
        with self.assertRaisesRegex(gate.GateError, "LINK_SIMBOLICO_RECUSADO"):
            gate.validate_scope(self.scope, self.folder)

    def test_duplicate_json_rejected(self):
        path = self.folder / "duplicate.json"
        path.write_text('{"a":1,"a":2}', encoding="utf-8")
        with self.assertRaisesRegex(gate.GateError, "JSON_CHAVE_DUPLICADA"):
            gate.read_json(path)

    def test_nonfinite_json_rejected(self):
        path = self.folder / "nan.json"; path.write_text('{"a":NaN}', encoding="utf-8")
        with self.assertRaisesRegex(gate.GateError, "JSON_CONSTANTE_INVALIDA"):
            gate.read_json(path)

    def test_canonical_hash_independent_of_key_order(self):
        reversed_scope = dict(reversed(list(self.scope.items())))
        self.assertEqual(gate.digest(self.scope), gate.digest(reversed_scope))

    def test_cli_bad_json_is_safe_json_error(self):
        path = self.folder / "bad.json"; path.write_text("{", encoding="utf-8")
        run = subprocess.run([sys.executable, "-B", "-S", str(ROOT / "scripts/scope_gate.py"),
                              "prepare", "--scope", str(path)], text=True, capture_output=True)
        self.assertEqual(run.returncode, 2)
        self.assertFalse(json.loads(run.stdout)["geracao_autorizada"])
        self.assertNotIn("Traceback", run.stdout + run.stderr)

    def test_cli_check_without_approval_is_blocked(self):
        path = self.folder / "scope.json"
        path.write_text(json.dumps(self.scope), encoding="utf-8")
        run = subprocess.run([sys.executable, "-B", "-S", str(ROOT / "scripts/scope_gate.py"),
                              "check", "--scope", str(path)], text=True, capture_output=True)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(json.loads(run.stdout)["erro"], "CONFIRMACAO_AUSENTE")

    def test_cli_positive_complete_flow(self):
        path, app = self.folder / "scope.json", self.folder / "approval.json"
        path.write_text(json.dumps(self.scope), encoding="utf-8")
        app.write_text(json.dumps(approval(self.scope)), encoding="utf-8")
        run = subprocess.run([sys.executable, "-B", "-S", str(ROOT / "scripts/scope_gate.py"),
                              "check", "--scope", str(path), "--approval", str(app)],
                             text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertTrue(json.loads(run.stdout)["geracao_autorizada"])

class LintTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name) / "exemplo"
        self.folder.mkdir()
        self.skill = self.folder / "SKILL.md"
        self.skill.write_text(minimal_skill(), encoding="utf-8")

    def test_valid_bundle(self):
        result = lintmod.lint(self.folder)
        self.assertTrue(result["pass"], result)

    def test_mismatched_name(self):
        self.skill.write_text(minimal_skill("outro"), encoding="utf-8")
        self.assertIn("NOME_INVALIDO", lintmod.lint(self.folder)["errors"])

    def test_missing_section(self):
        content = self.skill.read_text().replace("## Examples", "## Outro")
        self.skill.write_text(content, encoding="utf-8")
        self.assertIn("SECAO_AUSENTE_OU_DUPLICADA", lintmod.lint(self.folder)["errors"])

    def test_sections_out_of_order(self):
        content = self.skill.read_text().replace("## Quick start", "TEMP")
        content = content.replace("## Examples", "## Quick start").replace("TEMP", "## Examples")
        self.skill.write_text(content, encoding="utf-8")
        self.assertIn("SECOES_FORA_DE_ORDEM", lintmod.lint(self.folder)["errors"])

    def test_forbidden_version_top_level(self):
        content = self.skill.read_text().replace("name: exemplo", "name: exemplo\nversion: 1.0")
        self.skill.write_text(content, encoding="utf-8")
        self.assertFalse(lintmod.lint(self.folder)["pass"])

    def test_roman_numeral_not_false_positive(self):
        content = self.skill.read_text().replace("Organiza exemplos.", "Consulta Anexo I.")
        self.skill.write_text(content, encoding="utf-8")
        self.assertTrue(lintmod.lint(self.folder)["pass"])

    def test_orphan_script_rejected(self):
        (self.folder / "scripts").mkdir()
        (self.folder / "scripts/probe.py").write_text('print("teste")\n')
        self.assertIn("SCRIPT_NAO_CITADO", lintmod.lint(self.folder)["errors"])

    def test_shell_root_script_reference_accepted(self):
        (self.folder / "scripts").mkdir()
        (self.folder / "scripts/probe.py").write_text('print("teste")\n')
        with self.skill.open("a") as out:
            out.write('\n`python3 "$SKILL_ROOT/scripts/probe.py"`\n')
        result = lintmod.lint(self.folder)
        self.assertTrue(result["pass"], result)

    def test_broken_reference_rejected(self):
        with self.skill.open("a") as out:
            out.write("\n[Ausente](references/ausente.md)\n")
        self.assertIn("REFERENCIA_INEXISTENTE", lintmod.lint(self.folder)["errors"])

    def test_reference_traversal_rejected(self):
        with self.skill.open("a") as out:
            out.write("\n[Externo](../fora.md)\n")
        self.assertIn("REFERENCIA_INSEGURA", lintmod.lint(self.folder)["errors"])

    def test_case_collision_rejected(self):
        (self.folder / "a.md").write_text("um")
        (self.folder / "A.md").write_text("dois")
        if len(list(self.folder.glob("[aA].md"))) < 2:
            self.skipTest("Filesystem case-insensitive")
        self.assertIn("PATH_DUPLICADO_CASE_INSENSITIVE", lintmod.lint(self.folder)["errors"])

    def test_synthetic_credential_detected(self):
        # Constructed at runtime; not a real credential or plaintext secret fixture.
        fake = "sk-" + "proj-" + ("X" * 30)
        (self.folder / "risco.txt").write_text(fake, encoding="utf-8")
        self.assertIn("POSSIVEL_CREDENCIAL", lintmod.lint(self.folder)["errors"])

    def test_binary_outside_assets_rejected(self):
        (self.folder / "documento.pdf").write_bytes(b"%PDF synthetic fixture")
        self.assertIn("EXTENSAO_NAO_PERMITIDA", lintmod.lint(self.folder)["errors"])

    def test_duplicate_frontmatter_key_rejected(self):
        content = self.skill.read_text().replace("name: exemplo", "name: exemplo\nname: exemplo")
        self.skill.write_text(content, encoding="utf-8")
        self.assertFalse(lintmod.lint(self.folder)["pass"])

if __name__ == "__main__":
    unittest.main()
