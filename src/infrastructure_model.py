"""
infrastructure_model.py - Charging station demand projection, grid energy load simulation, and gap analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any


def calculate_infrastructure_requirements(
    forecast_df: pd.DataFrame,
    current_l2_ports: int = 26500,
    current_dcfc_ports: int = 8200,
    ev_per_l2: float = 22.0,
    ev_per_dcfc: float = 85.0,
    avg_annual_miles: float = 12500.0,
    avg_kwh_per_mile: float = 0.34,
    peak_coincidence_factor: float = 0.14
) -> pd.DataFrame:
    """
    Computes required charging infrastructure and electrical grid load for each year in the forecast.
    
    Parameters:
      - forecast_df: output of forecast_ev_adoption containing cumulative_fleet and year
      - current_l2_ports: baseline installed Level 2 ports
      - current_dcfc_ports: baseline installed DC Fast Charging ports
      - ev_per_l2: ratio of EVs to one public/workplace Level 2 port (benchmark 18-25)
      - ev_per_dcfc: ratio of EVs to one DC Fast Charger (benchmark 70-100)
      - avg_annual_miles: average miles driven per EV per year
      - avg_kwh_per_mile: grid electricity consumed per mile (accounting for charging losses)
      - peak_coincidence_factor: fraction of fleet charging simultaneously at peak grid hours
    """
    if forecast_df.empty:
        return pd.DataFrame()

    df = forecast_df.copy()

    # Charger Port Demand
    df["req_l2_ports"] = np.where(
        df["cumulative_fleet"] > 0,
        np.maximum(1, np.round(df["cumulative_fleet"] / max(1.0, ev_per_l2))).astype(int),
        0
    )
    df["req_dcfc_ports"] = np.where(
        df["cumulative_fleet"] > 0,
        np.maximum(1, np.round(df["cumulative_fleet"] / max(1.0, ev_per_dcfc))).astype(int),
        0
    )
    df["total_req_ports"] = df["req_l2_ports"] + df["req_dcfc_ports"]

    # Annual Energy Demand: Fleet * Miles * kWh/mile (converted to MWh and GWh)
    df["annual_energy_mwh"] = np.round(
        df["cumulative_fleet"] * avg_annual_miles * avg_kwh_per_mile / 1000.0, 1
    )
    df["annual_energy_gwh"] = (df["annual_energy_mwh"] / 1000.0).round(2)

    # Grid Peak Load:
    # Average charging power weighted: L2 ~ 9.6 kW, DCFC ~ 120 kW blended with home ~ 7.2 kW
    # Effective peak power demand in MW
    # Peak load MW = (Fleet * peak_coincidence_factor * avg_charging_power_kW) / 1000
    avg_peak_kw_per_charging_vehicle = 11.5
    df["peak_load_mw"] = np.round(
        df["cumulative_fleet"] * peak_coincidence_factor * avg_peak_kw_per_charging_vehicle / 1000.0, 1
    )

    # Gap Analysis against baseline
    df["l2_gap"] = np.maximum(0, df["req_l2_ports"] - current_l2_ports)
    df["dcfc_gap"] = np.maximum(0, df["req_dcfc_ports"] - current_dcfc_ports)
    df["total_ports_gap"] = df["l2_gap"] + df["dcfc_gap"]

    # Readiness Score (0% - 100%)
    total_req = np.maximum(1, df["total_req_ports"])
    installed_approx = current_l2_ports + current_dcfc_ports
    df["readiness_pct"] = np.clip(np.round((installed_approx / total_req) * 100, 1), 0.0, 100.0)

    return df


def generate_hourly_charging_load_profile(total_ev_fleet: int, avg_kwh_daily: float = 11.6) -> pd.DataFrame:
    """
    Simulates a 24-hour diurnal EV charging load profile (MW) for grid dispatch planning.
    Distinguishes Residential Night Charging, Workplace Day Charging, and Highway Fast Charging.
    """
    hours = np.arange(24)
    # 24-hour profile distribution weights (sum to 1.0)
    # Peak in late evening (20:00 - 23:00) from home charging, secondary bump at 09:00 - 11:00 from workplace
    weights = np.array([
        0.055, 0.045, 0.035, 0.025, 0.020, 0.025, # 00:00 - 05:00
        0.035, 0.050, 0.065, 0.060, 0.055, 0.050, # 06:00 - 11:00
        0.045, 0.040, 0.040, 0.045, 0.055, 0.065, # 12:00 - 17:00
        0.075, 0.085, 0.090, 0.085, 0.075, 0.060  # 18:00 - 23:00
    ])
    weights = weights / weights.sum()

    total_daily_mwh = (total_ev_fleet * avg_kwh_daily) / 1000.0
    hourly_mwh = total_daily_mwh * weights
    hourly_mw = hourly_mwh # 1 MWh in 1 hour = 1 MW average power

    residential_share = 0.65
    workplace_share = 0.20
    dcfc_highway_share = 0.15

    # Specific profile shapes
    res_weights = np.array([
        0.07, 0.06, 0.05, 0.04, 0.02, 0.01,
        0.01, 0.01, 0.02, 0.02, 0.02, 0.02,
        0.02, 0.02, 0.02, 0.03, 0.04, 0.06,
        0.09, 0.11, 0.12, 0.11, 0.09, 0.08
    ])
    res_weights = res_weights / res_weights.sum()

    work_weights = np.array([
        0.01, 0.01, 0.01, 0.01, 0.01, 0.02,
        0.04, 0.09, 0.14, 0.15, 0.14, 0.12,
        0.09, 0.06, 0.04, 0.03, 0.02, 0.01,
        0.01, 0.01, 0.01, 0.01, 0.01, 0.01
    ])
    work_weights = work_weights / work_weights.sum()

    highway_weights = np.array([
        0.01, 0.01, 0.01, 0.01, 0.01, 0.02,
        0.03, 0.04, 0.05, 0.06, 0.07, 0.08,
        0.08, 0.07, 0.07, 0.08, 0.09, 0.09,
        0.07, 0.06, 0.05, 0.04, 0.02, 0.01
    ])
    highway_weights = highway_weights / highway_weights.sum()

    res_mw = total_daily_mwh * residential_share * res_weights
    work_mw = total_daily_mwh * workplace_share * work_weights
    dcfc_mw = total_daily_mwh * dcfc_highway_share * highway_weights

    df_profile = pd.DataFrame({
        "Hour": hours,
        "Time_Label": [f"{h:02d}:00" for h in hours],
        "Residential_MW": np.round(res_mw, 2),
        "Workplace_MW": np.round(work_mw, 2),
        "DCFC_Public_MW": np.round(dcfc_mw, 2),
        "Total_Grid_Load_MW": np.round(res_mw + work_mw + dcfc_mw, 2)
    })

    return df_profile


def get_infrastructure_kpis(infra_df: pd.DataFrame, target_year: int = 2030) -> Dict[str, Any]:
    """
    Extracts high-level summary KPIs for a specific future target year.
    """
    if infra_df.empty:
        return {}

    target_row = infra_df[infra_df["year"] == target_year]
    if target_row.empty:
        target_row = infra_df.iloc[-1:]

    r = target_row.iloc[0]
    return {
        "target_year": int(r["year"]),
        "projected_fleet": int(r["cumulative_fleet"]),
        "req_l2": int(r["req_l2_ports"]),
        "req_dcfc": int(r["req_dcfc_ports"]),
        "total_ports": int(r["total_req_ports"]),
        "annual_energy_gwh": float(r["annual_energy_gwh"]),
        "peak_load_mw": float(r["peak_load_mw"]),
        "ports_gap": int(r["total_ports_gap"]),
        "readiness_pct": float(r["readiness_pct"])
    }

