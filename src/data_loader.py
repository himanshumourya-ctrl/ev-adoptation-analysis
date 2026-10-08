"""
data_loader.py - Ingestion, schema normalization, and benchmark dataset generator for EV Analytics.
"""

import os
import io
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

COLUMN_SYNONYMS = {
    "model_year": ["model year", "modelyear", "year", "registration year", "reg_year", "model_yr"],
    "make": ["make", "manufacturer", "brand", "vehicle_make", "car_make"],
    "model": ["model", "vehicle_model", "car_model"],
    "ev_type": ["electric vehicle type", "ev type", "ev_type", "vehicle type", "powertrain", "type"],
    "electric_range": ["electric range", "range", "range_miles", "range (mi)", "range_km", "battery range"],
    "base_msrp": ["base msrp", "msrp", "price", "base_price", "cost", "vehicle_price"],
    "state": ["state", "province", "region"],
    "county": ["county", "district", "area"],
    "city": ["city", "town", "municipality"]
}


def normalize_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Standardize DataFrame column names using fuzzy synonyms matching.
    Returns normalized DataFrame and mapping dictionary.
    """
    normalized_df = df.copy()
    raw_cols = {col: col.strip().lower().replace("_", " ") for col in df.columns}
    col_mapping = {}

    for standard_name, synonyms in COLUMN_SYNONYMS.items():
        matched = None
        for raw_col, clean_name in raw_cols.items():
            if clean_name in synonyms:
                matched = raw_col
                break
        if not matched:
            for raw_col, clean_name in raw_cols.items():
                if any(syn in clean_name for syn in synonyms):
                    matched = raw_col
                    break
        if matched:
            col_mapping[matched] = standard_name

    normalized_df = normalized_df.rename(columns=col_mapping)
    return normalized_df, col_mapping


def clean_ev_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans EV dataset, filling missing values and ensuring typed columns.
    """
    df, _ = normalize_columns(df)

    # Model Year cleanup
    if "model_year" in df.columns:
        df["model_year"] = pd.to_numeric(df["model_year"], errors="coerce")
        df = df.dropna(subset=["model_year"])
        df["model_year"] = df["model_year"].astype(int)
        # Filter realistic years
        df = df[(df["model_year"] >= 2010) & (df["model_year"] <= 2026)]

    # EV Type classification standardizing
    if "ev_type" in df.columns:
        def standardize_type(val):
            val_str = str(val).upper()
            if "PLUG-IN" in val_str or "PHEV" in val_str or "HYBRID" in val_str:
                return "Plug-in Hybrid (PHEV)"
            return "Battery Electric Vehicle (BEV)"
        df["ev_type"] = df["ev_type"].apply(standardize_type)
    else:
        df["ev_type"] = "Battery Electric Vehicle (BEV)"

    # Electric Range cleanup
    if "electric_range" in df.columns:
        df["electric_range"] = pd.to_numeric(df["electric_range"], errors="coerce")
        # Impute 0 or missing with typical range based on type
        bev_median = df[df["ev_type"] == "Battery Electric Vehicle (BEV)"]["electric_range"].replace(0, np.nan).median()
        phev_median = df[df["ev_type"] == "Plug-in Hybrid (PHEV)"]["electric_range"].replace(0, np.nan).median()
        bev_median = 240.0 if np.isnan(bev_median) or bev_median == 0 else bev_median
        phev_median = 35.0 if np.isnan(phev_median) or phev_median == 0 else phev_median

        def impute_range(row):
            r = row.get("electric_range", np.nan)
            if pd.isna(r) or r <= 0:
                return bev_median if row["ev_type"] == "Battery Electric Vehicle (BEV)" else phev_median
            return r
        df["electric_range"] = df.apply(impute_range, axis=1)
    else:
        df["electric_range"] = np.where(df["ev_type"] == "Battery Electric Vehicle (BEV)", 250.0, 38.0)

    # Make & Model
    if "make" in df.columns:
        df["make"] = df["make"].astype(str).str.strip().str.upper()
    else:
        df["make"] = "UNKNOWN"

    if "model" in df.columns:
        df["model"] = df["model"].astype(str).str.strip().str.title()
    else:
        df["model"] = "Unknown Model"

    # Base MSRP
    if "base_msrp" in df.columns:
        df["base_msrp"] = pd.to_numeric(df["base_msrp"], errors="coerce")
        # Impute missing with standard industry estimates
        median_msrp = df["base_msrp"].replace(0, np.nan).median()
        df["base_msrp"] = df["base_msrp"].replace(0, np.nan).fillna(median_msrp if not np.isnan(median_msrp) else 48000.0)
    else:
        df["base_msrp"] = 49500.0

    return df


def generate_benchmark_datasets(force: bool = False) -> Tuple[str, str, str]:
    """
    Generates realistic EV adoption, infrastructure, and customer feedback benchmark datasets.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    ev_path = os.path.join(DATA_DIR, "sample_ev_dataset.csv")
    infra_path = os.path.join(DATA_DIR, "charging_infrastructure.csv")
    feedback_path = os.path.join(DATA_DIR, "customer_feedback.csv")

    if not force and os.path.exists(ev_path) and os.path.exists(infra_path) and os.path.exists(feedback_path):
        return ev_path, infra_path, feedback_path

    np.random.seed(42)

    # 1. Generate EV Fleet Dataset (12,000 realistic records from 2015 to 2024)
    years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    year_weights = [0.03, 0.04, 0.06, 0.08, 0.11, 0.13, 0.16, 0.18, 0.20, 0.21]
    year_weights = np.array(year_weights) / sum(year_weights)

    makes_models = [
        ("TESLA", "Model 3", "Battery Electric Vehicle (BEV)", 272, 41000),
        ("TESLA", "Model Y", "Battery Electric Vehicle (BEV)", 310, 48000),
        ("TESLA", "Model S", "Battery Electric Vehicle (BEV)", 405, 88000),
        ("CHEVROLET", "Bolt EV", "Battery Electric Vehicle (BEV)", 259, 29000),
        ("FORD", "Mustang Mach-E", "Battery Electric Vehicle (BEV)", 290, 45000),
        ("FORD", "F-150 Lightning", "Battery Electric Vehicle (BEV)", 240, 56000),
        ("HYUNDAI", "Ioniq 5", "Battery Electric Vehicle (BEV)", 303, 44000),
        ("KIA", "EV6", "Battery Electric Vehicle (BEV)", 310, 46000),
        ("VOLKSWAGEN", "ID.4", "Battery Electric Vehicle (BEV)", 275, 41500),
        ("NISSAN", "Leaf", "Battery Electric Vehicle (BEV)", 212, 31000),
        ("RIVIAN", "R1T", "Battery Electric Vehicle (BEV)", 328, 73000),
        ("BMW", "i4", "Battery Electric Vehicle (BEV)", 301, 54000),
        ("TOYOTA", "Prius Prime", "Plug-in Hybrid (PHEV)", 44, 33500),
        ("TOYOTA", "RAV4 Prime", "Plug-in Hybrid (PHEV)", 42, 44000),
        ("JEEP", "Wrangler 4xe", "Plug-in Hybrid (PHEV)", 22, 54000),
        ("CHRYSLER", "Pacifica Hybrid", "Plug-in Hybrid (PHEV)", 32, 51000),
        ("BMW", "330e", "Plug-in Hybrid (PHEV)", 23, 46000),
        ("VOLVO", "XC90 Recharge", "Plug-in Hybrid (PHEV)", 36, 73000)
    ]
    model_probs = [
        0.22, 0.25, 0.05, 0.07, 0.06, 0.04, 0.05, 0.04, 0.04, 0.03,
        0.02, 0.02, 0.03, 0.03, 0.02, 0.01, 0.01, 0.01
    ]
    model_probs = np.array(model_probs) / sum(model_probs)

    count = 12000
    chosen_years = np.random.choice(years, size=count, p=year_weights)
    chosen_indices = np.random.choice(len(makes_models), size=count, p=model_probs)

    counties = ["King", "Snohomish", "Pierce", "Clark", "Thurston", "Kitsap", "Whatcom", "Spokane", "Benton", "Yakima"]
    county_weights = [0.46, 0.16, 0.12, 0.08, 0.05, 0.04, 0.03, 0.03, 0.02, 0.01]
    county_weights = np.array(county_weights) / sum(county_weights)
    chosen_counties = np.random.choice(counties, size=count, p=county_weights)

    data_rows = []
    for i in range(count):
        y = int(chosen_years[i])
        idx = chosen_indices[i]
        make, model, ev_t, base_r, base_p = makes_models[idx]
        
        # Add realistic noise/evolution to range and price
        year_factor = (y - 2015) / 10.0
        # older cars had slightly lower range
        adjusted_range = max(15, int(base_r * (0.82 + 0.22 * year_factor) + np.random.normal(0, 8)))
        # inflation/spec changes
        adjusted_price = max(20000, int(base_p * (0.90 + 0.15 * year_factor) + np.random.normal(0, 1500)))

        vin_prefix = f"{np.random.choice(['5YJ', '1FT', '1G1', 'KMH', 'WA1', 'JN1', '7JR', 'WBA'])}{y%100}{np.random.randint(1000, 9999)}"
        data_rows.append({
            "VIN (1-10)": vin_prefix,
            "County": chosen_counties[i],
            "City": f"{chosen_counties[i]} Metro",
            "State": "WA",
            "Model Year": y,
            "Make": make,
            "Model": model,
            "Electric Vehicle Type": ev_t,
            "Electric Range": adjusted_range,
            "Base MSRP": adjusted_price
        })

    ev_df = pd.DataFrame(data_rows)
    ev_df.to_csv(ev_path, index=False)

    # 2. Generate Charging Infrastructure Historical Dataset (2015 to 2024)
    infra_records = [
        {"Year": 2015, "Level_2_Ports": 1420, "DC_Fast_Ports": 280, "Public_Stations": 620, "Private_Stations": 210, "Total_Energy_MWh": 14200, "Grid_Peak_MW": 18.5},
        {"Year": 2016, "Level_2_Ports": 1950, "DC_Fast_Ports": 390, "Public_Stations": 850, "Private_Stations": 290, "Total_Energy_MWh": 21300, "Grid_Peak_MW": 26.2},
        {"Year": 2017, "Level_2_Ports": 2780, "DC_Fast_Ports": 560, "Public_Stations": 1210, "Private_Stations": 410, "Total_Energy_MWh": 32800, "Grid_Peak_MW": 39.4},
        {"Year": 2018, "Level_2_Ports": 3900, "DC_Fast_Ports": 820, "Public_Stations": 1690, "Private_Stations": 580, "Total_Energy_MWh": 51200, "Grid_Peak_MW": 58.1},
        {"Year": 2019, "Level_2_Ports": 5420, "DC_Fast_Ports": 1240, "Public_Stations": 2340, "Private_Stations": 830, "Total_Energy_MWh": 79400, "Grid_Peak_MW": 87.6},
        {"Year": 2020, "Level_2_Ports": 7210, "DC_Fast_Ports": 1780, "Public_Stations": 3120, "Private_Stations": 1140, "Total_Energy_MWh": 118500, "Grid_Peak_MW": 128.0},
        {"Year": 2021, "Level_2_Ports": 9950, "DC_Fast_Ports": 2620, "Public_Stations": 4350, "Private_Stations": 1620, "Total_Energy_MWh": 182000, "Grid_Peak_MW": 191.5},
        {"Year": 2022, "Level_2_Ports": 13800, "DC_Fast_Ports": 3850, "Public_Stations": 6050, "Private_Stations": 2310, "Total_Energy_MWh": 274000, "Grid_Peak_MW": 282.4},
        {"Year": 2023, "Level_2_Ports": 19400, "DC_Fast_Ports": 5700, "Public_Stations": 8450, "Private_Stations": 3320, "Total_Energy_MWh": 408000, "Grid_Peak_MW": 415.0},
        {"Year": 2024, "Level_2_Ports": 26500, "DC_Fast_Ports": 8200, "Public_Stations": 11600, "Private_Stations": 4700, "Total_Energy_MWh": 595000, "Grid_Peak_MW": 598.2}
    ]
    infra_df = pd.DataFrame(infra_records)
    infra_df.to_csv(infra_path, index=False)

    # 3. Generate Customer Feedback & Sentiment Dataset (650 realistic reviews)
    feedback_templates = [
        # Range Anxiety
        (5, "Range Anxiety", "Battery range exceeded my expectations on long highway road trips. Easily get 300+ miles.", "Positive"),
        (4, "Range Anxiety", "Range drops around 20% during freezing winter months, but still plenty for my 50-mile daily commute.", "Positive"),
        (2, "Range Anxiety", "Winter range penalty is severe and makes road trips stressful with unexpected detours.", "Negative"),
        (1, "Range Anxiety", "Constant anxiety when driving across rural corridors where no fast chargers are present.", "Negative"),
        (3, "Range Anxiety", "Range is acceptable in city conditions, but highway speeds drain the battery much faster than rated.", "Neutral"),
        # Charging Infrastructure
        (5, "Charging Infrastructure", "The fast charging network has expanded tremendously. Plug and charge works seamlessly.", "Positive"),
        (4, "Charging Infrastructure", "Home Level 2 charging is an absolute game-changer. I wake up with a full tank every morning.", "Positive"),
        (1, "Charging Infrastructure", "Arrived at a highway charging plaza with 3 out of 4 stalls broken and a 45-minute queue.", "Negative"),
        (2, "Charging Infrastructure", "Public chargers frequently suffer from payment card reader failures and degraded charging speeds.", "Negative"),
        (3, "Charging Infrastructure", "Plenty of slow destination chargers, but high-speed 150kW+ chargers are lacking along state highways.", "Neutral"),
        # Price & Value
        (5, "Price & Financial Value", "Saved over $2,400 in gasoline and oil changes in my first year alone! Extremely cost effective.", "Positive"),
        (4, "Price & Financial Value", "Federal and state clean vehicle tax incentives made this EV cheaper upfront than a gas equivalent.", "Positive"),
        (2, "Price & Financial Value", "Initial purchase price is still too premium for mass adoption without government subsidies.", "Negative"),
        (1, "Price & Financial Value", "Insurance premiums and tire replacement costs are notably higher than my previous gas car.", "Negative"),
        (3, "Price & Financial Value", "Higher upfront cost balanced out by low electricity rates, but tire wear is noticeable due to vehicle weight.", "Neutral"),
        # Driving Performance & Tech
        (5, "Driving Performance & Tech", "Instant torque and single-pedal driving make this the best driving vehicle I have ever owned.", "Positive"),
        (5, "Driving Performance & Tech", "Over-the-air software updates continue to add valuable navigation and battery preconditioning features.", "Positive"),
        (4, "Driving Performance & Tech", "Whisper quiet cabin, low center of gravity, and effortless acceleration.", "Positive"),
        (2, "Driving Performance & Tech", "Touchscreen lag and lack of tactile climate control buttons are distracting and irritating.", "Negative"),
        (3, "Driving Performance & Tech", "Great driving dynamics, but phone projection occasionally disconnects after firmware updates.", "Neutral"),
        # Battery Health & Reliability
        (5, "Battery & Reliability", "After 60,000 miles, battery degradation is under 3%. Extremely impressed with thermal management.", "Positive"),
        (4, "Battery & Reliability", "Almost zero maintenance needed besides cabin air filter and wiper fluid. Very reliable.", "Positive"),
        (2, "Battery & Reliability", "Noticed roughly 10% degradation in battery capacity within 2.5 years of ownership.", "Negative"),
        (1, "Battery & Reliability", "Experienced an onboard charger inverter failure that required two weeks in the shop waiting on parts.", "Negative"),
        (3, "Battery & Reliability", "Battery health is holding up fine, but 12V auxiliary battery needed premature replacement.", "Neutral")
    ]

    feedback_rows = []
    user_ids = [f"USR_{1000 + k}" for k in range(650)]
    makes_sample = ["TESLA", "FORD", "CHEVROLET", "HYUNDAI", "KIA", "VOLKSWAGEN", "RIVIAN", "NISSAN"]

    for uid in user_ids:
        template = feedback_templates[np.random.randint(len(feedback_templates))]
        rating, category, text, sentiment = template
        # Add slight rating jitter
        jittered_rating = max(1, min(5, rating + np.random.choice([0, 0, 0, 1, -1])))
        feedback_rows.append({
            "User_ID": uid,
            "Vehicle_Make": np.random.choice(makes_sample),
            "Rating": jittered_rating,
            "Category": category,
            "Feedback_Text": text,
            "Sentiment": sentiment,
            "Verified_Owner": np.random.choice([True, True, True, False]),
            "Date": f"202{np.random.randint(1, 5)}-{np.random.randint(1, 13):02d}-{np.random.randint(1, 29):02d}"
        })

    feedback_df = pd.DataFrame(feedback_rows)
    feedback_df.to_csv(feedback_path, index=False)

    return ev_path, infra_path, feedback_path


def load_dataset(uploaded_file=None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads EV dataset either from an uploaded file or default benchmark.
    """
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            df = clean_ev_dataset(df)
            return df, {"source": "uploaded", "filename": uploaded_file.name, "rows": len(df)}
        except Exception as e:
            # Fallback on error
            pass

    ev_path, _, _ = generate_benchmark_datasets()
    df = pd.read_csv(ev_path)
    df = clean_ev_dataset(df)
    return df, {"source": "benchmark", "filename": "sample_ev_dataset.csv", "rows": len(df)}


def load_infrastructure_data() -> pd.DataFrame:
    """Loads historical charging infrastructure data."""
    _, infra_path, _ = generate_benchmark_datasets()
    return pd.read_csv(infra_path)


def load_feedback_data() -> pd.DataFrame:
    """Loads customer feedback and sentiment dataset."""
    _, _, feedback_path = generate_benchmark_datasets()
    return pd.read_csv(feedback_path)

