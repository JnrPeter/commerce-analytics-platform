with source as (
    select * from {{ source('commerce', 'orders') }}
)

select
    order_id,
    customer_id,
    retailer_id,
    zone,
    lower(status)   as status,
    total_amount,
    created_at,
    updated_at
from source
