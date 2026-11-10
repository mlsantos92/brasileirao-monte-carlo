"""Validação fora da amostra: o que o modelo previu x o que aconteceu.

As previsões em outputs/previsoes_jogos.csv foram geradas com placares até 20/09/2026
(28ª rodada). Os jogos disputados depois disso nunca foram vistos pelo modelo.
Este módulo compara essas previsões congeladas com os placares reais.

Uso:  python -m brasileirao.validacao_fora_amostra
Fonte dos placares pós-corte: football-data.org via ValorFinal (CC BY 4.0), conferidos
com a imprensa em jogos de amostra (data/raw/resultados_pos_corte.csv).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import dados
from .avaliacao import _resultado, metricas

RAIZ = Path(__file__).resolve().parents[2]
SAIDAS = RAIZ / "outputs"
AZUL, LARANJA, CINZA, TINTA = "#2F5D9E", "#D2601A", "#9AA3AD", "#15202B"
ROTULO = {0: "mandante", 1: "empate", 2: "visitante"}


def carregar() -> tuple[pd.DataFrame, pd.DataFrame]:
    prev = pd.read_csv(SAIDAS / "previsoes_jogos.csv")
    real = pd.read_csv(RAIZ / "data" / "raw" / "resultados_pos_corte.csv")
    df = prev.merge(real, on=["rodada", "mandante", "visitante"], how="inner", validate="1:1")
    faltam = len(real) - len(df)
    if faltam:
        raise ValueError(f"{faltam} jogos do arquivo de resultados não estão nas previsões")
    df["resultado"] = _resultado(df)
    jogos = dados.carregar()
    return df, jogos[jogos["disputado"]]


def avaliar(df: pd.DataFrame, treino: pd.DataFrame) -> pd.DataFrame:
    p = df[["p_mandante", "p_empate", "p_visitante"]].to_numpy()
    y = df["resultado"].to_numpy()
    freq = np.bincount(_resultado(treino), minlength=3) / len(treino)
    out = pd.DataFrame({
        "modelo Dixon-Coles": metricas(p, y),
        "frequência do treino": metricas(np.tile(freq, (len(y), 1)), y),
        "uniforme (1/3)": metricas(np.full_like(p, 1 / 3), y),
    }).T
    out["placar_exato"] = [float((df.placar_mais_provavel == df.gols_mandante.astype(str) + "x" + df.gols_visitante.astype(str)).mean()), np.nan, np.nan]
    return out


def calibracao(df: pd.DataFrame) -> pd.DataFrame:
    """Para cada probabilidade prevista (3 por jogo), o resultado aconteceu?"""
    linhas = []
    for k, col in enumerate(["p_mandante", "p_empate", "p_visitante"]):
        linhas.append(pd.DataFrame({"prob": df[col], "ocorreu": (df["resultado"] == k).astype(int)}))
    c = pd.concat(linhas)
    c["faixa"] = pd.cut(c.prob, [0, .2, .3, .4, .5, .6, 1], include_lowest=True)
    return c.groupby("faixa", observed=True).agg(n=("ocorreu", "size"), prob_media=("prob", "mean"), frequencia=("ocorreu", "mean"))


def pontos_por_clube(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for _, j in df.iterrows():
        ganho = {0: (3, 0), 1: (1, 1), 2: (0, 3)}[j.resultado]
        linhas += [(j.mandante, 3 * j.p_mandante + j.p_empate, ganho[0]), (j.visitante, 3 * j.p_visitante + j.p_empate, ganho[1])]
    return pd.DataFrame(linhas, columns=["clube", "esperado", "real"]).groupby("clube").sum().sort_values("real")


def classificacao(treino: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    jogos = pd.concat([treino[["mandante", "visitante", "gols_mandante", "gols_visitante"]],
                       df[["mandante", "visitante", "gols_mandante", "gols_visitante"]]]).astype({"gols_mandante": int, "gols_visitante": int})
    t = {}
    for _, j in jogos.iterrows():
        for c, gp, gc in [(j.mandante, j.gols_mandante, j.gols_visitante), (j.visitante, j.gols_visitante, j.gols_mandante)]:
            s = t.setdefault(c, dict(pts=0, j=0, v=0, sg=0, gp=0))
            s["j"] += 1; s["sg"] += gp - gc; s["gp"] += gp
            s["pts"] += 3 if gp > gc else 1 if gp == gc else 0
            s["v"] += gp > gc
    tab = pd.DataFrame(t).T.sort_values(["pts", "v", "sg", "gp"], ascending=False)
    tab["pos"] = range(1, len(tab) + 1)
    return tab


def graficos(df, cal, pts, destino: Path) -> None:
    plt.rcParams.update({"figure.dpi": 150, "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    # calibração
    fig, ax = plt.subplots(figsize=(5.6, 5.0))
    ax.plot([0, 1], [0, 1], ls="--", color=CINZA, lw=1)
    ax.scatter(cal.prob_media, cal.frequencia, s=cal.n * 4, color=AZUL, zorder=3, alpha=.9)
    for _, r in cal.iterrows():
        ax.annotate(f"n={int(r.n)}", (r.prob_media, r.frequencia), xytext=(8, -4), textcoords="offset points", fontsize=8, color=TINTA)
    ax.set_xlim(0, .8); ax.set_ylim(0, 1.05)
    ax.set_xlabel("Probabilidade prevista"); ax.set_ylabel("Frequência observada")
    ax.set_title("Calibração fora da amostra", loc="left", fontsize=12)
    ax.grid(alpha=.25)
    fig.text(.01, .01, f"{len(df)} jogos após o corte de 20/09 · 3 probabilidades por jogo · tamanho = nº de previsões", fontsize=7.5, color="#566270")
    fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig(destino / "validacao_calibracao.png"); plt.close(fig)
    # pontos esperados x reais
    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    lim = (0, max(pts.max()) + 2)
    ax.plot(lim, lim, ls="--", color=CINZA, lw=1)
    ax.scatter(pts.esperado, pts.real, color=AZUL, s=36, zorder=3)
    # posição dos rótulos ajustada à mão onde os pontos ficam colados
    esquerda = {"Palmeiras", "Vasco", "Grêmio", "Vitória", "Bahia"}
    acima = {"Internacional"}
    for c, r in pts.iterrows():
        xy, ha = ((-6, 3), "right") if c in esquerda else (((0, 8), "center") if c in acima else ((6, 3), "left"))
        ax.annotate(c, (r.esperado, r.real), xytext=xy, ha=ha, textcoords="offset points", fontsize=7.5, color=TINTA)
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("Pontos esperados pelo modelo"); ax.set_ylabel("Pontos conquistados")
    ax.set_title("Pontos esperados x reais desde o corte", loc="left", fontsize=12)
    ax.grid(alpha=.25)
    r = np.corrcoef(pts.esperado, pts.real)[0, 1]
    fig.text(.01, .01, f"Rodadas 29 a 34 e 2 jogos adiados da 21ª · correlação {r:.2f}".replace(".", ","), fontsize=7.5, color="#566270")
    fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig(destino / "validacao_pontos.png"); plt.close(fig)
    # probabilidade dada ao que aconteceu, por jogo
    d = df.assign(p_real=[r[["p_mandante", "p_empate", "p_visitante"]].iloc[k] for (_, r), k in zip(df.iterrows(), df.resultado)])
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    cores = np.where(d.p_real == d[["p_mandante", "p_empate", "p_visitante"]].max(axis=1), AZUL, LARANJA)
    ax.bar(range(len(d)), d.p_real, color=cores, width=.8)
    ax.axhline(1 / 3, color=TINTA, ls="--", lw=1)
    pos = d.reset_index(drop=True).assign(i=lambda x: x.index).groupby("rodada").i.agg(["min", "max"])
    pos.loc[29, "min"] = pos.loc[21, "min"]
    pos = pos.drop(21)
    ax.set_xticks((pos["min"] + pos["max"]) / 2, ["R21 adiados + R29" if r == 29 else f"R{r}" for r in pos.index], fontsize=8)
    ax.set_ylabel("Probabilidade dada ao resultado real"); ax.set_ylim(0, .8)
    ax.set_title("Quanto o modelo apostou no que de fato aconteceu", loc="left", fontsize=12)
    fig.text(.01, .01, "Azul: o resultado era o favorito do modelo · laranja: não era · linha tracejada: palpite uniforme (1/3)", fontsize=7.5, color="#566270")
    fig.tight_layout(rect=(0, .04, 1, 1)); fig.savefig(destino / "validacao_jogos.png"); plt.close(fig)


def main() -> None:
    df, treino = carregar()
    res = avaliar(df, treino)
    cal = calibracao(df)
    pts = pontos_por_clube(df)
    graficos(df, cal, pts, SAIDAS)
    por_rodada = df.groupby("rodada").apply(lambda g: pd.Series(metricas(g[["p_mandante", "p_empate", "p_visitante"]].to_numpy(), g.resultado.to_numpy())), include_groups=False)
    tab = classificacao(treino, df)
    prob = pd.read_csv(SAIDAS / "probabilidades.csv").set_index("clube")
    proj = tab.join(prob[["pts_atuais", "pts_mediana", "titulo", "rebaixamento", "pos_media"]])
    res.round(4).to_csv(SAIDAS / "validacao_metricas.csv")
    cal.round(4).to_csv(SAIDAS / "validacao_calibracao.csv")
    pts.round(2).to_csv(SAIDAS / "validacao_pontos.csv")
    por_rodada.round(4).to_csv(SAIDAS / "validacao_por_rodada.csv")
    proj.to_csv(SAIDAS / "validacao_classificacao_atual.csv")
    df.assign(previsto=df[["p_mandante", "p_empate", "p_visitante"]].to_numpy().argmax(axis=1)).to_csv(SAIDAS / "validacao_jogos.csv", index=False)
    print(f"{len(df)} jogos fora da amostra")
    print(res.round(4).to_string())
    print(cal.round(3).to_string())
    print(por_rodada.round(3).to_string())
    print(pts.assign(dif=pts.real - pts.esperado).round(1).to_string())
    print(proj[["pos", "pts", "j", "pts_atuais", "pos_media", "titulo", "rebaixamento"]].to_string())


if __name__ == "__main__":
    main()
