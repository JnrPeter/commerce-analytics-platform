{{
    config(
        materialized='incremental',
        unique_key='order_id',
        incremental_strategy='merge'
    )
}}

select
    order_id,
    customer_id,
    retailer_id,
    zone,
    status,
    total_amount,
    created_at,
    updated_at
from {{ ref('int_orders_enriched') }}

{% if is_incremental() %}
where updated_at > (select max(updated_at) from {{ this }})
{% endif %}
