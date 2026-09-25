with source as (
    select * from {{ source('commerce', 'retailers') }}
)

select
    retailer_id,
    name            as retailer_name,
    zone,
    category,
    lower(status)   as status,
    onboarded_at,
    updated_at
from source
