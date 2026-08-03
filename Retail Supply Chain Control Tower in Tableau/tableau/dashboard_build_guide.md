# Tableau Public Build Guide

This guide assumes Tableau Public Desktop is installed.

## Step 1: Connect Data

1. Open Tableau Public.
2. Choose `Text file`.
3. Select `data/orders.csv`.
4. Drag the remaining CSVs into the data model:
   - `shipments.csv`
   - `returns.csv`
   - `inventory.csv`
   - `warehouse_targets.csv`

## Step 2: Create Relationships

Create these relationships:

1. `orders.order_id = shipments.order_id`
2. `orders.order_id = returns.order_id`
3. `orders.warehouse = warehouse_targets.warehouse`
4. `orders.sku_id = inventory.sku_id`

If Tableau lets you add a second relationship key for inventory, also add:

```text
orders.warehouse = inventory.warehouse
```

## Step 3: Set Data Types

Set date fields:

- `order_date`
- `ship_date`
- `promised_date`
- `delivery_date`
- `return_date`
- `snapshot_date`

Set geographic role:

- `region`: None or State/Province only if you map with generated coordinates later

Set numeric fields:

- revenue
- gross_profit
- quantity
- unit_price
- unit_cost
- shipment_cost
- refund_amount
- on_hand_units
- reorder_point
- monthly_demand_units

## Step 4: Create Parameters

Create:

1. `p.Metric Selector`
   - Type: String
   - Values: Revenue, Gross Margin, On-Time Rate, Return Rate, Stockout Risk
2. `p.SLA Threshold`
   - Type: Float
   - Default: 0.88
   - Display as percentage

## Step 5: Create Calculated Fields

Copy the fields from:

```text
tableau/calculated_fields.md
```

Start with:

- Revenue
- Gross Profit
- Gross Margin
- On-Time Delivery Rate
- Late Shipment Rate
- Return Count
- Order Count
- Return Rate
- Inventory Days Remaining
- Stockout Risk Score
- Warehouse SLA Status
- Selected Metric

## Step 6: Build Worksheets

### KPI Cards

Create one worksheet per KPI:

- Revenue
- Gross Margin
- On-Time Delivery Rate
- Return Rate
- High Risk SKU Count

Use large text marks and format numbers:

- Revenue: currency
- Gross Margin: percentage
- On-Time Delivery Rate: percentage
- Return Rate: percentage
- SKU Count: whole number

### Regional Performance

Rows: `region`

Columns: `Selected Metric`

Color: `Warehouse SLA Status`

Sort descending by selected metric.

### Warehouse SLA

Rows: `warehouse`

Columns: `On-Time Delivery Rate`

Color: `Warehouse SLA Status`

Reference line: `target_on_time_rate`

### Late Shipment Trend

Columns: `WEEK(order_date)`

Rows: `Late Shipment Rate`

Color: `region`

### Inventory Risk Ranking

Rows: `product_name`

Columns: `Stockout Risk Score`

Color: `Stockout Risk Band`

Filter: `Stockout Risk Band` = High or Medium.

### Return Reason Breakdown

Rows: `return_reason`

Columns: `Return Count`

Sort descending.

### Profitability Quadrant

Columns: `Revenue`

Rows: `Gross Margin`

Detail: `sku_id`, `product_name`

Color: `category`

Size: `Return Rate`

## Step 7: Build Dashboards

Create these dashboards:

1. `Executive Overview`
2. `Fulfillment Performance`
3. `Inventory Risk`
4. `Returns & Profitability`
5. `Drilldown`

Use the layout in `tableau/dashboard_spec.md`.

## Step 8: Add Dashboard Actions

On `Executive Overview`:

- Use region bar chart as filter.
- Use warehouse SLA chart as filter.

On `Inventory Risk`:

- Click SKU to filter the detail table.

On `Returns & Profitability`:

- Click category to filter SKU profitability.

## Step 9: Publish

1. Choose `Server`.
2. Choose `Tableau Public`.
3. Choose `Save to Tableau Public`.
4. Name the workbook:

```text
Retail Supply Chain Control Tower
```

5. Copy the published URL into:

```text
tableau/tableau_public_link.txt
```

After you send me the URL, I can update the website project card with the live Tableau Public link.
