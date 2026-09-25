with source as (
    select * from {{ source('commerce', 'order_items') }}
)

select
    item_id,
    order_id,
    product_id,
    product_name,
    quantity,
    unit_price,
    quantity * unit_price   as line_total,
    created_at
from source
