"""Validate Tableau project CSVs."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def read_csv(name: str) -> list[dict]:
    with (DATA_DIR / name).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def assert_unique(rows: list[dict], key: str, table: str) -> None:
    values = [row[key] for row in rows]
    duplicates = len(values) - len(set(values))
    if duplicates:
        raise AssertionError(f"{table}.{key} has {duplicates} duplicate values")


def main() -> None:
    orders = read_csv("orders.csv")
    shipments = read_csv("shipments.csv")
    inventory = read_csv("inventory.csv")
    returns = read_csv("returns.csv")
    targets = read_csv("warehouse_targets.csv")

    assert_unique(orders, "order_id", "orders")
    assert_unique(shipments, "shipment_id", "shipments")
    assert_unique(returns, "return_id", "returns")

    order_ids = {row["order_id"] for row in orders}
    shipment_order_ids = {row["order_id"] for row in shipments}
    return_order_ids = {row["order_id"] for row in returns}
    target_warehouses = {row["warehouse"] for row in targets}
    inventory_warehouses = {row["warehouse"] for row in inventory}

    if shipment_order_ids != order_ids:
        raise AssertionError("shipments must have exactly one row per order")
    if not return_order_ids.issubset(order_ids):
        raise AssertionError("returns contains order_id values missing from orders")
    if not inventory_warehouses.issubset(target_warehouses):
        raise AssertionError("inventory contains warehouse values missing from targets")

    for row in orders:
        if float(row["revenue"]) < 0 or float(row["gross_profit"]) < 0:
            raise AssertionError("orders revenue and gross_profit must be non-negative")

    for row in shipments:
        if int(row["fulfillment_days"]) < 0 or int(row["late_days"]) < 0:
            raise AssertionError("shipment day metrics must be non-negative")
        if row["on_time_flag"] not in {"0", "1"}:
            raise AssertionError("on_time_flag must be binary")

    for row in inventory:
        if int(row["on_hand_units"]) < 0 or int(row["monthly_demand_units"]) <= 0:
            raise AssertionError("inventory quantities must be valid")

    print("Data validation passed.")
    print(f"orders={len(orders)} shipments={len(shipments)} inventory={len(inventory)} returns={len(returns)} targets={len(targets)}")


if __name__ == "__main__":
    main()
