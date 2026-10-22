import gift_calc

# Official example from docs: 3 gifts, green backdrop x2, black x1, row [60,180,450]
def test_official_example():
    inputs = [
        gift_calc.CraftInputGift("g1", 1, 100, [{"type":"backdrop","id":"green"}]),
        gift_calc.CraftInputGift("g2", 1, 100, [{"type":"backdrop","id":"green"}]),
        gift_calc.CraftInputGift("g3", 1, 100, [{"type":"backdrop","id":"black"}]),
    ]
    cfg = [[100],[100,200],[60,180,450],[100,200,300,400]]  # row index 2 = 3 gifts
    probs = gift_calc.compute_attribute_persistence(inputs, cfg)
    assert probs["backdrop"]["green"] == 180/1000.0
    assert probs["backdrop"]["black"] == 60/1000.0

def test_craft_success_sum():
    inputs = [
        gift_calc.CraftInputGift("g1", 1, 300, []),
        gift_calc.CraftInputGift("g2", 1, 400, []),
    ]
    r = gift_calc.compute_craft_success(inputs)
    assert r.total_permille == 700
    assert r.success_probability == 0.7
    # UI: (700+5)//10 = 70
    assert r.ui_percentage == 70

def test_ui_round_up():
    # sum=701 => (701+5)//10 = 70 (706//10=70) actually 70.6->70? docs: round up by adding 5 then /10 (integer). 701+5=706//10=70. ok
    inputs = [gift_calc.CraftInputGift("g1",1,701,[])]
    r = gift_calc.compute_craft_success(inputs)
    assert r.ui_percentage == 70  # (701+5)//10=70

def test_edge_one_gift():
    inputs = [gift_calc.CraftInputGift("g1",1,500,[{"type":"pattern","id":42}])]
    r = gift_calc.compute_craft_success(inputs)
    assert r.total_permille == 500
    assert r.success_probability == 0.5

def test_edge_four_gifts():
    inputs = [gift_calc.CraftInputGift(f"g{i}",1,250,[]) for i in range(4)]
    r = gift_calc.compute_craft_success(inputs)
    assert r.total_permille == 1000
    assert r.success_probability == 1.0

def test_invalid_count():
    try:
        gift_calc.compute_craft_success([])
        assert False, "should raise"
    except ValueError:
        pass
    try:
        gift_calc.compute_craft_success([gift_calc.CraftInputGift(f"g{i}",1,100,[]) for i in range(5)])
        assert False, "should raise"
    except ValueError:
        pass

def test_different_base_ids():
    try:
        gift_calc.compute_craft_success([
            gift_calc.CraftInputGift("g1",1,100,[]),
            gift_calc.CraftInputGift("g2",2,100,[]),
        ])
        assert False, "should raise"
    except ValueError:
        pass

def test_attr_persistence_one_gift():
    inputs = [gift_calc.CraftInputGift("g1",1,100,[{"type":"pattern","id":7}])]
    cfg = [[999]]
    probs = gift_calc.compute_attribute_persistence(inputs, cfg)
    assert probs["pattern"][7] == 999/1000.0

def test_attr_persistence_row_length_mismatch():
    inputs = [gift_calc.CraftInputGift("g1",1,100,[{"type":"pattern","id":7}])]
    try:
        gift_calc.compute_attribute_persistence(inputs, [[1,2]])
        assert False, "should raise"
    except ValueError:
        pass

def test_expected_distribution_structure():
    inputs = [gift_calc.CraftInputGift("g1",1,200,[{"type":"backdrop","id":"red"}])]
    cfg = [[500]]
    out = gift_calc.expected_craft_outcome_distribution(inputs, cfg)
    assert out["success_probability"] == 0.2
    assert out["inputs_burned_on_attempt"] is True
    assert "limitations" in out

def test_invalid_permille_range():
    try:
        gift_calc.compute_craft_success([gift_calc.CraftInputGift("g1",1,-1,[])])
        assert False
    except ValueError:
        pass
    try:
        gift_calc.compute_craft_success([gift_calc.CraftInputGift("g1",1,1001,[])])
        assert False
    except ValueError:
        pass

def test_config_missing_row():
    inputs = [gift_calc.CraftInputGift("g1",1,100,[{"type":"pattern","id":7}])]
    try:
        gift_calc.compute_attribute_persistence(inputs, [])
        assert False
    except ValueError:
        pass

def test_no_attributes_empty_persistence():
    inputs = [gift_calc.CraftInputGift("g1",1,100,[])]
    cfg = [[500]]
    probs = gift_calc.compute_attribute_persistence(inputs, cfg)
    assert probs["pattern"] == {}
    assert probs["backdrop"] == {}

def test_success_probability_clamped():
    inputs = [gift_calc.CraftInputGift(f"g{i}",1,1000,[]) for i in range(4)]
    r = gift_calc.compute_craft_success(inputs)
    assert r.success_probability == 1.0
    assert r.ui_percentage == 100

def test_app_calc_endpoint():
    # smoke test via app module
    import app
    # build a fake handler? Instead test parse_scenario directly
    sc = {"base_gift_id": 1, "inputs": [{"permille": 250, "patterns": ["42","42"], "backdrops": []}], "config": [[500]]}
    out = app.parse_scenario(sc)
    assert out["ok"] if "ok" in out else True
    assert out["success_probability"] == 0.25

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
def test_fee_impact_profitable():
    r = gift_calc.compute_fee_impact(100, 120, buy_fee_pct=5, sell_fee_pct=5, gas=1)
    assert r["profitable"] is True
    assert r["net_profit"] > 0

def test_fee_impact_loss():
    r = gift_calc.compute_fee_impact(100, 105, buy_fee_pct=10, sell_fee_pct=10, gas=2)
    assert r["profitable"] is False

def test_fee_impact_invalid():
    try:
        gift_calc.compute_fee_impact(0, 100)
        assert False
    except ValueError:
        pass

def test_market_stats():
    r = gift_calc.market_stats([10, 20, 30, 40])
    assert r["count"] == 4
    assert r["min"] == 10
    assert r["max"] == 40
    assert r["median"] == 25
    assert r["mean"] == 25.0

def test_market_stats_empty():
    try:
        gift_calc.market_stats([])
        assert False
    except ValueError:
        pass

def test_craft_success_validation_types():
    try:
        gift_calc.compute_craft_success("not a list")
        assert False
    except (ValueError, TypeError):
        pass
