"""Roda o projeto inteiro: dados -> SQL -> modelo -> backtest -> simulação -> saídas.

Uso:
    python -m brasileirao.pipeline              # usa o arquivo já baixado
    python -m brasileirao.pipeline --atualizar  # baixa os placares mais recentes
"""

from __future__ import annotations

import argparse
from pathlib import Path

from . import avaliacao, banco, dados, graficos, simulacao
from .modelo import ModeloGols, prever_jogos

SAIDAS = Path(__file__).resolve().parents[2] / "outputs"


def main(atualizar: bool = False, n_sim: int = 50_000) -> None:
    SAIDAS.mkdir(exist_ok=True)

    jogos = dados.carregar(atualizar=atualizar)
    feitos = jogos[jogos["disputado"]]
    print(f"Jogos disputados: {len(feitos)} (até a {feitos['rodada'].max()}ª rodada)")

    con = banco.criar_banco(jogos)
    for nome in banco.consultas():
        banco.rodar(con, nome).to_csv(SAIDAS / f"sql_{nome}.csv", index=False)
    con.close()

    bt = avaliacao.backtest_rolante(jogos)
    bt.round(4).to_csv(SAIDAS / "backtest.csv")
    print("\nBacktest rolante (rodada seguinte, quanto menor melhor):")
    print(bt.round(4).to_string())

    modelo = ModeloGols.ajustar(jogos)
    forcas = modelo.tabela_forcas()
    forcas.round(4).to_csv(SAIDAS / "forcas.csv", index=False)
    prever_jogos(modelo, jogos[~jogos["disputado"]]).round(4).to_csv(
        SAIDAS / "previsoes_jogos.csv", index=False)

    sim = simulacao.simular(modelo, jogos, n_sim=n_sim)
    res = simulacao.resumo(sim)
    res.round(2).to_csv(SAIDAS / "probabilidades.csv", index=False)
    cor = simulacao.corte_rebaixamento(sim)
    cor.round(2).to_csv(SAIDAS / "corte_rebaixamento.csv", index=False)

    graficos.risco_rebaixamento(res, SAIDAS / "risco_rebaixamento.png")
    graficos.corte(cor, SAIDAS / "corte_rebaixamento.png")
    graficos.forcas(forcas, SAIDAS / "forcas.png")

    print(f"\nProjeção ({n_sim:,} simulações):".replace(",", "."))
    print(res[["clube", "pts_atuais", "pts_mediana", "titulo", "rebaixamento"]].round(1).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--atualizar", action="store_true", help="baixa os placares mais recentes")
    ap.add_argument("--simulacoes", type=int, default=50_000)
    a = ap.parse_args()
    main(a.atualizar, a.simulacoes)
