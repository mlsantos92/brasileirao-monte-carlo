"""Coleta e limpeza dos jogos do Brasileirão Série A.

Fonte: projeto aberto openfootball (domínio público), que publica o
calendário e os placares em JSON no GitHub.

Etapas:
1. baixar o JSON bruto e guardar em data/raw/ (nunca é editado à mão);
2. padronizar nomes de clubes, datas e placares;
3. salvar uma tabela limpa em data/processed/partidas.csv.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
import requests

URL_PADRAO = (
    "https://raw.githubusercontent.com/openfootball/football.json/"
    "master/{ano}/br.1.json"
)

RAIZ = Path(__file__).resolve().parents[2]
PASTA_RAW = RAIZ / "data" / "raw"
PASTA_PROC = RAIZ / "data" / "processed"

# Nomes oficiais longos -> nomes curtos usados no dia a dia.
NOMES = {
    "CA Mineiro": "Atlético-MG",
    "CA Paranaense": "Athletico-PR",
    "Botafogo FR": "Botafogo",
    "Chapecoense AF": "Chapecoense",
    "Clube do Remo": "Remo",
    "Coritiba FBC": "Coritiba",
    "CR Flamengo": "Flamengo",
    "CR Vasco da Gama": "Vasco",
    "Cruzeiro EC": "Cruzeiro",
    "EC Bahia": "Bahia",
    "EC Vitória": "Vitória",
    "Fluminense FC": "Fluminense",
    "Grêmio FBPA": "Grêmio",
    "Mirassol FC": "Mirassol",
    "RB Bragantino": "Bragantino",
    "Santos FC": "Santos",
    "São Paulo FC": "São Paulo",
    "SC Corinthians Paulista": "Corinthians",
    "SC Internacional": "Internacional",
    "SE Palmeiras": "Palmeiras",
}


def baixar(ano: int = 2026, destino: Path | None = None) -> Path:
    """Baixa o arquivo bruto da temporada e devolve o caminho salvo."""
    destino = destino or PASTA_RAW / f"br1_{ano}.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    resposta = requests.get(URL_PADRAO.format(ano=ano), timeout=30)
    resposta.raise_for_status()
    destino.write_bytes(resposta.content)
    return destino


def _placar_final(jogo: dict) -> tuple[int, int] | None:
    """O placar pode vir como {'ft': [a, b]} ou como [a, b]; sem placar = jogo futuro."""
    placar = jogo.get("score")
    if isinstance(placar, dict):
        placar = placar.get("ft")
    if isinstance(placar, list) and len(placar) == 2:
        return int(placar[0]), int(placar[1])
    return None


def limpar(caminho_raw: Path) -> pd.DataFrame:
    """Transforma o JSON bruto numa tabela com uma linha por jogo."""
    bruto = json.loads(Path(caminho_raw).read_text(encoding="utf-8"))
    linhas = []
    for jogo in bruto["matches"]:
        placar = _placar_final(jogo)
        rodada = int(re.search(r"\d+", jogo["round"]).group())
        linhas.append(
            {
                "rodada": rodada,
                "data": jogo.get("date"),
                "mandante": NOMES.get(jogo["team1"], jogo["team1"]),
                "visitante": NOMES.get(jogo["team2"], jogo["team2"]),
                "gols_mandante": placar[0] if placar else pd.NA,
                "gols_visitante": placar[1] if placar else pd.NA,
                "disputado": placar is not None,
            }
        )
    df = pd.DataFrame(linhas)
    df["data"] = pd.to_datetime(df["data"])
    df[["gols_mandante", "gols_visitante"]] = df[
        ["gols_mandante", "gols_visitante"]
    ].astype("Int64")
    df = df.sort_values(["rodada", "data", "mandante"]).reset_index(drop=True)
    df.insert(0, "jogo_id", range(1, len(df) + 1))
    validar(df)
    return df


def validar(df: pd.DataFrame) -> None:
    """Checagens de qualidade: falham cedo se o arquivo vier estranho."""
    clubes = set(df["mandante"]) | set(df["visitante"])
    assert len(clubes) == 20, f"esperava 20 clubes, vieram {len(clubes)}"
    assert len(df) == 380, f"esperava 380 jogos, vieram {len(df)}"
    pares = df[["mandante", "visitante"]].apply(tuple, axis=1)
    assert pares.is_unique, "há confronto mandante x visitante repetido"
    jogados = df[df["disputado"]]
    assert (jogados[["gols_mandante", "gols_visitante"]] >= 0).all().all()
    sem_nome = clubes - set(NOMES.values())
    assert not sem_nome, f"clubes sem nome curto: {sem_nome}"


def carregar(ano: int = 2026, atualizar: bool = False) -> pd.DataFrame:
    """Lê a tabela limpa; baixa de novo se pedido ou se ainda não existir."""
    raw = PASTA_RAW / f"br1_{ano}.json"
    if atualizar or not raw.exists():
        baixar(ano, raw)
    df = limpar(raw)
    PASTA_PROC.mkdir(parents=True, exist_ok=True)
    df.to_csv(PASTA_PROC / "partidas.csv", index=False)
    return df


if __name__ == "__main__":
    tabela = carregar(atualizar=True)
    feitos = int(tabela["disputado"].sum())
    print(f"{len(tabela)} jogos no calendário, {feitos} já disputados.")
