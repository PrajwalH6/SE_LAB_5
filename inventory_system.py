"""
Inventory management utilities: add, remove, persist, and report stock levels.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Configure module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handlers can be configured by the application; add a basic one as fallback
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    logger.addHandler(_handler)

# Global in-memory stock store
stock_data: Dict[str, float] = {}


def add_item(
    item: str = "default",
    qty: float = 0,
    logs: Optional[List[str]] = None,
) -> None:
    """
    Add quantity to an item in stock. Creates the item if it doesn't exist.

    Args:
        item: The item name (must be a non-empty string).
        qty: Quantity to add (numeric). Negative values are rejected.
        logs: Optional list to append human-readable log entries.

    Raises:
        ValueError: If item is empty/not str or qty is not a number
        or qty < 0.
    """
    if not isinstance(item, str) or not item.strip():
        raise ValueError("item must be a non-empty string")
    if not isinstance(qty, (int, float)):
        raise ValueError("qty must be numeric")
    if qty < 0:
        raise ValueError("qty must be non-negative")

    current = stock_data.get(item, 0.0)
    stock_data[item] = float(current) + float(qty)

    ts = datetime.now().isoformat()
    logger.info("%s: Added %s of %s", ts, qty, item)
    if logs is not None:
        logs.append(f"{ts}: Added {qty} of {item}")


def remove_item(item: str, qty: float) -> None:
    """
    Remove quantity from an item in stock. Deletes the item if it drops to 0.

    Args:
        item: The item name (str).
        qty: Quantity to remove (numeric, positive).

    Raises:
        ValueError: For invalid inputs or insufficient stock.
        KeyError: If the item does not exist.
    """
    if not isinstance(item, str) or not item.strip():
        raise ValueError("item must be a non-empty string")
    if not isinstance(qty, (int, float)) or qty <= 0:
        raise ValueError("qty must be a positive number")

    if item not in stock_data:
        raise KeyError(f"item '{item}' not found")

    new_qty = float(stock_data[item]) - float(qty)
    if new_qty < 0:
        raise ValueError(
            f"insufficient stock for '{item}': have {stock_data[item]}, "
            f"remove {qty}"
        )

    ts = datetime.now().isoformat()
    if new_qty == 0:
        del stock_data[item]
        logger.info(
            "%s: Removed %s of %s; item deleted at zero",
            ts,
            qty,
            item,
        )
    else:
        stock_data[item] = new_qty
        logger.info(
            "%s: Removed %s of %s; new qty %s",
            ts,
            qty,
            item,
            new_qty,
        )


def get_qty(item: str) -> float:
    """
    Get current quantity for an item.

    Args:
        item: Item name.

    Returns:
        Current quantity.

    Raises:
        KeyError: If item does not exist.
    """
    return float(stock_data[item])


def load_data(file: str = "inventory.json") -> None:
    """
    Load stock data from a JSON file into the global stock_data.

    The JSON must represent an object mapping strings to numbers.
    """
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("inventory file must contain a JSON object")

    # Validate and load in place to avoid reassigning the global
    stock_data.clear()
    for k, v in data.items():
        if not isinstance(k, str) or not isinstance(v, (int, float)):
            raise ValueError(
                "inventory must map strings to numeric quantities"
            )
        stock_data[k] = float(v)

    logger.info("Loaded %d items from %s", len(stock_data), file)


def save_data(file: str = "inventory.json") -> None:
    """
    Save current stock_data to a JSON file with UTF-8 encoding.
    """
    with open(file, "w", encoding="utf-8") as f:
        json.dump(stock_data, f, ensure_ascii=False, indent=2)
    logger.info("Saved %d items to %s", len(stock_data), file)


def print_data() -> None:
    """
    Print a simple report of all items and quantities.
    """
    print("Items Report")
    for name, qty in stock_data.items():
        print(f"{name} -> {qty}")


def check_low_items(threshold: float = 5) -> List[str]:
    """
    Return a list of items whose quantity is below the given threshold.

    Args:
        threshold: Numeric threshold (inclusive lower bound excluded).

    Returns:
        List of item names.
    """
    if not isinstance(threshold, (int, float)) or threshold < 0:
        raise ValueError("threshold must be a non-negative number")
    return [
        name
        for name, qty in stock_data.items()
        if qty < threshold
    ]


def main() -> None:
    """
    Demonstration routine; avoids insecure eval and invalid operations.
    """
    logs: List[str] = []
    add_item("apple", 10, logs)
    # The following would raise ValueError if uncommented:
    # add_item("banana", -2)
    # add_item(123, "ten")

    remove_item("apple", 3)
    if "apple" in stock_data:
        print(f"Apple stock: {get_qty('apple')}")
    print(f"Low items: {check_low_items()}")

    save_data()
    load_data()
    print_data()

    # Insecure eval removed.


if __name__ == "__main__":
    main()
