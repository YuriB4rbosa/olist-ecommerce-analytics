# Decisões de limpeza (Etapa 2)

Números obtidos rodando `src/carga.py` sobre os CSVs originais. Reproduzir: `python -m src.executar_limpeza`.

## Visão geral
| Tabela | Linhas | Duplicatas exatas | Nulos relevantes |
|---|---|---|---|
| pedidos | 99.441 | 0 | aprovação 160 · transportadora 1.783 · entrega ao cliente 2.965 |
| itens | 112.650 | 0 | — |
| pagamentos | 103.886 | 0 | — |
| avaliacoes | 99.224 | 0 | título 87.656 · mensagem 58.247 |
| clientes | 99.441 | 0 | — |
| vendedores | 3.095 | 0 | — |
| produtos | 32.951 | 0 | categoria 610 · medidas 2 |
| geolocalizacao | 1.000.163 | **261.831** | — |
| traducao_categorias | 71 | 0 | — |

Período dos pedidos: **set/2016 a out/2018**. Fora do intervalo jan/2017–ago/2018 há pouquíssimos pedidos (4 em set/2016, 1 em dez/2016, 16 em set/2018, 4 em out/2018), então as análises temporais devem usar **jan/2017–ago/2018** para não distorcer tendências.

## Decisões
| # | Problema encontrado | Decisão | Por quê |
|---|---|---|---|
| 1 | Datas lidas como texto | `pd.to_datetime` em pedidos/itens/avaliações | Permite calcular atraso e agrupar por mês |
| 2 | Nulos em datas de orders | **Mantidos** | Pedido cancelado/em andamento não tem data de entrega; é informação, não erro |
| 3 | 8 pedidos `delivered` sem data de entrega | Mantidos na base, **excluídos** das métricas de prazo | Sem data não há como medir atraso |
| 4 | Pedidos com status `canceled`/`unavailable` (1.234) | Mantidos, filtrados nas análises de receita | Decisão por análise, não na limpeza |
| 5 | 775 pedidos sem item; 1 sem pagamento | Mantidos em `orders` | Geram NaN no join; receita deles é 0 |
| 6 | Avaliações: 551 `id_pedido` repetidos (814 `id_avaliacao` repetidos) | 1 avaliação por pedido: **a mais recente** | Evita duplicar pedidos/receita no join. 99.224 → 98.673 |
| 7 | Texto dos comentários | Removido do dado limpo | Não usado nas perguntas; reduz peso |
| 8 | Erro de grafia `lenght` nas colunas de produtos | Corrigido já na carga (`tamanho_nome`, `tamanho_descricao`) | Legibilidade |
| 9 | 610 produtos sem categoria | `sem_categoria` | Não perder itens no join; vão aparecer como categoria própria |
| 10 | 2 categorias sem tradução (`pc_gamer`, `portateis_cozinha_e_preparadores_de_alimentos`) | Tradução manual | Evita NaN em gráficos por categoria |
| 11 | geolocation com 1M linhas e 19.015 CEPs únicos | Agregada por CEP (mediana de lat/lng) | Join 1:1; sem isso o join multiplicaria linhas |
| 12 | Frete = 0 em 383 itens | Mantido | Frete grátis é plausível |
| 13 | Pagamentos `not_defined` (3) e valor 0 (9) | Mantidos | Impacto desprezível; receita virá de `items` |

## Ponto de atenção: definição de receita
- Soma de `preco` dos itens: **R$ 13.591.643,70** · soma de `valor_frete`: **R$ 2.251.909,54** (total 15,84 mi)
- Soma de `valor_pagamento`: **R$ 16.008.872,12**

A diferença vem de juros de parcelamento e vouchers. **Decisão proposta:** faturamento = `preco` (produtos); frete analisado à parte. Isso é pergunta 6 e será confirmado na Etapa 3.
