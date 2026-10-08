with source as (
    select * from {{ source('commerce', 'orders') }}
)

select
    order_id,
    customer_id,
    retailer_id,
    zone,
    lower(status)               as status,
    lower(payment_method)       as payment_method,
    lower(order_channel)        as order_channel,
    subtotal,
    discount_amount,
    delivery_fee,
    total_amount,
    estimated_delivery_minutes,
    actual_delivery_minutes,
    rating,
    created_at,
    updated_at
from source
