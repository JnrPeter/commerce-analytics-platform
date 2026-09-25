-- SCD Type 1: latest state only, overwrites on change
select
    customer_id,
    customer_name,
    phone,
    email,
    tier,
    created_at,
    updated_at
from {{ ref('stg_customers') }}
