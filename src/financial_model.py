"""
financial_model.py - EV market valuation, Total Cost of Ownership (TCO), charging revenue, and CapEx ROI.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any


def format_currency_inr(value: float, decimals: int = 0, suffix: str = "") -> str:
    """
    Format a numeric value using Indian rupee grouping, e.g. 485000 -> ₹4,85,000.
    """
    if value is None:
        value = 0

    numeric_value = float(value)
    sign = "-" if numeric_value < 0 else ""
    abs_value = abs(numeric_value)

    if decimals > 0:
        rounded = round(abs_value, decimals)
        int_part = int(rounded)
        fraction = str(round((rounded - int_part) * (10 ** decimals)))
        fraction = fraction.rjust(decimals, "0")
        return f"{sign}₹{format_currency_inr(int_part, 0)}.{fraction}{suffix}"

    integer_value = int(round(abs_value))
    s = str(integer_value)
    if len(s) <= 3:
        formatted = s
    else:
        last_three = s[-3:]
        rest = s[:-3]
        groups = []
        while len(rest) > 2:
            groups.append(rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.append(rest)
        groups.reverse()
        formatted = ",".join(groups + [last_three])

    return f"{sign}₹{formatted}{suffix}"


def calculate_financial_growth(
    forecast_df: pd.DataFrame,
    avg_ev_price: float = 48500.0,
    avg_charging_tariff_kwh: float = 0.32,
    wholesale_electricity_kwh: float = 0.13,
    l2_capex_per_port: float = 4500.0,
    dcfc_capex_per_port: float = 65000.0
) -> pd.DataFrame:
    """
    Calculates macro financial metrics: vehicle sales market size, public charging revenue,
    and cumulative infrastructure CapEx requirements.
    """
    if forecast_df.empty:
        return pd.DataFrame()

    df = forecast_df.copy()

    # 1. Annual Vehicle Market Value ($ Millions & Billions)
    df["annual_vehicle_sales_val_m"] = np.round((df["annual_additions"] * avg_ev_price) / 1e6, 2)
    df["cum_market_val_b"] = np.round((df["cumulative_fleet"] * avg_ev_price) / 1e9, 2)

    # 2. Charging Network Economics
    # Assuming ~30% of total charging energy happens on public/commercial networks
    public_kwh_share = 0.30
    if "annual_energy_mwh" in df.columns:
        df["public_energy_mwh"] = df["annual_energy_mwh"] * public_kwh_share
    else:
        # 12,500 miles * 0.34 kWh/mi = 4,250 kWh/year per EV
        df["public_energy_mwh"] = (df["cumulative_fleet"] * 12500 * 0.34 / 1000.0) * public_kwh_share

    df["public_energy_kwh"] = df["public_energy_mwh"] * 1000.0

    # Gross Charging Revenue ($ Millions)
    df["charging_revenue_m"] = np.round((df["public_energy_kwh"] * avg_charging_tariff_kwh) / 1e6, 2)
    df["charging_electricity_cost_m"] = np.round((df["public_energy_kwh"] * wholesale_electricity_kwh) / 1e6, 2)
    df["charging_gross_profit_m"] = np.round(df["charging_revenue_m"] - df["charging_electricity_cost_m"], 2)

    # 3. Infrastructure CapEx Requirement to meet ports demand
    req_l2 = df["req_l2_ports"] if "req_l2_ports" in df.columns else (df["cumulative_fleet"] / 22.0)
    req_dcfc = df["req_dcfc_ports"] if "req_dcfc_ports" in df.columns else (df["cumulative_fleet"] / 85.0)

    df["cum_l2_capex_m"] = np.round((req_l2 * l2_capex_per_port) / 1e6, 2)
    df["cum_dcfc_capex_m"] = np.round((req_dcfc * dcfc_capex_per_port) / 1e6, 2)
    df["total_infra_capex_m"] = df["cum_l2_capex_m"] + df["cum_dcfc_capex_m"]

    return df


def calculate_tco_comparison(
    years_ownership: int = 10,
    annual_miles: float = 12500.0,
    ev_purchase_price: float = 46000.0,
    ev_tax_credit: float = 7500.0,
    ice_purchase_price: float = 38000.0,
    gas_price_per_gallon: float = 3.65,
    ice_mpg: float = 28.0,
    ev_efficiency_mi_per_kwh: float = 3.3,
    electricity_price_kwh: float = 0.16,
    annual_ev_maintenance: float = 550.0,
    annual_ice_maintenance: float = 1150.0
) -> pd.DataFrame:
    """
    Computes year-by-year Total Cost of Ownership (TCO) comparing Electric Vehicle vs Gas (ICE) Car.
    """
    timeline = np.arange(1, years_ownership + 1)

    # Initial Net Purchase Cost
    net_ev_initial = ev_purchase_price - ev_tax_credit
    net_ice_initial = ice_purchase_price

    # Annual Operating Costs
    # Fuel
    ice_annual_fuel = (annual_miles / ice_mpg) * gas_price_per_gallon
    ev_annual_electricity = (annual_miles / ev_efficiency_mi_per_kwh) * electricity_price_kwh
    annual_fuel_savings = ice_annual_fuel - ev_annual_electricity

    # Maintenance
    annual_maint_savings = annual_ice_maintenance - annual_ev_maintenance

    # Depreciation estimation (~12% per year reducing balance)
    ev_depreciation_rates = np.array([0.18, 0.15, 0.12, 0.10, 0.09, 0.08, 0.07, 0.06, 0.05, 0.05][:years_ownership])
    ice_depreciation_rates = np.array([0.17, 0.14, 0.12, 0.10, 0.09, 0.08, 0.07, 0.06, 0.05, 0.05][:years_ownership])

    cum_ev_tco = []
    cum_ice_tco = []
    cum_savings = []

    running_ev = net_ev_initial
    running_ice = net_ice_initial

    for yr in range(years_ownership):
        running_ev += (ev_annual_electricity + annual_ev_maintenance)
        running_ice += (ice_annual_fuel + annual_ice_maintenance)
        cum_ev_tco.append(round(running_ev, 2))
        cum_ice_tco.append(round(running_ice, 2))
        cum_savings.append(round(running_ice - running_ev, 2))

    tco_df = pd.DataFrame({
        "Year": timeline,
        "EV_Cumulative_TCO": cum_ev_tco,
        "ICE_Cumulative_TCO": cum_ice_tco,
        "Cumulative_Savings_EV": cum_savings,
        "Annual_Fuel_Savings": round(annual_fuel_savings, 2),
        "Annual_Maintenance_Savings": round(annual_maint_savings, 2),
        "Total_Annual_Operating_Savings": round(annual_fuel_savings + annual_maint_savings, 2)
    })

    # Find breakeven year
    positive_savings = tco_df[tco_df["Cumulative_Savings_EV"] >= 0]
    breakeven_year = positive_savings.iloc[0]["Year"] if not positive_savings.empty else "10+"
    tco_df.attrs["breakeven_year"] = breakeven_year

    return tco_df


def get_financial_kpis(fin_df: pd.DataFrame, target_year: int = 2030) -> Dict[str, Any]:
    """
    Extracts key economic and financial indicators for target projection year.
    """
    if fin_df.empty:
        return {}

    target_row = fin_df[fin_df["year"] == target_year]
    if target_row.empty:
        target_row = fin_df.iloc[-1:]

    r = target_row.iloc[0]
    return {
        "target_year": int(r["year"]),
        "annual_sales_m": float(r["annual_vehicle_sales_val_m"]),
        "cum_market_b": float(r["cum_market_val_b"]),
        "charging_revenue_m": float(r["charging_revenue_m"]),
        "charging_profit_m": float(r["charging_gross_profit_m"]),
        "total_capex_m": float(r["total_infra_capex_m"])
    }

