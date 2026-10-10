"""Testes do omie_num.py com servidor HTTP local (sem acesso a Omie).

Roda igual na skill geradora (assets/omie/) e nas skills Conferidor geradas
(tests/ ao lado de scripts/): o script e procurado nos dois lugares.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

AQUI = Path(__file__).resolve().parent
for candidato in (AQUI / "omie_num.py", AQUI.parent / "scripts" / "omie_num.py"):
    if candidato.is_file():
        SCRIPT = candidato
        break
else:
    raise FileNotFoundError("omie_num.py nao encontrado ao lado nem em ../scripts/")

spec = importlib.util.spec_from_file_location("omie_num", SCRIPT)
num = importlib.util.module_from_spec(spec)
spec.loader.exec_module(num)

CHAVE, SEGREDO = "chave-de-teste-123", "segredo-de-teste-456"


class Servidor:
    """Devolve, por pagina, o que o teste configurar em `paginas`."""

    def __init__(self):
        self.paginas: list[dict] = []
        self.erro: tuple[int, dict] | None = None
        self.chamadas: list[dict] = []
        dono = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                corpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                dono.chamadas.append(corpo)
                if dono.erro:
                    codigo, payload = dono.erro
                else:
                    pagina = corpo["param"][0].get("nPagina", 1)
                    codigo, payload = 200, dono.paginas[pagina - 1]
                dados = json.dumps(payload).encode()
                self.send_response(codigo)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(dados)))
                self.end_headers()
                self.wfile.write(dados)

        self.httpd = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.httpd.server_port}/api/v1/"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def fechar(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def pagina(registros, total_registros, total_paginas):
    return {"nPagina": 1, "nTotPaginas": total_paginas, "nRegistros": len(registros),
            "nTotRegistros": total_registros, "titulosEncontrados": registros}


def titulo(valor, natureza="R"):
    return {"cabecTitulo": {"nValorTitulo": valor, "cNatureza": natureza}, "resumo": {"nValAberto": valor}}


class Base(unittest.TestCase):
    SERVICO, METODO = "financas/pesquisartitulos", "PesquisarLancamentos"
    PARAM = {"nPagina": 1, "nRegPorPagina": 50, "cStatus": "ATRASADO"}

    def setUp(self):
        self.srv = Servidor()
        self.env = mock_env({"OMIE_BASE_URL": self.srv.url})
        self.env.__enter__()
        self.catalogo = num.load_catalog()
        self.cliente = num.Client(CHAVE, SEGREDO, pause=0, waits=())

    def tearDown(self):
        self.env.__exit__(None, None, None)
        self.srv.fechar()

    def assert_sem_agregado(self, rc, out, motivo):
        self.assertEqual((rc, out["status"], out["motivo"]), (2, "divergente", motivo))
        self.assertFalse({"total", "grupos", "nota"} & set(out))
        self.assertEqual(set(out["conferencia"]), {"lidos", "informados"})

    def totalizar(self, agrupar=None):
        return num.totalizar(self.cliente, self.catalogo, self.SERVICO, self.METODO, self.PARAM,
                             "resumo.nValAberto", agrupar)


@contextlib.contextmanager
def mock_env(valores):
    antigos = {k: os.environ.get(k) for k in valores}
    os.environ.update(valores)
    try:
        yield
    finally:
        for k, v in antigos.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


class TotalTests(Base):
    def test_uma_pagina_ok(self):
        self.srv.paginas = [pagina([titulo(100.5), titulo("1.234,50")], 2, 1)]
        rc, out = self.totalizar()
        self.assertEqual(rc, 0)
        self.assertEqual(out["status"], "ok")
        self.assertEqual(out["total"], "1335.00")
        self.assertEqual(out["conferencia"]["lidos"], 2)
        self.assertEqual(out["conferencia"]["informados"], 2)
        self.assertEqual(out["conferencia"]["soma_direta"], out["conferencia"]["soma_por_particao"])
        self.assertEqual(out["conferencia"]["particao"], "pagina")

    def test_formatos_de_texto(self):
        casos = {"1.234,50": "1234.50", "1234,56": "1234.56", "10.5": "10.5", "-7": "-7"}
        for entrada, esperado in casos.items():
            with self.subTest(entrada=entrada):
                self.assertEqual(str(num.to_decimal(entrada)), esperado)
        for ambiguo in ("1.234", "10.500", "1,2,3", "abc"):
            with self.subTest(ambiguo=ambiguo):
                self.assertIsNone(num.to_decimal(ambiguo))

    def test_milhar_sem_centavos_nao_vira_total(self):
        self.srv.paginas = [pagina([titulo("1.234"), titulo(10)], 2, 1)]
        rc, out = self.totalizar()
        self.assert_sem_agregado(rc, out, "valor_nao_numerico")

    def test_cinco_paginas_e_o_teto_exato(self):
        self.srv.paginas = [pagina([titulo(10)], 5, 5) for _ in range(5)]
        rc, out = self.totalizar()
        self.assertEqual(rc, 0)
        self.assertEqual(out["total"], "50")
        self.assertEqual(out["memoria"]["paginas_lidas"], 5)

    def test_seis_paginas_trunca_e_nao_entrega_total(self):
        self.srv.paginas = [pagina([titulo(10)], 6, 6) for _ in range(6)]
        rc, out = self.totalizar()
        self.assert_sem_agregado(rc, out, "truncado")
        self.assertEqual(len(self.srv.chamadas), 5)

    def test_contagem_divergente(self):
        self.srv.paginas = [pagina([titulo(10), titulo(20)], 3, 1)]
        rc, out = self.totalizar()
        self.assert_sem_agregado(rc, out, "contagem")

    def test_valor_nao_numerico_nao_vira_zero(self):
        self.srv.paginas = [pagina([titulo(100), titulo("invalido")], 2, 1)]
        rc, out = self.totalizar()
        self.assert_sem_agregado(rc, out, "valor_nao_numerico")
        self.assertEqual(out["registros"], [1])

    def test_valor_ausente_tambem_diverge(self):
        self.srv.paginas = [pagina([titulo(100), {"cabecTitulo": {}}], 2, 1)]
        rc, out = self.totalizar()
        self.assert_sem_agregado(rc, out, "valor_nao_numerico")

    def test_valor_infinito_nao_vira_total(self):
        self.srv.paginas = [pagina([titulo(100), titulo(float("inf"))], 2, 1)]
        rc, out = self.totalizar()
        self.assert_sem_agregado(rc, out, "valor_nao_numerico")

    def test_lista_vazia_da_omie_e_zero_com_conferencia(self):
        self.srv.erro = (500, {"faultstring": "ERROR: Não existem registros para a página [1]!"})
        rc, out = self.totalizar()
        self.assertEqual((rc, out["status"], out["total"]), (0, "ok", "0"))
        self.assertEqual((out["conferencia"]["lidos"], out["conferencia"]["informados"]), (0, 0))

    def test_lista_vazia_fora_da_pagina_1_nao_vira_zero(self):
        self.srv.erro = (500, {"faultstring": "ERROR: Não existem registros para a página [5]!"})
        param = dict(self.PARAM, nPagina=5)
        with self.assertRaises(num.ApiError):
            num.totalizar(self.cliente, self.catalogo, self.SERVICO, self.METODO, param, "resumo.nValAberto")

    def test_teto_por_pagina_sem_chave_de_pagina(self):
        self.srv.paginas = [pagina([titulo(1)], 1, 1)]
        param = {"nRegPorPagina": 500, "cStatus": "ATRASADO"}
        num.totalizar(self.cliente, self.catalogo, self.SERVICO, self.METODO, param, "resumo.nValAberto")
        self.assertEqual(self.srv.chamadas[0]["param"][0]["nRegPorPagina"], 100)

    def test_sem_contagem_informada(self):
        self.srv.paginas = [{"titulosEncontrados": [titulo(1)]}]
        rc, out = self.totalizar()
        self.assert_sem_agregado(rc, out, "sem_contagem_informada")

    def test_consistencia_por_injecao(self):
        self.srv.paginas = [pagina([titulo(10), titulo(20)], 2, 1)]
        original = num.somar_particoes
        num.somar_particoes = lambda partes: original(partes) + num.Decimal("0.01")
        try:
            rc, out = self.totalizar()
        finally:
            num.somar_particoes = original
        self.assert_sem_agregado(rc, out, "consistencia")

    def test_agrupar_por_natureza(self):
        self.srv.paginas = [pagina([titulo(10, "R"), titulo(5, "P"), titulo(2.5, "R")], 3, 1)]
        rc, out = num.totalizar(self.cliente, self.catalogo, self.SERVICO, self.METODO, self.PARAM,
                                "resumo.nValAberto", "cabecTitulo.cNatureza")
        self.assertEqual(rc, 0)
        self.assertEqual(out["grupos"], {"P": "5", "R": "12.5"})
        self.assertEqual(out["conferencia"]["particao"], "grupo")
        self.assertEqual(out["total"], "17.5")


class EmpresaELimiteTests(Base):
    def test_empresa_das_chaves(self):
        self.srv.paginas = [{"pagina": 1, "total_de_paginas": 1, "registros": 1, "total_de_registros": 1,
                             "empresas_cadastro": [{"razao_social": "Empresa Sintetica", "nome_fantasia": "Sintetica", "cnpj": "x"}]}]
        out = num.empresa(self.cliente, self.catalogo)
        self.assertEqual(out["empresas"][0]["razao_social"], "Empresa Sintetica")
        self.assertEqual(self.srv.chamadas[0]["call"], "ListarEmpresas")

    def test_too_many_para_sem_retentar(self):
        self.cliente.waits = (0, 0, 0)
        self.srv.erro = (429, {"faultstring": "Too many requests"})
        with self.assertRaises(num.ApiError):
            self.totalizar()
        self.assertEqual(len(self.srv.chamadas), 1)


class PoliticaTests(unittest.TestCase):
    def setUp(self):
        self.catalogo = num.load_catalog()

    def test_escrita_e_recusada(self):
        for servico, metodo in (("produtos/pedido", "IncluirPedido"),
                                ("produtos/pedidovendafat", "FaturarPedidoVenda"),
                                ("servicos/os", "AlterarOS")):
            with self.subTest(metodo=metodo), self.assertRaises(num.PolicyError):
                num.check_allowed(self.catalogo, servico, metodo)

    def test_leitura_fora_dos_exemplos_e_aceita(self):
        self.assertEqual(num.check_allowed(self.catalogo, "servicos/os", "ListarOS"), "servicos/os")

    def test_barreira_de_nome_e_independente(self):
        catalogo = {"x/y": {"leitura": ["GerarBoleto"], "bloqueados": {}}}
        with self.assertRaises(num.PolicyError):
            num.check_allowed(catalogo, "x/y", "GerarBoleto")

    def test_cli_recusa_escrita_sem_pedir_credencial(self):
        saida = io.StringIO()
        with mock_env({"OMIE_APP_KEY": "", "OMIE_APP_SECRET": ""}), contextlib.redirect_stdout(saida):
            rc = num.main(["totalizar", "--servico", "produtos/pedido", "--metodo", "IncluirPedido",
                           "--param", "{}", "--soma", "x"])
        self.assertEqual(rc, 5)
        self.assertIn("bloqueado", json.loads(saida.getvalue()))

    def test_http_fora_de_localhost_e_recusado(self):
        with mock_env({"OMIE_BASE_URL": "http://app.omie.com.br/api/v1/"}), self.assertRaises(num.ConfigError):
            num.base_url()


class CredencialTests(Base):
    def test_erro_da_api_nao_vaza_credencial(self):
        self.srv.erro = (400, {"faultstring": f"chave {CHAVE} e segredo {SEGREDO} recusados"})
        with self.assertRaises(num.ApiError) as ctx:
            self.totalizar()
        self.assertNotIn(CHAVE, str(ctx.exception))
        self.assertNotIn(SEGREDO, str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
