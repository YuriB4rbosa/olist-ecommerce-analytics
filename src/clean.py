"""Limpeza das tabelas brutas. Cada função documenta a decisão tomada (ver docs/decisoes_limpeza.md)."""
import pandas as pd

# 2 categorias presentes em products mas ausentes na tabela de tradução
TRADUCAO_MANUAL = {
    "pc_gamer": "pc_gamer",
    "portateis_cozinha_e_preparadores_de_alimentos": "portable_kitchen_food_preparers",
}


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Converte colunas de data para datetime. Nulos de data são legítimos (pedido ainda não chegou
    a essa etapa ou foi cancelado), então NÃO são removidos."""
    df = df.copy()
    for col in df.columns[df.columns.str.contains("timestamp|_at$|_date$")]:
        df[col] = pd.to_datetime(df[col])
    return df


def clean_items(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"])
    return df


def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """Garante 1 review por pedido (evita duplicar linhas no join): mantém a resposta mais recente."""
    df = df.copy()
    for col in ["review_creation_date", "review_answer_timestamp"]:
        df[col] = pd.to_datetime(df[col])
    df = df.sort_values("review_answer_timestamp").drop_duplicates("order_id", keep="last")
    return df.drop(columns=["review_comment_title", "review_comment_message"])  # texto não usado (privacidade/peso)


def clean_products(df: pd.DataFrame, trad: pd.DataFrame) -> pd.DataFrame:
    """Corrige typo 'lenght', preenche categoria ausente e traduz categorias para inglês."""
    df = df.rename(columns={"product_name_lenght": "product_name_length",
                            "product_description_lenght": "product_description_length"})
    mapa = {**dict(zip(trad.product_category_name, trad.product_category_name_english)), **TRADUCAO_MANUAL}
    df["product_category_name"] = df["product_category_name"].fillna("sem_categoria")
    df["category_en"] = df["product_category_name"].map(mapa).fillna("uncategorized")
    return df


def clean_geolocation(df: pd.DataFrame) -> pd.DataFrame:
    """1 linha por prefixo de CEP (mediana de lat/lng): a tabela original tem ~1M linhas p/ 19 mil CEPs."""
    return (df.groupby("geolocation_zip_code_prefix", as_index=False)
              .agg(lat=("geolocation_lat", "median"), lng=("geolocation_lng", "median"),
                   city=("geolocation_city", "first"), state=("geolocation_state", "first")))
