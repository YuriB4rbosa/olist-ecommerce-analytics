# Modelo analítico (Etapa 3)

Gerado por `python -m src.run_clean && python -m src.run_model` → `data/processed/model/*.parquet`.

## Esquema estrela
```
              dim_date ──────────┐
                                 │ date_key
dim_customer ── fact_orders ─────┤
 (customer_id)   (grão: pedido)  │ order_id
                                 │
dim_product ─── fact_items ──────┘
dim_seller  ─── (grão: item)
```
| Tabela | Linhas | Chave | Relacionamento |
|---|---|---|---|
| fact_orders | 99.441 | order_id | customer_id → dim_customer · date_key → dim_date |
| fact_items | 112.650 | order_id + order_item_id | order_id → fact_orders · product_id → dim_product · seller_id → dim_seller · date_key → dim_date |
| dim_customer | 99.441 | customer_id | (inclui `customer_unique_id`, cidade, UF, lat/lng) |
| dim_product | 32.951 | product_id | (categoria PT/EN, peso, dimensões) |
| dim_seller | 3.095 | seller_id | (cidade, UF, lat/lng) |
| dim_date | 852 | date_key (AAAAMMDD) | calendário 2016-09 a 2018-12 |

Por que dois fatos? Pedido e item têm grãos diferentes. Atraso, nota e recorrência são do pedido; categoria, vendedor e preço são do item. Misturar tudo em uma tabela duplicaria o frete e a nota a cada item.

## Colunas derivadas e regras de negócio
| Coluna | Regra |
|---|---|
| `revenue` | Soma de `price` dos itens (**faturamento = produto, sem frete**). `freight` fica separado |
| `delivery_days` | Entrega ao cliente − compra, em dias. Só pedidos `delivered` com data de entrega |
| `delay_days` | Data de entrega − data estimada, em **datas** (>0 = atrasou). Estimativa vem às 00:00, então comparar timestamps marcaria como atrasado quem recebeu no dia previsto |
| `is_late` | `delay_days > 0`. Nulo para pedidos fora do universo de entregues |
| `is_valid_order` | Status ≠ `canceled`/`unavailable`. Usar nas análises de receita e recorrência |
| `customer_order_seq` | Nº do pedido da pessoa (`customer_unique_id`), por data, entre pedidos válidos |
| `is_recurring_customer` | A pessoa tem 2+ pedidos válidos |
| `cohort_month` | Mês da 1ª compra válida da pessoa |
| `payment_type_main` | Forma de pagamento de maior valor no pedido |
| `installments_max` | Maior nº de parcelas do pedido |
| `review_score` | Nota da review mais recente do pedido |

**Cuidado com `customer_id`:** ele muda a cada pedido. Para contar pessoas ou recorrência, use sempre `customer_unique_id`.

## Validações executadas (todas passaram)
- Chaves primárias únicas nas 6 tabelas; **0 chaves órfãs** em todos os relacionamentos.
- Receita: fact_items = fact_orders = **R$ 13.591.643,70** (bate com o CSV original, sem duplicação de linhas).
- Nulos remanescentes são esperados: 2.971 sem métrica de prazo (não entregues), 768 sem review, 1.234 pedidos inválidos sem sequência de cliente, 278 clientes e 7 vendedores com CEP sem coordenada.

## Primeiros números (a confirmar na Etapa 4)
- Entregues com data: 96.470 · atrasados: **6.534 (6,8%)** · prazo mediano de entrega **10,2 dias**
- Pessoas com pedido válido: 94.990 · recorrentes: **2.888 (3,04%)**
- Ticket médio por pedido: **R$ 137,42**
