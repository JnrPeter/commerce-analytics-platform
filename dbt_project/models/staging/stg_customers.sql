with source as (
    select * from {{ source('commerce', 'customers') }}
)

select
    customer_id,
    name            as customer_name,
    phone,
    email,
    lower(tier)     as tier,
    created_at,
    updated_at
from source
