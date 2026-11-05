"""Gráficos do relatório (matplotlib, salvos em outputs/)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

TINTA, CINZA, ALERTA, DESTAQUE = "#1f2328", "#8c959f", "#cf222e", "#0969da"


def _estilo(ax):
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(colors=TINTA)
    ax.grid(axis="x", color="#d0d7de", linewidth=0.6)
    ax.set_axisbelow(True)


def risco_rebaixamento(resumo: pd.DataFrame, caminho: Path) -> None:
    d = resumo[resumo["rebaixamento"] >= 0.5].sort_values("rebaixamento")
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(d) + 1.2))
    cores = [ALERTA if v >= 50 else DESTAQUE for v in d["rebaixamento"]]
    ax.barh(d["clube"], d["rebaixamento"], color=cores, height=0.6)
    for y, v in enumerate(d["rebaixamento"]):
        ax.text(v + 1, y, f"{v:.1f}%".replace(".", ","), va="center", color=TINTA, fontsize=9)
    ax.set_xlim(0, 110)
    ax.set_xlabel("% das simulações terminando entre 17º e 20º", color=TINTA)
    ax.set_title("Probabilidade de rebaixamento", loc="left", color=TINTA, fontweight="bold")
    _estilo(ax)
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)


def corte(corte_df: pd.DataFrame, caminho: Path) -> None:
    d = corte_df[(corte_df["permanencia_pct"] > 1) & (corte_df["permanencia_pct"] < 99.9)]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.bar(d["pontos"], d["permanencia_pct"], color=DESTAQUE, width=0.75)
    ax.axhline(50, color=CINZA, linestyle="--", linewidth=1)
    ax.set_xlabel("pontos ao fim do campeonato", color=TINTA)
    ax.set_ylabel("% de permanência", color=TINTA)
    ax.set_title("Quantos pontos livram da queda", loc="left", color=TINTA, fontweight="bold")
    _estilo(ax)
    ax.grid(axis="y", color="#d0d7de", linewidth=0.6)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)


def forcas(tabela: pd.DataFrame, caminho: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(tabela["ataque"], -tabela["defesa"], color=DESTAQUE, s=28)
    usados: list[tuple[float, float]] = []
    for _, r in tabela.iterrows():
        x, y = r["ataque"], -r["defesa"]
        # rótulo vai para baixo se já houver outro rótulo muito perto
        perto = any(abs(x - a) < 0.06 and abs(y - b) < 0.03 for a, b in usados)
        ax.annotate(r["clube"], (x, y), fontsize=8, color=TINTA,
                    xytext=(4, -11 if perto else 3), textcoords="offset points")
        usados.append((x, y))
    ax.axhline(0, color=CINZA, linewidth=0.8)
    ax.axvline(0, color=CINZA, linewidth=0.8)
    ax.set_xlabel("ataque (→ marca mais que a média)", color=TINTA)
    ax.set_ylabel("defesa (↑ sofre menos que a média)", color=TINTA)
    ax.set_title("Força estimada dos clubes", loc="left", color=TINTA, fontweight="bold")
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)
