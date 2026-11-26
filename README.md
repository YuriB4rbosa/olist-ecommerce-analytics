# Análise de E-Commerce Olist — Python (Pandas) + Power BI

> 🚧 Projeto em construção. README inicial; versão final na Etapa 7.

## Problema
Um marketplace precisa entender **para onde vai a receita, onde a logística falha e se os clientes voltam**.
Este projeto analisa o dataset público [Brazilian E-Commerce by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (~100 mil pedidos, 2016–2018).

## Perguntas de negócio
1. Como evoluem faturamento, nº de pedidos e ticket médio ao longo do tempo?
2. Quais categorias e estados concentram mais receita?
3. Qual o impacto do atraso na entrega na nota de avaliação?
4. Qual a taxa de clientes recorrentes vs. compra única (cohort/retenção)?
5. Quais vendedores e categorias têm pior desempenho logístico?
6. Como frete e forma de pagamento influenciam o valor dos pedidos?

## Estrutura do repositório
```
olist-dataset/
├── data/
│   ├── raw/          # CSVs originais do Kaggle (não versionados)
│   └── processed/    # tabelas limpas/modelo estrela p/ Power BI (não versionadas)
├── notebooks/        # exploração e narrativa (01_exploracao, 02_limpeza, ...)
├── src/              # funções reutilizáveis (carga, limpeza, métricas)
├── powerbi/          # arquivo .pbix e tema
├── docs/             # decisões de limpeza, modelo de dados, prints (docs/img)
├── requirements.txt
└── README.md
```

## Como reproduzir
```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
# Coloque os CSVs do Kaggle em data/raw/
python -m src.run_clean      # limpeza  -> data/processed/clean
python -m src.run_model      # modelo estrela -> data/processed/model
python -m src.export_powerbi # tabelas p/ Power BI -> data/processed/powerbi
jupyter lab                  # notebooks 01 e 02
```

## Stack
Python · Pandas · Matplotlib/Seaborn · Parquet · Power BI (DAX)

## Status
- [x] Etapa 1 — Estrutura
- [x] Etapa 2 — Exploração e limpeza
- [x] Etapa 3 — Modelagem
- [x] Etapa 4 — Análise
- [x] Etapa 5 — Exportação
- [ ] Etapa 6 — Power BI
- [ ] Etapa 7 — Divulgação
