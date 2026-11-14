"""Build the Excel version of the store-day P&L model (live formulas, sourced inputs).

Run:  python -m model.build_excel   -> outputs/qcommerce_store_day_model.xlsx
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "qcommerce_store_day_model.xlsx"

F = "Arial"
BLUE = Font(name=F, color="0000FF")
BLACK = Font(name=F, color="000000")
GREEN = Font(name=F, color="008000")
BOLD = Font(name=F, bold=True)
TITLE = Font(name=F, bold=True, size=14)
HEAD = Font(name=F, bold=True, color="FFFFFF")
HEAD_FILL = PatternFill("solid", fgColor="1F3864")
YELLOW = PatternFill("solid", fgColor="FFFF00")
THIN = Border(bottom=Side(style="thin", color="BFBFBF"))
INR0 = '#,##0;(#,##0);"-"'
INR1 = '#,##0.0;(#,##0.0);"-"'
PCT = '0.0%;(0.0%);"-"'


def header(ws, row, labels, widths):
    for c, (lab, w) in enumerate(zip(labels, widths), start=1):
        cell = ws.cell(row=row, column=c, value=lab)
        cell.font, cell.fill = HEAD, HEAD_FILL
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        ws.column_dimensions[cell.column_letter].width = w
    ws.row_dimensions[row].height = 45


def blinkit_sheet(wb):
    ws = wb.create_sheet("Blinkit")
    d = pd.read_csv(ROOT / "data" / "blinkit_quarterly.csv")
    ws["A1"], ws["A1"].font = "Blinkit: store-day P&L (INR)", TITLE
    ws["A2"] = "Blue = reported input (Eternal shareholders' letters, Annexure A). Black = formula."
    ws["A2"].font = Font(name=F, italic=True, color="595959")
    labels = ["Quarter", "NOV (INR Cr)", "Contribution (INR Cr)", "Adj. EBITDA (INR Cr)", "Orders (mn)",
              "Net AOV (INR)", "NOV per store per day (INR '000)", "Stores at end",
              "Orders per store per day", "Store-days", "Contribution per order (INR)", "EBITDA per order (INR)",
              "Overhead per store-day (INR)", "Break-even orders per store per day", "Margin of safety"]
    header(ws, 4, labels, [10, 11, 13, 12, 10, 10, 15, 10, 13, 13, 14, 13, 15, 16, 11])
    for k, r in enumerate(d.itertuples(), start=5):
        vals = [r.quarter, r.nov_cr, r.contribution_cr, r.adj_ebitda_cr, r.orders_mn, r.naov_inr,
                r.nov_per_store_day_inr_k, r.stores_end]
        for c, v in enumerate(vals, start=1):
            cell = ws.cell(row=k, column=c, value=v)
            cell.font = BLUE if c > 1 else BOLD
            cell.number_format = INR1 if c == 5 else INR0
        f = {
            9: f"=G{k}*1000/F{k}",
            10: f"=E{k}*1000000/I{k}",
            11: f"=C{k}*10000000/(E{k}*1000000)",
            12: f"=D{k}*10000000/(E{k}*1000000)",
            13: f"=(C{k}-D{k})*10000000/J{k}",
            14: f'=IF(K{k}>0,M{k}/K{k},"n/a")',
            15: f'=IF(ISNUMBER(N{k}),I{k}/N{k}-1,"n/a")',
        }
        for c, formula in f.items():
            cell = ws.cell(row=k, column=c, value=formula)
            cell.font = BLACK
            cell.number_format = PCT if c == 15 else (INR1 if c in (11, 12) else INR0)
        for c in range(1, 16):
            ws.cell(row=k, column=c).border = THIN
    ws.cell(row=4, column=9).comment = Comment("Derived: NOV per store per day / net AOV.", "Model")
    ws.cell(row=4, column=13).comment = Comment(
        "Everything between Contribution and Adjusted EBITDA (brand marketing, corporate costs, rent), "
        "spread over store-days.", "Model")
    ws.cell(row=4, column=14).comment = Comment("Overhead per store-day / contribution per order.", "Model")
    ws.freeze_panes = "B5"
    return ws, 4 + len(d)


def instamart_sheet(wb):
    ws = wb.create_sheet("Instamart")
    d = pd.read_csv(ROOT / "data" / "instamart_quarterly.csv")
    ws["A1"], ws["A1"].font = "Swiggy Instamart: store-day P&L (INR)", TITLE
    ws["A2"] = "Blue = reported input (Swiggy shareholder letters). Black = formula. GOV = orders x AOV."
    ws["A2"].font = Font(name=F, italic=True, color="595959")
    labels = ["Quarter", "Orders (mn)", "AOV (INR)", "Contribution margin (% of GOV)", "Adj. EBITDA (INR Cr)",
              "Active dark stores (exit)", "Orders per store per day", "GOV (INR Cr)", "Contribution (INR Cr)",
              "Store-days", "Contribution per order (INR)", "EBITDA per order (INR)", "Overhead per store-day (INR)",
              "Contribution per order needed to break even (INR)", "Gap per order (INR)", "Gap (% of AOV)"]
    header(ws, 4, labels, [10, 10, 10, 14, 12, 12, 12, 11, 13, 12, 14, 13, 15, 18, 12, 11])
    for k, r in enumerate(d.itertuples(), start=5):
        vals = [r.quarter, r.orders_mn, r.aov_inr, r.contribution_pct_gov / 100, r.adj_ebitda_cr,
                r.stores_end, r.orders_per_store_day]
        for c, v in enumerate(vals, start=1):
            cell = ws.cell(row=k, column=c, value=v)
            cell.font = BLUE if c > 1 else BOLD
            cell.number_format = PCT if c == 4 else (INR1 if c == 2 else INR0)
        f = {
            8: f"=B{k}*C{k}/10",
            9: f"=D{k}*H{k}",
            10: f"=B{k}*1000000/G{k}",
            11: f"=I{k}*10000000/(B{k}*1000000)",
            12: f"=E{k}*10000000/(B{k}*1000000)",
            13: f"=(I{k}-E{k})*10000000/J{k}",
            14: f"=M{k}/G{k}",
            15: f"=N{k}-K{k}",
            16: f"=O{k}/C{k}",
        }
        for c, formula in f.items():
            cell = ws.cell(row=k, column=c, value=formula)
            cell.font = BLACK
            cell.number_format = PCT if c == 16 else (INR1 if c in (9, 11, 12, 14, 15) else INR0)
        for c in range(1, 17):
            ws.cell(row=k, column=c).border = THIN
    ws.cell(row=4, column=7).comment = Comment("Reported by Swiggy, based on active dark store-days.", "Model")
    ws.freeze_panes = "B5"
    return ws, 4 + len(d)


def levers_sheet(wb, b_last, i_last):
    ws = wb.create_sheet("Levers")
    ws["A1"], ws["A1"].font = "Instamart: three levers to Adjusted EBITDA break-even (latest quarter)", TITLE
    ws.column_dimensions["A"].width = 58
    ws.column_dimensions["B"].width = 16
    ws.column_dimensions["C"].width = 60
    rows = [
        ("Starting point", None, None),
        ("Orders per store per day (today)", f"=Instamart!G{i_last}", "link"),
        ("Contribution per order today (INR)", f"=Instamart!K{i_last}", "link"),
        ("Overhead per store-day (INR)", f"=Instamart!M{i_last}", "link"),
        ("AOV (INR)", f"=Instamart!C{i_last}", "link"),
        ("Assumptions (edit the yellow cells)", None, None),
        ("Target orders per store per day", f"=Blinkit!I{b_last}", "assume"),
        ("Overhead per store-day reduction", 0.20, "assume"),
        ("Results (INR per order)", None, None),
        ("Gap today", "=B5/B3-B4", "calc"),
        ("Lever 1: throughput to target", "=B5/B3-B5/B8", "calc"),
        ("Lever 2: overhead reduction", "=B5/B8-B5*(1-B9)/B8", "calc"),
        ("Lever 3: per-order margin still needed", "=B5*(1-B9)/B8-B4", "calc"),
        ("Lever 3 as % of AOV", "=B14/B6", "pct"),
        ("Check: levers sum to gap (should be 0)", "=B11-B12-B13-B14", "calc"),
    ]
    notes = {
        8: "Default links to Blinkit's latest throughput. Overwrite with a number to test other targets.",
        9: "Assumed operating leverage on marketing, rent and corporate costs. Not from filings.",
        14: "Would need higher take rate, ad income, 1P margins, lower discounts or delivery cost.",
    }
    for k, (lab, val, kind) in enumerate(rows, start=2):
        a = ws.cell(row=k, column=1, value=lab)
        if val is None:
            a.font = BOLD
            continue
        a.font = BLACK
        cell = ws.cell(row=k, column=2, value=val)
        cell.font = {"link": GREEN, "assume": BLUE}.get(kind, BLACK)
        if kind == "assume":
            cell.fill = YELLOW
        cell.number_format = PCT if (kind == "pct" or k == 9) else INR1
        if k in notes:
            ws.cell(row=k, column=3, value=notes[k]).font = Font(name=F, italic=True, color="595959")
    ws["A19"], ws["A19"].font = "Contribution per order needed to break even, by throughput", BOLD
    ws["A20"], ws["B20"] = "Orders per store per day", "INR per order"
    ws["A20"].font = ws["B20"].font = BOLD
    for k, t in enumerate([1192, 1400, 1718, 2000, 2500], start=21):
        ws.cell(row=k, column=1, value=t).font = BLUE
        ws.cell(row=k, column=1).number_format = INR0
        c = ws.cell(row=k, column=2, value=f"=$B$5/A{k}")
        c.font, c.number_format = BLACK, INR1


def sources_sheet(wb):
    ws = wb.create_sheet("Sources")
    ws["A1"], ws["A1"].font = "Sources", TITLE
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 100
    rows = [
        ("Blinkit Q2FY25 to Q1FY26", "https://b.zmtcdn.com/investor-relations/Eternal_Shareholders_Letter_Q2FY26_Results.pdf (Annexure A)"),
        ("Blinkit Q2FY26 to Q2FY27", "https://b.zmtcdn.com/investor-relations/Eternal_Limited_Shareholders_Letter_Q2FY27_Results.pdf (Annexure A)"),
        ("Instamart operating table", "Swiggy shareholder letters Q1FY26, Q4FY26, Q1FY27, Q2FY27 (quick commerce key metrics table)"),
        ("Instamart contribution margin", "Quarter-by-quarter highlights, Swiggy shareholder letters Q2FY25 to Q2FY27"),
        ("Swiggy letters index", "https://www.swiggy.com/corporate/investor-relations/financial-results/"),
        ("Note", "Blinkit uses net AOV (after discounts); Instamart AOV is on GOV (before discounts). "
                 "Per-order rupee comparisons are valid; % of AOV comparisons across companies are not like for like."),
    ]
    for k, (a, b) in enumerate(rows, start=3):
        ws.cell(row=k, column=1, value=a).font = BOLD
        ws.cell(row=k, column=2, value=b).font = BLACK


def build():
    wb = Workbook()
    wb.remove(wb.active)
    _, b_last = blinkit_sheet(wb)
    _, i_last = instamart_sheet(wb)
    levers_sheet(wb, b_last, i_last)
    sources_sheet(wb)
    OUT.parent.mkdir(exist_ok=True)
    wb.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
