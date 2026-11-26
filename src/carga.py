"""Carga dos CSVs brutos, já com as colunas renomeadas para português."""
import pandas as pd
from .config import BRUTO, ARQUIVOS, COLUNAS


def carregar_bruto(nome: str, **kwargs) -> pd.DataFrame:
    """Lê um CSV bruto pelo nome curto (ex.: 'pedidos') e traduz os nomes das colunas.
    utf-8-sig remove o BOM do arquivo de tradução de categorias."""
    df = pd.read_csv(BRUTO / ARQUIVOS[nome], encoding="utf-8-sig", **kwargs)
    faltando = set(COLUNAS[nome]) - set(df.columns)
    if faltando:  # protege contra mudança de layout do dataset
        raise ValueError(f"Colunas esperadas ausentes em {nome}: {sorted(faltando)}")
    return df.rename(columns=COLUNAS[nome])


def carregar_tudo() -> dict[str, pd.DataFrame]:
    return {nome: carregar_bruto(nome) for nome in ARQUIVOS}
