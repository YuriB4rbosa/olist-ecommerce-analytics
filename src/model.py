"""Modelo analítico em estrela a partir das tabelas limpas.

Fatos : fact_orders (grão = pedido) e fact_items (grão = item do pedido)
Dims  : dim_customer, dim_product, dim_seller, dim_date
Definições de negócio: ver docs/modelo_dados.md
"""
import pandas as pd

STATUS_VALIDOS = ["delivered", "shipped", "invoiced", "processing", "approved", "created"]  # exclui canceled/unavailable
INICIO_ANALISE, FIM_ANALISE = "2017-01-01", "2018-08-31"  # janela com volume relevante (ver decisoes_limpeza.md)


def build_dim_date(inicio="2016-09-01", fim="2018-12-31") -> pd.DataFrame:
    d = pd.DataFrame({"date": pd.date_range(inicio, fim, freq="D")})
    d["date_key"] = d["date"].dt.strftime("%Y%m%d").astype(int)
    d["year"] = d["date"].dt.year
    d["quarter"] = d["date"].dt.quarter
    d["month"] = d["date"].dt.month
    d["month_name"] = d["date"].dt.strftime("%b")
    d["year_month"] = d["date"].dt.strftime("%Y-%m")
    d["weekday_num"] = d["date"].dt.weekday
    d["weekday_name"] = d["date"].dt.day_name()
    d["in_analysis_period"] = d["date"].between(INICIO_ANALISE, FIM_ANALISE)
    return d


def build_dim_customer(customers, geo) -> pd.DataFrame:
    g = geo[["geolocation_zip_code_prefix", "lat", "lng"]]
    out = customers.merge(g, left_on="customer_zip_code_prefix", right_on="geolocation_zip_code_prefix", how="left")
    return out.drop(columns="geolocation_zip_code_prefix")


def build_dim_seller(sellers, geo) -> pd.DataFrame:
    g = geo[["geolocation_zip_code_prefix", "lat", "lng"]]
    out = sellers.merge(g, left_on="seller_zip_code_prefix", right_on="geolocation_zip_code_prefix", how="left")
    return out.drop(columns="geolocation_zip_code_prefix")


def build_dim_product(products) -> pd.DataFrame:
    cols = ["product_id", "product_category_name", "category_en", "product_photos_qty", "product_weight_g",
            "product_length_cm", "product_height_cm", "product_width_cm"]
    return products[cols].copy()


def _payment_summary(payments) -> pd.DataFrame:
    """Resume pagamentos por pedido: forma principal (maior valor), parcelas máximas, nº de formas."""
    p = payments.sort_values("payment_value", ascending=False)
    main = p.drop_duplicates("order_id").set_index("order_id")["payment_type"].rename("payment_type_main")
    agg = payments.groupby("order_id").agg(payment_value=("payment_value", "sum"),
                                           installments_max=("payment_installments", "max"),
                                           n_payment_methods=("payment_type", "nunique"))
    return agg.join(main).reset_index()


def build_fact_orders(orders, items, payments, reviews, customers) -> pd.DataFrame:
    f = orders.copy()
    f["customer_unique_id"] = f["customer_id"].map(customers.set_index("customer_id")["customer_unique_id"])
    f["purchase_date"] = f["order_purchase_timestamp"].dt.normalize()
    f["date_key"] = f["purchase_date"].dt.strftime("%Y%m%d").astype(int)

    # Métricas de prazo: só para pedidos entregues COM data de entrega (8 entregues não têm)
    entregue = f["order_status"].eq("delivered") & f["order_delivered_customer_date"].notna()
    dias_entrega = (f["order_delivered_customer_date"] - f["order_purchase_timestamp"]).dt.total_seconds() / 86400
    # Atraso comparado por DATA (estimativa vem sempre às 00:00; comparar timestamps marcaria
    # como atrasado quem recebeu no próprio dia previsto)
    atraso = (f["order_delivered_customer_date"].dt.normalize() - f["order_estimated_delivery_date"].dt.normalize()).dt.days
    f["delivery_days"] = dias_entrega.where(entregue).round(2)
    f["delay_days"] = atraso.where(entregue)                      # >0 = atrasou
    f["is_late"] = (f["delay_days"] > 0).where(entregue).astype("boolean")  # <NA> fora do universo de entregues
    f["estimated_days"] = ((f["order_estimated_delivery_date"] - f["order_purchase_timestamp"])
                           .dt.total_seconds() / 86400).round(2)

    it = items.groupby("order_id").agg(items_qty=("order_item_id", "count"), revenue=("price", "sum"),
                                       freight=("freight_value", "sum"), n_sellers=("seller_id", "nunique"))
    f = (f.merge(it, on="order_id", how="left")
          .merge(_payment_summary(payments), on="order_id", how="left")
          .merge(reviews[["order_id", "review_score"]], on="order_id", how="left"))
    f[["items_qty", "revenue", "freight", "n_sellers"]] = f[["items_qty", "revenue", "freight", "n_sellers"]].fillna(0)
    f["is_valid_order"] = f["order_status"].isin(STATUS_VALIDOS)

    # Recorrência: ordem de compra de cada pessoa (customer_unique_id) entre pedidos válidos
    v = f[f["is_valid_order"]].sort_values(["customer_unique_id", "order_purchase_timestamp"])
    f["customer_order_seq"] = v.groupby("customer_unique_id").cumcount() + 1
    n_orders = v.groupby("customer_unique_id")["order_id"].transform("count")
    f["is_recurring_customer"] = (n_orders > 1).reindex(f.index).astype("boolean")  # pessoa com 2+ pedidos válidos
    primeira = v.groupby("customer_unique_id")["purchase_date"].transform("min").dt.to_period("M").dt.to_timestamp()
    f["cohort_month"] = primeira.reindex(f.index)
    return f


def build_fact_items(items, fact_orders) -> pd.DataFrame:
    f = items.copy()
    f["revenue"] = f["price"]  # decisão A: faturamento = preço do produto; frete é coluna separada
    ped = fact_orders[["order_id", "date_key", "order_status", "is_valid_order", "is_late", "delay_days"]]
    return f.merge(ped, on="order_id", how="left")
