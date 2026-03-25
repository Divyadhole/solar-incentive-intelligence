# US Solar Incentive Intelligence Dashboard

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Dashboard](https://img.shields.io/badge/🌐%20Live%20Dashboard-Click%20Here-27AE60)](https://divyadhole.github.io/solar-incentive-intelligence/)
[![EIA](https://img.shields.io/badge/EIA-Electricity%20Rates%202023-orange)](https://www.eia.gov/opendata/)
[![NREL](https://img.shields.io/badge/NREL-Solar%20Resource-yellow)](https://developer.nrel.gov/)
[![DSIRE](https://img.shields.io/badge/DSIRE-State%20Incentives-green)](https://www.dsireusa.org/)

## Live Dashboard

**[divyadhole.github.io/solar-incentive-intelligence](https://divyadhole.github.io/solar-incentive-intelligence/)**

---

## What This Answers

Which states make the most financial sense for commercial solar right now?

This project runs a standard 100kW commercial solar financial model across every US state using real EIA utility rates and NREL solar resource data, then layers in DSIRE state incentive programs to produce a composite ranking.

The answer for SOLON's home market: **Arizona ranks #5 nationally** with a 13.0% IRR and 7.2-year payback on a standard commercial system.

---

## Data Sources (All Free, All Government)

**EIA Open Data** — Commercial electricity rates by state
```python
url = "https://api.eia.gov/v2/electricity/retail-sales/data/"
# Table 5.6.B — EIA Electric Power Monthly, September 2024
# 2023 commercial rates, all 50 states, cents/kWh
```

**NREL Solar Resource Database** — Capacity factors and GHI by state
```python
url = "https://developer.nrel.gov/api/solar/"
# 10km resolution, annual average capacity factors
# Global Horizontal Irradiance (kWh/m²/day) by state
```

**DSIRE** (NC State University) — State incentive programs
```
https://www.dsireusa.org/
# Database of State Incentives for Renewables & Efficiency
# Net metering policies, state tax credits, rebate programs
```

---

## State Rankings (Top 10)

| Rank | State | Score | IRR | Payback | EIA Rate |
|---|---|---|---|---|---|
| 1 | Hawaii | 96 | 38.3% | 2.6yr | 38.8¢/kWh |
| 2 | California | 69 | 23.9% | 4.1yr | 23.1¢/kWh |
| 3 | Connecticut | 52 | 19.4% | 4.9yr | 23.0¢/kWh |
| 4 | Nevada | 52 | 13.3% | 7.0yr | 12.0¢/kWh |
| **5** | **Arizona** | **52** | **13.0%** | **7.2yr** | **11.7¢/kWh** |
| 6 | Massachusetts | 51 | 18.9% | 5.0yr | 22.4¢/kWh |
| 7 | New Mexico | 51 | 13.0% | 7.2yr | 11.9¢/kWh |
| 8 | Colorado | 44 | 11.0% | 8.4yr | 10.7¢/kWh |
| 9 | Florida | 43 | 11.4% | 8.1yr | 11.4¢/kWh |
| 10 | New Hampshire | 43 | 18.5% | 5.1yr | 22.1¢/kWh |

*100kW DC, $2.80/W, 25yr, 7% WACC, 30% ITC, MACRS*

---

## Key Findings

**High utility rates matter more than sun.** Connecticut (19.4% IRR) beats Nevada (13.3% IRR) despite Nevada having more sun, because Connecticut pays nearly double the electricity rate.

**The Arizona sweet spot.** Arizona combines strong solar resource (20.1% capacity factor) with a moderate utility rate (11.7¢/kWh) and full retail net metering. It won't top the national list but it's consistently bankable.

**State incentives add 2.1 years off payback on average.** States with strong programs (AZ, CA, NM, NV, CO) average 7.6-year paybacks vs 9.7 years for states with no state-level programs.

**Washington state has great sun economics — except the rate.** At 7.6¢/kWh (cheapest in the US), solar just doesn't pencil well regardless of solar resource.

---

## SQL Analysis

```sql
-- States where solar is clearly bankable (IRR > 12%)
SELECT state_name, irr, simple_payback_yrs, elec_rate_cents,
    RANK() OVER (ORDER BY irr DESC) AS irr_rank
FROM state_solar_economics
WHERE irr > 0.12
ORDER BY irr DESC;

-- Incentive tier impact on average payback
SELECT incentive_tier,
    COUNT(*) states,
    ROUND(AVG(irr)*100, 1) avg_irr_pct,
    ROUND(AVG(simple_payback_yrs), 1) avg_payback_yr
FROM state_solar_economics
GROUP BY incentive_tier
ORDER BY avg_irr_pct DESC;
```

---

## Run Locally

```bash
git clone https://github.com/Divyadhole/solar-incentive-intelligence
cd solar-incentive-intelligence
pip install -r requirements.txt
python run_analysis.py
```

To use live EIA API (register free at eia.gov/opendata):
```bash
export EIA_API_KEY=your_key_here
python run_analysis.py
```

---

*Built by Divya Dhole · MS Data Science @ UArizona · [divyadhole.github.io](https://divyadhole.github.io) · [LinkedIn](https://www.linkedin.com/in/divyadhole/)*
