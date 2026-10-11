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
    # Review pós-build rodada 2 (fable): 3ª pessoa, verbos que faltavam, upsert, nome composto
    ("listar_clientes", "Lista os clientes e desativa os inativos", "escrita", "desativa"),
    ("listar_titulos", "Lista e liquida os títulos vencidos", "escrita", "liquida"),
    ("consultar_conta", "Consulta a conta e ativa o acesso à API", "escrita", "ativa"),
    ("listar_e_apagar_duplicados", "", "escrita", "apagar"),
    ("get_or_reset_token", "Gets the token; resets it when expired", "escrita", "reset"),
    ("obter_cliente", "Cliente criado ou atualizado conforme os dados informados", "escrita", "upsert: particípio perto de ou"),
    ("listar_e_xpto_registros", "", "indeterminada", "nome composto com verbo desconhecido"),
    ("get_or_frobnicate", "", "indeterminada", "nome composto com verbo desconhecido"),
    ("listar_cobrancas", "", "leitura", "cobranças é substantivo"),
    ("listar_agendamentos", "", "leitura", "agendamentos é substantivo"),
    # Review pós-build rodada 2 (codex)
    ("listar_titulos", "Lista os títulos e começa a pagar os vencidos", "escrita", "a pagar sem 'contas' antes é verbo"),
    ("obter_cliente", "O cliente é rapidamente atualizado com os dados", "escrita", "advérbio entre auxiliar e particípio"),
    ("listar_titulos_a_receber", "Lista os títulos a receber", "leitura", "títulos a receber é nome de conta"),
    # Review pós-build rodada 3 (codex): forma exata terminada em -ida/-ado não é particípio
    ("consultar_titulos", "Consulta títulos; liquida os vencidos", "escrita", "liquida sem auxiliar antes"),
    # Review pós-build rodada 4 (codex): camelCase e voz passiva com trecho intercalado
    ("listOrCreateCustomer", "", "escrita", "camelCase: create"),
    ("getCustomer", "", "leitura", "camelCase: get"),
    ("listInvoices", "", "leitura", "camelCase: list"),
    ("GetOrUpdateHTTPStatus", "", "escrita", "PascalCase + sigla: update"),
    ("obter_cliente", "O cliente é, quando necessário, atualizado", "escrita", "auxiliar longe do particípio"),
    ("obter_cliente", "The customer is, when needed, updated", "escrita", "auxiliar longe do particípio (EN)"),
    ("listar_notas", "Lista as notas emitidas e canceladas no período", "escrita", "canceladas não vem colado a substantivo (lado seguro)"),
    # Review pós-build rodada 4 (auditor): read como palavra exata e condicionais
    ("readd_customer", "", "indeterminada", "readd não é read"),
    ("readjust_prices", "", "indeterminada", "readjust não é read"),
    ("read_customer", "", "leitura", "read exato"),
    ("listar_clientes", "Lista clientes; cliente criado caso inexistente", "escrita", "caso inexistente"),
    ("get_customer", "Returns the customer; created if it doesn't exist", "escrita", "doesn't exist"),
    ("listar_clientes", "Lista clientes; cliente cadastrado quando necessário", "escrita", "quando necessário"),
    ("listar_notas", "Lista as notas emitidas", "leitura", "sem condição: particípio segue adjetivo"),
    # Review pós-build rodada 5 (auditor): isenção de particípio vira lista de permissão
    ("listar_clientes", "Lista clientes; cliente criado quando não encontrado", "escrita", "palavra de condição"),
    ("obter_cliente_existente", "Devolve o cliente; cliente criado em caso contrário", "escrita", "condição no nome + descrição juntos"),
    ("listar_clientes", "Lista os clientes cadastrados", "leitura", "cadastrados colado a clientes"),
    ("listar_registros", "Lista registros já atualizados pelo sistema", "escrita", "atualizados não colado a substantivo"),
    # Review pós-build rodada 6 (codex): substantivo e particípio em trechos diferentes
    ("listar_clientes", "Lista clientes. Criado um cliente de teste a cada chamada.", "escrita", "ponto separa"),
    ("listar_notas", "Lista as notas, emitidas na hora", "escrita", "vírgula separa"),
    ("listar_notas", "Lista as notas emitidas.", "leitura", "mesmo trecho"),
    # Desconhecido
    ("conta_azul_status", "", "indeterminada", "sem termo conhecido"),
]


class TestClassificador(unittest.TestCase):
    def test_casos_de_fronteira(self):
        for nome, desc, esperado, porque in CASOS:
            with self.subTest(nome=nome, desc=desc):
                self.assertEqual(cf.classificar(nome, desc)[0], esperado, porque)

    def test_auxiliar_em_unicode_decomposto(self):
        """Review rodada 5 (codex): 'é' em NFD (e + acento combinante) tem de contar como auxiliar."""
        import unicodedata
        for forma in ("NFC", "NFD"):
            with self.subTest(forma=forma):
                d = unicodedata.normalize(forma, "O cliente é, quando possível, atualizado")
                self.assertEqual(cf.classificar("obter_cliente", d)[0], "escrita")

    def test_prosa_segue_a_ordem_do_script(self):
        """Review rodada 5 (codex): a prosa tem de mandar ler o auxiliar e o camelCase ANTES de tirar acento e caixa."""
        md = (RAIZ / "references" / "CLASSIFICACAO_FERRAMENTAS.md").read_text(encoding="utf-8")
        i_aux, i_camel, i_acento = md.find("Antes de mexer no texto"), md.find("camelCase"), md.find("tire os acentos")
        self.assertTrue(0 <= i_aux < i_camel < i_acento, (i_aux, i_camel, i_acento))

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
            "CONJUNCOES_ALTERNATIVA": list(cf.CONJUNCOES_ALTERNATIVA),
            "CONJUNCOES_NO_NOME": list(cf.CONJUNCOES_NO_NOME),
            "ANTES_DE_NOME_DE_CONTA": list(cf.ANTES_DE_NOME_DE_CONTA),
            "RADICAIS_CONDICIONAIS": list(cf.RADICAIS_CONDICIONAIS),
            "PALAVRAS_DE_CONDICAO": list(cf.PALAVRAS_DE_CONDICAO),
            "SUBSTANTIVOS_DO_DOMINIO": list(cf.SUBSTANTIVOS_DO_DOMINIO),
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
