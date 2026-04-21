from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
except ImportError:
    from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx


if __name__ == "__main__" and get_script_run_ctx() is None:
    subprocess.run([sys.executable, "-m", "streamlit", "run", __file__], check=False)
    sys.exit()

st.set_page_config(page_title="War Impact On Trade", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    :root {
        --bg-main: #040507;
        --bg-shell: #090b10;
        --bg-secondary: #0d1016;
        --bg-tertiary: #121722;
        --bg-elevated: #171d29;
        --border: rgba(255,255,255,0.10);
        --border-soft: rgba(255,255,255,0.07);
        --text-primary: #f7f9fc;
        --text-secondary: #a4aec3;
        --text-dim: #6f7b92;
        --accent: #32d7ff;
        --accent-2: #7d6bff;
        --accent-3: #ff53b5;
        --accent-4: #ffb84f;
        --shadow: 0 24px 48px rgba(0, 0, 0, 0.42);
        --glow: 0 0 0 1px rgba(255,255,255,0.03), 0 0 56px rgba(125, 107, 255, 0.08);
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body, .stApp {
        background: linear-gradient(180deg, #090b11 0%, #040507 100%);
        color: var(--text-primary);
        font-family: "Inter", "Segoe UI Variable Display", "SF Pro Display", Arial, sans-serif;
    }
    .block-container {
        max-width: 1580px;
        padding: 1.2rem 1.8rem 2rem 1.8rem;
        background: transparent;
    }
    [data-testid="stSidebar"] {
        background: #0b0e14;
        border-right: 1px solid var(--border-soft);
    }
    [data-testid="stSidebar"] > div:first-child {
        background: #0b0e14;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: var(--text-primary); font-weight: 600; }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: var(--text-secondary); font-size: 0.9rem; }
    [data-testid="stSidebar"] [data-baseweb="radio"] > div { gap: 0.45rem; }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        background:
            linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0)),
            linear-gradient(135deg, rgba(50,215,255,0.03), rgba(125,107,255,0.03) 52%, rgba(255,83,181,0.04)),
            var(--bg-tertiary);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 0.7rem 0.8rem;
        transition: all 0.15s ease;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.025);
        pointer-events: auto !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        border-color: rgba(125, 107, 255, 0.22);
        background:
            linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0)),
            linear-gradient(135deg, rgba(50,215,255,0.05), rgba(125,107,255,0.04) 52%, rgba(255,83,181,0.06)),
            var(--bg-elevated);
        transform: translateY(-1px);
    }
    [data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] {
        border-color: rgba(125, 107, 255, 0.34);
        box-shadow:
            inset 0 0 0 1px rgba(125, 107, 255, 0.16),
            0 0 0 1px rgba(255, 83, 181, 0.06),
            0 0 30px rgba(125, 107, 255, 0.10);
    }
    h1, h2, h3, h4 { color: var(--text-primary); }
    h1 { font-weight: 800; font-size: 1.7rem; margin: 0; }
    h2 { font-weight: 600; font-size: 1.4rem; margin: 1.2rem 0 0.8rem 0; }
    h3 { font-weight: 600; font-size: 1.1rem; margin: 1rem 0 0.6rem 0; }
    h4 { font-weight: 500; font-size: 1rem; margin: 0.8rem 0 0.4rem 0; }
    p { color: var(--text-secondary); line-height: 1.5; }
    div[data-testid="stSelectbox"] [data-baseweb="select"] {
        background:
            linear-gradient(180deg, rgba(255,255,255,0.025), rgba(255,255,255,0)),
            linear-gradient(135deg, rgba(50,215,255,0.03), rgba(125,107,255,0.03) 50%, rgba(255,83,181,0.03)),
            var(--bg-tertiary) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 8px !important;
        min-height: 48px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
    }
    div[data-baseweb="popover"] ul {
        background: #111621 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 8px !important;
    }
    div[data-testid="stDataFrame"] {
        background-color: var(--bg-tertiary) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 8px !important;
        box-shadow: var(--glow);
    }
    div[data-testid="stDataFrameRowHeaderCell"] { background-color: var(--bg-secondary) !important; }
    [data-testid="stMetric"] {
        background:
            radial-gradient(circle at top right, rgba(255,83,181,0.13), transparent 26%),
            radial-gradient(circle at 22% 10%, rgba(50,215,255,0.12), transparent 24%),
            radial-gradient(circle at 50% 0%, rgba(125,107,255,0.10), transparent 18%),
            linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0)),
            var(--bg-tertiary);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 1.1rem 1.2rem;
        box-shadow: var(--shadow);
    }
    [data-testid="stMetricLabel"] p {
        color: var(--text-secondary);
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="stMetricValue"] { color: var(--text-primary); font-size: 1.7rem; font-weight: 700; margin-top: 0.4rem; }
    [data-testid="stAlert"] {
        background:
            linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0)),
            var(--bg-tertiary);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        color: var(--text-secondary);
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0)), transparent;
        border: 1px solid transparent;
        border-radius: 8px 8px 0 0;
        color: var(--text-secondary);
        font-weight: 600;
        padding: 0.75rem 1rem;
    }
    # [data-testid="stTabs"] [aria-selected="true"] {
        color: var(--text-primary);
        border: 1px solid rgba(125, 107, 255, 0.28) !important;
        background:
            linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0)),
            linear-gradient(135deg, rgba(50,215,255,0.06), rgba(125,107,255,0.07) 55%, rgba(255,83,181,0.08)),
            var(--bg-tertiary);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.03), 0 0 26px rgba(125,107,255,0.08);
    }
    [data-testid="stTabs"] button p { font-weight: 600; color: inherit; }
    [data-testid="stColumnBlock"] { gap: 1rem; }
    .stDivider { margin: 1.5rem 0; border-color: var(--border) !important; }
    hr { background-color: var(--border); border: none; height: 1px; }
    .topbar {
        height: 68px;
        background:
            radial-gradient(circle at 82% 18%, rgba(255,83,181,0.16), transparent 20%),
            radial-gradient(circle at 18% 18%, rgba(50,215,255,0.10), transparent 20%),
            radial-gradient(circle at 50% -10%, rgba(125,107,255,0.10), transparent 22%),
            linear-gradient(180deg, rgba(255,255,255,0.025), rgba(255,255,255,0)),
            #0f131a;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 1rem 0 1.1rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow);
    }
    .topbar-left, .topbar-right { display: flex; align-items: center; gap: 0.7rem; }
    .topbar-search {
        min-width: 280px;
        height: 38px;
        border-radius: 999px;
        background:
            linear-gradient(135deg, rgba(50,215,255,0.04), rgba(125,107,255,0.04) 55%, rgba(255,83,181,0.05)),
            rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        color: var(--text-dim);
        display: flex;
        align-items: center;
        padding: 0 1rem;
        font-size: 0.84rem;
        font-weight: 500;
    }
    .topbar-icon, .topbar-chip {
        border-radius: 8px;
        background:
            linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0)),
            linear-gradient(135deg, rgba(50,215,255,0.04), rgba(125,107,255,0.04) 55%, rgba(255,83,181,0.04)),
            var(--bg-tertiary);
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
    }
    .topbar-icon {
        width: 34px;
        height: 34px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: var(--text-secondary);
        font-size: 0.82rem;
        font-weight: 700;
    }
    .topbar-brand {
        width: 34px;
        height: 34px;
        border-radius: 8px;
        background: linear-gradient(135deg, var(--accent), var(--accent-2) 48%, var(--accent-3) 76%, var(--accent-4));
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 0.95rem;
        font-weight: 800;
        box-shadow: 0 12px 28px rgba(125, 107, 255, 0.26);
    }
    .topbar-title { color: var(--text-primary); font-size: 0.96rem; font-weight: 700; }
    .topbar-subtitle { color: var(--text-dim); font-size: 0.8rem; margin-top: 0.15rem; }
    .topbar-chip {
        height: 34px;
        min-width: 36px;
        padding: 0 0.9rem;
        color: var(--text-secondary);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.84rem;
        font-weight: 600;
    }
    .topbar-chip.primary {
        color: #070a11;
        background: linear-gradient(135deg, var(--accent), var(--accent-2) 48%, var(--accent-3) 76%, var(--accent-4));
        border-color: transparent;
        box-shadow: 0 12px 28px rgba(125, 107, 255, 0.22);
    }
    .hero {
        background:
            radial-gradient(circle at 78% 22%, rgba(255,83,181,0.16), transparent 22%),
            radial-gradient(circle at 14% 12%, rgba(50,215,255,0.16), transparent 22%),
            radial-gradient(circle at 50% -10%, rgba(125,107,255,0.12), transparent 24%),
            linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0)),
            var(--bg-secondary);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 1.25rem 1.3rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow);
    }
    .eyebrow {
        color: var(--accent);
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.35rem;
    }
    .hero h1 { font-size: 2.08rem; font-weight: 800; color: var(--text-primary); margin-bottom: 0.45rem; }
    .hero p { max-width: 760px; color: var(--text-secondary); font-size: 0.96rem; }
    .method-card, .paper-card, .metrics-card, .map-frame {
        background:
            linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0)),
            linear-gradient(135deg, rgba(50,215,255,0.025), rgba(125,107,255,0.025) 55%, rgba(255,83,181,0.03)),
            var(--bg-secondary);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        box-shadow: var(--shadow);
    }
    .method-card { padding: 0.95rem 1rem; margin-bottom: 1rem; color: var(--text-secondary); }
    .method-card strong { color: var(--text-primary); }
    .map-frame {
        padding: 0.55rem;
        margin-bottom: 1rem;
        background:
            linear-gradient(180deg, rgba(255,255,255,0.018), rgba(255,255,255,0)),
            linear-gradient(135deg, rgba(50,215,255,0.04), rgba(125,107,255,0.03) 50%, rgba(255,83,181,0.04)),
            var(--bg-secondary);
    }
    .paper-card { padding: 1rem 1.1rem; margin-bottom: 1rem; }
    .paper-card h2 { margin: 0 0 0.9rem 0; font-size: 1.15rem; }
    .paper-card h3 { margin: 1rem 0 0.5rem 0; font-size: 1rem; }
    .paper-card p, .paper-card li { color: var(--text-secondary); line-height: 1.7; font-size: 0.95rem; }
    .paper-card ul { padding-left: 1.1rem; margin: 0.55rem 0 0.8rem 0; }
    .paper-card .authors { color: var(--text-primary); font-weight: 600; margin-bottom: 1rem; }
    .metrics-card { padding: 1rem 1.05rem; margin-bottom: 1rem; }
    .metrics-card h3 { margin-top: 0; }
    .small-note { color: var(--text-dim); font-size: 0.82rem; line-height: 1.55; }
    .sidebar-section-label {
        color: var(--text-dim);
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 0.3rem 0 0.8rem 0;
    }
    .stPlotlyChart, div[data-testid="stPlotlyChart"] { border-radius: 8px; overflow: hidden; }
    .stButton button, .stDownloadButton button {
        border-radius: 8px !important;
        background:
            linear-gradient(135deg, rgba(50,215,255,0.14), rgba(125,107,255,0.16) 55%, rgba(255,83,181,0.16)),
            #141927 !important;
        color: #f7f9fc !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        font-weight: 600 !important;
        box-shadow: 0 12px 28px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.03);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda",
    "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas",
    "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin",
    "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei",
    "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon",
    "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia",
    "Comoros", "Costa Rica", "Cote d'Ivoire", "Croatia", "Cuba", "Cyprus",
    "Czechia", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica",
    "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea",
    "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France",
    "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada",
    "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary",
    "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy",
    "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kuwait",
    "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya",
    "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia",
    "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius",
    "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco",
    "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands",
    "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia",
    "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay",
    "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia",
    "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines",
    "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia",
    "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia",
    "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan",
    "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria",
    "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga",
    "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda",
    "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay",
    "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe",
    "Palestine", "Taiwan", "Kosovo", "Western Sahara", "Hong Kong", "Macau", "Vatican City",
    "Puerto Rico",
]

COMMODITIES = ["Grains", "Coal", "Semiconductors", "Petrol", "Fertilizer"]
TRANSPORT_MODES = ["Sea", "Rail", "Road", "Pipeline", "Air"]


@dataclass(frozen=True)
class TensionEdge:
    source: str
    target: str
    intensity: int
    note: str


@dataclass(frozen=True)
class TradeFlow:
    exporter: str
    importer: str
    commodity: str
    modes: tuple[str, ...]
    note: str


SEED_TENSIONS = [
    TensionEdge("Russia", "Ukraine", 5, "Full-scale interstate war."),
    TensionEdge("Israel", "Palestine", 5, "Gaza/West Bank conflict."),
    TensionEdge("Israel", "Iran", 5, "Direct and proxy confrontation."),
    TensionEdge("United States", "Iran", 5, "Direct military confrontation and escalation risk."),
    TensionEdge("Israel", "Lebanon", 4, "Cross-border conflict involving Hezbollah."),
    TensionEdge("Israel", "Syria", 4, "Repeated strikes and spillover risk."),
    TensionEdge("Turkey", "Syria", 4, "Border and northern Syria military operations."),
    TensionEdge("India", "Pakistan", 4, "Kashmir and border crisis risk."),
    TensionEdge("China", "Taiwan", 4, "Cross-strait military pressure."),
    TensionEdge("China", "Philippines", 4, "South China Sea incidents."),
    TensionEdge("China", "India", 3, "Himalayan border standoff risk."),
    TensionEdge("North Korea", "South Korea", 4, "Korean peninsula escalation risk."),
    TensionEdge("Azerbaijan", "Armenia", 3, "Nagorno-Karabakh and border settlement risk."),
    TensionEdge("Serbia", "Kosovo", 3, "Northern Kosovo and recognition disputes."),
    TensionEdge("Morocco", "Western Sahara", 3, "Western Sahara status conflict."),
    TensionEdge("Democratic Republic of the Congo", "Rwanda", 4, "Eastern DRC conflict and M23 accusations."),
    TensionEdge("Ethiopia", "Eritrea", 3, "Post-Tigray and Red Sea security concerns."),
    TensionEdge("Ethiopia", "Somalia", 3, "Port access and Somaliland dispute."),
    TensionEdge("Venezuela", "Guyana", 3, "Essequibo territorial dispute."),
    TensionEdge("United States", "Russia", 4, "Ukraine war and strategic confrontation."),
    TensionEdge("United States", "China", 4, "Taiwan, trade, and military competition."),
    TensionEdge("Greece", "Turkey", 2, "Aegean and eastern Mediterranean disputes."),
    TensionEdge("Egypt", "Ethiopia", 3, "Nile/GERD dispute."),
    TensionEdge("Saudi Arabia", "Yemen", 3, "Yemen conflict and border/drone risk."),
    TensionEdge("Iran", "Saudi Arabia", 3, "Gulf security and proxy competition."),
    TensionEdge("Qatar", "Iran", 2, "Gulf maritime and regional security tension."),
    TensionEdge("United Arab Emirates", "Iran", 3, "Gulf islands and shipping security tension."),
    TensionEdge("Iraq", "Iran", 2, "Border, militia, and regional security pressure."),
    TensionEdge("Syria", "Iraq", 2, "Militant movement and border insecurity."),
    TensionEdge("Lebanon", "Syria", 2, "Border and armed group spillover."),
    TensionEdge("Sudan", "Chad", 3, "Civil-war spillover and refugee pressure."),
    TensionEdge("Mali", "Niger", 2, "Shared Sahel insurgency theater."),
    TensionEdge("Mali", "Burkina Faso", 2, "Shared Sahel insurgency theater."),
    TensionEdge("Niger", "Nigeria", 2, "Lake Chad and Sahel militant movement."),
    TensionEdge("Colombia", "Venezuela", 2, "Border armed groups and political tension."),
    TensionEdge("United States", "Venezuela", 3, "Sanctions and military pressure risk."),
    TensionEdge("Japan", "China", 3, "East China Sea maritime dispute."),
    TensionEdge("Japan", "Russia", 2, "Kuril/Northern Territories dispute."),
    TensionEdge("Cyprus", "Turkey", 2, "Northern Cyprus and maritime claims."),
    TensionEdge("United States", "North Korea", 4, "Nuclear and missile threat escalation."),
    TensionEdge("China", "Vietnam", 3, "South China Sea and land border disputes."),
    TensionEdge("Turkey", "Armenia", 3, "Genocide recognition and border tensions."),
    TensionEdge("Georgia", "Russia", 3, "Abkhazia and South Ossetia occupation."),
    TensionEdge("Ukraine", "Belarus", 3, "Military cooperation and border tensions."),
    TensionEdge("Poland", "Belarus", 2, "Border migrant crisis and sanctions."),
    TensionEdge("Lithuania", "Belarus", 2, "Border migrant crisis and sanctions."),
    TensionEdge("Estonia", "Russia", 3, "NATO border and cyber tensions."),
    TensionEdge("Latvia", "Russia", 3, "NATO border and cyber tensions."),
    TensionEdge("Finland", "Russia", 3, "NATO membership and border tensions."),
    TensionEdge("Sweden", "Russia", 3, "NATO membership and border tensions."),
    TensionEdge("United Kingdom", "Russia", 3, "Ukraine support and sanctions."),
    TensionEdge("France", "Russia", 3, "Ukraine support and sanctions."),
    TensionEdge("Germany", "Russia", 3, "Ukraine support and sanctions."),
    TensionEdge("Italy", "Russia", 3, "Ukraine support and sanctions."),
    TensionEdge("Spain", "Russia", 3, "Ukraine support and sanctions."),
    TensionEdge("Netherlands", "Russia", 3, "Ukraine support and sanctions."),
    TensionEdge("Belgium", "Russia", 3, "Ukraine support and sanctions."),
    TensionEdge("Denmark", "Russia", 3, "Ukraine support and sanctions."),
    TensionEdge("Norway", "Russia", 3, "Ukraine support and sanctions."),
    TensionEdge("Canada", "Russia", 3, "Ukraine support and sanctions."),
    TensionEdge("Australia", "China", 3, "Trade disputes and military presence."),
    TensionEdge("New Zealand", "China", 2, "Trade and regional security."),
    TensionEdge("South Korea", "China", 3, "THAAD deployment and trade tensions."),
    TensionEdge("Hong Kong", "China", 4, "Autonomy and democracy protests."),
    TensionEdge("Macau", "China", 2, "Autonomy issues."),
    TensionEdge("United Kingdom", "China", 3, "Hong Kong and Xinjiang issues."),
    TensionEdge("France", "China", 3, "Taiwan and human rights."),
    TensionEdge("Germany", "China", 3, "Trade and human rights."),
    TensionEdge("Italy", "China", 3, "Belt and Road investments."),
    TensionEdge("Spain", "China", 2, "Regional influence."),
    TensionEdge("Netherlands", "China", 3, "Semiconductor export controls."),
    TensionEdge("Belgium", "China", 2, "Regional influence."),
    TensionEdge("Denmark", "China", 2, "Regional influence."),
    TensionEdge("Norway", "China", 2, "Regional influence."),
    TensionEdge("Canada", "China", 3, "Huawei and trade disputes."),
]

SEED_TRADE_FLOWS = [
    # Petrol (Oil) - 40 routes
    TradeFlow("Russia", "China", "Petrol", ("Pipeline", "Rail", "Sea"), "Major oil and refined-products route."),
    TradeFlow("Saudi Arabia", "China", "Petrol", ("Sea",), "Major Gulf-to-Asia oil route."),
    TradeFlow("Saudi Arabia", "India", "Petrol", ("Sea",), "Major Gulf-to-India oil route."),
    TradeFlow("Saudi Arabia", "Japan", "Petrol", ("Sea",), "Major Gulf-to-East Asia oil route."),
    TradeFlow("Iraq", "China", "Petrol", ("Sea",), "Crude oil route through Gulf shipping lanes."),
    TradeFlow("Canada", "United States", "Petrol", ("Pipeline", "Rail", "Road"), "North American oil route."),
    TradeFlow("United States", "Mexico", "Petrol", ("Pipeline", "Road", "Sea"), "Regional refined-products route."),
    TradeFlow("Norway", "Germany", "Petrol", ("Pipeline", "Sea"), "European petroleum route."),
    TradeFlow("Kazakhstan", "China", "Petrol", ("Pipeline", "Rail"), "Central Asia-to-China energy route."),
    TradeFlow("Qatar", "Japan", "Petrol", ("Sea",), "Qatari oil to Japan."),
    TradeFlow("Qatar", "South Korea", "Petrol", ("Sea",), "Qatari oil to South Korea."),
    TradeFlow("United States", "Japan", "Petrol", ("Sea",), "US oil to Japan."),
    TradeFlow("Australia", "Japan", "Petrol", ("Sea",), "Australian oil to Japan."),
    TradeFlow("Australia", "South Korea", "Petrol", ("Sea",), "Australian oil to South Korea."),
    TradeFlow("United Arab Emirates", "India", "Petrol", ("Sea",), "UAE oil to India."),
    TradeFlow("Kuwait", "South Korea", "Petrol", ("Sea",), "Kuwaiti oil to South Korea."),
    TradeFlow("Iran", "China", "Petrol", ("Sea",), "Iranian oil to China."),
    TradeFlow("Nigeria", "United States", "Petrol", ("Sea",), "Nigerian oil to US."),
    TradeFlow("Nigeria", "Netherlands", "Petrol", ("Sea",), "Nigerian oil to Europe."),
    TradeFlow("Angola", "China", "Petrol", ("Sea",), "Angolan oil to China."),
    TradeFlow("Angola", "India", "Petrol", ("Sea",), "Angolan oil to India."),
    TradeFlow("Venezuela", "China", "Petrol", ("Sea",), "Venezuelan oil to China."),
    TradeFlow("Venezuela", "United States", "Petrol", ("Sea",), "Venezuelan oil to US."),
    TradeFlow("Algeria", "Italy", "Petrol", ("Sea",), "Algerian oil to Italy."),
    TradeFlow("Algeria", "Spain", "Petrol", ("Sea",), "Algerian oil to Spain."),
    TradeFlow("Libya", "Italy", "Petrol", ("Sea",), "Libyan oil to Italy."),
    TradeFlow("Egypt", "Germany", "Petrol", ("Sea",), "Egyptian oil to Germany."),
    TradeFlow("Oman", "India", "Petrol", ("Sea",), "Omani oil to India."),
    TradeFlow("Oman", "China", "Petrol", ("Sea",), "Omani oil to China."),
    TradeFlow("Azerbaijan", "Italy", "Petrol", ("Sea",), "Azerbaijani oil to Italy."),
    TradeFlow("Azerbaijan", "Turkey", "Petrol", ("Sea",), "Azerbaijani oil to Turkey."),
    TradeFlow("Turkmenistan", "China", "Petrol", ("Pipeline",), "Turkmen oil to China."),
    TradeFlow("Uzbekistan", "China", "Petrol", ("Pipeline",), "Uzbek oil to China."),
    TradeFlow("Mexico", "United States", "Petrol", ("Pipeline", "Sea"), "Mexican oil to US."),
    TradeFlow("Brazil", "United States", "Petrol", ("Sea",), "Brazilian oil to US."),
    TradeFlow("Colombia", "United States", "Petrol", ("Sea",), "Colombian oil to US."),
    TradeFlow("Ecuador", "United States", "Petrol", ("Sea",), "Ecuadorian oil to US."),
    TradeFlow("Peru", "China", "Petrol", ("Sea",), "Peruvian oil to China."),
    TradeFlow("Peru", "United States", "Petrol", ("Sea",), "Peruvian oil to US."),
    TradeFlow("United Kingdom", "Netherlands", "Petrol", ("Sea",), "UK oil to Netherlands."),
    TradeFlow("United Kingdom", "Germany", "Petrol", ("Sea",), "UK oil to Germany."),

    # Coal - 35 routes
    TradeFlow("Australia", "Japan", "Coal", ("Sea",), "Australian coal to Japan."),
    TradeFlow("Australia", "South Korea", "Coal", ("Sea",), "Australian coal to South Korea."),
    TradeFlow("Australia", "China", "Coal", ("Sea",), "Australian coal to China."),
    TradeFlow("Australia", "India", "Coal", ("Sea",), "Australian coal to India."),
    TradeFlow("Indonesia", "China", "Coal", ("Sea",), "Indonesian coal to China."),
    TradeFlow("Indonesia", "India", "Coal", ("Sea",), "Indonesian coal to India."),
    TradeFlow("Indonesia", "Japan", "Coal", ("Sea",), "Indonesian coal to Japan."),
    TradeFlow("Indonesia", "South Korea", "Coal", ("Sea",), "Indonesian coal to South Korea."),
    TradeFlow("Russia", "China", "Coal", ("Rail", "Sea"), "Russian coal to China."),
    TradeFlow("Russia", "Japan", "Coal", ("Sea",), "Russian coal to Japan."),
    TradeFlow("Russia", "South Korea", "Coal", ("Sea",), "Russian coal to South Korea."),
    TradeFlow("United States", "Japan", "Coal", ("Sea",), "US coal to Japan."),
    TradeFlow("United States", "South Korea", "Coal", ("Sea",), "US coal to South Korea."),
    TradeFlow("Colombia", "Europe", "Coal", ("Sea",), "Colombian coal to Europe."),
    TradeFlow("South Africa", "India", "Coal", ("Sea",), "South African coal to India."),
    TradeFlow("South Africa", "China", "Coal", ("Sea",), "South African coal to China."),
    TradeFlow("Canada", "Japan", "Coal", ("Sea",), "Canadian coal to Japan."),
    TradeFlow("Canada", "South Korea", "Coal", ("Sea",), "Canadian coal to South Korea."),
    TradeFlow("Poland", "Germany", "Coal", ("Rail", "Sea"), "Polish coal to Germany."),
    TradeFlow("Poland", "Ukraine", "Coal", ("Rail",), "Polish coal to Ukraine."),
    TradeFlow("Kazakhstan", "China", "Coal", ("Rail",), "Kazakh coal to China."),
    TradeFlow("Kazakhstan", "Russia", "Coal", ("Rail",), "Kazakh coal to Russia."),
    TradeFlow("Mongolia", "China", "Coal", ("Rail",), "Mongolian coal to China."),
    TradeFlow("Vietnam", "China", "Coal", ("Sea",), "Vietnamese coal to China."),
    TradeFlow("Vietnam", "Japan", "Coal", ("Sea",), "Vietnamese coal to Japan."),
    TradeFlow("Mozambique", "India", "Coal", ("Sea",), "Mozambican coal to India."),
    TradeFlow("Mozambique", "China", "Coal", ("Sea",), "Mozambican coal to China."),
    TradeFlow("Botswana", "India", "Coal", ("Sea",), "Botswana coal to India."),
    TradeFlow("Botswana", "China", "Coal", ("Sea",), "Botswana coal to China."),
    TradeFlow("Zimbabwe", "China", "Coal", ("Sea",), "Zimbabwe coal to China."),
    TradeFlow("Zimbabwe", "India", "Coal", ("Sea",), "Zimbabwe coal to India."),
    TradeFlow("Turkey", "Europe", "Coal", ("Sea",), "Turkish coal to Europe."),
    TradeFlow("Greece", "Italy", "Coal", ("Sea",), "Greek coal to Italy."),
    TradeFlow("Bulgaria", "Turkey", "Coal", ("Sea",), "Bulgarian coal to Turkey."),
    TradeFlow("Serbia", "Bosnia", "Coal", ("Rail",), "Serbian coal to Bosnia."),
    TradeFlow("Ukraine", "Poland", "Coal", ("Rail",), "Ukrainian coal to Poland."),
    TradeFlow("Ukraine", "Slovakia", "Coal", ("Rail",), "Ukrainian coal to Slovakia."),
    TradeFlow("Russia", "Japan", "Coal", ("Sea",), "Russian coal to Japan."),
    TradeFlow("Russia", "South Korea", "Coal", ("Sea",), "Russian coal to South Korea."),
    TradeFlow("Canada", "Japan", "Coal", ("Sea",), "Canadian coal to Japan."),
    TradeFlow("Canada", "South Korea", "Coal", ("Sea",), "Canadian coal to South Korea."),
    TradeFlow("Australia", "India", "Coal", ("Sea",), "Australian coal to India."),

    # Grains - 30 routes
    TradeFlow("Ukraine", "Egypt", "Grains", ("Sea",), "Black Sea grain route."),
    TradeFlow("Ukraine", "Turkey", "Grains", ("Sea", "Rail"), "Black Sea grain route."),
    TradeFlow("Russia", "Turkey", "Grains", ("Sea", "Rail"), "Black Sea grain route."),
    TradeFlow("United States", "Mexico", "Grains", ("Rail", "Road"), "North American grain route."),
    TradeFlow("United States", "Japan", "Grains", ("Sea",), "Pacific grain route."),
    TradeFlow("Brazil", "China", "Grains", ("Sea",), "Major soybean/corn route."),
    TradeFlow("Argentina", "China", "Grains", ("Sea",), "South America-to-China grain route."),
    TradeFlow("India", "Bangladesh", "Grains", ("Road", "Rail", "Sea"), "Regional grain route."),
    TradeFlow("Vietnam", "Philippines", "Grains", ("Sea",), "Regional rice/grain route."),
    TradeFlow("United States", "China", "Grains", ("Sea",), "US grain to China."),
    TradeFlow("United States", "South Korea", "Grains", ("Sea",), "US grain to South Korea."),
    TradeFlow("United States", "Egypt", "Grains", ("Sea",), "US grain to Egypt."),
    TradeFlow("United States", "Saudi Arabia", "Grains", ("Sea",), "US grain to Saudi Arabia."),
    TradeFlow("Canada", "China", "Grains", ("Sea",), "Canadian grain to China."),
    TradeFlow("Canada", "Japan", "Grains", ("Sea",), "Canadian grain to Japan."),
    TradeFlow("Australia", "China", "Grains", ("Sea",), "Australian grain to China."),
    TradeFlow("Australia", "Indonesia", "Grains", ("Sea",), "Australian grain to Indonesia."),
    TradeFlow("Ukraine", "China", "Grains", ("Sea",), "Ukrainian grain to China."),
    TradeFlow("Ukraine", "India", "Grains", ("Sea",), "Ukrainian grain to India."),
    TradeFlow("Russia", "China", "Grains", ("Rail", "Sea"), "Russian grain to China."),
    TradeFlow("Russia", "India", "Grains", ("Sea",), "Russian grain to India."),
    TradeFlow("Kazakhstan", "China", "Grains", ("Rail",), "Kazakh grain to China."),
    TradeFlow("Kazakhstan", "Turkey", "Grains", ("Rail",), "Kazakh grain to Turkey."),
    TradeFlow("France", "Algeria", "Grains", ("Sea",), "French grain to Algeria."),
    TradeFlow("France", "Morocco", "Grains", ("Sea",), "French grain to Morocco."),
    TradeFlow("Germany", "Netherlands", "Grains", ("Road", "Rail"), "German grain to Netherlands."),
    TradeFlow("Thailand", "Vietnam", "Grains", ("Sea",), "Thai rice to Vietnam."),
    TradeFlow("Thailand", "Philippines", "Grains", ("Sea",), "Thai rice to Philippines."),
    TradeFlow("Pakistan", "Bangladesh", "Grains", ("Sea",), "Pakistani grain to Bangladesh."),
    TradeFlow("Pakistan", "Sri Lanka", "Grains", ("Sea",), "Pakistani grain to Sri Lanka."),

    # Semiconductors - 30 routes (realistic Air/Sea mix based on value/urgency)
    TradeFlow("Taiwan", "United States", "Semiconductors", ("Air", "Sea"), "Time-sensitive and bulk routes for US demand."),
    TradeFlow("Taiwan", "China", "Semiconductors", ("Sea",), "Cost-optimized bulk commodity chip shipments."),
    TradeFlow("South Korea", "China", "Semiconductors", ("Sea",), "Standard component sea freight via Busan."),
    TradeFlow("South Korea", "United States", "Semiconductors", ("Air",), "Urgent memory chips and premium processors."),
    TradeFlow("Japan", "United States", "Semiconductors", ("Air",), "High-value logic chips and advanced components."),
    TradeFlow("Netherlands", "Taiwan", "Semiconductors", ("Air",), "Lithography equipment for TSMC - urgent."),
    TradeFlow("Germany", "China", "Semiconductors", ("Sea",), "Bulk semiconductor manufacturing equipment."),
    TradeFlow("Taiwan", "Japan", "Semiconductors", ("Air",), "Advanced chip orders require rapid delivery."),
    TradeFlow("Taiwan", "South Korea", "Semiconductors", ("Air",), "Inter-Asian urgent semiconductor trade."),
    TradeFlow("Taiwan", "Germany", "Semiconductors", ("Sea",), "European bulk orders via Suez Canal."),
    TradeFlow("Taiwan", "United Kingdom", "Semiconductors", ("Sea",), "UK market through Mediterranean/Atlantic route."),
    TradeFlow("South Korea", "Japan", "Semiconductors", ("Air",), "Regional rush orders and critical stock."),
    TradeFlow("South Korea", "Germany", "Semiconductors", ("Sea",), "Container ship through Suez to Europe."),
    TradeFlow("South Korea", "United Kingdom", "Semiconductors", ("Sea",), "Weekly container service to UK ports."),
    TradeFlow("Japan", "Germany", "Semiconductors", ("Sea",), "Slow steaming trans-Pacific via Suez route."),
    TradeFlow("Japan", "United Kingdom", "Semiconductors", ("Sea",), "Bulk container shipment to UK/Netherlands."),
    TradeFlow("Netherlands", "United States", "Semiconductors", ("Air",), "Critical fab equipment and precision components."),
    TradeFlow("Netherlands", "China", "Semiconductors", ("Sea",), "Large equipment shipments via Rotterdam port."),
    TradeFlow("Germany", "United States", "Semiconductors", ("Air",), "High-value precision semiconductor equipment."),
    TradeFlow("Germany", "Japan", "Semiconductors", ("Air",), "Equipment replacement and spare parts rush."),
    TradeFlow("Malaysia", "United States", "Semiconductors", ("Air",), "Assembly/test facility products - air priority."),
    TradeFlow("Malaysia", "China", "Semiconductors", ("Sea",), "Regional bulk shipments via South China Sea."),
    TradeFlow("Singapore", "United States", "Semiconductors", ("Air",), "Hub consolidation center - air-only export."),
    TradeFlow("Singapore", "China", "Semiconductors", ("Sea",), "Transhipment via Singapore port to China."),
    TradeFlow("Philippines", "United States", "Semiconductors", ("Air",), "Fab outputs direct to US customer centers."),
    TradeFlow("Philippines", "China", "Semiconductors", ("Sea",), "Container consolidation in South China Sea."),
    TradeFlow("China", "United States", "Semiconductors", ("Sea",), "Commodity chips via TransPac container lines."),
    TradeFlow("China", "Japan", "Semiconductors", ("Air",), "Premium automotive chip components urgent."),
    TradeFlow("Israel", "United States", "Semiconductors", ("Air",), "High-tech fabless chip design outputs."),
    TradeFlow("Israel", "Europe", "Semiconductors", ("Sea",), "Mediterranean route via Suez Canal to EU ports."),

    # Fertilizer - 30 routes
    TradeFlow("Russia", "Brazil", "Fertilizer", ("Sea",), "Fertilizer route exposed to war and sanctions."),
    TradeFlow("Russia", "India", "Fertilizer", ("Sea", "Rail"), "Fertilizer route exposed to war and sanctions."),
    TradeFlow("Belarus", "Brazil", "Fertilizer", ("Rail", "Sea"), "Potash route exposed to sanctions and regional war."),
    TradeFlow("Canada", "India", "Fertilizer", ("Sea",), "Potash route."),
    TradeFlow("Morocco", "India", "Fertilizer", ("Sea",), "Phosphate fertilizer route."),
    TradeFlow("Morocco", "Brazil", "Fertilizer", ("Sea",), "Phosphate fertilizer route."),
    TradeFlow("Saudi Arabia", "India", "Fertilizer", ("Sea",), "Ammonia/urea fertilizer route."),
    TradeFlow("Qatar", "India", "Fertilizer", ("Sea",), "Ammonia/urea fertilizer route."),
    TradeFlow("China", "Pakistan", "Fertilizer", ("Road", "Rail", "Sea"), "Regional fertilizer route."),
    TradeFlow("Russia", "China", "Fertilizer", ("Rail", "Sea"), "Russian fertilizer to China."),
    TradeFlow("Russia", "United States", "Fertilizer", ("Sea",), "Russian fertilizer to US."),
    TradeFlow("Belarus", "India", "Fertilizer", ("Sea",), "Belarusian fertilizer to India."),
    TradeFlow("Belarus", "China", "Fertilizer", ("Rail", "Sea"), "Belarusian fertilizer to China."),
    TradeFlow("Canada", "China", "Fertilizer", ("Sea",), "Canadian fertilizer to China."),
    TradeFlow("Canada", "Brazil", "Fertilizer", ("Sea",), "Canadian fertilizer to Brazil."),
    TradeFlow("Morocco", "China", "Fertilizer", ("Sea",), "Moroccan fertilizer to China."),
    TradeFlow("Morocco", "United States", "Fertilizer", ("Sea",), "Moroccan fertilizer to US."),
    TradeFlow("Saudi Arabia", "China", "Fertilizer", ("Sea",), "Saudi fertilizer to China."),
    TradeFlow("Saudi Arabia", "Brazil", "Fertilizer", ("Sea",), "Saudi fertilizer to Brazil."),
    TradeFlow("Qatar", "China", "Fertilizer", ("Sea",), "Qatari fertilizer to China."),
    TradeFlow("Qatar", "Brazil", "Fertilizer", ("Sea",), "Qatari fertilizer to Brazil."),
    TradeFlow("Egypt", "India", "Fertilizer", ("Sea",), "Egyptian fertilizer to India."),
    TradeFlow("Egypt", "China", "Fertilizer", ("Sea",), "Egyptian fertilizer to China."),
    TradeFlow("Tunisia", "Italy", "Fertilizer", ("Sea",), "Tunisian fertilizer to Italy."),
    TradeFlow("Tunisia", "Spain", "Fertilizer", ("Sea",), "Tunisian fertilizer to Spain."),
    TradeFlow("Jordan", "India", "Fertilizer", ("Sea",), "Jordanian fertilizer to India."),
    TradeFlow("Jordan", "Turkey", "Fertilizer", ("Sea",), "Jordanian fertilizer to Turkey."),
    TradeFlow("Syria", "Lebanon", "Fertilizer", ("Road", "Rail"), "Syrian fertilizer to Lebanon."),
    TradeFlow("Syria", "Jordan", "Fertilizer", ("Road", "Rail"), "Syrian fertilizer to Jordan."),
    TradeFlow("Israel", "Turkey", "Fertilizer", ("Sea",), "Israeli fertilizer to Turkey."),

    # More Petrol routes
    TradeFlow("Iraq", "Japan", "Petrol", ("Sea",), "Iraqi oil to Japan."),
    TradeFlow("Iran", "Japan", "Petrol", ("Sea",), "Iranian oil to Japan."),
    TradeFlow("Kuwait", "Japan", "Petrol", ("Sea",), "Kuwaiti oil to Japan."),
    TradeFlow("UAE", "Japan", "Petrol", ("Sea",), "UAE oil to Japan."),
    TradeFlow("Saudi Arabia", "South Korea", "Petrol", ("Sea",), "Saudi oil to South Korea."),

    # More Coal routes
    TradeFlow("Qatar", "United States", "Coal", ("Sea",), "Qatari coal to US."),
    TradeFlow("Australia", "United States", "Coal", ("Sea",), "Australian coal to US."),
    TradeFlow("Russia", "United States", "Coal", ("Sea",), "Russian coal to US."),
    TradeFlow("Canada", "United States", "Coal", ("Rail",), "Canadian coal to US."),
    TradeFlow("Norway", "United States", "Coal", ("Sea",), "Norwegian coal to US."),

    # More Grains routes
    TradeFlow("United States", "Indonesia", "Grains", ("Sea",), "US grain to Indonesia."),
    TradeFlow("Canada", "Indonesia", "Grains", ("Sea",), "Canadian grain to Indonesia."),
    TradeFlow("Australia", "Egypt", "Grains", ("Sea",), "Australian grain to Egypt."),
    TradeFlow("Ukraine", "Egypt", "Grains", ("Sea",), "Ukrainian grain to Egypt."),
    TradeFlow("Russia", "Indonesia", "Grains", ("Sea",), "Russian grain to Indonesia."),

    # More Semiconductors routes
    TradeFlow("Taiwan", "Canada", "Semiconductors", ("Air", "Sea"), "Taiwanese chips to Canada."),
    TradeFlow("South Korea", "Canada", "Semiconductors", ("Air", "Sea"), "Korean chips to Canada."),
    TradeFlow("Japan", "Canada", "Semiconductors", ("Air", "Sea"), "Japanese chips to Canada."),
    TradeFlow("Netherlands", "Canada", "Semiconductors", ("Air", "Sea"), "Dutch equipment to Canada."),
    TradeFlow("Germany", "Canada", "Semiconductors", ("Air", "Sea"), "German equipment to Canada."),

    # More Fertilizer routes
    TradeFlow("Qatar", "Brazil", "Fertilizer", ("Sea",), "Qatari fertilizer to Brazil."),
    TradeFlow("Saudi Arabia", "Brazil", "Fertilizer", ("Sea",), "Saudi fertilizer to Brazil."),
    TradeFlow("Egypt", "Brazil", "Fertilizer", ("Sea",), "Egyptian fertilizer to Brazil."),
    TradeFlow("Tunisia", "Brazil", "Fertilizer", ("Sea",), "Tunisian fertilizer to Brazil."),
    TradeFlow("Jordan", "Brazil", "Fertilizer", ("Sea",), "Jordanian fertilizer to Brazil."),
]

MANUAL_COORDS = {
    "Cabo Verde": (16.5388, -23.0418),
    "Cote d'Ivoire": (7.5400, -5.5471),
    "Czechia": (49.8175, 15.4730),
    "Democratic Republic of the Congo": (-4.0383, 21.7587),
    "Eswatini": (-26.5225, 31.4659),
    "Hong Kong": (22.3193, 114.1694),
    "Kosovo": (42.6026, 20.9030),
    "Macau": (22.1987, 113.5439),
    "Micronesia": (7.4256, 150.5508),
    "North Korea": (40.3399, 127.5101),
    "Palestine": (31.9522, 35.2332),
    "Puerto Rico": (18.2208, -66.5901),
    "Saint Kitts and Nevis": (17.3578, -62.7830),
    "Saint Lucia": (13.9094, -60.9789),
    "Saint Vincent and the Grenadines": (12.9843, -61.2872),
    "Sao Tome and Principe": (0.1864, 6.6131),
    "South Korea": (35.9078, 127.7669),
    "Taiwan": (23.6978, 120.9605),
    "Timor-Leste": (-8.8742, 125.7275),
    "United Kingdom": (55.3781, -3.4360),
    "United States": (37.0902, -95.7129),
    "Vatican City": (41.9029, 12.4534),
    "Western Sahara": (24.2155, -12.8858),
}

API_NAME_ALIASES = {
    "Bahamas": "The Bahamas",
    "Bolivia": "Bolivia (Plurinational State of)",
    "Brunei": "Brunei Darussalam",
    "Iran": "Iran (Islamic Republic of)",
    "Laos": "Lao People's Democratic Republic",
    "Moldova": "Moldova, Republic of",
    "Russia": "Russian Federation",
    "Syria": "Syrian Arab Republic",
    "Tanzania": "Tanzania, United Republic of",
    "Turkey": "Turkiye",
    "Venezuela": "Venezuela (Bolivarian Republic of)",
    "Vietnam": "Viet Nam",
}


def country_index() -> dict[str, int]:
    return {country: index for index, country in enumerate(COUNTRIES)}


def empty_matrix() -> np.ndarray:
    return np.zeros((len(COUNTRIES), len(COUNTRIES)), dtype=np.uint8)


def build_war_matrix() -> np.ndarray:
    matrix = empty_matrix()
    lookup = country_index()
    for edge in SEED_TENSIONS:
        i = lookup[edge.source]
        j = lookup[edge.target]
        matrix[i, j] = 1
        matrix[j, i] = 1
    return matrix


def build_seed_trade_catalog() -> pd.DataFrame:
    rows = []
    for flow in SEED_TRADE_FLOWS:
        for mode in flow.modes:
            rows.append(
                {
                    "exporter": flow.exporter,
                    "importer": flow.importer,
                    "commodity": flow.commodity,
                    "mode": mode,
                    "source": "Illustrative fallback",
                    "note": flow.note,
                }
            )
    return pd.DataFrame(rows)


@st.cache_data(ttl=60 * 60 * 24)
def load_trade_catalog() -> pd.DataFrame:
    return build_seed_trade_catalog()


def build_trade_tensors(trade_catalog: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    n = len(COUNTRIES)
    commodity_tensor = np.zeros((n, n, len(COMMODITIES)), dtype=np.uint8)
    transport_tensor = np.zeros((n, n, len(TRANSPORT_MODES)), dtype=np.uint8)
    lookup = country_index()
    commodity_lookup = {commodity: index for index, commodity in enumerate(COMMODITIES)}
    mode_lookup = {mode: index for index, mode in enumerate(TRANSPORT_MODES)}

    for row in trade_catalog.itertuples(index=False):
        if row.exporter not in lookup or row.importer not in lookup:
            continue
        if row.commodity not in commodity_lookup or row.mode not in mode_lookup:
            continue
        i = lookup[row.exporter]
        j = lookup[row.importer]
        commodity_tensor[i, j, commodity_lookup[row.commodity]] = 1
        transport_tensor[i, j, mode_lookup[row.mode]] = 1

    return commodity_tensor, transport_tensor


def trade_edges_base_frame(trade_catalog: pd.DataFrame, war_matrix: np.ndarray) -> pd.DataFrame:
    war_degree = war_matrix.sum(axis=1)
    lookup = country_index()
    frame = trade_catalog.copy()
    frame["war_exposed"] = frame.apply(
        lambda row: bool(
            war_degree[lookup.get(row["exporter"], 0)] > 0
            or war_degree[lookup.get(row["importer"], 0)] > 0
            or war_matrix[lookup.get(row["exporter"], 0), lookup.get(row["importer"], 0)] == 1
        ),
        axis=1,
    )
    frame["direct_conflict"] = frame.apply(
        lambda row: bool(war_matrix[lookup.get(row["exporter"], 0), lookup.get(row["importer"], 0)] == 1),
        axis=1,
    )
    frame["impact_score"] = frame["war_exposed"].astype(int) + frame["direct_conflict"].astype(int)
    return frame


@st.cache_data(ttl=60 * 60 * 24)
def load_country_coords() -> dict[str, tuple[float, float]]:
    coords = dict(MANUAL_COORDS)
    try:
        response = requests.get(
            "https://restcountries.com/v3.1/all?fields=name,latlng",
            timeout=8,
        )
        response.raise_for_status()
        for item in response.json():
            latlng = item.get("latlng") or []
            names = item.get("name") or {}
            if len(latlng) < 2:
                continue
            for name in (names.get("official"), names.get("common")):
                if name:
                    coords[name] = (float(latlng[0]), float(latlng[1]))
        for local_name, api_name in API_NAME_ALIASES.items():
            if api_name in coords:
                coords[local_name] = coords[api_name]
    except requests.RequestException:
        pass
    return coords


def war_edges_frame(war_matrix: np.ndarray) -> pd.DataFrame:
    seeded_notes = {tuple(sorted((edge.source, edge.target))): edge.note for edge in SEED_TENSIONS}
    seeded_intensity = {tuple(sorted((edge.source, edge.target))): edge.intensity for edge in SEED_TENSIONS}
    rows = []
    for i in range(len(COUNTRIES)):
        for j in range(i + 1, len(COUNTRIES)):
            if war_matrix[i, j] == 1:
                source = COUNTRIES[i]
                target = COUNTRIES[j]
                key = tuple(sorted((source, target)))
                rows.append(
                    {
                        "source": source,
                        "target": target,
                        "intensity": seeded_intensity.get(key, 1),
                        "note": seeded_notes.get(key, "Seeded tension link."),
                    }
                )
    return pd.DataFrame(rows, columns=["source", "target", "intensity", "note"])


def trade_edges_frame(
    trade_catalog: pd.DataFrame,
    war_matrix: np.ndarray,
    selected_commodity: str,
    selected_mode: str,
) -> pd.DataFrame:
    frame = trade_edges_base_frame(trade_catalog, war_matrix)
    frame = frame[frame["commodity"] == selected_commodity].copy()
    if selected_mode != "All modes":
        frame = frame[frame["mode"] == selected_mode].copy()
        return frame.sort_values(["exporter"], ascending=True).reset_index(drop=True)

    grouped = (
        frame.groupby(["exporter", "importer", "commodity"], as_index=False)
        .agg(
            mode=("mode", lambda values: ", ".join(sorted(set(values)))),
            war_exposed=("war_exposed", "max"),
            direct_conflict=("direct_conflict", "max"),
            impact_score=("impact_score", "max"),
            source=("source", lambda values: " + ".join(sorted(set(values)))),
            note=("note", lambda values: next((value for value in values if pd.notna(value) and value), "")),
        )
    )
    return grouped.sort_values(["exporter"], ascending=True).reset_index(drop=True)


def all_trade_edges_frame(
    trade_catalog: pd.DataFrame,
    war_matrix: np.ndarray,
) -> pd.DataFrame:
    frame = trade_edges_base_frame(trade_catalog, war_matrix)
    return frame.sort_values(["commodity", "exporter"], ascending=[True, True]).reset_index(drop=True)


def countries_for_edges(edges: pd.DataFrame, source_col: str, target_col: str) -> set[str]:
    if edges.empty:
        return set()
    return set(edges[source_col]).union(set(edges[target_col]))


def add_route_trace(
    fig: go.Figure,
    coords: dict[str, tuple[float, float]],
    source: str,
    target: str,
    color: str,
    width: float,
    text: str,
) -> None:
    if source not in coords or target not in coords:
        return
    src_lat, src_lon = coords[source]
    dst_lat, dst_lon = coords[target]
    fig.add_trace(
        go.Scattergeo(
            lon=[src_lon, dst_lon],
            lat=[src_lat, dst_lat],
            mode="lines",
            line=dict(width=width, color=color),
            hoverinfo="text",
            text=text,
            showlegend=False,
        )
    )


def add_node_trace(
    fig: go.Figure,
    coords: dict[str, tuple[float, float]],
    countries: set[str],
    label: str,
    color: str,
    symbol: str,
) -> None:
    lats = []
    lons = []
    names = []
    for country in sorted(countries):
        if country in coords:
            lat, lon = coords[country]
            lats.append(lat)
            lons.append(lon)
            names.append(country)
    fig.add_trace(
        go.Scattergeo(
            lon=lons,
            lat=lats,
            mode="markers",
            marker=dict(size=9, color=color, symbol=symbol, line=dict(width=1.5, color="white")),
            text=[f"{label}: {country}" for country in names],
            hoverinfo="text",
            name=label,
            showlegend=False,
        )
    )


def add_line_legend(fig: go.Figure, name: str, color: str, width: float) -> None:
    fig.add_trace(
        go.Scattergeo(
            lon=[None],
            lat=[None],
            mode="lines",
            line=dict(width=width, color=color),
            name=name,
            hoverinfo="skip",
            showlegend=True,
        )
    )


def add_marker_legend(fig: go.Figure, name: str, color: str, symbol: str) -> None:
    fig.add_trace(
        go.Scattergeo(
            lon=[None],
            lat=[None],
            mode="markers",
            marker=dict(size=9, color=color, symbol=symbol, line=dict(width=1.5, color="white")),
            name=name,
            hoverinfo="skip",
            showlegend=True,
        )
    )


def route_line_width(value: float | int | None, default_width: float) -> float:
    return default_width


def map_figure(
    view: str,
    war_edges: pd.DataFrame,
    trade_edges: pd.DataFrame,
    coords: dict[str, tuple[float, float]],
) -> go.Figure:
    fig = go.Figure()

    if view == "War network":
        add_line_legend(fig, "War/tension link", "rgba(255, 92, 108, 0.88)", 3.2)
        add_marker_legend(fig, "War/tension country", "#ff5c6c", "circle")
        for row in war_edges.itertuples(index=False):
            add_route_trace(
                fig,
                coords,
                row.source,
                row.target,
                "rgba(255, 92, 108, 0.68)",
                1.8 + row.intensity * 0.45,
                f"War/tension<br>{row.source} - {row.target}<br>Intensity: {row.intensity}<br>{row.note}",
            )
        countries = countries_for_edges(war_edges, "source", "target")
        add_node_trace(fig, coords, countries, "War/tension country", "#ff5c6c", "circle")
    elif view == "Trade routes":
        add_line_legend(fig, "Selected trade route", "rgba(32, 215, 210, 0.80)", 3.0)
        add_marker_legend(fig, "Exporter", "#20d7d2", "diamond")
        add_marker_legend(fig, "Importer", "#45d483", "circle")
        for row in trade_edges.itertuples(index=False):
            add_route_trace(
                fig,
                coords,
                row.exporter,
                row.importer,
                "rgba(32, 215, 210, 0.58)",
                route_line_width(getattr(row, "display_value_usd", np.nan), 1.8),
                f"{row.commodity} by {row.mode}<br>{row.exporter} -> {row.importer}<br>{row.note}",
            )
        add_node_trace(fig, coords, set(trade_edges["exporter"]) if not trade_edges.empty else set(), "Exporter", "#20d7d2", "diamond")
        add_node_trace(fig, coords, set(trade_edges["importer"]) if not trade_edges.empty else set(), "Importer", "#45d483", "circle")
    else:
        add_line_legend(fig, "Direct conflict route", "rgba(255, 92, 108, 0.90)", 3.4)
        add_line_legend(fig, "Endpoint-exposed route", "rgba(245, 163, 64, 0.88)", 3.0)
        add_marker_legend(fig, "Exposed exporter", "#ff5c6c", "diamond")
        add_marker_legend(fig, "Exposed importer", "#f5a340", "circle")
        disrupted = trade_edges[trade_edges["war_exposed"]]
        for row in disrupted.itertuples(index=False):
            color = "rgba(255, 92, 108, 0.78)" if row.direct_conflict else "rgba(245, 163, 64, 0.76)"
            add_route_trace(
                fig,
                coords,
                row.exporter,
                row.importer,
                color,
                route_line_width(getattr(row, "display_value_usd", np.nan), 2.2 if row.direct_conflict else 1.8),
                (
                    f"Disrupted {row.commodity} route by {row.mode}"
                    f"<br>{row.exporter} -> {row.importer}"
                    f"<br>Direct conflict: {'yes' if row.direct_conflict else 'no'}"
                    f"<br>{row.note}"
                ),
            )
        add_node_trace(fig, coords, set(disrupted["exporter"]) if not disrupted.empty else set(), "Exposed exporter", "#ff5c6c", "diamond")
        add_node_trace(fig, coords, set(disrupted["importer"]) if not disrupted.empty else set(), "Exposed importer", "#f5a340", "circle")

    fig.update_geos(
        projection_type="natural earth",
        showland=True,
        landcolor="rgb(29, 35, 46)",
        showcountries=True,
        countrycolor="rgb(64, 74, 91)",
        showocean=True,
        oceancolor="rgb(13, 17, 24)",
        showlakes=True,
        lakecolor="rgb(13, 17, 24)",
        coastlinecolor="rgb(78, 88, 105)",
        bgcolor="#151922",
    )
    fig.update_layout(
        height=680,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="#151922",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.02,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(17,21,29,0.94)",
            bordercolor="rgba(47,58,74,0.95)",
            borderwidth=1,
            font=dict(size=12, color="#e8edf5"),
        ),
        font=dict(family="Inter, Arial, sans-serif", size=13, color="#e8edf5"),
    )
    return fig


def matrix_slice_frame(tensor: np.ndarray, slice_name: str, labels: list[str]) -> pd.DataFrame:
    if slice_name == "All modes" and labels == TRANSPORT_MODES:
        matrix = np.any(tensor == 1, axis=2).astype(np.uint8)
    else:
        idx = labels.index(slice_name)
        matrix = tensor[:, :, idx]
    active_rows = np.where(matrix.sum(axis=1) + matrix.sum(axis=0) > 0)[0]
    active_countries = [COUNTRIES[i] for i in active_rows]
    if not active_countries:
        return pd.DataFrame()
    active_idx = [COUNTRIES.index(country) for country in active_countries]
    return pd.DataFrame(matrix[np.ix_(active_idx, active_idx)].astype(int), index=active_countries, columns=active_countries)


def build_war_graph(war_matrix: np.ndarray) -> nx.Graph:
    graph = nx.Graph()
    active_nodes = set()
    for i in range(len(COUNTRIES)):
        for j in range(i + 1, len(COUNTRIES)):
            if war_matrix[i, j] > 0:
                graph.add_edge(COUNTRIES[i], COUNTRIES[j], weight=float(war_matrix[i, j]))
                active_nodes.add(COUNTRIES[i])
                active_nodes.add(COUNTRIES[j])
    graph.add_nodes_from(active_nodes)
    return graph


def build_trade_graph(
    commodity_tensor: np.ndarray,
    transport_tensor: np.ndarray,
    commodity: str = "All commodities",
    mode: str = "All modes",
) -> nx.DiGraph:
    graph = nx.DiGraph()
    commodity_indices = range(len(COMMODITIES)) if commodity == "All commodities" else [COMMODITIES.index(commodity)]
    mode_indices = range(len(TRANSPORT_MODES)) if mode == "All modes" else [TRANSPORT_MODES.index(mode)]

    for i in range(len(COUNTRIES)):
        for j in range(len(COUNTRIES)):
            if i == j:
                continue
            commodity_active = any(commodity_tensor[i, j, idx] > 0 for idx in commodity_indices)
            mode_active = any(transport_tensor[i, j, idx] > 0 for idx in mode_indices)
            if commodity_active and mode_active:
                graph.add_edge(COUNTRIES[i], COUNTRIES[j], weight=1.0)
    return graph


def build_route_graph(transport_tensor: np.ndarray, mode: str = "All modes") -> nx.DiGraph:
    graph = nx.DiGraph()
    mode_indices = range(len(TRANSPORT_MODES)) if mode == "All modes" else [TRANSPORT_MODES.index(mode)]
    for i in range(len(COUNTRIES)):
        for j in range(len(COUNTRIES)):
            if i == j:
                continue
            if any(transport_tensor[i, j, idx] > 0 for idx in mode_indices):
                graph.add_edge(COUNTRIES[i], COUNTRIES[j], weight=1.0)
    return graph



def graph_metric_summary(graph: nx.Graph | nx.DiGraph, directed: bool) -> dict[str, float | int | None]:
    node_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()
    if node_count == 0:
        return {
            "nodes": 0,
            "edges": 0,
            "density": 0.0,
            "avg_degree": 0.0,
            "components": 0,
            "gcc_nodes": 0,
            "gcc_ratio": 0.0,
            "clustering": 0.0,
            "avg_path_length": None,
            "diameter": None,
        }

    if directed:
        degree_values = [value for _, value in graph.degree()]
        components = list(nx.weakly_connected_components(graph))
        undirected = graph.to_undirected()
    else:
        degree_values = [value for _, value in graph.degree()]
        components = list(nx.connected_components(graph))
        undirected = graph

    gcc_size = max((len(component) for component in components), default=0)
    gcc_ratio = gcc_size / node_count if node_count else 0.0
    clustering = nx.average_clustering(undirected) if undirected.number_of_nodes() > 1 else 0.0

    avg_path_length = None
    diameter = None
    if components:
        gcc_nodes = max(components, key=len)
        gcc_graph = undirected.subgraph(gcc_nodes).copy()
        if gcc_graph.number_of_nodes() > 1 and gcc_graph.number_of_edges() > 0:
            try:
                avg_path_length = float(nx.average_shortest_path_length(gcc_graph))
                diameter = int(nx.diameter(gcc_graph))
            except Exception:
                avg_path_length = None
                diameter = None

    return {
        "nodes": node_count,
        "edges": edge_count,
        "density": float(nx.density(graph)),
        "avg_degree": float(np.mean(degree_values)) if degree_values else 0.0,
        "components": len(components),
        "gcc_nodes": gcc_size,
        "gcc_ratio": gcc_ratio,
        "clustering": float(clustering),
        "avg_path_length": avg_path_length,
        "diameter": diameter,
    }


def centrality_frame(graph: nx.Graph | nx.DiGraph, directed: bool) -> pd.DataFrame:
    if graph.number_of_nodes() == 0:
        return pd.DataFrame(columns=["country", "degree", "betweenness", "closeness", "eigenvector"])

    degree = dict(graph.degree())
    betweenness = nx.betweenness_centrality(graph) if graph.number_of_edges() > 0 else {node: 0.0 for node in graph.nodes()}
    closeness = nx.closeness_centrality(graph) if graph.number_of_edges() > 0 else {node: 0.0 for node in graph.nodes()}
    eigenvector_source = graph.to_undirected() if directed else graph
    try:
        eigenvector = nx.eigenvector_centrality_numpy(eigenvector_source) if eigenvector_source.number_of_edges() > 0 else {node: 0.0 for node in graph.nodes()}
    except Exception:
        eigenvector = {node: 0.0 for node in graph.nodes()}

    rows = []
    for node in graph.nodes():
        rows.append(
            {
                "country": node,
                "degree": degree.get(node, 0),
                "betweenness": betweenness.get(node, 0.0),
                "closeness": closeness.get(node, 0.0),
                "eigenvector": eigenvector.get(node, 0.0),
            }
        )
    return pd.DataFrame(rows).sort_values(["betweenness", "degree"], ascending=[False, False])


def degree_distribution_figure(graph: nx.Graph | nx.DiGraph, title: str) -> go.Figure:
    degrees = [degree for _, degree in graph.degree()]
    values, counts = np.unique(degrees, return_counts=True) if degrees else ([], [])
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=list(values),
            y=list(counts),
            marker=dict(color="#45a3ff"),
            hovertemplate="Degree %{x}<br>Nodes %{y}<extra></extra>",
        )
    )
    fig.update_layout(
        title=title,
        height=280,
        margin=dict(l=20, r=20, t=45, b=20),
        paper_bgcolor="#11141b",
        plot_bgcolor="#11141b",
        font=dict(color="#f3f5f8"),
        xaxis=dict(title="Degree", gridcolor="#262c38", zeroline=False),
        yaxis=dict(title="Frequency", gridcolor="#262c38", zeroline=False),
    )
    return fig


war_matrix = build_war_matrix()
trade_catalog = load_trade_catalog()
commodity_tensor, transport_tensor = build_trade_tensors(trade_catalog)
coords = load_country_coords()

with st.sidebar:
    st.markdown('<div class="sidebar-section-label">Pages</div>', unsafe_allow_html=True)
    page = st.radio(
        "Select page",
        ["Commodity Analysis", "Design Rationale", "Network Metrics"],
        label_visibility="collapsed",
        key="page_nav",
    )
    st.divider()

    if page == "Commodity Analysis":
        st.markdown('<div class="sidebar-section-label">Layers</div>', unsafe_allow_html=True)
        view = st.radio(
            "Map view",
            ["War network", "Trade routes", "Disrupted trade routes"],
            key="map_view_nav",
        )
        commodity = st.selectbox(
            "Commodity",
            COMMODITIES,
            index=COMMODITIES.index("Petrol"),
            key="commodity_select",
        )
        transport_mode = st.selectbox(
            "Transport mode",
            ["All modes", *TRANSPORT_MODES],
            key="transport_select",
        )
        st.divider()
        st.markdown('<div class="sidebar-section-label">Assets</div>', unsafe_allow_html=True)
        st.write(f"War: `{war_matrix.shape}`")
        st.write(f"Commodity: `{commodity_tensor.shape}`")
        st.write(f"Transport: `{transport_tensor.shape}`")
        official_rows = int((trade_catalog["source"] != "Illustrative fallback").sum())
        st.write(f"Official trade rows: `{official_rows}`")

if page == "Commodity Analysis":
    st.markdown(
        """
        <div class="hero">
            <p class="eyebrow">Trade Risk Network</p>
            <h1>War Impact On Global Trade Routes</h1>
            <p>
                Track how conflict exposure affects commodity flows across sea, rail, road, pipeline, and air corridors.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

if page == "Commodity Analysis":
    war_edges = war_edges_frame(war_matrix)
    selected_trade_edges = trade_edges_frame(trade_catalog, war_matrix, commodity, transport_mode)
    all_trade_edges = all_trade_edges_frame(trade_catalog, war_matrix)
    
    impacted = selected_trade_edges[selected_trade_edges["war_exposed"]]
    direct = selected_trade_edges[selected_trade_edges["direct_conflict"]]
    
    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("War/tension links", len(war_edges))
    metric_b.metric("Selected routes", len(selected_trade_edges))
    metric_c.metric("Exposed routes", len(impacted))
    
    st.markdown('<div class="map-frame">', unsafe_allow_html=True)
    st.plotly_chart(map_figure(view, war_edges, selected_trade_edges, coords), width="stretch")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.info(
        "The conflict layer is based on conflict/tension matrix, and trade routes are based on major global flows."
    )
    
    tab_routes, tab_risk, tab_tensors, tab_impact = st.tabs(["Route Observations", "Exposure Summary", "Tensor Matrices", "Single Node Analysis"])
    
    with tab_routes:
        st.subheader(f"{commodity} routes by {transport_mode}")
        if selected_trade_edges.empty:
            st.write("No routes match this commodity and transport mode in the current dataset.")
        else:
            st.dataframe(
                selected_trade_edges.drop(columns=["impact_score", "source"]).sort_values(["war_exposed", "exporter"], ascending=[False, True]),
                width="stretch",
                hide_index=True,
            )
    
    with tab_risk:
        if all_trade_edges.empty:
            st.write("No trade routes are available.")
        else:
            commodity_summary = (
                all_trade_edges.groupby("commodity")
                .agg(routes=("commodity", "size"), exposed=("war_exposed", "sum"), direct=("direct_conflict", "sum"))
                .reset_index()
            )
            commodity_summary["exposure_rate"] = (commodity_summary["exposed"] / commodity_summary["routes"]).round(3)
            mode_summary = (
                all_trade_edges.groupby("mode")
                .agg(routes=("mode", "size"), exposed=("war_exposed", "sum"), direct=("direct_conflict", "sum"))
                .reset_index()
            )
            mode_summary["exposure_rate"] = (mode_summary["exposed"] / mode_summary["routes"]).round(3)
            
            left, right = st.columns(2)
            with left:
                st.subheader("By commodity")
                st.dataframe(commodity_summary.drop(columns=["exposure_rate"]).sort_values("exposed", ascending=False), width="stretch", hide_index=True)
            with right:
                st.subheader("By transport mode")
                st.dataframe(mode_summary.drop(columns=["exposure_rate"]).sort_values("exposed", ascending=False), width="stretch", hide_index=True)
            
            country_summary = (
                pd.concat(
                    [
                        all_trade_edges[["exporter", "war_exposed"]].rename(columns={"exporter": "country"}),
                        all_trade_edges[["importer", "war_exposed"]].rename(columns={"importer": "country"}),
                    ],
                    ignore_index=True,
                )
                .groupby("country")
                .agg(route_touchpoints=("country", "size"), exposed_touchpoints=("war_exposed", "sum"))
                .reset_index()
            )
            st.subheader("Countries most present in exposed routes")
            st.dataframe(
                country_summary[["country", "exposed_touchpoints"]].sort_values("exposed_touchpoints", ascending=False).head(20),
                width="stretch",
                hide_index=True,
            )
    
    with tab_tensors:
        st.subheader("Commodity tensor slice")
        st.write(f"`A[i, j, k] = 1` means country `i` exports `{commodity}` to country `j`.")
        st.dataframe(matrix_slice_frame(commodity_tensor, commodity, COMMODITIES), width="stretch")
        
        st.subheader("Transport tensor slice")
        if transport_mode == "All modes":
            st.write("This preview marks `1` when at least one transport mode is available between the country pair.")
        else:
            st.write(f"`T[i, j, m] = 1` means trade from country `i` to country `j` can use `{transport_mode}`.")
        st.dataframe(matrix_slice_frame(transport_tensor, transport_mode, TRANSPORT_MODES), width="stretch")
    
    with tab_impact:
        st.markdown("<h2>Single Node Analysis</h2>", unsafe_allow_html=True)
        your_country = st.selectbox("Select country to analyze", COUNTRIES, key="impact_country")
        your_idx = COUNTRIES.index(your_country)
        
        st.markdown("<h3>Active Conflicts</h3>", unsafe_allow_html=True)
        affecting_wars = []
        for i, country in enumerate(COUNTRIES):
            if war_matrix[your_idx, i] == 1 and i != your_idx:
                affecting_wars.append({"Country": country, "Type": "Direct Conflict"})
        
        for edge in SEED_TENSIONS:
            if edge.source == your_country or edge.target == your_country:
                other = edge.target if edge.source == your_country else edge.source
                affecting_wars.append({"Country": other, "Type": edge.note})
        
        if affecting_wars:
            wars_df = pd.DataFrame(affecting_wars).drop_duplicates(subset=["Country"])
            st.dataframe(wars_df, hide_index=True, width="stretch")
        else:
            st.write(f"No active conflicts involving {your_country}")
        
        st.markdown("<h3>Exposed Trade Routes</h3>", unsafe_allow_html=True)
        your_routes = all_trade_edges[
            ((all_trade_edges["exporter"] == your_country) | (all_trade_edges["importer"] == your_country)) &
            (all_trade_edges["war_exposed"] == True)
        ].copy()
        
        if not your_routes.empty:
            # Add conflict information to each route
            def find_affecting_conflict(row):
                exporter_idx = COUNTRIES.index(row["exporter"])
                importer_idx = COUNTRIES.index(row["importer"])
                
                # Check for direct conflict between exporter and importer
                if war_matrix[exporter_idx, importer_idx] == 1:
                    return f"{row['exporter']}-{row['importer']}: Direct conflict"
                
                # Check if exporter is in any conflict
                for i, country in enumerate(COUNTRIES):
                    if war_matrix[exporter_idx, i] == 1 and country != row["exporter"]:
                        for edge in SEED_TENSIONS:
                            if (edge.source == row["exporter"] and edge.target == country) or (edge.target == row["exporter"] and edge.source == country):
                                return f"{edge.source}-{edge.target}: {edge.note}"
                        return f"{row['exporter']}-{country}: Conflict"
                
                # Check if importer is in any conflict
                for i, country in enumerate(COUNTRIES):
                    if war_matrix[importer_idx, i] == 1 and country != row["importer"]:
                        for edge in SEED_TENSIONS:
                            if (edge.source == row["importer"] and edge.target == country) or (edge.target == row["importer"] and edge.source == country):
                                return f"{edge.source}-{edge.target}: {edge.note}"
                        return f"{row['importer']}-{country}: Conflict"
                
                # Check any SEED_TENSIONS involving either country
                for edge in SEED_TENSIONS:
                    if edge.source == row["exporter"] or edge.target == row["exporter"] or edge.source == row["importer"] or edge.target == row["importer"]:
                        return f"{edge.source}-{edge.target}: {edge.note}"
                
                return "Related to active conflict zone"
            
            your_routes["affecting_conflict"] = your_routes.apply(find_affecting_conflict, axis=1)
            your_routes["direction"] = your_routes.apply(
                lambda x: f"Export to {x['importer']}" if x["exporter"] == your_country else f"Import from {x['exporter']}",
                axis=1
            )
            
            st.markdown("<h4>By Commodity</h4>", unsafe_allow_html=True)
            commodity_risk = your_routes.groupby("commodity").agg(
                routes=("commodity", "size"),
                transport_modes=("mode", lambda x: ", ".join(set([m for modes in x for m in modes.split(", ")]))),
            ).reset_index()
            st.dataframe(commodity_risk.rename(columns={"commodity": "Commodity", "routes": "Exposed Routes", "transport_modes": "Transport Modes"}), hide_index=True, width="stretch")
            
            st.markdown("<h4>Detailed Routes</h4>", unsafe_allow_html=True)
            display_routes = your_routes[["direction", "commodity", "mode", "affecting_conflict"]].rename(
                columns={"direction": "Route", "commodity": "Commodity", "mode": "Transport", "affecting_conflict": "Risk Due To"}
            )
            st.dataframe(display_routes.sort_values("Route"), hide_index=True, width="stretch")
        else:
            st.write(f"No exposed trade routes for {your_country}. All trade appears secure.")
        
        st.markdown("<h3>Summary</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            direct_conflicts = len([w for w in affecting_wars if "Direct" in w.get("Type", "")])
            st.metric("Direct Conflicts", direct_conflicts)
        with col2:
            st.metric("Exposed Trade Routes", len(your_routes) if not your_routes.empty else 0)
        with col3:
            if not your_routes.empty:
                high_risk = len(your_routes[your_routes["impact_score"] > 1])
            else:
                high_risk = 0
            st.metric("High Risk Routes", high_risk)

elif page == "Design Rationale":
    st.markdown(
        """
        <div class="hero">
            <p class="eyebrow">Design Rationale</p>
            <h1>Thought Process Behind the Network</h1>
            <p>Kshitij Srivastava & Kushal Kumar</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="paper-card">
            <h2>1 Introduction</h2>
            <p>For the purposes of network science, we can imagine global trade to be a large, complex network where countries are interconnected through import and export of goods and services. In this system, each country is dependent on others for commodities, services, and transport, and those countries are also dependent on others, forming a highly interconnected network.</p>
            <p>However, political conflicts and war can disrupt these connections and thereby affect the trade of goods and services between countries. As studied in network science class, disrupting a bottleneck node in a network can have effects that propagate throughout the system. We are interested in the inferences we can make on world trade through different routes of different commodities purely by using a network model and no external data. By this we aim to show the true power of network science and hopefully giving us the insight needed to predict future outcomes and preparing for them in advance.</p>
            <p>This system can be represented as a network or graph:</p>
            <ul>
                <li>Countries are represented as nodes</li>
                <li>Trade relationships are represented as edges</li>
            </ul>
            <p>In many cases, these edges are directed since trade between two countries is not always balanced. Also, the weights of these edges can change over time depending on policies, demand and economic conditions.</p>
            <h3>Data Availability</h3>
            <p>Data for such a network is available from international organizations such as:</p>
            <ul>
                <li>World Trade Organization</li>
                <li>International Maritime Organisation</li>
                <li>International Air Transport Association</li>
            </ul>
            <p>These datasets provide trade routes and commodity specific trade flows.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="paper-card">
            <h2>2 Network Representation</h2>
            <h3>2.1 War Interaction Matrix (W)</h3>
            <p>This matrix represents the conflict layer of the network. A value of 1 indicates the existence of active conflict or full-fledged war, which can disrupt trade connections. This can also be a fractional value if necessary, such as in the case of tensions between countries which are not formally at war, for example India and China. This gives us a more detailed picture of the conflict network.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.latex(r"W_{ij}=\begin{cases}1, & \text{if countries } i \text{ and } j \text{ are in a state of conflict}\\0, & \text{otherwise}\end{cases}")
    st.markdown(
        """
        <div class="paper-card">
            <ul>
                <li>Dimensions: (countries x countries)</li>
                <li>Type: Binary, symmetric matrix</li>
                <li>Purpose: Encodes political conflicts between countries</li>
            </ul>
            <h3>2.2 Trade Tensor (T)</h3>
            <p>Each slice represents a trade network for a specific commodity such as oil or grains. This allows us to distinguish between different types of goods instead of aggregating all trade into a single value. This distinction is important because different commodities behave differently in the market. Essential goods like food and energy have a much larger impact when disrupted compared to non-essential goods. Additionally, this tensor helps in identifying dependencies of countries on specific commodities, which is useful for policy making and ensuring our country does not depend on only one source for a commodity.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.latex(r"T_{ijk}=\text{volume of export of commodity }k\text{ from country }i\text{ to country }j")
    st.markdown(
        """
        <div class="paper-card">
            <ul>
                <li>Dimensions: (countries x countries x commodities)</li>
                <li>Type: Weighted directed tensor</li>
                <li>Purpose: Captures trade flows for different commodities</li>
            </ul>
            <h3>2.3 Route Tensor (R)</h3>
            <p>This tensor models the infrastructure layer of the network, such as shipping routes, airways or railways that enable trade. We find this to be important as apart from using trade routes to analyse networks we use the infrastructure network to find alternative routes for any commodity in case of loss of connection.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.latex(r"R_{ijk}=\text{existence of route of transport }k\text{ from country }i\text{ to country }j")
    st.markdown(
        """
        <div class="paper-card">
            <ul>
                <li>Dimensions: (countries x countries x modes of transport)</li>
                <li>Type: Binary tensor</li>
                <li>Purpose: Represents the existence of transportation route</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="paper-card">
            <h2>3 Analysis Using Network Science</h2>
            <p>Now that the system is represented using the war matrix W, trade tensor T, and route tensor R, we can analyse the behaviour of the world trade network under different geopolitical scenarios.</p>
            <p>Country pairs that are not directly involved in a conflict may still be affected through intermediate trade partners. For example, several African countries were affected by the Russia-Ukraine war due to disruptions in global supply chains. With the full adjacency structure of trade routes, we can analyse alternative trade pathways when conflicts disrupt intermediate nodes. With the help of route tensor R we can also search for alternative routes.</p>
            <p>To start we make a degree distribution and fit a power law curve to find the gamma of the distribution. We can then find the clustering coefficient to give us idea about clusters. We can check whether the graph is connected under each mode of transport or whether certain regions are isolated.</p>
            <p>As in any real-world network, significant insights can be gained by identifying bottlenecks. These are nodes with high connectivity that are critical for maintaining the flow of goods and commodities. Metrics such as betweenness centrality and the Fiedler value or algebraic connectivity can be used to identify such important nodes. These measures can be computed per commodity or aggregated across all commodities.</p>
            <p>Identifying hubs and communities in this network provides information about how regions are interconnected through trade. Community detection algorithms can reveal clusters of countries with strong internal trade relationships.</p>
            <p>Since global trade networks often exhibit properties of scale-free networks, we can simulate cascading failures. A conflict between two major economies can trigger a domino effect, affecting multiple countries and trade routes. Shortest path analysis can be used to determine optimal trade routes, while robustness can be tested through targeted hub removal and random node deletion.</p>
            <p>By separating each mode of transport we can analyse railway networks, air trade networks and shipping networks to a significant extent. Dijkstra and A* can be used to analyse shortest paths, connectivity between nodes and connected components. Analysis of the aggregate matrix, which is the sum of all slices of the route tensor, will give us the full picture of trade of multiple commodities through multiple nations.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="paper-card">
            <h2>4 Conclusion</h2>
            <p>World trade can be modelled as a multilayer network including geopolitical conflicts, specific commodity trade, and trade route networks. The use of a war matrix, trade tensor and route tensor allows us to gain as much insight as we can.</p>
            <p>This network highlights the closely interconnected nature of world trade and shows us how interference such as war can spread effects throughout the network. Network science provides powerful tools to analyse these effects, provide us with crucial data, and evaluate system robustness and stability.</p>
            <p>Our goal with this project is to use network models to predict choke points in trade and give insight into which commodities are at risk of shortage in case of future war. We hope our project will provide meaningful new insights into underlying network behaviour.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

elif page == "Network Metrics":
    st.markdown(
        """
        <div class="hero">
            <p class="eyebrow">Network Analysis</p>
            <h1>Network Science Metrics</h1>
            <p>Degree statistics, connectivity, centrality, clustering, and structural summaries for war, trade, and route networks.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    metric_tabs = st.tabs(["War Layer", "Trade Layer", "Route Layer"])

    with metric_tabs[0]:
        war_graph = build_war_graph(war_matrix)
        war_summary = graph_metric_summary(war_graph, directed=False)
        war_centrality = centrality_frame(war_graph, directed=False)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Nodes", war_summary["nodes"])
        c2.metric("Edges", war_summary["edges"])
        c3.metric("Average Degree", f"{war_summary['avg_degree']:.2f}")
        c4.metric("Density", f"{war_summary['density']:.4f}")

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Connected Components", war_summary["components"])
        c6.metric("GCC Size", war_summary["gcc_nodes"])
        c7.metric("GCC Ratio", f"{war_summary['gcc_ratio']:.2%}")
        c8.metric("Clustering Coefficient", f"{war_summary['clustering']:.4f}")

        left, right = st.columns(2)
        with left:
            st.plotly_chart(degree_distribution_figure(war_graph, "War Degree Distribution"), width="stretch")
        with right:
            st.markdown('<div class="metrics-card">', unsafe_allow_html=True)
            st.subheader("Top Bottleneck Countries")
            st.dataframe(war_centrality.drop(columns=["eigenvector"]).head(12), hide_index=True, width="stretch")
            st.markdown('<p class="small-note">Betweenness centrality is especially useful here because it highlights countries that sit between many conflict-linked paths in the war and tension layer.</p>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with metric_tabs[1]:
        selected_metric_commodity = st.selectbox("Commodity slice", ["All commodities", *COMMODITIES], key="metric_trade_commodity")
        selected_metric_mode = st.selectbox("Route filter", ["All modes", *TRANSPORT_MODES], key="metric_trade_mode")
        trade_graph = build_trade_graph(commodity_tensor, transport_tensor, selected_metric_commodity, selected_metric_mode)
        trade_summary = graph_metric_summary(trade_graph, directed=True)
        trade_centrality = centrality_frame(trade_graph, directed=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Nodes", trade_summary["nodes"])
        c2.metric("Edges", trade_summary["edges"])
        c3.metric("Average Degree", f"{trade_summary['avg_degree']:.2f}")
        c4.metric("Density", f"{trade_summary['density']:.4f}")

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Weak Components", trade_summary["components"])
        c6.metric("GCC Size", trade_summary["gcc_nodes"])
        c7.metric("GCC Ratio", f"{trade_summary['gcc_ratio']:.2%}")
        c8.metric("Average Clustering", f"{trade_summary['clustering']:.4f}")

        c9 = st.columns(1)[0]
        c9.metric("Average Path Length", "-" if trade_summary["avg_path_length"] is None else f"{trade_summary['avg_path_length']:.3f}")

        left, right = st.columns(2)
        with left:
            st.plotly_chart(degree_distribution_figure(trade_graph, "Trade Degree Distribution"), width="stretch")
        with right:
            st.markdown('<div class="metrics-card">', unsafe_allow_html=True)
            st.subheader("Top Trade Hubs")
            st.dataframe(trade_centrality.drop(columns=["eigenvector"]).head(12), hide_index=True, width="stretch")
            st.markdown('<p class="small-note">For the trade layer, high-degree and high-betweenness countries are likely to function as hubs or bottlenecks for commodity circulation.</p>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with metric_tabs[2]:
        selected_route_mode = st.selectbox("Transport network", ["All modes", *TRANSPORT_MODES], key="metric_route_mode")
        route_graph = build_route_graph(transport_tensor, selected_route_mode)
        route_summary = graph_metric_summary(route_graph, directed=True)
        route_centrality = centrality_frame(route_graph, directed=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Nodes", route_summary["nodes"])
        c2.metric("Edges", route_summary["edges"])
        c3.metric("Average Degree", f"{route_summary['avg_degree']:.2f}")
        c4.metric("Density", f"{route_summary['density']:.4f}")

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Weak Components", route_summary["components"])
        c6.metric("GCC Size", route_summary["gcc_nodes"])
        c7.metric("GCC Ratio", f"{route_summary['gcc_ratio']:.2%}")
        c8.metric("Clustering Coefficient", f"{route_summary['clustering']:.4f}")

        left, right = st.columns(2)
        with left:
            st.plotly_chart(degree_distribution_figure(route_graph, "Route Degree Distribution"), width="stretch")
        with right:
            st.markdown('<div class="metrics-card">', unsafe_allow_html=True)
            st.subheader("Top Route Connectors")
            st.dataframe(route_centrality.drop(columns=["eigenvector"]).head(12), hide_index=True, width="stretch")
            st.markdown('<p class="small-note">This layer isolates infrastructure connectivity. It is useful for identifying whether particular transport modes create isolated regions or fragile chokepoints.</p>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
