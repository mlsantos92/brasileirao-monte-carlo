-- Consultas analíticas. Cada bloco começa com "-- name: <nome>",
-- e o script src/brasileirao/banco.py roda todas e salva os resultados.

-- name: classificacao
-- Tabela com critérios de desempate: pontos, vitórias, saldo, gols pró.
SELECT
    RANK() OVER (ORDER BY SUM(CASE WHEN gp > gc THEN 3 WHEN gp = gc THEN 1 ELSE 0 END) DESC,
                          SUM(gp > gc) DESC, SUM(gp - gc) DESC, SUM(gp) DESC) AS pos,
    clube,
    COUNT(*)                                                   AS j,
    SUM(CASE WHEN gp > gc THEN 3 WHEN gp = gc THEN 1 ELSE 0 END) AS pts,
    SUM(gp > gc)  AS v,
    SUM(gp = gc)  AS e,
    SUM(gp < gc)  AS d,
    SUM(gp)       AS gp,
    SUM(gc)       AS gc,
    SUM(gp - gc)  AS sg
FROM desempenho
GROUP BY clube
ORDER BY pos;

-- name: casa_fora
-- Aproveitamento (% dos pontos possíveis) em casa e fora, e a diferença.
SELECT
    clube,
    ROUND(100.0 * SUM(CASE WHEN mando = 'casa' THEN (gp > gc) * 3 + (gp = gc) END)
          / (3 * SUM(mando = 'casa')), 1) AS aprov_casa,
    ROUND(100.0 * SUM(CASE WHEN mando = 'fora' THEN (gp > gc) * 3 + (gp = gc) END)
          / (3 * SUM(mando = 'fora')), 1) AS aprov_fora,
    ROUND(100.0 * SUM(CASE WHEN mando = 'casa' THEN (gp > gc) * 3 + (gp = gc) END)
          / (3 * SUM(mando = 'casa'))
        - 100.0 * SUM(CASE WHEN mando = 'fora' THEN (gp > gc) * 3 + (gp = gc) END)
          / (3 * SUM(mando = 'fora')), 1) AS diferenca
FROM desempenho
GROUP BY clube
ORDER BY diferenca DESC;

-- name: forma_ultimos_5
-- Pontos nos últimos 5 jogos e sequência (V/E/D, do mais antigo ao mais recente).
WITH numerados AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY clube ORDER BY data DESC, jogo_id DESC) AS n,
           CASE WHEN gp > gc THEN 'V' WHEN gp = gc THEN 'E' ELSE 'D' END AS res
    FROM desempenho
)
SELECT clube,
       SUM(CASE WHEN res = 'V' THEN 3 WHEN res = 'E' THEN 1 ELSE 0 END) AS pts_5,
       GROUP_CONCAT(res, '') AS sequencia
FROM (SELECT * FROM numerados WHERE n <= 5 ORDER BY clube, data, jogo_id)
GROUP BY clube
ORDER BY pts_5 DESC, clube;

-- name: evolucao_pontos
-- Pontos acumulados jogo a jogo (função de janela com soma corrente).
SELECT clube, data,
       ROW_NUMBER() OVER (PARTITION BY clube ORDER BY data, jogo_id) AS jogo,
       SUM(CASE WHEN gp > gc THEN 3 WHEN gp = gc THEN 1 ELSE 0 END)
           OVER (PARTITION BY clube ORDER BY data, jogo_id) AS pts_acumulados
FROM desempenho
ORDER BY clube, jogo;

-- name: resultados_liga
-- Retrato da liga: % de vitórias do mandante, empates e vitórias do visitante.
SELECT
    COUNT(*) AS jogos,
    ROUND(100.0 * AVG(gols_mandante > gols_visitante), 1) AS pct_mandante,
    ROUND(100.0 * AVG(gols_mandante = gols_visitante), 1) AS pct_empate,
    ROUND(100.0 * AVG(gols_mandante < gols_visitante), 1) AS pct_visitante,
    ROUND(AVG(gols_mandante + gols_visitante), 2)         AS gols_por_jogo
FROM partidas
WHERE disputado = 1;

-- name: calendario_restante
-- Jogos que faltam para cada clube e a média de pontos por jogo dos adversários
-- (uma medida simples de dificuldade da tabela).
WITH ppg AS (
    SELECT clube, 1.0 * SUM(CASE WHEN gp > gc THEN 3 WHEN gp = gc THEN 1 ELSE 0 END) / COUNT(*) AS ppg
    FROM desempenho GROUP BY clube
),
restantes AS (
    SELECT mandante AS clube, visitante AS adversario FROM partidas WHERE disputado = 0
    UNION ALL
    SELECT visitante, mandante FROM partidas WHERE disputado = 0
)
SELECT r.clube,
       COUNT(*) AS jogos_restantes,
       ROUND(AVG(p.ppg), 2) AS ppg_medio_adversarios
FROM restantes r JOIN ppg p ON p.clube = r.adversario
GROUP BY r.clube
ORDER BY ppg_medio_adversarios DESC;
