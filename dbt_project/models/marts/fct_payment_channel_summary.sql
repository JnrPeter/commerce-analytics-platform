select
    cast(created_at as date)        as order_date,
    payment_method,
    order_channel,
    count(distinct order_id)        as order_count,
    sum(total_amount)               as total_revenue,
    avg(total_amount)               as avg_order_value,
    sum(discount_amount)            as total_discounts,
    avg(rating)                     as avg_rating,
    count(case when status = 'cancelled' then 1 end) as cancelled_count,
    round(
        count(case when status = 'cancelled' then 1 end) * 100.0
        / nullif(count(distinct order_id), 0),
        2
    )                               as cancellation_rate
from {{ ref('fct_orders') }}
group by 1, 2, 3
