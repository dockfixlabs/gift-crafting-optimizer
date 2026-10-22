"""Gift Crafting Optimizer — independent calculation module.

Implements Telegram documented crafting probability rules.
No claims about market value or guaranteed outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import median
from typing import Any, Dict, List


@dataclass
class CraftInputGift:
    """One collectible gift used as crafting input."""
    unique_id: str
    base_gift_id: int
    craft_chance_permille: int  # 0..1000
    attributes: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class CraftResult:
    total_permille: int
    success_probability: float
    ui_percentage: int
    attribute_groups: Dict[str, Dict[Any, int]]
    attribute_probabilities: Dict[str, Dict[Any, float]]
    inputs_burned: bool = True


def _validate_inputs(inputs: List[CraftInputGift]) -> None:
    if not isinstance(inputs, list) or not (1 <= len(inputs) <= 4):
        raise ValueError("Crafting requires 1 to 4 gifts")
    base_ids = {g.base_gift_id for g in inputs}
    if len(base_ids) != 1:
        raise ValueError("All inputs must share the same base gift_id")
    for g in inputs:
        if not isinstance(g.craft_chance_permille, int):
            raise ValueError("craft_chance_permille must be an integer")
        if not (0 <= g.craft_chance_permille <= 1000):
            raise ValueError("craft_chance_permille must be 0..1000")


def compute_craft_success(inputs: List[CraftInputGift]) -> CraftResult:
    """Compute crafting success probability from documented rules.

    Rules (core.telegram.org/api/gifts):
    - 1 to 4 gifts of the same base type.
    - success rate = sum(craft_chance_permille) permille.
    - UI percentage = floor((sum + 5) / 10), clamped to 0..100.
    - All inputs are burned regardless of outcome (except invalid inputs).
    """
    _validate_inputs(inputs)
    total_raw = sum(g.craft_chance_permille for g in inputs)
    total_permille = max(0, min(total_raw, 4000))
    success_prob = min(total_permille / 1000.0, 1.0)
    ui_pct = min((total_permille + 5) // 10, 100)

    groups: Dict[str, Dict[Any, int]] = {"pattern": {}, "backdrop": {}}
    for g in inputs:
        for attr in g.attributes:
            t = attr.get("type")
            key = attr.get("id")
            if t in groups:
                groups[t][key] = groups[t].get(key, 0) + 1

    return CraftResult(
        total_permille=total_permille,
        success_probability=success_prob,
        ui_percentage=ui_pct,
        attribute_groups=groups,
        attribute_probabilities={},
    )


def compute_attribute_persistence(
    inputs: List[CraftInputGift],
    craft_attr_permilles: List[List[int]],
) -> Dict[str, Dict[Any, float]]:
    """Compute per-attribute persistence probability.

    craft_attr_permilles: stargifts_craft_attribute_permilles from client config.
    Array of 4 rows; row N (0-indexed) has N+1 integers (permille).
    For k inputs, use row k-1. For a group of size m, probability = row[m-1]/1000.
    """
    _validate_inputs(inputs)
    k = len(inputs)
    if not isinstance(craft_attr_permilles, list) or len(craft_attr_permilles) < k:
        raise ValueError("craft_attr_permilles missing row for count %d" % k)
    row = craft_attr_permilles[k - 1]
    if not isinstance(row, list) or len(row) != k:
        raise ValueError("Row %d must have %d entries, got %d" % (k - 1, k, len(row) if isinstance(row, list) else -1))
    for v in row:
        if not isinstance(v, int) or v < 0 or v > 1000:
            raise ValueError("permille values must be integers 0..1000")

    groups: Dict[str, Dict[Any, int]] = {"pattern": {}, "backdrop": {}}
    for g in inputs:
        for attr in g.attributes:
            t = attr.get("type")
            key = attr.get("id")
            if t in groups:
                groups[t][key] = groups[t].get(key, 0) + 1

    result: Dict[str, Dict[Any, float]] = {"pattern": {}, "backdrop": {}}
    for t in ("pattern", "backdrop"):
        for key, count in groups[t].items():
            if 1 <= count <= k:
                result[t][key] = row[count - 1] / 1000.0
    return result


def expected_craft_outcome_distribution(
    inputs: List[CraftInputGift],
    craft_attr_permilles: List[List[int]],
) -> Dict[str, Any]:
    """Return a structured summary of what can be computed.

    Does NOT predict which specific attribute is chosen on success,
    nor future market value.
    """
    success = compute_craft_success(inputs)
    attr_probs = compute_attribute_persistence(inputs, craft_attr_permilles)
    return {
        "inputs_count": len(inputs),
        "base_gift_id": inputs[0].base_gift_id if inputs else None,
        "total_craft_chance_permille": success.total_permille,
        "success_probability": success.success_probability,
        "ui_percentage": success.ui_percentage,
        "attribute_persistence": attr_probs,
        "attribute_groups": success.attribute_groups,
        "inputs_burned_on_attempt": True,
        "limitations": [
            "Outcome attribute selection on success is random among candidates; exact result not predictable.",
            "Future market value is not estimated.",
            "craft_attr_permilles must be sourced from client config (stargifts_craft_attribute_permilles); not verified here.",
        ],
    }


def compute_fee_impact(
    buy_price: float,
    sell_price: float,
    buy_fee_pct: float = 0.0,
    sell_fee_pct: float = 0.0,
    gas: float = 0.0,
) -> Dict[str, float]:
    """Compute net profit/loss after fees for a buy→sell round trip.

    All prices in the same currency unit. Fees are percentages (0..100).
    Returns net profit (can be negative) and ROI percentage.
    """
    if buy_price <= 0:
        raise ValueError("buy_price must be > 0")
    buy_cost = buy_price * (1 + buy_fee_pct / 100.0)
    sell_net = sell_price * (1 - sell_fee_pct / 100.0) - gas
    net_profit = sell_net - buy_cost
    roi_pct = (net_profit / buy_cost) * 100.0
    return {
        "buy_cost": round(buy_cost, 4),
        "sell_net": round(sell_net, 4),
        "net_profit": round(net_profit, 4),
        "roi_percent": round(roi_pct, 2),
        "profitable": net_profit > 0,
    }


def market_stats(prices: List[float]) -> Dict[str, Any]:
    """Compute basic statistics for a price sample."""
    if not prices:
        raise ValueError("prices must be non-empty")
    vals = sorted(prices)
    return {
        "count": len(vals),
        "min": vals[0],
        "max": vals[-1],
        "median": median(vals),
        "mean": round(sum(vals) / len(vals), 2),
    }
