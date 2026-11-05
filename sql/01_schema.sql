-- Esquema do banco SQLite (data/processed/brasileirao.db).
-- Uma tabela de fatos (partidas) e uma visão "uma linha por clube por jogo",
-- que simplifica quase todas as análises.

DROP TABLE IF EXISTS partidas;
CREATE TABLE partidas (
    jogo_id         INTEGER PRIMARY KEY,
    rodada          INTEGER NOT NULL,
    data            TEXT    NOT NULL,          -- AAAA-MM-DD
    mandante        TEXT    NOT NULL,
    visitante       TEXT    NOT NULL,
    gols_mandante   INTEGER,                   -- NULL = jogo ainda não disputado
    gols_visitante  INTEGER,
    disputado       INTEGER NOT NULL CHECK (disputado IN (0, 1)),
    UNIQUE (mandante, visitante)
);

DROP VIEW IF EXISTS desempenho;
CREATE VIEW desempenho AS
SELECT jogo_id, rodada, data, mandante AS clube, visitante AS adversario,
       'casa' AS mando, gols_mandante AS gp, gols_visitante AS gc
FROM partidas WHERE disputado = 1
UNION ALL
SELECT jogo_id, rodada, data, visitante, mandante,
       'fora', gols_visitante, gols_mandante
FROM partidas WHERE disputado = 1;
