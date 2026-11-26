"""Exporta o modelo estrela pronto para importar no Power BI.

Uso (após src.run_clean e src.run_model):  python -m src.export_powerbi
Saída: data/processed/powerbi/*.csv  (UTF-8 com BOM, separador ',', decimal '.', datas ISO)
       data/processed/powerbi/*.parquet (mesmos dados, com tipos preservados)

Decisões de design (detalhes em docs/powerbi_modelo.md):
- fact_items NÃO carrega date_key/flags de pedido: evita dois caminhos de filtro desde dim_date
  (dim_date -> fact_orders -> fact_items e dim_date -> fact_items) e relacionamentos ambíguos.
- Receita vive só em fact_items.revenue (fonte única); fact_orders não repete revenue/freight.
- Flags booleanas viram 0/1 (nulo quando não se aplica; em DAX teste sempre '= 1', nunca '= 0') para AVERAGE/SUM funcionarem direto em DAX.
"""
import pandas as pd
from .config import PROCESSED

MODELO = PROCESSED / "model"
SAIDA = PROCESSED / "powerbi"

MESES_PT = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
            7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
DIAS_PT = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}


def _flag(s: pd.Series) -> pd.Series:
    """boolean (True/False/<NA>) -> Int8 (1/0/<NA>)."""
    return s.astype("boolean").astype("Int8")


def prep_fact_orders(fo: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame({
        "order_id": fo["order_id"],
        "customer_id": fo["customer_id"],
        "customer_unique_id": fo["customer_unique_id"],
        "date_key": fo["date_key"],
        "order_status": fo["order_status"],
        "is_valid_order": _flag(fo["is_valid_order"]),
        "purchase_timestamp": fo["order_purchase_timestamp"],
        "delivered_customer_date": fo["order_delivered_customer_date"],
        "estimated_delivery_date": fo["order_estimated_delivery_date"],
        "delivery_days": fo["delivery_days"],
        "estimated_days": fo["estimated_days"],
        "delay_days": fo["delay_days"],
        "is_delivered": _flag(fo["is_late"].notna()),  # 1 = entregue c/ data (nunca nulo; em DAX BLANK()=0, então não filtre is_late = 0)
        "is_late": _flag(fo["is_late"]),
        "items_qty": fo["items_qty"].astype(int),
        "payment_value": fo["payment_value"],
        "installments_max": fo["installments_max"].astype("Int64"),
        "payment_type_main": fo["payment_type_main"],
        "n_payment_methods": fo["n_payment_methods"].astype("Int64"),
        "review_score": fo["review_score"].astype("Int64"),
        "customer_order_seq": fo["customer_order_seq"].astype("Int64"),
        "is_first_order": _flag(fo["customer_order_seq"].eq(1).where(fo["customer_order_seq"].notna())),
        "is_recurring_customer": _flag(fo["is_recurring_customer"]),
        "cohort_month": fo["cohort_month"],
    })
    return out


def prep_fact_items(fi: pd.DataFrame) -> pd.DataFrame:
    return fi[["order_id", "order_item_id", "product_id", "seller_id", "revenue", "freight_value"]].copy()


def prep_dim_date(dd: pd.DataFrame) -> pd.DataFrame:
    d = dd.copy()
    d["month_name"] = d["month"].map(MESES_PT)
    d["weekday_name"] = d["weekday_num"].map(DIAS_PT)
    d["year_month_key"] = d["year"] * 100 + d["month"]  # coluna de ordenação para year_month
    d["in_analysis_period"] = d["in_analysis_period"].astype("Int8")
    return d[["date_key", "date", "year", "quarter", "month", "month_name", "year_month", "year_month_key",
              "weekday_num", "weekday_name", "in_analysis_period"]]


def prep_dim_customer(dc: pd.DataFrame) -> pd.DataFrame:
    return dc.rename(columns={"customer_zip_code_prefix": "zip_prefix", "customer_city": "city",
                              "customer_state": "state"})[
        ["customer_id", "customer_unique_id", "zip_prefix", "city", "state", "lat", "lng"]]


def prep_dim_seller(ds: pd.DataFrame) -> pd.DataFrame:
    return ds.rename(columns={"seller_zip_code_prefix": "zip_prefix", "seller_city": "city",
                              "seller_state": "state"})[["seller_id", "zip_prefix", "city", "state", "lat", "lng"]]


def prep_dim_product(dp: pd.DataFrame) -> pd.DataFrame:
    return dp[["product_id", "category_en", "product_category_name", "product_photos_qty", "product_weight_g"]] \
        .rename(columns={"product_category_name": "category_pt"})


def main():
    ld = lambda n: pd.read_parquet(MODELO / f"{n}.parquet")
    tabelas = {
        "fact_orders": prep_fact_orders(ld("fact_orders")),
        "fact_items": prep_fact_items(ld("fact_items")),
        "dim_date": prep_dim_date(ld("dim_date")),
        "dim_customer": prep_dim_customer(ld("dim_customer")),
        "dim_seller": prep_dim_seller(ld("dim_seller")),
        "dim_product": prep_dim_product(ld("dim_product")),
    }
    SAIDA.mkdir(parents=True, exist_ok=True)
    for nome, df in tabelas.items():
        df.to_csv(SAIDA / f"{nome}.csv", index=False, encoding="utf-8-sig", date_format="%Y-%m-%d %H:%M:%S")
        df.to_parquet(SAIDA / f"{nome}.parquet", index=False)
        mb = (SAIDA / f"{nome}.csv").stat().st_size / 1e6
        print(f"{nome:13s} {df.shape[0]:>8,} linhas x {df.shape[1]:>2} colunas  ({mb:.1f} MB csv)")


if __name__ == "__main__":
    main()
