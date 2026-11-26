"""Executa a limpeza e grava Parquet em data/processed/clean/. Uso: python -m src.run_clean"""
from .config import PROCESSED
from .load import load_all
from . import clean as c

d = load_all()
out = {
    "orders": c.clean_orders(d["orders"]),
    "items": c.clean_items(d["items"]),
    "reviews": c.clean_reviews(d["reviews"]),
    "products": c.clean_products(d["products"], d["category_translation"]),
    "geolocation": c.clean_geolocation(d["geolocation"]),
    "payments": d["payments"],
    "customers": d["customers"],
    "sellers": d["sellers"],
}
pasta = PROCESSED / "clean"; pasta.mkdir(parents=True, exist_ok=True)
for nome, df in out.items():
    df.to_parquet(pasta / f"{nome}.parquet", index=False)
    print(f"{nome:12s} {df.shape}")
