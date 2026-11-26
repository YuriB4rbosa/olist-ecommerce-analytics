# Rascunho do post de LinkedIn

> Antes de publicar: troque `[LINK]`, confira se os prints do dashboard estão no repositório e **remova a linha marcada com ⚠️ se ainda não tiver montado o dashboard**. Anexe 1 imagem forte: `docs/img/q3_atraso_vs_nota.png` ou a Visão Executiva do dashboard.

---

## Versão principal (formato problema → descoberta → ferramentas)

Analisei ~100 mil pedidos de um e-commerce brasileiro para responder uma pergunta simples: **onde esse negócio está perdendo dinheiro sem perceber?** 🧵

**O problema**
O faturamento crescia, mas ninguém sabia se vinha de clientes novos, de preço ou de volume. E se a operação estava ajudando ou atrapalhando.

**O que descobri**

📉 O crescimento travou. Jan–ago/2018 foi +138% sobre 2017, mas de abril a agosto o faturamento caiu 14,6%. O ticket médio ficou parado em ~R$ 137: o crescimento era só volume.

⏱️ Atraso é o maior destruidor de satisfação. Pedido no prazo: nota 4,29. Atrasado: 2,27. Com apenas 1 a 3 dias de atraso, a nota já cai para 3,29.

🗺️ O problema logístico não são os vendedores, é a geografia. 37 vendedores concentram o pior desempenho, mas são só 2,8% dos pedidos. Já em Alagoas 21% das entregas atrasam, contra 4,5% em São Paulo.

🔁 Só 3% dos clientes compram de novo. E quem volta, volta rápido: mediana de 28 dias. A janela para recompra está nos primeiros 30 dias.

📦 Frete pesa mais onde dói menos: em pedidos abaixo de R$ 50, ele equivale a 46% do valor dos produtos. Acima de R$ 500, 4%.

**O que eu recomendaria**
→ Meta de zero atrasos acima de 3 dias, com prazos mais realistas no Nordeste
→ Ação de recompra nos 30 dias pós-entrega
→ Teste A/B de frete grátis para pedidos pequenos (os dados mostram correlação, não causa, então eu testaria antes de apostar)

**Como fiz**
🐍 Python (Pandas) para limpeza, modelagem em estrela e análises
📊 Matplotlib/Seaborn para os gráficos
⚡ Power BI + DAX para o dashboard ⚠️ *(remover se ainda não estiver pronto)*

Um detalhe que me ensinou muito: ao validar minhas medidas, descobri que contar atraso por linha de item e por pedido distinto dava resultados diferentes (40 vs 37 vendedores problemáticos). Pequena diferença no número, grande diferença na credibilidade da análise.

Código, notebooks e documentação das decisões: [LINK]

Vim do desenvolvimento backend (Python/Django/PostgreSQL) e esse projeto foi minha forma de aplicar esse olhar a dados. Feedback é muito bem-vindo!

#AnáliseDeDados #Python #Pandas #PowerBI #DataAnalytics #Portfólio

---

## Versão curta (se preferir algo mais enxuto)

Usei dados reais de 100 mil pedidos de um e-commerce para responder: onde esse negócio perde dinheiro sem perceber?

3 achados:
• Pedido atrasado recebe nota 2,27. No prazo, 4,29.
• O gargalo logístico é geográfico: 21% de atraso em AL vs 4,5% em SP. Só 2,8% dos pedidos vêm dos vendedores com pior desempenho.
• Só 3% dos clientes voltam a comprar, e quem volta o faz em até ~28 dias.

Feito com Python/Pandas [+ Power BI]. Código e decisões no GitHub: [LINK]

#AnáliseDeDados #Python #PowerBI

---

## Dicas de publicação
- Publique em dia útil de manhã e responda os comentários na primeira hora.
- Fixe o repositório no seu perfil do GitHub e adicione o projeto à seção "Destaques" do LinkedIn.
- Tenha uma frase pronta para entrevistas sobre uma decisão difícil: por exemplo, por que usar `customer_unique_id` e não `customer_id`, ou por que a janela de análise é jan/2017–ago/2018.
