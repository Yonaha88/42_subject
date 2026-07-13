#!/usr/bin/env python3

import sys


def main() -> None:
    print("=== Inventory System Analysis ===")
    inventory: dict[str, int] = {}

    for param in sys.argv[1:]:
        if ":" not in param:
            print(f"Error - invalid parameter '{param}'")
            continue
        name, qty_str = param.split(":", 1)
        if name in inventory:
            print(f"Redundant item '{name}' - discarding")
            continue
        try:
            qty = int(qty_str)
        except ValueError as e:
            print(f"Quantity error for '{name}': {e}")
            continue
        inventory[name] = qty

    if not inventory:
        return

    items = list(inventory.keys())
    total = sum(inventory.values())
    print(f"Got inventory: {inventory}")
    print(f"Item list: {items}")
    print(f"Total quantity of the {len(items)} items: {total}")

    for item in inventory.keys():
        pct = round(inventory[item] / total * 100, 1)
        print(f"Item {item} represents {pct}%")

    most_item = items[0]
    least_item = items[0]
    for item in items[1:]:
        if inventory[item] > inventory[most_item]:
            most_item = item
        if inventory[item] < inventory[least_item]:
            least_item = item

    qty = inventory[most_item]
    print(f"Item most abundant: {most_item} with quantity {qty}")
    qty = inventory[least_item]
    print(f"Item least abundant: {least_item} with quantity {qty}")

    inventory.update({"magic_item": 1})
    print(f"Updated inventory: {inventory}")


if __name__ == "__main__":
    main()
