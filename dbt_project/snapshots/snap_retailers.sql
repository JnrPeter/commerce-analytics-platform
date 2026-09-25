{% snapshot snap_retailers %}

{{
    config(
        target_schema='snapshots',
        unique_key='retailer_id',
        strategy='timestamp',
        updated_at='updated_at'
    )
}}

select * from {{ source('commerce', 'retailers') }}

{% endsnapshot %}
