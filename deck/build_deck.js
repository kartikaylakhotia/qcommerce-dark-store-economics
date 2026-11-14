// Builds deck/QCommerce_Dark_Store_Economics.pptx from deck_data.json and outputs/charts.
// Run: node deck/build_deck.js   (from the repo root)
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
// Optional: writes the theme colours into the .pptx if the helper is available (set PPTX_SKILL).
const applyTheme = process.env.PPTX_SKILL ? require(process.env.PPTX_SKILL + "/scripts/apply_theme.js").applyTheme : async () => {};

const ROOT = path.resolve(__dirname, "..");
const D = JSON.parse(fs.readFileSync(path.join(__dirname, "deck_data.json"), "utf8"));
const R = D.results;

const THEME = {
  name: "QCommerce",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B2430", lt1: "FFFFFF", dk2: "52514E", lt2: "F3F4F6",
    accent1: "2A78D6", accent2: "EB6834", accent3: "8A8985", accent4: "1B2430",
    accent5: "1BAF7A", accent6: "E34948", hlink: "2A78D6", folHlink: "6250D6",
  },
};
const HEX = { ink: "1B2430", ink2: "52514E", muted: "8A8985", grid: "E6E5E1", blue: "2A78D6", orange: "EB6834", light: "F3F4F6" };

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Quick-Commerce Dark-Store Profitability";
pres.author = "Kartikay Lakhotia";
const C = pres.SchemeColor;
const SRC = "Source: Eternal and Swiggy quarterly shareholder letters, Q2FY25 to Q2FY27; author's analysis";

pres.defineSlideMaster({
  title: "DARK",
  background: { color: HEX.ink },
  objects: [],
  placeholders: [],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: "FFFFFF" },
  objects: [
    { text: { text: SRC, options: { x: 0.5, y: 5.22, w: 8.2, h: 0.25, fontSize: 9, color: C.text2, fontFace: "Calibri" } } },
  ],
  slideNumber: { x: 9.1, y: 5.22, w: 0.4, h: 0.25, fontSize: 9, color: HEX.muted, fontFace: "Calibri" },
});

const chartFont = { catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", legendFontFace: "+mn-lt",
  dataLabelFontFace: "+mn-lt", titleFontFace: "+mn-lt" };
const axisStyle = { catAxisLabelColor: HEX.ink2, valAxisLabelColor: HEX.ink2, catAxisLabelFontSize: 10, valAxisLabelFontSize: 10,
  valGridLine: { color: HEX.grid, size: 0.75 }, catGridLine: { style: "none" }, catAxisLineColor: HEX.muted, valAxisLineShow: false };

function content(title, sectionTitle) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle });
  s.addText(title, { x: 0.5, y: 0.3, w: 9.0, h: 0.85, fontFace: "Cambria", fontSize: 22, bold: true, color: C.text1,
    valign: "top", margin: 0, isTextBox: true, objectName: "title" });
  return s;
}
function note(s, lines, x, y, w, h) {
  s.addText(lines.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < lines.length - 1 } })),
    { x, y, w, h, fontSize: 14, color: C.text1, valign: "top", paraSpaceAfter: 8, isTextBox: true, objectName: "commentary" });
}
function stat(s, value, label, x, y, color) {
  s.addText(value, { x, y, w: 2.7, h: 0.6, fontFace: "Cambria", fontSize: 28, bold: true, color, margin: 0, isTextBox: true });
  s.addText(label, { x, y: y + 0.6, w: 2.6, h: 0.45, fontSize: 11, color: C.text2, margin: 0, valign: "top", isTextBox: true });
}
const inr = (v) => "₹" + v.toLocaleString("en-IN", { maximumFractionDigits: 1 });

// 1. Title -----------------------------------------------------------------
pres.addSection({ title: "Answer" });
let s = pres.addSlide({ masterName: "DARK", sectionTitle: "Answer" });
s.addText("Quick commerce profitability is won on margin per order, not on density alone", {
  x: 0.6, y: 1.2, w: 8.8, h: 1.7, fontFace: "Cambria", fontSize: 34, bold: true, color: "FFFFFF", valign: "top", margin: 0, isTextBox: true });
s.addText("Blinkit vs Swiggy Instamart: a store-day P&L built from 9 quarters of shareholder letters (Q2FY25 to Q2FY27)", {
  x: 0.6, y: 3.05, w: 8.4, h: 0.7, fontSize: 16, color: "CADCFC", margin: 0, valign: "top", isTextBox: true });
s.addText("Kartikay Lakhotia  |  November 2026", { x: 0.6, y: 4.7, w: 6, h: 0.35, fontSize: 12, color: "AEB4BF", margin: 0, isTextBox: true });

// 2. Executive summary -----------------------------------------------------
s = content("Executive summary: Instamart must earn ₹69 more per order; density can close only part of it", "Answer");
const rows = [
  ["1", `Blinkit breaks even at ~${R.blinkit.breakeven_orders_per_store_day.toLocaleString("en-IN")} orders per store per day and runs ${R.blinkit.orders_per_store_day.toLocaleString("en-IN")}, a ${Math.round(R.blinkit.margin_of_safety_pct)}% cushion. It turned profitable in Q3FY26 mainly by earning more per order, which pulled its break-even down from ~2,290 to ~1,360.`, HEX.blue],
  ["2", `Instamart loses ${inr(-R.instamart.contribution_per_order)} on every order at 1,192 orders per store per day. To cover its overheads it needs ${inr(R.instamart.gap_per_order)} more per order, ${R.instamart.gap_pct_of_aov}% of its basket.`, HEX.orange],
  ["3", `Matching Blinkit's density and cutting overhead per store-day by 20% close only 40% of that gap. The other ${inr(R.instamart.levers.lever3_contribution_per_order)} per order has to come from take rate, ad income, 1P margins and lower discounts.`, HEX.ink],
];
rows.forEach(([n, t, col], k) => {
  const y = 1.35 + k * 1.22;
  s.addShape(pres.shapes.OVAL, { x: 0.55, y: y + 0.05, w: 0.5, h: 0.5, fill: { color: col }, line: { color: col }, objectName: "num" + n });
  s.addText(n, { x: 0.55, y: y + 0.05, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0, isTextBox: true });
  s.addText(t, { x: 1.3, y, w: 8.2, h: 1.05, fontSize: 15, color: C.text1, valign: "top", margin: 0, isTextBox: true });
});

// 3. Context ---------------------------------------------------------------
pres.addSection({ title: "Context and method" });
s = content("Blinkit handles 3x Instamart's orders from 2.2x the stores", "Context and method");
s.addChart(pres.charts.LINE, [
  { name: "Blinkit", labels: D.quarters, values: D.b_orders },
  { name: "Instamart", labels: D.quarters, values: D.i_orders },
], { x: 0.4, y: 1.25, w: 6.1, h: 3.85, chartColors: [HEX.blue, HEX.orange], lineSize: 2, lineDataSymbolSize: 7,
  showLegend: true, legendPos: "t", legendFontSize: 11, legendColor: HEX.ink2, showValAxisTitle: true, valAxisTitle: "Orders per quarter (mn)",
  valAxisTitleFontSize: 10, valAxisTitleColor: HEX.ink2, ...axisStyle, ...chartFont });
stat(s, "399 mn", "Blinkit orders in Q2FY27 (4.3x two years earlier)", 6.9, 1.35, HEX.blue);
stat(s, "130 mn", "Instamart orders in Q2FY27 (1.9x)", 6.9, 2.55, HEX.orange);
stat(s, "2,751 vs 1,240", "Dark stores at end of Q2FY27", 6.9, 3.75, HEX.ink);

// 4. Method ----------------------------------------------------------------
s = content("One identity explains profit per dark store per day", "Context and method");
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.3, w: 9.0, h: 1.05, rectRadius: 0.1, fill: { color: HEX.light }, line: { color: HEX.light }, objectName: "identity" });
s.addText([
  { text: "EBITDA per store-day", options: { bold: true, color: HEX.ink } },
  { text: "  =  orders per store-day  ×  contribution per order  −  overhead per store-day", options: { color: HEX.ink } },
], { x: 0.7, y: 1.4, w: 8.6, h: 0.5, fontSize: 15, margin: 0, isTextBox: true });
s.addText("Break-even orders per store per day  =  overhead per store-day  ÷  contribution per order", {
  x: 0.7, y: 1.85, w: 8.6, h: 0.4, fontSize: 14, color: C.text2, margin: 0, isTextBox: true });
const steps = [
  ["Collect", "180 reported data points: orders, order value, contribution, Adjusted EBITDA, stores and store productivity, 9 quarters each."],
  ["Convert", "Turn quarterly totals into store-days, contribution per order and overhead per store-day (all costs between contribution and EBITDA)."],
  ["Test", "Rebuild reported EBITDA exactly from the identity, then size break-even, gaps and levers. Six automated checks run on every change."],
];
steps.forEach(([h, t], k) => {
  const x = 0.5 + k * 3.05;
  s.addShape(pres.shapes.OVAL, { x, y: 2.75, w: 0.45, h: 0.45, fill: { color: HEX.ink }, line: { color: HEX.ink }, objectName: "step" + k });
  s.addText(String(k + 1), { x, y: 2.75, w: 0.45, h: 0.45, fontSize: 14, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0, isTextBox: true });
  s.addText(h, { x: x + 0.6, y: 2.75, w: 2.2, h: 0.45, fontFace: "Cambria", fontSize: 16, bold: true, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
  s.addText(t, { x, y: 3.35, w: 2.8, h: 1.6, fontSize: 13, color: C.text1, valign: "top", margin: 0, isTextBox: true });
});

// 5. Blinkit break-even ------------------------------------------------------
pres.addSection({ title: "Findings" });
s = content("Blinkit got profitable by cutting its break-even point, not by density alone", "Findings");
s.addChart(pres.charts.LINE, [
  { name: "Actual orders per store per day", labels: D.quarters, values: D.b_opsd },
  { name: "Break-even orders per store per day", labels: D.quarters, values: D.b_be },
], { x: 0.4, y: 1.25, w: 6.0, h: 3.85, chartColors: [HEX.blue, HEX.muted], lineSize: 2, lineDataSymbolSize: 7,
  showLegend: true, legendPos: "t", legendFontSize: 11, legendColor: HEX.ink2,
  valAxisMinVal: 1000, valAxisMaxVal: 2400, valAxisMajorUnit: 200, ...axisStyle, ...chartFont });
note(s, [
  "Throughput barely moved for six quarters: ~1,370 to 1,490 orders per store per day.",
  "Break-even fell from ~2,290 to ~1,360 as contribution per order rose from ₹20 to ₹30.",
  "Q3FY26 is where the lines cross: Blinkit's first profitable quarter.",
  "Today: 1,718 actual vs 1,435 break-even, a 20% cushion.",
], 6.7, 1.35, 2.9, 3.7);

// 6. Contribution per order ----------------------------------------------------
s = content("The real difference: Blinkit earns ₹35 more on every order than Instamart", "Findings");
s.addChart(pres.charts.LINE, [
  { name: "Blinkit", labels: D.quarters, values: D.b_cpo },
  { name: "Instamart", labels: D.quarters, values: D.i_cpo },
], { x: 0.4, y: 1.25, w: 6.0, h: 3.85, chartColors: [HEX.blue, HEX.orange], lineSize: 2, lineDataSymbolSize: 7,
  showLegend: true, legendPos: "t", legendFontSize: 11, legendColor: HEX.ink2, showValAxisTitle: true,
  valAxisTitle: "Contribution per order (₹)", valAxisTitleFontSize: 10, valAxisTitleColor: HEX.ink2, ...axisStyle, ...chartFont });
note(s, [
  "Contribution per order = what an order leaves after delivery, discounts, dark store and other variable costs.",
  "Blinkit: ₹28.0 in Q2FY27. Instamart: −₹7.1.",
  "Instamart has not earned a positive contribution in any of the 9 quarters; its best was −₹1.4 (Q1FY27).",
], 6.7, 1.35, 2.9, 3.7);

// 7. Iso-profit -----------------------------------------------------------
s = content("Instamart sits far below its break-even line at every throughput it has reached", "Findings");
s.addImage({ path: path.join(ROOT, "outputs/charts/02_isoprofit.png"), x: 0.4, y: 1.2, w: 6.0, h: 3.69, altText: "Contribution per order vs orders per store per day, with break-even curves" });
note(s, [
  "Each dashed curve is the set of points where Adjusted EBITDA is exactly zero.",
  "Blinkit's path crossed its curve in Q3FY26 and is now above it.",
  "Instamart's points all sit below zero contribution, so more orders alone deepen losses.",
], 6.7, 1.35, 2.9, 3.7);

// 8. Required contribution table ------------------------------------------------
s = content("Even at 2,500 orders a day, Instamart would need ₹29 per order, more than it has ever earned", "Findings");
const req = R.instamart.required_contribution_by_throughput;
const hdr = [{ text: "Orders per store per day", options: { bold: true, color: "FFFFFF", fill: { color: HEX.ink } } },
             { text: "Contribution per order needed (₹)", options: { bold: true, color: "FFFFFF", fill: { color: HEX.ink } } },
             { text: "As % of basket (AOV ₹708)", options: { bold: true, color: "FFFFFF", fill: { color: HEX.ink } } }];
const body = req.map((r) => [
  { text: r.orders_per_store_day.toLocaleString("en-IN") + (r.orders_per_store_day === 1192 ? " (today)" : r.orders_per_store_day === 1718 ? " (Blinkit today)" : "") },
  { text: inr(r.required_contribution_per_order) },
  { text: (100 * r.required_contribution_per_order / 708).toFixed(1) + "%" },
]);
s.addTable([hdr, ...body], { x: 0.5, y: 1.35, w: 5.9, colW: [2.2, 2.1, 1.6], fontSize: 13, fontFace: "Calibri", color: HEX.ink,
  border: { type: "solid", pt: 0.75, color: HEX.grid }, rowH: 0.42, valign: "middle" });
note(s, [
  `Overhead is ${inr(R.instamart.overhead_per_store_day)} per store per day, so every store must earn that back before profit.`,
  `Today Instamart earns −₹7.1 per order: the gap is ${inr(R.instamart.gap_per_order)}.`,
  "Even at 2,000 orders a day, the hurdle is still ₹37 per order.",
], 6.7, 1.35, 2.9, 3.7);

// 9. Levers waterfall -------------------------------------------------------
pres.addSection({ title: "Recommendation" });
const L = R.instamart.levers;
s = content(`Density and overhead cuts close only 40% of the gap; ${inr(L.lever3_contribution_per_order)} per order must come from margin`, "Recommendation");
const cats = [`Gap today\n${inr(L.start_gap_per_order)}`, `Throughput to\nBlinkit level\n−${inr(L.lever1_throughput_per_order)}`, `Overhead per\nstore-day −20%\n−${inr(L.lever2_overhead_per_order)}`, `Left for margin\nper order\n${inr(L.lever3_contribution_per_order)}`];
const base = [0, L.start_gap_per_order - L.lever1_throughput_per_order, L.lever3_contribution_per_order, 0];
const vals = [L.start_gap_per_order, L.lever1_throughput_per_order, L.lever2_overhead_per_order, L.lever3_contribution_per_order];
s.addChart(pres.charts.BAR, [
  { name: "base", labels: cats, values: base },
  { name: "value", labels: cats, values: vals },
], { x: 0.4, y: 1.25, w: 6.0, h: 3.85, barDir: "col", barGrouping: "stacked", chartColors: ["FFFFFF", HEX.orange],
  showLegend: false, showValue: false, valAxisMinVal: 0, valAxisMaxVal: 80, valAxisMajorUnit: 20, barGapWidthPct: 60,
  catAxisLabelRotate: 0, showValAxisTitle: true, valAxisTitle: "₹ per order", valAxisTitleFontSize: 10, valAxisTitleColor: HEX.ink2, ...axisStyle, ...chartFont });
note(s, [
  "Per-order margin sources: take rate, ad income from brands, 1P (own inventory) margins, fewer platform discounts, cheaper delivery.",
  "Swiggy expects the move to its own inventory to add ~80 bps of contribution margin: about ₹6 per order, only a seventh of what is needed.",
], 6.7, 1.35, 2.9, 3.7);

// 10. Recommendations ------------------------------------------------------
s = pres.addSlide({ masterName: "DARK", sectionTitle: "Recommendation" });
s.addText("What Instamart should do, in order", { x: 0.6, y: 0.4, w: 8.8, h: 0.6, fontFace: "Cambria", fontSize: 26, bold: true, color: "FFFFFF", margin: 0, isTextBox: true });
const recs = [
  ["Fix the order before the network", "Target +₹41 per order: finish the inventory-led shift, grow brand ad income, and cut platform-funded discounts (discounts take ~29% off GOV)."],
  ["Add stores only where density is proven", "Open new dark stores only where existing ones run above ~1,700 orders a day, the throughput at which Blinkit is profitable today."],
  ["Hold overhead flat while orders grow", "A 20% lower overhead per store-day is worth ₹8.5 per order; keep marketing and corporate costs flat in absolute terms."],
];
recs.forEach(([h, t], k) => {
  const y = 1.3 + k * 1.05;
  s.addText(String(k + 1), { x: 0.6, y, w: 0.45, h: 0.45, fontSize: 18, bold: true, color: HEX.orange, margin: 0, isTextBox: true });
  s.addText(h, { x: 1.15, y, w: 8.2, h: 0.4, fontFace: "Cambria", fontSize: 17, bold: true, color: "FFFFFF", margin: 0, isTextBox: true });
  s.addText(t, { x: 1.15, y: y + 0.4, w: 8.2, h: 0.55, fontSize: 13, color: "D5D9E0", margin: 0, valign: "top", isTextBox: true });
});
s.addText("For Blinkit: a 5% EBITDA margin at today's density needs ~₹50 per order (vs ₹28), so the next leg is also per-order margin.  Caveats: overhead is treated as fixed per store-day; Blinkit AOV is net of discounts while Instamart's is gross.", {
  x: 0.6, y: 4.5, w: 8.8, h: 0.7, fontSize: 11, color: "AEB4BF", margin: 0, valign: "top", isTextBox: true });

(async () => {
  const out = path.join(__dirname, "QCommerce_Dark_Store_Economics.pptx");
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log(out);
})();
