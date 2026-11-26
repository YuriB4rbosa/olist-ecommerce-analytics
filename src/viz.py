"""Helpers de carga e visualização compartilhados pelos notebooks."""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from .config import PROCESSED, ROOT

IMG = ROOT / "docs" / "img"
AZUL, CINZA, VERMELHO = "#2563EB", "#9CA3AF", "#DC2626"
INICIO_KEY, FIM_KEY = 20170101, 20180831  # janela de análise (ver docs/decisoes_limpeza.md)


def setup():
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titleweight": "bold", "axes.titlesize": 13})


def load_model() -> dict:
    nomes = ["fact_orders", "fact_items", "dim_customer", "dim_product", "dim_seller", "dim_date"]
    return {n: pd.read_parquet(PROCESSED / "model" / f"{n}.parquet") for n in nomes}


def no_periodo(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra a janela jan/2017–ago/2018, a única com volume relevante."""
    return df[df["date_key"].between(INICIO_KEY, FIM_KEY)]


def pct_fmt(ax, eixo="y"):
    getattr(ax, f"{eixo}axis").set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0%}"))


def brl_mil(x, pos=None):
    return f"R$ {x/1e3:,.0f} mil".replace(",", ".")


def brl_fmt(ax, eixo="y"):
    getattr(ax, f"{eixo}axis").set_major_formatter(FuncFormatter(brl_mil))


def savefig(nome: str):
    IMG.mkdir(parents=True, exist_ok=True)
    plt.savefig(IMG / f"{nome}.png", bbox_inches="tight", dpi=150)
