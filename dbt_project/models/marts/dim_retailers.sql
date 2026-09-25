-- SCD Type 2: tracks history via dbt snapshots
-- Each row represents one version of a retailer's profile
-- is_current = true for the active record
select
    dbt_scd_id                                                  as retailer_key,
    retailer_id,
    name                                                        as retailer_name,
    zone,
    category,
    status,
    onboarded_at,
    dbt_valid_from                                              as valid_from,
    dbt_valid_to                                                as valid_to,
    case when dbt_valid_to is null then true else false end      as is_current
from {{ ref('snap_retailers') }}
