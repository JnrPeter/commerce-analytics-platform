with items as (
    select * from {{ ref('stg_order_items') }}
),

products as (
    select * from {{ ref('stg_products') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
)

select
    i.item_id,
    i.order_id,
    o.customer_id,
    o.retailer_id,
    o.zone,
    o.status        as order_status,
    i.product_id,
    i.product_name,
    p.category      as product_category,
    i.quantity,
    i.unit_price,
    i.line_total,
    i.created_at
from items i
left join products p on i.product_id = p.product_id
left join orders o on i.order_id = o.order_id
