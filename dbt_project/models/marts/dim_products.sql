-- SCD Type 2: tracks price history via dbt snapshots
-- Each row represents one version of a product's profile
-- is_current = true for the active record
select
    dbt_scd_id                                                  as product_key,
    product_id,
    name                                                        as product_name,
    category,
    price,
    dbt_valid_from                                              as valid_from,
    dbt_valid_to                                                as valid_to,
    case when dbt_valid_to is null then true else false end      as is_current
from {{ ref('snap_products') }}
