"""Checks that the model reproduces reported figures and that the identities hold."""
import pandas as pd
import pytest

from model.model import instamart_levers, load_blinkit, load_instamart, store_day_pnl, run


@pytest.fixture(scope="module")
def blinkit():
    return store_day_pnl(load_blinkit())


@pytest.fixture(scope="module")
def instamart():
    return store_day_pnl(load_instamart())


def test_identity_reconstructs_reported_ebitda(blinkit, instamart):
    for d in (blinkit, instamart):
        rebuilt = d.orders_per_store_day * d.contribution_per_order - d.overhead_per_store_day
        assert (rebuilt - d.ebitda_per_store_day).abs().max() < 1e-6


def test_derived_gov_matches_reported_instamart_gov(instamart):
    # Swiggy reported Instamart GOV of INR 7,022 Cr (Q2FY26) and 9,230 Cr (Q2FY27).
    gov = dict(zip(instamart.quarter, load_instamart().gov_cr))
    assert gov["Q2FY26"] == pytest.approx(7022, rel=0.005)
    assert gov["Q2FY27"] == pytest.approx(9230, rel=0.005)


def test_blinkit_breakeven_consistent_with_first_profitable_quarter(blinkit):
    # Below break-even while EBITDA < 0, above it once EBITDA > 0.
    for _, r in blinkit.iterrows():
        if r.adj_ebitda_cr < 0:
            assert r.orders_per_store_day < r.breakeven_orders_per_store_day
        elif r.adj_ebitda_cr > 0:
            assert r.orders_per_store_day > r.breakeven_orders_per_store_day


def test_instamart_has_no_breakeven_while_contribution_negative(instamart):
    neg = instamart[instamart.contribution_per_order < 0]
    assert neg.breakeven_orders_per_store_day.isna().all()


def test_levers_add_up_to_gap(instamart):
    lv = instamart_levers(instamart.iloc[-1], target_throughput=1718, overhead_cut=0.2)
    total = lv["lever1_throughput_per_order"] + lv["lever2_overhead_per_order"] + lv["lever3_contribution_per_order"]
    assert total == pytest.approx(lv["start_gap_per_order"])


def test_run_writes_outputs():
    res = run()
    assert res["reported_data_points"] == 180
    assert res["blinkit"]["first_ebitda_positive_quarter"] == "Q3FY26"
