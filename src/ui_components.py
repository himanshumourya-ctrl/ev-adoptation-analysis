"""
ui_components.py - Reusable Plotly chart builders, KPI metric widgets, and custom CSS for Streamlit.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Theme Color Constants
PRIMARY_COLOR = "#0D9488"      # Teal
SECONDARY_COLOR = "#3B82F6"    # Electric Blue
ACCENT_GREEN = "#10B981"       # Emerald Green
ACCENT_PURPLE = "#8B5CF6"      # Indigo / Violet
ACCENT_AMBER = "#F59E0B"       # Warm Amber
ACCENT_CORAL = "#EF4444"       # Red / Alert
DARK_BG = "#0F172A"            # Slate 900
CARD_BG = "#1E293B"            # Slate 800
BORDER_COLOR = "#334155"       # Slate 700
TEXT_MUTED = "#94A3B8"         # Slate 400


def apply_custom_css():
    """
    Returns custom CSS styles for cards, KPI tiles, and layout polish.
    """
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
        :root {
            --ink: #102a2b;
            --muted: #607878;
            --teal: #0d9488;
            --lime: #c9f36b;
            --line: #d9e9e2;
        }
                width: 150px;
                height: 38px;
                border-radius: 48% 58% 12% 15% / 70% 78% 25% 28%;
                background: linear-gradient(165deg, #d9ff78 0 17%, #50d5b6 18% 42%, #0d9488 43% 67%, #07383d 68% 100%);
                border: 2px solid #102a2b;
                box-shadow: 0 9px 0 rgba(12, 29, 30, 0.18), 0 10px 20px rgba(12, 29, 30, 0.28), 0 0 12px rgba(201, 243, 107, 0.55);
            background-image: radial-gradient(circle at 92% 4%, rgba(201, 243, 107, 0.22), transparent 24rem), radial-gradient(circle at 4% 72%, rgba(13, 148, 136, 0.08), transparent 28rem);
        }
        .stApp p, .stApp label, .stApp [data-testid="stMarkdownContainer"] { color: #243b3b; }
        .stApp .stCaption, .stApp [data-testid="stCaptionContainer"] { color: #4d6664 !important; font-size: 0.9rem; }
        header[data-testid="stHeader"] { background: #102a2b; }
        header[data-testid="stHeader"] *, header[data-testid="stHeader"] button, header[data-testid="stHeader"] button svg { color: #dff7ef !important; fill: #dff7ef; }
        h1, h2, h3, h4, .stTabs [data-baseweb="tab"] { font-family: 'Space Grotesk', sans-serif; }
                left: 38px;
                top: -19px;
                width: 72px;
                height: 25px;
                border-radius: 65% 75% 10% 10%;
                background: linear-gradient(135deg, #c9f1ec 0 38%, #276b73 39% 76%, #102a2b 77% 100%);
                border: 3px solid #102a2b;
                transform: skewX(-12deg);
                box-shadow: inset -15px 0 0 rgba(8, 35, 40, 0.35);
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] label p,
                right: 20px;
                top: 8px;
                color: #efffc0;
                font-size: 0.9rem;
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
                text-shadow: 0 0 7px #c9f36b;
        [data-testid="stSidebar"] [data-baseweb="select"],
            .motion-car + * { position: relative; }
        [data-testid="stSidebar"] [data-baseweb="select"] *,
        [data-testid="stSidebar"] [data-testid="stSlider"] *,
        [data-testid="stSidebar"] [data-testid="stNumberInput"] *,
                width: 22px;
                height: 22px;
                border: 5px solid #07181b;
        [data-testid="stSidebar"] textarea {
                background: radial-gradient(circle, #dff7ef 0 18%, #6f9691 20% 35%, #07181b 38% 100%);
            -webkit-text-fill-color: #e7f6ef !important;
        }
            .motion-wheel-left { left: 21px; }
            .motion-wheel-right { right: 21px; }
            color: #102a2b !important;
            -webkit-text-fill-color: #102a2b !important;
        }
        [data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] label { color: #a9c7bc; }
        [data-testid="stSidebar"] img { display: none !important; }
        [data-testid="stSidebar"] {
            background: #ffffff !important;
        }
        [data-testid="stSidebar"] *,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            color: #102a2b !important;
            -webkit-text-fill-color: #102a2b !important;
        }
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            color: #4d6664 !important;
            -webkit-text-fill-color: #4d6664 !important;
        }
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] textarea,
        [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: #ffffff !important;
            border-color: #9bd8c5 !important;
            color: #102a2b !important;
            -webkit-text-fill-color: #102a2b !important;
        }
        [data-testid="stSidebar"] hr { border-color: rgba(223, 247, 239, 0.18); }
        [data-testid="stSidebar"] img { border-radius: 14px; border: 1px solid rgba(223, 247, 239, 0.22); }
        [data-testid="stSidebar"] [data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(223, 247, 239, 0.15);
            border-radius: 10px;
        }
        section[data-testid="stSidebar"] {
            background: #102a2b !important;
        }
        section[data-testid="stSidebar"] div,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
        section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            color: #f5fff9 !important;
            -webkit-text-fill-color: #f5fff9 !important;
        }
        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] textarea,
        section[data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: #174444 !important;
            border-color: #75bbaa !important;
            color: #f5fff9 !important;
            -webkit-text-fill-color: #f5fff9 !important;
        }
        section[data-testid="stSidebar"] input::placeholder,
        section[data-testid="stSidebar"] textarea::placeholder {
            color: #b9d9cc !important;
            -webkit-text-fill-color: #b9d9cc !important;
        }
        section[data-testid="stSidebar"] [role="option"],
        section[data-testid="stSidebar"] [role="listbox"] {
            color: #102a2b !important;
            -webkit-text-fill-color: #102a2b !important;
        }
        .hero-shell {
            position: relative;
            overflow: hidden;
            min-height: 265px;
            bottom: 2px;
            width: 190px;
            height: 86px;
            animation: drive-across var(--drive-duration, 10s) linear infinite;
            filter: drop-shadow(0 10px 8px rgba(12, 29, 30, 0.35));
        }
        .motion-car img {
            display: block;
            width: 100%;
            height: 100%;
            object-fit: contain;
            margin-bottom: 1.6rem;
            box-shadow: 0 18px 45px rgba(16, 42, 43, 0.16);
            content: none;
        }
            background-size: 42px 42px;
            mask-image: linear-gradient(90deg, black, transparent 78%);
            content: none;
            position: absolute;
            top: -120px;
            border: 42px solid rgba(201, 243, 107, 0.18);
            border-radius: 50%;
        }
        .hero-kicker { color: var(--lime); font-size: 0.76rem; font-weight: 700; letter-spacing: 0.13em; text-transform: uppercase; margin-bottom: 0.75rem; }
        h1.hero-title, h1.hero-title span { color: #f5fff9 !important; font-family: 'Space Grotesk', sans-serif; font-size: clamp(2rem, 4vw, 3.65rem); line-height: 1.02; letter-spacing: -0.04em; max-width: 780px; margin: 0; }
        .hero-shell .hero-copy { color: #c4e3d7 !important; font-size: 1rem; line-height: 1.6; max-width: 680px; margin: 1rem 0 0; }
        .hero-status { display: inline-flex; align-items: center; gap: 0.5rem; color: #dff7ef; background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.16); border-radius: 999px; padding: 0.45rem 0.75rem; margin-top: 1.5rem; font-size: 0.78rem; font-weight: 600; }
        .hero-status::before { content: ''; width: 7px; height: 7px; border-radius: 50%; background: var(--lime); box-shadow: 0 0 0 4px rgba(201, 243, 107, 0.16); }
        .motion-road {
            position: relative;
            height: 112px;
            overflow: hidden;
            margin: -0.65rem 0 1.7rem;
            border: 1px solid #c9e3d8;
            border-radius: 16px;
            background: linear-gradient(180deg, #dff7ef 0 43%, #9bc8b8 44% 48%, #294c4c 49% 100%);
            box-shadow: 0 10px 24px rgba(16, 42, 43, 0.1);
        }
        .motion-road::before {
            content: '';
            position: absolute;
            left: 0;
            right: 0;
            bottom: 15px;
            height: 4px;
            background: repeating-linear-gradient(90deg, #f5fff9 0 48px, transparent 48px 82px);
            opacity: 0.85;
            animation: road-rush 0.42s linear infinite;
        }
        .motion-road::after {
            content: '';
            position: absolute;
            left: 0;
            right: 0;
            top: 0;
            height: 43%;
            background: radial-gradient(circle at 16% 40%, rgba(255,255,255,0.9) 0 16px, transparent 17px), radial-gradient(circle at 19% 40%, rgba(255,255,255,0.72) 0 11px, transparent 12px), radial-gradient(circle at 76% 30%, rgba(255,255,255,0.85) 0 13px, transparent 14px);
        }
        .motion-car {
            position: absolute;
            z-index: 2;
            left: 2%;
            bottom: 12px;
            width: 150px;
            height: 38px;
            border-radius: 48% 58% 12% 15% / 70% 78% 25% 28%;
            background: linear-gradient(165deg, #d9ff78 0 17%, #50d5b6 18% 42%, #0d9488 43% 67%, #07383d 68% 100%);
            border: 2px solid #102a2b;
            box-shadow: 0 8px 0 rgba(12, 29, 30, 0.18), 0 10px 20px rgba(12, 29, 30, 0.28);
            animation: drive-across var(--drive-duration, 10s) linear infinite;
            filter: drop-shadow(0 0 8px rgba(201, 243, 107, 0.75));
            will-change: transform;
        }
        .motion-car::before {
            content: '';
            position: absolute;
            left: 38px;
            top: -19px;
            width: 72px;
            height: 25px;
            border-radius: 65% 75% 10% 10%;
            background: linear-gradient(135deg, #c9f1ec 0 38%, #276b73 39% 76%, #102a2b 77% 100%);
            border: 3px solid #102a2b;
            transform: skewX(-12deg);
        }
        .motion-car::after {
            content: '⚡';
            position: absolute;
            right: 20px;
            top: 8px;
            color: #efffc0;
            font-size: 0.9rem;
            text-shadow: 0 0 7px #c9f36b;
            font-weight: 700;
        }
        .motion-spoiler {
            position: absolute;
            left: 5px;
            top: 1px;
            width: 26px;
            height: 7px;
            border-radius: 4px;
            background: #102a2b;
            box-shadow: 0 4px 0 #c9f36b;
            transform: skewX(-18deg);
        }
        .motion-intake {
            position: absolute;
            left: 48px;
            bottom: 5px;
            width: 26px;
            height: 8px;
            border-radius: 2px 9px 2px 8px;
            background: #06171a;
            transform: skewX(-22deg);
            box-shadow: inset 0 0 0 2px rgba(201, 243, 107, 0.35);
        }
        .motion-headlight {
            position: absolute;
            right: 8px;
            top: 13px;
            width: 17px;
            height: 5px;
            border-radius: 70% 15% 15% 70%;
            background: #f7ffd3;
            box-shadow: 0 0 8px 2px rgba(201, 243, 107, 0.9);
            transform: skewX(-24deg);
        }
        .motion-headlight-right { top: 23px; opacity: 0.82; }
        .motion-wheel {
            position: absolute;
            bottom: -8px;
            width: 22px;
            height: 22px;
            border: 5px solid #07181b;
            border-radius: 50%;
            background: radial-gradient(circle, #dff7ef 0 18%, #6f9691 20% 35%, #07181b 38% 100%);
            animation: wheel-spin 0.45s linear infinite;
        }
        .motion-wheel-left { left: 21px; }
        .motion-wheel-right { right: 21px; }
        @keyframes drive-across {
            0% { transform: translateX(0) translateY(1px) scale(0.96) rotate(-1deg); }
            8% { transform: translateX(7vw) translateY(-2px) scale(1.02) rotate(1deg); }
            72% { transform: translateX(68vw) translateY(1px) scale(1) rotate(-1deg); }
            100% { transform: translateX(calc(100vw - 5%)) translateY(-1px) scale(0.98) rotate(1deg); }
        }
        @keyframes road-rush {
            from { background-position: 0 0; }
            to { background-position: -130px 0; }
        }
        @keyframes wheel-spin {
            to { transform: rotate(360deg); }
        }
        @media (prefers-reduced-motion: reduce) {
            .motion-car, .motion-wheel, .motion-road::before { animation-play-state: paused; }
        }
        @media (max-width: 640px) {
            .motion-road { height: 92px; margin-bottom: 1.2rem; }
            .motion-car { transform: scale(0.86); transform-origin: left bottom; animation-duration: 4.2s; }
        }
        .page-intro {
            display: flex;
            justify-content: space-between;
            gap: 1.5rem;
            align-items: flex-end;
            border-bottom: 1px solid var(--line);
            padding: 0.35rem 0 1.1rem;
            margin-bottom: 1.25rem;
        }
        .page-intro h3 { margin: 0 0 0.35rem; color: var(--ink); }
        .page-intro p { margin: 0; color: var(--muted); line-height: 1.55; max-width: 760px; }
        .context-chip {
            white-space: nowrap;
            color: #0b6f66;
            background: #dff7ef;
            border: 1px solid #b9e8d8;
            border-radius: 999px;
            padding: 0.45rem 0.75rem;
            font-size: 0.75rem;
            font-weight: 700;
        }
        .insight-card {
            background: #ffffff;
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 0.9rem 1rem;
            min-height: 88px;
        }
        .insight-label { color: var(--teal); font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
        .insight-text { color: var(--ink); font-size: 0.9rem; line-height: 1.45; margin-top: 0.35rem; }
        .welcome-card {
            background: rgba(255,255,255,0.82);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 1.1rem 1.15rem;
            min-height: 128px;
            box-shadow: 0 8px 22px rgba(16,42,43,0.045);
        }
        .welcome-number { color: #8ab31f; font-family: 'Space Grotesk', sans-serif; font-size: 1.65rem; font-weight: 700; }
        .welcome-card h4 { color: var(--ink); margin: 0.25rem 0 0.35rem; }
        .welcome-card p { color: var(--muted); font-size: 0.84rem; line-height: 1.45; margin: 0; }
        .welcome-lead {
            background: #102a2b;
            border-radius: 16px;
            padding: 1.35rem 1.5rem;
            margin-bottom: 1rem;
        }
        .welcome-lead h2 { color: #f5fff9; margin: 0.2rem 0 0.55rem; font-size: clamp(1.35rem, 2.2vw, 2rem); }
        .welcome-lead p { color: #c4e3d7; line-height: 1.55; margin: 0; }
        .stLinkButton > a { width: 100%; justify-content: center; border-radius: 8px; border: 1px solid #9bd8c5; color: #0b6f66; font-weight: 700; background: #effbf6; }
        .stLinkButton > a:hover { border-color: var(--teal); color: #075e57; }
        .price-card { background: #102a2b; color: #effbf6; border-radius: 14px; padding: 1.2rem 1.35rem; min-height: 120px; }
        .price-card .price-label { color: #a9c7bc; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; }
        .price-card .price-value { color: #c9f36b; font-family: 'Space Grotesk', sans-serif; font-size: 1.75rem; font-weight: 700; margin-top: 0.4rem; }
        .price-card .price-note { color: #c4e3d7; font-size: 0.8rem; margin-top: 0.3rem; }
        .stButton > button, .stDownloadButton > button {
            border-radius: 8px;
            border: 1px solid #9bd8c5;
            color: #0b6f66;
            font-weight: 700;
            background: #effbf6;
        }
        .stButton > button:hover, .stDownloadButton > button:hover { border-color: var(--teal); color: #075e57; }
        div[data-testid="stMetric"] { background: #ffffff; border: 1px solid var(--line); border-radius: 12px; padding: 0.85rem 1rem; }
        div[data-testid="stMetricLabel"] { color: var(--muted); }
        div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
        .app-footer { text-align: center; margin-top: 3rem; padding: 1.2rem; color: var(--muted); font-size: 0.78rem; border-top: 1px solid var(--line); }
        .metric-card {
            position: relative;
            overflow: hidden;
            background: #ffffff;
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 8px 24px rgba(16, 42, 43, 0.05);
            margin-bottom: 12px;
            transition: all 0.2s ease-in-out;
        }
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--teal), #7dd3c0);
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 28px rgba(16, 42, 43, 0.1);
            border-color: #9bd8c5;
        }
        .metric-title {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--muted);
            font-weight: 600;
            margin-bottom: 4px;
        }
        .metric-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.9rem;
            font-weight: 700;
            color: var(--ink);
            margin-bottom: 4px;
        }
        .metric-delta {
            font-size: 0.82rem;
            font-weight: 600;
        }
        .delta-pos { color: #10b981; }
        .delta-neg { color: #ef4444; }
        .delta-neu { color: #64748b; }
        
        .section-header {
            border-left: 4px solid var(--teal);
            padding: 0.15rem 0 0.15rem 12px;
            margin-top: 15px;
            margin-bottom: 15px;
        }
        .stTabs [data-baseweb="tab-list"] { gap: 0.35rem; border-bottom: 1px solid var(--line); }
        .stTabs [data-baseweb="tab"] { color: var(--muted); font-weight: 600; padding: 0.75rem 0.9rem; }
        .stTabs [data-baseweb="tab"] * { color: var(--muted) !important; }
        .stTabs [aria-selected="true"] { color: var(--teal); }
        .stTabs [aria-selected="true"] * { color: var(--teal) !important; }
        .stTabs [data-baseweb="tab"] p { font-size: 0.92rem; font-weight: 700; }
        div[data-testid="stSlider"] label p, div[data-testid="stSelectSlider"] label p { color: #243b3b !important; font-weight: 700; }
        div[data-testid="stSlider"] [data-testid="stThumbValue"] { color: #0b6f66; font-weight: 700; }
        .stPlotlyChart {
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 0.35rem;
            box-shadow: 0 8px 22px rgba(16, 42, 43, 0.045);
        }
        [data-testid="stAlert"] { border-radius: 12px; border-left-width: 4px; }
        [data-testid="stExpander"] { border-color: var(--line); border-radius: 12px; background: rgba(255,255,255,0.72); }
        [data-testid="stFileUploader"] { border: 1px dashed #75bbaa; border-radius: 10px; padding: 0.35rem; }
        [data-testid="stTable"] { background: #ffffff; border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
        [data-testid="stTable"] th { background: #e5f4ee !important; color: #102a2b !important; font-weight: 700; }
        [data-testid="stTable"] td { color: #243b3b !important; background: #ffffff !important; }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            font-size: 0.75rem;
            font-weight: 600;
            border-radius: 6px;
        }
        .badge-high { background-color: #fee2e2; color: #dc2626; }
        .badge-med { background-color: #fef3c7; color: #d97706; }
        .badge-low { background-color: #d1fae5; color: #059669; }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
        section[data-testid="stSidebar"] div[data-testid="stSlider"] label p,
        section[data-testid="stSidebar"] div[data-testid="stSelectSlider"] label p,
        section[data-testid="stSidebar"] [data-testid="stRadioOption"],
        section[data-testid="stSidebar"] [data-testid="stRadioOption"] *,
        section[data-testid="stSidebar"] [data-testid="stThumbValue"],
        section[data-testid="stSidebar"] span[data-heading-text] {
            color: #f5fff9 !important;
            -webkit-text-fill-color: #f5fff9 !important;
        }
        @media (max-width: 800px) {
            .block-container { padding: 1rem 0.75rem 3rem; }
            .hero-shell { min-height: 230px; padding: 2rem 1.4rem; border-radius: 16px; }
            .hero-title { font-size: 2.25rem; }
            .hero-copy { font-size: 0.92rem; }
            .page-intro { display: block; }
            .context-chip { display: inline-block; margin-top: 0.8rem; }
        }
        /* Final surface and vehicle overrides keep the dashboard readable after theme updates. */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main,
        [data-testid="stAppViewContainer"] > .main > div, .stApp {
            background: #ffffff !important;
            background-image: none !important;
        }
        .motion-road {
            height: 112px !important;
            background: linear-gradient(180deg, #effff9 0 43%, #9bc8b8 44% 48%, #294c4c 49% 100%) !important;
        }
        .motion-car {
            left: 2% !important;
            bottom: 12px !important;
            width: 122px !important;
            height: 35px !important;
            border-radius: 24px 28px 8px 8px !important;
            background: linear-gradient(150deg, #c9f36b 0 52%, #0d9488 53% 100%) !important;
            border: 0 !important;
            box-shadow: 0 8px 0 rgba(12, 29, 30, 0.18), 0 10px 20px rgba(12, 29, 30, 0.28) !important;
            filter: none !important;
        }
        .motion-car::before {
            content: '' !important;
            left: 27px !important;
            top: -16px !important;
            width: 61px !important;
            height: 22px !important;
            border-radius: 28px 28px 5px 5px !important;
            background: linear-gradient(135deg, #b7e8e2 0 48%, #5ca8a0 49% 100%) !important;
            border: 3px solid #0d9488 !important;
            transform: none !important;
            box-shadow: none !important;
        }
        .motion-car::after {
            content: '⚡' !important;
            right: 12px !important;
            top: 7px !important;
            left: auto !important;
            bottom: auto !important;
            width: auto !important;
            height: auto !important;
            color: #102a2b !important;
            background: transparent !important;
            box-shadow: none !important;
            filter: none !important;
            font-size: 0.85rem !important;
        }
        .motion-spoiler, .motion-intake, .motion-headlight { display: none !important; }
        .motion-wheel {
            bottom: -8px !important;
            width: 20px !important;
            height: 20px !important;
            border: 5px solid #102a2b !important;
            background: #dff7ef !important;
        }
        .motion-wheel-left { left: 18px !important; }
        .motion-wheel-right { right: 18px !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
        .stApp [data-testid="stMarkdownContainer"] h1,
        .stApp [data-testid="stMarkdownContainer"] h2,
        .stApp [data-testid="stMarkdownContainer"] h3,
        .stApp [data-testid="stMarkdownContainer"] h4,
        .stApp [data-testid="stMarkdownContainer"] h5,
        .stApp [data-testid="stMarkdownContainer"] h6 {
            color: #102a2b !important;
            -webkit-text-fill-color: #102a2b !important;
        }
        .stApp .stTabs [data-baseweb="tab"],
        .stApp .stTabs [data-baseweb="tab"] p,
        .stApp .stTabs [role="tab"],
        .stApp .stTabs [role="tab"] p {
            color: #102a2b !important;
            -webkit-text-fill-color: #102a2b !important;
        }
        .stApp .stTabs [aria-selected="true"],
        .stApp .stTabs [aria-selected="true"] p {
            color: #0d9488 !important;
            -webkit-text-fill-color: #0d9488 !important;
        }
        .stApp [data-testid="stCaptionContainer"],
        .stApp [data-testid="stCaptionContainer"] p,
        .stApp [data-testid="stMarkdownContainer"] p {
            color: #3f5b5b !important;
            -webkit-text-fill-color: #3f5b5b !important;
        }
        .stApp .welcome-lead h2,
        .stApp .welcome-lead p,
        .stApp .welcome-lead .hero-kicker {
            color: #f5fff9 !important;
            -webkit-text-fill-color: #f5fff9 !important;
        }
        .stApp .welcome-lead p { color: #c4e3d7 !important; }
    </style>
    """


def build_adoption_forecast_chart(forecast_df: pd.DataFrame, scenario_name: str = "Baseline") -> go.Figure:
    """
    Renders an interactive historical + projected EV fleet adoption curve with confidence intervals.
    """
    fig = go.Figure()

    hist_data = forecast_df[~forecast_df["is_forecast"]]
    future_data = forecast_df[forecast_df["is_forecast"]]

    # Confidence Interval Shading for Forecast
    if not future_data.empty:
        combined_future = pd.concat([hist_data.iloc[-1:], future_data])
        fig.add_trace(go.Scatter(
            x=pd.concat([combined_future["year"], combined_future["year"][::-1]]),
            y=pd.concat([combined_future["fleet_upper_bound"], combined_future["fleet_lower_bound"][::-1]]),
            fill="toself",
            fillcolor="rgba(13, 148, 136, 0.14)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            showlegend=True,
            name="Forecast Confidence Range (±8-16%)"
        ))

    # Historical Line
    fig.add_trace(go.Scatter(
        x=hist_data["year"],
        y=hist_data["cumulative_fleet"],
        mode="lines+markers",
        name="Historical Fleet Registrations",
        line=dict(color="#0284C7", width=3.5),
        marker=dict(size=7, color="#0284C7")
    ))

    # Forecast Line
    if not future_data.empty:
        bridge_data = pd.concat([hist_data.iloc[-1:], future_data])
        fig.add_trace(go.Scatter(
            x=bridge_data["year"],
            y=bridge_data["cumulative_fleet"],
            mode="lines+markers",
            name=f"Projected Adoption ({scenario_name})",
            line=dict(color="#0D9488", width=3.5, dash="dash"),
            marker=dict(size=7, color="#0D9488", symbol="diamond")
        ))

    fig.update_layout(
        title="<b>Cumulative EV Fleet Adoption & Multi-Year Projection</b>",
        xaxis_title="Calendar Year",
        yaxis_title="Total Registered Electric Vehicles",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=30, t=60, b=40)
    )
    return fig


def build_powertrain_split_chart(yearly_df: pd.DataFrame) -> go.Figure:
    """
    Renders stacked bar chart showing BEV vs PHEV volume and percentage evolution.
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=yearly_df["year"],
        y=yearly_df["bev_count"],
        name="Battery Electric (BEV)",
        marker_color="#0D9488"
    ))

    fig.add_trace(go.Bar(
        x=yearly_df["year"],
        y=yearly_df["phev_count"],
        name="Plug-in Hybrid (PHEV)",
        marker_color="#38BDF8"
    ))

    fig.update_layout(
        barmode="stack",
        title="<b>Annual Powertrain Mix: BEV vs. PHEV</b>",
        xaxis_title="Year",
        yaxis_title="Vehicles Registered",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=30, t=60, b=40)
    )
    return fig


def build_top_makes_chart(top_makes_df: pd.DataFrame) -> go.Figure:
    """
    Renders horizontal bar chart of leading automakers.
    """
    df_sorted = top_makes_df.sort_values(by="Count", ascending=True)
    fig = px.bar(
        df_sorted,
        x="Count",
        y="Make",
        orientation="h",
        text="Count",
        title="<b>Top EV Manufacturers by Fleet Volume</b>",
        color="Count",
        color_continuous_scale="Teal"
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig.update_layout(
        template="plotly_white",
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


def build_infrastructure_growth_chart(infra_df: pd.DataFrame) -> go.Figure:
    """
    Renders stacked bar chart of Level 2 and DC Fast Charger requirements.
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=infra_df["year"],
        y=infra_df["req_l2_ports"],
        name="Level 2 Public & Workplace Ports",
        marker_color="#0D9488"
    ))

    fig.add_trace(go.Bar(
        x=infra_df["year"],
        y=infra_df["req_dcfc_ports"],
        name="DC Fast Charging (DCFC) Ports",
        marker_color="#F59E0B"
    ))

    fig.update_layout(
        barmode="stack",
        title="<b>Required Charging Network Ports (Level 2 vs DC Fast)</b>",
        xaxis_title="Year",
        yaxis_title="Total Required Ports",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=30, t=60, b=40)
    )
    return fig


def build_grid_load_curve(profile_df: pd.DataFrame) -> go.Figure:
    """
    Renders 24-hour diurnal charging load profile across residential, workplace, and highway charging.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=profile_df["Time_Label"],
        y=profile_df["Residential_MW"],
        name="Residential (Overnight)",
        mode="lines",
        stackgroup="one",
        line=dict(color="#3B82F6")
    ))

    fig.add_trace(go.Scatter(
        x=profile_df["Time_Label"],
        y=profile_df["Workplace_MW"],
        name="Workplace & Commercial (Midday)",
        mode="lines",
        stackgroup="one",
        line=dict(color="#10B981")
    ))

    fig.add_trace(go.Scatter(
        x=profile_df["Time_Label"],
        y=profile_df["DCFC_Public_MW"],
        name="Highway DC Fast Charging",
        mode="lines",
        stackgroup="one",
        line=dict(color="#F59E0B")
    ))

    fig.update_layout(
        title="<b>Simulated 24-Hour Diurnal Grid Power Load Profile (MW)</b>",
        xaxis_title="Time of Day",
        yaxis_title="Charging Demand (MW)",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=30, t=60, b=40)
    )
    return fig


def build_tco_comparison_chart(tco_df: pd.DataFrame) -> go.Figure:
    """
    Renders 10-year cumulative TCO line chart comparing Electric Vehicle vs ICE Gas Vehicle.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=tco_df["Year"],
        y=tco_df["EV_Cumulative_TCO"],
        mode="lines+markers",
        name="Electric Vehicle (EV) TCO",
        line=dict(color="#0D9488", width=3),
        marker=dict(size=6)
    ))

    fig.add_trace(go.Scatter(
        x=tco_df["Year"],
        y=tco_df["ICE_Cumulative_TCO"],
        mode="lines+markers",
        name="Gasoline Internal Combustion (ICE) TCO",
        line=dict(color="#EF4444", width=3, dash="dot"),
        marker=dict(size=6)
    ))

    # Crossover breakeven indicator
    breakeven = tco_df.attrs.get("breakeven_year", "N/A")
    title_suffix = f" (Breakeven in Year {breakeven})" if breakeven != "N/A" and breakeven != "10+" else ""

    fig.update_layout(
        title=f"<b>10-Year Cumulative Total Cost of Ownership (TCO) Comparison{title_suffix}</b>",
        xaxis_title="Years of Vehicle Ownership",
        yaxis_title="Cumulative Spend (₹)",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=30, t=60, b=40)
    )
    return fig


def build_financial_market_chart(fin_df: pd.DataFrame) -> go.Figure:
    """
    Renders cumulative market valuation ($B) and annual charging revenue ($M).
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=fin_df["year"],
        y=fin_df["charging_revenue_m"],
        name="Annual Charging Revenue (₹M)",
        marker_color="#10B981",
        yaxis="y2"
    ))

    fig.add_trace(go.Scatter(
        x=fin_df["year"],
        y=fin_df["cum_market_val_b"],
        name="Cumulative Fleet Value (₹B)",
        line=dict(color="#6366F1", width=3.5),
        mode="lines+markers",
        yaxis="y1"
    ))

    fig.update_layout(
        title="<b>Economic Expansion: Fleet Value vs. Public Charging Revenue</b>",
        xaxis_title="Year",
        yaxis=dict(
            title=dict(text="Cumulative Fleet Market Value (₹B)", font=dict(color="#6366F1")),
            tickfont=dict(color="#6366F1")
        ),
        yaxis2=dict(
            title=dict(text="Annual Public Charging Revenue (₹M)", font=dict(color="#10B981")),
            tickfont=dict(color="#10B981"),
            overlaying="y",
            side="right"
        ),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


def build_sentiment_donut(sentiment_dist: dict) -> go.Figure:
    """
    Renders donut chart for overall customer sentiment distribution.
    """
    labels = list(sentiment_dist.keys())
    values = list(sentiment_dist.values())
    colors = ["#10B981", "#94A3B8", "#EF4444"]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors),
        textinfo="label+percent",
        insidetextorientation="radial"
    )])

    fig.update_layout(
        title="<b>Overall Customer Sentiment Distribution</b>",
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )
    return fig


def build_category_satisfaction_chart(cat_df: pd.DataFrame) -> go.Figure:
    """
    Renders horizontal stacked bar chart showing positive, neutral, and negative percentage per category.
    """
    df_sorted = cat_df.sort_values(by="Avg_Rating", ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df_sorted["Category"],
        x=df_sorted["Positive_Pct"],
        name="Positive %",
        orientation="h",
        marker_color="#10B981"
    ))

    fig.add_trace(go.Bar(
        y=df_sorted["Category"],
        x=df_sorted["Neutral_Pct"],
        name="Neutral %",
        orientation="h",
        marker_color="#CBD5E1"
    ))

    fig.add_trace(go.Bar(
        y=df_sorted["Category"],
        x=df_sorted["Negative_Pct"],
        name="Negative %",
        orientation="h",
        marker_color="#EF4444"
    ))

    fig.update_layout(
        barmode="stack",
        title="<b>Sentiment Breakdown by Feature Category</b>",
        xaxis_title="Percentage (%)",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=30, t=60, b=40)
    )
    return fig


def build_charging_points_map(user_lat: float, user_lon: float, user_city: str, stations_df: pd.DataFrame) -> go.Figure:
    """
    Renders an interactive map centered on the user location with nearby EV charging stations.
    Compatible with Plotly 7+ (Scattermap) and Plotly 5/6 (Scattermapbox).
    """
    fig = go.Figure()
    top_stations = stations_df.head(20).copy()

    scatter_cls = getattr(go, "Scattermap", getattr(go, "Scattermapbox", None))

    # Add Charging Stations
    if not top_stations.empty:
        fig.add_trace(scatter_cls(
            lat=top_stations["latitude"],
            lon=top_stations["longitude"],
            mode="markers+text",
            marker=dict(size=12, color="#0D9488"),
            text=top_stations["name"],
            textposition="top right",
            customdata=top_stations[["address", "city", "type", "power_kw", "Distance from you (km)"]],
            hovertemplate="<b>%{text}</b><br>%{customdata[0]}, %{customdata[1]}<br>Type: %{customdata[2]} (%{customdata[3]} kW)<br><b>%{customdata[4]} km away</b><extra></extra>",
            name="Charging Stations"
        ))

    # Add User Location Pin
    fig.add_trace(scatter_cls(
        lat=[user_lat],
        lon=[user_lon],
        mode="markers",
        marker=dict(size=16, color="#EF4444"),
        hovertext=[f"Your Location: {user_city} ({user_lat:.4f}, {user_lon:.4f})"],
        name="Your Location"
    ))

    map_cfg = dict(
        style="open-street-map",
        center=dict(lat=user_lat, lon=user_lon),
        zoom=7 if (not top_stations.empty and top_stations.iloc[0]["Distance from you (km)"] < 80) else 5
    )

    if hasattr(go.Layout(), "map"):
        fig.update_layout(map=map_cfg)
    else:
        fig.update_layout(mapbox=map_cfg)

    fig.update_layout(
        title="<b>Interactive Map: Your Location & Nearest Charging Stations</b>",
        margin=dict(l=0, r=0, t=35, b=0),
        height=400,
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


