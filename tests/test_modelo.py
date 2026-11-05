import numpy as np
import pandas as pd
import pytest

from brasileirao import dados, simulacao
from brasileirao.modelo import ModeloGols, peso_atipico


@pytest.fixture(scope="module")
def jogos():
    return dados.limpar(dados.PASTA_RAW / "br1_2026.json")


def test_dados_tem_20_clubes_e_380_jogos(jogos):
    assert len(jogos) == 380
    assert jogos["mandante"].nunique() == 20


def test_tabela_bate_com_pontos_de_vitorias_e_empates(jogos):
    t = simulacao.tabela_atual(jogos)
    assert (t["pts"] == 3 * t["v"] + t["e"]).all()
    assert t["sg"].sum() == 0  # todo gol marcado é sofrido por alguém


def test_matriz_de_placares_soma_um(jogos):
    m = ModeloGols.ajustar(jogos)
    mat = m.matriz_placares("Flamengo", "Remo")
    assert mat.sum() == pytest.approx(1.0)
    assert (mat >= 0).all()


def test_forcas_somam_zero(jogos):
    m = ModeloGols.ajustar(jogos)
    assert sum(m.ataque.values()) == pytest.approx(0, abs=1e-5)
    assert sum(m.defesa.values()) == pytest.approx(0, abs=1e-5)


def test_peso_atipico_faixas():
    saldo = pd.Series([0] * 98 + [10, -10])
    w = peso_atipico(saldo)
    assert w[0] == 1.0 and w[-1] == 0.4


def test_simulacao_posicoes_sao_permutacoes(jogos):
    m = ModeloGols.ajustar(jogos)
    s = simulacao.simular(m, jogos, n_sim=500, semente=1)
    assert (np.sort(s["posicoes"], axis=1) == np.arange(1, 21)).all()
    r = simulacao.resumo(s)
    assert r["titulo"].sum() == pytest.approx(100)
    assert r["rebaixamento"].sum() == pytest.approx(400)  # 4 vagas no Z4
