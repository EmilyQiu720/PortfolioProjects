# Data Dictionary

## Relationship Model

Use these relationships in Tableau:

| Left Table | Key | Right Table | Key | Cardinality |
|---|---|---|---|---|
| `orders` | `order_id` | `shipments` | `order_id` | One-to-one |
| `orders` | `order_id` | `returns` | `order_id` | One-to-many / zero-to-many |
| `orders` | `sku_id` + `warehouse` | `inventory` | `sku_id` + `warehouse` | Many-to-one |
| `orders` | `warehouse` | `warehouse_targets` | `warehouse` | Many-to-one |

If Tableau Public makes multi-field relationships awkward, create the relationship between `orders` and `inventory` on `sku_id`, then use warehouse filters consistently on dashboards.

## orders.csv

| Field | Type | Description |
|---|---|---|
| `order_id` | string | Unique retail order identifier. |
| `order_date` | date | Order creation date. |
| `region` | string | Sales and fulfillment region. |
| `warehouse` | string | Warehouse responsible for fulfillment. |
| `customer_segment` | string | Consumer, Small Business, or Enterprise. |
| `sku_id` | string | Product SKU identifier. |
| `category` | string | Product category. |
| `product_name` | string | Product name. |
| `quantity` | integer | Units ordered. |
| `unit_price` | decimal | Selling price per unit before discount. |
| `unit_cost` | decimal | Product cost per unit. |
| `discount_rate` | decimal | Discount rate applied to the order. |
| `revenue` | decimal | Net revenue after discount. |
| `gross_profit` | decimal | Revenue less product cost. |
| `order_status` | string | Completed, Returned, or Cancelled. |

## shipments.csv

| Field | Type | Description |
|---|---|---|
| `shipment_id` | string | Unique shipment identifier. |
| `order_id` | string | Order key. |
| `carrier` | string | Fulfillment carrier. |
| `ship_date` | date | Date order left warehouse. |
| `promised_date` | date | Customer promise date. |
| `delivery_date` | date | Actual delivery date. |
| `fulfillment_days` | integer | Days from order to delivery. |
| `on_time_flag` | integer | 1 if delivered on or before promised date, otherwise 0. |
| `late_days` | integer | Days late beyond promise date. |
| `shipment_cost` | decimal | Cost to ship the order. |

## inventory.csv

| Field | Type | Description |
|---|---|---|
| `snapshot_date` | date | Inventory snapshot date. |
| `region` | string | Region. |
| `warehouse` | string | Warehouse. |
| `sku_id` | string | SKU identifier. |
| `category` | string | Category. |
| `product_name` | string | Product name. |
| `on_hand_units` | integer | Current inventory. |
| `reorder_point` | integer | Minimum desired inventory. |
| `monthly_demand_units` | integer | Recent monthly demand. |
| `inventory_value` | decimal | Inventory value at unit cost. |

## returns.csv

| Field | Type | Description |
|---|---|---|
| `return_id` | string | Unique return identifier. |
| `order_id` | string | Returned order key. |
| `return_date` | date | Return creation date. |
| `return_reason` | string | Return reason. |
| `refund_amount` | decimal | Refund value. |
| `restockable_flag` | integer | 1 if item can be restocked, otherwise 0. |

## warehouse_targets.csv

| Field | Type | Description |
|---|---|---|
| `region` | string | Region. |
| `warehouse` | string | Warehouse. |
| `target_on_time_rate` | decimal | SLA target for on-time delivery. |
| `target_fill_rate` | decimal | Inventory fill-rate target. |
| `target_return_rate` | decimal | Return-rate target. |
| `target_gross_margin` | decimal | Gross-margin target. |
