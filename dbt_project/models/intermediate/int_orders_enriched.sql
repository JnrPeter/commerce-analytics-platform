with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

retailers as (
    select * from {{ ref('stg_retailers') }}
)

select
    o.order_id,
    o.customer_id,
    c.customer_name,
    c.tier          as customer_tier,
    o.retailer_id,
    r.retailer_name,
    r.category      as retailer_category,
    o.zone,
    o.status,
    o.total_amount,
    o.created_at,
    o.updated_at
from orders o
left join customers c on o.customer_id = c.customer_id
left join retailers r on o.retailer_id = r.retailer_id
