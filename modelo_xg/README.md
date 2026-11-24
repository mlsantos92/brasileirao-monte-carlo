# Versão 2: modelo com xG, jogadores e escalações prováveis

Segunda versão do modelo, usada no painel de acompanhamento da reta final do Brasileirão 2026. A primeira versão (pasta `src/`) usa só placares. Esta troca os gols por **chances criadas e cedidas (xG e grandes chances, por mando)** e avalia cada clube **jogador a jogador**, a partir do XI provável.

Retrato de 24/11/2026: 36ª rodada quase completa (falta Atlético-MG x Corinthians, em 25/11).

## Resultado atual

| Clube | Pontos | Rebaixamento |
|---|---|---|
| Remo | 32 | 100% |
| Chapecoense | 21 | 100% |
| Internacional | 38 | 95,9% |
| Grêmio | 41 | 36,6% |
| Mirassol | 41 | 35,8% |
| Corinthians | 40 | 26,0% |
| Botafogo | 43 | 5,7% |

Tabela completa: `probabilidades_xg.csv`.

**Final da Copa do Brasil** (Grêmio x Palmeiras, jogo único em 06/12, no Mané Garrincha, em Brasília):

| | Grêmio | Palmeiras |
|---|---|---|
| Gols esperados | 0,82 | 1,33 |
| Vitória nos 90 minutos | 22,5% | 47,6% |
| Título | **35,7%** | **64,3%** |

O empate nos 90 minutos sai em 29,9% das simulações, e a decisão chega aos pênaltis em 17,8%.

## Como o modelo funciona

1. **Perfil de cada clube.** Chances criadas e cedidas em casa e fora (xG e grandes chances) entram em desvios-padrão da liga. Jogos atípicos pesam menos: 1 até 1 DP, 0,7 entre 1 e 2 DP, 0,4 acima de 2 DP. Jogos com expulsão antes dos 70 minutos ficam de fora.
2. **Fase recente.** Conta os últimos 6 jogos (3 em casa e 3 fora), em todas as competições, com xG criado e cedido e pontos (`recente.py`).
3. **Descanso.** Dias entre partidas de todas as competições, com rodízio antes de jogo decisivo de copa.
4. **Escalação provável** (`escal.py`):
   - **XI:** o goleiro e os 10 jogadores de linha que mais começaram os últimos 5 jogos, sem média. Lesionados e suspensos são trocados pelo reserva da mesma posição com mais jogos como titular.
   - **Goleiro:** entra o mérito ajustado do titular, explicado abaixo.
   - **Finalização:** gols − xG dos finalizadores do XI, sem pênaltis, com encolhimento.
   - **Criação:** (npxG + 0,8·xA) por 90 minutos do XI, comparado ao XI mais usado.
   - **Linha:** xG impedido pelos defensores.
   - **Peso:** 70% vem da escalação e 30% da temporada.
5. **Monte Carlo.** São 100 mil simulações do restante do campeonato, com Poisson e correção de placares baixos (rho 0,08), mais variação de forma por clube em cada simulação (`sim39.py`).

### Mérito dos goleiros (`temporada/gk2.py`, `gk3.py`)

- **Quem estava no gol:** a atribuição de cada chute ao goleiro usa a escalação e as substituições de cada jogo. Cinco jogos com o goleiro errado no FotMob foram conferidos com a súmula e a imprensa.
- **Gols evitados:** xGOT − gols sofridos, sem pênaltis, com encolhimento bayesiano empírico.
- **Pênaltis:** um pênalti defendido vale +0,79 (o xG do pênalti), seja por sorte ou por mérito. Um pênalti na trave ou para fora vale 10% disso (+0,08).

### Raio-X da temporada (`temporada/`)

São 359 jogos do FotMob, analisados jogador a jogador:
- **Finalização:** gols − xG e colocação do chute (xGOT).
- **Criação:** assistências e xA. O xA conta como parte do ataque, junto do xG.
- **Defesa:** bloqueios, cortes sobre a linha e xG impedido por defensor.
- **Duelos:** atacante contra goleiro, chute a chute.

A tabela de jogadores (`dash/jogadores.json`) traz todos os jogadores de linha com 300 minutos ou mais e todos os goleiros, com cada uma dessas métricas.

### Final da Copa do Brasil (`final_cdb.py`)

- **Campo neutro:** a média dos dois mandos, com o XI titular, o goleiro, os finalizadores e a fase recente de cada clube.
- **Prorrogação:** 30 minutos, com gols a 85% do ritmo normal.
- **Pênaltis:** 50% para cada lado.

## Backtest da temporada

Os 359 jogos foram previstos em ordem cronológica, cada um só com os jogos anteriores (`temporada/wf*.py`). Os parâmetros foram escolhidos no 1º turno e conferidos no 2º turno, que o ajuste não viu. O resultado e os parâmetros recomendados para 2027 estão em `temporada/wf_out.json` e `temporada/wf_best.json`.

## Como rodar

```bash
cd modelo_xg
python sim39.py      # simulação do campeonato: resultado39.json, simj39.json, dash/simulador.json
python final_cdb.py  # final da Copa do Brasil: dash/final_cdb.json
```

O `sim39.py` carrega a base de `sim.py` (tabela e calendário) e os dados de `v8/`, `v9/`, `v10/` e dos arquivos `.txt`: forma, desfalques, descanso e viagem. Os arquivos em `dash/` são os dados do painel.

## Limitações

- O xG soma cada chute como independente. Um volume grande de chutes de baixa qualidade infla o número sem perigo real. As grandes chances no perfil amortecem parte disso, mas a fase recente usa só o xG.
- O XI provável é uma aposta: muda com lesões e escolhas do técnico na semana do jogo.
- A atribuição de goleiro do FotMob tem erros pontuais, corrigidos só nos casos conferidos.

Fonte dos dados: FotMob (xG, xGOT, chutes, escalações e eventos de jogo).
