"""
app.py - Main Streamlit application for EV Adoption Analysis, Forecasting, Infrastructure Planning, Financial Growth, and Customer Sentiment.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from urllib.parse import unquote

# Page configuration
st.set_page_config(
    page_title="EV Adoption & Infrastructure AI Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.data_loader import (
    load_dataset,
    load_infrastructure_data,
    load_feedback_data,
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
    MAJOR_INDIAN_CITIES,
    build_google_maps_directions,
    fetch_ip_location,
    get_nearest_stations,
    haversine_km,
    normalize_user_location
)
from src.feedback_analyzer import (
    analyze_customer_feedback
)
from components.geo_locator import geo_locator
from src.ui_components import (
    apply_custom_css,
    build_adoption_forecast_chart,
    build_powertrain_split_chart,
    build_top_makes_chart,
    build_infrastructure_growth_chart,
    build_grid_load_curve,
    build_financial_market_chart,
    build_tco_comparison_chart,
    build_sentiment_donut,
    build_category_satisfaction_chart,
    build_charging_points_map
)


def render_geo_location_button() -> dict | None:
    location = geo_locator("Use my current location", key="charging_location")
    return normalize_user_location(location) if location is not None else None

# Apply styling
st.markdown(apply_custom_css(), unsafe_allow_html=True)


# ---------------------------------------------------------
# Sidebar Controls & Configuration
# ---------------------------------------------------------
with st.sidebar:
    st.title("⚡ Control Panel")
    
    # 1. Dataset Selection
    st.markdown("### 📂 Data Source")
    data_choice = st.radio(
        "Choose Data Mode:",
        ["Curated Benchmark Dataset", "Upload Custom Dataset (CSV/XLSX)"],
        index=0
    )
    
    uploaded_file = None
    if data_choice == "Upload Custom Dataset (CSV/XLSX)":
        uploaded_file = st.file_uploader("Upload EV Fleet Dataset", type=["csv", "xlsx"])
        if uploaded_file is None:
            st.info("No file uploaded yet. Using curated benchmark data in the meantime.")
    
    st.divider()

    # 2. Growth Forecasting Settings
    st.markdown("### 📈 Growth Forecasting")
    target_year = st.slider("Forecast Horizon Year", min_value=2026, max_value=2035, value=2032, step=1)
    growth_scenario = st.selectbox(
        "Adoption Scenario",
        ["Baseline", "Aggressive (Net-Zero Push)", "Conservative"],
        index=0
    )
    forecasting_algo = st.selectbox(
        "Prediction Algorithm",
        ["Bass Diffusion", "Polynomial Regression"],
        index=0
    )

    st.divider()

    # 3. Infrastructure Assumptions
    with st.expander("⚡ Infrastructure Parameters"):
        ev_per_l2 = st.slider("EVs per Level 2 Port", min_value=12, max_value=35, value=22, step=1)
        ev_per_dcfc = st.slider("EVs per DC Fast Port", min_value=50, max_value=150, value=85, step=5)
        annual_miles = st.number_input("Avg Annual Miles / EV", min_value=6000, max_value=25000, value=12500, step=500)
        kwh_per_mile = st.slider("Consumption (kWh / mile)", min_value=0.25, max_value=0.50, value=0.34, step=0.01)

    # 4. Financial & TCO Assumptions
    with st.expander("💰 Financial & TCO Parameters"):
        avg_ev_price = st.number_input("Avg EV MSRP (₹)", min_value=250000, max_value=9000000, value=4850000, step=100000)
        gas_price = st.number_input("Gasoline Price (₹/litre)", min_value=70.0, max_value=220.0, value=110.0, step=5.0)
        elec_tariff = st.number_input("Electricity Cost (₹/kWh)", min_value=3.0, max_value=25.0, value=8.0, step=0.5)
        ev_tax_credit = st.number_input("EV Purchase Incentive (₹)", min_value=0, max_value=250000, value=150000, step=10000)


# ---------------------------------------------------------
# Load & Process Data
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_all_data(uploaded_f):
    df_ev, meta = load_dataset(uploaded_f)
    df_infra = load_infrastructure_data()
    df_feedback = load_feedback_data()
    return df_ev, meta, df_infra, df_feedback

df_ev, dataset_meta, df_infra_hist, df_feedback = get_all_data(uploaded_file)

# Historical metrics
hist_metrics = get_historical_metrics(df_ev)
yearly_hist = hist_metrics.get("yearly_data", pd.DataFrame())

# Run Predictive Forecasting Model
forecast_df = forecast_ev_adoption(
    yearly_hist,
    target_year=target_year,
    scenario=growth_scenario,
    model_type=forecasting_algo
)

# Run Infrastructure & Grid Model
current_l2 = int(df_infra_hist.iloc[-1]["Level_2_Ports"]) if not df_infra_hist.empty else 25000
current_dcfc = int(df_infra_hist.iloc[-1]["DC_Fast_Ports"]) if not df_infra_hist.empty else 8000

infra_forecast_df = calculate_infrastructure_requirements(
    forecast_df,
    current_l2_ports=current_l2,
    current_dcfc_ports=current_dcfc,
    ev_per_l2=ev_per_l2,
    ev_per_dcfc=ev_per_dcfc,
    avg_annual_miles=annual_miles,
    avg_kwh_per_mile=kwh_per_mile
)

# Infrastructure KPIs
infra_kpis = get_infrastructure_kpis(infra_forecast_df, target_year=target_year)

# Financial Metrics
fin_forecast_df = calculate_financial_growth(
    infra_forecast_df,
    avg_ev_price=avg_ev_price
)
fin_kpis = get_financial_kpis(fin_forecast_df, target_year=target_year)

# TCO Comparison
tco_df = calculate_tco_comparison(
    years_ownership=10,
    annual_miles=annual_miles,
    ev_purchase_price=avg_ev_price,
    ev_tax_credit=ev_tax_credit,
    gas_price_per_gallon=gas_price,
    electricity_price_kwh=elec_tariff
)

# Customer Feedback Analysis
feedback_results = analyze_customer_feedback(df_feedback)

# 24-hour Diurnal Grid Load Simulation
curr_fleet = infra_kpis.get("projected_fleet", 100000)
hourly_profile = generate_hourly_charging_load_profile(curr_fleet)


# ---------------------------------------------------------
# Main Page Header
# ---------------------------------------------------------
motion_duration = {
    "Baseline": "4.8s",
    "Aggressive (Net-Zero Push)": "3.6s",
    "Conservative": "5.8s",
}.get(growth_scenario, "4.8s")

st.markdown("""
<div class="motion-road" style="--drive-duration: %s;" aria-label="Animated electric vehicle driving along a road">
    <div class="motion-car" aria-hidden="true">
        <span class="motion-spoiler"></span>
        <span class="motion-intake"></span>
        <span class="motion-headlight motion-headlight-left"></span>
        <span class="motion-headlight motion-headlight-right"></span>
        <span class="motion-wheel motion-wheel-left"></span>
        <span class="motion-wheel motion-wheel-right"></span>
    </div>
</div>
""" % motion_duration, unsafe_allow_html=True)


# ---------------------------------------------------------
# App Tabs Layout
# ---------------------------------------------------------
tab_labels = [
    "✦ Welcome",
    "📊 Executive Summary",
    "🚗 EV Adoption & AI Forecast",
    "⚡ Infrastructure & Grid",
    "💰 Financial Growth & TCO",
    "💬 Customer Feedback & Sentiment",
    "🎛️ Scenario Simulator & Export",
    "🔌 Charging Points",
    "💸 EV Price Explorer"
]
workspace_keys = {
    "welcome": "✦ Welcome",
    "executive": "📊 Executive Summary",
    "adoption": "🚗 EV Adoption & AI Forecast",
    "infrastructure": "⚡ Infrastructure & Grid",
    "financial": "💰 Financial Growth & TCO",
    "feedback": "💬 Customer Feedback & Sentiment",
    "scenario": "🎛️ Scenario Simulator & Export",
    "charging": "🔌 Charging Points",
    "prices": "💸 EV Price Explorer",
}
requested_workspace = st.query_params.get("workspace", "welcome")
active_tab = workspace_keys.get(requested_workspace, workspace_keys["welcome"])
ordered_tab_labels = [active_tab] + [label for label in tab_labels if label != active_tab]
tab_views = dict(zip(ordered_tab_labels, st.tabs(ordered_tab_labels)))
welcome_tab = tab_views[workspace_keys["welcome"]]
tab1 = tab_views[workspace_keys["executive"]]
tab2 = tab_views[workspace_keys["adoption"]]
tab3 = tab_views[workspace_keys["infrastructure"]]
tab4 = tab_views[workspace_keys["financial"]]
tab5 = tab_views[workspace_keys["feedback"]]
tab6 = tab_views[workspace_keys["scenario"]]
tab7 = tab_views[workspace_keys["charging"]]
tab8 = tab_views[workspace_keys["prices"]]


# =========================================================
# WELCOME / WORKSPACE NAVIGATION
# =========================================================
with welcome_tab:
    st.markdown("""
    <div class="page-intro">
        <div><h3>✦ Welcome to EVision</h3><p>Your command center for understanding electric mobility adoption, investment, infrastructure, and customer demand.</p></div>
        <span class="context-chip">Workspace home</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="welcome-lead">
        <div class="hero-kicker">EVISION / ELECTRIC FUTURE</div>
        <h2>Make the next move with clarity.</h2>
        <p>Choose a topic below to open its full analysis workspace. Your current data, forecast horizon, and scenario controls stay active as you move through the platform.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Choose a workspace")
    st.caption("Click any topic to open its full page. Use the tabs at the top whenever you want to switch views.")
    welcome_cols = st.columns(4)
    welcome_items = [
        ("01", "Executive Summary", "See the headline signals, readiness score, market size, and sentiment in one view.", "executive"),
        ("02", "Adoption Forecast", "Explore historical growth, powertrain mix, leading makes, and future scenarios.", "adoption"),
        ("03", "Infrastructure & Grid", "Plan charging ports, energy demand, deployment pace, and peak load exposure.", "infrastructure"),
        ("04", "Financial & TCO", "Compare market value, charging revenue, capital needs, and driver savings.", "financial"),
        ("05", "Customer Feedback", "Turn owner sentiment, satisfaction, and review themes into action areas.", "feedback"),
        ("06", "Scenario Simulator", "Stress-test incentives, fuel prices, rollout speed, and export the results.", "scenario"),
        ("07", "Charging Points", "Find nearby public charging stations and get directions to the best-fit locations.", "charging"),
        ("08", "EV Price Explorer", "Compare indicative prices and ranges across electric two-wheelers and cars.", "prices"),
    ]
    for item_index, (number, title, description, workspace_key) in enumerate(welcome_items):
        welcome_col = welcome_cols[item_index % 4]
        with welcome_col:
            st.markdown(f'<div class="welcome-card"><div class="welcome-number">{number}</div><h4>{title}</h4><p>{description}</p></div>', unsafe_allow_html=True)
            st.link_button("Open topic →", f"?workspace={workspace_key}", use_container_width=True)

    st.markdown("#### Start with the signal that matters")
    start_cols = st.columns(3)
    with start_cols[0]:
        st.markdown(f'<div class="insight-card"><div class="insight-label">Current dataset</div><div class="insight-text"><strong>{dataset_meta["rows"]:,}</strong> EV records ready for analysis from {dataset_meta["filename"]}.</div></div>', unsafe_allow_html=True)
    with start_cols[1]:
        st.markdown(f'<div class="insight-card"><div class="insight-label">Active model</div><div class="insight-text"><strong>{growth_scenario}</strong> adoption scenario through <strong>{target_year}</strong>.</div></div>', unsafe_allow_html=True)
    with start_cols[2]:
        st.markdown('<div class="insight-card"><div class="insight-label">New in this workspace</div><div class="insight-text">Open <strong>Charging Points</strong> to locate the nearest stations from your live position and jump to Google Maps directions.</div></div>', unsafe_allow_html=True)

    st.markdown("#### How to use EVision")
    st.markdown("""
    <div class="hero-status" style="background:#102a2b;color:#dff7ef;margin-top:0;">1 · Choose a workspace</div>
    <div class="hero-status" style="background:#0d9488;color:#effbf6;margin:0.6rem 0 0;">2 · Adjust assumptions in the control panel</div>
    <div class="hero-status" style="background:#c9f36b;color:#102a2b;margin-top:0.6rem;">3 · Turn insights into an action plan</div>
    """, unsafe_allow_html=True)


# =========================================================
# TAB 1: EXECUTIVE SUMMARY
# =========================================================
with tab1:
    st.markdown(f"""
    <div class="page-intro">
        <div><h3>🌐 Strategic Executive Overview</h3><p>A decision-ready snapshot of adoption momentum, network readiness, economics, and owner sentiment.</p></div>
        <span class="context-chip">{growth_scenario} · through {target_year}</span>
    </div>
    <p style="color:#607878;font-size:0.82rem;margin-top:-0.7rem;margin-bottom:1.1rem;">Active source: <strong>{dataset_meta['filename']}</strong> · {dataset_meta['rows']:,} records analyzed</p>
    """, unsafe_allow_html=True)

    # Top KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Current Active Fleet</div>
            <div class="metric-value">{hist_metrics.get('total_active_fleet', 0):,}</div>
            <div class="metric-delta delta-pos">Historical CAGR: +{hist_metrics.get('cagr', 0)}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        proj_fleet = infra_kpis.get("projected_fleet", 0)
        fleet_mult = round(proj_fleet / max(1, hist_metrics.get('total_active_fleet', 1)), 1)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Projected Fleet ({target_year})</div>
            <div class="metric-value">{proj_fleet:,}</div>
            <div class="metric-delta delta-pos">▲ {fleet_mult}x Fleet Expansion</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        req_ports = infra_kpis.get("total_ports", 0)
        gap = infra_kpis.get("ports_gap", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Required Chargers</div>
            <div class="metric-value">{req_ports:,}</div>
            <div class="metric-delta delta-neg">Port Deficit: {gap:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        cum_market_b = fin_kpis.get("cum_market_b", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Cumulative Market Size</div>
            <div class="metric-value">₹{cum_market_b:,.1f}B</div>
            <div class="metric-delta delta-pos">Total Vehicle Capital</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        csat = feedback_results.get("avg_rating", 0)
        nps = feedback_results.get("nps", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Owner Satisfaction</div>
            <div class="metric-value">{csat} / 5.0</div>
            <div class="metric-delta {'delta-pos' if nps >= 0 else 'delta-neg'}">NPS Score: {nps:+.1f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### At-a-glance signals")
    signal1, signal2, signal3 = st.columns(3)
    with signal1:
        st.markdown(f'<div class="insight-card"><div class="insight-label">Adoption momentum</div><div class="insight-text">Fleet growth is tracking at <strong>+{hist_metrics.get("cagr", 0)}%</strong> historical CAGR.</div></div>', unsafe_allow_html=True)
    with signal2:
        st.markdown(f'<div class="insight-card"><div class="insight-label">Network readiness</div><div class="insight-text">Current deployment covers <strong>{infra_kpis.get("readiness_pct", 0)}%</strong> of the {target_year} requirement.</div></div>', unsafe_allow_html=True)
    with signal3:
        st.markdown(f'<div class="insight-card"><div class="insight-label">Owner economics</div><div class="insight-text">Estimated annual operating savings reach <strong>₹{tco_df.iloc[0]["Total_Annual_Operating_Savings"]:,.0f}</strong> per EV.</div></div>', unsafe_allow_html=True)

    # Overview Visuals
    c_left, c_right = st.columns([3, 2])
    with c_left:
        st.plotly_chart(build_adoption_forecast_chart(forecast_df, growth_scenario), use_container_width=True, key="exec_adoption_forecast_chart")

    with c_right:
        st.plotly_chart(build_sentiment_donut(feedback_results.get("sentiment_distribution", {})), use_container_width=True, key="exec_sentiment_donut_chart")

    # Summary Callout Table
    st.markdown("#### 📌 Key Readiness & Growth Observations")
    ob1, ob2, ob3 = st.columns(3)
    with ob1:
        st.info(f"**Infrastructure Readiness:** At present deployment levels, existing public chargers cover **{infra_kpis.get('readiness_pct', 0)}%** of the estimated **{target_year}** requirement.")
    with ob2:
        st.success(f"**Consumer Economics:** EV drivers achieve **₹{tco_df.iloc[0]['Total_Annual_Operating_Savings']:,.0f}/year** in combined fuel and maintenance savings compared to ICE counterparts.")
    with ob3:
        st.warning(f"**Grid Impact:** Fleet electricity demand reaches **{infra_kpis.get('annual_energy_gwh', 0):,.1f} GWh/year**, peaking at **{infra_kpis.get('peak_load_mw', 0):,.1f} MW** during evening residential charging.")


# =========================================================
# TAB 2: EV ADOPTION & GROWTH FORECASTING
# =========================================================
with tab2:
    st.markdown("""
    <div class="page-intro"><div><h3>🚗 EV Adoption Trajectory & Machine Learning Forecast</h3><p>Understand where adoption has been, how the powertrain mix is shifting, and what the selected model expects next.</p></div><span class="context-chip">Forecast lens</span></div>
    """, unsafe_allow_html=True)

    col_f1, col_f2 = st.columns([3, 2])
    with col_f1:
        st.plotly_chart(build_adoption_forecast_chart(forecast_df, growth_scenario), use_container_width=True, key="growth_adoption_forecast_chart")
    with col_f2:
        st.plotly_chart(build_powertrain_split_chart(yearly_hist), use_container_width=True, key="growth_powertrain_mix_chart")

    st.divider()

    # Automaker and Model Leaders
    st.markdown("#### 🏆 Market Share & Manufacturer Distribution")
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.plotly_chart(build_top_makes_chart(hist_metrics.get("top_makes", pd.DataFrame())), use_container_width=True, key="growth_top_makes_chart")
    with c_m2:
        st.markdown("##### 🚙 Top 10 EV Models Registered")
        top_models_df = hist_metrics.get("top_models", pd.DataFrame())
        if not top_models_df.empty:
            st.dataframe(
                top_models_df[["Vehicle", "make", "model", "Count"]].rename(
                    columns={"Vehicle": "Vehicle Name", "make": "Make", "model": "Model", "Count": "Registrations"}
                ),
                use_container_width=True,
                hide_index=True
            )

    # Detailed Forecast Table
    with st.expander("📋 View Forecast Data Table (Historical + Predictions)"):
        st.dataframe(
            forecast_df.rename(columns={
                "year": "Year",
                "cumulative_fleet": "Projected Cumulative Fleet",
                "annual_additions": "Annual Additions",
                "is_forecast": "Is Projected",
                "fleet_lower_bound": "Lower Confidence (-)",
                "fleet_upper_bound": "Upper Confidence (+)",
                "bev_pct": "BEV Share (%)",
                "phev_pct": "PHEV Share (%)"
            }),
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# TAB 3: INFRASTRUCTURE REQUIREMENTS & GRID LOAD
# =========================================================
with tab3:
    st.markdown("""
    <div class="page-intro"><div><h3>⚡ Infrastructure Requirements & Grid Load Modeling</h3><p>Translate fleet growth into charging capacity, deployment pace, annual energy demand, and peak grid exposure.</p></div><span class="context-chip">Capacity planning</span></div>
    """, unsafe_allow_html=True)

    i_kpi1, i_kpi2, i_kpi3, i_kpi4 = st.columns(4)
    with i_kpi1:
        st.metric("Required Level 2 Ports", f"{infra_kpis.get('req_l2', 0):,}", f"Deficit: {infra_forecast_df.iloc[-1]['l2_gap']:,}")
    with i_kpi2:
        st.metric("Required DC Fast Ports", f"{infra_kpis.get('req_dcfc', 0):,}", f"Deficit: {infra_forecast_df.iloc[-1]['dcfc_gap']:,}")
    with i_kpi3:
        st.metric(f"Annual Energy ({target_year})", f"{infra_kpis.get('annual_energy_gwh', 0):,.1f} GWh")
    with i_kpi4:
        st.metric(f"Simulated Peak Grid Load", f"{infra_kpis.get('peak_load_mw', 0):,.1f} MW")

    st.divider()

    c_i1, c_i2 = st.columns([3, 3])
    with c_i1:
        st.plotly_chart(build_infrastructure_growth_chart(infra_forecast_df), use_container_width=True, key="infra_requirements_growth_chart")
    with c_i2:
        st.plotly_chart(build_grid_load_curve(hourly_profile), use_container_width=True, key="infra_diurnal_grid_load_chart")

    # Infrastructure Gap Summary
    st.markdown("#### 🚨 Infrastructure Deficit & Deployment Targets")
    curr_total_ports = current_l2 + current_dcfc
    needed_total_ports = infra_kpis.get("total_ports", 0)
    gap_ports = infra_kpis.get("ports_gap", 0)
    years_remaining = max(1, target_year - 2024)
    annual_ports_needed = int(gap_ports / years_remaining)
    monthly_ports_needed = int(annual_ports_needed / 12)

    g1, g2, g3 = st.columns(3)
    g1.metric("Currently Installed Ports", f"{curr_total_ports:,}")
    g2.metric("Target Network Ports", f"{needed_total_ports:,}")
    g3.metric("Required Installation Pace", f"{monthly_ports_needed:,} ports / month", f"{annual_ports_needed:,} / year")


# =========================================================
# TAB 4: FINANCIAL GROWTH & ECONOMIC ROI
# =========================================================
with tab4:
    st.markdown("""
    <div class="page-intro"><div><h3>💰 Financial Growth, Charging Economy & Total Cost of Ownership</h3><p>Connect vehicle market expansion with infrastructure investment, charging revenue, and lifetime driver economics.</p></div><span class="context-chip">Investment view</span></div>
    """, unsafe_allow_html=True)

    fk1, fk2, fk3, fk4 = st.columns(4)
    with fk1:
        st.metric("Cumulative Fleet Value", f"₹{fin_kpis.get('cum_market_b', 0):,.1f}B")
    with fk2:
        st.metric(f"Annual Charging Revenue ({target_year})", f"₹{fin_kpis.get('charging_revenue_m', 0):,.1f}M")
    with fk3:
        st.metric("Total Infrastructure CapEx Required", f"₹{fin_kpis.get('total_capex_m', 0):,.1f}M")
    with fk4:
        be_yr = tco_df.attrs.get("breakeven_year", "N/A")
        st.metric("EV TCO Breakeven Horizon", f"Year {be_yr}", "Vs. Comparable Gas Vehicle")

    st.divider()

    cf1, cf2 = st.columns([3, 3])
    with cf1:
        st.plotly_chart(build_financial_market_chart(fin_forecast_df), use_container_width=True, key="financial_market_expansion_chart")
    with cf2:
        st.plotly_chart(build_tco_comparison_chart(tco_df), use_container_width=True, key="financial_tco_comparison_chart")

    # Detailed TCO Breakdown Table
    st.markdown("#### 📊 10-Year Cumulative Total Cost of Ownership Breakdown")
    st.dataframe(
        tco_df.rename(columns={
            "Year": "Ownership Year",
            "EV_Cumulative_TCO": "EV Cumulative Spend (₹)",
            "ICE_Cumulative_TCO": "ICE Gas Cumulative Spend (₹)",
            "Cumulative_Savings_EV": "Net EV Cumulative Savings (₹)",
            "Annual_Fuel_Savings": "Annual Fuel Savings (₹)",
            "Annual_Maintenance_Savings": "Annual Maint Savings (₹)",
            "Total_Annual_Operating_Savings": "Total Annual Op Savings (₹)"
        }),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# TAB 5: CUSTOMER FEEDBACK & SENTIMENT INSIGHTS
# =========================================================
with tab5:
    st.markdown("""
    <div class="page-intro"><div><h3>💬 Customer Feedback, Satisfaction & Sentiment Intelligence</h3><p>Turn owner feedback into a prioritized view of experience strengths, adoption barriers, and action areas.</p></div><span class="context-chip">Voice of customer</span></div>
    """, unsafe_allow_html=True)

    fb_k1, fb_k2, fb_k3, fb_k4 = st.columns(4)
    with fb_k1:
        st.metric("Total Reviews Analyzed", f"{feedback_results.get('total_reviews', 0):,}")
    with fb_k2:
        st.metric("Average CSAT Rating", f"{feedback_results.get('avg_rating', 0)} / 5.0")
    with fb_k3:
        st.metric("Satisfied Owners (4-5★)", f"{feedback_results.get('satisfied_pct', 0)}%")
    with fb_k4:
        st.metric("Net Promoter Score (NPS)", f"+{feedback_results.get('nps', 0)}")

    st.divider()

    fb_c1, fb_c2 = st.columns([2, 3])
    with fb_c1:
        st.plotly_chart(build_sentiment_donut(feedback_results.get("sentiment_distribution", {})), use_container_width=True, key="feedback_sentiment_donut_chart")
    with fb_c2:
        st.plotly_chart(build_category_satisfaction_chart(feedback_results.get("category_summary", pd.DataFrame())), use_container_width=True, key="feedback_category_satisfaction_chart")

    st.divider()

    # Strategic Recommendations & Action Items
    st.markdown("#### 🎯 AI-Generated Strategic Interventions for Adoption Acceleration")
    recs = feedback_results.get("recommendations", [])
    for rec in recs:
        badge_class = "badge-high" if rec["severity"] == "High" else ("badge-med" if rec["severity"] == "Medium" else "badge-low")
        st.markdown(f"""
        <div style="background-color: #f8fafc; border-left: 4px solid #0d9488; padding: 14px 18px; border-radius: 8px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <strong style="color: #0f172a; font-size: 1.05rem;">{rec['area']}</strong>
                <span class="badge {badge_class}">Priority: {rec['severity']}</span>
            </div>
            <p style="margin: 0 0 6px 0; color: #475569; font-size: 0.95rem;"><strong>Issue Diagnostic:</strong> {rec['finding']}</p>
            <p style="margin: 0; color: #0d9488; font-size: 0.95rem;"><strong>Recommended Strategy:</strong> {rec['action']}</p>
        </div>
        """, unsafe_allow_html=True)

    # Sample Customer Reviews Filter
    with st.expander("🔍 Explore Filtered Customer Reviews"):
        cat_filter = st.selectbox("Filter by Category", ["All Categories"] + list(feedback_results.get("category_summary", pd.DataFrame())["Category"].unique()))
        sent_filter = st.selectbox("Filter by Sentiment", ["All Sentiments", "Positive", "Neutral", "Negative"])
        
        raw_df = feedback_results.get("raw_reviews", pd.DataFrame())
        filtered_df = raw_df.copy()
        if cat_filter != "All Categories":
            filtered_df = filtered_df[filtered_df["Category"] == cat_filter]
        if sent_filter != "All Sentiments":
            filtered_df = filtered_df[filtered_df["Sentiment"] == sent_filter]

        st.dataframe(
            filtered_df[["Date", "Vehicle_Make", "Rating", "Category", "Sentiment", "Feedback_Text"]],
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# TAB 6: SCENARIO SIMULATOR & DATA EXPORT
# =========================================================
with tab6:
    st.markdown("""
    <div class="page-intro"><div><h3>🎛️ Interactive 'What-If' Policy & Infrastructure Simulator</h3><p>Stress-test incentives, fuel-price changes, and rollout speed to see how strategic choices alter the end state.</p></div><span class="context-chip">Scenario lab</span></div>
    """, unsafe_allow_html=True)

    sim_c1, sim_c2, sim_c3 = st.columns(3)
    with sim_c1:
        sub_boost = st.slider("Additional Purchase Rebate (₹)", 0, 10000, 2500, 500)
    with sim_c2:
        gas_spike = st.slider("Gasoline Price Shock (₹/litre)", 70.00, 220.00, 110.00, 5.00)
    with sim_c3:
        infra_speedup = st.select_slider("Charger Deployment Acceleration", options=["Standard", "+20% Fast Track", "+50% Supercharged"], value="+20% Fast Track")

    # Interactive simulation metrics
    accel_factor = 1.0 + (sub_boost / 25000.0) + (max(0, gas_spike - 3.65) * 0.08)
    simulated_fleet = int(proj_fleet * accel_factor)
    simulated_ports = int(req_ports * accel_factor)
    simulated_energy = round(infra_kpis.get("annual_energy_gwh", 0) * accel_factor, 1)
    simulated_market_b = round(cum_market_b * accel_factor, 1)

    st.markdown("#### ⚡ Simulation Results Comparison")
    sim_res_df = pd.DataFrame({
        "Metric": [
            f"Projected Fleet Size ({target_year})",
            f"Required Charging Ports ({target_year})",
            f"Annual Energy Demand ({target_year})",
            f"Cumulative Market Value ({target_year})"
        ],
        "Baseline Model": [
            f"{proj_fleet:,}",
            f"{req_ports:,} ports",
            f"{infra_kpis.get('annual_energy_gwh', 0):,.1f} GWh",
            f"₹{cum_market_b:,.1f} Billion"
        ],
        "Simulated Policy Scenario": [
            f"{simulated_fleet:,}",
            f"{simulated_ports:,} ports",
            f"{simulated_energy:,.1f} GWh",
            f"₹{simulated_market_b:,.1f} Billion"
        ],
        "Net Impact": [
            f"+{int(simulated_fleet - proj_fleet):,} EVs (+{round((accel_factor-1)*100, 1)}%)",
            f"+{int(simulated_ports - req_ports):,} chargers",
            f"+{round(simulated_energy - infra_kpis.get('annual_energy_gwh', 0), 1)} GWh",
            f"+₹{round(simulated_market_b - cum_market_b, 1)}B"
        ]
    })
    st.table(sim_res_df)

    st.divider()

    # Data Export Section
    st.markdown("#### 📥 Export Forecast & Analysis Datasets")
    st.caption("Download comprehensive multi-year projection tables for reporting and offline analysis.")

    exp_col1, exp_col2, exp_col3 = st.columns(3)
    with exp_col1:
        csv_forecast = forecast_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download EV Forecast (CSV)",
            data=csv_forecast,
            file_name=f"ev_adoption_forecast_{target_year}.csv",
            mime="text/csv"
        )


# =========================================================
# TAB 7: CHARGING POINTS
# =========================================================
with tab7:
    st.markdown("""
    <div class="page-intro"><div><h3>🔌 Charging Points & Nearby Stations</h3><p>Find the best public charging options near you, review station details, and open turn-by-turn directions in Google Maps.</p></div><span class="context-chip">Location-aware routing</span></div>
    """, unsafe_allow_html=True)

    if "user_location" not in st.session_state:
        # Automatically detect real location on first load via network IP
        auto_loc = fetch_ip_location()
        if auto_loc and auto_loc.get("lat") and auto_loc.get("lon"):
            st.session_state.user_location = auto_loc
        else:
            st.session_state.user_location = {
                "lat": 23.6739,
                "lon": 86.9524,
                "city": "Asansol, West Bengal",
                "source": "default"
            }

    # Prominent Quick-Action Bar
    q_col1, q_col2 = st.columns([1.2, 1.8])
    with q_col1:
        if st.button("🎯 Detect My Location Now", key="quick_detect_btn", use_container_width=True):
            with st.spinner("Detecting your location..."):
                auto_loc = fetch_ip_location()
                if auto_loc and auto_loc.get("lat") and auto_loc.get("lon"):
                    st.session_state.user_location = auto_loc
                    st.success(f"✓ Detected: {auto_loc['city']}")
                    st.rerun()
                else:
                    st.warning("Network lookup timed out. Please select your city from the dropdown.")
    with q_col2:
        city_names = list(MAJOR_INDIAN_CITIES.keys())
        current_city_raw = st.session_state.user_location.get("city", "")
        matched_idx = 0
        for idx, cname in enumerate(city_names):
            if cname.split(" ")[0].lower() in current_city_raw.lower():
                matched_idx = idx
                break
        
        c_pick, c_btn = st.columns([3, 1])
        with c_pick:
            selected_city_quick = st.selectbox(
                "Quick City Switcher:",
                city_names,
                index=matched_idx,
                key="quick_city_selector",
                label_visibility="collapsed"
            )
        with c_btn:
            if st.button("Set City", key="btn_apply_quick_city"):
                coords = MAJOR_INDIAN_CITIES[selected_city_quick]
                st.session_state.user_location = {
                    "lat": coords["lat"],
                    "lon": coords["lon"],
                    "city": selected_city_quick,
                    "source": "manual_city"
                }
                st.rerun()

    # Advanced Location Options (Browser GPS & Custom Lat/Lon)
    with st.expander("⚙️ Advanced: Browser GPS & Custom Coordinates"):
        adv_tab1, adv_tab2 = st.tabs(["📍 Browser GPS Component", "📌 Custom Latitude & Longitude"])
        with adv_tab1:
            st.caption("Requests high-precision GPS directly from your device browser. (Works in secure browser contexts with permission allowed)")
            location_result = render_geo_location_button()
            if location_result is not None:
                if location_result.get("error"):
                    st.info(f"💡 {location_result['error']}")
                elif location_result.get("lat") is not None and location_result.get("lon") is not None:
                    new_lat = float(location_result["lat"])
                    new_lon = float(location_result["lon"])
                    new_city = str(location_result.get("city") or "Live Device GPS")
                    curr = st.session_state.user_location
                    if abs(curr.get("lat", 0) - new_lat) > 0.0005 or abs(curr.get("lon", 0) - new_lon) > 0.0005:
                        st.session_state.user_location = {
                            "lat": new_lat,
                            "lon": new_lon,
                            "city": new_city,
                            "source": location_result.get("source", "device_gps")
                        }
                        st.success(f"✓ Location updated from GPS: {new_city} ({new_lat:.4f}, {new_lon:.4f})")
                        st.rerun()
        with adv_tab2:
            c_lat, c_lon = st.columns(2)
            with c_lat:
                inp_lat = st.number_input("Latitude", value=float(st.session_state.user_location.get("lat", 23.6739)), format="%.4f", key="custom_lat_val")
            with c_lon:
                inp_lon = st.number_input("Longitude", value=float(st.session_state.user_location.get("lon", 86.9524)), format="%.4f", key="custom_lon_val")
            if st.button("Apply Custom Coordinates", key="btn_apply_custom_coords"):
                st.session_state.user_location = {
                    "lat": inp_lat,
                    "lon": inp_lon,
                    "city": f"Custom Coordinates ({inp_lat:.3f}, {inp_lon:.3f})",
                    "source": "custom_coords"
                }
                st.success(f"✓ Location set to {inp_lat:.4f}, {inp_lon:.4f}")
                st.rerun()

    # Active Location Display Banner
    user_lat = float(st.session_state.user_location.get("lat", 23.6739))
    user_lon = float(st.session_state.user_location.get("lon", 86.9524))
    user_city = st.session_state.user_location.get("city", "Active Location")
    user_source = st.session_state.user_location.get("source", "default")

    source_tag = "📍 Live Device GPS" if user_source in ["device_gps", "gps"] else (
        "🌐 Network IP Detected" if user_source == "network_ip" else (
            "🏙️ Selected City" if user_source == "manual_city" else (
                "📌 Custom Coordinates" if user_source == "custom_coords" else "🚩 Default Location"
            )
        )
    )

    st.markdown(f"""
    <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:12px 18px;margin:12px 0 16px 0;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
        <div>
            <strong style="color:#166534;font-size:1.02rem;">Current Position: {user_city}</strong>
            <span style="color:#15803d;font-size:0.86rem;margin-left:8px;">({user_lat:.4f}, {user_lon:.4f})</span>
        </div>
        <span style="background:#dcfce7;color:#166534;padding:4px 10px;border-radius:999px;font-size:0.78rem;font-weight:700;">{source_tag}</span>
    </div>
    """, unsafe_allow_html=True)

    # Station calculations
    station_df = pd.DataFrame(STATIONS)
    station_df["Distance from you (km)"] = station_df.apply(
        lambda row: round(haversine_km(user_lat, user_lon, row["latitude"], row["longitude"]), 1),
        axis=1,
    )
    station_df = station_df.sort_values("Distance from you (km)", ascending=True).reset_index(drop=True)

    station_df["Map Link"] = station_df.apply(
        lambda row: build_google_maps_directions(user_lat, user_lon, row["latitude"], row["longitude"]),
        axis=1,
    )

    # Interactive Map View
    st.plotly_chart(
        build_charging_points_map(user_lat, user_lon, user_city, station_df),
        use_container_width=True,
        key="charging_points_interactive_map"
    )

    # Nearest stations shortlist
    nearest_df = station_df[["name", "address", "city", "type", "power_kw", "Distance from you (km)"]].head(5).copy()
    nearest_df.columns = ["Station", "Address", "City", "Type", "Power (kW)", "Distance from you (km)"]

    closest_distance = nearest_df.iloc[0]["Distance from you (km)"] if not nearest_df.empty else 0.0

    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric("Closest Station", f"{closest_distance:.1f} km", nearest_df.iloc[0]["Station"] if not nearest_df.empty else "")
    with m_col2:
        fast_count = len(station_df[station_df["type"].str.contains("DC|Fast", case=False, na=False)])
        st.metric("Fast Chargers in Network", f"{fast_count} stations")
    with m_col3:
        st.metric("Total Listed Network Stations", f"{len(station_df)} stations across India")

    col1, col2 = st.columns([1.2, 1.4])
    with col1:
        st.markdown("#### ⚡ Closest Charging Points")
        for _, row in nearest_df.iterrows():
            station_record = next(s for s in STATIONS if s["name"] == row["Station"])
            maps_url = build_google_maps_directions(user_lat, user_lon, station_record["latitude"], station_record["longitude"])

            st.markdown(f"""
            <div style="background:#f8fafc;border:1px solid #dfe7e5;border-radius:12px;padding:16px;margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;">
                    <strong style="font-size:1.02rem;color:#0f172a;">{row['Station']}</strong>
                    <span style="background:#dff7ef;color:#0d9488;padding:4px 8px;border-radius:999px;font-size:0.72rem;font-weight:700;">{row['Distance from you (km)']:.1f} km away</span>
                </div>
                <p style="margin:0.5rem 0 0.2rem;color:#475569;">📍 {row['Address']}, {row['City']}</p>
                <p style="margin:0 0 0.8rem;color:#475569;">⚡ {row['Type']} · {row['Power (kW)']} kW</p>
                <a href="{maps_url}" target="_blank" style="text-decoration:none;color:#ffffff;background:#0d9488;padding:0.55rem 0.95rem;border-radius:8px;display:inline-block;font-weight:600;font-size:0.88rem;">📍 Open in Google Maps</a>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### 📋 All Charging Stations (Sorted by Proximity)")
        display_df = station_df[["name", "address", "city", "state", "type", "power_kw", "Distance from you (km)"]].copy()
        display_df.columns = ["Station", "Address", "City", "State", "Type", "Power (kW)", "Distance from you (km)"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

# =========================================================
# TAB 8: EV PRICE EXPLORER
# =========================================================
with tab8:
    st.markdown("""
    <div class="page-intro"><div><h3>💸 EV Price Explorer</h3><p>Compare indicative ex-showroom prices across popular electric two-wheelers and four-wheelers in the Indian market.</p></div><span class="context-chip">Market reference</span></div>
    """, unsafe_allow_html=True)
    st.info("Prices are indicative reference values for comparison and may vary by city, trim, battery pack, subsidies, insurance, and dealer offers.")

    two_wheeler_prices = pd.DataFrame([
        {"Model": "Ola S1 Pro", "Body Type": "Electric Scooter", "Starting Price": 115000, "Top Variant": 135000, "Claimed Range": "176 km"},
        {"Model": "TVS iQube", "Body Type": "Electric Scooter", "Starting Price": 94999, "Top Variant": 185373, "Claimed Range": "150 km"},
        {"Model": "Ather 450X", "Body Type": "Electric Scooter", "Starting Price": 139000, "Top Variant": 170000, "Claimed Range": "161 km"},
        {"Model": "Bajaj Chetak", "Body Type": "Electric Scooter", "Starting Price": 107243, "Top Variant": 154189, "Claimed Range": "153 km"},
        {"Model": "Revolt RV400", "Body Type": "Electric Motorcycle", "Starting Price": 127950, "Top Variant": 142950, "Claimed Range": "150 km"},
    ])
    four_wheeler_prices = pd.DataFrame([
        {"Model": "Tata Tiago EV", "Body Type": "Hatchback", "Starting Price": 799000, "Top Variant": 1199000, "Claimed Range": "315 km"},
        {"Model": "MG Comet EV", "Body Type": "City Hatchback", "Starting Price": 699800, "Top Variant": 991800, "Claimed Range": "230 km"},
        {"Model": "Tata Nexon EV", "Body Type": "Compact SUV", "Starting Price": 1450000, "Top Variant": 1999000, "Claimed Range": "465 km"},
        {"Model": "Mahindra XUV400", "Body Type": "Compact SUV", "Starting Price": 1599000, "Top Variant": 1949000, "Claimed Range": "456 km"},
        {"Model": "Hyundai Ioniq 5", "Body Type": "Premium SUV", "Starting Price": 4650000, "Top Variant": 4650000, "Claimed Range": "631 km"},
    ])

    price_kpi1, price_kpi2, price_kpi3 = st.columns(3)
    with price_kpi1:
        st.markdown('<div class="price-card"><div class="price-label">Two-wheeler entry point</div><div class="price-value">₹69,800+</div><div class="price-note">From the listed scooter and motorcycle segment</div></div>', unsafe_allow_html=True)
    with price_kpi2:
        st.markdown('<div class="price-card"><div class="price-label">Four-wheeler entry point</div><div class="price-value">₹6.99L+</div><div class="price-note">Compact city EV reference price</div></div>', unsafe_allow_html=True)
    with price_kpi3:
        st.markdown('<div class="price-card"><div class="price-label">Longest listed range</div><div class="price-value">631 km</div><div class="price-note">Premium four-wheeler reference</div></div>', unsafe_allow_html=True)

    price_left, price_right = st.columns(2)
    with price_left:
        st.markdown("#### 🛵 Electric two-wheelers")
        display_two_wheeler = two_wheeler_prices.copy()
        for price_column in ["Starting Price", "Top Variant"]:
            display_two_wheeler[price_column] = display_two_wheeler[price_column].map(lambda value: f"₹{value:,.0f}")
        st.dataframe(display_two_wheeler, use_container_width=True, hide_index=True)
    with price_right:
        st.markdown("#### 🚙 Electric four-wheelers")
        display_four_wheeler = four_wheeler_prices.copy()
        for price_column in ["Starting Price", "Top Variant"]:
            display_four_wheeler[price_column] = display_four_wheeler[price_column].map(lambda value: f"₹{value:,.0f}")
        st.dataframe(display_four_wheeler, use_container_width=True, hide_index=True)

    st.markdown("#### Price band comparison")
    price_chart_df = pd.concat([
        two_wheeler_prices.assign(Segment="Two-wheelers"),
        four_wheeler_prices.assign(Segment="Four-wheelers")
    ], ignore_index=True)
    price_chart = px.bar(price_chart_df, x="Model", y="Starting Price", color="Segment", title="Indicative starting prices by model", labels={"Starting Price": "Starting price (INR)"}, color_discrete_map={"Two-wheelers": "#0d9488", "Four-wheelers": "#f59e0b"})
    price_chart.update_layout(template="plotly_white", showlegend=False, margin=dict(l=30, r=20, t=55, b=90), xaxis_tickangle=-35)
    st.plotly_chart(price_chart, use_container_width=True, key="ev_price_comparison_chart")
    with exp_col2:
        csv_infra = infra_forecast_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⚡ Download Infrastructure Plan (CSV)",
            data=csv_infra,
            file_name=f"ev_infrastructure_plan_{target_year}.csv",
            mime="text/csv"
        )
    with exp_col3:
        csv_tco = tco_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💰 Download 10-Yr TCO Model (CSV)",
            data=csv_tco,
            file_name="ev_tco_comparison.csv",
            mime="text/csv"
        )

st.markdown("""
<div class="app-footer">
    EV Adoption & Infrastructure AI Platform • Built with Streamlit, Plotly, Pandas & Scikit-Learn
</div>
""", unsafe_allow_html=True)

