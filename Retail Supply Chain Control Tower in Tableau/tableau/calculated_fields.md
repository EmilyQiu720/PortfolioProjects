# Tableau Calculated Fields

Create these fields in Tableau after connecting the CSV files.

## Parameters

### `p.Metric Selector`

Data type: String

Allowed values:

- Revenue
- Gross Margin
- On-Time Rate
- Return Rate
- Stockout Risk

### `p.SLA Threshold`

Data type: Float

Default: `0.88`

Display format: Percentage

## Core Measures

### `Revenue`

```tableau
SUM([revenue])
```

### `Gross Profit`

```tableau
SUM([gross_profit])
```

### `Gross Margin`

```tableau
SUM([gross_profit]) / SUM([revenue])
```

### `On-Time Delivery Rate`

```tableau
AVG([on_time_flag])
```

### `Late Shipment Rate`

```tableau
1 - [On-Time Delivery Rate]
```

### `Average Fulfillment Days`

```tableau
AVG([fulfillment_days])
```

### `Return Count`

```tableau
COUNTD([return_id])
```

### `Order Count`

```tableau
COUNTD([order_id])
```

### `Return Rate`

```tableau
[Return Count] / [Order Count]
```

### `Refund Rate`

```tableau
SUM([refund_amount]) / SUM([revenue])
```

## Inventory Measures

### `Daily Demand Units`

```tableau
SUM([monthly_demand_units]) / 30
```

### `Inventory Days Remaining`

```tableau
SUM([on_hand_units]) / [Daily Demand Units]
```

### `Fill Rate`

```tableau
SUM([on_hand_units]) / SUM([monthly_demand_units])
```

### `Reorder Flag`

```tableau
IF SUM([on_hand_units]) <= SUM([reorder_point]) THEN "Reorder"
ELSE "Healthy"
END
```

### `Stockout Risk Score`

```tableau
IF [Inventory Days Remaining] < 7 THEN 100
ELSEIF [Inventory Days Remaining] < 14 THEN 75
ELSEIF [Inventory Days Remaining] < 21 THEN 50
ELSE 20
END
```

### `Stockout Risk Band`

```tableau
IF [Stockout Risk Score] >= 75 THEN "High"
ELSEIF [Stockout Risk Score] >= 50 THEN "Medium"
ELSE "Low"
END
```

## Target / Variance Measures

### `SLA Gap`

```tableau
[On-Time Delivery Rate] - AVG([target_on_time_rate])
```

### `Gross Margin Gap`

```tableau
[Gross Margin] - AVG([target_gross_margin])
```

### `Return Rate Gap`

```tableau
[Return Rate] - AVG([target_return_rate])
```

### `Warehouse SLA Status`

```tableau
IF [On-Time Delivery Rate] >= AVG([target_on_time_rate]) THEN "On Target"
ELSEIF [On-Time Delivery Rate] >= [p.SLA Threshold] THEN "Watch"
ELSE "At Risk"
END
```

## LOD-Style Fields

### `Warehouse Revenue LOD`

```tableau
{ FIXED [warehouse] : SUM([revenue]) }
```

### `Warehouse On-Time Rate LOD`

```tableau
{ FIXED [warehouse] : AVG([on_time_flag]) }
```

### `SKU Revenue LOD`

```tableau
{ FIXED [sku_id] : SUM([revenue]) }
```

### `SKU Return Rate LOD`

```tableau
{ FIXED [sku_id] : COUNTD([return_id]) / COUNTD([order_id]) }
```

## Parameter-Driven Display

### `Selected Metric`

```tableau
CASE [p.Metric Selector]
WHEN "Revenue" THEN [Revenue]
WHEN "Gross Margin" THEN [Gross Margin]
WHEN "On-Time Rate" THEN [On-Time Delivery Rate]
WHEN "Return Rate" THEN [Return Rate]
WHEN "Stockout Risk" THEN AVG([Stockout Risk Score])
END
```

### `Selected Metric Label`

```tableau
[p.Metric Selector]
```
