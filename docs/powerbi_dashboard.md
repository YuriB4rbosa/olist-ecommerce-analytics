# Dashboard Power BI (Etapa 6)

Arquivos: [`powerbi/medidas.dax`](../powerbi/medidas.dax) (medidas e colunas calculadas) · [`powerbi/tema_olist.json`](../powerbi/tema_olist.json) (cores).
Pré-requisito: tabelas importadas e relacionamentos criados, conforme [`powerbi_modelo.md`](powerbi_modelo.md).

> **Aviso:** não tenho acesso ao Power BI Desktop, então o DAX e os passos abaixo **não foram executados**. Eu validei a *lógica* reproduzindo cada medida em Pandas nos CSV exportados e listei os valores esperados na seção "Gabarito". Se uma medida divergir, compare com o gabarito antes de procurar outro erro.

## Passo a passo

**1. Importar e modelar** (≈15 min)
1. Obter dados → Parquet → as 6 tabelas de `data/processed/powerbi/`. Carregar sem transformar.
2. Exibição de Modelo → criar os 5 relacionamentos da tabela de `powerbi_modelo.md` (muitos para um, filtro único).
3. `dim_date` → Ferramentas de tabela → **Marcar como tabela de datas** (`date`). Ordenar `month_name` por `month`, `year_month` por `year_month_key`, `weekday_name` por `weekday_num`.
4. `dim_customer[state]` → categoria *Estado/Província*; `lat`/`lng` → Latitude/Longitude.

**2. Colunas calculadas** (em `fact_orders` → Nova coluna; código na seção 6 de `medidas.dax`)
`Meses Desde 1ª Compra`, `Faixa Atraso`, `Faixa Parcelas`, `Valor Produtos`, `Faixa Valor Pedido`.
Crie `Valor Produtos` **antes** de `Faixa Valor Pedido`.

**3. Medidas** (≈20 min)
1. Página inicial → Inserir dados → tabela vazia chamada `_Medidas` (concentra as medidas em um só lugar).
2. Para cada bloco das seções 1 a 5 de `medidas.dax`: selecionar `_Medidas` → Nova medida → colar.
3. Formatar: `Faturamento`, `Frete Total`, `Ticket Médio` → Moeda R$; as que começam com `%`, `Var` e `Taxa` → Porcentagem com 1–2 casas; `Nota Média` → 2 casas.

**4. Tema e filtros globais**
1. Exibir → Temas → Procurar temas → `powerbi/tema_olist.json`.
2. Em cada página, Filtros → *Filtros nesta página*: `dim_date[in_analysis_period] = 1`. Ele reproduz a janela jan/2017–ago/2018 usada nas análises em Python.
3. Slicers sincronizados nas 5 páginas (Exibir → Sincronizar segmentações): **Ano** (`dim_date[year]`), **Mês** (`dim_date[month_name]`), **UF** (`dim_customer[state]`), **Categoria** (`dim_product[category_en]`).

**5. Montar as páginas** (layout abaixo) → **6. Validar** com o gabarito → **7. Registrar**: salvar em `powerbi/olist_dashboard.pbix`, exportar cada página como PNG para `docs/img/dashboard_1.png`… (Arquivo → Exportar → PDF, ou captura de tela) para o README.

## Layout das páginas
Princípios: uma cor de destaque (azul) e vermelho só para o que é problema; **título de cada gráfico escrito como conclusão**, não como rótulo ("Atraso de 4+ dias derruba a nota para ~2", em vez de "Nota por atraso").

### Página 1 · Visão Executiva (perguntas 1 e 2)
| Zona | Visual | Campos |
|---|---|---|
| Topo | 6 cartões | `Faturamento` · `Pedidos` · `Ticket Médio` · `% Pedidos Atrasados` · `Nota Média` · `Taxa de Recompra` (cada um com `Var YoY %` no subtítulo, quando aplicável) |
| Centro | Colunas + linha | Eixo `dim_date[year_month]`; colunas = `Faturamento`; linha (eixo secundário) = `Var MoM %` |
| Inferior esq. | Barras (top 5) | `dim_product[category_en]` × `Faturamento`, rótulo com `% do Faturamento Total` |
| Inferior dir. | Mapa de bolhas | `dim_customer` (lat/lng), tamanho = `Faturamento` |

### Página 2 · Categorias e Estados (pergunta 2)
- Barras horizontais, top 10 categorias (filtro Top N) × `Faturamento`, rótulo `% do Faturamento Total`.
- Barras por `dim_customer[state]` × `% do Faturamento Total` (destaque nos 3 primeiros com formatação condicional).
- Tabela: `state`, `Faturamento`, `Pedidos`, `Ticket Médio`, com filtro de visual `Pedidos >= 300` (evita ruído de estados pequenos).

### Página 3 · Logística e Satisfação (perguntas 3 e 5)
- Colunas: `fact_orders[Faixa Atraso]` × `Nota Média` (vermelho nas faixas atrasadas) e ao lado `% Avaliações 1-2`.
- Cartões: `% Pedidos Atrasados`, `Prazo Mediano de Entrega (dias)`, `Atraso Médio dos Atrasados (dias)`.
- Barras: `state` × `% Pedidos Atrasados` (filtro Top 10) e `category_en` × `% Pedidos Atrasados` (Top 10, filtro `Pedidos Entregues >= 300`).
- Tabela de vendedores: `dim_seller[seller_id]`, `Pedidos Entregues`, `% Pedidos Atrasados`, com filtro de visual `Pedidos Entregues >= 30` e ordenação decrescente por % de atraso.

### Página 4 · Clientes e Retenção (pergunta 4)
- Cartões: `Clientes`, `Clientes Recorrentes`, `Taxa de Recompra`.
- **Matriz de cohort:** linhas = `fact_orders[cohort_month]`, colunas = `Meses Desde 1ª Compra`, valores = `Retenção Cohort`, formatação condicional em escala de azul. Filtros do visual: `Meses Desde 1ª Compra` entre 1 e 6 e `cohort_month` ≤ 01/02/2018 (cohorts com 6 meses observáveis).
- Colunas: `dim_date[year_month]` × `Clientes Novos`.

### Página 5 · Frete e Pagamento (pergunta 6)
- Colunas: `Faixa Valor Pedido` × `Frete % do Faturamento`.
- Barras: `state` × `Frete % do Faturamento` (filtro `Pedidos >= 300`).
- Colunas: `fact_orders[payment_type_main]` × `Ticket Médio`; e `Faixa Parcelas` × `Ticket Médio`.

## Gabarito (valores esperados)
Calculados em Pandas sobre os CSV exportados. A coluna **Contexto** diz se é preciso o filtro `in_analysis_period = 1`.

| Medida | Contexto | Valor esperado |
|---|---|---|
| Faturamento | com filtro de período | **R$ 13.449.529,68** |
| Pedidos | com filtro de período | **97.905** |
| Ticket Médio | com filtro de período | **R$ 137,37** |
| Frete Total · Frete % do Faturamento | com filtro de período | R$ 2.234.177,06 · **16,61%** |
| Faturamento · % do Faturamento Total | período · UF = SP | **38,30%** |
| Faturamento | período · categoria = health_beauty | R$ 1.251.145,54 |
| Var MoM % | nov/2017 | **+52,06%** (R$ 1.003.862,14 vs R$ 660.179,62) |
| Var YoY % | período · Ano = 2018 (jan–ago vs jan–ago/2017) | **+138,28%** |
| Pedidos Entregues · Atrasados · % Pedidos Atrasados | sem filtro de período | 96.470 · 6.534 · **6,77%** |
| % Pedidos Atrasados | UF = AL / UF = SP | **21,41%** (85 de 397) / **4,49%** |
| % Pedidos Atrasados | categoria = audio / luggage_accessories | 11,78% (41 de 348) / 4,32% |
| Vendedores com ≥ 30 pedidos entregues e > 15% de atraso | sem filtro de período | 627 vendedores, **37** acima de 15% (pior: 32,6% em 43 pedidos) |
| Nota Média | sem filtro de período | ≈ **4,09** |
| Nota Média | `is_late` = 1 / `is_late` = 0 | 2,27 / 4,29 |
| Nota Média | categoria = audio | ≈ 3,84 |
| Clientes · Clientes Recorrentes · Taxa de Recompra | sem filtro de período | 94.990 · 2.888 · **3,04%** |
| Clientes Novos | nov/2017 | 7.190 |
| Retenção Cohort | cohort 2017-10, M+1 | ≈ 0,71% |
| Frete % do Faturamento por faixa de valor | período: até 50 / 50–100 / 100–200 / 200–500 / >500 | 48,3% / 25,3% / 17,3% / 11,8% / 6,2% |
| Ticket Médio por pagamento | período: cartão / boleto / débito / voucher | R$ 143,6 / 121,7 / 119,6 / 94,9 |
| Ticket Médio por parcelas | período: 1x / 2–3x / 4–6x / 7–10x / >10x | R$ 100,2 / 114,3 / 157,4 / 301,2 / 323,1 |

### Por que alguns números diferem do notebook
- **Frete por faixa de valor:** o notebook mostra a **mediana por pedido** (46% / 23% / 14% / 9% / 4%); o DAX mostra a **razão agregada** (soma do frete ÷ soma da receita). As duas contam a mesma história (frete pesa mais em pedido barato), mas os valores diferem, e nenhuma está errada. Use a mediana nos posts, e o painel como confirmação.
- **Atraso por vendedor/categoria:** ambos contam **pedidos distintos** (o notebook foi alinhado a esse critério na Etapa 6). Por isso são 37 vendedores, e não os 40 da primeira versão, que contava linhas de item.

## Armadilhas conhecidas
| Sintoma | Causa provável |
|---|---|
| Nota/atraso não muda ao filtrar categoria | Medida calculada só sobre `fact_orders`; use as versões com `CROSSFILTER`/`fact_items` do arquivo |
| `% Pedidos Atrasados` maior que o esperado | Filtro `is_late = 0` em algum lugar (em DAX, `BLANK() = 0`); use `is_delivered = 1` |
| `Var MoM %` vazio | `dim_date` não foi marcada como tabela de datas, ou o visual não usa `dim_date[date]`/`year_month` no eixo |
| Faturamento ~100× maior | Decimais lidos com vírgula ao importar CSV; reimporte o Parquet |
| Meses fora de ordem | Falta "Classificar por coluna" em `month_name`/`year_month` |
