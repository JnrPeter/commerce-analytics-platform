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
    c.tier              as customer_tier,
    o.retailer_id,
    r.retailer_name,
    r.category          as retailer_category,
    o.zone,
    o.status,
    o.payment_method,
    o.order_channel,
    o.subtotal,
    o.discount_amount,
    o.delivery_fee,
    o.total_amount,
    o.estimated_delivery_minutes,
    o.actual_delivery_minutes,
    o.actual_delivery_minutes - o.estimated_delivery_minutes as delivery_delay_minutes,
    case
        when o.actual_delivery_minutes is null then null
        when o.actual_delivery_minutes <= o.estimated_delivery_minutes then 'on_time'
        when o.actual_delivery_minutes <= o.estimated_delivery_minutes + 15 then 'slightly_late'
        when o.actual_delivery_minutes <= o.estimated_delivery_minutes + 30 then 'late'
        else 'very_late'
    end as delivery_performance,
    o.rating,
    o.created_at,
    o.updated_at
from orders o
left join customers c on o.customer_id = c.customer_id
left join retailers r on o.retailer_id = r.retailer_id
