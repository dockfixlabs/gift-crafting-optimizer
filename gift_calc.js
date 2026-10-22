// Gift Crafting Optimizer - client-side calculation (mirrors gift_calc.py)
// No external dependencies.

function _validateInputs(inputs) {
  if (!Array.isArray(inputs) || inputs.length < 1 || inputs.length > 4) {
    throw new Error("Crafting requires 1 to 4 gifts");
  }
  const baseIds = new Set(inputs.map(g => g.base_gift_id));
  if (baseIds.size !== 1) throw new Error("All inputs must share the same base gift_id");
  for (const g of inputs) {
    if (typeof g.craft_chance_permille !== "number" || !Number.isInteger(g.craft_chance_permille)) {
      throw new Error("craft_chance_permille must be an integer");
    }
    if (g.craft_chance_permille < 0 || g.craft_chance_permille > 1000) {
      throw new Error("craft_chance_permille must be 0..1000");
    }
  }
}

function computeCraftSuccess(inputs) {
  _validateInputs(inputs);
  const totalRaw = inputs.reduce((s, g) => s + g.craft_chance_permille, 0);
  const totalPermille = Math.max(0, Math.min(totalRaw, 4000));
  const successProb = Math.min(totalPermille / 1000.0, 1.0);
  const uiPct = Math.min(Math.floor((totalPermille + 5) / 10), 100);

  const groups = { pattern: {}, backdrop: {} };
  for (const g of inputs) {
    for (const attr of (g.attributes || [])) {
      const t = attr.type;
      const key = attr.id;
      if (groups[t]) groups[t][key] = (groups[t][key] || 0) + 1;
    }
  }
  return { totalPermille, successProb, uiPct, groups };
}

function computeAttributePersistence(inputs, config) {
  _validateInputs(inputs);
  const k = inputs.length;
  if (!Array.isArray(config) || config.length < k) {
    throw new Error("craft_attr_permilles missing row for count " + k);
  }
  const row = config[k - 1];
  if (!Array.isArray(row) || row.length !== k) {
    throw new Error("Row " + (k - 1) + " must have " + k + " entries");
  }
  for (const v of row) {
    if (typeof v !== "number" || !Number.isInteger(v) || v < 0 || v > 1000) {
      throw new Error("permille values must be integers 0..1000");
    }
  }

  const groups = { pattern: {}, backdrop: {} };
  for (const g of inputs) {
    for (const attr of (g.attributes || [])) {
      const t = attr.type;
      const key = attr.id;
      if (groups[t]) groups[t][key] = (groups[t][key] || 0) + 1;
    }
  }
  const result = { pattern: {}, backdrop: {} };
  for (const t of ["pattern", "backdrop"]) {
    for (const key of Object.keys(groups[t])) {
      const count = groups[t][key];
      if (count >= 1 && count <= k) {
        result[t][key] = row[count - 1] / 1000.0;
      }
    }
  }
  return result;
}

function expectedDistribution(inputs, config) {
  const succ = computeCraftSuccess(inputs);
  const attr = computeAttributePersistence(inputs, config);
  return {
    inputs_count: inputs.length,
    total_permille: succ.totalPermille,
    success_probability: succ.successProb,
    ui_percentage: succ.uiPct,
    attribute_persistence: attr,
    attribute_groups: succ.groups,
    inputs_burned_on_attempt: true,
    limitations: [
      "Outcome attribute selection on success is random among candidates; exact result not predictable.",
      "Future market value is not estimated.",
      "config values (stargifts_craft_attribute_permilles) are user-provided; not verified against live Telegram client."
    ]
  };
}

function computeFeeImpact(buyPrice, sellPrice, buyFeePct, sellFeePct, gas) {
  buyFeePct = buyFeePct || 0;
  sellFeePct = sellFeePct || 0;
  gas = gas || 0;
  if (typeof buyPrice !== "number" || buyPrice <= 0) throw new Error("buy_price must be > 0");
  const buyCost = buyPrice * (1 + buyFeePct / 100.0);
  const sellNet = sellPrice * (1 - sellFeePct / 100.0) - gas;
  const netProfit = sellNet - buyCost;
  const roiPct = (netProfit / buyCost) * 100.0;
  return {
    buy_cost: Math.round(buyCost * 10000) / 10000,
    sell_net: Math.round(sellNet * 10000) / 10000,
    net_profit: Math.round(netProfit * 10000) / 10000,
    roi_percent: Math.round(roiPct * 100) / 100,
    profitable: netProfit > 0
  };
}

function marketStats(prices) {
  if (!Array.isArray(prices) || prices.length === 0) throw new Error("prices must be non-empty");
  const vals = [...prices].sort((a, b) => a - b);
  const sum = vals.reduce((s, v) => s + v, 0);
  const mid = Math.floor(vals.length / 2);
  const med = vals.length % 2 === 0 ? (vals[mid - 1] + vals[mid]) / 2 : vals[mid];
  return {
    count: vals.length,
    min: vals[0],
    max: vals[vals.length - 1],
    median: med,
    mean: Math.round((sum / vals.length) * 100) / 100
  };
}
