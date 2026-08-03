# Methodology

## Business Framing

This project treats Tableau as a supply chain control tower. The goal is not to show every metric, but to help leadership move from executive signal to operational root cause.

The dashboard flow is:

```text
Executive Overview -> Fulfillment Performance -> Inventory Risk -> Returns & Profitability -> Order Drilldown
```

## Synthetic Data Generation

The Python generator creates six months of retail operations data:

- daily orders by region, warehouse, category, SKU, and customer segment
- shipment performance with carrier, promise date, delivery date, and late days
- inventory snapshots with on-hand units, reorder point, monthly demand, and inventory value
- returns with reason, refund amount, and restockable flag
- warehouse targets for SLA, fill rate, returns, and gross margin

The data intentionally includes operational patterns:

- Miami DC and Los Angeles DC have elevated late-delivery risk.
- Apparel has a higher return probability.
- Some SKUs have low inventory relative to demand.
- On-time rate varies by region and warehouse.
- Profitability varies by category and SKU.

## KPI Definitions

| KPI | Definition |
|---|---|
| Revenue | Sum of order revenue. |
| Gross Profit | Sum of gross profit. |
| Gross Margin | Gross profit divided by revenue. |
| On-Time Delivery Rate | Average of `on_time_flag`. |
| Late Shipment Rate | One minus on-time delivery rate. |
| Average Fulfillment Days | Average days from order to delivery. |
| Return Rate | Returned orders divided by total orders. |
| Fill Rate | On-hand units divided by monthly demand units. |
| Inventory Days Remaining | On-hand units divided by daily demand velocity. |
| Stockout Risk Score | Weighted score based on inventory days, reorder flag, and demand velocity. |

## Tableau Design Principles

- Use parameters for metric selection and SLA thresholding.
- Use dashboard actions to support region-to-warehouse-to-SKU drilldown.
- Use maps and bar charts for fast operational scanning.
- Use detail tables only after a user has filtered into a problem area.
- Keep dashboard colors meaningful: teal for healthy, amber for watchlist, red for risk.

## Validation

The validation script confirms:

- one shipment per order
- returns reference valid orders
- inventory warehouse values exist in target table
- revenue and gross profit are non-negative
- fulfillment and late-day metrics are non-negative
- on-time flag is binary
