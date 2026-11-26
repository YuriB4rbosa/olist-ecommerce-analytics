"""Funções de carga e visualização compartilhadas pelos notebooks."""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from .config import PROCESSADO, RAIZ

IMAGENS = RAIZ / "docs" / "img"
AZUL, CINZA, VERMELHO = "#2563EB", "#9CA3AF", "#DC2626"
INICIO_CHAVE, FIM_CHAVE = 20170101, 20180831  # janela de análise (ver docs/decisoes_limpeza.md)


def configurar():
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titleweight": "bold", "axes.titlesize": 13})


def carregar_modelo() -> dict:
    nomes = ["fato_pedidos", "fato_itens", "dim_cliente", "dim_produto", "dim_vendedor", "dim_data"]
    return {n: pd.read_parquet(PROCESSADO / "model" / f"{n}.parquet") for n in nomes}


def no_periodo(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra a janela jan/2017–ago/2018, a única com volume relevante."""
    return df[df["chave_data"].between(INICIO_CHAVE, FIM_CHAVE)]


def fmt_pct(ax, eixo="y"):
    getattr(ax, f"{eixo}axis").set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0%}"))


def brl_mil(x, pos=None):
    return f"R$ {x/1e3:,.0f} mil".replace(",", ".")


def fmt_brl(ax, eixo="y"):
    getattr(ax, f"{eixo}axis").set_major_formatter(FuncFormatter(brl_mil))


def salvar_figura(nome: str):
    IMAGENS.mkdir(parents=True, exist_ok=True)
    plt.savefig(IMAGENS / f"{nome}.png", bbox_inches="tight", dpi=150)
