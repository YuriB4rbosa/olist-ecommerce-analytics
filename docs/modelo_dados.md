# Modelo analítico (Etapa 3)

Gerado por `python -m src.executar_limpeza && python -m src.executar_modelo` → `data/processed/model/*.parquet`.

## Esquema estrela
```
              dim_data ──────────┐
                                 │ chave_data
dim_cliente ── fato_pedidos ─────┤
 (id_cliente)   (grão: pedido)  │ id_pedido
                                 │
dim_produto ─── fato_itens ──────┘
dim_vendedor  ─── (grão: item)
```
| Tabela | Linhas | Chave | Relacionamento |
|---|---|---|---|
| fato_pedidos | 99.441 | id_pedido | id_cliente → dim_cliente · chave_data → dim_data |
| fato_itens | 112.650 | id_pedido + id_item | id_pedido → fato_pedidos · id_produto → dim_produto · id_vendedor → dim_vendedor · chave_data → dim_data |
| dim_cliente | 99.441 | id_cliente | (inclui `id_cliente_unico`, cidade, UF, lat/lng) |
| dim_produto | 32.951 | id_produto | (categoria PT/EN, peso, dimensões) |
| dim_vendedor | 3.095 | id_vendedor | (cidade, UF, lat/lng) |
| dim_data | 852 | chave_data (AAAAMMDD) | calendário 2016-09 a 2018-12 |

Por que dois fatos? Pedido e item têm grãos diferentes. Atraso, nota e recorrência são do pedido; categoria, vendedor e preço são do item. Misturar tudo em uma tabela duplicaria o frete e a nota a cada item.

## Colunas derivadas e regras de negócio
| Coluna | Regra |
|---|---|
| `receita` | Soma de `preco` dos itens (**faturamento = produto, sem frete**). `frete` fica separado |
| `dias_entrega` | Entrega ao cliente − compra, em dias. Só pedidos `delivered` com data de entrega |
| `dias_atraso` | Data de entrega − data estimada, em **datas** (>0 = atrasou). Estimativa vem às 00:00, então comparar timestamps marcaria como atrasado quem recebeu no dia previsto |
| `atrasado` | `dias_atraso > 0`. Nulo para pedidos fora do universo de entregues |
| `pedido_valido` | Status ≠ `canceled`/`unavailable`. Usar nas análises de receita e recorrência |
| `seq_pedido_cliente` | Nº do pedido da pessoa (`id_cliente_unico`), por data, entre pedidos válidos |
| `cliente_recorrente` | A pessoa tem 2+ pedidos válidos |
| `mes_coorte` | Mês da 1ª compra válida da pessoa |
| `forma_pagamento_principal` | Forma de pagamento de maior valor no pedido |
| `parcelas_max` | Maior nº de parcelas do pedido |
| `nota_avaliacao` | Nota da avaliação mais recente do pedido |

**Cuidado com `id_cliente`:** ele muda a cada pedido. Para contar pessoas ou recorrência, use sempre `id_cliente_unico`.

## Validações executadas (todas passaram)
- Chaves primárias únicas nas 6 tabelas; **0 chaves órfãs** em todos os relacionamentos.
- Receita: fato_itens = fato_pedidos = **R$ 13.591.643,70** (bate com o CSV original, sem duplicação de linhas).
- Nulos remanescentes são esperados: 2.971 sem métrica de prazo (não entregues), 768 sem avaliação, 1.234 pedidos inválidos sem sequência de cliente, 278 clientes e 7 vendedores com CEP sem coordenada.

## Primeiros números (a confirmar na Etapa 4)
- Entregues com data: 96.470 · atrasados: **6.534 (6,8%)** · prazo mediano de entrega **10,2 dias**
- Pessoas com pedido válido: 94.990 · recorrentes: **2.888 (3,04%)**
- Ticket médio por pedido: **R$ 137,42**
