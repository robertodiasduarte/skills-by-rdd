"""Controles Omie da meta-skill: perfil, escrita, degradacao e o script de totalizacao.

Os controles herdados (scope_gate, lint_bundle) ficam em test_controls.py, copia do pai.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
ASSETS = ROOT / "assets" / "omie"
sys.path.insert(0, str(SCRIPTS))
import lint_bundle_omie as lo  # noqa: E402
import scope_gate as gate  # noqa: E402

CATALOGO = json.loads((ASSETS / "catalogo_leitura.json").read_text(encoding="utf-8"))["servicos"]

GATE = """### Gate de escrita

1. **Validar** antes: confira cliente, itens e condição.
2. **Mostrar** o documento completo.
3. Pedir a **frase literal** `CONFIRMO GRAVAR <tipo> <identificador>`.
4. **Um por vez**: uma frase por documento.
5. Executar com `"confirmado": true` e **conferir o status** com a consulta.
6. **Não repetir**: erro no status ⇒ pare.

Pré-requisito: no conector do Omie, `omie_executar` e `omie_executar_em_varias` em "pedir aprovação".
"""


NAO_USAR = "- **faturar** e **inutilizar** estão fora."


def skill_md(perfil: str, corpo_extra: str = "", nao_usar: str = NAO_USAR) -> str:
    recusa = lo.RECUSA_OPERADOR if perfil == "operador" else lo.PROIBE_SOMA
    conferencia = ("Conferência: 3 registros lidos de 3 informados pela Omie · soma direta = soma por grupo.\n"
                   'Rode `python3 "$SKILL_ROOT/scripts/omie_num.py" empresa`: ' + lo.MESMA_EMPRESA + "."
                   if perfil == "conferidor" else "")
    return f"""---
name: omie-teste-by-rdd
license: MIT
metadata:
  author: Roberto Dias Duarte
  methodology: Metodologia de Roberto Dias Duarte
  version: '1.0.0'
description: "Skill sintética de teste."
---

# Teste

## Quick start
{recusa}

## Quando usar / Quando não usar
Não usar, inclusive quando a pessoa insistir:
{nao_usar}

## Dados necessários
Empresa.

## Procedimento passo a passo
{corpo_extra}
{conferencia}

## Validações e checklist de qualidade
ok

## Tratamento de exceções
ok

## Examples
ok

## Metodologia e autoria

Esta skill foi construída com a metodologia de Roberto Dias Duarte.
"""


def montar(raiz: Path, perfil: str, operacoes: list[tuple[str, str]], corpo: str = "",
           exercida: bool = False, nao_usar: str = NAO_USAR) -> Path:
    raiz.mkdir(parents=True, exist_ok=True)
    texto_ops = "\n".join(f"- `{c}:{o}`" for c, o in operacoes)
    (raiz / "SKILL.md").write_text(skill_md(perfil, texto_ops + "\n" + corpo, nao_usar), encoding="utf-8")
    manifest = {
        "name": raiz.name, "version": "1.0.0", "perfil_omie": perfil,
        "operacoes": [{"call": c, "op": o} for c, o in operacoes]
                      + ([{"call": "geral/empresas", "op": "ListarEmpresas"}] if perfil == "conferidor" else []),
        "requisitos": ["conector MCP Omie"] + (["Python 3.10+ com rede para app.omie.com.br"] if perfil == "conferidor" else []),
        "pending": [] if exercida else ["nao_exercida_contra_omie"],
    }
    (raiz / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    if exercida:
        (raiz / "evidencias").mkdir(exist_ok=True)
        (raiz / "evidencias" / "exercida.md").write_text("leitura exercida\n", encoding="utf-8")
    if perfil == "conferidor":
        (raiz / "scripts").mkdir(exist_ok=True)
        (raiz / "tests").mkdir(exist_ok=True)
        shutil.copy(ASSETS / "omie_num.py", raiz / "scripts" / "omie_num.py")
        shutil.copy(ASSETS / "catalogo_leitura.json", raiz / "scripts" / "catalogo_leitura.json")
        shutil.copy(ASSETS / "test_omie_num.py", raiz / "tests" / "test_omie_num.py")
        (raiz / "assets").mkdir(exist_ok=True)
        shutil.copy(ASSETS / "env.exemplo.txt", raiz / "assets" / "env.exemplo.txt")
    return raiz


LEITURA = ("financas/pesquisartitulos", "PesquisarLancamentos")
INCLUIR = ("produtos/pedido", "IncluirPedido")


class TempDir(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()


class PerfilTests(TempDir):
    BASE = {"schema": 1, "totaliza": True, "executa_python_com_rede": True, "perfil": "conferidor",
            "multi_empresa": False, "aprovacao_por_ferramenta": "declarada_sim", "mcp_disponivel": True}

    def escopo_com(self, perfil: dict) -> dict:
        escopo = json.loads((ROOT / "assets" / "escopo.template.json").read_text(encoding="utf-8"))
        escopo["restricoes"] = [lo.restricao(perfil)]
        return escopo

    def test_derivacao(self):
        casos = [((True, True, True), "conferidor"), ((True, False, True), "operador"),
                 ((False, True, True), "operador"), ((True, True, False), "operador")]
        for (totaliza, python, mcp), esperado in casos:
            p = dict(self.BASE, totaliza=totaliza, executa_python_com_rede=python, mcp_disponivel=mcp)
            with self.subTest(p=(totaliza, python, mcp)):
                self.assertEqual(lo.perfil_derivado(p), esperado)

    def test_perfil_valido_amarrado_ao_escopo(self):
        self.assertEqual(lo.checar_perfil(self.BASE, self.escopo_com(self.BASE)), [])

    def test_perfil_escolhido_e_nao_derivado(self):
        p = dict(self.BASE, executa_python_com_rede=False)
        self.assertIn("PERFIL_NAO_DERIVADO", lo.checar_perfil(p, self.escopo_com(p)))

    def test_perfil_alterado_depois_do_escopo(self):
        escopo = self.escopo_com(self.BASE)
        alterado = dict(self.BASE, multi_empresa=True)
        self.assertIn("PERFIL_FORA_DO_ESCOPO", lo.checar_perfil(alterado, escopo))

    def test_campo_extra_ou_tipo_errado(self):
        self.assertEqual(lo.checar_perfil(dict(self.BASE, extra=1), {}), ["PERFIL_CAMPOS_INVALIDOS"])
        self.assertEqual(lo.checar_perfil(dict(self.BASE, totaliza="sim"), {}), ["PERFIL_CAMPOS_INVALIDOS"])

    def test_mudar_perfil_invalida_a_confirmacao_herdada(self):
        operador = dict(self.BASE, executa_python_com_rede=False, perfil="operador")
        escopo = json.loads((ROOT / "assets" / "escopo.template.json").read_text(encoding="utf-8"))
        escopo.update({"nome": "omie-teste-by-rdd", "tema": "atrasos", "objetivo": "ver atrasos",
                       "publico": "contador", "jurisdicao": "Brasil", "revisao_humana": "contador",
                       "cobre": ["títulos atrasados"], "recusa": ["faturar", "inutilizar"],
                       "entradas": ["período"], "saidas": ["lista"], "criterios_aceite": ["lista conferida"],
                       "restricoes": [lo.restricao(operador)]})
        aprovacao = {"origem": "usuario", "escopo_id": escopo["id"], "revisao": escopo["revisao"],
                     "sha256_escopo": gate.digest(escopo), "texto": gate.confirmation_text(escopo),
                     "apos_apresentacao": True, "mensagem_id": "m1"}
        self.assertTrue(gate.check_approval(escopo, aprovacao)["geracao_autorizada"])
        trocado = copy.deepcopy(escopo)
        trocado["restricoes"] = [lo.restricao(self.BASE)]
        with self.assertRaises(gate.GateError):
            gate.check_approval(trocado, aprovacao)

    def test_cli_cruza_sidecar_com_o_bundle(self):
        operador = dict(self.BASE, executa_python_com_rede=False, perfil="operador")
        arq, esc = self.tmp / "perfil_omie.json", self.tmp / "escopo.json"
        arq.write_text(json.dumps(operador), encoding="utf-8")
        esc.write_text(json.dumps(self.escopo_com(operador)), encoding="utf-8")
        raiz = montar(self.tmp / "b", "conferidor", [LEITURA])
        r = subprocess.run([sys.executable, "-B", str(SCRIPTS / "lint_bundle_omie.py"), "--root", str(raiz),
                            "--perfil-arquivo", str(arq), "--escopo", str(esc)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("PERFIL_DIVERGENTE_DO_MANIFEST", json.loads(r.stdout)["errors"])

    def test_restricao_pela_cli(self):
        arq = self.tmp / "perfil_omie.json"
        arq.write_text(json.dumps(self.BASE), encoding="utf-8")
        out = subprocess.run([sys.executable, "-B", str(SCRIPTS / "lint_bundle_omie.py"), "--restricao", str(arq)],
                             capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(out, lo.restricao(self.BASE))


class EscritaTests(TempDir):
    def erros(self, raiz, perfil=None):
        return lo.lint(raiz, perfil, CATALOGO)

    def test_operador_so_leitura_aprovado(self):
        self.assertEqual(self.erros(montar(self.tmp / "a", "operador", [LEITURA])), [])

    def test_operador_com_escrita_completa_aprovado(self):
        self.assertEqual(self.erros(montar(self.tmp / "a", "operador", [LEITURA, INCLUIR], GATE)), [])

    def test_escrita_sem_gate(self):
        corpo = GATE.replace("### Gate de escrita", "### Passos")
        self.assertIn("ESCRITA_SEM_GATE", self.erros(montar(self.tmp / "a", "operador", [INCLUIR], corpo)))

    def test_gate_fora_de_ordem(self):
        linhas = GATE.splitlines()
        trocado = "\n".join(linhas[:2] + [linhas[3].replace("2.", "1."), linhas[2].replace("1.", "2.")] + linhas[4:])
        self.assertIn("ESCRITA_SEM_GATE", self.erros(montar(self.tmp / "a", "operador", [INCLUIR], trocado)))

    def test_escrita_sem_confirmado(self):
        corpo = GATE.replace('`"confirmado": true`', "a confirmação")
        self.assertIn("ESCRITA_SEM_CONFIRMADO", self.erros(montar(self.tmp / "a", "operador", [INCLUIR], corpo)))

    def test_escrita_sem_prerequisito(self):
        corpo = GATE.replace('"pedir aprovação"', '"perguntar"')
        self.assertIn("PREREQ_APROVACAO_AUSENTE", self.erros(montar(self.tmp / "a", "operador", [INCLUIR], corpo)))

    def test_sem_fronteira_fiscal(self):
        raiz = montar(self.tmp / "a", "operador", [INCLUIR], GATE, nao_usar="nada a declarar.")
        self.assertIn("FRONTEIRA_FISCAL_AUSENTE", self.erros(raiz))

    def test_fronteira_so_vale_na_lista_abaixo_de_nao_usar(self):
        casos = {
            "radical na própria linha": ("faturar e inutilizar:", "- **faturar** e **inutilizar** estão fora.",
                                         {"FRONTEIRA_FISCAL_FORA_DA_LISTA"}),
            "sem lista": ("", "faturar e inutilizar estão fora.",
                          {"FRONTEIRA_FISCAL_AUSENTE", "FRONTEIRA_FISCAL_FORA_DA_LISTA"}),
            "sem fiscal e sem lista": ("", "nada a declarar.", {"FRONTEIRA_FISCAL_AUSENTE"}),
            "lista com linha em branco antes": ("", "\n- **faturar** e **inutilizar** estão fora.",
                                                {"FRONTEIRA_FISCAL_AUSENTE", "FRONTEIRA_FISCAL_FORA_DA_LISTA"}),
            "continuação indentada": ("", "- emitir documento fiscal:\n  **faturar**, **inutilizar** numeração.", set()),
            "flexão e maiúscula": ("", "- Faturamento e Inutilização de numeração.", set()),
        }
        for nome, (sufixo, lista, esperado) in casos.items():
            with self.subTest(nome):
                raiz = montar(self.tmp / nome, "operador", [LEITURA], nao_usar=lista)
                skill = raiz / "SKILL.md"
                skill.write_text(skill.read_text(encoding="utf-8").replace(
                    "Não usar, inclusive quando a pessoa insistir:", "Nao usar, inclusive quando a pessoa insistir " + sufixo),
                    encoding="utf-8")
                erros = {e for e in self.erros(raiz) if e.startswith("FRONTEIRA")}
                self.assertEqual(erros, esperado)

    def test_texto_nao_utf8_reprova_e_binario_permitido_passa(self):
        raiz = montar(self.tmp / "a", "operador", [LEITURA])
        (raiz / "assets").mkdir()
        (raiz / "assets" / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n\0\0\0\rIHDR\xff")
        self.assertEqual(self.erros(raiz), [])
        for nome, dados in {"assets/nota.txt": "olá".encode("latin-1"), "references/x.md": "oi\0".encode(),
                            "logo.png": b"\x89PNG\0\xff"}.items():
            with self.subTest(nome):
                alvo = raiz / nome
                alvo.parent.mkdir(exist_ok=True)
                alvo.write_bytes(dados)
                self.assertIn("TEXTO_NAO_UTF8", self.erros(raiz))
                alvo.unlink()

    def test_faturar_declarado(self):
        raiz = montar(self.tmp / "a", "operador", [("produtos/pedidovendafat", "FaturarPedidoVenda")], GATE)
        self.assertIn("FATURAR_NO_ESCOPO", self.erros(raiz))

    def test_escrita_fora_da_antiga_denylist(self):
        raiz = montar(self.tmp / "a", "operador", [("produtos/op", "ConcluirOrdemProducao")])
        self.assertIn("ESCRITA_SEM_GATE", self.erros(raiz))

    def test_nome_de_leitura_fora_do_catalogo_conta_como_escrita(self):
        self.assertEqual(lo.classificar(CATALOGO, "financas/pesquisartitulos", "ListarNovidadeSemCatalogo"), "escrita")

    def test_deprecated_recusada(self):
        raiz = montar(self.tmp / "a", "operador", [("financas/pesquisartitulos", "ObterURLBoleto")])
        self.assertIn("OPERACAO_DEPRECATED", self.erros(raiz))

    def test_servico_fora_do_catalogo(self):
        raiz = montar(self.tmp / "a", "operador", [("geral/auditoria", "ListarAuditoriaAlteracoes")])
        self.assertIn("OPERACAO_FORA_DO_CATALOGO", self.erros(raiz))

    def test_operacao_no_texto_nao_declarada(self):
        raiz = montar(self.tmp / "a", "operador", [LEITURA], "Depois chame `servicos/os:ListarOS`.")
        self.assertIn("OPERACAO_NAO_DECLARADA", self.erros(raiz))

    def test_metodo_citado_sem_endereco(self):
        raiz = montar(self.tmp / "a", "operador", [("geral/clientes", "ListarClientes")], "Depois chame `IncluirPedido` na etapa 10.")
        self.assertIn("OPERACAO_NAO_DECLARADA", self.erros(raiz))

    def test_operacao_em_json_nao_declarada(self):
        corpo = 'Chame `omie_executar` com `{"call": "produtos/pedido", "op": "IncluirPedido"}`.'
        raiz = montar(self.tmp / "a", "operador", [("geral/clientes", "ListarClientes")], corpo)
        self.assertIn("OPERACAO_NAO_DECLARADA", self.erros(raiz))

    def test_operacao_em_json_fora_do_catalogo(self):
        corpo = 'Chame `omie_executar` com `{"call": "geral/auditoria", "op": "ListarAuditoriaAlteracoes"}`.'
        raiz = montar(self.tmp / "a", "operador", [LEITURA], corpo)
        self.assertIn("OPERACAO_NAO_DECLARADA", self.erros(raiz))

    def test_verbo_de_escrita_fora_do_catalogo_citado_solto(self):
        corpo = "Depois de conferir, chame LancarRecebimentoEmLote pelo omie_executar."
        raiz = montar(self.tmp / "a", "conferidor", [LEITURA], corpo)
        self.assertIn("OPERACAO_NAO_DECLARADA", self.erros(raiz))

    def test_confirmado_sem_escrita(self):
        raiz = montar(self.tmp / "a", "operador", [LEITURA], 'Use `"confirmado": true`.')
        self.assertIn("CONFIRMADO_SEM_ESCRITA", self.erros(raiz))

    def test_varredura_do_catalogo(self):
        excecoes = []
        for call, entrada in CATALOGO.items():
            for op in entrada.get("leitura", []):
                if lo.classificar(CATALOGO, call, op) != "leitura":
                    excecoes.append(("leitura", call, op))
            for op, motivo in entrada.get("bloqueados", {}).items():
                esperado = "deprecated" if motivo == "deprecated" else "escrita"
                if lo.classificar(CATALOGO, call, op) != esperado:
                    excecoes.append(("bloqueado", call, op))
        self.assertEqual(excecoes, [])


class PerfilBundleTests(TempDir):
    def test_operador_com_script(self):
        raiz = montar(self.tmp / "a", "operador", [LEITURA])
        (raiz / "x.py").write_text("print(1)\n", encoding="utf-8")
        self.assertIn("PERFIL_OPERADOR_COM_SCRIPT", lo.lint(raiz, None, CATALOGO))

    def test_operador_sem_recusa(self):
        raiz = montar(self.tmp / "a", "operador", [LEITURA])
        skill = raiz / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace(lo.RECUSA_OPERADOR, "Não somo."), encoding="utf-8")
        self.assertIn("RECUSA_TOTALIZACAO_AUSENTE", lo.lint(raiz, None, CATALOGO))

    def test_conferidor_aprovado(self):
        self.assertEqual(lo.lint(montar(self.tmp / "a", "conferidor", [LEITURA]), None, CATALOGO), [])

    def test_conferidor_sem_modelo_de_env(self):
        raiz = montar(self.tmp / "a", "conferidor", [LEITURA])
        (raiz / "assets" / "env.exemplo.txt").unlink()
        self.assertIn("CONFERIDOR_SEM_SCRIPT", lo.lint(raiz, None, CATALOGO))

    def test_conferidor_script_alterado(self):
        raiz = montar(self.tmp / "a", "conferidor", [LEITURA])
        alvo = raiz / "scripts" / "omie_num.py"
        alvo.write_text(alvo.read_text(encoding="utf-8") + "\n# mexido\n", encoding="utf-8")
        self.assertIn("OMIE_NUM_DIVERGENTE", lo.lint(raiz, None, CATALOGO))

    def test_conferidor_sem_linha_de_conferencia(self):
        raiz = montar(self.tmp / "a", "conferidor", [LEITURA])
        skill = raiz / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace("informados pela Omie", "da Omie"), encoding="utf-8")
        self.assertIn("CONFERENCIA_LITERAL_AUSENTE", lo.lint(raiz, None, CATALOGO))

    def test_conferidor_sem_conferencia_de_empresa(self):
        raiz = montar(self.tmp / "a", "conferidor", [LEITURA])
        skill = raiz / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace(lo.MESMA_EMPRESA, "confira a empresa"), encoding="utf-8")
        self.assertIn("CONFERIDOR_SEM_CONFERENCIA_DE_EMPRESA", lo.lint(raiz, None, CATALOGO))

    def test_conferidor_sem_operacao_de_empresa(self):
        raiz = montar(self.tmp / "a", "conferidor", [LEITURA])
        m = json.loads((raiz / "manifest.json").read_text(encoding="utf-8"))
        m["operacoes"] = [o for o in m["operacoes"] if o["op"] != "ListarEmpresas"]
        (raiz / "manifest.json").write_text(json.dumps(m), encoding="utf-8")
        self.assertIn("CONFERIDOR_SEM_OPERACAO_DE_EMPRESA", lo.lint(raiz, None, CATALOGO))

    def test_conferidor_nao_grava(self):
        raiz = montar(self.tmp / "a", "conferidor", [LEITURA, INCLUIR], GATE)
        self.assertIn("CONFERIDOR_COM_ESCRITA", lo.lint(raiz, None, CATALOGO))

    def test_perfil_do_manifest_diverge_do_pedido(self):
        raiz = montar(self.tmp / "a", "operador", [LEITURA])
        self.assertIn("PERFIL_DIVERGENTE_DO_MANIFEST", lo.lint(raiz, "conferidor", CATALOGO))

    def test_versao_divergente(self):
        raiz = montar(self.tmp / "a", "operador", [LEITURA])
        m = json.loads((raiz / "manifest.json").read_text(encoding="utf-8"))
        m["version"] = "1.0.1"
        (raiz / "manifest.json").write_text(json.dumps(m), encoding="utf-8")
        self.assertIn("VERSAO_AUSENTE_OU_DIVERGENTE", lo.lint(raiz, None, CATALOGO))


class DegradacaoTests(TempDir):
    def test_sem_evidencia_exige_pending(self):
        raiz = montar(self.tmp / "a", "operador", [LEITURA])
        m = json.loads((raiz / "manifest.json").read_text(encoding="utf-8"))
        m["pending"] = []
        (raiz / "manifest.json").write_text(json.dumps(m), encoding="utf-8")
        self.assertIn("PENDING_NAO_EXERCIDA_AUSENTE", lo.lint(raiz, None, CATALOGO))

    def test_evidencia_e_pending_se_contradizem(self):
        raiz = montar(self.tmp / "a", "operador", [LEITURA], exercida=True)
        m = json.loads((raiz / "manifest.json").read_text(encoding="utf-8"))
        m["pending"] = ["nao_exercida_contra_omie"]
        (raiz / "manifest.json").write_text(json.dumps(m), encoding="utf-8")
        self.assertIn("PENDING_CONTRADIZ_EVIDENCIA", lo.lint(raiz, None, CATALOGO))

    def test_sem_mcp_quer_somar_vira_operador(self):
        p = dict(PerfilTests.BASE, mcp_disponivel=False)
        self.assertEqual(lo.perfil_derivado(p), "operador")

    def test_cli_reprova_com_exit_2(self):
        raiz = montar(self.tmp / "a", "operador", [INCLUIR])
        r = subprocess.run([sys.executable, "-B", str(SCRIPTS / "lint_bundle_omie.py"), "--root", str(raiz)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("ESCRITA_SEM_GATE", json.loads(r.stdout)["errors"])


EXEMPLOS = ROOT.parent


@unittest.skipUnless((EXEMPLOS / "omie-atrasos-conferidos-by-rdd").is_dir()
                     and (EXEMPLOS / "omie-tirar-pedido-by-rdd").is_dir(),
                     "exemplos reais ficam no repositório do catálogo, fora do pacote publicado")
class ExemplosAdulteradosTests(TempDir):
    """AT-004 sobre cópias adulteradas dos exemplos reais (achados do avaliador fresco, ciclo 1)."""

    def rodar(self, raiz: Path, perfil: str):
        r = subprocess.run([sys.executable, "-B", str(SCRIPTS / "lint_bundle_omie.py"), "--root", str(raiz),
                            "--perfil", perfil], capture_output=True, text=True)
        return r.returncode, json.loads(r.stdout)["errors"]

    def test_escrita_instruida_fora_do_skill_md_reprova(self):
        raiz = Path(shutil.copytree(EXEMPLOS / "omie-atrasos-conferidos-by-rdd", self.tmp / "atrasos"))
        (raiz / "assets" / "roteiro.md").write_text(
            "chame `financas/contareceber:LancarRecebimento` pelo omie_executar\n", encoding="utf-8")
        skill = raiz / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8")
                         + "\nPara baixar títulos pagos, siga `assets/roteiro.md`.\n", encoding="utf-8")
        rc, erros = self.rodar(raiz, "conferidor")
        self.assertEqual(rc, 2)
        self.assertTrue({"ESCRITA_SEM_GATE", "ESCRITA_SEM_CONFIRMADO", "OPERACAO_NAO_DECLARADA"} & set(erros), erros)

    def test_faturar_e_inutilizar_so_no_usar_para_reprova(self):
        raiz = Path(shutil.copytree(EXEMPLOS / "omie-tirar-pedido-by-rdd", self.tmp / "pedido"))
        skill = raiz / "SKILL.md"
        texto = skill.read_text(encoding="utf-8")
        tirar = "- **faturar** o pedido ou emitir NF-e, e **inutilizar** numeração"
        usar = "Usar para: incluir **um** pedido"
        self.assertIn(tirar, texto)
        self.assertIn(usar, texto)
        texto = texto.replace(tirar, "-").replace(usar, "Usar para: faturar e inutilizar numeração, e incluir **um** pedido")
        skill.write_text(texto, encoding="utf-8")
        rc, erros = self.rodar(raiz, "operador")
        self.assertEqual(rc, 2)
        self.assertIn("FRONTEIRA_FISCAL_AUSENTE", erros)

    # Ciclo 2 do avaliador: a fronteira é a LISTA logo abaixo de "Não usar"; radical fiscal fora dela reprova.
    LINHA_FISCAL = ("- **faturar** o pedido ou emitir NF-e, e **inutilizar** numeração — o servidor da Omie não "
                    "pede confirmação para essas ações; faça pelo Omie;\n")
    ULTIMO_NAO_USAR = "- análise comercial, de margem ou de crédito do cliente.\n"

    def pedido_sem_linha_fiscal(self) -> tuple[Path, str]:
        raiz = Path(shutil.copytree(EXEMPLOS / "omie-tirar-pedido-by-rdd", self.tmp / "pedido"))
        texto = (raiz / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(self.LINHA_FISCAL, texto)
        self.assertIn(self.ULTIMO_NAO_USAR, texto)
        return raiz, texto.replace(self.LINHA_FISCAL, "")

    def test_c3_usar_para_faturar_depois_da_lista_nao_usar_reprova(self):
        raiz, texto = self.pedido_sem_linha_fiscal()
        texto = texto.replace(self.ULTIMO_NAO_USAR, self.ULTIMO_NAO_USAR
                              + "Usar também para: faturar o pedido e inutilizar numeração quando a pessoa pedir.\n")
        (raiz / "SKILL.md").write_text(texto, encoding="utf-8")
        rc, erros = self.rodar(raiz, "operador")
        self.assertEqual(rc, 2)
        self.assertIn("FRONTEIRA_FISCAL_AUSENTE", erros)
        self.assertIn("FRONTEIRA_FISCAL_FORA_DA_LISTA", erros)

    def test_c4_nao_usar_parentetico_dentro_de_usar_para_reprova(self):
        raiz, texto = self.pedido_sem_linha_fiscal()
        usar = "Usar para: incluir **um** pedido"
        self.assertIn(usar, texto)
        texto = texto.replace(usar, "Usar para (não usar sem cliente cadastrado): faturar e inutilizar numeração, "
                                    "e incluir **um** pedido")
        (raiz / "SKILL.md").write_text(texto, encoding="utf-8")
        rc, erros = self.rodar(raiz, "operador")
        self.assertEqual(rc, 2)
        self.assertIn("FRONTEIRA_FISCAL_AUSENTE", erros)
        self.assertIn("FRONTEIRA_FISCAL_FORA_DA_LISTA", erros)

    def test_c5_controle_linha_fiscal_no_fim_da_lista_aprova(self):
        raiz, texto = self.pedido_sem_linha_fiscal()
        texto = texto.replace(self.ULTIMO_NAO_USAR, self.ULTIMO_NAO_USAR.replace(".\n", ";\n")
                              + self.LINHA_FISCAL.replace(";\n", ".\n"))
        (raiz / "SKILL.md").write_text(texto, encoding="utf-8")
        self.assertEqual(self.rodar(raiz, "operador"), (0, []))

    def test_h7_escrita_em_md_utf16_reprova(self):
        raiz = Path(shutil.copytree(EXEMPLOS / "omie-atrasos-conferidos-by-rdd", self.tmp / "atrasos"))
        conteudo = "Para baixar, chame `financas/contareceber:LancarRecebimento` pelo omie_executar.\n"
        (raiz / "assets" / "baixa.md").write_bytes(conteudo.encode("utf-16"))
        self.assertIn(b"\0", (raiz / "assets" / "baixa.md").read_bytes())
        skill = raiz / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\nBaixas: `assets/baixa.md`.\n", encoding="utf-8")
        rc, erros = self.rodar(raiz, "conferidor")
        self.assertEqual(rc, 2)
        self.assertIn("TEXTO_NAO_UTF8", erros)


def load_tests(loader, tests, pattern):
    """Inclui os testes do omie_num.py (o mesmo arquivo que vai para as skills Conferidor)."""
    spec = importlib.util.spec_from_file_location("test_omie_num", ASSETS / "test_omie_num.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    tests.addTests(loader.loadTestsFromModule(mod))
    return tests


if __name__ == "__main__":
    unittest.main()
