"""Simulação Monte Carlo do restante do campeonato.

Para cada um dos N campeonatos simulados:
1. sorteia o placar de cada jogo que falta, a partir da matriz de placares
   do modelo;
2. soma pontos, vitórias, saldo e gols pró à tabela atual;
3. ordena pelos critérios de desempate do regulamento
   (pontos > vitórias > saldo > gols pró; empate total = sorteio).

Tudo é vetorizado com NumPy: 50 mil temporadas rodam em segundos.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .modelo import MAX_GOLS, ModeloGols


def tabela_atual(jogos: pd.DataFrame) -> pd.DataFrame:
    """Classificação a partir dos jogos já disputados."""
    j = jogos[jogos["disputado"]]
    casa = pd.DataFrame({"clube": j["mandante"], "gp": j["gols_mandante"], "gc": j["gols_visitante"]})
    fora = pd.DataFrame({"clube": j["visitante"], "gp": j["gols_visitante"], "gc": j["gols_mandante"]})
    t = pd.concat([casa, fora]).astype({"gp": int, "gc": int})
    t["v"] = (t["gp"] > t["gc"]).astype(int)
    t["e"] = (t["gp"] == t["gc"]).astype(int)
    t["d"] = (t["gp"] < t["gc"]).astype(int)
    t = t.groupby("clube").agg(j=("gp", "size"), v=("v", "sum"), e=("e", "sum"),
                                d=("d", "sum"), gp=("gp", "sum"), gc=("gc", "sum"))
    t["sg"] = t["gp"] - t["gc"]
    t["pts"] = 3 * t["v"] + t["e"]
    t = t.sort_values(["pts", "v", "sg", "gp"], ascending=False).reset_index()
    t.insert(0, "pos", range(1, len(t) + 1))
    return t


def simular(
    modelo: ModeloGols,
    jogos: pd.DataFrame,
    n_sim: int = 50_000,
    semente: int = 42,
) -> dict:
    """Devolve as posições finais de cada simulação e a tabela de partida."""
    rng = np.random.default_rng(semente)
    base = tabela_atual(jogos).set_index("clube")
    clubes = list(base.index)
    idx = {c: i for i, c in enumerate(clubes)}
    n = len(clubes)

    pts = np.tile(base["pts"].to_numpy(), (n_sim, 1)).astype(np.int64)
    vit = np.tile(base["v"].to_numpy(), (n_sim, 1)).astype(np.int64)
    sg = np.tile(base["sg"].to_numpy(), (n_sim, 1)).astype(np.int64)
    gp = np.tile(base["gp"].to_numpy(), (n_sim, 1)).astype(np.int64)

    restantes = jogos[~jogos["disputado"]]
    lado = MAX_GOLS + 1
    for _, r in restantes.iterrows():
        m = modelo.matriz_placares(r["mandante"], r["visitante"]).ravel()
        sorteio = rng.choice(m.size, size=n_sim, p=m)
        a, b = sorteio // lado, sorteio % lado
        i, k = idx[r["mandante"]], idx[r["visitante"]]
        pts[:, i] += np.where(a > b, 3, np.where(a == b, 1, 0))
        pts[:, k] += np.where(b > a, 3, np.where(a == b, 1, 0))
        vit[:, i] += a > b
        vit[:, k] += b > a
        sg[:, i] += a - b
        sg[:, k] += b - a
        gp[:, i] += a
        gp[:, k] += b

    # chave única de desempate; o ruído final resolve empates totais
    chave = (pts * 10**8 + vit * 10**6 + (sg + 500) * 10**3 + gp).astype(float)
    chave += rng.random(chave.shape) * 0.5
    ordem = np.argsort(-chave, axis=1)
    posicoes = np.empty_like(ordem)
    posicoes[np.arange(n_sim)[:, None], ordem] = np.arange(1, n + 1)
    return {"clubes": clubes, "posicoes": posicoes, "pontos": pts, "base": base.reset_index()}


def resumo(sim: dict) -> pd.DataFrame:
    """Probabilidades por faixa da tabela e distribuição de pontos."""
    pos, pts, clubes = sim["posicoes"], sim["pontos"], sim["clubes"]
    df = pd.DataFrame({
        "clube": clubes,
        "pts_atuais": sim["base"].set_index("clube").loc[clubes, "pts"].to_numpy(),
        "pts_p10": np.percentile(pts, 10, axis=0).round(),
        "pts_mediana": np.median(pts, axis=0).round(),
        "pts_p90": np.percentile(pts, 90, axis=0).round(),
        "titulo": (pos == 1).mean(axis=0) * 100,
        "top4": (pos <= 4).mean(axis=0) * 100,
        "top6": (pos <= 6).mean(axis=0) * 100,
        "rebaixamento": (pos >= 17).mean(axis=0) * 100,
        "pos_media": pos.mean(axis=0),
    })
    return df.sort_values("pos_media").reset_index(drop=True)


def corte_rebaixamento(sim: dict) -> pd.DataFrame:
    """Para cada pontuação final, a % de vezes em que ela bastou para escapar."""
    pos, pts = sim["posicoes"].ravel(), sim["pontos"].ravel()
    df = pd.DataFrame({"pontos": pts, "escapou": pos <= 16})
    t = df.groupby("pontos")["escapou"].agg(["mean", "size"]).reset_index()
    t = t[t["size"] >= 200]  # só pontuações com amostra suficiente
    t["permanencia_pct"] = t["mean"] * 100
    return t[["pontos", "permanencia_pct", "size"]].rename(columns={"size": "ocorrencias"})
