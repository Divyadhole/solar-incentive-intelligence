"""
src/charts.py
All charts for US Solar Incentive Intelligence Dashboard.
Published to GitHub Pages via docs/index.html.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from pathlib import Path

OUT = Path("outputs/charts")
OUT.mkdir(parents=True, exist_ok=True)

SOLAR_ORANGE = "#FF6B35"
DARK_BLUE    = "#1B3A5C"
MID_BLUE     = "#4A90C4"
GREEN        = "#27AE60"
AMBER        = "#F39C12"
RED          = "#E74C3C"
GRAY         = "#95A5A6"

BASE = {
    "figure.facecolor":"white","axes.facecolor":"#FAFAFA",
    "axes.spines.top":False,"axes.spines.right":False,
    "axes.spines.left":False,"axes.grid":True,
    "axes.grid.axis":"y","grid.color":"#ECECEC","grid.linewidth":0.6,
    "font.family":"DejaVu Sans","axes.titlesize":12,
    "axes.titleweight":"bold","axes.labelsize":10,
    "xtick.labelsize":8.5,"ytick.labelsize":9,
    "xtick.bottom":False,"ytick.left":False,
}

def save(fig, name):
    p = OUT / f"{name}.png"
    fig.savefig(p, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓ {name}.png")


def chart_irr_by_state(df: pd.DataFrame):
    """Top 20 states by IRR — the core commercial decision chart."""
    top = df.nlargest(20, "irr").sort_values("irr", ascending=True)
    tier_color = {
        "Strong": GREEN, "Moderate": AMBER,
    }
    colors = [tier_color.get(t, GRAY) for t in top["incentive_tier"]]

    with plt.rc_context({**BASE, "axes.grid.axis":"x"}):
        fig, ax = plt.subplots(figsize=(11, 7))
        bars = ax.barh(top["state_name"].fillna(top["state"]),
                       top["irr"] * 100, color=colors, height=0.65, alpha=0.88)
        ax.axvline(8, color=GRAY, lw=1.2, linestyle="--",
                   label="8% hurdle rate")
        for bar, v in zip(bars, top["irr"] * 100):
            ax.text(v + 0.1, bar.get_y() + bar.get_height() / 2,
                    f"{v:.1f}%", va="center", fontsize=9, fontweight="bold")
        patches = [
            mpatches.Patch(color=GREEN, label="Strong incentives"),
            mpatches.Patch(color=AMBER, label="Moderate incentives"),
            mpatches.Patch(color=GRAY,  label="No state data"),
        ]
        ax.legend(handles=patches, fontsize=8.5)
        ax.set_xlabel("IRR (%) — 100kW commercial, $2.80/W, 25yr")
        ax.set_title("Top 20 States by Commercial Solar IRR\n"
                     "Source: EIA 2023 electricity rates + NREL solar resource")
        fig.tight_layout()
        save(fig, "01_irr_by_state")


def chart_electricity_rates_map_data(df: pd.DataFrame):
    """Bar chart of electricity rates — proxy for map visualization."""
    sorted_df = df.sort_values("elec_rate_cents", ascending=True)
    states_short = sorted_df["state"].values
    rates = sorted_df["elec_rate_cents"].values
    colors = [RED if r > 18 else AMBER if r > 12 else GREEN for r in rates]

    with plt.rc_context({**BASE, "axes.grid.axis":"y"}):
        fig, ax = plt.subplots(figsize=(18, 5))
        bars = ax.bar(states_short, rates, color=colors, alpha=0.88, width=0.7)
        ax.axhline(df["elec_rate_cents"].mean(), color=DARK_BLUE, lw=1.5,
                   linestyle="--",
                   label=f"National avg {df['elec_rate_cents'].mean():.1f}¢/kWh")
        ax.set_ylabel("Commercial Rate (¢/kWh)")
        ax.set_title("EIA 2023 Commercial Electricity Rates — All 50 States\n"
                     "Green < 12¢ | Orange 12-18¢ | Red > 18¢")
        ax.legend(fontsize=9)
        ax.tick_params(axis="x", labelsize=7)
        ax.spines["bottom"].set_visible(True)
        fig.tight_layout()
        save(fig, "02_electricity_rates_all_states")


def chart_solar_resource_vs_rate(df: pd.DataFrame):
    """Scatter: solar resource vs electricity rate — sweet spot analysis."""
    with plt.rc_context({**BASE, "axes.grid": False}):
        fig, ax = plt.subplots(figsize=(11, 7))

        sc = ax.scatter(
            df["capacity_factor"] * 100,
            df["elec_rate_cents"],
            c=df["irr"] * 100,
            cmap="RdYlGn",
            s=100, alpha=0.85,
            edgecolors="white", linewidths=0.7, vmin=5, vmax=30,
        )
        for _, row in df.iterrows():
            if row["irr"] > 0.15 or row["elec_rate_cents"] > 20:
                ax.annotate(
                    row["state"],
                    (row["capacity_factor"] * 100, row["elec_rate_cents"]),
                    fontsize=7.5, color="#333",
                    xytext=(4, 3), textcoords="offset points",
                )
        cbar = plt.colorbar(sc, ax=ax, fraction=0.03)
        cbar.set_label("IRR (%)", size=9)
        ax.axvline(17.5, color=GRAY, lw=1, linestyle=":")
        ax.axhline(12.0, color=GRAY, lw=1, linestyle=":")
        ax.set_xlabel("Capacity Factor (%) — NREL solar resource")
        ax.set_ylabel("Commercial Electricity Rate (¢/kWh) — EIA 2023")
        ax.set_title("Solar Resource vs Electricity Rate\n"
                     "Top-right quadrant = best for commercial solar (high rate + high sun)")
        ax.spines["left"].set_visible(True)
        ax.spines["bottom"].set_visible(True)
        fig.tight_layout()
        save(fig, "03_solar_resource_vs_rate")


def chart_composite_score(df: pd.DataFrame):
    """Top 25 states by composite solar economics score."""
    top = df.nlargest(25, "composite_score").sort_values("composite_score")
    colors = [GREEN if s > 60 else AMBER if s > 40 else GRAY
              for s in top["composite_score"]]

    with plt.rc_context({**BASE, "axes.grid.axis":"x"}):
        fig, ax = plt.subplots(figsize=(11, 8))
        bars = ax.barh(top["state_name"].fillna(top["state"]),
                       top["composite_score"],
                       color=colors, height=0.65, alpha=0.88)
        for bar, v in zip(bars, top["composite_score"]):
            ax.text(v + 0.3, bar.get_y() + bar.get_height() / 2,
                    f"{v:.0f}", va="center", fontsize=9, fontweight="bold")
        ax.set_xlabel("Composite Solar Economics Score (0-100)")
        ax.set_title("US States Ranked by Commercial Solar Economics\n"
                     "Score = EIA Rate (30%) + NREL Solar (25%) + IRR (25%) "
                     "+ Payback (10%) + Incentives (10%)")
        fig.tight_layout()
        save(fig, "04_composite_score_ranking")


def chart_payback_distribution(df: pd.DataFrame):
    """Distribution of payback periods across all states."""
    with plt.rc_context({**BASE, "axes.grid.axis":"y"}):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

        ax1.hist(df["simple_payback_yrs"].dropna(), bins=15,
                 color=MID_BLUE, alpha=0.85, edgecolor="white")
        ax1.axvline(df["simple_payback_yrs"].mean(), color=RED, lw=2,
                    linestyle="--",
                    label=f"Avg {df['simple_payback_yrs'].mean():.1f} yr")
        ax1.axvline(10, color=GREEN, lw=1.5, linestyle=":",
                    label="10-yr threshold")
        ax1.set_xlabel("Simple Payback Period (years)")
        ax1.set_ylabel("Number of States")
        ax1.set_title("Payback Period Distribution\n(100kW, $2.80/W, state-specific EIA rate)")
        ax1.legend(fontsize=9)
        ax1.spines["left"].set_visible(True)

        sorted_df = df.sort_values("simple_payback_yrs")
        pb_colors = [GREEN if p < 8 else AMBER if p < 12 else RED
                     for p in sorted_df["simple_payback_yrs"]]
        ax2.bar(range(len(sorted_df)), sorted_df["simple_payback_yrs"],
                color=pb_colors, alpha=0.85, width=0.8)
        ax2.set_xticks(range(len(sorted_df)))
        ax2.set_xticklabels(sorted_df["state"].values, rotation=90, fontsize=7)
        ax2.set_ylabel("Simple Payback (years)")
        ax2.set_title("Payback Period by State\nGreen < 8yr | Orange 8-12yr | Red > 12yr")
        ax2.spines["left"].set_visible(True)

        fig.tight_layout()
        save(fig, "05_payback_distribution")


def chart_incentive_breakdown(df: pd.DataFrame):
    """State incentive tiers and their impact on economics."""
    tier_stats = df.groupby("incentive_tier").agg(
        avg_irr         = ("irr",           "mean"),
        avg_payback     = ("simple_payback_yrs", "mean"),
        count           = ("state",          "count"),
    ).reset_index()

    with plt.rc_context(BASE):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        tier_colors_map = {"Strong": GREEN, "Moderate": AMBER,
                           "Unknown": GRAY, "Weak": RED}
        colors_t = [tier_colors_map.get(t, GRAY) for t in tier_stats["incentive_tier"]]

        ax1.bar(tier_stats["incentive_tier"], tier_stats["avg_irr"] * 100,
                color=colors_t, alpha=0.88,
                width=0.5)
        for i, (_, row) in enumerate(tier_stats.iterrows()):
            ax1.text(i, row["avg_irr"] * 100 + 0.1, f"{row['avg_irr']*100:.1f}%",
                     ha="center", fontsize=10, fontweight="bold")
        ax1.set_ylabel("Average IRR (%)")
        ax1.set_title("Average IRR by State Incentive Tier\n"
                      "Source: DSIRE + EIA + NREL")
        ax1.spines["left"].set_visible(True)

        ax2.bar(tier_stats["incentive_tier"], tier_stats["avg_payback"],
                color=colors_t, alpha=0.88, width=0.5)
        for i, (_, row) in enumerate(tier_stats.iterrows()):
            ax2.text(i, row["avg_payback"] + 0.1,
                     f"{row['avg_payback']:.1f}yr",
                     ha="center", fontsize=10, fontweight="bold")
        ax2.set_ylabel("Average Payback (years)")
        ax2.set_title("Average Payback Period by Incentive Tier")
        ax2.spines["left"].set_visible(True)

        fig.tight_layout()
        save(fig, "06_incentive_tier_impact")


def run_all(df: pd.DataFrame):
    print("\nGenerating charts...")
    chart_irr_by_state(df)
    chart_electricity_rates_map_data(df)
    chart_solar_resource_vs_rate(df)
    chart_composite_score(df)
    chart_payback_distribution(df)
    chart_incentive_breakdown(df)
    print(f"  All charts saved to outputs/charts/")
