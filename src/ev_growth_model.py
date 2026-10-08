"""
ev_growth_model.py - Historical analysis, Bass Diffusion modeling, and ML growth forecasting for Electric Vehicles.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from scipy.optimize import curve_fit


def get_historical_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes historical EV adoption metrics from the dataset.
    """
    if "model_year" not in df.columns:
        return {}

    yearly = df.groupby("model_year").agg(
        total_vehicles=("model_year", "count"),
        bev_count=("ev_type", lambda s: (s == "Battery Electric Vehicle (BEV)").sum()),
        phev_count=("ev_type", lambda s: (s == "Plug-in Hybrid (PHEV)").sum()),
        avg_range=("electric_range", "mean"),
        avg_price=("base_msrp", "mean")
    ).reset_index().rename(columns={"model_year": "year"})

    yearly["bev_pct"] = (yearly["bev_count"] / yearly["total_vehicles"] * 100).round(1)
    yearly["phev_pct"] = (yearly["phev_count"] / yearly["total_vehicles"] * 100).round(1)
    yearly["cumulative_fleet"] = yearly["total_vehicles"].cumsum()
    yearly["yoy_growth"] = yearly["total_vehicles"].pct_change() * 100

    # Top Makes
    top_makes = df["make"].value_counts().head(8).reset_index()
    top_makes.columns = ["Make", "Count"]
    top_makes["Percentage"] = (top_makes["Count"] / len(df) * 100).round(1)

    # Top Models
    top_models = df.groupby(["make", "model"]).size().reset_index(name="Count")
    top_models = top_models.sort_values(by="Count", ascending=False).head(10)
    top_models["Vehicle"] = top_models["make"] + " " + top_models["model"]

    # Geographical breakdown
    geo_col = "county" if "county" in df.columns else ("city" if "city" in df.columns else None)
    if geo_col:
        geo_distribution = df[geo_col].value_counts().head(12).reset_index()
        geo_distribution.columns = [geo_col.capitalize(), "Count"]
    else:
        geo_distribution = pd.DataFrame()

    total_fleet = len(df)
    latest_year = yearly["year"].max() if not yearly.empty else 2024
    earliest_year = yearly["year"].min() if not yearly.empty else 2015

    # Calculate CAGR
    years_span = max(1, latest_year - earliest_year)
    start_val = yearly.iloc[0]["total_vehicles"] if not yearly.empty else 1
    end_val = yearly.iloc[-1]["total_vehicles"] if not yearly.empty else 1
    cagr = ((end_val / max(1, start_val)) ** (1 / years_span) - 1) * 100 if start_val > 0 else 0.0

    return {
        "yearly_data": yearly,
        "top_makes": top_makes,
        "top_models": top_models,
        "geo_distribution": geo_distribution,
        "total_active_fleet": total_fleet,
        "latest_year": latest_year,
        "earliest_year": earliest_year,
        "cagr": round(cagr, 1)
    }


def bass_diffusion_cumulative(t: np.ndarray, M: float, p: float, q: float) -> np.ndarray:
    """
    Standard cumulative Bass Diffusion Model formula.
    t: relative time (years from start, t >= 0)
    M: total potential market size (fleet capacity)
    p: coefficient of innovation
    q: coefficient of imitation
    """
    val = (1.0 - np.exp(-(p + q) * t)) / (1.0 + (q / max(1e-6, p)) * np.exp(-(p + q) * t))
    return M * np.clip(val, 0, 1.0)


def forecast_ev_adoption(
    yearly_df: pd.DataFrame,
    target_year: int = 2035,
    scenario: str = "Baseline",
    market_capacity_multiplier: float = 3.5,
    model_type: str = "Bass Diffusion"
) -> pd.DataFrame:
    """
    Forecasts annual and cumulative EV adoption up to target_year under different scenarios.
    Scenarios:
      - 'Baseline': Empirical trajectory
      - 'Aggressive (Net-Zero / Fast Transition)': +30% acceleration
      - 'Conservative (High Interest / Grid Constraints)': -25% deceleration
    """
    if yearly_df.empty or len(yearly_df) < 3:
        # Fallback if too few rows
        return pd.DataFrame()

    years_hist = yearly_df["year"].values
    cum_hist = yearly_df["cumulative_fleet"].values
    annual_hist = yearly_df["total_vehicles"].values

    start_year = int(years_hist[0])
    last_hist_year = int(years_hist[-1])
    future_years = np.arange(last_hist_year + 1, target_year + 1)
    all_years = np.arange(start_year, target_year + 1)

    t_hist = years_hist - start_year
    t_all = all_years - start_year

    # Scenario adjustment factors
    scenario_multipliers = {
        "Conservative": 0.75,
        "Baseline": 1.0,
        "Aggressive (Net-Zero Push)": 1.32
    }
    multiplier = scenario_multipliers.get(scenario, 1.0)

    # 1. Bass Diffusion Fitting
    cum_forecast = np.zeros(len(all_years))
    annual_forecast = np.zeros(len(all_years))

    if model_type == "Bass Diffusion":
        # Initial estimate for market capacity M
        current_cum = cum_hist[-1]
        m_est = current_cum * market_capacity_multiplier * multiplier

        # Bounds for Bass parameters: M > current_cum, p in [0.001, 0.05], q in [0.15, 0.8]
        try:
            popt, _ = curve_fit(
                bass_diffusion_cumulative,
                t_hist + 1.0,
                cum_hist,
                p0=[m_est, 0.015, 0.38],
                bounds=([current_cum * 1.05, 0.001, 0.10], [m_est * 4.0, 0.08, 0.90]),
                maxfev=5000
            )
            M_fit, p_fit, q_fit = popt
            M_fit = M_fit * multiplier
            cum_curve = bass_diffusion_cumulative(t_all + 1.0, M_fit, p_fit, q_fit)
        except Exception:
            # Analytical fallback with calibrated coefficients
            M_val = current_cum * market_capacity_multiplier * multiplier
            cum_curve = bass_diffusion_cumulative(t_all + 1.0, M_val, 0.018, 0.35)

        # Preserve exact historical points and ensure monotonically increasing forecast
        n_hist = len(cum_hist)
        bridge_offset = cum_hist[-1] - cum_curve[n_hist - 1]
        for idx, yr in enumerate(all_years):
            if idx < n_hist:
                cum_curve[idx] = cum_hist[idx]
            else:
                cum_curve[idx] = max(cum_curve[idx - 1] + 50, cum_curve[idx] + bridge_offset)

        cum_forecast = cum_curve
        annual_forecast[0] = annual_hist[0]
        annual_forecast[1:n_hist] = annual_hist[1:n_hist]
        annual_forecast[n_hist:] = np.diff(cum_forecast)[n_hist - 1:]

    else:
        # Polynomial Ridge Regression
        poly_model = make_pipeline(
            PolynomialFeatures(degree=2, include_bias=False),
            Ridge(alpha=1.0)
        )
        poly_model.fit(years_hist.reshape(-1, 1), cum_hist)
        cum_preds = poly_model.predict(all_years.reshape(-1, 1))

        # Adjust future values based on scenario
        for idx, yr in enumerate(all_years):
            if yr > last_hist_year:
                added_growth = (cum_preds[idx] - cum_preds[idx - 1]) * multiplier
                cum_preds[idx] = max(cum_preds[idx - 1] + 10, cum_preds[idx - 1] + added_growth)
            else:
                cum_preds[idx] = cum_hist[idx] if idx < len(cum_hist) else cum_preds[idx]

        cum_forecast = cum_preds
        annual_forecast[0] = cum_forecast[0]
        annual_forecast[1:] = np.diff(cum_forecast)

    # Compile into clean output DataFrame
    forecast_df = pd.DataFrame({
        "year": all_years,
        "cumulative_fleet": np.round(cum_forecast).astype(int),
        "annual_additions": np.round(annual_forecast).astype(int),
        "is_forecast": all_years > last_hist_year
    })

    # Add lower and upper confidence bounds (±8% baseline, widening for future years)
    years_ahead = np.maximum(0, all_years - last_hist_year)
    uncertainty = 0.04 + 0.02 * years_ahead
    forecast_df["fleet_lower_bound"] = np.round(forecast_df["cumulative_fleet"] * (1 - uncertainty)).astype(int)
    forecast_df["fleet_upper_bound"] = np.round(forecast_df["cumulative_fleet"] * (1 + uncertainty)).astype(int)

    # Estimate BEV share growth (rising from current ~70-75% to 88-92% by 2035)
    bev_base_pct = yearly_df.iloc[-1]["bev_pct"] if "bev_pct" in yearly_df.columns else 75.0
    bev_share = []
    for yr in all_years:
        if yr <= last_hist_year:
            hist_match = yearly_df[yearly_df["year"] == yr]
            val = hist_match["bev_pct"].values[0] if not hist_match.empty else bev_base_pct
            bev_share.append(val)
        else:
            diff = yr - last_hist_year
            projected = min(94.0, bev_base_pct + diff * 1.5)
            bev_share.append(round(projected, 1))

    forecast_df["bev_pct"] = bev_share
    forecast_df["phev_pct"] = (100.0 - np.array(bev_share)).round(1)

    return forecast_df

