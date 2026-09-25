with orders as (
    select * from {{ ref('fct_orders') }}
    where status != 'cancelled'
),

items as (
    select * from {{ ref('fct_order_items') }}
    where order_status != 'cancelled'
),

retailers as (
    select * from {{ ref('dim_retailers') }}
    where is_current = true
)

select
    r.retailer_id,
    r.retailer_name,
    r.zone,
    r.category,
    r.status,
    count(distinct o.order_id)      as total_orders,
    count(distinct o.customer_id)   as unique_customers,
    sum(o.total_amount)             as total_revenue,
    avg(o.total_amount)             as avg_order_value,
    sum(i.quantity)                  as total_items_sold,
    min(o.created_at)               as first_order_at,
    max(o.created_at)               as last_order_at
from retailers r
left join orders o on r.retailer_id = o.retailer_id
left join items i on o.order_id = i.order_id
group by 1, 2, 3, 4, 5
