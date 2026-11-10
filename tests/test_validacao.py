"""Validação fora da amostra: as previsões congeladas cobrem os jogos reais e batem as referências."""
from brasileirao import validacao_fora_amostra as v


def test_previsoes_cobrem_resultados_pos_corte():
    df, treino = v.carregar()
    assert len(df) == 62
    import pandas as pd
    assert treino["data"].max() < pd.to_datetime(df["data"]).min()  # nenhum jogo avaliado entrou no treino


def test_modelo_melhor_que_referencias():
    df, treino = v.carregar()
    m = v.avaliar(df, treino)
    assert m.loc["modelo Dixon-Coles", "log_loss"] < m.loc["frequência do treino", "log_loss"] < m.loc["uniforme (1/3)", "log_loss"]
