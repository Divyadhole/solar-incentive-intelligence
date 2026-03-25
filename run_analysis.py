"""
run_analysis.py — US Solar Incentive Intelligence Pipeline
Sources: EIA Open Data + NREL Solar Resource + DSIRE
"""
import sys, os, sqlite3
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from src.fetch_data import fetch_all
from src.solar_economics import compute_state_economics
from src.charts import run_all

PROCESSED = "data/processed"
EXCEL     = "outputs/excel"
os.makedirs(PROCESSED, exist_ok=True)
os.makedirs(EXCEL, exist_ok=True)

print("=" * 60)
print("  US SOLAR INCENTIVE INTELLIGENCE")
print("  EIA + NREL + DSIRE")
print("=" * 60)

print("\n[1/4] Fetching data...")
rates, solar, incentives = fetch_all()

print("\n[2/4] Computing state solar economics...")
df = compute_state_economics()
print(f"  {len(df)} states analyzed")
print(f"\n  Top 5 states for commercial solar:")
for _, r in df.head(5).iterrows():
    print(f"    #{int(r['rank'])} {r['state_name'] or r['state']:<18} "
          f"Score:{r['composite_score']:.0f}  "
          f"IRR:{r['irr']*100:.1f}%  "
          f"Payback:{r['simple_payback_yrs']:.1f}yr")

print("\n[3/4] Generating charts...")
run_all(df)

print("\n[4/4] Building Excel workbook...")
with pd.ExcelWriter(f"{EXCEL}/solar_incentive_analysis.xlsx",
                    engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="State Rankings", index=False)

    summary = pd.DataFrame([
        {"Metric": "States analyzed",           "Value": str(len(df))},
        {"Metric": "Best IRR state",            "Value": f"{df.iloc[0]['state_name']} ({df.iloc[0]['irr']*100:.1f}%)"},
        {"Metric": "Worst IRR state",           "Value": f"{df.iloc[-1]['state_name']} ({df.iloc[-1]['irr']*100:.1f}%)"},
        {"Metric": "States with >12% IRR",      "Value": str((df["irr"]>0.12).sum())},
        {"Metric": "States with <10yr payback", "Value": str((df["simple_payback_yrs"]<10).sum())},
        {"Metric": "Avg IRR all states",        "Value": f"{df['irr'].mean()*100:.1f}%"},
        {"Metric": "Avg payback all states",    "Value": f"{df['simple_payback_yrs'].mean():.1f} yr"},
        {"Metric": "EIA data source",           "Value": "EIA Electric Power Monthly 2023, Table 5.6.B"},
        {"Metric": "NREL data source",          "Value": "NREL 10km Solar Resource Database"},
        {"Metric": "Incentive source",          "Value": "DSIRE - dsireusa.org (Jan 2024)"},
    ])
    summary.to_excel(writer, sheet_name="Summary", index=False)
    incentives.to_excel(writer, sheet_name="State Incentives", index=False)
    solar.to_excel(writer, sheet_name="NREL Solar Resource", index=False)
    rates.to_excel(writer, sheet_name="EIA Rates", index=False)

    for ws in writer.sheets.values():
        for col in ws.columns:
            w = max(len(str(c.value or "")) for c in col) + 3
            ws.column_dimensions[col[0].column_letter].width = min(w, 40)

print(f"  ✓ Excel → {EXCEL}/solar_incentive_analysis.xlsx")
print(f"\n{'='*60}\n  PIPELINE COMPLETE\n{'='*60}")
print(f"  Best state: {df.iloc[0]['state_name']} — "
      f"IRR {df.iloc[0]['irr']*100:.1f}%, "
      f"Payback {df.iloc[0]['simple_payback_yrs']:.1f}yr")
print(f"  SOLON market (AZ): rank #{int(df[df['state']=='AZ']['rank'].values[0])}, "
      f"IRR {float(df[df['state']=='AZ']['irr'].values[0])*100:.1f}%")
