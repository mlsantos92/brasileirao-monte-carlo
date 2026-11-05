"""Backtest: o modelo prevê melhor do que um palpite ingênuo?

Treina só com os jogos até uma rodada de corte e prevê as rodadas
seguintes, que o modelo nunca viu. Compara com duas referências:

- "uniforme": 1/3 para cada resultado;
- "frequência": % de vitórias do mandante, empates e vitórias do
  visitante observadas no período de treino.

Métricas (quanto MENOR, melhor):
- log loss: penaliza muito errar com confiança;
- Brier: erro quadrático médio das três probabilidades.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .modelo import ModeloGols, prever_jogos


def _resultado(df: pd.DataFrame) -> np.ndarray:
    """0 = mandante vence, 1 = empate, 2 = visitante vence."""
    gm, gv = df["gols_mandante"].astype(int), df["gols_visitante"].astype(int)
    return np.where(gm > gv, 0, np.where(gm == gv, 1, 2))


def metricas(probs: np.ndarray, real: np.ndarray) -> dict:
    probs = np.clip(probs, 1e-12, 1)
    um_hot = np.eye(3)[real]
    return {
        "log_loss": float(-np.log(probs[np.arange(len(real)), real]).mean()),
        "brier": float(((probs - um_hot) ** 2).sum(axis=1).mean()),
        "acerto_favorito": float((probs.argmax(axis=1) == real).mean()),
    }


def backtest_rolante(jogos: pd.DataFrame, primeira: int = 12, **kwargs_modelo) -> pd.DataFrame:
    """Treina até a rodada r e prevê só a rodada r+1, para r = primeira, ..., última-1.

    É o jeito honesto de avaliar: em cada momento, o modelo usa apenas o que
    já tinha acontecido. Um único corte depende muito de poucas rodadas.
    """
    feitos = jogos[jogos["disputado"]]
    ultima = int(feitos["rodada"].max())
    probs, freqs, reais = [], [], []
    for r in range(primeira, ultima):
        treino = feitos[feitos["rodada"] <= r]
        teste = feitos[feitos["rodada"] == r + 1]
        if teste.empty:
            continue
        modelo = ModeloGols.ajustar(treino, referencia=teste["data"].min(), **kwargs_modelo)
        probs.append(prever_jogos(modelo, teste)[["p_mandante", "p_empate", "p_visitante"]].to_numpy())
        f = np.bincount(_resultado(treino), minlength=3) / len(treino)
        freqs.append(np.tile(f, (len(teste), 1)))
        reais.append(_resultado(teste))
    p, f, y = np.vstack(probs), np.vstack(freqs), np.concatenate(reais)
    out = pd.DataFrame({
        "modelo": metricas(p, y),
        "frequência do treino": metricas(f, y),
        "uniforme (1/3)": metricas(np.full_like(p, 1 / 3), y),
    }).T
    out.attrs["n_jogos_previstos"] = len(y)
    return out


def backtest(jogos: pd.DataFrame, rodada_corte: int, **kwargs_modelo) -> pd.DataFrame:
    treino = jogos[jogos["disputado"] & (jogos["rodada"] <= rodada_corte)]
    teste = jogos[jogos["disputado"] & (jogos["rodada"] > rodada_corte)]
    modelo = ModeloGols.ajustar(treino, **kwargs_modelo)

    real = _resultado(teste)
    p_modelo = prever_jogos(modelo, teste)[["p_mandante", "p_empate", "p_visitante"]].to_numpy()
    freq = np.bincount(_resultado(treino), minlength=3) / len(treino)

    linhas = {
        "modelo Dixon-Coles": metricas(p_modelo, real),
        "frequência do treino": metricas(np.tile(freq, (len(teste), 1)), real),
        "uniforme (1/3)": metricas(np.full((len(teste), 3), 1 / 3), real),
    }
    out = pd.DataFrame(linhas).T
    out.attrs["n_treino"], out.attrs["n_teste"] = len(treino), len(teste)
    return out
