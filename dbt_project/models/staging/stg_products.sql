with source as (
    select * from {{ source('commerce', 'products') }}
)

select
    product_id,
    name            as product_name,
    category,
    price,
    created_at,
    updated_at
from source
