"""Generate Tableau-ready synthetic retail supply chain data."""

from __future__ import annotations

import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

REGIONS = {
    "West": ["Seattle DC", "Los Angeles DC", "Denver DC"],
    "Central": ["Dallas DC", "Chicago DC", "Minneapolis DC"],
    "East": ["New Jersey DC", "Atlanta DC", "Miami DC"],
}

CATEGORIES = {
    "Electronics": ["Noise-Canceling Headphones", "Smart Home Hub", "Portable Charger"],
    "Home": ["Air Purifier", "Bedding Set", "Kitchen Organizer"],
    "Apparel": ["Performance Jacket", "Running Shoes", "Travel Backpack"],
    "Beauty": ["Skin Care Kit", "Hair Dryer", "Fragrance Set"],
}

CARRIERS = ["ParcelFast", "ShipRight", "NorthLine", "MetroCourier"]
RETURN_REASONS = ["Damaged", "Wrong item", "Late delivery", "Changed mind", "Quality issue"]


def money(value: float) -> float:
    return round(value, 2)


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_products() -> list[dict]:
    products = []
    sku_id = 1001
    for category, names in CATEGORIES.items():
        for name in names:
            base_price = random.uniform(32, 260)
            unit_cost = base_price * random.uniform(0.42, 0.72)
            products.append(
                {
                    "sku_id": f"SKU-{sku_id}",
                    "category": category,
                    "product_name": name,
                    "unit_price": money(base_price),
                    "unit_cost": money(unit_cost),
                }
            )
            sku_id += 1
    return products


def generate_orders(products: list[dict]) -> list[dict]:
    rows = []
    start = date(2026, 1, 1)
    order_id = 500001
    region_weights = {"West": 0.34, "Central": 0.30, "East": 0.36}

    for day_index in range(181):
        current_date = start + timedelta(days=day_index)
        seasonal_multiplier = 1.0 + 0.18 * math.sin(day_index / 181 * math.pi)
        daily_orders = max(14, int(random.gauss(36 * seasonal_multiplier, 8)))

        for _ in range(daily_orders):
            region = random.choices(list(REGIONS), weights=[region_weights[r] for r in REGIONS])[0]
            warehouse = random.choice(REGIONS[region])
            product = random.choice(products)
            quantity = random.choices([1, 2, 3, 4], weights=[0.58, 0.25, 0.12, 0.05])[0]
            discount = random.choice([0, 0, 0, 0.05, 0.10, 0.15])
            revenue = product["unit_price"] * quantity * (1 - discount)
            cost = product["unit_cost"] * quantity
            order_status = random.choices(["Completed", "Completed", "Completed", "Returned", "Cancelled"], [0.72, 0.12, 0.08, 0.06, 0.02])[0]

            rows.append(
                {
                    "order_id": f"ORD-{order_id}",
                    "order_date": current_date.isoformat(),
                    "region": region,
                    "warehouse": warehouse,
                    "customer_segment": random.choice(["Consumer", "Small Business", "Enterprise"]),
                    "sku_id": product["sku_id"],
                    "category": product["category"],
                    "product_name": product["product_name"],
                    "quantity": quantity,
                    "unit_price": product["unit_price"],
                    "unit_cost": product["unit_cost"],
                    "discount_rate": discount,
                    "revenue": money(revenue),
                    "gross_profit": money(revenue - cost),
                    "order_status": order_status,
                }
            )
            order_id += 1
    return rows


def generate_shipments(orders: list[dict]) -> list[dict]:
    rows = []
    for order in orders:
        order_date = date.fromisoformat(order["order_date"])
        region_delay = {"West": 0.15, "Central": 0.10, "East": 0.18}[order["region"]]
        warehouse_penalty = 0.12 if order["warehouse"] in {"Miami DC", "Los Angeles DC"} else 0.0
        late_probability = min(0.45, 0.11 + region_delay + warehouse_penalty)
        processing_days = random.choices([0, 1, 2, 3], weights=[0.22, 0.48, 0.22, 0.08])[0]
        transit_days = random.choices([1, 2, 3, 4, 5], weights=[0.20, 0.36, 0.25, 0.13, 0.06])[0]
        if random.random() < late_probability:
            transit_days += random.choice([1, 2, 3])
        ship_date = order_date + timedelta(days=processing_days)
        delivery_date = ship_date + timedelta(days=transit_days)
        promised_date = order_date + timedelta(days=4)
        on_time = delivery_date <= promised_date

        rows.append(
            {
                "shipment_id": order["order_id"].replace("ORD", "SHP"),
                "order_id": order["order_id"],
                "carrier": random.choice(CARRIERS),
                "ship_date": ship_date.isoformat(),
                "promised_date": promised_date.isoformat(),
                "delivery_date": delivery_date.isoformat(),
                "fulfillment_days": (delivery_date - order_date).days,
                "on_time_flag": int(on_time),
                "late_days": max(0, (delivery_date - promised_date).days),
                "shipment_cost": money(7.5 + 1.2 * int(order["quantity"]) + random.uniform(0, 4)),
            }
        )
    return rows


def generate_inventory(products: list[dict], orders: list[dict]) -> list[dict]:
    rows = []
    recent_orders = [row for row in orders if row["order_date"] >= "2026-05-01"]
    demand_by_warehouse_sku: dict[tuple[str, str], int] = {}
    for order in recent_orders:
        key = (order["warehouse"], order["sku_id"])
        demand_by_warehouse_sku[key] = demand_by_warehouse_sku.get(key, 0) + int(order["quantity"])

    for region, warehouses in REGIONS.items():
        for warehouse in warehouses:
            for product in products:
                monthly_demand = demand_by_warehouse_sku.get((warehouse, product["sku_id"]), random.randint(8, 35))
                on_hand = max(4, int(monthly_demand * random.uniform(0.35, 2.4)))
                reorder_point = max(8, int(monthly_demand * 0.65))
                rows.append(
                    {
                        "snapshot_date": "2026-06-30",
                        "region": region,
                        "warehouse": warehouse,
                        "sku_id": product["sku_id"],
                        "category": product["category"],
                        "product_name": product["product_name"],
                        "on_hand_units": on_hand,
                        "reorder_point": reorder_point,
                        "monthly_demand_units": monthly_demand,
                        "inventory_value": money(on_hand * product["unit_cost"]),
                    }
                )
    return rows


def generate_returns(orders: list[dict], shipments: list[dict]) -> list[dict]:
    shipment_lookup = {shipment["order_id"]: shipment for shipment in shipments}
    rows = []
    return_id = 900001

    for order in orders:
        shipment = shipment_lookup[order["order_id"]]
        late = int(shipment["late_days"]) > 0
        base_return_probability = 0.035 + (0.035 if late else 0) + (0.025 if order["category"] == "Apparel" else 0)
        if order["order_status"] == "Returned" or random.random() < base_return_probability:
            return_date = date.fromisoformat(shipment["delivery_date"]) + timedelta(days=random.randint(2, 21))
            rows.append(
                {
                    "return_id": f"RET-{return_id}",
                    "order_id": order["order_id"],
                    "return_date": return_date.isoformat(),
                    "return_reason": random.choice(RETURN_REASONS),
                    "refund_amount": money(float(order["revenue"]) * random.uniform(0.65, 1.0)),
                    "restockable_flag": random.choice([1, 1, 1, 0]),
                }
            )
            return_id += 1
    return rows


def generate_targets() -> list[dict]:
    rows = []
    for region, warehouses in REGIONS.items():
        for warehouse in warehouses:
            base_sla = 0.88 if warehouse not in {"Miami DC", "Los Angeles DC"} else 0.84
            rows.append(
                {
                    "region": region,
                    "warehouse": warehouse,
                    "target_on_time_rate": round(base_sla, 3),
                    "target_fill_rate": 0.940,
                    "target_return_rate": 0.075,
                    "target_gross_margin": 0.380,
                }
            )
    return rows


def main() -> None:
    random.seed(720)
    products = build_products()
    orders = generate_orders(products)
    shipments = generate_shipments(orders)
    inventory = generate_inventory(products, orders)
    returns = generate_returns(orders, shipments)
    targets = generate_targets()

    write_csv(DATA_DIR / "orders.csv", orders)
    write_csv(DATA_DIR / "shipments.csv", shipments)
    write_csv(DATA_DIR / "inventory.csv", inventory)
    write_csv(DATA_DIR / "returns.csv", returns)
    write_csv(DATA_DIR / "warehouse_targets.csv", targets)

    print(f"orders={len(orders)} shipments={len(shipments)} inventory={len(inventory)} returns={len(returns)} targets={len(targets)}")


if __name__ == "__main__":
    main()
