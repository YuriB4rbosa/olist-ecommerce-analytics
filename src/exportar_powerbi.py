"""Exporta o modelo estrela pronto para importar no Power BI.

Uso (após src.executar_limpeza e src.executar_modelo):  python -m src.exportar_powerbi
Saída: data/processed/powerbi/*.csv  (UTF-8 com BOM, separador ',', decimal '.', datas ISO)
       data/processed/powerbi/*.parquet (mesmos dados, com tipos preservados)

Decisões de design (detalhes em docs/powerbi_modelo.md):
- fato_itens NÃO carrega chave_data/flags de pedido: evita dois caminhos de filtro desde dim_data
  (dim_data -> fato_pedidos -> fato_itens e dim_data -> fato_itens) e relacionamentos ambíguos.
- Receita vive só em fato_itens.receita (fonte única); fato_pedidos não repete receita/frete.
- Flags booleanas viram 0/1 (nulo quando não se aplica; em DAX teste sempre '= 1', nunca '= 0').
- Os VALORES de texto (status, forma de pagamento, categoria) saem em português; no restante do
  projeto (notebooks) eles continuam como no dataset original.
"""
import pandas as pd
from .categorias import nome_categoria_pt
from .config import PROCESSADO

MODELO = PROCESSADO / "model"
SAIDA = PROCESSADO / "powerbi"

STATUS_PT = {"delivered": "Entregue", "shipped": "Enviado", "canceled": "Cancelado",
             "unavailable": "Indisponível", "invoiced": "Faturado", "processing": "Em processamento",
             "created": "Criado", "approved": "Aprovado"}
PAGAMENTO_PT = {"credit_card": "Cartão de crédito", "boleto": "Boleto", "voucher": "Voucher",
                "debit_card": "Cartão de débito", "not_defined": "Não definido"}


def _flag(s: pd.Series) -> pd.Series:
    """boolean (True/False/<NA>) -> Int8 (1/0/<NA>)."""
    return s.astype("boolean").astype("Int8")


def _traduzir(s: pd.Series, mapa: dict) -> pd.Series:
    """Traduz valores; um valor sem tradução vira erro (melhor que sumir silenciosamente do filtro)."""
    desconhecidos = set(s.dropna().unique()) - set(mapa)
    if desconhecidos:
        raise ValueError(f"Valores sem tradução: {sorted(desconhecidos)}")
    return s.map(mapa)


def preparar_fato_pedidos(fp: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "id_pedido": fp["id_pedido"],
        "id_cliente": fp["id_cliente"],
        "id_cliente_unico": fp["id_cliente_unico"],
        "chave_data": fp["chave_data"],
        "status_pedido": _traduzir(fp["status_pedido"], STATUS_PT),
        "pedido_valido": _flag(fp["pedido_valido"]),
        "datahora_compra": fp["datahora_compra"],
        "data_entrega_cliente": fp["data_entrega_cliente"],
        "data_entrega_estimada": fp["data_entrega_estimada"],
        "dias_entrega": fp["dias_entrega"],
        "dias_estimados": fp["dias_estimados"],
        "dias_atraso": fp["dias_atraso"],
        "atrasado": _flag(fp["atrasado"]),
        # 1 = entregue com data de entrega; nunca nulo (em DAX BLANK()=0, então não filtre atrasado = 0)
        "entregue": _flag(fp["atrasado"].notna()),
        "qtd_itens": fp["qtd_itens"].astype(int),
        "valor_pagamento": fp["valor_pagamento"],
        "parcelas_max": fp["parcelas_max"].astype("Int64"),
        "forma_pagamento_principal": _traduzir(fp["forma_pagamento_principal"], PAGAMENTO_PT),
        "qtd_formas_pagamento": fp["qtd_formas_pagamento"].astype("Int64"),
        "nota_avaliacao": fp["nota_avaliacao"].astype("Int64"),
        "seq_pedido_cliente": fp["seq_pedido_cliente"].astype("Int64"),
        "primeira_compra": _flag(fp["seq_pedido_cliente"].eq(1).where(fp["seq_pedido_cliente"].notna())),
        "cliente_recorrente": _flag(fp["cliente_recorrente"]),
        "mes_coorte": fp["mes_coorte"],
    })


def preparar_fato_itens(fi: pd.DataFrame) -> pd.DataFrame:
    return fi[["id_pedido", "id_item", "id_produto", "id_vendedor", "receita", "valor_frete"]].copy()


def preparar_dim_data(dd: pd.DataFrame) -> pd.DataFrame:
    d = dd.copy()
    d["periodo_analise"] = d["periodo_analise"].astype("Int8")
    return d[["chave_data", "data", "ano", "trimestre", "mes", "nome_mes", "ano_mes", "ano_mes_chave",
              "dia_semana_num", "nome_dia_semana", "periodo_analise"]]


def preparar_dim_cliente(dc: pd.DataFrame) -> pd.DataFrame:
    return dc[["id_cliente", "id_cliente_unico", "cep_prefixo", "cidade", "uf", "latitude", "longitude"]].copy()


def preparar_dim_vendedor(dv: pd.DataFrame) -> pd.DataFrame:
    return dv[["id_vendedor", "cep_prefixo", "cidade", "uf", "latitude", "longitude"]].copy()


def preparar_dim_produto(dp: pd.DataFrame) -> pd.DataFrame:
    out = dp[["id_produto", "categoria_en", "qtd_fotos", "peso_g"]].copy()
    out.insert(1, "categoria", dp["nome_categoria"].map(nome_categoria_pt))
    return out


def main():
    def ler(n):
        return pd.read_parquet(MODELO / f"{n}.parquet")

    tabelas = {
        "fato_pedidos": preparar_fato_pedidos(ler("fato_pedidos")),
        "fato_itens": preparar_fato_itens(ler("fato_itens")),
        "dim_data": preparar_dim_data(ler("dim_data")),
        "dim_cliente": preparar_dim_cliente(ler("dim_cliente")),
        "dim_vendedor": preparar_dim_vendedor(ler("dim_vendedor")),
        "dim_produto": preparar_dim_produto(ler("dim_produto")),
    }
    SAIDA.mkdir(parents=True, exist_ok=True)
    for nome, df in tabelas.items():
        df.to_csv(SAIDA / f"{nome}.csv", index=False, encoding="utf-8-sig", date_format="%Y-%m-%d %H:%M:%S")
        df.to_parquet(SAIDA / f"{nome}.parquet", index=False)
        mb = (SAIDA / f"{nome}.csv").stat().st_size / 1e6
        print(f"{nome:13s} {df.shape[0]:>8,} linhas x {df.shape[1]:>2} colunas  ({mb:.1f} MB csv)")


if __name__ == "__main__":
    main()
