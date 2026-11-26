# Modelo para Power BI (Etapa 5)

Gerar os arquivos: `python -m src.run_clean && python -m src.run_model && python -m src.export_powerbi`
Saída em `data/processed/powerbi/` (não versionada): 6 tabelas em **CSV** (UTF-8 com BOM) e **Parquet** (mesmos dados).

| Tabela | Linhas | Colunas | Papel |
|---|---|---|---|
| fact_orders | 99.441 | 24 | Fato, grão = pedido (datas, prazo, atraso, nota, pagamento, recorrência) |
| fact_items | 112.650 | 6 | Fato, grão = item (receita, frete, produto, vendedor) |
| dim_date | 852 | 11 | Calendário (2016-09 a 2018-12), rótulos em português |
| dim_customer | 99.441 | 7 | Cliente por pedido (`customer_id`), com `customer_unique_id`, UF, lat/lng |
| dim_product | 32.951 | 5 | Categoria (PT/EN), peso, fotos |
| dim_seller | 3.095 | 6 | Vendedor, UF, lat/lng |

## Como importar
**Opção recomendada: Parquet** (Obter dados → Parquet). Os tipos já vêm corretos e não há problema de configuração regional.

**Se usar CSV:** os decimais usam ponto (`58.90`). Se o Power BI estiver em pt-BR, ele pode interpretar `58.90` como 5890. Para evitar:
1. Obter dados → Texto/CSV → *Origem do arquivo*: **65001 UTF-8**;
2. Transformar dados → selecionar as colunas numéricas (`revenue`, `freight_value`, `delivery_days`, `delay_days`, `payment_value`, `estimated_days`, `lat`, `lng`) → Alterar tipo → **Usando a configuração regional… → Número decimal → Inglês (Estados Unidos)**.

> Não consegui abrir o Power BI Desktop aqui, então o passo a passo abaixo segue a documentação do produto e **não foi testado**. Confira os totais com o gabarito no fim deste documento.

## Relacionamentos
```
dim_date ─────────┐
                  │ 1 ──< *
dim_customer ─── fact_orders ──< fact_items >── dim_product
   1 ──< *            1 ──< *           * >── 1
                                        └──── dim_seller
```
| De (lado muitos) | Para (lado um) | Cardinalidade | Direção do filtro | Ativo |
|---|---|---|---|---|
| fact_orders[date_key] | dim_date[date_key] | Muitos para um | Única | Sim |
| fact_orders[customer_id] | dim_customer[customer_id] | Muitos para um | Única | Sim |
| fact_items[order_id] | fact_orders[order_id] | Muitos para um | Única | Sim |
| fact_items[product_id] | dim_product[product_id] | Muitos para um | Única | Sim |
| fact_items[seller_id] | dim_seller[seller_id] | Muitos para um | Única | Sim |

Integridade já verificada no CSV exportado: chaves únicas nas dimensões e em `fact_orders`, `(order_id, order_item_id)` único em `fact_items`, **0 chaves órfãs** nos 5 relacionamentos.

### Por que não há `date_key` em `fact_items`
Com `date_key` nas duas fatos, `dim_date` alcançaria `fact_items` por dois caminhos (direto e via `fact_orders`), e o Power BI desativa um relacionamento ou gera ambiguidade. Deixando a data só em `fact_orders`, o filtro de data **propaga para os itens** pelo relacionamento `fact_orders → fact_items`.

### Consequência importante: o filtro não volta de `fact_items` para `fact_orders`
- Filtrar por **UF do cliente, data ou status** afeta tudo, porque esses filtros descem de `fact_orders` para `fact_items`.
- Filtrar por **categoria ou vendedor** afeta só `fact_items`. Medidas **no nível do pedido** (nota, % de atraso) **não reagem** à categoria/vendedor se forem calculadas sobre `fact_orders`.
- Solução (Etapa 6): para a análise por categoria/vendedor, calcular as medidas sobre `DISTINCTCOUNT(fact_items[order_id])` com filtro em `fact_orders[is_late]`. Evite a direção "Ambas" no relacionamento, que causa ambiguidade e lentidão.
- Por isso o % de atraso **por vendedor/categoria** em DAX contará pedidos distintos, e o notebook (Pergunta 5) calcula por itens: os números podem diferir levemente.

## Ajustes no Power BI após importar
1. **Tabela de datas:** Ferramentas de tabela → *Marcar como tabela de datas* → coluna `date` (em `dim_date`).
2. **Ordenação:** `dim_date[month_name]` ordenar por `month`; `dim_date[year_month]` ordenar por `year_month_key`; `weekday_name` por `weekday_num`.
3. **Categoria de dados** (para mapas): `state` → Estado/Província · `lat` → Latitude · `lng` → Longitude.
4. **Ocultar** chaves e colunas técnicas (`customer_id`, `date_key`, `order_id`, `product_id`, `seller_id`, `year_month_key`, `weekday_num`) para o usuário do relatório só ver o que importa.
5. **Resumir por:** colocar *Não resumir* em `year`, `month`, `review_score`, `installments_max`, `delay_days`, `delivery_days` e nas flags (as medidas DAX farão a agregação).
6. **Filtro de período:** `dim_date[in_analysis_period] = 1` (jan/2017–ago/2018) como filtro de relatório, igual às análises em Python.

## Flags (todas 0/1, nulo quando não se aplica)
> **Armadilha de DAX:** `BLANK() = 0` é verdadeiro. Teste flags sempre com `= 1`, nunca `= 0`; um filtro `is_late = 0` incluiria os pedidos não entregues (nulos).
| Coluna | Significado |
|---|---|
| `is_valid_order` | 1 = status diferente de `canceled`/`unavailable`. **Filtrar em quase toda medida de receita** |
| `is_late` | 1 = entregue após a data estimada; nulo se não foi entregue (então `AVERAGE(is_late)` já dá o % de atrasados) |
| `is_delivered` | 1 = entregue com data de entrega; **nunca nulo**. Use-o como universo de entregues em DAX |
| `is_first_order` | 1 = primeira compra válida da pessoa (para contar clientes novos) |
| `is_recurring_customer` | 1 = a pessoa tem 2+ pedidos válidos |

## Gabarito para validar as medidas (Etapa 6)
Calculado a partir dos CSV exportados. Se uma medida DAX não bater, o erro é de filtro, não de dado.

| Medida | Contexto | Valor esperado |
|---|---|---|
| Faturamento | pedidos válidos, jan/2017–ago/2018 | **R$ 13.449.529,68** |
| Faturamento | pedidos válidos, todo o período | R$ 13.494.400,74 |
| Pedidos (com item) | jan/2017–ago/2018, válidos | **97.905** |
| Ticket médio | jan/2017–ago/2018, válidos | **R$ 137,37** |
| Frete total | jan/2017–ago/2018, válidos | R$ 2.234.177,06 |
| % pedidos atrasados | todos os entregues com data | **6,77%** (6.534 de 96.470) |
| Nota média | todos os pedidos avaliados | 4,09 (atrasados 2,27 · no prazo 4,29) |
| Clientes (pessoas) com pedido válido | todo o período | 94.990 |
| Taxa de recompra | pessoas com 2+ pedidos válidos | **3,04%** (2.888) |
| Clientes novos | nov/2017 | 7.190 |
| Faturamento nov/2017 e variação MoM | | R$ 1.003.862,14 · **+52,06%** vs out/2017 |
