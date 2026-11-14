"""Store-day P&L model for Indian quick commerce (Blinkit vs Swiggy Instamart).

Core identity (per dark store, per day):

    EBITDA per store-day = orders per store-day x contribution per order
                           - overhead per store-day

where overhead = everything between Contribution and Adjusted EBITDA
(brand marketing, corporate costs, rent and other fixed costs).

Break-even throughput (orders per store per day at which Adjusted EBITDA = 0):

    BE = overhead per store-day / contribution per order

All inputs come from the companies' quarterly shareholder letters (see data/).
Run:  python -m model.model      -> writes outputs/*.csv and outputs/results.json
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
CR = 1e7   # 1 crore = 10 million rupees
MN = 1e6


def load_blinkit() -> pd.DataFrame:
    d = pd.read_csv(DATA / "blinkit_quarterly.csv")
    d["company"] = "Blinkit"
    d["aov_inr"] = d["naov_inr"]                                   # net AOV (after discounts)
    d["orders_per_store_day"] = d["nov_per_store_day_inr_k"] * 1000 / d["naov_inr"]
    d["contribution_cr_calc"] = d["contribution_cr"]
    return d


def load_instamart() -> pd.DataFrame:
    d = pd.read_csv(DATA / "instamart_quarterly.csv")
    d["company"] = "Instamart"
    d["gov_cr"] = d["orders_mn"] * d["aov_inr"] / 10                # orders (mn) x AOV (INR) -> INR crore
    d["contribution_cr_calc"] = d["contribution_pct_gov"] / 100 * d["gov_cr"]
    return d


def store_day_pnl(d: pd.DataFrame) -> pd.DataFrame:
    """Turn reported quarterly totals into per-order and per-store-day economics."""
    d = d.copy()
    d["store_days"] = d["orders_mn"] * MN / d["orders_per_store_day"]
    d["contribution_per_order"] = d["contribution_cr_calc"] * CR / (d["orders_mn"] * MN)
    d["ebitda_per_order"] = d["adj_ebitda_cr"] * CR / (d["orders_mn"] * MN)
    d["overhead_per_store_day"] = (d["contribution_cr_calc"] - d["adj_ebitda_cr"]) * CR / d["store_days"]
    d["ebitda_per_store_day"] = d["adj_ebitda_cr"] * CR / d["store_days"]
    # Break-even throughput only exists when each order makes a positive contribution.
    d["breakeven_orders_per_store_day"] = d.apply(
        lambda r: r.overhead_per_store_day / r.contribution_per_order if r.contribution_per_order > 0 else float("nan"),
        axis=1,
    )
    d["required_contribution_per_order"] = d["overhead_per_store_day"] / d["orders_per_store_day"]
    d["gap_per_order"] = d["required_contribution_per_order"] - d["contribution_per_order"]
    d["gap_pct_of_aov"] = 100 * d["gap_per_order"] / d["aov_inr"]
    return d


def required_contribution(overhead_psd: float, throughputs: list[float]) -> list[dict]:
    """Contribution per order needed for EBITDA break-even at each throughput."""
    return [{"orders_per_store_day": t, "required_contribution_per_order": overhead_psd / t} for t in throughputs]


def instamart_levers(r: pd.Series, target_throughput: float, overhead_cut: float) -> dict:
    """Split Instamart's per-order gap into three levers applied in sequence.

    1. Throughput: lift orders per store-day to target (fixed overhead spread over more orders).
    2. Overhead: cut overhead per store-day by `overhead_cut` (operating leverage, rent, marketing).
    3. Contribution margin: whatever gap remains must come from better per-order economics
       (take rate, ad income, 1P margins, lower discounts and delivery cost).
    """
    c0, o0, t0, aov = r.contribution_per_order, r.overhead_per_store_day, r.orders_per_store_day, r.aov_inr
    need0 = o0 / t0
    need1 = o0 / target_throughput
    need2 = o0 * (1 - overhead_cut) / target_throughput
    return {
        "start_gap_per_order": need0 - c0,
        "lever1_throughput_per_order": need0 - need1,
        "lever2_overhead_per_order": need1 - need2,
        "lever3_contribution_per_order": need2 - c0,
        "lever3_contribution_pct_of_aov": 100 * (need2 - c0) / aov,
        "target_contribution_per_order": need2,
        "target_contribution_pct_of_aov": 100 * need2 / aov,
        "assumptions": {"target_throughput": target_throughput, "overhead_cut": overhead_cut},
    }


def margin_target(r: pd.Series, ebitda_margin: float, throughputs: list[float]) -> list[dict]:
    """Contribution per order needed to reach an Adjusted EBITDA margin (as % of AOV) at each throughput.

    margin = (t*c - O) / (t*AOV)  =>  c = O/t + margin*AOV
    """
    return [
        {"orders_per_store_day": t,
         "required_contribution_per_order": r.overhead_per_store_day / t + ebitda_margin * r.aov_inr}
        for t in throughputs
    ]


def sensitivity(r: pd.Series, shock: float = 0.10) -> list[dict]:
    """Break-even throughput when each driver moves by +/- shock (one at a time)."""
    base = r.overhead_per_store_day / r.contribution_per_order
    rows = []
    for name, f in [
        ("Contribution per order", lambda c, o, s: o / (c * (1 + s))),
        ("Overhead per store-day", lambda c, o, s: o * (1 + s) / c),
    ]:
        lo = f(r.contribution_per_order, r.overhead_per_store_day, -shock)
        hi = f(r.contribution_per_order, r.overhead_per_store_day, shock)
        rows.append({"driver": name, "minus_10pct": lo, "plus_10pct": hi, "base": base})
    return rows


def run() -> dict:
    OUT.mkdir(exist_ok=True)
    b = store_day_pnl(load_blinkit())
    i = store_day_pnl(load_instamart())
    cols = ["company", "quarter", "orders_mn", "aov_inr", "orders_per_store_day", "store_days",
            "contribution_per_order", "ebitda_per_order", "overhead_per_store_day", "ebitda_per_store_day",
            "breakeven_orders_per_store_day", "required_contribution_per_order", "gap_per_order", "gap_pct_of_aov"]
    panel = pd.concat([b[cols], i[cols]], ignore_index=True)
    panel.round(2).to_csv(OUT / "store_day_pnl.csv", index=False)

    bl, im = b.iloc[-1], i.iloc[-1]
    first_positive = b.loc[b["adj_ebitda_cr"] > 0, "quarter"].iloc[0]
    results = {
        "latest_quarter": bl.quarter,
        "blinkit": {
            "orders_per_store_day": round(bl.orders_per_store_day),
            "contribution_per_order": round(bl.contribution_per_order, 1),
            "overhead_per_store_day": round(bl.overhead_per_store_day),
            "breakeven_orders_per_store_day": round(bl.breakeven_orders_per_store_day),
            "margin_of_safety_pct": round(100 * (bl.orders_per_store_day / bl.breakeven_orders_per_store_day - 1), 1),
            "first_ebitda_positive_quarter": first_positive,
            "contribution_needed_for_5pct_margin": [
                {k: round(v, 1) for k, v in x.items()}
                for x in margin_target(bl, 0.05, [1718, 2000, 2500])
            ],
            "sensitivity": [{k: (round(v) if isinstance(v, float) else v) for k, v in x.items()} for x in sensitivity(bl)],
        },
        "instamart": {
            "orders_per_store_day": round(im.orders_per_store_day),
            "contribution_per_order": round(im.contribution_per_order, 1),
            "overhead_per_store_day": round(im.overhead_per_store_day),
            "gap_per_order": round(im.gap_per_order, 1),
            "gap_pct_of_aov": round(im.gap_pct_of_aov, 1),
            "required_contribution_by_throughput": [
                {k: round(v, 1) for k, v in x.items()}
                for x in required_contribution(im.overhead_per_store_day, [1192, 1400, 1718, 2000, 2500])
            ],
            "levers": {k: (round(v, 1) if isinstance(v, float) else v)
                       for k, v in instamart_levers(im, target_throughput=bl.orders_per_store_day, overhead_cut=0.20).items()},
        },
        "reported_data_points": int(sum(
            pd.read_csv(DATA / f).drop(columns=["quarter", "source"]).size
            for f in ("blinkit_quarterly.csv", "instamart_quarterly.csv"))),
    }
    (OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    return results


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
