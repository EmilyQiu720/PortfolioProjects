# Dashboard Specification

## Dashboard 1: Executive Overview

Purpose: Give leadership a one-page view of operating health.

Recommended layout:

- Top KPI cards:
  - Revenue
  - Gross Margin
  - On-Time Delivery Rate
  - Return Rate
  - High-Risk SKU Count
- Left: regional performance map or region bar chart
- Center: revenue and on-time trend by week
- Right: top at-risk warehouses
- Bottom: top SKU risks table

Filters:

- Date range
- Region
- Category
- Customer segment
- Metric selector parameter

Actions:

- Click a region to filter all dashboard sheets.
- Click a warehouse to open fulfillment drilldown.

## Dashboard 2: Fulfillment Performance

Purpose: Identify warehouse and carrier bottlenecks.

Recommended sheets:

- Warehouse SLA bar chart
- Late shipment trend by week
- Average fulfillment days by warehouse
- Carrier on-time rate
- Late order detail table

Key fields:

- Region
- Warehouse
- Carrier
- On-Time Delivery Rate
- Average Fulfillment Days
- Late Days
- SLA Gap
- Warehouse SLA Status

## Dashboard 3: Inventory Risk

Purpose: Identify products likely to stock out.

Recommended sheets:

- SKU stockout risk ranked bar chart
- Inventory days remaining heatmap by warehouse and category
- Reorder flag table
- Demand vs on-hand scatter plot

Key fields:

- SKU
- Product Name
- Category
- Warehouse
- On-Hand Units
- Monthly Demand Units
- Inventory Days Remaining
- Stockout Risk Score
- Reorder Flag

## Dashboard 4: Returns & Profitability

Purpose: Connect fulfillment quality with returns and margin risk.

Recommended sheets:

- Return rate by category
- Return reason breakdown
- Gross margin by SKU
- Revenue vs gross margin quadrant
- Returned order detail table

Key fields:

- Category
- Product Name
- SKU
- Return Reason
- Return Rate
- Refund Rate
- Gross Margin
- Revenue

## Dashboard 5: Drilldown

Purpose: Give the user an investigation path from summary signal to order detail.

Drilldown path:

```text
Region -> Warehouse -> Category -> SKU -> Order ID
```

Detail table columns:

- Order ID
- Order Date
- Region
- Warehouse
- SKU
- Product Name
- Revenue
- Gross Profit
- Carrier
- Fulfillment Days
- Late Days
- Return Reason
