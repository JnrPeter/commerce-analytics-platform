-- Every order must have at least one line item.
-- If this returns rows, we have orphan orders.
select o.order_id
from {{ ref('fct_orders') }} o
left join {{ ref('fct_order_items') }} i on o.order_id = i.order_id
where i.item_id is null
