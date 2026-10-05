select
    cast(created_at as date)                                        as order_date,
    zone,
    count(distinct order_id)                                        as order_count,
    count(distinct customer_id)                                     as unique_customers,
    count(distinct retailer_id)                                     as unique_retailers,
    sum(total_amount)                                               as total_revenue,
    sum(subtotal)                                                   as gross_revenue,
    sum(discount_amount)                                            as total_discounts,
    sum(delivery_fee)                                               as total_delivery_fees,
    avg(total_amount)                                               as avg_order_value,
    avg(rating)                                                     as avg_rating,
    avg(actual_delivery_minutes)                                    as avg_delivery_minutes,
    count(case when delivery_performance = 'on_time' then 1 end)    as on_time_count,
    count(case when delivery_performance is not null then 1 end)    as delivered_count,
    round(
        count(case when delivery_performance = 'on_time' then 1 end) * 100.0
        / nullif(count(case when delivery_performance is not null then 1 end), 0),
        2
    )                                                               as on_time_pct,
    count(case when status = 'cancelled' then 1 end)                as cancelled_count,
    round(
        count(case when status = 'cancelled' then 1 end) * 100.0
        / nullif(count(distinct order_id), 0),
        2
    )                                                               as cancellation_rate
from {{ ref('fct_orders') }}
group by 1, 2
