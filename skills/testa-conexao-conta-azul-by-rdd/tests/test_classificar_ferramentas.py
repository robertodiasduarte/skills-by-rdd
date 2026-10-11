"""Testes do classificador leitura × escrita. Cada caso tem a classe esperada ESCRITA À MÃO (não é saída do script).

Rodar: python3 -B -m unittest discover -s tests -p "test_*.py"   (a partir da raiz da skill)
"""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import classificar_ferramentas as cf  # noqa: E402

# (nome, descrição, classe esperada, por quê)
CASOS = [
    # Fronteiras do domínio
    ("baixar_xml_nfe", "", "indeterminada", "baixar = dar baixa (quitação) ou download: nunca executar"),
    ("listar_baixas", "", "indeterminada", "baixa é quitação; na dúvida, indeterminada"),
    ("get_or_create_cliente", "", "escrita", "escrita vence leitura no mesmo nome"),
    ("listar_titulos_baixados", "", "indeterminada", "baix vale também no particípio"),
    # Verbo flexionado na descrição contradizendo o nome
    ("listar_clientes", "Lista os clientes e cria um novo se não existir", "escrita", "cria"),
    ("obter_token", "Gera um novo token de acesso", "escrita", "gera"),
    ("buscar_venda", "Busca a venda e atualiza o status", "escrita", "atualiza"),
    ("consultar_pedido", "Consulta e cancela o pedido", "escrita", "cancela"),
    ("get_invoice", "Creates an invoice if missing", "escrita", "creates"),
    ("listar_pessoas", "Lista pessoas; com o parâmetro force, registra uma nova", "escrita", "registra"),
    # Substantivo de ação
    ("criacao_cliente", "", "escrita", "criação"),
    ("exclusao_lancamento", "", "escrita", "exclusão"),
    # Pedaço de palavra NÃO casa (o erro da 1ª versão)
    ("reverter_conciliacao", "", "escrita", "reverter é escrita; 'ver' dentro dele não é leitura"),
    ("converter_orcamento_em_venda", "", "escrita", "converter"),
    ("enviar_lista_cobranca", "", "escrita", "enviar; 'lista' depois não salva"),
    ("adicionar_blacklist", "", "escrita", "adicionar"),
    ("verificar_status", "", "indeterminada", "'ver' só casa a palavra inteira"),
    ("obter_versao_api", "", "leitura", "'versao' não é 'ver'"),
    ("forget_cliente", "", "indeterminada", "'get' dentro de forget não é leitura"),
    ("postergar_vencimento", "", "indeterminada", "post só casa a palavra inteira; sem leitura, indeterminada"),
    # Leitura legítima
    ("listar_notas", "Lista as notas emitidas", "leitura", "particípio adjetivo não é verbo"),
    ("listagem_clientes", "", "leitura", "radical list"),
    ("listar_contas_a_pagar", "Lista as contas a pagar em aberto", "leitura", "contas a pagar é nome de conta"),
    ("listar_pagamentos", "Lista os pagamentos realizados no período", "leitura", "pagamentos não é o verbo pagar"),
    ("buscar_lancamentos", "", "leitura", "lançamentos não é o verbo lançar"),
    ("get_conta_conectada", "Retorna os dados da empresa conectada", "leitura", "get"),
    ("search_products", "Searches products by name", "leitura", "search"),
    # Inglês e português, escrita
    ("delete_customer", "", "escrita", "delete"),
    ("update_sale", "", "escrita", "update"),
    ("dar_baixa_titulo", "", "indeterminada", "baixa"),
    ("pagar_titulo", "", "escrita", "pagar como verbo"),
    # Voz passiva e criação condicional (R1 do review pós-build)
    ("listar_clientes", "Lista os clientes; se o CPF não existir, um novo cliente é criado", "escrita", "é criado = passiva"),
    ("listar_clientes", "Lista clientes; cliente criado automaticamente se não existir", "escrita", "criação condicional"),
    ("get_customers", "Returns customers; a new one is created if missing", "escrita", "is created = passiva"),
    # Verbos que faltavam (R2 do review pós-build)
    ("get_or_register_customer", "", "escrita", "register"),
    ("fetch_customer", "Fetches the customer; registers it if absent", "escrita", "registers"),
    ("listar_titulos", "Lista e autoriza a pagar os títulos vencidos", "escrita", "autoriza"),
    ("consultar_e_conciliar", "", "escrita", "conciliar"),
    ("buscar_e_arquivar", "", "escrita", "arquivar"),
    # Substantivos de leitura que NÃO podem virar escrita
    ("listar_arquivos", "", "leitura", "arquivo é substantivo"),
    ("listar_clientes_ativos", "", "leitura", "ativo é adjetivo"),
    ("buscar_conciliacoes", "", "leitura", "conciliação é substantivo"),
    ("consultar_valor_liquido", "", "leitura", "líquido é adjetivo"),
    # Review pós-build rodada 1 (kimi): 3ª pessoa de verbos exatos
    ("listar_vendas", "Lista e fatura as vendas", "escrita", "fatura = 3ª pessoa de faturar"),
    ("get_invoice", "Gets the invoice and patches its status", "escrita", "patches"),
    ("listar_faturas", "", "leitura", "faturas (plural) é substantivo"),
    # Desconhecido
    ("conta_azul_status", "", "indeterminada", "sem termo conhecido"),
]


class TestClassificador(unittest.TestCase):
    def test_casos_de_fronteira(self):
        for nome, desc, esperado, porque in CASOS:
            with self.subTest(nome=nome, desc=desc):
                self.assertEqual(cf.classificar(nome, desc)[0], esperado, porque)

    def test_cli_deterministico(self):
        entrada = json.dumps([{"nome": n, "descricao": d} for n, d, _, _ in CASOS], ensure_ascii=False)
        script = RAIZ / "scripts" / "classificar_ferramentas.py"
        saidas = [subprocess.run([sys.executable, "-I", "-B", str(script)], input=entrada,
                                 capture_output=True, text=True, check=True).stdout for _ in range(2)]
        self.assertEqual(saidas[0], saidas[1])
        self.assertEqual([x["classe"] for x in json.loads(saidas[0])], [c for _, _, c, _ in CASOS])

    def test_cli_entrada_invalida(self):
        script = RAIZ / "scripts" / "classificar_ferramentas.py"
        for entrada in ('{"nome": "x"}', '[{"nome": "x", "descricao": 123}]', '[{"nome": 1}]'):
            with self.subTest(entrada=entrada):
                r = subprocess.run([sys.executable, "-I", "-B", str(script)], input=entrada, capture_output=True, text=True)
                self.assertEqual(r.returncode, 2)
                self.assertIn("erro", json.loads(r.stdout))
                self.assertNotIn("Traceback", r.stderr)

    def test_paridade_com_a_tabela_em_prosa(self):
        """CLASSIFICACAO_FERRAMENTAS.md é o que o modelo segue quando não pode rodar o script: tem de ser igual."""
        md = (RAIZ / "references" / "CLASSIFICACAO_FERRAMENTAS.md").read_text(encoding="utf-8")
        m = re.search(r"<!-- LISTAS:INICIO -->\s*```json\s*(\{.*?\})\s*```\s*<!-- LISTAS:FIM -->", md, re.S)
        self.assertIsNotNone(m, "bloco de listas ausente em CLASSIFICACAO_FERRAMENTAS.md")
        listas = json.loads(m.group(1))
        self.assertEqual(listas, {
            "RADICAIS_ESCRITA": list(cf.RADICAIS_ESCRITA),
            "EXATOS_ESCRITA": list(cf.EXATOS_ESCRITA),
            "RADICAIS_LEITURA": list(cf.RADICAIS_LEITURA),
            "EXATOS_LEITURA": list(cf.EXATOS_LEITURA),
            "RADICAL_INDETERMINADO": cf.RADICAL_INDETERMINADO,
            "SUFIXOS_PARTICIPIO": list(cf.SUFIXOS_PARTICIPIO),
            "NOME_DE_CONTA": list(cf.NOME_DE_CONTA),
            "AUXILIARES": list(cf.AUXILIARES),
            "MARCADORES_CONDICIONAIS": list(cf.MARCADORES_CONDICIONAIS),
        })

    def test_regra_fail_closed_identica(self):
        regra = lambda p: [l.strip() for l in p.read_text(encoding="utf-8").splitlines() if l.strip().startswith("REGRA FAIL-CLOSED:")]
        a = regra(RAIZ / "SKILL.md")
        b = regra(RAIZ / "references" / "CLASSIFICACAO_FERRAMENTAS.md")
        self.assertEqual(len(a), 1)
        self.assertEqual(a, b)

    def test_recusa_canonica_igual_ao_eval(self):
        sk = (RAIZ / "SKILL.md").read_text(encoding="utf-8")
        secao = re.search(r"^## Texto canônico de recusa\s*\n(.*?)(?=^## |\Z)", sk, re.M | re.S)
        self.assertIsNotNone(secao)
        frases = [f for f in re.findall(r"“([^”]+)”", secao.group(1)) if all(t in f.lower() for t in ("client_secret", "token", "senha"))]
        self.assertEqual(len(frases), 1)
        casos = {c["id"]: c for c in json.loads((RAIZ / "evals" / "cases.json").read_text(encoding="utf-8"))["cases"]}
        self.assertEqual(casos["E6"]["recusa_canonica"], frases[0])
        for c in ("E2", "E5"):
            self.assertEqual(casos[c]["chamadas_escrita_esperadas"], 0)


if __name__ == "__main__":
    unittest.main()
