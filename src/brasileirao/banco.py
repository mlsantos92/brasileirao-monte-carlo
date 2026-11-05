"""Carrega as partidas num banco SQLite e roda as consultas de sql/."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
PASTA_SQL = RAIZ / "sql"
BANCO = RAIZ / "data" / "processed" / "brasileirao.db"


def criar_banco(jogos: pd.DataFrame, caminho: Path = BANCO) -> sqlite3.Connection:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(caminho)
    con.executescript((PASTA_SQL / "01_schema.sql").read_text(encoding="utf-8"))
    t = jogos.copy()
    t["data"] = t["data"].dt.strftime("%Y-%m-%d")
    t["disputado"] = t["disputado"].astype(int)
    t["gols_mandante"] = t["gols_mandante"].astype(object).where(t["disputado"] == 1, None)
    t["gols_visitante"] = t["gols_visitante"].astype(object).where(t["disputado"] == 1, None)
    t.to_sql("partidas", con, if_exists="append", index=False)
    return con


def consultas(arquivo: str = "02_analises.sql") -> dict[str, str]:
    """Separa o arquivo SQL em consultas nomeadas por '-- name: x'."""
    texto = (PASTA_SQL / arquivo).read_text(encoding="utf-8")
    partes = re.split(r"^-- name: (\w+)\s*$", texto, flags=re.M)
    return {partes[i]: partes[i + 1].strip() for i in range(1, len(partes), 2)}


def rodar(con: sqlite3.Connection, nome: str) -> pd.DataFrame:
    return pd.read_sql_query(consultas()[nome], con)
