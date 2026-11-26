"""Limpeza das tabelas brutas. Cada função documenta a decisão tomada (ver docs/decisoes_limpeza.md)."""
import pandas as pd

# 2 categorias presentes em produtos mas ausentes na tabela de tradução
TRADUCAO_MANUAL = {
    "pc_gamer": "pc_gamer",
    "portateis_cozinha_e_preparadores_de_alimentos": "portable_kitchen_food_preparers",
}


def limpar_pedidos(df: pd.DataFrame) -> pd.DataFrame:
    """Converte as colunas de data para datetime. Nulos de data são legítimos (pedido ainda não chegou
    a essa etapa ou foi cancelado), então NÃO são removidos."""
    df = df.copy()
    for col in df.columns[df.columns.str.startswith("data")]:
        df[col] = pd.to_datetime(df[col])
    return df


def limpar_itens(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["data_limite_envio"] = pd.to_datetime(df["data_limite_envio"])
    return df


def limpar_avaliacoes(df: pd.DataFrame) -> pd.DataFrame:
    """Garante 1 avaliação por pedido (evita duplicar linhas no join): mantém a resposta mais recente."""
    df = df.copy()
    for col in ["data_criacao_avaliacao", "datahora_resposta_avaliacao"]:
        df[col] = pd.to_datetime(df[col])
    df = df.sort_values("datahora_resposta_avaliacao").drop_duplicates("id_pedido", keep="last")
    return df.drop(columns=["titulo_comentario", "mensagem_comentario"])  # texto não usado (privacidade/peso)


def limpar_produtos(df: pd.DataFrame, traducao: pd.DataFrame) -> pd.DataFrame:
    """Preenche categoria ausente e traduz as categorias para inglês (o typo 'lenght' já foi corrigido na carga)."""
    df = df.copy()
    mapa = {**dict(zip(traducao.nome_categoria, traducao.categoria_en)), **TRADUCAO_MANUAL}
    df["nome_categoria"] = df["nome_categoria"].fillna("sem_categoria")
    df["categoria_en"] = df["nome_categoria"].map(mapa).fillna("uncategorized")
    return df


def limpar_geolocalizacao(df: pd.DataFrame) -> pd.DataFrame:
    """1 linha por prefixo de CEP (mediana de lat/lng): a tabela original tem ~1M linhas p/ 19 mil CEPs."""
    return (df.groupby("cep_prefixo", as_index=False)
              .agg(latitude=("latitude", "median"), longitude=("longitude", "median"),
                   cidade=("cidade", "first"), uf=("uf", "first")))
