"""Gera o modelo estrela em data/processed/model/. Uso: python -m src.executar_modelo (após src.executar_limpeza)"""
import pandas as pd
from .config import PROCESSADO
from . import modelo as md

LIMPO = PROCESSADO / "clean"


def ler(nome):
    return pd.read_parquet(LIMPO / f"{nome}.parquet")


pedidos, itens, pagamentos, avaliacoes, clientes, vendedores, produtos, geo = (
    ler(n) for n in ["pedidos", "itens", "pagamentos", "avaliacoes", "clientes", "vendedores", "produtos",
                     "geolocalizacao"])

fato_pedidos = md.montar_fato_pedidos(pedidos, itens, pagamentos, avaliacoes, clientes)
saida = {
    "fato_pedidos": fato_pedidos,
    "fato_itens": md.montar_fato_itens(itens, fato_pedidos),
    "dim_cliente": md.montar_dim_cliente(clientes, geo),
    "dim_produto": md.montar_dim_produto(produtos),
    "dim_vendedor": md.montar_dim_vendedor(vendedores, geo),
    "dim_data": md.montar_dim_data(),
}
pasta = PROCESSADO / "model"
pasta.mkdir(parents=True, exist_ok=True)
for nome, df in saida.items():
    df.to_parquet(pasta / f"{nome}.parquet", index=False)
    print(f"{nome:13s} {df.shape}")
