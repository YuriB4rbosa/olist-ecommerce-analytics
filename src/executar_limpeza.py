"""Executa a limpeza e grava Parquet em data/processed/clean/. Uso: python -m src.executar_limpeza"""
from .config import PROCESSADO
from .carga import carregar_tudo
from . import limpeza as lp

d = carregar_tudo()
saida = {
    "pedidos": lp.limpar_pedidos(d["pedidos"]),
    "itens": lp.limpar_itens(d["itens"]),
    "avaliacoes": lp.limpar_avaliacoes(d["avaliacoes"]),
    "produtos": lp.limpar_produtos(d["produtos"], d["traducao_categorias"]),
    "geolocalizacao": lp.limpar_geolocalizacao(d["geolocalizacao"]),
    "pagamentos": d["pagamentos"],
    "clientes": d["clientes"],
    "vendedores": d["vendedores"],
}
pasta = PROCESSADO / "clean"
pasta.mkdir(parents=True, exist_ok=True)
for nome, df in saida.items():
    df.to_parquet(pasta / f"{nome}.parquet", index=False)
    print(f"{nome:15s} {df.shape}")
