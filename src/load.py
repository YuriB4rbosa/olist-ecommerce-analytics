"""Carga dos CSVs brutos."""
import pandas as pd
from .config import RAW, ARQUIVOS


def load_raw(nome: str, **kwargs) -> pd.DataFrame:
    """Lê um CSV bruto pelo nome curto (ex.: 'orders'). utf-8-sig remove o BOM do arquivo de tradução."""
    return pd.read_csv(RAW / ARQUIVOS[nome], encoding="utf-8-sig", **kwargs)


def load_all() -> dict[str, pd.DataFrame]:
    return {nome: load_raw(nome) for nome in ARQUIVOS}
