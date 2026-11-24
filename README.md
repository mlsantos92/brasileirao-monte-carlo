# Brasileirão 2026 — quem cai?

Modelo estatístico que estima a probabilidade de título, vaga e rebaixamento de cada clube da Série A, combinando um **modelo de gols Dixon-Coles** com **50 mil simulações Monte Carlo** do restante do campeonato.

![Probabilidade de rebaixamento](outputs/risco_rebaixamento.png)

> Resultados com dados públicos até a 28ª rodada. Rode `python -m brasileirao.pipeline --atualizar` para usar os placares mais recentes da fonte.

> **Versão 2 (24/11/2026):** a pasta [`modelo_xg/`](modelo_xg/) traz o modelo atual, com xG e grandes chances por mando, fase recente, descanso, escalações prováveis avaliadas jogador a jogador (goleiro, finalizadores, criação e defesa), mérito dos goleiros conferido com a súmula e a simulação da final da Copa do Brasil (Grêmio x Palmeiras). Rebaixamento hoje: Internacional 95,9%, Grêmio 36,6%, Mirassol 35,8% e Corinthians 26,0%.

## Por que este projeto

Trabalho com planejamento financeiro, onde o dia a dia é transformar incerteza em probabilidades e cenários. Este projeto aplica o mesmo raciocínio a um problema público, com dados abertos, para mostrar o ciclo completo de um trabalho de dados: coleta, limpeza, SQL, modelagem, **validação honesta** e comunicação dos resultados.

## O que tem aqui

| Etapa | Onde | O que faz |
|---|---|---|
| Coleta e limpeza | `src/brasileirao/dados.py` | Baixa o JSON público, padroniza nomes e placares, valida (20 clubes, 380 jogos, sem duplicatas) |
| SQL | `sql/` + `banco.py` | Banco SQLite com tabela de fatos e visão por clube; classificação com desempate, casa x fora, forma recente com funções de janela, dificuldade do calendário |
| Modelo | `modelo.py` | Dixon-Coles (Poisson com correção de placares baixos), ajustado por máxima verossimilhança ponderada com `scipy` |
| Validação | `avaliacao.py` | Backtest rolante: treina até a rodada *r*, prevê a *r+1*; compara com referências ingênuas por log loss e Brier |
| Simulação | `simulacao.py` | Monte Carlo vetorizado em NumPy (50 mil temporadas em ~1 s), com critérios oficiais de desempate |
| Análise | `notebooks/analise.ipynb` | A história completa, passo a passo, com tabelas e gráficos |
| Testes | `tests/` | Integridade dos dados, coerência da tabela e da simulação (`pytest`) |

## Como o modelo funciona

Os gols de cada lado seguem uma Poisson:

```
log(gols esperados do mandante)  = μ + mando + ataque[mandante]  + defesa[visitante]
log(gols esperados do visitante) = μ         + ataque[visitante] + defesa[mandante]
```

A correção de Dixon & Coles (1997) ajusta a chance de 0x0, 1x0, 0x1 e 1x1. Uma penalidade ridge evita forças extremas com poucos jogos.

**Jogos atípicos pesam menos.** O saldo de cada jogo é medido em desvios-padrão da média da liga: até 1 DP o jogo vale 1, entre 1 e 2 DP vale 0,7, acima de 2 DP vale 0,4. Uma goleada fora da curva não redefine a força de um time.

## Decisões tomadas com dados, não no olho

Testei três hipóteses de modelagem no mesmo backtest rolante (157 jogos previstos sem que o modelo os tivesse visto):

| Hipótese | Resultado | Decisão |
|---|---|---|
| Peso menor para jogos atípicos | melhora em todas as combinações | **mantido** |
| Peso maior para jogos recentes (meia-vida 30–120 dias) | piora: com ~280 jogos e só gols, descarta informação demais | **descartado** |
| Vantagem de casa própria de cada clube | não melhora: a diferença casa/fora vista na tabela é, em boa parte, ruído de amostra | **descartado** |

Desempenho do modelo final (menor = melhor):

| | Log loss | Brier |
|---|---|---|
| **Modelo Dixon-Coles** | **1,064** | **0,648** |
| Frequência histórica (mandante/empate/visitante) | 1,078 | 0,652 |
| Uniforme (1/3 para cada) | 1,099 | 0,667 |

O ganho é real, mas modesto. Isso é esperado no futebol, um esporte de poucos gols, e é exatamente o que motiva a próxima versão com xG.

## Validação fora da amostra: previsto x aconteceu

As previsões jogo a jogo em `outputs/previsoes_jogos.csv` foram geradas com os placares até 20/09/2026 (28ª rodada) e ficaram congeladas no repositório. Depois disso foram disputados 62 jogos: as rodadas 29 a 34 e 2 jogos adiados da 21ª. O modelo nunca viu nenhum deles, e o teste `tests/test_validacao.py` confere que todos são posteriores ao corte. Rodar o modelo de novo sobre o mesmo retrato reproduz as previsões exatamente.

| 62 jogos após o corte | Log loss | Brier | Acerto do favorito | Placar exato |
|---|---|---|---|---|
| **Modelo Dixon-Coles** | **0,931** | **0,549** | **62,9%** | 14,5% |
| Frequência do treino | 1,005 | 0,600 | 56,5% | – |
| Uniforme (1/3) | 1,099 | 0,667 | 56,5% | – |

- **O modelo bateu as duas referências em todas as métricas.** Em seis das sete rodadas, a log loss ficou abaixo do palpite uniforme. A exceção são os 2 jogos adiados da 21ª, que ficaram no nível do palpite uniforme.
- **O desempenho foi melhor do que no backtest** (log loss 1,064). Com só 62 jogos, parte disso é sorte. A conclusão segura é que o modelo continuou acima das referências fora da amostra.

![Probabilidade dada ao resultado real](outputs/validacao_jogos.png)

![Calibração](outputs/validacao_calibracao.png)

**Calibração:** os eventos com probabilidade prevista entre 40% e 60% aconteceram mais do que o previsto (53% e 80%). Os eventos com menos de 30% aconteceram menos (7% e 18%). O modelo foi **cauteloso demais**: os favoritos ganharam mais do que ele dizia. A penalidade ridge e o peso menor para goleadas puxam as forças para a média, e esse é o efeito esperado. Com 62 jogos, a amostra ainda é pequena para mexer nesses parâmetros.

![Pontos esperados x reais](outputs/validacao_pontos.png)

**Pontos por clube:** a correlação entre os pontos esperados e os conquistados nesses 62 jogos foi de 0,66. As maiores surpresas positivas foram Cruzeiro (+6), Palmeiras (+5) e Flamengo (+4,5). As negativas foram Athletico-PR (−4,8) e Coritiba (−3,7).

**Rebaixamento:** os quatro clubes com maior risco de queda no corte eram Chapecoense (99,9%), Remo (96,5%), Internacional (59,1%) e Grêmio (57,7%). Após a 34ª rodada, três deles estão no Z4 (Chapecoense, Remo e Grêmio). O Internacional está em 16º, empatado em pontos com o Vitória, e o Corinthians (17,4% no corte) ocupa a 17ª posição.

Placares após o corte: [ValorFinal](https://valorfinal.com.br/brasileirao/2026) (dados do football-data.org, CC BY 4.0), conferidos com a imprensa em jogos de amostra, porque a fonte aberta original parou de ser atualizada em 20/09. Código em `src/brasileirao/validacao_fora_amostra.py`; números em `outputs/validacao_*.csv`.

## Como rodar

```bash
git clone https://github.com/mlsantos92/brasileirao-monte-carlo
cd brasileirao-monte-carlo
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .

python -m brasileirao.pipeline --atualizar   # baixa dados, roda tudo e grava outputs/
python -m brasileirao.validacao_fora_amostra # compara as previsões congeladas com os placares pós-corte
pytest                                       # testes
jupyter notebook notebooks/analise.ipynb     # análise completa
```

Saídas em `outputs/`: probabilidades por clube, previsões jogo a jogo, forças estimadas, curva de corte do rebaixamento, resultados do backtest e de cada consulta SQL.

## Limitações

- Usa só placares: não sabe de lesões, suspensões, troca de técnico, viagens ou copas.
- Cada jogo simulado é independente; não há efeito de "momento" dentro da simulação.
- A fonte pública pode estar algumas rodadas atrás do campeonato real.

## Próximos passos

- ~~Trocar gols por **xG e grandes chances por mando**, métricas menos ruidosas.~~ Feito em [`modelo_xg/`](modelo_xg/).
- Ajustar a força da penalidade ridge, já que a validação fora da amostra mostrou um modelo cauteloso demais com os favoritos.
- ~~Testar descanso entre jogos e desfalques.~~ Descanso, desfalques e escalações prováveis já estão em [`modelo_xg/`](modelo_xg/); falta passá-los pelo backtest da temporada inteira.

## Sobre o uso de IA

O projeto foi desenvolvido com IA como copiloto de código. As perguntas, as hipóteses de modelagem (pesos para jogos atípicos, recência, mando por clube), os critérios de validação e a interpretação dos resultados são meus; a IA acelerou a escrita da sintaxe. Todo o código é testado e reproduzível.

## Dados

Placares: [openfootball/football.json](https://github.com/openfootball/football.json), domínio público.
