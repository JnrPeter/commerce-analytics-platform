{{
    config(
        materialized='incremental',
        unique_key='item_id',
        incremental_strategy='merge'
    )
}}

select
    item_id,
    order_id,
    customer_id,
    retailer_id,
    zone,
    order_status,
    product_id,
    product_name,
    product_category,
    quantity,
    unit_price,
    line_total,
    created_at
from {{ ref('int_order_items_enriched') }}

{% if is_incremental() %}
where created_at > (select max(created_at) from {{ this }})
{% endif %}
