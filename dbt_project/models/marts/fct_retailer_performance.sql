with orders as (
    select * from {{ ref('fct_orders') }}
),

items as (
    select * from {{ ref('fct_order_items') }}
    where order_status != 'cancelled'
),

retailers as (
    select * from {{ ref('dim_retailers') }}
    where is_current = true
),

zones as (
    select * from {{ ref('zone_lookup') }}
)

select
    r.retailer_id,
    r.retailer_name,
    r.zone,
    z.region,
    z.area_type,
    r.category,
    r.status,
    count(distinct o.order_id)                                      as total_orders,
    count(distinct case when o.status != 'cancelled' then o.order_id end) as completed_orders,
    count(distinct o.customer_id)                                   as unique_customers,
    sum(o.total_amount)                                             as total_revenue,
    avg(o.total_amount)                                             as avg_order_value,
    sum(o.discount_amount)                                          as total_discounts_given,
    sum(i.quantity)                                                  as total_items_sold,
    avg(o.rating)                                                   as avg_rating,
    avg(o.actual_delivery_minutes)                                  as avg_delivery_minutes,
    count(case when o.delivery_performance = 'on_time' then 1 end)  as on_time_count,
    count(case when o.delivery_performance is not null then 1 end)  as delivered_count,
    round(
        count(case when o.delivery_performance = 'on_time' then 1 end) * 100.0
        / nullif(count(case when o.delivery_performance is not null then 1 end), 0),
        2
    )                                                               as on_time_pct,
    round(
        count(case when o.status = 'cancelled' then 1 end) * 100.0
        / nullif(count(distinct o.order_id), 0),
        2
    )                                                               as cancellation_rate,
    min(o.created_at)                                               as first_order_at,
    max(o.created_at)                                               as last_order_at
from retailers r
left join orders o on r.retailer_id = o.retailer_id
left join items i on o.order_id = i.order_id
left join zones z on r.zone = z.zone
group by 1, 2, 3, 4, 5, 6, 7
