"""Gera o modelo estrela em data/processed/model/. Uso: python -m src.run_model (após src.run_clean)"""
import pandas as pd
from .config import PROCESSED
from . import model as m

C = PROCESSED / "clean"
ld = lambda n: pd.read_parquet(C / f"{n}.parquet")
orders, items, pay, rev, cust, sell, prod, geo = (ld(n) for n in
    ["orders", "items", "payments", "reviews", "customers", "sellers", "products", "geolocation"])

fo = m.build_fact_orders(orders, items, pay, rev, cust)
out = {
    "fact_orders": fo,
    "fact_items": m.build_fact_items(items, fo),
    "dim_customer": m.build_dim_customer(cust, geo),
    "dim_product": m.build_dim_product(prod),
    "dim_seller": m.build_dim_seller(sell, geo),
    "dim_date": m.build_dim_date(),
}
pasta = PROCESSED / "model"; pasta.mkdir(parents=True, exist_ok=True)
for nome, df in out.items():
    df.to_parquet(pasta / f"{nome}.parquet", index=False)
    print(f"{nome:13s} {df.shape}")
