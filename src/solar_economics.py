"""
src/solar_economics.py
Computes a composite solar economics score for each state
by combining EIA utility rates, NREL solar resource, and
state incentive program quality.

The score answers: "Which states are best for commercial solar right now?"

Used by SOLON-type companies to prioritize market development
and by analysts to advise clients on project siting.
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fetch_data import (fetch_eia_commercial_rates,
                              fetch_nrel_solar_resource,
                              get_state_incentives)
from src.financial_model import SolarProjectInputs, calculate


def compute_state_economics(
    system_size_kw: float = 100.0,
    cost_per_watt:  float = 2.80,
) -> pd.DataFrame:
    """
    For every state, compute the financial metrics of a standard
    100kW commercial solar system using real EIA + NREL data.
    """
    rates     = fetch_eia_commercial_rates()
    solar     = fetch_nrel_solar_resource()
    incentives = get_state_incentives()

    # Merge all three data sources
    merged = rates.merge(solar, on="state", how="inner")
    merged = merged.merge(
        incentives[["state","state_name","incentive_tier","state_incentive","net_metering_policy"]],
        left_on="state", right_on="state", how="left"
    )

    results_rows = []
    for _, row in merged.iterrows():
        inputs = SolarProjectInputs(
            system_size_kw   = system_size_kw,
            cost_per_watt    = cost_per_watt,
            capacity_factor  = row["capacity_factor"],
            electricity_rate = row["rate_usd_kwh"],
            rate_escalation  = 0.025,
            discount_rate    = 0.07,
            project_year     = 2024,
        )
        r = calculate(inputs)

        results_rows.append({
            "state":               row["state"],
            "state_name":          row.get("state_name", row["state"]),
            "elec_rate_kwh":       row["rate_usd_kwh"],
            "elec_rate_cents":     row["rate_cents_kwh"],
            "capacity_factor":     row["capacity_factor"],
            "ghi_kwh_m2_day":      row["ghi_kwh_m2_day"],
            "irr":                 r.irr,
            "npv_25yr":            r.npv,
            "simple_payback_yrs":  r.simple_payback_yrs,
            "lcoe":                r.lcoe,
            "year1_savings":       r.year1_savings_usd,
            "lifetime_savings":    r.lifetime_savings_usd,
            "incentive_tier":      row.get("incentive_tier", "Unknown"),
            "state_incentive":     row.get("state_incentive", False),
            "net_metering":        row.get("net_metering_policy", "Unknown"),
        })

    df = pd.DataFrame(results_rows)

    # Composite score (0-100): weighted combination
    # Higher is better for commercial solar development
    df["rate_score"]    = _normalize(df["elec_rate_cents"],    higher_better=True)
    df["solar_score"]   = _normalize(df["capacity_factor"],    higher_better=True)
    df["irr_score"]     = _normalize(df["irr"],                higher_better=True)
    df["payback_score"] = _normalize(df["simple_payback_yrs"], higher_better=False)
    df["incentive_score"] = df["incentive_tier"].map(
        {"Strong": 1.0, "Moderate": 0.5, "Weak": 0.2}
    ).fillna(0.3)

    df["composite_score"] = (
        df["rate_score"]    * 0.30 +
        df["solar_score"]   * 0.25 +
        df["irr_score"]     * 0.25 +
        df["payback_score"] * 0.10 +
        df["incentive_score"] * 0.10
    ) * 100

    df["composite_score"] = df["composite_score"].round(1)
    df = df.sort_values("composite_score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1

    return df


def _normalize(series: pd.Series, higher_better: bool = True) -> pd.Series:
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series([0.5] * len(series), index=series.index)
    normalized = (series - mn) / (mx - mn)
    return normalized if higher_better else (1 - normalized)


if __name__ == "__main__":
    print("Computing solar economics for all states...")
    df = compute_state_economics()
    print(f"\nTop 10 states for commercial solar (100kW, $2.80/W):\n")
    print(f"{'Rank':<5} {'State':<20} {'Score':<8} {'IRR':<8} "
          f"{'Payback':<10} {'Rate(¢)':<10} {'CF%'}")
    print("-" * 70)
    for _, row in df.head(10).iterrows():
        print(f"  {int(row['rank']):<4} {row['state_name']:<20} "
              f"{row['composite_score']:<8.1f} {row['irr']*100:<8.1f}% "
              f"{row['simple_payback_yrs']:<10.1f} {row['elec_rate_cents']:<10.1f} "
              f"{row['capacity_factor']*100:.1f}%")

    df.to_csv("data/processed/state_solar_economics.csv", index=False)
    print(f"\nSaved: data/processed/state_solar_economics.csv")
