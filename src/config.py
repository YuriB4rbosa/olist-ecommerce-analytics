"""Caminhos e constantes do projeto (sempre relativos à raiz do repositório)."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BRUTO = RAIZ / "data" / "raw"
PROCESSADO = RAIZ / "data" / "processed"
SEMENTE = 42

# nome curto da tabela -> arquivo CSV original
ARQUIVOS = {
    "pedidos": "olist_orders_dataset.csv",
    "itens": "olist_order_items_dataset.csv",
    "pagamentos": "olist_order_payments_dataset.csv",
    "avaliacoes": "olist_order_reviews_dataset.csv",
    "clientes": "olist_customers_dataset.csv",
    "vendedores": "olist_sellers_dataset.csv",
    "produtos": "olist_products_dataset.csv",
    "geolocalizacao": "olist_geolocation_dataset.csv",
    "traducao_categorias": "product_category_name_translation.csv",
}

# Colunas originais (inglês) -> nomes em português usados em todo o projeto.
# A tradução acontece na carga (src/carga.py), então todo o código seguinte já usa os nomes em português.
COLUNAS = {
    "pedidos": {
        "order_id": "id_pedido",
        "customer_id": "id_cliente",
        "order_status": "status_pedido",
        "order_purchase_timestamp": "datahora_compra",
        "order_approved_at": "datahora_aprovacao",
        "order_delivered_carrier_date": "data_envio_transportadora",
        "order_delivered_customer_date": "data_entrega_cliente",
        "order_estimated_delivery_date": "data_entrega_estimada",
    },
    "itens": {
        "order_id": "id_pedido",
        "order_item_id": "id_item",
        "product_id": "id_produto",
        "seller_id": "id_vendedor",
        "shipping_limit_date": "data_limite_envio",
        "price": "preco",
        "freight_value": "valor_frete",
    },
    "pagamentos": {
        "order_id": "id_pedido",
        "payment_sequential": "sequencial_pagamento",
        "payment_type": "tipo_pagamento",
        "payment_installments": "parcelas",
        "payment_value": "valor_pagamento",
    },
    "avaliacoes": {
        "review_id": "id_avaliacao",
        "order_id": "id_pedido",
        "review_score": "nota_avaliacao",
        "review_comment_title": "titulo_comentario",
        "review_comment_message": "mensagem_comentario",
        "review_creation_date": "data_criacao_avaliacao",
        "review_answer_timestamp": "datahora_resposta_avaliacao",
    },
    "clientes": {
        "customer_id": "id_cliente",
        "customer_unique_id": "id_cliente_unico",
        "customer_zip_code_prefix": "cep_prefixo",
        "customer_city": "cidade",
        "customer_state": "uf",
    },
    "vendedores": {
        "seller_id": "id_vendedor",
        "seller_zip_code_prefix": "cep_prefixo",
        "seller_city": "cidade",
        "seller_state": "uf",
    },
    "produtos": {
        "product_id": "id_produto",
        "product_category_name": "nome_categoria",
        "product_name_lenght": "tamanho_nome",          # o original tem o erro de grafia "lenght"
        "product_description_lenght": "tamanho_descricao",
        "product_photos_qty": "qtd_fotos",
        "product_weight_g": "peso_g",
        "product_length_cm": "comprimento_cm",
        "product_height_cm": "altura_cm",
        "product_width_cm": "largura_cm",
    },
    "geolocalizacao": {
        "geolocation_zip_code_prefix": "cep_prefixo",
        "geolocation_lat": "latitude",
        "geolocation_lng": "longitude",
        "geolocation_city": "cidade",
        "geolocation_state": "uf",
    },
    "traducao_categorias": {
        "product_category_name": "nome_categoria",
        "product_category_name_english": "categoria_en",
    },
}
