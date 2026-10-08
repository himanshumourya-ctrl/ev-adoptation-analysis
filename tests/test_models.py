"""
test_models.py - Unit test suite for EV Adoption, Infrastructure, Financial, and Sentiment models.
"""

import unittest
from pathlib import Path
import pandas as pd
import numpy as np

from src.data_loader import (
    normalize_columns,
    clean_ev_dataset,
    generate_benchmark_datasets
)
from src.ev_growth_model import (
    get_historical_metrics,
    forecast_ev_adoption
)
from src.infrastructure_model import (
    calculate_infrastructure_requirements,
    generate_hourly_charging_load_profile,
    get_infrastructure_kpis
)
from src.financial_model import (
    calculate_financial_growth,
    calculate_tco_comparison,
    get_financial_kpis,
    format_currency_inr
)
from src.charging_points import (
    STATIONS,
    build_google_maps_directions,
    get_nearest_stations,
    haversine_km,
    normalize_user_location,
)
from src.feedback_analyzer import (
    analyze_customer_feedback,
    analyze_sentiment_rule
)


class TestEVAnalyticsApp(unittest.TestCase):

    def setUp(self):
        # Generate datasets if not existing
        self.ev_path, self.infra_path, self.feedback_path = generate_benchmark_datasets()
        self.ev_df = pd.read_csv(self.ev_path)
        self.infra_df = pd.read_csv(self.infra_path)
        self.feedback_df = pd.read_csv(self.feedback_path)

    def test_data_cleaning_and_normalization(self):
        cleaned = clean_ev_dataset(self.ev_df)
        self.assertIn("model_year", cleaned.columns)
        self.assertIn("ev_type", cleaned.columns)
        self.assertIn("electric_range", cleaned.columns)
        self.assertIn("base_msrp", cleaned.columns)
        self.assertTrue((cleaned["model_year"] >= 2010).all())
        self.assertTrue((cleaned["electric_range"] > 0).all())

    def test_historical_metrics(self):
        cleaned = clean_ev_dataset(self.ev_df)
        metrics = get_historical_metrics(cleaned)
        self.assertIn("yearly_data", metrics)
        self.assertIn("top_makes", metrics)
        self.assertIn("cagr", metrics)
        self.assertGreater(metrics["total_active_fleet"], 1000)
        self.assertGreater(metrics["cagr"], 0)

    def test_ev_forecasting(self):
        cleaned = clean_ev_dataset(self.ev_df)
        metrics = get_historical_metrics(cleaned)
        yearly = metrics["yearly_data"]
        
        # Test Bass Diffusion
        forecast_bass = forecast_ev_adoption(yearly, target_year=2030, scenario="Baseline", model_type="Bass Diffusion")
        self.assertFalse(forecast_bass.empty)
        self.assertIn("cumulative_fleet", forecast_bass.columns)
        self.assertIn("annual_additions", forecast_bass.columns)
        # Fleet should be monotonically increasing
        self.assertTrue((np.diff(forecast_bass["cumulative_fleet"]) >= 0).all())

        # Test Polynomial Regression
        forecast_poly = forecast_ev_adoption(yearly, target_year=2030, scenario="Aggressive (Net-Zero Push)", model_type="Polynomial Regression")
        self.assertFalse(forecast_poly.empty)
        self.assertGreater(forecast_poly.iloc[-1]["cumulative_fleet"], forecast_poly.iloc[0]["cumulative_fleet"])

    def test_infrastructure_requirements(self):
        cleaned = clean_ev_dataset(self.ev_df)
        metrics = get_historical_metrics(cleaned)
        forecast = forecast_ev_adoption(metrics["yearly_data"], target_year=2030)
        
        infra = calculate_infrastructure_requirements(forecast, current_l2_ports=20000, current_dcfc_ports=5000)
        self.assertIn("req_l2_ports", infra.columns)
        self.assertIn("req_dcfc_ports", infra.columns)
        self.assertIn("annual_energy_gwh", infra.columns)
        self.assertIn("peak_load_mw", infra.columns)
        self.assertTrue((infra["req_l2_ports"] > 0).all())

        kpis = get_infrastructure_kpis(infra, target_year=2030)
        self.assertEqual(kpis["target_year"], 2030)
        self.assertGreater(kpis["projected_fleet"], 0)

    def test_diurnal_grid_load_profile(self):
        profile = generate_hourly_charging_load_profile(100000)
        self.assertEqual(len(profile), 24)
        self.assertIn("Total_Grid_Load_MW", profile.columns)
        self.assertIn("Residential_MW", profile.columns)
        self.assertTrue((profile["Total_Grid_Load_MW"] > 0).all())

    def test_financial_and_tco_model(self):
        cleaned = clean_ev_dataset(self.ev_df)
        metrics = get_historical_metrics(cleaned)
        forecast = forecast_ev_adoption(metrics["yearly_data"], target_year=2030)
        infra = calculate_infrastructure_requirements(forecast)
        
        fin = calculate_financial_growth(infra)
        self.assertIn("charging_revenue_m", fin.columns)
        self.assertIn("cum_market_val_b", fin.columns)
        self.assertIn("total_infra_capex_m", fin.columns)

        tco = calculate_tco_comparison(years_ownership=10)
        self.assertEqual(len(tco), 10)
        self.assertIn("EV_Cumulative_TCO", tco.columns)
        self.assertIn("Cumulative_Savings_EV", tco.columns)
        self.assertTrue(tco.iloc[-1]["Cumulative_Savings_EV"] > 0) # EV should save over 10 years

    def test_currency_formatting_uses_rupees(self):
        self.assertEqual(format_currency_inr(485000), "₹4,85,000")
        self.assertEqual(format_currency_inr(4850000, suffix="/year"), "₹48,50,000/year")

    def test_nearest_charging_stations_and_directions(self):
        closest = get_nearest_stations(12.9716, 77.5946, limit=3)
        self.assertEqual(len(closest), 3)
        self.assertLess(closest[0]["distance_km"], closest[1]["distance_km"])
        self.assertIn("Bengaluru Green Hub", closest[0]["name"])
        self.assertTrue(build_google_maps_directions(12.9716, 77.5946, STATIONS[0]["latitude"], STATIONS[0]["longitude"]).startswith("https://www.google.com/maps/dir/"))
        self.assertGreater(haversine_km(12.9716, 77.5946, 13.0827, 80.2707), 0)

    def test_user_location_payload_is_normalized_for_charging_page(self):
        valid = normalize_user_location({"lat": 19.0760, "lon": 72.8777, "error": None})
        self.assertEqual(valid["lat"], 19.0760)
        self.assertEqual(valid["lon"], 72.8777)
        self.assertIsNone(valid["error"])

        aliased = normalize_user_location({"latitude": 19.0760, "longitude": 72.8777, "error": None})
        self.assertEqual(aliased["lat"], 19.0760)
        self.assertEqual(aliased["lon"], 72.8777)
        self.assertIsNone(aliased["error"])

        blocked = normalize_user_location({"lat": None, "lon": None, "error": "Location access was denied."})
        self.assertIsNone(blocked["lat"])
        self.assertIsNone(blocked["lon"])
        self.assertEqual(blocked["error"], "Location access was denied.")

    def test_default_charging_fallback_uses_asansol_and_india_stations(self):
        fallback = get_nearest_stations(limit=5)
        self.assertGreater(len(STATIONS), 10)
        self.assertAlmostEqual(fallback[0]["latitude"], 23.6739, places=3)
        self.assertAlmostEqual(fallback[0]["longitude"], 86.9524, places=3)
        self.assertAlmostEqual(fallback[0]["distance_km"], 0.0, places=1)

    def test_customer_feedback_sentiment(self):
        res = analyze_customer_feedback(self.feedback_df)
        self.assertIn("avg_rating", res)
        self.assertIn("nps", res)
        self.assertIn("sentiment_distribution", res)
        self.assertIn("category_summary", res)
        self.assertIn("recommendations", res)
        self.assertGreater(res["total_reviews"], 0)
        self.assertGreaterEqual(res["avg_rating"], 1.0)
        self.assertLessEqual(res["avg_rating"], 5.0)

    def test_geo_locator_component_posts_ready_and_value_messages(self):
        component_html_path = Path(__file__).resolve().parents[1] / "components" / "geo_locator" / "index.html"
        html = component_html_path.read_text(encoding="utf-8")

        self.assertIn("streamlit:componentReady", html)
        self.assertIn("streamlit:componentValue", html)
        self.assertIn("window.parent.postMessage", html)


if __name__ == "__main__":
    unittest.main()

