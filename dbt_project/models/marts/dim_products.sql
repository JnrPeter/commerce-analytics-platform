-- SCD Type 1: latest state only
select
    product_id,
    product_name,
    category,
    price,
    created_at,
    updated_at
from {{ ref('stg_products') }}
