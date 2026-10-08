# ⚡ Electric Vehicle Adoption, Infrastructure & Economic Analytics Platform

An end-to-end interactive intelligence dashboard and predictive analytics platform built to analyze historical EV market penetration, forecast adoption trajectories to 2035, model charging infrastructure & power grid requirements, analyze financial/economic ROI, and extract customer feedback sentiment insights.

---

## 🚀 Quickstart Guide

### 1. Installation
All required dependencies are specified in `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### 2. Launch the Application
Run the Streamlit application from the project root:
```powershell
streamlit run app.py
```
Then navigate to `http://localhost:8501` in your web browser.

### 3. Run Automated Tests
Execute the unit test suite to verify data models, calculations, and ML algorithms:
```powershell
python -m unittest discover tests
```

---

## 🧭 Application Modules & Capabilities

### 1. 📊 Executive Summary Dashboard
- Real-time KPI scorecards: Total Active Fleet, Projected Fleet, Required Public Ports, Cumulative Market Size (\$B), Customer CSAT & Net Promoter Score (NPS).
- High-level multi-year adoption curve with confidence intervals.
- Fast diagnostic callouts on network readiness, driver savings, and grid load impact.

### 2. 🚗 EV Adoption & AI Growth Forecasting
- Historical registration trends and Compound Annual Growth Rate (CAGR).
- Powertrain mix shifts: Battery Electric Vehicles (BEV) vs. Plug-in Hybrids (PHEV).
- Market share leaderboards across major EV manufacturers and dominant models.
- **Predictive ML Modeling**:
  - **Bass Diffusion Model**: Fitting innovation ($p$) and imitation ($q$) coefficients to simulate technology S-curve dynamics.
  - **Polynomial & Ridge Regression**: Empirical curve projection with confidence intervals.
  - **Scenario Modes**: Baseline, Aggressive (Net-Zero Push), and Conservative.

### 3. ⚡ Infrastructure Requirements & Grid Load Modeling
- Charging port projections: Level 2 (commercial/workplace) and DC Fast Charging (DCFC) demand.
- Infrastructure gap analysis: Compares current installed network to future targets with required monthly installation pace.
- Fleet energy consumption: Total annual MWh and GWh demand.
- **Diurnal Grid Load Curve Simulation**: 24-hour diurnal power dispatch profile (MW) differentiating residential night charging, workplace daytime charging, and highway DCFC charging.

### 4. 💰 Financial Growth & Economic ROI
- Cumulative vehicle market valuation (\$ Billions).
- Charging network monetization: Annual electricity sales revenue, operator gross margin, and total CapEx required.
- **10-Year Total Cost of Ownership (TCO) Comparison**: Side-by-side analysis of EV vs. Internal Combustion Engine (ICE) vehicle showing annual fuel savings, maintenance cost reductions, and crossover breakeven year.

### 5. 💬 Customer Feedback & Sentiment Intelligence
- CSAT (Average Rating / 5.0) and Net Promoter Score (NPS) tracking.
- Sentiment distribution (Positive, Neutral, Negative) across 5 critical dimensions:
  - *Range Anxiety & Cold-Weather Range Decays*
  - *Charging Station Availability & Uptime Reliability*
  - *Vehicle Purchase Price & Incentives*
  - *Driving Performance & In-Cabin Tech*
  - *Battery Health & Longevity*
- Strategic recommendations for automakers, charge point operators, and policymakers.
- Interactive filterable review explorer.

### 6. 🎛️ Interactive 'What-If' Scenario Simulator & Data Export
- Real-time adjustment of purchase subsidies, gasoline price shocks, and charger rollout pace.
- Side-by-side comparison table between baseline and simulated policy outcomes.
- One-click CSV export of adoption forecasts, infrastructure deployment plans, and 10-year TCO schedules.

---

## 📂 Project Structure

```
├── app.py                     # Streamlit main entrypoint & dashboard UI
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── data/
│   ├── sample_ev_dataset.csv         # Curated multi-year EV fleet dataset (12,000 records)
│   ├── charging_infrastructure.csv    # Historical charging station counts and power metrics
│   └── customer_feedback.csv          # Curated customer reviews and sentiment labels
├── src/
│   ├── __init__.py
│   ├── data_loader.py         # File ingestion, schema normalizer & synthetic data generator
│   ├── ev_growth_model.py     # Bass diffusion, polynomial regression & historical metrics
│   ├── infrastructure_model.py# Charger ratios, diurnal grid load curve & gap analysis
│   ├── financial_model.py     # Market size, TCO savings, charging revenue & CapEx
│   ├── feedback_analyzer.py   # Sentiment classification, NPS & strategic recommendations
│   └── ui_components.py       # Plotly chart builders, metric card styling & theme constants
└── tests/
    └── test_models.py         # Automated unit test suite
```

