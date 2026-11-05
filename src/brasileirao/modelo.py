"""Modelo de gols Dixon-Coles com pesos por recência e por jogo atípico.

Ideia central
-------------
Os gols de cada time num jogo seguem uma distribuição de Poisson:

    log(λ_mandante)  = μ + mando + ataque[mandante]  + defesa[visitante]
    log(λ_visitante) = μ         + ataque[visitante] + defesa[mandante]

Opcional (``mando_por_clube=True``): cada clube ganha um desvio próprio
da vantagem de casa, com penalidade forte para não exagerar com poucos jogos.

- ``ataque`` positivo  = o time marca mais que a média;
- ``defesa`` positiva  = o time SOFRE mais que a média (defesa fraca);
- ``mando``            = vantagem de jogar em casa, igual para todos.

A correção de Dixon & Coles (1997) ajusta a probabilidade dos placares
baixos (0x0, 1x0, 0x1, 1x1), que o Poisson puro erra um pouco.

Pesos (decisões de modelagem)
-----------------------------
1. Recência (opcional): com ``meia_vida_dias=60``, um jogo de 60 dias atrás
   vale metade de um jogo de hoje. O backtest mostrou que, só com gols,
   isso PIORA as previsões (descarta informação demais), então o padrão é
   não usar decaimento. Veja o README.
2. Jogo atípico: medimos o saldo de gols de cada jogo em desvios-padrão
   (z). Até 1 DP o jogo vale 1; entre 1 e 2 DP vale 0,7; acima de 2 DP,
   0,4. Uma goleada fora da curva não deve redefinir a força de um time.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson

MAX_GOLS = 10  # placares acima de 10 gols têm probabilidade desprezível


def peso_recencia(datas: pd.Series, referencia: pd.Timestamp, meia_vida_dias: float | None) -> np.ndarray:
    if meia_vida_dias is None:  # sem decaimento: todos os jogos valem igual
        return np.ones(len(datas))
    dias = (referencia - datas).dt.days.clip(lower=0).to_numpy(float)
    return np.exp(-np.log(2) * dias / meia_vida_dias)


def peso_atipico(saldo: pd.Series) -> np.ndarray:
    z = (saldo - saldo.mean()) / saldo.std(ddof=0)
    z = z.abs().to_numpy(float)
    return np.where(z <= 1, 1.0, np.where(z <= 2, 0.7, 0.4))


def _tau(gm, gv, lm, lv, rho):
    """Correção Dixon-Coles para os placares 0x0, 1x0, 0x1 e 1x1."""
    t = np.ones_like(lm)
    t = np.where((gm == 0) & (gv == 0), 1 - lm * lv * rho, t)
    t = np.where((gm == 0) & (gv == 1), 1 + lm * rho, t)
    t = np.where((gm == 1) & (gv == 0), 1 + lv * rho, t)
    t = np.where((gm == 1) & (gv == 1), 1 - rho, t)
    return t


@dataclass
class ModeloGols:
    clubes: list[str]
    mu: float
    mando: float
    ataque: dict[str, float]
    defesa: dict[str, float]
    rho: float
    mando_clube: dict[str, float] | None = None

    # ---------------------------------------------------------------- ajuste
    @classmethod
    def ajustar(
        cls,
        jogos: pd.DataFrame,
        referencia: pd.Timestamp | None = None,
        meia_vida_dias: float | None = None,
        usar_peso_atipico: bool = True,
        mando_por_clube: bool = False,
        penalidade_mando: float = 5.0,
    ) -> "ModeloGols":
        """Estima os parâmetros por máxima verossimilhança ponderada."""
        j = jogos[jogos["disputado"]].copy()
        referencia = referencia or j["data"].max()
        clubes = sorted(set(j["mandante"]) | set(j["visitante"]))
        idx = {c: i for i, c in enumerate(clubes)}
        n = len(clubes)

        im = j["mandante"].map(idx).to_numpy()
        iv = j["visitante"].map(idx).to_numpy()
        gm = j["gols_mandante"].to_numpy(int)
        gv = j["gols_visitante"].to_numpy(int)

        w = peso_recencia(j["data"], referencia, meia_vida_dias)
        if usar_peso_atipico:
            w = w * peso_atipico(j["gols_mandante"] - j["gols_visitante"])

        def desempacotar(p):
            mu, mando, rho = p[0], p[1], p[2]
            # soma zero: o último clube é o negativo da soma dos outros
            atq = np.append(p[3 : 3 + n - 1], -p[3 : 3 + n - 1].sum())
            dfs = np.append(p[3 + n - 1 : 3 + 2 * (n - 1)], -p[3 + n - 1 : 3 + 2 * (n - 1)].sum())
            mc = p[3 + 2 * (n - 1) :] if mando_por_clube else np.zeros(n)
            return mu, mando, rho, atq, dfs, mc

        def neg_log_vero(p):
            mu, mando, rho, atq, dfs, mc = desempacotar(p)
            lm = np.exp(mu + mando + mc[im] + atq[im] + dfs[iv])
            lv = np.exp(mu + atq[iv] + dfs[im])
            tau = np.clip(_tau(gm, gv, lm, lv, rho), 1e-10, None)
            ll = np.log(tau) + poisson.logpmf(gm, lm) + poisson.logpmf(gv, lv)
            # pequena penalidade (ridge) evita forças extremas com poucos jogos
            return (-(w * ll).sum() + 0.5 * (atq @ atq + dfs @ dfs)
                    + 0.5 * penalidade_mando * (mc @ mc))

        n_params = 3 + 2 * (n - 1) + (n if mando_por_clube else 0)
        p0 = np.zeros(n_params)
        p0[0] = np.log(max(j[["gols_mandante", "gols_visitante"]].to_numpy().mean(), 0.1))
        limites = [(None, None), (None, None), (-0.3, 0.3)] + [(None, None)] * (n_params - 3)
        res = minimize(neg_log_vero, p0, method="L-BFGS-B", bounds=limites)
        if not res.success:
            raise RuntimeError(f"otimização não convergiu: {res.message}")
        mu, mando, rho, atq, dfs, mc = desempacotar(res.x)
        return cls(
            clubes=clubes,
            mu=float(mu),
            mando=float(mando),
            ataque=dict(zip(clubes, atq.round(6))),
            defesa=dict(zip(clubes, dfs.round(6))),
            rho=float(rho),
            mando_clube=dict(zip(clubes, mc.round(6))) if mando_por_clube else None,
        )

    # ------------------------------------------------------------- previsão
    def gols_esperados(self, mandante: str, visitante: str) -> tuple[float, float]:
        extra = self.mando_clube.get(mandante, 0.0) if self.mando_clube else 0.0
        lm = np.exp(self.mu + self.mando + extra + self.ataque[mandante] + self.defesa[visitante])
        lv = np.exp(self.mu + self.ataque[visitante] + self.defesa[mandante])
        return float(lm), float(lv)

    def matriz_placares(self, mandante: str, visitante: str) -> np.ndarray:
        """Matriz P[gols_mandante, gols_visitante], somando 1."""
        lm, lv = self.gols_esperados(mandante, visitante)
        g = np.arange(MAX_GOLS + 1)
        m = np.outer(poisson.pmf(g, lm), poisson.pmf(g, lv))
        gm, gv = np.meshgrid(g, g, indexing="ij")
        m = m * _tau(gm, gv, np.full_like(m, lm), np.full_like(m, lv), self.rho)
        return m / m.sum()

    def prob_1x2(self, mandante: str, visitante: str) -> tuple[float, float, float]:
        m = self.matriz_placares(mandante, visitante)
        return float(np.tril(m, -1).sum()), float(np.trace(m)), float(np.triu(m, 1).sum())

    def tabela_forcas(self) -> pd.DataFrame:
        df = pd.DataFrame(
            {"clube": self.clubes,
             "ataque": [self.ataque[c] for c in self.clubes],
             "defesa": [self.defesa[c] for c in self.clubes]}
        )
        # saldo de força: quanto maior, melhor (ataca mais e sofre menos)
        df["forca"] = df["ataque"] - df["defesa"]
        return df.sort_values("forca", ascending=False).reset_index(drop=True)


def prever_jogos(modelo: ModeloGols, jogos: pd.DataFrame) -> pd.DataFrame:
    """Probabilidades 1X2, gols esperados e placar mais provável por jogo."""
    linhas = []
    for _, r in jogos.iterrows():
        m = modelo.matriz_placares(r["mandante"], r["visitante"])
        pm, pe, pv = np.tril(m, -1).sum(), np.trace(m), np.triu(m, 1).sum()
        lm, lv = modelo.gols_esperados(r["mandante"], r["visitante"])
        a, b = np.unravel_index(m.argmax(), m.shape)
        linhas.append({
            "jogo_id": r["jogo_id"], "rodada": r["rodada"],
            "mandante": r["mandante"], "visitante": r["visitante"],
            "p_mandante": pm, "p_empate": pe, "p_visitante": pv,
            "gols_esp_mandante": lm, "gols_esp_visitante": lv,
            "placar_mais_provavel": f"{a}x{b}", "p_placar": m[a, b],
        })
    return pd.DataFrame(linhas)
