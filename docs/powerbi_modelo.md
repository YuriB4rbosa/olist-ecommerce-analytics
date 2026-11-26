# Modelo para Power BI (Etapa 5)

Gerar os arquivos: `python -m src.executar_limpeza && python -m src.executar_modelo && python -m src.exportar_powerbi`
Saída em `data/processed/powerbi/` (não versionada): 6 tabelas em **CSV** (UTF-8 com BOM) e **Parquet** (mesmos dados).

| Tabela | Linhas | Colunas | Papel |
|---|---|---|---|
| fato_pedidos | 99.441 | 24 | Fato, grão = pedido (datas, prazo, atraso, nota, pagamento, recorrência) |
| fato_itens | 112.650 | 6 | Fato, grão = item (receita, frete, produto, vendedor) |
| dim_data | 852 | 11 | Calendário (2016-09 a 2018-12), rótulos em português |
| dim_cliente | 99.441 | 7 | Cliente por pedido (`id_cliente`), com `id_cliente_unico`, UF, lat/lng |
| dim_produto | 32.951 | 5 | Categoria (PT/EN), peso, fotos |
| dim_vendedor | 3.095 | 6 | Vendedor, UF, lat/lng |

> **Idioma:** nomes de tabelas, colunas e medidas estão em português. Os **valores de texto** também saem em português nesta exportação (status: `Entregue`, `Cancelado`…; forma de pagamento: `Cartão de crédito`, `Boleto`…; categoria: `Beleza e saúde`…). Nos notebooks Python eles continuam como no dataset original.

## Como importar
**Opção recomendada: Parquet** (Obter dados → Parquet). Os tipos já vêm corretos e não há problema de configuração regional.

**Se usar CSV:** os decimais usam ponto (`58.90`). Se o Power BI estiver em pt-BR, ele pode interpretar `58.90` como 5890. Para evitar:
1. Obter dados → Texto/CSV → *Origem do arquivo*: **65001 UTF-8**;
2. Transformar dados → selecionar as colunas numéricas (`receita`, `valor_frete`, `dias_entrega`, `dias_atraso`, `valor_pagamento`, `dias_estimados`, `latitude`, `longitude`) → Alterar tipo → **Usando a configuração regional… → Número decimal → Inglês (Estados Unidos)**.

> Não consegui abrir o Power BI Desktop aqui, então o passo a passo abaixo segue a documentação do produto e **não foi testado**. Confira os totais com o gabarito no fim deste documento.

## Relacionamentos
```
dim_data ─────────┐
                  │ 1 ──< *
dim_cliente ─── fato_pedidos ──< fato_itens >── dim_produto
   1 ──< *            1 ──< *           * >── 1
                                        └──── dim_vendedor
```
| De (lado muitos) | Para (lado um) | Cardinalidade | Direção do filtro | Ativo |
|---|---|---|---|---|
| fato_pedidos[chave_data] | dim_data[chave_data] | Muitos para um | Única | Sim |
| fato_pedidos[id_cliente] | dim_cliente[id_cliente] | Muitos para um | Única | Sim |
| fato_itens[id_pedido] | fato_pedidos[id_pedido] | Muitos para um | Única | Sim |
| fato_itens[id_produto] | dim_produto[id_produto] | Muitos para um | Única | Sim |
| fato_itens[id_vendedor] | dim_vendedor[id_vendedor] | Muitos para um | Única | Sim |

Integridade já verificada no CSV exportado: chaves únicas nas dimensões e em `fato_pedidos`, `(id_pedido, id_item)` único em `fato_itens`, **0 chaves órfãs** nos 5 relacionamentos.

### Por que não há `chave_data` em `fato_itens`
Com `chave_data` nas duas fatos, `dim_data` alcançaria `fato_itens` por dois caminhos (direto e via `fato_pedidos`), e o Power BI desativa um relacionamento ou gera ambiguidade. Deixando a data só em `fato_pedidos`, o filtro de data **propaga para os itens** pelo relacionamento `fato_pedidos → fato_itens`.

### Consequência importante: o filtro não volta de `fato_itens` para `fato_pedidos`
- Filtrar por **UF do cliente, data ou status** afeta tudo, porque esses filtros descem de `fato_pedidos` para `fato_itens`.
- Filtrar por **categoria ou vendedor** afeta só `fato_itens`. Medidas **no nível do pedido** (nota, % de atraso) **não reagem** à categoria/vendedor se forem calculadas sobre `fato_pedidos`.
- Solução (Etapa 6): para a análise por categoria/vendedor, calcular as medidas sobre `DISTINCTCOUNT(fato_itens[id_pedido])` com filtro em `fato_pedidos[atrasado]`. Evite a direção "Ambas" no relacionamento, que causa ambiguidade e lentidão.
- Por isso o % de atraso **por vendedor/categoria** em DAX contará pedidos distintos, e o notebook (Pergunta 5) calcula por itens: os números podem diferir levemente.

## Ajustes no Power BI após importar
1. **Tabela de datas:** Ferramentas de tabela → *Marcar como tabela de datas* → coluna `data` (em `dim_data`).
2. **Ordenação:** `dim_data[nome_mes]` ordenar por `mes`; `dim_data[ano_mes]` ordenar por `ano_mes_chave`; `nome_dia_semana` por `dia_semana_num`.
3. **Categoria de dados** (para mapas): `uf` → Estado/Província · `latitude` → Latitude · `longitude` → Longitude.
4. **Ocultar** chaves e colunas técnicas (`id_cliente`, `chave_data`, `id_pedido`, `id_produto`, `id_vendedor`, `ano_mes_chave`, `dia_semana_num`) para o usuário do relatório só ver o que importa.
5. **Resumir por:** colocar *Não resumir* em `ano`, `mes`, `nota_avaliacao`, `parcelas_max`, `dias_atraso`, `dias_entrega` e nas flags (as medidas DAX farão a agregação).
6. **Filtro de período:** `dim_data[periodo_analise] = 1` (jan/2017–ago/2018) como filtro de relatório, igual às análises em Python.

## Flags (todas 0/1, nulo quando não se aplica)
> **Armadilha de DAX:** `BLANK() = 0` é verdadeiro. Teste flags sempre com `= 1`, nunca `= 0`; um filtro `atrasado = 0` incluiria os pedidos não entregues (nulos).
| Coluna | Significado |
|---|---|
| `pedido_valido` | 1 = status diferente de `canceled`/`unavailable`. **Filtrar em quase toda medida de receita** |
| `atrasado` | 1 = entregue após a data estimada; nulo se não foi entregue (então `AVERAGE(atrasado)` já dá o % de atrasados) |
| `entregue` | 1 = entregue com data de entrega; **nunca nulo**. Use-o como universo de entregues em DAX |
| `primeira_compra` | 1 = primeira compra válida da pessoa (para contar clientes novos) |
| `cliente_recorrente` | 1 = a pessoa tem 2+ pedidos válidos |

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
