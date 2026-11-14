"""Charts for the deck and README (PNG for slides, SVG for the repo).

Run after the model:  python -m model.charts
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
FIG = OUT / "charts"

# Validated categorical slots (light mode) + neutral ink.
BLINKIT = "#2a78d6"
INSTAMART = "#eb6834"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8985"
GRID = "#e6e5e1"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "axes.titleweight": "bold", "axes.titlesize": 13, "axes.titlecolor": INK, "axes.titlelocation": "left",
    "figure.facecolor": "white", "savefig.facecolor": "white",
})


def save(fig, name: str) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(FIG / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)


def chart_breakeven(p: pd.DataFrame) -> None:
    b = p[p.company == "Blinkit"]
    x = np.arange(len(b))
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.plot(x, b.orders_per_store_day, color=BLINKIT, lw=2, marker="o", ms=8, label="Actual orders per store per day")
    ax.plot(x, b.breakeven_orders_per_store_day, color=MUTED, lw=2, ls="--", marker="o", ms=6,
            label="Break-even orders per store per day")
    ax.fill_between(x, b.orders_per_store_day, b.breakeven_orders_per_store_day,
                    where=b.orders_per_store_day >= b.breakeven_orders_per_store_day, color=BLINKIT, alpha=0.08)
    i3 = list(b.quarter).index("Q3FY26")
    ax.annotate("Q3FY26: lines cross,\nfirst profitable quarter", xy=(i3, b.orders_per_store_day.iloc[i3]),
                xytext=(i3 - 1.9, 1130), color=INK2, fontsize=10, arrowprops=dict(arrowstyle="-", color=MUTED))
    last = b.iloc[-1]
    ax.text(x[-1] + 0.15, last.orders_per_store_day, f"{last.orders_per_store_day:,.0f}", color=INK, va="center", fontsize=10)
    ax.text(x[-1] + 0.15, last.breakeven_orders_per_store_day, f"{last.breakeven_orders_per_store_day:,.0f}",
            color=INK2, va="center", fontsize=10)
    ax.set_xticks(x, b.quarter)
    ax.set_ylim(1000, 2400)
    ax.set_ylabel("Orders per dark store per day")
    ax.set_title("Blinkit got profitable by cutting its break-even, not by density alone")
    ax.legend(frameon=False, loc="upper left", fontsize=10)
    save(fig, "01_blinkit_breakeven")


def chart_isoprofit(p: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.8))
    t = np.linspace(800, 2600, 200)
    for comp, col in (("Blinkit", BLINKIT), ("Instamart", INSTAMART)):
        d = p[p.company == comp]
        o = d.overhead_per_store_day.iloc[-1]
        ax.plot(t, o / t, color=col, lw=1.5, ls="--", alpha=0.7)
        ax.plot(d.orders_per_store_day, d.contribution_per_order, color=col, lw=2, marker="o", ms=8, label=comp)
        off0, off1 = ((10, -14), (8, -4)) if comp == "Blinkit" else ((10, -12), (8, 6))
        ax.annotate(d.quarter.iloc[0], (d.orders_per_store_day.iloc[0], d.contribution_per_order.iloc[0]),
                    textcoords="offset points", xytext=off0, fontsize=9, color=INK2)
        ax.annotate(d.quarter.iloc[-1], (d.orders_per_store_day.iloc[-1], d.contribution_per_order.iloc[-1]),
                    textcoords="offset points", xytext=off1, fontsize=9, color=INK)
    ax.text(2150, 40228 / 2150 + 3, "Blinkit break-even line", color=INK2, fontsize=9)
    ax.text(1880, 73436 / 1880 + 4, "Instamart break-even line", color=INK2, fontsize=9)
    ax.axhline(0, color=MUTED, lw=1)
    ax.set_xlim(800, 2600)
    ax.set_ylim(-35, 80)
    ax.set_xlabel("Orders per dark store per day")
    ax.set_ylabel("Contribution per order (INR)")
    ax.set_title("Profit needs both density and per-order margin")
    ax.legend(frameon=False, loc="upper right", fontsize=10)
    save(fig, "02_isoprofit")


def chart_levers(r: dict) -> None:
    lv = r["instamart"]["levers"]
    steps = [("Gap today", lv["start_gap_per_order"]),
             ("Throughput to\nBlinkit level", -lv["lever1_throughput_per_order"]),
             ("Overhead per\nstore-day -20%", -lv["lever2_overhead_per_order"]),
             ("Left for per-order\nmargin to close", lv["lever3_contribution_per_order"])]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    run = 0
    for k, (lab, v) in enumerate(steps):
        if k == 0 or k == len(steps) - 1:
            bottom, h, col = 0, v, INSTAMART if k == 0 else INK2
        else:
            bottom, h, col = run + v, -v, MUTED
        ax.bar(k, h, bottom=bottom, color=col, width=0.6, edgecolor="white", linewidth=2)
        ax.text(k, bottom + h + 1.5, f"INR {abs(v):.1f}", ha="center", color=INK, fontsize=10)
        run = run + v if 0 < k < len(steps) - 1 else (v if k == 0 else run)
    ax.set_xticks(range(len(steps)), [s[0] for s in steps])
    ax.set_ylim(0, 80)
    ax.set_ylabel("INR per order")
    ax.set_title("Density and overhead cuts close only 40% of Instamart's gap")
    ax.grid(axis="x", visible=False)
    save(fig, "03_instamart_levers")


def chart_contribution(p: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.2))
    for comp, col in (("Blinkit", BLINKIT), ("Instamart", INSTAMART)):
        d = p[p.company == comp]
        x = np.arange(len(d))
        ax.plot(x, d.contribution_per_order, color=col, lw=2, marker="o", ms=8, label=comp)
        ax.text(x[-1] + 0.15, d.contribution_per_order.iloc[-1], f"INR {d.contribution_per_order.iloc[-1]:.1f}",
                color=INK, va="center", fontsize=10)
    ax.axhline(0, color=MUTED, lw=1)
    ax.set_xticks(np.arange(9), p[p.company == "Blinkit"].quarter)
    ax.set_ylabel("Contribution per order (INR)")
    ax.set_title("Blinkit earns ~INR 35 more per order than Instamart")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.66), fontsize=10)
    save(fig, "04_contribution_per_order")


def chart_scale(p: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.2))
    for comp, col in (("Blinkit", BLINKIT), ("Instamart", INSTAMART)):
        d = p[p.company == comp]
        x = np.arange(len(d))
        ax.plot(x, d.orders_mn, color=col, lw=2, marker="o", ms=8, label=comp)
        ax.text(x[-1] + 0.15, d.orders_mn.iloc[-1], f"{d.orders_mn.iloc[-1]:.0f} mn", color=INK, va="center", fontsize=10)
    ax.set_xticks(np.arange(9), p[p.company == "Blinkit"].quarter)
    ax.set_ylabel("Orders per quarter (million)")
    ax.set_title("Blinkit's quarterly orders grew 4.3x in two years; Instamart's 1.9x")
    ax.legend(frameon=False, loc="upper left", fontsize=10)
    save(fig, "05_order_scale")


def export_deck_data(p: pd.DataFrame, r: dict) -> None:
    """Series the PowerPoint builder (deck/build_deck.js) reads."""
    b, i = p[p.company == "Blinkit"], p[p.company == "Instamart"]
    d = {"quarters": list(b.quarter),
         "b_opsd": [round(x) for x in b.orders_per_store_day],
         "b_be": [round(x) for x in b.breakeven_orders_per_store_day],
         "b_cpo": [round(x, 1) for x in b.contribution_per_order],
         "i_cpo": [round(x, 1) for x in i.contribution_per_order],
         "b_orders": [round(x, 1) for x in b.orders_mn],
         "i_orders": [round(x, 1) for x in i.orders_mn],
         "results": r}
    (ROOT / "deck" / "deck_data.json").write_text(json.dumps(d, indent=1) + "\n")


def run() -> None:
    p = pd.read_csv(OUT / "store_day_pnl.csv")
    r = json.loads((OUT / "results.json").read_text())
    export_deck_data(p, r)
    chart_breakeven(p)
    chart_isoprofit(p)
    chart_levers(r)
    chart_contribution(p)
    chart_scale(p)


if __name__ == "__main__":
    run()
