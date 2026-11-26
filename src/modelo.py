"""Modelo analítico em estrela a partir das tabelas limpas.

Fatos : fato_pedidos (grão = pedido) e fato_itens (grão = item do pedido)
Dims  : dim_cliente, dim_produto, dim_vendedor, dim_data
Definições de negócio: ver docs/modelo_dados.md
"""
import pandas as pd

STATUS_VALIDOS = ["delivered", "shipped", "invoiced", "processing", "approved", "created"]  # exclui canceled/unavailable
INICIO_ANALISE, FIM_ANALISE = "2017-01-01", "2018-08-31"  # janela com volume relevante (ver decisoes_limpeza.md)

MESES_PT = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
            7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
DIAS_PT = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}


def montar_dim_data(inicio="2016-09-01", fim="2018-12-31") -> pd.DataFrame:
    d = pd.DataFrame({"data": pd.date_range(inicio, fim, freq="D")})
    d["chave_data"] = d["data"].dt.strftime("%Y%m%d").astype(int)
    d["ano"] = d["data"].dt.year
    d["trimestre"] = d["data"].dt.quarter
    d["mes"] = d["data"].dt.month
    d["nome_mes"] = d["mes"].map(MESES_PT)
    d["ano_mes"] = d["data"].dt.strftime("%Y-%m")
    d["ano_mes_chave"] = d["ano"] * 100 + d["mes"]  # coluna de ordenação para ano_mes no Power BI
    d["dia_semana_num"] = d["data"].dt.weekday
    d["nome_dia_semana"] = d["dia_semana_num"].map(DIAS_PT)
    d["periodo_analise"] = d["data"].between(INICIO_ANALISE, FIM_ANALISE)
    return d


def _com_coordenadas(tabela: pd.DataFrame, geo: pd.DataFrame) -> pd.DataFrame:
    """Anexa latitude/longitude (por prefixo de CEP) à tabela de clientes ou vendedores."""
    return tabela.merge(geo[["cep_prefixo", "latitude", "longitude"]], on="cep_prefixo", how="left")


def montar_dim_cliente(clientes, geo) -> pd.DataFrame:
    return _com_coordenadas(clientes, geo)


def montar_dim_vendedor(vendedores, geo) -> pd.DataFrame:
    return _com_coordenadas(vendedores, geo)


def montar_dim_produto(produtos) -> pd.DataFrame:
    cols = ["id_produto", "nome_categoria", "categoria_en", "qtd_fotos", "peso_g",
            "comprimento_cm", "altura_cm", "largura_cm"]
    return produtos[cols].copy()


def _resumo_pagamentos(pagamentos) -> pd.DataFrame:
    """Resume pagamentos por pedido: forma principal (maior valor), parcelas máximas, nº de formas."""
    p = pagamentos.sort_values("valor_pagamento", ascending=False)
    principal = p.drop_duplicates("id_pedido").set_index("id_pedido")["tipo_pagamento"].rename("forma_pagamento_principal")
    agg = pagamentos.groupby("id_pedido").agg(valor_pagamento=("valor_pagamento", "sum"),
                                              parcelas_max=("parcelas", "max"),
                                              qtd_formas_pagamento=("tipo_pagamento", "nunique"))
    return agg.join(principal).reset_index()


def montar_fato_pedidos(pedidos, itens, pagamentos, avaliacoes, clientes) -> pd.DataFrame:
    f = pedidos.copy()
    f["id_cliente_unico"] = f["id_cliente"].map(clientes.set_index("id_cliente")["id_cliente_unico"])
    f["data_compra"] = f["datahora_compra"].dt.normalize()
    f["chave_data"] = f["data_compra"].dt.strftime("%Y%m%d").astype(int)

    # Métricas de prazo: só para pedidos entregues COM data de entrega (8 entregues não têm)
    foi_entregue = f["status_pedido"].eq("delivered") & f["data_entrega_cliente"].notna()
    dias_entrega = (f["data_entrega_cliente"] - f["datahora_compra"]).dt.total_seconds() / 86400
    # Atraso comparado por DATA (a estimativa vem sempre às 00:00; comparar horários marcaria
    # como atrasado quem recebeu no próprio dia previsto)
    atraso = (f["data_entrega_cliente"].dt.normalize() - f["data_entrega_estimada"].dt.normalize()).dt.days
    f["dias_entrega"] = dias_entrega.where(foi_entregue).round(2)
    f["dias_atraso"] = atraso.where(foi_entregue)                          # >0 = atrasou
    f["atrasado"] = (f["dias_atraso"] > 0).where(foi_entregue).astype("boolean")  # <NA> fora do universo de entregues
    f["dias_estimados"] = ((f["data_entrega_estimada"] - f["datahora_compra"])
                           .dt.total_seconds() / 86400).round(2)

    it = itens.groupby("id_pedido").agg(qtd_itens=("id_item", "count"), receita=("preco", "sum"),
                                        frete=("valor_frete", "sum"), qtd_vendedores=("id_vendedor", "nunique"))
    f = (f.merge(it, on="id_pedido", how="left")
          .merge(_resumo_pagamentos(pagamentos), on="id_pedido", how="left")
          .merge(avaliacoes[["id_pedido", "nota_avaliacao"]], on="id_pedido", how="left"))
    cols_soma = ["qtd_itens", "receita", "frete", "qtd_vendedores"]
    f[cols_soma] = f[cols_soma].fillna(0)
    f["pedido_valido"] = f["status_pedido"].isin(STATUS_VALIDOS)

    # Recorrência: ordem de compra de cada pessoa (id_cliente_unico) entre pedidos válidos
    v = f[f["pedido_valido"]].sort_values(["id_cliente_unico", "datahora_compra"])
    f["seq_pedido_cliente"] = v.groupby("id_cliente_unico").cumcount() + 1
    n_pedidos = v.groupby("id_cliente_unico")["id_pedido"].transform("count")
    f["cliente_recorrente"] = (n_pedidos > 1).reindex(f.index).astype("boolean")  # pessoa com 2+ pedidos válidos
    primeira = v.groupby("id_cliente_unico")["data_compra"].transform("min").dt.to_period("M").dt.to_timestamp()
    f["mes_coorte"] = primeira.reindex(f.index)
    return f


def montar_fato_itens(itens, fato_pedidos) -> pd.DataFrame:
    f = itens.copy()
    f["receita"] = f["preco"]  # decisão: faturamento = preço do produto; frete é coluna separada
    ped = fato_pedidos[["id_pedido", "chave_data", "status_pedido", "pedido_valido", "atrasado", "dias_atraso"]]
    return f.merge(ped, on="id_pedido", how="left")
