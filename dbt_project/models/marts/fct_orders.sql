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
    customer_name,
    customer_tier,
    retailer_id,
    retailer_name,
    retailer_category,
    zone,
    status,
    payment_method,
    order_channel,
    subtotal,
    discount_amount,
    delivery_fee,
    total_amount,
    estimated_delivery_minutes,
    actual_delivery_minutes,
    delivery_delay_minutes,
    delivery_performance,
    rating,
    created_at,
    updated_at
from {{ ref('int_orders_enriched') }}

{% if is_incremental() %}
where updated_at > (select max(updated_at) from {{ this }})
{% endif %}
