with orders as (
    select * from {{ ref('fct_orders') }}
),

zones as (
    select * from {{ ref('zone_lookup') }}
)

select
    cast(o.created_at as date)                                        as order_date,
    o.zone,
    z.region,
    z.area_type,
    count(distinct o.order_id)                                        as order_count,
    count(distinct o.customer_id)                                     as unique_customers,
    count(distinct o.retailer_id)                                     as unique_retailers,
    sum(o.total_amount)                                               as total_revenue,
    sum(o.subtotal)                                                   as gross_revenue,
    sum(o.discount_amount)                                            as total_discounts,
    sum(o.delivery_fee)                                               as total_delivery_fees,
    avg(o.total_amount)                                               as avg_order_value,
    avg(o.rating)                                                     as avg_rating,
    avg(o.actual_delivery_minutes)                                    as avg_delivery_minutes,
    count(case when o.delivery_performance = 'on_time' then 1 end)    as on_time_count,
    count(case when o.delivery_performance is not null then 1 end)    as delivered_count,
    round(
        count(case when o.delivery_performance = 'on_time' then 1 end) * 100.0
        / nullif(count(case when o.delivery_performance is not null then 1 end), 0),
        2
    )                                                                 as on_time_pct,
    count(case when o.status = 'cancelled' then 1 end)                as cancelled_count,
    round(
        count(case when o.status = 'cancelled' then 1 end) * 100.0
        / nullif(count(distinct o.order_id), 0),
        2
    )                                                                 as cancellation_rate
from orders o
left join zones z on o.zone = z.zone
group by 1, 2, 3, 4
