select
    cast(created_at as date)        as order_date,
    zone,
    count(distinct order_id)        as order_count,
    count(distinct customer_id)     as unique_customers,
    count(distinct retailer_id)     as unique_retailers,
    sum(total_amount)               as total_revenue,
    avg(total_amount)               as avg_order_value
from {{ ref('fct_orders') }}
where status != 'cancelled'
group by 1, 2
