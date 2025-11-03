import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path
import base64
import requests
from datetime import datetime

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Clinic P&L – Financial Model",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# UNIFIED PROFESSIONAL PALETTE
# One single blue scale for the whole app
# =========================================================
PALETTE = {
    "bg_page": "#F8FAFC",
    "surface": "#FFFFFF",
    "surface_alt": "#F1F5F9",
    "primary": "#1E40AF",
    "primary_light": "#3B82F6",
    "primary_dark": "#1E3A8A",
    "secondary": "#0EA5E9",
    "accent": "#60A5FA",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "text_primary": "#0F172A",
    "text_secondary": "#475569",
    "text_tertiary": "#64748B",
    "border": "#E2E8F0",
    "grid": "#F1F5F9",
    "chart": ["#1E40AF", "#3B82F6", "#0EA5E9", "#60A5FA", "#93C5FD", "#BFDBFE"],
}

# =========================================================
# PLOTLY THEME (force white background + blue colorway)
# =========================================================
clinic_template = go.layout.Template()
clinic_template.layout.paper_bgcolor = "white"
clinic_template.layout.plot_bgcolor = "white"
clinic_template.layout.font = dict(color=PALETTE["text_primary"], family="Inter, system-ui, sans-serif")
clinic_template.layout.colorway = PALETTE["chart"]
pio.templates["clinic_blue"] = clinic_template
pio.templates.default = "clinic_blue"

# =========================================================
# LOGO HANDLING - Safe loading with graceful fallback
# =========================================================
LOGO_PATH = "logo-colombiana-trasplantes-2024-blanco-2.png"

def load_logo_base64(path: str) -> str:
    """Safely load and encode logo image to base64."""
    try:
        logo_path = Path(path)
        if logo_path.exists():
            return base64.b64encode(logo_path.read_bytes()).decode()
    except Exception as e:
        st.warning(f"Logo not found: {e}")
    return None

logo_b64 = load_logo_base64(LOGO_PATH)

# =========================================================
# GLOBAL STYLES – force white cards even in dark theme
# =========================================================
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        box-sizing: border-box;
    }}

    .stApp {{
        background: {PALETTE["bg_page"]} !important;
        color: {PALETTE["text_primary"]} !important;
    }}

    .block-container {{
        padding-top: 0rem !important;
        max-width: 1900px;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
    }}

    /* HEADER */
    .ct-header {{
        background: linear-gradient(135deg, {PALETTE["primary"]} 0%, {PALETTE["primary_dark"]} 100%);
        padding: 2.5rem 3rem;
        margin-top: 3.4rem;
        margin-bottom: 2.5rem;
        border-radius: 0 0 24px 24px;
        box-shadow: 0 4px 20px rgba(30,64,175,0.15);
    }}
    .ct-main-title {{
        font-size: 2rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }}
    .ct-subtitle {{
        font-size: 1rem;
        color: rgba(255,255,255,0.9);
        margin: 0.75rem 0 0 0;
        font-weight: 400;
        line-height: 1.4;
    }}

    /* SIDEBAR */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {PALETTE["primary_dark"]} 0%, #1E293B 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.08);
    }}
    .sidebar-logo {{
        text-align: center;
        padding: 0rem 1rem 1.5rem 1rem;
        margin-top: -2.5rem;
        border-bottom: 2px solid rgba(255,255,255,0.12);
        margin-bottom: 1.5rem;
    }}
    .sidebar-logo img {{
        max-width: 110%;
        height: auto;
        filter: brightness(1.2);
    }}
    .ct-side-title {{
        color: #E2E8F0 !important;
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 1.6rem !important;
        margin-bottom: 0.6rem !important;
    }}

    /* Sidebar labels - always white */
    section[data-testid="stSidebar"] label {{
        color: #F9FAFB !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em;
    }}

    /* Sidebar subheaders - white */
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: #FFFFFF !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.8rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 1px solid rgba(255,255,255,0.2) !important;
    }}

    /* Inputs: white background, black text */
    section[data-testid="stSidebar"] .stNumberInput input,
    section[data-testid="stSidebar"] .stSelectbox select,
    section[data-testid="stSidebar"] select {{
        background: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        color: #0F172A !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        padding: 0.5rem !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        transition: all 0.2s ease !important;
    }}

    section[data-testid="stSidebar"] .stNumberInput input:focus,
    section[data-testid="stSidebar"] .stSelectbox select:focus,
    section[data-testid="stSidebar"] select:focus {{
        border: 2px solid {PALETTE["primary_light"]} !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }}

    /* Selectbox specific styling */
    section[data-testid="stSidebar"] .stSelectbox > div > div {{
        background: #FFFFFF !important;
        border-radius: 8px !important;
    }}

    /* Help icon styling - visible in both light and dark mode */
    section[data-testid="stSidebar"] .stTooltipIcon {{
        color: #FFFFFF !important;
        background-color: rgba(255,255,255,0.25) !important;
        border-radius: 50% !important;
        padding: 3px !important;
        width: 18px !important;
        height: 18px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    section[data-testid="stSidebar"] .stTooltipIcon:hover {{
        background-color: {PALETTE["primary_light"]} !important;
    }}

    section[data-testid="stSidebar"] .stTooltipIcon svg {{
        fill: #FFFFFF !important;
        stroke: #FFFFFF !important;
        color: #FFFFFF !important;
        width: 12px !important;
        height: 12px !important;
    }}

    section[data-testid="stSidebar"] .stTooltipIcon svg path {{
        fill: #FFFFFF !important;
        stroke: #FFFFFF !important;
    }}

    section[data-testid="stSidebar"] .stTooltipIcon svg circle {{
        stroke: #FFFFFF !important;
        fill: none !important;
    }}

    section[data-testid="stSidebar"] .stTooltipIcon svg text {{
        fill: #FFFFFF !important;
    }}

    section[data-testid="stSidebar"] .stTooltipIcon * {{
        color: #FFFFFF !important;
    }}

    /* Number input buttons */
    section[data-testid="stSidebar"] .stNumberInput button {{
        color: #0F172A !important;
    }}

    /* Input spacing and containers */
    section[data-testid="stSidebar"] .stNumberInput,
    section[data-testid="stSidebar"] .stSelectbox {{
        margin-bottom: 1rem !important;
    }}

    /* Sidebar dividers for visual separation */
    section[data-testid="stSidebar"] hr {{
        border: none !important;
        border-top: 1px solid rgba(255,255,255,0.15) !important;
        margin: 1.5rem 0 !important;
    }}

    /* Download button container - remove ALL background circles and elements */
    section[data-testid="stSidebar"] .stDownloadButton {{
        background: transparent !important;
    }}

    section[data-testid="stSidebar"] .stDownloadButton * {{
        background: transparent !important;
    }}

    section[data-testid="stSidebar"] .stDownloadButton > div {{
        background: transparent !important;
    }}

    section[data-testid="stSidebar"] .stDownloadButton div {{
        background: transparent !important;
    }}

    section[data-testid="stSidebar"] .stDownloadButton::before,
    section[data-testid="stSidebar"] .stDownloadButton::after,
    section[data-testid="stSidebar"] .stDownloadButton *::before,
    section[data-testid="stSidebar"] .stDownloadButton *::after {{
        display: none !important;
        background: transparent !important;
        content: none !important;
    }}

    section[data-testid="stSidebar"] .stDownloadButton button {{
        background: {PALETTE["primary_light"]} !important;
    }}

    /* Download button - simple and clean */
    section[data-testid="stSidebar"] .stDownloadButton button {{
        background: {PALETTE["primary_light"]} !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.75rem 1rem !important;
        width: 100% !important;
        margin-top: 3.5rem !important;
        margin-left: 16rem !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.2s ease !important;
        font-size: 0.8rem !important;
        line-height: 1.5 !important;
        text-align: center !important;
        white-space: pre-line !important;
        min-height: 3.5rem !important;
    }}

    section[data-testid="stSidebar"] .stDownloadButton button:hover {{
        background: {PALETTE["primary"]} !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
        transform: translateY(-1px) !important;
    }}

    section[data-testid="stSidebar"] .stDownloadButton button p,
    section[data-testid="stSidebar"] .stDownloadButton button div,
    section[data-testid="stSidebar"] .stDownloadButton button span {{
        writing-mode: horizontal-tb !important;
        display: inline !important;
        white-space: nowrap !important;
    }}

    /* Markdown text in sidebar */
    section[data-testid="stSidebar"] .stMarkdown p {{
        color: rgba(255,255,255,0.9) !important;
        font-size: 0.75rem !important;
        line-height: 1.5 !important;
    }}

    /* DATAFRAMES */
    div[data-testid="stDataFrame"] {{
        background: white !important;
        border: 1px solid {PALETTE["border"]} !important;
        border-radius: 16px !important;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(15,23,42,0.04);
    }}
    .dataframe thead tr th {{
        background: {PALETTE["primary"]} !important;
        color: white !important;
        text-transform: uppercase;
    }}

    /* Download button style (report) */
    .report-btn button {{
        background: {PALETTE["primary"]} !important;
        color: #ffffff !important;
        border-radius: 9999px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: .5rem 1.5rem !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <style>
    /* ===== SCENARIO BAR ===== */
    .ct-scenario {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 1rem;
        background: {PALETTE["surface"]};
        border: 1px solid {PALETTE["border"]};
        border-radius: 18px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 2px 8px rgba(15,23,42,0.03);
    }}
    .scenario-item {{
        display: flex;
        flex-direction: column;
        gap: .15rem;
    }}
    .scenario-label {{
        font-size: .65rem;
        text-transform: uppercase;
        letter-spacing: .05em;
        color: {PALETTE["text_tertiary"]};
        font-weight: 600;
    }}
    .scenario-value {{
        font-size: 1rem;
        font-weight: 700;
        color: {PALETTE["text_primary"]};
    }}

    /* ===== KPI CARDS (4 en una fila) ===== */
    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 1.25rem;
        margin-bottom: 2rem;
    }}
    .kpi-card {{
        background: {PALETTE["surface"]};
        border: 1px solid {PALETTE["border"]};
        border-radius: 1rem;
        padding: 1.2rem 1.2rem 1.05rem 1.2rem;
        box-shadow: 0 6px 20px rgba(15,23,42,0.04);
        position: relative;
        overflow: hidden;
    }}
    .kpi-accent {{
        position: absolute;
        inset: 0;
        height: 4px;
        background: linear-gradient(90deg, {PALETTE["primary"]} 0%, {PALETTE["secondary"]} 100%);
    }}
    .kpi-label {{
        margin-top: .6rem;
        font-size: .70rem;
        text-transform: uppercase;
        letter-spacing: .05em;
        color: {PALETTE["text_tertiary"]};
        font-weight: 600;
    }}
    .kpi-value {{
        font-size: 1.5rem;
        font-weight: 800;
        color: {PALETTE["text_primary"]};
        margin-top: .3rem;
        margin-bottom: .2rem;
    }}
    .kpi-meta {{
        font-size: .72rem;
        color: {PALETTE["text_secondary"]};
    }}

    /* ===== SECTION HEADERS ===== */
    .section-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin: 1.5rem 0 1rem 0;
    }}
    .section-title {{
        font-size: 1.1rem;
        font-weight: 700;
        color: {PALETTE["text_primary"]};
    }}

    /* ===== INSIGHT BOXES ===== */
    .insight-box {{
        background: {PALETTE["surface"]};
        border: 1px solid {PALETTE["border"]};
        border-radius: 1rem;
        padding: 1.2rem 1.2rem 1rem 1.2rem;
        margin-top: 1.1rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 6px 18px rgba(15,23,42,0.03);
    }}
    .insight-title {{
        font-weight: 700;
        margin-bottom: .9rem;
        display: flex;
        gap: .5rem;
        align-items: center;
    }}
    .insight-number {{
        background: {PALETTE["primary_light"]};
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 999px;
        display: grid;
        place-items: center;
        font-size: .7rem;
    }}
    .insight-content {{
        font-size: .78rem;
        color: {PALETTE["text_secondary"]};
        line-height: 1.45;
    }}

    /* TAGS */
    .insight-tag {{
        display: inline-block;
        padding: .20rem .55rem .25rem .55rem;
        border-radius: 9999px;
        background: rgba(99, 102, 241, .1);
        color: {PALETTE["text_primary"]};
        font-size: .63rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: .04em;
        margin-right: .35rem;
    }}
    .insight-tag.positive {{
        background: rgba(16, 185, 129, .12);
        color: #065f46;
    }}
    .insight-tag.warning {{
        background: rgba(245, 158, 11, .12);
        color: #92400e;
    }}
    .insight-tag.negative {{
        background: rgba(239, 68, 68, .1);
        color: #7f1d1d;
    }}

    /* FOOTER */
    .footer {{
        text-align: center;
        font-size: .7rem;
        color: {PALETTE["text_tertiary"]};
        margin-bottom: 2rem;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# PROFESSIONAL HEADER
# =========================================================
header_html = f"""
<div class="ct-header">
    <div>
        <h1 class="ct-main-title">Clinic P&L Financial Model</h1>
        <p class="ct-subtitle">Colombiana de Trasplantes · Outpatient Follow-up Division · Strategic Financial Analysis</p>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# =========================================================
# SIDEBAR – Unified, NO removed variables, all same style
# Removed:
#   - Start-up variable months
#   - Initial investment (% of Y1 profit)
# Kept:
#   - Initial investment (only one source of truth)
# =========================================================
if logo_b64:
    st.sidebar.markdown(
        f"""
        <div class="sidebar-logo">
            <img src="data:image/png;base64,{logo_b64}" alt="Colombiana de Trasplantes">
        </div>
        """,
        unsafe_allow_html=True
    )

# MODEL SETUP
st.sidebar.markdown('<div class="ct-side-title">Model Setup</div>', unsafe_allow_html=True)

# Function to fetch live exchange rates from Currency API
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_exchange_rates():
    """
    Fetch current exchange rates from Currency API (fawazahmed0/currency-api).
    Free, no API key required, updates daily. Supports 150+ currencies including COP.
    Falls back to static rates if API fails.
    """
    try:
        # Get rates with USD as base
        response_usd = requests.get('https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json', timeout=5)
        response_usd.raise_for_status()
        data_usd = response_usd.json()

        # Get rates with EUR as base
        response_eur = requests.get('https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/eur.json', timeout=5)
        response_eur.raise_for_status()
        data_eur = response_eur.json()

        # Get rates with COP as base
        response_cop = requests.get('https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/cop.json', timeout=5)
        response_cop.raise_for_status()
        data_cop = response_cop.json()

        # Extract rates
        usd_to_cop = data_usd['usd']['cop']
        usd_to_eur = data_usd['usd']['eur']
        eur_to_usd = data_eur['eur']['usd']
        eur_to_cop = data_eur['eur']['cop']
        cop_to_usd = data_cop['cop']['usd']
        cop_to_eur = data_cop['cop']['eur']

        rates = {
            "USD": {"USD": 1.0, "COP": usd_to_cop, "EUR": usd_to_eur},
            "COP": {"USD": cop_to_usd, "COP": 1.0, "EUR": cop_to_eur},
            "EUR": {"USD": eur_to_usd, "COP": eur_to_cop, "EUR": 1.0}
        }

        return rates, data_usd['date']

    except Exception as e:
        # Fallback to static rates if API fails
        st.warning(f"Using cached exchange rates. Live rates unavailable: {str(e)}")
        fallback_rates = {
            "USD": {"USD": 1.0, "COP": 3855.0, "EUR": 0.868},
            "COP": {"USD": 1/3855.0, "COP": 1.0, "EUR": 0.868/3855.0},
            "EUR": {"USD": 1/0.868, "COP": 3855.0/0.868, "EUR": 1.0}
        }
        return fallback_rates, "Cached"

# Get live exchange rates
EXCHANGE_RATES, rates_date = get_exchange_rates()

# Initialize session state for currency tracking
if 'previous_currency' not in st.session_state:
    st.session_state.previous_currency = "USD"
if 'base_values' not in st.session_state:
    # Store base values in USD
    st.session_state.base_values = {
        'tariff': 54.0,
        'drugs_base': 1.34,
        'labs_base': 0.17,
        'clinical_pay': 831.0,
        'admin_pay': 399.0,
        'rent': 125.0,
        'ehr_m': 2.0,
        'it_m': 1.0,
        'office_y': 10.0,
        'licenses_y': 5.0,
        'mal_md_y': 20.0,
        'mal_np_y': 3.0,
        'initial_investment': 650.0,
        'low_tariff': 42.0
    }

currency = st.sidebar.selectbox(
    "Currency",
    ["USD", "COP", "EUR"],
    index=0,
    help=f"Select the currency for all financial values throughout the model (USD: US Dollar, COP: Colombian Peso, EUR: Euro). Exchange rates updated: {rates_date}"
)

# Show exchange rates info
if rates_date != "Cached":
    rates_info = f"1 USD = {EXCHANGE_RATES['USD']['COP']:.2f} COP | 1 EUR = {EXCHANGE_RATES['EUR']['USD']:.4f} USD"
    st.sidebar.caption(f"📊 Rates ({rates_date}): {rates_info}")

# Dynamic currency label
currency_label = f"k{currency}"
currency_symbol = "$" if currency == "USD" else "€" if currency == "EUR" else "$"

# Convert values when currency changes
if currency != st.session_state.previous_currency:
    conversion_rate = EXCHANGE_RATES[st.session_state.previous_currency][currency]
    for key in st.session_state.base_values:
        st.session_state.base_values[key] *= conversion_rate
    st.session_state.previous_currency = currency

# VOLUME & PRICING
st.sidebar.markdown('<div class="ct-side-title">Volume & Pricing</div>', unsafe_allow_html=True)
patients = st.sidebar.number_input(
    "Patients per year",
    min_value=0,
    max_value=2000,
    value=250,
    step=5,
    help="Total annual patient volume served by the clinic. This is the primary revenue driver and affects variable costs like drugs and labs."
)
tariff = st.sidebar.number_input(
    f"Tariff per patient/year ({currency_label})",
    min_value=0.0,
    max_value=1000000.0,
    value=st.session_state.base_values['tariff'],
    step=1.0 if currency != "COP" else 1000.0,
    help="Average annual reimbursement received per patient from insurance payers or healthcare system. This is your primary revenue per patient."
)
st.session_state.base_values['tariff'] = tariff

# VARIABLE COSTS
st.sidebar.markdown('<div class="ct-side-title">Variable Costs</div>', unsafe_allow_html=True)
drugs_base = st.sidebar.number_input(
    f"Drugs ({currency_label}/patient/month)",
    min_value=0.0,
    max_value=100000.0,
    value=st.session_state.base_values['drugs_base'],
    step=0.01 if currency != "COP" else 100.0,
    help="Base monthly pharmaceutical cost per patient. Includes immunosuppressants and other medications required for transplant follow-up care."
)
st.session_state.base_values['drugs_base'] = drugs_base
drugs_cont = st.sidebar.number_input(
    "Drugs contingency (%)",
    min_value=0.0,
    max_value=100.0,
    value=20.0,
    step=1.0,
    help="Safety buffer percentage to account for drug price fluctuations, dosage adjustments, or unexpected medication needs."
) / 100.0

labs_base = st.sidebar.number_input(
    f"Labs & imaging ({currency_label}/patient/month)",
    min_value=0.0,
    max_value=50000.0,
    value=st.session_state.base_values['labs_base'],
    step=0.01 if currency != "COP" else 100.0,
    help="Base monthly cost for laboratory tests and imaging studies per patient. Includes routine monitoring and diagnostic procedures."
)
st.session_state.base_values['labs_base'] = labs_base
labs_cont = st.sidebar.number_input(
    "Labs contingency (%)",
    min_value=0.0,
    max_value=100.0,
    value=20.0,
    step=1.0,
    help="Safety buffer percentage for unexpected tests, additional imaging, or price variations in diagnostic services."
) / 100.0

# PAYROLL
st.sidebar.markdown(f'<div class="ct-side-title">Payroll (Annual, {currency_label})</div>', unsafe_allow_html=True)
clinical_pay = st.sidebar.number_input(
    "Clinical staff",
    min_value=0.0,
    max_value=50000000.0,
    value=st.session_state.base_values['clinical_pay'],
    step=5.0 if currency != "COP" else 5000.0,
    help="Total annual base salaries for all clinical personnel including physicians, nurses, nurse practitioners, and medical assistants."
)
st.session_state.base_values['clinical_pay'] = clinical_pay
clinical_bur = st.sidebar.number_input(
    "Clinical burden (%)",
    min_value=0.0,
    max_value=100.0,
    value=25.0,
    step=1.0,
    help="Payroll burden rate covering benefits, payroll taxes, health insurance, retirement contributions, and other employment costs."
) / 100.0

admin_pay = st.sidebar.number_input(
    "Administrative staff",
    min_value=0.0,
    max_value=50000000.0,
    value=st.session_state.base_values['admin_pay'],
    step=5.0 if currency != "COP" else 5000.0,
    help="Total annual base salaries for administrative personnel including office managers, billing staff, schedulers, and support staff."
)
st.session_state.base_values['admin_pay'] = admin_pay
admin_bur = st.sidebar.number_input(
    "Admin burden (%)",
    min_value=0.0,
    max_value=100.0,
    value=25.0,
    step=1.0,
    help="Payroll burden rate for administrative staff covering benefits, taxes, insurance, and other employment-related costs."
) / 100.0

# FACILITIES & OPEX
st.sidebar.markdown('<div class="ct-side-title">Facilities & OPEX</div>', unsafe_allow_html=True)
rent = st.sidebar.number_input(
    f"Rent (annual, {currency_label})",
    min_value=0.0,
    max_value=10000000.0,
    value=st.session_state.base_values['rent'],
    step=5.0 if currency != "COP" else 5000.0,
    help="Total annual facility lease or occupancy cost for clinic space. Includes rent, property fees, and basic facility charges."
)
st.session_state.base_values['rent'] = rent
util_pct = st.sidebar.number_input(
    "Utilities (% of rent)",
    min_value=0.0,
    max_value=100.0,
    value=15.0,
    step=1.0,
    help="Utilities cost as a percentage of rent. Covers electricity, water, gas, heating/cooling, and other building services."
) / 100.0
ehr_m = st.sidebar.number_input(
    f"EHR ({currency_label}/month)",
    min_value=0.0,
    max_value=500000.0,
    value=st.session_state.base_values['ehr_m'],
    step=0.5 if currency != "COP" else 500.0,
    help="Monthly subscription cost for Electronic Health Record (EHR) system. Includes software licensing, hosting, and support."
)
st.session_state.base_values['ehr_m'] = ehr_m
it_m = st.sidebar.number_input(
    f"IT/phone/internet ({currency_label}/month)",
    min_value=0.0,
    max_value=500000.0,
    value=st.session_state.base_values['it_m'],
    step=0.5 if currency != "COP" else 500.0,
    help="Monthly technology and communications costs including internet service, phone systems, IT support, and network infrastructure."
)
st.session_state.base_values['it_m'] = it_m
office_y = st.sidebar.number_input(
    f"Office & supplies (annual, {currency_label})",
    min_value=0.0,
    max_value=5000000.0,
    value=st.session_state.base_values['office_y'],
    step=1.0 if currency != "COP" else 1000.0,
    help="Annual cost for general office supplies, medical supplies, stationery, forms, and other consumables needed for operations."
)
st.session_state.base_values['office_y'] = office_y
licenses_y = st.sidebar.number_input(
    f"Licenses & dues (annual, {currency_label})",
    min_value=0.0,
    max_value=5000000.0,
    value=st.session_state.base_values['licenses_y'],
    step=1.0 if currency != "COP" else 1000.0,
    help="Annual professional licenses, certifications, association memberships, and regulatory compliance fees for the clinic and staff."
)
st.session_state.base_values['licenses_y'] = licenses_y
mal_md_y = st.sidebar.number_input(
    f"Malpractice MD (annual, {currency_label})",
    min_value=0.0,
    max_value=2000000.0,
    value=st.session_state.base_values['mal_md_y'],
    step=1.0 if currency != "COP" else 1000.0,
    help="Annual malpractice insurance premium per physician (MD/DO). Protects against professional liability claims."
)
st.session_state.base_values['mal_md_y'] = mal_md_y
mal_np_y = st.sidebar.number_input(
    f"Malpractice NP (annual, {currency_label})",
    min_value=0.0,
    max_value=2000000.0,
    value=st.session_state.base_values['mal_np_y'],
    step=1.0 if currency != "COP" else 1000.0,
    help="Annual malpractice insurance premium per nurse practitioner (NP/PA). Generally lower than physician coverage."
)
st.session_state.base_values['mal_np_y'] = mal_np_y

# TAX, GROWTH, INVESTMENT
# Tax, Growth & Valuation
st.sidebar.subheader("Tax & Valuation")

tax_rate = st.sidebar.number_input(
    "Income tax rate (%)",
    min_value=0.0,
    max_value=100.0,
    value=21.0,
    step=1.0,
    help="Effective corporate income tax rate applied to EBITDA. Varies by jurisdiction (e.g., 21% US federal, ~32% Colombia)."
) / 100.0

rev_growth = st.sidebar.number_input(
    "Revenue/FCF growth (%)",
    min_value=0.0,
    max_value=100.0,
    value=15.0,
    step=1.0,
    help="Expected annual growth rate for revenue and free cash flow projections. Used in 5-year DCF valuation model."
) / 100.0

ke = st.sidebar.number_input(
    "Discount rate / Ke (%)",
    min_value=0.0,
    max_value=100.0,
    value=18.0,
    step=0.5,
    help="Cost of equity (Ke) - the required rate of return investors expect. Used as discount rate in NPV calculations."
) / 100.0

# ✅ NUEVO: este reemplaza al porcentaje sobre la utilidad
initial_investment = st.sidebar.number_input(
    f"Initial investment ({currency_label})",
    min_value=0.0,
    max_value=50000000.0,
    value=st.session_state.base_values['initial_investment'],
    step=50.0 if currency != "COP" else 50000.0,
    help="Upfront capital required for clinic setup including equipment, furniture, initial inventory, and startup costs (Year 0 cash flow)."
)
st.session_state.base_values['initial_investment'] = initial_investment

# ✅ Se mantiene porque la DCF lo usa en la Parte 2
fcf_factor = st.sidebar.number_input(
    "FCF as % of net profit",
    min_value=5.0,
    max_value=100.0,
    value=40.0,
    step=5.0,
    help="Free Cash Flow conversion rate - the percentage of net profit that converts to actual distributable cash after working capital needs."
) / 100.0

# STRESS TESTING – no sliders, only number inputs
st.sidebar.markdown('<div class="ct-side-title">Stress Testing</div>', unsafe_allow_html=True)
mix_low_pct = st.sidebar.number_input(
    "Low-tariff patients (%)",
    min_value=0.0,
    max_value=50.0,
    value=30.0,
    step=5.0,
    help="Percentage of patient volume receiving lower reimbursement rates (e.g., Medicaid, discounted plans). Used for downside scenario analysis."
) / 100.0
low_tariff = st.sidebar.number_input(
    f"Low tariff ({currency_label})",
    min_value=0.0,
    max_value=2000000.0,
    value=st.session_state.base_values['low_tariff'],
    step=1.0 if currency != "COP" else 1000.0,
    help="Reduced annual reimbursement rate for low-payer mix patients. Typically 20-30% below standard tariff."
)
st.session_state.base_values['low_tariff'] = low_tariff
stress_costs = st.sidebar.number_input(
    "Clinical cost stress (%)",
    min_value=0.0,
    max_value=30.0,
    value=10.0,
    step=5.0,
    help="Cost inflation percentage applied to clinical expenses in stress scenario. Simulates wage increases, supply chain issues, or market pressures."
) / 100.0

# =========================================================
# PART 2: CORE FINANCIAL CALCULATIONS & FUNCTIONS
# All metrics, calculations, and interpretation functions
# =========================================================

# =========================================================
# REVENUE CALCULATIONS
# =========================================================
rev_m = patients * tariff / 12  # Monthly revenue (kUSD)
rev_y = rev_m * 12              # Annual revenue (kUSD)

# =========================================================
# CLINICAL STAFF COSTS (Fixed)
# =========================================================
clinical_m = clinical_pay * (1 + clinical_bur) / 12
clinical_y = clinical_m * 12

# =========================================================
# VARIABLE COSTS - Drugs and Labs
# =========================================================
drugs_m = drugs_base * patients * (1 + drugs_cont)
labs_m = labs_base * patients * (1 + labs_cont)
drugs_y = drugs_m * 12
labs_y = labs_m * 12

# =========================================================
# GROSS PROFIT
# =========================================================
gross_m = rev_m - (clinical_m + drugs_m + labs_m)
gross_y = gross_m * 12

# =========================================================
# ADMINISTRATIVE COSTS (Fixed)
# =========================================================
admin_m = admin_pay * (1 + admin_bur) / 12
admin_y = admin_m * 12

# =========================================================
# OTHER OPERATING EXPENSES (Fixed)
# =========================================================
other_m = (
    (rent / 12) * (1 + util_pct) +             # rent + utilities
    (ehr_m + it_m) +                           # monthly IT/EHR
    (office_y + licenses_y + mal_md_y + mal_np_y) / 12   # annual overhead to monthly
)
other_y = other_m * 12

# =========================================================
# EBITDA - Operating Profit
# =========================================================
ebitda_m = gross_m - admin_m - other_m
ebitda_y = ebitda_m * 12

# =========================================================
# TAXES AND NET PROFIT
# =========================================================
taxes_y = max(0, ebitda_y * tax_rate)
net_y = ebitda_y - taxes_y

# =========================================================
# BREAK-EVEN ANALYSIS
# =========================================================
# variable cost per patient per month (kUSD)
var_pp_m = (drugs_base * (1 + drugs_cont)) + (labs_base * (1 + labs_cont))
var_pp_y = var_pp_m * 12
# contribution per patient per year
contrib_pp = tariff - var_pp_y
fixed_y = clinical_y + admin_y + other_y

if contrib_pp > 0:
    be_patients = fixed_y / contrib_pp
    be_revenue = be_patients * tariff
    mos_pat = patients - be_patients
    mos_pct = (patients - be_patients) / patients if patients > 0 else 0
else:
    be_patients = np.nan
    be_revenue = np.nan
    mos_pat = np.nan
    mos_pct = np.nan

if patients > 0:
    # tariff needed to break even AT CURRENT VOLUME
    be_tariff_at_plan = var_pp_y + (fixed_y / patients)
    tariff_headroom = max(0, tariff - be_tariff_at_plan)
else:
    be_tariff_at_plan = np.nan
    tariff_headroom = np.nan

# =========================================================
# KEY PERFORMANCE METRICS
# =========================================================
ebitda_margin = ebitda_y / rev_y if rev_y > 0 else 0
net_margin = net_y / rev_y if rev_y > 0 else 0
gross_margin = gross_y / rev_y if rev_y > 0 else 0
fixed_ratio = fixed_y / rev_y if rev_y > 0 else 0
var_ratio = (drugs_y + labs_y) / rev_y if rev_y > 0 else 0
ebitda_per_patient = ebitda_y / patients if patients > 0 else 0
revenue_per_patient = rev_y / patients if patients > 0 else 0

total_costs = clinical_y + drugs_y + labs_y + admin_y + other_y
revenue_per_dollar_cost = rev_y / total_costs if total_costs > 0 else 0
clinical_cost_per_patient = clinical_y / patients if patients > 0 else 0
total_cost_per_patient = total_costs / patients if patients > 0 else 0

# =========================================================
# CASH FLOW PROJECTIONS - 5-Year DCF
# IMPORTANT: we removed "startup_var_months" and
# "Initial investment (% of Y1 profit)".
# Now Year 0 = -(initial_investment)
# =========================================================

# Year 0 cash flow (kUSD): only the initial investment the user entered
cf0 = -initial_investment

# Base free cash flow = net profit × FCF conversion
cf1 = net_y * fcf_factor
cf2 = cf1 * (1 + rev_growth)
cf3 = cf2 * (1 + rev_growth)
cf4 = cf3 * (1 + rev_growth)
cf5 = cf4 * (1 + rev_growth)

cf_vec = np.array([cf0, cf1, cf2, cf3, cf4, cf5], dtype=float)

cf_df = pd.DataFrame({
    "Year": ["Year 0 (Initial)", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"],
    f"Cash Flow ({currency_label})": [f"{currency_symbol}{v:,.0f}k" for v in cf_vec],
    f"Cumulative CF ({currency_label})": [f"{currency_symbol}{v:,.0f}k" for v in np.cumsum(cf_vec)],
    "Description": [
        f"Initial investment: {currency_symbol}{initial_investment:,.0f}k",
        f"Year 1 FCF: {fcf_factor*100:.0f}% of net profit",
        f"Year 2 FCF: Y1 × (1 + {rev_growth*100:.0f}%)",
        f"Year 3 FCF: Y2 × (1 + {rev_growth*100:.0f}%)",
        f"Year 4 FCF: Y3 × (1 + {rev_growth*100:.0f}%)",
        f"Year 5 FCF: Y4 × (1 + {rev_growth*100:.0f}%)"
    ]
})

# =========================================================
# DCF VALUATION FUNCTIONS
# =========================================================
def npv_calc(rate, cfs):
    """Calculate Net Present Value"""
    years = np.arange(len(cfs))
    return float(np.sum(cfs / (1 + rate) ** years))

def irr_calc(cfs, guess=0.2):
    """Calculate Internal Rate of Return using Newton-Raphson"""
    r = guess
    for _ in range(100):
        yrs = np.arange(len(cfs))
        f = np.sum(cfs / (1 + r) ** yrs)
        df = np.sum(-yrs * cfs / (1 + r) ** (yrs + 1))
        if abs(df) < 1e-9:
            break
        nr = r - f / df
        if abs(nr - r) < 1e-7:
            return float(nr)
        r = nr
    return None

npv_val = npv_calc(ke, cf_vec)
irr_val = irr_calc(cf_vec)
cum_cf = np.cumsum(cf_vec)
payback_year = next((i for i, v in enumerate(cum_cf) if v >= 0), None)

# =========================================================
# P&L DATAFRAME
# =========================================================
pnl_df = pd.DataFrame({
    "Line Item": [
        "Revenue",
        "Clinical Staff",
        "Drugs (with contingency)",
        "Exams / Labs (with contingency)",
        "Gross Profit",
        "Administrative Staff",
        "Other Operating Expenses",
        "EBITDA",
        "Income Tax",
        "Net Profit",
    ],
    f"Monthly ({currency_label})": [
        f"{currency_symbol}{rev_m:,.0f}",
        f"-{currency_symbol}{clinical_m:,.0f}",
        f"-{currency_symbol}{drugs_m:,.0f}",
        f"-{currency_symbol}{labs_m:,.0f}",
        f"{currency_symbol}{gross_m:,.0f}",
        f"-{currency_symbol}{admin_m:,.0f}",
        f"-{currency_symbol}{other_m:,.0f}",
        f"{currency_symbol}{ebitda_m:,.0f}",
        f"-{currency_symbol}{taxes_y/12:,.0f}",
        f"{currency_symbol}{net_y/12:,.0f}",
    ],
    f"Annual ({currency_label})": [
        f"{currency_symbol}{rev_y:,.0f}",
        f"-{currency_symbol}{clinical_y:,.0f}",
        f"-{currency_symbol}{drugs_y:,.0f}",
        f"-{currency_symbol}{labs_y:,.0f}",
        f"{currency_symbol}{gross_y:,.0f}",
        f"-{currency_symbol}{admin_y:,.0f}",
        f"-{currency_symbol}{other_y:,.0f}",
        f"{currency_symbol}{ebitda_y:,.0f}",
        f"-{currency_symbol}{taxes_y:,.0f}",
        f"{currency_symbol}{net_y:,.0f}",
    ],
    "% of Revenue": [
        "100.0%",
        f"{(clinical_y/rev_y*100):.1f}%" if rev_y > 0 else "0.0%",
        f"{(drugs_y/rev_y*100):.1f}%" if rev_y > 0 else "0.0%",
        f"{(labs_y/rev_y*100):.1f}%" if rev_y > 0 else "0.0%",
        f"{(gross_y/rev_y*100):.1f}%" if rev_y > 0 else "0.0%",
        f"{(admin_y/rev_y*100):.1f}%" if rev_y > 0 else "0.0%",
        f"{(other_y/rev_y*100):.1f}%" if rev_y > 0 else "0.0%",
        f"{(ebitda_y/rev_y*100):.1f}%" if rev_y > 0 else "0.0%",
        f"{(taxes_y/rev_y*100):.1f}%" if rev_y > 0 else "0.0%",
        f"{(net_y/rev_y*100):.1f}%" if rev_y > 0 else "0.0%",
    ],
})

# =========================================================
# UTILITY FUNCTIONS
# =========================================================
def format_currency(value, decimals=0, curr_label=None, curr_symbol=None):
    """Format currency values consistently"""
    label = curr_label if curr_label else currency_label
    symbol = curr_symbol if curr_symbol else currency_symbol
    return f"{symbol}{value:,.{decimals}f}{label[-1]}"

def format_percentage(value, decimals=1):
    """Format percentage values consistently"""
    return f"{value*100:.{decimals}f}%"

def safe_divide(numerator, denominator, default=0):
    """Safe division with default value"""
    return numerator / denominator if denominator != 0 else default

def apply_chart_layout(fig, height=400, title=""):
    """Apply consistent styling to Plotly charts (white bg + blue)"""
    fig.update_layout(
        template="clinic_blue",
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=height,
        title=dict(text=title, font=dict(size=16, color=PALETTE["text_primary"], family="Inter")),
        font=dict(family="Inter", color=PALETTE["text_primary"], size=12),
        margin=dict(t=60, b=60, l=70, r=40),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Inter",
            bordercolor=PALETTE["border"]
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=PALETTE["text_primary"])
        )
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=PALETTE["grid"],
        gridwidth=1,
        zeroline=False,
        showline=True,
        linewidth=1,
        linecolor=PALETTE["border"],
        title_font=dict(size=12, color=PALETTE["text_primary"])
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=PALETTE["grid"],
        gridwidth=1,
        zeroline=False,
        showline=True,
        linewidth=1,
        linecolor=PALETTE["border"],
        title_font=dict(size=12, color=PALETTE["text_primary"])
    )
    return fig

def create_insight_box(number, title, content):
    """Generate standardized insight box HTML"""
    return f"""
    <div class="insight-box">
        <div class="insight-title">
            <span class="insight-number">{number}</span>
            {title}
        </div>
        <div class="insight-content">
            {content}
        </div>
    </div>
    """

# =========================================================
# INTERPRETATION FUNCTIONS - FIXED: Proper HTML formatting
# =========================================================
def interpret_margin(margin, metric_name):
    """Generate margin interpretation with proper tags"""
    if metric_name == "EBITDA":
        if margin >= 0.40:
            tag = '<span class="insight-tag positive">EXCEPTIONAL</span>'
            text = f"{metric_name} margin of <b>{format_percentage(margin)}</b> significantly exceeds industry benchmarks (25–35% for outpatient facilities)."
        elif margin >= 0.30:
            tag = '<span class="insight-tag positive">STRONG</span>'
            text = f"{metric_name} margin of <b>{format_percentage(margin)}</b> is within top-quartile range for specialized outpatient services."
        elif margin >= 0.20:
            tag = '<span class="insight-tag">ADEQUATE</span>'
            text = f"{metric_name} margin of <b>{format_percentage(margin)}</b> meets industry standards."
        elif margin >= 0.10:
            tag = '<span class="insight-tag warning">BELOW TARGET</span>'
            text = f"{metric_name} margin of <b>{format_percentage(margin)}</b> is below optimal levels."
        else:
            tag = '<span class="insight-tag negative">CRITICAL</span>'
            text = f"{metric_name} margin of <b>{format_percentage(margin)}</b> indicates fundamental profitability challenges."
    else:
        if margin >= 0.25:
            tag = '<span class="insight-tag positive">EXCELLENT</span>'
            text = f"Net margin of <b>{format_percentage(margin)}</b> demonstrates strong bottom-line performance."
        elif margin >= 0.15:
            tag = '<span class="insight-tag positive">HEALTHY</span>'
            text = f"Net margin of <b>{format_percentage(margin)}</b> provides adequate returns."
        elif margin >= 0.08:
            tag = '<span class="insight-tag">ACCEPTABLE</span>'
            text = f"Net margin of <b>{format_percentage(margin)}</b> is sustainable."
        else:
            tag = '<span class="insight-tag warning">SUBOPTIMAL</span>'
            text = f"Net margin of <b>{format_percentage(margin)}</b> may challenge long-term viability."
    
    return f"{tag} {text}"

def interpret_breakeven(patients_plan, be_patients, mos_pct):
    """Generate break-even interpretation"""
    if np.isnan(be_patients) or np.isnan(mos_pct):
        return '<span class="insight-tag negative">ERROR</span> Unable to calculate break-even metrics with current parameters.'
    
    if mos_pct >= 0.60:
        tag = '<span class="insight-tag positive">ROBUST SAFETY</span>'
        text = f"Current volume of <b>{patients_plan:,.0f} patients</b> exceeds break-even of <b>{be_patients:,.0f}</b> by <b>{format_percentage(mos_pct)}</b>. Business can withstand significant volume erosion."
    elif mos_pct >= 0.40:
        tag = '<span class="insight-tag positive">SOLID BUFFER</span>'
        text = f"Margin of safety at <b>{format_percentage(mos_pct)}</b> provides reasonable protection. Break-even: <b>{be_patients:,.0f} patients</b>."
    elif mos_pct >= 0.25:
        tag = '<span class="insight-tag">MODERATE RISK</span>'
        text = f"Margin of safety at <b>{format_percentage(mos_pct)}</b> suggests vulnerability. Break-even: <b>{be_patients:,.0f} patients</b>."
    elif mos_pct >= 0.15:
        tag = '<span class="insight-tag warning">HIGH RISK</span>'
        text = f"Thin margin of safety at <b>{format_percentage(mos_pct)}</b>. Break-even: <b>{be_patients:,.0f} patients</b>."
    else:
        tag = '<span class="insight-tag negative">CRITICAL EXPOSURE</span>'
        text = f"Margin of safety at <b>{format_percentage(mos_pct)}</b> indicates extremely fragile position."
    
    return f"{tag} {text}"

def interpret_unit_economics(contrib_pp, ebitda_per_patient, tariff):
    """Analyze per-patient profitability - FIXED: Proper spacing"""
    contrib_rate = safe_divide(contrib_pp, tariff)
    
    if contrib_rate >= 0.70:
        status = "EXCEPTIONAL"
        status_class = "positive"
        detail = "High contribution margin indicates strong pricing power and efficient variable cost management."
    elif contrib_rate >= 0.50:
        status = "HEALTHY"
        status_class = "positive"
        detail = "Solid contribution margin provides good coverage for fixed costs."
    elif contrib_rate >= 0.35:
        status = "ACCEPTABLE"
        status_class = ""
        detail = "Moderate contribution margin is sustainable but leaves limited buffer for cost increases."
    else:
        status = "WEAK"
        status_class = "warning"
        detail = "Low contribution margin indicates pricing pressure or high variable costs requiring attention."
    
    return f"""Unit contribution of <b>{format_currency(contrib_pp)}</b> per patient represents <b>{format_percentage(contrib_rate)}</b> of tariff.<br><br>
<span class="insight-tag {status_class}">{status} UNIT ECONOMICS</span><br><br>
{detail}<br><br>
<b>EBITDA per patient:</b> {format_currency(ebitda_per_patient)}<br>
<b>Contribution margin:</b> {format_percentage(contrib_rate)} (industry target: 50%+)"""

def interpret_cost_structure(fixed_ratio, var_ratio, clinical_y, admin_y):
    """Analyze cost structure - FIXED: Proper spacing"""
    admin_ratio = safe_divide(admin_y, (clinical_y + admin_y))
    
    if fixed_ratio >= 0.50:
        structure = "HIGH FIXED BURDEN"
        structure_class = "warning"
        leverage = "High operating leverage: profits are very sensitive to volume changes."
    elif fixed_ratio >= 0.35:
        structure = "BALANCED STRUCTURE"
        structure_class = ""
        leverage = "Balanced cost structure provides moderate operating leverage."
    else:
        structure = "VARIABLE-HEAVY"
        structure_class = "positive"
        leverage = "Variable-heavy structure provides cost flexibility but limits economies of scale."
    
    return f"""Fixed costs represent <b>{format_percentage(fixed_ratio)}</b> of revenue (Clinical: {format_currency(clinical_y)}, Admin: {format_currency(admin_y)}).<br>
Variable costs represent <b>{format_percentage(var_ratio)}</b>.<br><br>
<span class="insight-tag {structure_class}">{structure}</span><br><br>
{leverage}<br><br>
<b>Administrative ratio:</b> {format_percentage(admin_ratio)} of total labor {'(lean structure)' if admin_ratio <= 0.35 else '(typical for healthcare)' if admin_ratio <= 0.45 else '(high admin burden)'}"""

def interpret_valuation(npv_val, irr_val, payback_year, ebitda_y, ke):
    """Investment valuation interpretation - FIXED: Proper spacing and no broken tags"""
    npv_status = "VALUE CREATIVE" if npv_val > 0 else "VALUE DESTRUCTIVE"
    npv_class = "positive" if npv_val > 0 else "negative"
    
    result = (
        f'DCF analysis yields NPV of <b>{format_currency(npv_val)}</b> at '
        f'<b>{format_percentage(ke)}</b> discount rate. '
        f'<span class="insight-tag {npv_class}">{npv_status}</span><br><br>'
    )
    
    if irr_val is not None:
        irr_status = "EXCEEDS HURDLE" if irr_val > ke else "BELOW HURDLE"
        irr_class = "positive" if irr_val > ke else "negative"
        hurdle_spread = (irr_val - ke) * 100
        result += (
            f'Internal Rate of Return: <b>{format_percentage(irr_val)}</b> '
            f'<span class="insight-tag {irr_class}">{irr_status}</span><br>'
            f'Spread vs. hurdle rate: <b>{hurdle_spread:+.1f}pp</b><br><br>'
        )
    
    if payback_year is not None:
        payback_quality = "excellent" if payback_year <= 2 else "good" if payback_year <= 3 else "acceptable" if payback_year <= 4 else "extended"
        result += f"Payback period: <b>{payback_year} years</b> ({payback_quality} capital recovery)<br><br>"
    
    ev_ebitda = safe_divide(npv_val, ebitda_y)
    if not np.isnan(ev_ebitda) and ev_ebitda > 0:
        multiple_assessment = "premium" if ev_ebitda >= 8 else "market" if ev_ebitda >= 5 else "discount"
        result += (
            f"Implied EV/EBITDA multiple: <b>{ev_ebitda:.1f}x</b> ({multiple_assessment} valuation)<br>"
            "Healthcare outpatient benchmarks: 6–10x EBITDA"
        )
    
    return result

def generate_stress_scenarios(
    patients,
    tariff,
    mix_low_pct,
    low_tariff,
    clinical_y,
    drugs_y,
    labs_y,
    admin_y,
    other_y,
    stress_costs
):
    """Generate stress scenarios with same blue logic"""
    scenarios = []
    
    base_rev = patients * tariff
    base_costs = clinical_y + drugs_y + labs_y + admin_y + other_y
    base_ebitda = base_rev - base_costs
    base_margin = safe_divide(base_ebitda, base_rev)
    
    # 1. Payer mix erosion
    stress1_rev = (patients * (1 - mix_low_pct) * tariff) + (patients * mix_low_pct * low_tariff)
    stress1_ebitda = stress1_rev - base_costs
    stress1_margin = safe_divide(stress1_ebitda, stress1_rev)
    stress1_impact = safe_divide((stress1_ebitda - base_ebitda) * 100, base_ebitda, -100)
    scenarios.append({
        "name": "Payer Mix Erosion",
        "description": f"{mix_low_pct*100:.0f}% patients at {format_currency(low_tariff)} tariff",
        "ebitda": stress1_ebitda,
        "margin": stress1_margin,
        "impact_pct": stress1_impact,
    })
    
    # 2. Volume decline
    stress2_patients = patients * 0.85
    stress2_rev = stress2_patients * tariff
    stress2_var_costs = (drugs_y + labs_y) * 0.85
    stress2_costs = clinical_y + stress2_var_costs + admin_y + other_y
    stress2_ebitda = stress2_rev - stress2_costs
    stress2_margin = safe_divide(stress2_ebitda, stress2_rev)
    stress2_impact = safe_divide((stress2_ebitda - base_ebitda) * 100, base_ebitda, -100)
    scenarios.append({
        "name": "Volume Decline",
        "description": "15% patient volume reduction",
        "ebitda": stress2_ebitda,
        "margin": stress2_margin,
        "impact_pct": stress2_impact,
    })
    
    # 3. Cost inflation
    stress3_clinical = clinical_y * (1 + stress_costs)
    stress3_costs = stress3_clinical + drugs_y + labs_y + admin_y + other_y
    stress3_ebitda = base_rev - stress3_costs
    stress3_margin = safe_divide(stress3_ebitda, base_rev)
    stress3_impact = safe_divide((stress3_ebitda - base_ebitda) * 100, base_ebitda, -100)
    scenarios.append({
        "name": "Clinical Cost Inflation",
        "description": f"{stress_costs*100:.0f}% clinical cost increase",
        "ebitda": stress3_ebitda,
        "margin": stress3_margin,
        "impact_pct": stress3_impact,
    })
    
    # 4. Combined stress
    stress4_rev = stress2_patients * ((1 - mix_low_pct) * tariff + mix_low_pct * low_tariff)
    stress4_var_costs = (drugs_y + labs_y) * 0.85
    stress4_costs = stress3_clinical + stress4_var_costs + admin_y + other_y
    stress4_ebitda = stress4_rev - stress4_costs
    stress4_margin = safe_divide(stress4_ebitda, stress4_rev)
    stress4_impact = safe_divide((stress4_ebitda - base_ebitda) * 100, base_ebitda, -100)
    scenarios.append({
        "name": "Combined Stress",
        "description": "All adverse conditions",
        "ebitda": stress4_ebitda,
        "margin": stress4_margin,
        "impact_pct": stress4_impact,
    })
    
    return scenarios, base_ebitda, base_margin

# =========================================================
# PART 3: SCENARIO BAR & KPI CARDS
# =========================================================
scenario_html = f"""
<div class="ct-scenario">
    <div class="scenario-item">
        <span class="scenario-label">Volume</span>
        <span class="scenario-value">{patients} pts/year</span>
    </div>
    <div class="scenario-item">
        <span class="scenario-label">Tariff</span>
        <span class="scenario-value">{format_currency(tariff)}</span>
    </div>
    <div class="scenario-item">
        <span class="scenario-label">Tax Rate</span>
        <span class="scenario-value">{int(tax_rate*100)}%</span>
    </div>
    <div class="scenario-item">
        <span class="scenario-label">Growth</span>
        <span class="scenario-value">{int(rev_growth*100)}%</span>
    </div>
    <div class="scenario-item">
        <span class="scenario-label">Discount Rate</span>
        <span class="scenario-value">{format_percentage(ke)}</span>
    </div>
    <div class="scenario-item">
        <span class="scenario-label">Initial Investment</span>
        <span class="scenario-value">{format_currency(initial_investment)}</span>
    </div>
</div>
"""
st.markdown(scenario_html, unsafe_allow_html=True)

# KPI CARDS – 4 in one row
kpi_html = f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-accent"></div>
        <div class="kpi-label">Annual Revenue</div>
        <div class="kpi-value">{format_currency(rev_y)}</div>
        <div class="kpi-meta">{patients} pts × {format_currency(tariff)}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-accent"></div>
        <div class="kpi-label">EBITDA</div>
        <div class="kpi-value">{format_currency(ebitda_y)}</div>
        <div class="kpi-meta">{format_percentage(ebitda_margin)} margin</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-accent"></div>
        <div class="kpi-label">Net Profit</div>
        <div class="kpi-value">{format_currency(net_y)}</div>
        <div class="kpi-meta">{format_percentage(net_margin)} after tax</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-accent"></div>
        <div class="kpi-label">Break-Even (pts)</div>
        <div class="kpi-value">{'N/A' if np.isnan(be_patients) else f'{be_patients:,.0f}'}</div>
        <div class="kpi-meta">{'N/A' if np.isnan(mos_pct) else f'{format_percentage(mos_pct)} safety'}</div>
    </div>
</div>
"""
st.markdown(kpi_html, unsafe_allow_html=True)

# =========================================================
# TABS - Main navigation
# =========================================================
tab_pl, tab_sens, tab_dash, tab_val, tab_analysis = st.tabs([
    "P&L Statement",
    "Sensitivity Analysis",
    "Visual Dashboard",
    "Valuation Model",
    "Strategic Analysis"
])

# =========================================================
# TAB 1: P&L STATEMENT  (solo P&L y análisis de P&L)
# =========================================================
with tab_pl:
    st.markdown(
        '<div class="section-header"><h2 class="section-title">Operating Profit & Loss Statement</h2></div>',
        unsafe_allow_html=True
    )
    st.dataframe(pnl_df, use_container_width=True, hide_index=True)

    st.markdown(
        '<div class="section-header"><h2 class="section-title">P&L Waterfall Analysis</h2></div>',
        unsafe_allow_html=True
    )
    fig_wf = go.Figure(go.Waterfall(
        name="P&L Flow",
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "total", "relative", "relative", "total"],
        x=["Revenue", "Clinical Staff", "Drugs", "Labs", "Gross Profit", "Admin Staff", "Other OpEx", "EBITDA"],
        y=[rev_y, -clinical_y, -drugs_y, -labs_y, 0, -admin_y, -other_y, 0],
        increasing={"marker": {"color": PALETTE["chart"][0]}},
        decreasing={"marker": {"color": PALETTE["chart"][2]}},
        totals={"marker": {"color": PALETTE["chart"][1]}},
        connector={"line": {"color": PALETTE["border"], "width": 2}},
        textposition="outside",
        textfont=dict(size=11, color=PALETTE["text_primary"], family="Inter")
    ))
    apply_chart_layout(fig_wf, height=450)
    fig_wf.update_yaxes(title=f"Thousands {currency}")
    st.plotly_chart(fig_wf, use_container_width=True)

    # insight solo de P&L
    content_pl = (
        f"Revenue of <b>{format_currency(rev_y)}</b> flows through gross margin of "
        f"<b>{format_percentage(gross_margin)}</b> to EBITDA of <b>{format_currency(ebitda_y)}</b>.<br><br>"
        f"{interpret_margin(ebitda_margin, 'EBITDA')}<br><br>"
        f"{interpret_margin(net_margin, 'Net')}<br><br>"
        f"<b>Profitability cascade:</b> For every dollar of revenue, <b>{gross_margin*100:.1f}%</b> remains after direct costs, "
        f"<b>{ebitda_margin*100:.1f}%</b> after operating expenses, and <b>{net_margin*100:.1f}%</b> flows to bottom line.<br><br>"
        f"<b>Cost efficiency:</b> The business generates <b>{currency_symbol}{revenue_per_dollar_cost:.2f}</b> of revenue for every {currency_symbol}1 of total costs "
        f"{'(excellent efficiency)' if revenue_per_dollar_cost >= 1.5 else '(good efficiency)' if revenue_per_dollar_cost >= 1.3 else '(adequate efficiency)' if revenue_per_dollar_cost >= 1.2 else '(low efficiency - requires attention)'}."
    )
    st.markdown(create_insight_box("1", "P&L STRUCTURE ANALYSIS", content_pl), unsafe_allow_html=True)


# =========================================================
# TAB 2: SENSITIVITY ANALYSIS (CVP, Tornado, Break-even, 2D, Stress)
# =========================================================
with tab_sens:
    
    # =====================================================
    # SECTION 1: CVP FUNDAMENTALS (AUTOMATED, CORPORATE TONE)
    # =====================================================
    st.markdown(
        '<div class="section-header"><h2 class="section-title">Cost-Volume-Profit Analysis</h2></div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # 1. AUTOMATED CVP BUILD
    # -----------------------------------------------------
    # unit contribution per patient/year
    contrib_pp = max(tariff - var_pp_y, 0)

    # fixed costs = structure that does NOT depend on patient volume
    # (clinical staff + admin + other OpEx)
    fixed_y = max((clinical_y + admin_y + other_y), 0)

    # break-even in patients
    if contrib_pp > 0:
        be_patients = fixed_y / contrib_pp
        be_revenue = be_patients * tariff
    else:
        be_patients = np.nan
        be_revenue = np.nan

    # margin of safety vs planned volume
    if not np.isnan(be_patients) and patients > 0:
        mos_pat = max(patients - be_patients, 0)
        mos_pct = mos_pat / patients
    else:
        mos_pat = 0
        mos_pct = 0

    # fixed-cost share at current volume
    total_variable_at_plan = var_pp_y * patients
    fixed_share = safe_divide(fixed_y, fixed_y + total_variable_at_plan)

    if not np.isnan(be_patients):

        # ===== 4 KPI CARDS IN ONE ROW =====
        c1, c2, c3, c4 = st.columns(4)

        # -------------------------------------------------
        # CARD 1 – Unit Contribution
        # -------------------------------------------------
        with c1:
            st.markdown(
                f"""
                <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                            border-radius:1rem;padding:1.4rem;box-shadow:0 6px 20px rgba(15,23,42,0.06);
                            position:relative;overflow:hidden;min-height:210px;">
                    <div style="position:absolute;top:0;left:0;right:0;height:4px;
                                background:linear-gradient(90deg,{PALETTE['primary']},{PALETTE['secondary']});"></div>
                    <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.06em;
                                color:{PALETTE['text_tertiary']};font-weight:700;margin:.75rem 0 .45rem 0;">
                        Unit Contribution
                    </div>
                    <div style="font-size:2rem;font-weight:800;color:{PALETTE['text_primary']};line-height:1;">
                        {format_currency(contrib_pp)}
                    </div>
                    <div style="font-size:0.74rem;color:{PALETTE['text_secondary']};margin:.4rem 0 1.05rem 0;">
                        {format_percentage(safe_divide(contrib_pp, tariff))} of tariff
                    </div>
                    <div style="background:{PALETTE['surface_alt']};padding:.6rem .85rem;border-radius:10px;
                                font-size:0.7rem;color:{PALETTE['text_secondary']};line-height:1.45;">
                        Tariff: <b>{format_currency(tariff)}</b><br>
                        Variable cost: <b>{format_currency(var_pp_y)}</b><br>
                        <span style="color:{PALETTE['primary']};font-weight:600;">
                            → Contribution: {format_currency(contrib_pp)}
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # -------------------------------------------------
        # CARD 2 – Break-Even Volume
        # -------------------------------------------------
        with c2:
            st.markdown(
                f"""
                <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                            border-radius:1rem;padding:1.4rem;box-shadow:0 6px 20px rgba(15,23,42,0.06);
                            position:relative;overflow:hidden;min-height:210px;">
                    <div style="position:absolute;top:0;left:0;right:0;height:4px;
                                background:linear-gradient(90deg,{PALETTE['primary']},{PALETTE['secondary']});"></div>
                    <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.06em;
                                color:{PALETTE['text_tertiary']};font-weight:700;margin:.75rem 0 .45rem 0;">
                        Break-Even Volume
                    </div>
                    <div style="font-size:2rem;font-weight:800;color:{PALETTE['text_primary']};line-height:1;">
                        {be_patients:,.0f}
                    </div>
                    <div style="font-size:0.74rem;color:{PALETTE['text_secondary']};margin:.4rem 0 1.05rem 0;">
                        patients per year
                    </div>
                    <div style="background:{PALETTE['surface_alt']};padding:.6rem .85rem;border-radius:10px;
                                font-size:0.7rem;color:{PALETTE['text_secondary']};line-height:1.45;">
                        Fixed costs: <b>{format_currency(fixed_y)}</b><br>
                        Formula: <b>Fixed ÷ Contribution</b><br>
                        <span style="color:{PALETTE['primary']};font-weight:600;">
                            → BE revenue: {format_currency(be_revenue)}
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # -------------------------------------------------
        # CARD 3 – Margin of Safety
        # -------------------------------------------------
        with c3:
            safety_color = '#065f46' if mos_pct >= 0.40 else '#92400e' if mos_pct >= 0.25 else '#7f1d1d'
            safety_bg = 'rgba(16,185,129,.12)' if mos_pct >= 0.40 else 'rgba(245,158,11,.12)' if mos_pct >= 0.25 else 'rgba(239,68,68,.12)'
            safety_label = 'ROBUST BUFFER' if mos_pct >= 0.40 else 'MODERATE RISK' if mos_pct >= 0.25 else 'HIGH RISK'

            st.markdown(
                f"""
                <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                            border-radius:1rem;padding:1.4rem;box-shadow:0 6px 20px rgba(15,23,42,0.06);
                            position:relative;overflow:hidden;min-height:210px;">
                    <div style="position:absolute;top:0;left:0;right:0;height:4px;
                                background:linear-gradient(90deg,{PALETTE['primary']},{PALETTE['secondary']});"></div>
                    <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.06em;
                                color:{PALETTE['text_tertiary']};font-weight:700;margin:.75rem 0 .45rem 0;">
                        Margin of Safety
                    </div>
                    <div style="font-size:2rem;font-weight:800;color:{PALETTE['text_primary']};line-height:1;">
                        {format_percentage(mos_pct)}
                    </div>
                    <div style="font-size:0.74rem;color:{PALETTE['text_secondary']};margin:.4rem 0 1.05rem 0;">
                        {mos_pat:,.0f} patients buffer
                    </div>
                    <div style="background:{safety_bg};padding:.6rem .85rem;border-radius:10px;
                                font-size:0.7rem;line-height:1.45;">
                        <div style="color:{safety_color};font-weight:700;font-size:0.67rem;
                                    text-transform:uppercase;letter-spacing:0.04em;margin-bottom:0.35rem;">
                            {safety_label}
                        </div>
                        Up to <b style="color:{safety_color};">{format_percentage(mos_pct)}</b> of current volume
                        can be absorbed before break-even is reached.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # -------------------------------------------------
        # CARD 4 – Fixed-Cost Share
        # -------------------------------------------------
        with c4:
            st.markdown(
                f"""
                <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                            border-radius:1rem;padding:1.4rem;box-shadow:0 6px 20px rgba(15,23,42,0.06);
                            position:relative;overflow:hidden;min-height:210px;">
                    <div style="position:absolute;top:0;left:0;right:0;height:4px;
                                background:linear-gradient(90deg,{PALETTE['primary']},{PALETTE['secondary']});"></div>
                    <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.06em;
                                color:{PALETTE['text_tertiary']};font-weight:700;margin:.75rem 0 .45rem 0;">
                        Fixed-Cost Share
                    </div>
                    <div style="font-size:2rem;font-weight:800;color:{PALETTE['text_primary']};line-height:1;">
                        {format_percentage(fixed_share)}
                    </div>
                    <div style="font-size:0.74rem;color:{PALETTE['text_secondary']};margin:.4rem 0 1.05rem 0;">
                        of operating cost base
                    </div>
                    <div style="background:{PALETTE['surface_alt']};padding:.6rem .85rem;border-radius:10px;
                                font-size:0.7rem;color:{PALETTE['text_secondary']};line-height:1.45;">
                        Fixed: <b>{format_currency(fixed_y)}</b><br>
                        Variable @ {patients} pts: <b>{format_currency(total_variable_at_plan)}</b><br>
                        <span style="color:{PALETTE['primary']};font-weight:600;">
                            → Additional volume improves EBITDA directly
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # -----------------------------------------------------
        # 2. SINGLE, NON-REPETITIVE INTERPRETATION (NO “YOU”)
        # -----------------------------------------------------
        # choose headline by strength of CVP
        if contrib_pp > 0 and mos_pct >= 0.6:
            headline = "Scalable, low-risk CVP"
            tone = (
                "Current unit economics generate enough contribution to cover the fixed clinical and administrative "
                "structure, so incremental volume is largely accretive."
            )
        elif contrib_pp > 0 and mos_pct >= 0.35:
            headline = "Healthy CVP with acceptable buffer"
            tone = (
                "The model tolerates moderate fluctuations in patient volume, provided tariff conditions remain aligned "
                "with current contribution levels."
            )
        else:
            headline = "Tight CVP – volume and tariff must be defended"
            tone = (
                "A high fixed-cost base relative to contribution per patient leaves limited room for simultaneous volume "
                "contraction and tariff pressure."
            )

        cvp_content = (
            f"<b>{headline}</b><br>{tone}<br><br>"
            f"The break-even volume (<b>{be_patients:,.0f} patients</b>) results from dividing the current fixed-cost "
            f"structure (<b>{format_currency(fixed_y)}</b>) by the effective contribution per patient "
            f"(<b>{format_currency(contrib_pp)}</b>). At the present operating level "
            f"(<b>{patients} patients</b>), the model maintains a volume margin of safety of "
            f"<b>{mos_pat:,.0f} patients</b> ({format_percentage(mos_pct)})."
        )

        st.markdown(
            create_insight_box("1", "CVP STRATEGIC ANALYSIS", cvp_content),
            unsafe_allow_html=True
        )

    else:
        st.warning("⚠️ Break-even analysis unavailable with current parameters. Check tariff and variable cost.")
    
    # =====================================================
    # SECCIÓN 2: TORNADO ANALYSIS
    # =====================================================
    st.markdown(
        '<div class="section-header"><h2 class="section-title">Tornado Sensitivity Analysis</h2></div>',
        unsafe_allow_html=True
    )
    
    st.markdown(
        f"""
        <div style="background:{PALETTE['surface_alt']};padding:1rem 1.2rem;border-radius:12px;
                    margin-bottom:1.5rem;font-size:0.78rem;color:{PALETTE['text_secondary']};
                    border-left:5px solid {PALETTE['primary']};line-height:1.6;">
            <b style="color:{PALETTE['text_primary']};font-size:0.8rem;">Univariate Sensitivity Analysis</b><br>
            Shows EBITDA impact when each variable changes ±20% independently. 
            Identifies which drivers have the most leverage on profitability.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Calcular sensibilidades
    tornado_data = []
    base_ebitda_tornado = ebitda_y
    
    sensitivity_vars = [
        ("Volume (patients)", patients, 
         lambda x: (x * tariff) - (clinical_y + (drugs_y + labs_y) * x / patients + admin_y + other_y)),
        ("Tariff", tariff, 
         lambda x: (patients * x) - (clinical_y + drugs_y + labs_y + admin_y + other_y)),
        ("Clinical costs", clinical_y, 
         lambda x: rev_y - (x + drugs_y + labs_y + admin_y + other_y)),
        ("Drug costs", drugs_y, 
         lambda x: rev_y - (clinical_y + x + labs_y + admin_y + other_y)),
        ("Lab costs", labs_y, 
         lambda x: rev_y - (clinical_y + drugs_y + x + admin_y + other_y)),
        ("Admin costs", admin_y, 
         lambda x: rev_y - (clinical_y + drugs_y + labs_y + x + other_y)),
        ("Other OpEx", other_y, 
         lambda x: rev_y - (clinical_y + drugs_y + labs_y + admin_y + x)),
    ]
    
    for var_name, base_val, calc_func in sensitivity_vars:
        if base_val == 0:
            continue
        
        low_val = base_val * 0.8
        ebitda_low = calc_func(low_val)
        delta_low = ebitda_low - base_ebitda_tornado
        
        high_val = base_val * 1.2
        ebitda_high = calc_func(high_val)
        delta_high = ebitda_high - base_ebitda_tornado
        
        total_swing = abs(delta_high - delta_low)
        
        tornado_data.append({
            "variable": var_name,
            "delta_low": delta_low,
            "delta_high": delta_high,
            "swing": total_swing
        })
    
    # ordenar de mayor a menor impacto (forma de tornado)
    tornado_data.sort(key=lambda x: x["swing"], reverse=True)
    
    # Crear gráfico tornado mejorado (SOLO AZULES)
    fig_tornado = go.Figure()
    
    y_labels = [item["variable"] for item in tornado_data]
    
    fig_tornado.add_trace(go.Bar(
        y=y_labels,
        x=[item["delta_low"] for item in tornado_data],
        orientation='h',
        name='-20%',
        marker=dict(
            color=PALETTE["chart"][0],
            line=dict(width=2, color="white")
        ),
        text=[f"{item['delta_low']:+.0f}k" for item in tornado_data],
        textposition='inside',
        textfont=dict(color="white", size=11, family="Inter", weight="bold"),
        hovertemplate="<b>%{y}</b><br>-20% impact: %{x:+,.0f}k<extra></extra>"
    ))
    
    fig_tornado.add_trace(go.Bar(
        y=y_labels,
        x=[item["delta_high"] for item in tornado_data],
        orientation='h',
        name='+20%',
        marker=dict(
            color=PALETTE["chart"][2],
            line=dict(width=2, color="white")
        ),
        text=[f"{item['delta_high']:+.0f}k" for item in tornado_data],
        textposition='inside',
        textfont=dict(color="white", size=11, family="Inter", weight="bold"),
        hovertemplate="<b>%{y}</b><br>+20% impact: %{x:+,.0f}k<extra></extra>"
    ))
    
    fig_tornado.add_vline(
        x=0,
        line_dash="solid",
        line_color=PALETTE["text_primary"],
        line_width=3,
        annotation_text="Base Case",
        annotation_position="top",
        annotation_font=dict(size=12, color=PALETTE["text_primary"], family="Inter", weight="bold")
    )
    
    apply_chart_layout(fig_tornado, height=480)
    fig_tornado.update_layout(
        barmode='overlay',
        xaxis_title=f"EBITDA Impact ({currency_label})",
        yaxis_title="",
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=11, color=PALETTE["text_primary"])
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=PALETTE["border"],
            borderwidth=1
        )
    )
    
    st.plotly_chart(fig_tornado, use_container_width=True)
    
    most_sensitive = tornado_data[0]
    least_sensitive = tornado_data[-1]
    
    tornado_content = (
        f"<b>Primary value driver:</b> <b>{most_sensitive['variable']}</b> — "
        f"total swing of <b>{format_currency(most_sensitive['swing'])}</b> across ±20% variation.<br><br>"
        f"<b>Downside (-20%):</b> {format_currency(abs(most_sensitive['delta_low']))} EBITDA reduction.<br>"
        f"<b>Upside (+20%):</b> {format_currency(most_sensitive['delta_high'])} EBITDA increase.<br><br>"
        f"<b>Least sensitive:</b> {least_sensitive['variable']} ({format_currency(least_sensitive['swing'])})."
    )
    
    st.markdown(
        create_insight_box("2", "TORNADO ANALYSIS INTERPRETATION", tornado_content),
        unsafe_allow_html=True
    )

    # =====================================================
    # 3. BREAK-EVEN FRONTIER (Volume × Tariff) – FULL CURVE
    # =====================================================
    st.markdown(
        '<div class="section-header"><h2 class="section-title">Break-Even Frontier (Volume × Tariff)</h2></div>',
        unsafe_allow_html=True
    )

    # parámetros base (ya existen arriba en la app)
    fixed_costs_y = fixed_y            # kUSD/year – fixed staff, admin, overhead
    var_cost_pp_y = var_pp_y           # kUSD/patient/year – drugs+labs+variable clínico

    # rango automático de volumen para dibujar TODA la curva
    min_vol = 30
    max_vol = max(int(patients * 1.6), 400)
    be_x = np.linspace(min_vol, max_vol, 160)

    # curva teórica de equilibrio: tarifa(p) = (CF + CV * p) / p
    be_y = (fixed_costs_y + var_cost_pp_y * be_x) / be_x

    # métricas derivadas para la interpretación
    # break-even al TARIF actual (ya lo tenías como be_patients)
    be_vol_at_current_tariff = be_patients
    # tarifa mínima al VOLUMEN actual
    be_tariff_at_current_vol = (fixed_costs_y + var_cost_pp_y * patients) / patients
    # buffer de volumen
    vol_buffer = max(patients - be_vol_at_current_tariff, 0)
    vol_buffer_pct = vol_buffer / patients if patients > 0 else 0
    # holgura de tarifa
    tariff_headroom = max(tariff - be_tariff_at_current_vol, 0)
    tariff_headroom_pct = tariff_headroom / tariff if tariff > 0 else 0

    fig_be = go.Figure()

    # zona rentable (por debajo de la curva)
    fig_be.add_trace(go.Scatter(
        x=np.concatenate([be_x, [be_x.max(), be_x.min()]]),
        y=np.concatenate([be_y, [be_y.min() * 0.9, be_y.min() * 0.9]]),
        fill='toself',
        fillcolor='rgba(37, 99, 235, 0.04)',
        line=dict(width=0),
        name="Profitable zone",
        hoverinfo="skip"
    ))

    # curva de break-even completa
    fig_be.add_trace(go.Scatter(
        x=be_x,
        y=be_y,
        mode="lines",
        name="Break-even curve",
        line=dict(color=PALETTE["chart"][0], width=4),
        hovertemplate=f"<b>Break-even</b><br>Patients: %{{x:.0f}}<br>Tariff: {currency_symbol}%{{y:.1f}}k<extra></extra>"
    ))

    # punto operativo actual
    fig_be.add_trace(go.Scatter(
        x=[patients],
        y=[tariff],
        mode="markers+text",
        name="Current position",
        marker=dict(
            size=12,
            color="white",
            line=dict(width=3, color=PALETTE["primary"])
        ),
        text=["Current"],
        textposition="middle right",
        textfont=dict(size=11, color=PALETTE["text_primary"]),
        hovertemplate=(
            f"<b>Current position</b><br>"
            f"Patients: {patients}<br>"
            f"Tariff: {format_currency(tariff)}<extra></extra>"
        )
    ))

    # layout
    apply_chart_layout(fig_be, height=420)
    fig_be.update_layout(
        xaxis_title="Patients per year",
        yaxis_title=f"Tariff ({currency_label}/patient/year)",
        xaxis=dict(
            range=[min_vol, max_vol],
            tickmode="auto",
            nticks=8,
        ),
        yaxis=dict(
            range=[max(0, be_y.min() * 0.85), max(tariff, be_y.max()) * 1.05],
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=PALETTE["border"],
            borderwidth=1
        )
    )

    st.plotly_chart(fig_be, use_container_width=True)

    # interpretación 100% automática
    be_text = (
        f"Frontier derived from a fixed-cost base of <b>{format_currency(fixed_costs_y)}</b> and an effective "
        f"variable cost per patient of <b>{format_currency(var_cost_pp_y)}</b>."
        f"<br><br>At the current operating point (<b>{patients} patients</b> at <b>{format_currency(tariff)}</b>), "
        f"the model breaks even at <b>{be_vol_at_current_tariff:.0f} patients</b>, which implies a volume buffer of "
        f"<b>{vol_buffer:.0f} patients</b> ({format_percentage(vol_buffer_pct)} of present volume). "
        f"The minimum sustainable tariff at the current volume is <b>{format_currency(be_tariff_at_current_vol)}</b>, "
        f"so the present tariff includes a pricing headroom of <b>{format_percentage(tariff_headroom_pct)}</b>."
    )
    st.markdown(
        create_insight_box(
            "3",
            "BREAK-EVEN FRONTIER – AUTOMATED INTERPRETATION",
            be_text
        ),
        unsafe_allow_html=True
    )


    # =====================================================
    # 4. 2D SENSITIVITY MATRIX (same BE curve on top)
    # =====================================================
    st.markdown(
        '<div class="section-header"><h2 class="section-title">2D Sensitivity: Patients × Tariff → EBITDA</h2></div>',
        unsafe_allow_html=True
    )

    # rangos centrados en el punto actual, coherentes con la curva anterior
    pts_min = max(30, int(patients * 0.55))
    pts_max = int(patients * 1.45)
    pts_step = max(1, (pts_max - pts_min) // 14)
    pts_range = np.arange(pts_min, pts_max + 1, pts_step)
    # asegurar que el volumen actual esté en el eje
    if patients not in pts_range:
        pts_range = np.sort(np.append(pts_range, patients))

    tariff_min = max(10, round(tariff * 0.65, 1))
    tariff_max = round(tariff * 1.35, 1)
    tariff_step = max(0.5, (tariff_max - tariff_min) / 14)
    tariff_range = np.round(np.arange(tariff_min, tariff_max + 0.001, tariff_step), 1)

    # grid EBITDA
    ebitda_grid = np.zeros((len(tariff_range), len(pts_range)))
    for i, t in enumerate(tariff_range):
        for j, p in enumerate(pts_range):
            rev_tmp   = p * t
            drugs_tmp = (drugs_base * 12 * (1 + drugs_cont)) * p
            labs_tmp  = (labs_base  * 12 * (1 + labs_cont))  * p
            ebitda_tmp = rev_tmp - clinical_y - drugs_tmp - labs_tmp - admin_y - other_y
            ebitda_grid[i, j] = ebitda_tmp

    # % de celdas rentables para la interpretación
    profitable_cells = np.sum(ebitda_grid >= 0)
    total_cells = ebitda_grid.size
    profitable_share = profitable_cells / total_cells if total_cells > 0 else 0

    fig_2d = go.Figure(
        data=go.Heatmap(
            z=ebitda_grid,
            x=pts_range,
            y=tariff_range,
            colorscale=[
                [0.00, "#E2E8F0"],
                [0.48, "#CBD5F5"],
                [0.50, "#FFFFFF"],           # break-even
                [0.80, PALETTE["chart"][1]],
                [1.00, PALETTE["chart"][2]],
            ],
            zmid=0,
            showscale=True,
            colorbar=dict(
                title=f"EBITDA ({currency_label})",
                len=0.65,
                thickness=14
            ),
            hovertemplate=f"<b>Scenario</b><br>Patients: %{{x}}<br>Tariff: {currency_symbol}%{{y}}k<br>EBITDA: %{{z:,.0f}}k<extra></extra>"
        )
    )

    # misma curva, pero acotada al rango mostrado
    be_x_local = np.linspace(pts_range.min(), pts_range.max(), 140)
    be_y_local = (fixed_costs_y + var_cost_pp_y * be_x_local) / be_x_local
    mask = (be_y_local >= tariff_min) & (be_y_local <= tariff_max)
    be_x_local = be_x_local[mask]
    be_y_local = be_y_local[mask]

    fig_2d.add_trace(go.Scatter(
        x=be_x_local,
        y=be_y_local,
        mode="lines",
        name="Break-even line",
        line=dict(color=PALETTE["primary"], width=3),
        hovertemplate=f"<b>Break-even</b><br>Patients: %{{x:.0f}}<br>Tariff: {currency_symbol}%{{y:.1f}}k<extra></extra>"
    ))

    # punto actual
    fig_2d.add_trace(go.Scatter(
        x=[patients],
        y=[tariff],
        mode="markers+text",
        marker=dict(
            size=12,
            color="white",
            line=dict(width=3, color=PALETTE["primary"])
        ),
        text=["Current"],
        textposition="middle right",
        textfont=dict(size=11, color=PALETTE["text_primary"]),
        name="Current position",
        hovertemplate=(
            f"<b>Current</b><br>"
            f"Patients: {patients}<br>"
            f"Tariff: {format_currency(tariff)}<br>"
            f"EBITDA: {format_currency(ebitda_y)}<extra></extra>"
        )
    ))

    apply_chart_layout(fig_2d, height=430)
    fig_2d.update_layout(
        xaxis_title="Patients per year",
        yaxis_title=f"Tariff ({currency_label}/patient/year)",
        xaxis=dict(
            tickmode="auto",
            nticks=8,
        ),
        yaxis=dict(
            tickmode="auto",
            nticks=7,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=PALETTE["border"],
            borderwidth=1
        )
    )

    st.plotly_chart(fig_2d, use_container_width=True)

    # interpretación 100% automática de la matriz
    matrix_text = (
        f"Matrix built for volumes between <b>{pts_range.min()}</b> and <b>{pts_range.max()}</b> patients/year "
        f"and tariffs between <b>{tariff_min:.1f}k</b> and <b>{tariff_max:.1f}k</b>. "
        f"{format_percentage(profitable_share)} of simulated combinations remain at EBITDA ≥ 0 with the current fixed-cost base. "
        f"The operating point ({patients} pts, {format_currency(tariff)}) stays on the profitable side of the same break-even line used in the frontier."
    )
    st.markdown(
        create_insight_box(
            "4",
            "2D SENSITIVITY – AUTOMATED INTERPRETATION",
            matrix_text
        ),
        unsafe_allow_html=True
    )
    
    # =====================================================
    # SECTION 5: DOWNSIDE STRESS TESTING
    # =====================================================
    st.markdown(
        '<div class="section-header"><h2 class="section-title">Downside Stress Testing</h2></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="background:{PALETTE['surface_alt']};padding:0.8rem 1rem;border-radius:10px;
                    margin-bottom:1.2rem;font-size:0.75rem;color:{PALETTE['text_secondary']};
                    border-left:4px solid {PALETTE['primary']};">
            <b>Stress methodology:</b> Multi-factor stress framework evaluating EBITDA resilience under isolated and 
            combined adverse scenarios. Stress parameters calibrated to historical volatility and market conditions.
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # GENERATE SCENARIOS
    # -----------------------------------------------------
    scenarios, base_ebitda_stress, base_margin_stress = generate_stress_scenarios(
        patients, tariff, mix_low_pct, low_tariff,
        clinical_y, drugs_y, labs_y, admin_y, other_y, stress_costs
    )

    stress_df = pd.DataFrame(scenarios)

    # Extract parameters
    base_volume = patients
    base_tariff = tariff
    volume_drop_pct = 0.15
    stressed_volume = int(round(base_volume * (1 - volume_drop_pct), 0))
    payer_shift_pct = float(mix_low_pct) if mix_low_pct is not None else 0.0
    low_tariff_val = float(low_tariff) if low_tariff is not None else base_tariff * 0.7

    if isinstance(stress_costs, dict) and "clinical" in stress_costs:
        clinical_infl_pct = float(stress_costs["clinical"])
    else:
        clinical_infl_pct = 0.10

    # -----------------------------------------------------
    # STRESS PARAMETERS - COMPACT
    # -----------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                        border-radius:1rem;padding:1rem;text-align:center;
                        box-shadow:0 4px 12px rgba(15,23,42,0.04);">
                <div style="font-size:0.65rem;text-transform:uppercase;color:{PALETTE['text_tertiary']};
                            letter-spacing:0.05em;margin-bottom:0.5rem;font-weight:600;">Baseline</div>
                <div style="font-size:1.3rem;font-weight:800;color:{PALETTE['primary']};line-height:1;">
                    {base_volume}
                </div>
                <div style="font-size:0.7rem;color:{PALETTE['text_secondary']};margin-top:0.3rem;">
                    patients @ {format_currency(base_tariff)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                        border-radius:1rem;padding:1rem;text-align:center;
                        box-shadow:0 4px 12px rgba(15,23,42,0.04);">
                <div style="font-size:0.65rem;text-transform:uppercase;color:{PALETTE['text_tertiary']};
                            letter-spacing:0.05em;margin-bottom:0.5rem;font-weight:600;">Volume Shock</div>
                <div style="font-size:1.3rem;font-weight:800;color:{PALETTE['chart'][0]};line-height:1;">
                    -{int(volume_drop_pct*100)}%
                </div>
                <div style="font-size:0.7rem;color:{PALETTE['text_secondary']};margin-top:0.3rem;">
                    → {stressed_volume} patients
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                        border-radius:1rem;padding:1rem;text-align:center;
                        box-shadow:0 4px 12px rgba(15,23,42,0.04);">
                <div style="font-size:0.65rem;text-transform:uppercase;color:{PALETTE['text_tertiary']};
                            letter-spacing:0.05em;margin-bottom:0.5rem;font-weight:600;">Payer Shift</div>
                <div style="font-size:1.3rem;font-weight:800;color:{PALETTE['chart'][0]};line-height:1;">
                    {int(payer_shift_pct*100)}%
                </div>
                <div style="font-size:0.7rem;color:{PALETTE['text_secondary']};margin-top:0.3rem;">
                    to {format_currency(low_tariff_val)} tier
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                        border-radius:1rem;padding:1rem;text-align:center;
                        box-shadow:0 4px 12px rgba(15,23,42,0.04);">
                <div style="font-size:0.65rem;text-transform:uppercase;color:{PALETTE['text_tertiary']};
                            letter-spacing:0.05em;margin-bottom:0.5rem;font-weight:600;">Cost Inflation</div>
                <div style="font-size:1.3rem;font-weight:800;color:{PALETTE['chart'][0]};line-height:1;">
                    +{int(clinical_infl_pct*100)}%
                </div>
                <div style="font-size:0.7rem;color:{PALETTE['text_secondary']};margin-top:0.3rem;">
                    clinical cost base
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # RESULTS TABLE - WITH STATUS COLUMN
    # -----------------------------------------------------
    display_rows = [{
        "Scenario": "Baseline",
        "EBITDA": format_currency(base_ebitda_stress),
        "Margin": format_percentage(base_margin_stress),
        "Δ EBITDA": "—",
        "Δ%": "—",
        "Status": "✓ Profitable" if base_ebitda_stress > 0 else "✗ Unprofitable"
    }]

    for _, r in stress_df.iterrows():
        status = "✓ Profitable" if r["ebitda"] > 0 else "✗ Unprofitable"
        display_rows.append({
            "Scenario": r["name"],
            "EBITDA": format_currency(r["ebitda"]),
            "Margin": format_percentage(r["margin"]),
            "Δ EBITDA": format_currency(r['ebitda'] - base_ebitda_stress),
            "Δ%": f"{r['impact_pct']:+.1f}%",
            "Status": status
        })

    st.dataframe(
        pd.DataFrame(display_rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn(
                "Status",
                help="Profitability status: whether EBITDA remains positive under this scenario"
            )
        }
    )

    # -----------------------------------------------------
    # VISUAL - BLUE GRADIENT
    # -----------------------------------------------------
    fig_stress = go.Figure()

    x_labels = ["Baseline"] + stress_df["name"].tolist()
    y_values = [base_ebitda_stress] + stress_df["ebitda"].tolist()

    # Blue gradient by severity
    bar_colors = [PALETTE["chart"][3]]
    for e in stress_df["ebitda"]:
        if base_ebitda_stress > 0:
            retention = e / base_ebitda_stress
        else:
            retention = 0
        
        if retention >= 0.9:
            bar_colors.append("#60A5FA")
        elif retention >= 0.7:
            bar_colors.append("#3B82F6")
        elif retention >= 0.5:
            bar_colors.append("#2563EB")
        elif retention >= 0 :
            bar_colors.append("#1E40AF")
        else:
            bar_colors.append("#0F3F72")

    fig_stress.add_bar(
        x=x_labels,
        y=y_values,
        marker=dict(color=bar_colors, line=dict(width=2, color="white")),
        text=[format_currency(v) for v in y_values],
        textposition="outside",
        textfont=dict(size=11, family="Inter", weight="bold"),
        hovertemplate="<b>%{x}</b><br>EBITDA: %{y:,.0f}k<extra></extra>",
        showlegend=False
    )

    fig_stress.add_hline(
        y=0, line_dash="solid", line_color=PALETTE["chart"][0], line_width=2,
        annotation_text="Break-Even", annotation_position="right"
    )

    apply_chart_layout(fig_stress, height=440)
    fig_stress.update_yaxes(title=f"EBITDA (Thousands {currency})")
    fig_stress.update_xaxes(tickangle=-15)

    st.plotly_chart(fig_stress, use_container_width=True)

    # -----------------------------------------------------
    # AUTOMATED ANALYSIS
    # -----------------------------------------------------

    def _find_scenario(df, keyword: str):
        if df.empty or "name" not in df.columns:
            return None
        sub = df[df["name"].str.lower().str.contains(keyword.lower(), na=False)]
        return sub.iloc[0].to_dict() if not sub.empty else None

    # Find scenarios
    sc_vol = _find_scenario(stress_df, "volume")
    sc_mix = _find_scenario(stress_df, "mix")
    sc_cost = _find_scenario(stress_df, "cost")
    sc_comb = _find_scenario(stress_df, "combined")
    if sc_comb is None:
        sc_comb = _find_scenario(stress_df, "worst")

    # Calculate metrics
    min_ebitda = stress_df["ebitda"].min() if not stress_df.empty else base_ebitda_stress
    worst_ebitda = sc_comb["ebitda"] if sc_comb else min_ebitda
    max_drawdown = base_ebitda_stress - min_ebitda
    drawdown_pct = safe_divide(max_drawdown, base_ebitda_stress)

    # Resilience score (0-100)
    # 100 = no impact, 0 = complete EBITDA loss
    if base_ebitda_stress > 0:
        resilience_score = max(0, min(100, safe_divide(worst_ebitda, base_ebitda_stress) * 100))
    else:
        resilience_score = 0

    # Risk factors
    impacts = []
    if sc_mix: impacts.append(("Payer Mix", abs(sc_mix["impact_pct"]), sc_mix))
    if sc_vol: impacts.append(("Volume", abs(sc_vol["impact_pct"]), sc_vol))
    if sc_cost: impacts.append(("Cost", abs(sc_cost["impact_pct"]), sc_cost))
    impacts.sort(key=lambda x: x[1], reverse=True)

    # Primary risk
    if impacts:
        primary_label, primary_impact, primary_sc = impacts[0]
    else:
        primary_label, primary_impact = "N/A", 0

    # Resilience classification
    if resilience_score >= 75:
        res_tag = '<span class="insight-tag positive">ROBUST</span>'
        res_txt = "Business retains >75% of baseline EBITDA under combined stress."
    elif resilience_score >= 50:
        res_tag = '<span class="insight-tag">ADEQUATE</span>'
        res_txt = "Business retains 50-75% of baseline EBITDA under combined stress."
    elif worst_ebitda >= 0:
        res_tag = '<span class="insight-tag">LIMITED</span>'
        res_txt = "Business remains profitable but retains <50% of baseline EBITDA."
    else:
        res_tag = '<span class="insight-tag">FRAGILE</span>'
        res_txt = "Combined stress pushes EBITDA below zero (unprofitable)."

    # Mitigation action
    if primary_label == "Payer Mix":
        action = "Implement tiered contract strategy with minimum reimbursement floors and quarterly payer mix rebalancing."
    elif primary_label == "Volume":
        action = "Establish systematic referral network development and patient retention programs targeting high-risk cohorts."
    elif primary_label == "Cost":
        action = "Negotiate multi-year supply contracts and improve clinical productivity through process optimization."
    else:
        action = "Deploy integrated risk management framework with real-time monitoring and quarterly stress testing."

    # -----------------------------------------------------
    # INSIGHT BOX - CLEAN, VISUAL, NO COMPLEX HTML
    # -----------------------------------------------------

    # Calculate summary stats
    profitable_scenarios = sum(1 for _, r in stress_df.iterrows() if r["ebitda"] > 0)
    total_scenarios = len(stress_df)
    survival_rate = safe_divide(profitable_scenarios, total_scenarios)

    # 3 KPI CARDS usando columnas de Streamlit
    st.markdown(
        f'<div style="font-size:0.85rem;font-weight:600;color:{PALETTE["text_primary"]};margin:1rem 0 0.8rem 0;">Key Metrics</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                        border-radius:0.8rem;padding:1rem;text-align:center;">
                <div style="font-size:0.65rem;text-transform:uppercase;color:{PALETTE['text_tertiary']};
                            letter-spacing:0.05em;margin-bottom:0.4rem;">Resilience Score</div>
                <div style="font-size:2rem;font-weight:800;color:{PALETTE['primary']};line-height:1;">
                    {resilience_score:.0f}<span style="font-size:1.2rem;color:{PALETTE['text_secondary']};">/100</span>
                </div>
                <div style="font-size:0.7rem;color:{PALETTE['text_secondary']};margin-top:0.3rem;">
                    Retains {resilience_score:.0f}% of base EBITDA
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                        border-radius:0.8rem;padding:1rem;text-align:center;">
                <div style="font-size:0.65rem;text-transform:uppercase;color:{PALETTE['text_tertiary']};
                            letter-spacing:0.05em;margin-bottom:0.4rem;">Max Drawdown</div>
                <div style="font-size:2rem;font-weight:800;color:{PALETTE['chart'][0]};line-height:1;">
                    {format_percentage(drawdown_pct)}
                </div>
                <div style="font-size:0.7rem;color:{PALETTE['text_secondary']};margin-top:0.3rem;">
                    {format_currency(max_drawdown)} worst-case loss
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                        border-radius:0.8rem;padding:1rem;text-align:center;">
                <div style="font-size:0.65rem;text-transform:uppercase;color:{PALETTE['text_tertiary']};
                            letter-spacing:0.05em;margin-bottom:0.4rem;">Scenario Survival</div>
                <div style="font-size:2rem;font-weight:800;color:{PALETTE['primary']};line-height:1;">
                    {profitable_scenarios}/{total_scenarios}
                </div>
                <div style="font-size:0.7rem;color:{PALETTE['text_secondary']};margin-top:0.3rem;">
                    {format_percentage(survival_rate)} remain profitable
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ASSESSMENT BOX
    assessment_box = f"""
    <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                border-radius:1rem;padding:1.2rem;margin-bottom:1rem;">
        <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:0.8rem;">
            <div style="font-size:0.7rem;text-transform:uppercase;color:{PALETTE['text_tertiary']};
                        letter-spacing:0.05em;font-weight:700;">Assessment</div>
            {res_tag}
        </div>
        <div style="font-size:0.8rem;color:{PALETTE['text_primary']};line-height:1.6;">
            {res_txt}
        </div>
    </div>
    """
    st.markdown(assessment_box, unsafe_allow_html=True)

    # PRIMARY RISK BOX
    risk_box = f"""
    <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                border-radius:1rem;padding:1.2rem;margin-bottom:1rem;">
        <div style="font-size:0.7rem;text-transform:uppercase;color:{PALETTE['text_tertiary']};
                    letter-spacing:0.05em;font-weight:700;margin-bottom:0.8rem;">Primary Risk Factor</div>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;">
            <div style="font-size:1.1rem;font-weight:700;color:{PALETTE['text_primary']};">
                {primary_label}
            </div>
            <div style="font-size:1.1rem;font-weight:700;color:{PALETTE['chart'][0]};">
                {primary_impact:.1f}% impact
            </div>
        </div>
        <div style="font-size:0.75rem;color:{PALETTE['text_secondary']};line-height:1.5;">
            {action}
        </div>
    </div>
    """
    st.markdown(risk_box, unsafe_allow_html=True)

    # RISK RANKING
    if len(impacts) > 1:
        st.markdown(
            f"""
            <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                        border-radius:1rem;padding:1.2rem;">
                <div style="font-size:0.7rem;text-transform:uppercase;color:{PALETTE['text_tertiary']};
                            letter-spacing:0.05em;font-weight:700;margin-bottom:0.8rem;">Risk Ranking</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        for i, (label, impact, sc) in enumerate(impacts, 1):
            status_color = PALETTE["success"] if sc["ebitda"] > 0 else PALETTE["danger"]
            status_icon = "✓" if sc["ebitda"] > 0 else "✗"
            bar_width = (impact / impacts[0][1]) * 100
            
            rank_html = f"""
            <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                        border-radius:0.8rem;padding:0.8rem 1rem;margin-bottom:0.5rem;">
                <div style="display:flex;align-items:center;gap:0.8rem;">
                    <div style="font-size:0.75rem;font-weight:700;color:{PALETTE['text_primary']};
                                min-width:80px;">{label}</div>
                    <div style="flex:1;background:{PALETTE['surface_alt']};border-radius:999px;height:8px;
                                position:relative;overflow:hidden;">
                        <div style="position:absolute;left:0;top:0;bottom:0;width:{bar_width}%;
                                    background:{PALETTE['chart'][0]};border-radius:999px;"></div>
                    </div>
                    <div style="font-size:0.75rem;font-weight:600;color:{PALETTE['chart'][0]};
                                min-width:60px;text-align:right;">{impact:.1f}%</div>
                    <div style="font-size:0.9rem;color:{status_color};min-width:20px;">{status_icon}</div>
                </div>
            </div>
            """
            st.markdown(rank_html, unsafe_allow_html=True)
    
# =========================================================
# TAB 3: VISUAL DASHBOARD  (solo gráficos)
# =========================================================
with tab_dash:
    st.markdown(
        '<div class="section-header"><h2 class="section-title">Cost Structure Breakdown</h2></div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        cost_labels = ["Clinical", "Drugs", "Labs", "Admin", "Other OpEx"]
        cost_values = [clinical_y, drugs_y, labs_y, admin_y, other_y]
        fig_cost = go.Figure(data=[go.Pie(
            labels=cost_labels,
            values=cost_values,
            hole=0.5,
            marker=dict(colors=PALETTE["chart"][:5], line=dict(color="white", width=3)),
            textposition='outside',
            textinfo='label+percent',
            textfont=dict(size=12, family="Inter", color=PALETTE["text_primary"])
        )])
        apply_chart_layout(fig_cost, height=400)
        fig_cost.update_layout(showlegend=False)
        st.plotly_chart(fig_cost, use_container_width=True)

    with col2:
        fig_fixed_var = go.Figure(data=[
            go.Bar(
                name="Fixed Costs",
                x=["Cost Structure"],
                y=[fixed_y],
                marker=dict(color=PALETTE["chart"][0], line=dict(width=2, color="white")),
                text=[f"{format_currency(fixed_y)} ({format_percentage(fixed_ratio)})"],
                textposition="inside",
                textfont=dict(size=12, color="white")
            ),
            go.Bar(
                name="Variable Costs",
                x=["Cost Structure"],
                y=[drugs_y + labs_y],
                marker=dict(color=PALETTE["chart"][1], line=dict(width=2, color="white")),
                text=[f"{format_currency(drugs_y + labs_y)} ({format_percentage(var_ratio)})"],
                textposition="inside",
                textfont=dict(size=12, color="white")
            )
        ])
        apply_chart_layout(fig_fixed_var, height=400)
        fig_fixed_var.update_layout(barmode="stack", yaxis_title=f"Annual Costs ({currency_label})")
        st.plotly_chart(fig_fixed_var, use_container_width=True)

    st.markdown(create_insight_box("1", "COST STRUCTURE ANALYSIS", interpret_cost_structure(fixed_ratio, var_ratio, clinical_y, admin_y)), unsafe_allow_html=True)

    st.markdown(
        '<div class="section-header"><h2 class="section-title">Revenue & Profitability</h2></div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        metrics = ["Revenue", "EBITDA", "Net Profit"]
        values = [rev_y, ebitda_y, net_y]
        fig_rev = go.Figure()
        fig_rev.add_bar(
            x=metrics,
            y=values,
            marker=dict(color=PALETTE["chart"][:3], line=dict(width=2, color="white")),
            text=[format_currency(v) for v in values],
            textposition='outside'
        )
        apply_chart_layout(fig_rev, height=400)
        fig_rev.update_yaxes(title=f"Thousands {currency}")
        fig_rev.update_layout(showlegend=False)
        st.plotly_chart(fig_rev, use_container_width=True)

    with col2:
        fig_margins = go.Figure(data=[go.Bar(
            x=["Gross", "EBITDA", "Net"],
            y=[gross_margin * 100, ebitda_margin * 100, net_margin * 100],
            marker=dict(color=PALETTE["chart"][:3], line=dict(width=2, color="white")),
            text=[f"{v*100:.1f}%" for v in [gross_margin, ebitda_margin, net_margin]],
            textposition='outside'
        )])
        apply_chart_layout(fig_margins, height=400)
        fig_margins.update_yaxes(title="Margin %")
        fig_margins.update_layout(showlegend=False)
        st.plotly_chart(fig_margins, use_container_width=True)

    st.markdown(create_insight_box("2", "PROFITABILITY ANALYSIS", 
        f"<b>Revenue generation:</b> {format_currency(rev_y)} from {patients} patients at {format_currency(tariff)} average tariff.<br><br>"
        f"{interpret_margin(gross_margin, 'Gross')}<br><br>"
        f"{interpret_margin(ebitda_margin, 'EBITDA')}<br><br>"
        f"{interpret_margin(net_margin, 'Net')}"), unsafe_allow_html=True)

    st.markdown(
        '<div class="section-header"><h2 class="section-title">Unit Economics</h2></div>',
        unsafe_allow_html=True
    )
    fig_unit = go.Figure()
    fig_unit.add_bar(
        name="Variable Costs",
        x=["Per Patient Economics"],
        y=[var_pp_y],
        marker=dict(color=PALETTE["chart"][1], line=dict(width=2, color="white")),
        text=[format_currency(var_pp_y)],
        textposition="inside",
        textfont=dict(color="white", size=12)
    )
    fig_unit.add_bar(
        name="Fixed Costs Allocation",
        x=["Per Patient Economics"],
        y=[fixed_y / patients if patients > 0 else 0],
        marker=dict(color=PALETTE["chart"][0], line=dict(width=2, color="white")),
        text=[format_currency(fixed_y / patients if patients > 0 else 0)],
        textposition="inside",
        textfont=dict(color="white", size=12)
    )
    fig_unit.add_bar(
        name="EBITDA per Patient",
        x=["Per Patient Economics"],
        y=[ebitda_per_patient],
        marker=dict(color=PALETTE["chart"][3], line=dict(width=2, color="white")),
        text=[format_currency(ebitda_per_patient)],
        textposition="inside",
        textfont=dict(color="white", size=12)
    )
    fig_unit.add_scatter(
        name="Tariff (Revenue)",
        x=["Per Patient Economics"],
        y=[tariff],
        mode="markers+text",
        marker=dict(size=20, color=PALETTE["danger"], symbol="diamond", line=dict(width=3, color="white")),
        text=[format_currency(tariff)],
        textposition="top center",
        textfont=dict(size=14, color=PALETTE["danger"])
    )
    apply_chart_layout(fig_unit, height=400)
    fig_unit.update_layout(barmode="stack", yaxis_title=f"Per Patient ({currency_label})", showlegend=True)
    st.plotly_chart(fig_unit, use_container_width=True)

    st.markdown(create_insight_box("3", "UNIT ECONOMICS ANALYSIS", interpret_unit_economics(contrib_pp, ebitda_per_patient, tariff)), unsafe_allow_html=True)


# =========================================================
# TAB 4: VALUATION MODEL (DCF + IRR + MIRR + Sensitivity)
# =========================================================
with tab_val:
    st.markdown(
        '<div class="section-header"><h2 class="section-title">Discounted Cash Flow (DCF) Valuation</h2></div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # 0. HELPERS (IRR, MIRR)
    # -----------------------------------------------------
    def mirr_from_cf(cash_flows, finance_rate, reinvest_rate):
        """
        cash_flows: array-like, cash_flows[0] = CF0
        finance_rate: rate for negative CFs (cost of capital)
        reinvest_rate: rate at which positive CFs are reinvested
        """
        cf = np.array(cash_flows, dtype=float)
        n = len(cf) - 1  # años posteriores al 0

        # PV de los negativos (traídos a t0 con finance_rate)
        pv_neg = 0.0
        for t, c in enumerate(cf):
            if c < 0:
                pv_neg += c / ((1 + finance_rate) ** t)

        # FV de los positivos (llevados a tN con reinvest_rate)
        fv_pos = 0.0
        for t, c in enumerate(cf):
            if c > 0:
                fv_pos += c * ((1 + reinvest_rate) ** (n - t))

        if pv_neg == 0 or n == 0:
            return None

        mirr_val = (abs(fv_pos / pv_neg) ** (1 / n)) - 1
        return mirr_val

    # -----------------------------------------------------
    # 1. CASH FLOWS – table + chart
    # -----------------------------------------------------
    col_cf_table, col_cf_chart = st.columns([0.45, 0.55], gap="large")

    with col_cf_table:
        # cf_df ya viene del modelo principal
        st.dataframe(cf_df, use_container_width=True, hide_index=True)

    with col_cf_chart:
        years_cf = list(range(len(cf_vec)))
        fig_cf_val = go.Figure()

        fig_cf_val.add_bar(
            name="Annual Cash Flow",
            x=[f"Y{y}" for y in years_cf],
            y=cf_vec,
            marker=dict(
                color=[PALETTE["chart"][0] if v < 0 else PALETTE["chart"][1] for v in cf_vec],
                line=dict(width=2, color="white")
            ),
            text=[format_currency(v) for v in cf_vec],
            textposition="outside"
        )

        fig_cf_val.add_scatter(
            name="Cumulative CF",
            x=[f"Y{y}" for y in years_cf],
            y=np.cumsum(cf_vec),
            mode="lines+markers",
            line=dict(color=PALETTE["chart"][3], width=4),
            marker=dict(size=10, color=PALETTE["chart"][3], line=dict(width=2, color="white")),
            yaxis="y2"
        )

        apply_chart_layout(fig_cf_val, height=420)
        fig_cf_val.update_layout(
            xaxis=dict(title="Year"),
            yaxis=dict(title=f"Annual Cash Flow ({currency_label})"),
            yaxis2=dict(title=f"Cumulative CF ({currency_label})", overlaying="y", side="right", showgrid=False)
        )
        st.plotly_chart(fig_cf_val, use_container_width=True)

    # -----------------------------------------------------
    # 2. VALUATION SUMMARY – KPI DECK
    # -----------------------------------------------------
    st.markdown(
        '<div class="section-header"><h2 class="section-title">Valuation Summary</h2></div>',
        unsafe_allow_html=True
    )

    # --- core metrics que ya tenías ---
    # ke: viene del sidebar
    # npv_val: NPV @ ke
    # irr_val: IRR ya calculado arriba en tu modelo
    # payback_year: payback ya calculado arriba
    # ebitda_y: EBITDA actual para múltiplo

    # MIRR: usamos un enfoque conservador → financiamos y reinvertimos al mismo Ke
    mirr_val = mirr_from_cf(cf_vec, finance_rate=ke, reinvest_rate=ke)

    # IRR spread
    if irr_val is not None:
        irr_spread_pp = (irr_val - ke) * 100  # puntos porcentuales reales
    else:
        irr_spread_pp = None

    # MIRR spread
    if mirr_val is not None:
        mirr_spread_pp = (mirr_val - ke) * 100
    else:
        mirr_spread_pp = None

    # implied multiple
    implied_multiple = None
    if ebitda_y and ebitda_y > 0:
        implied_multiple = npv_val / ebitda_y

    # labels seguros
    irr_label = "N/A" if irr_val is None else format_percentage(irr_val)
    mirr_label = "N/A" if mirr_val is None else format_percentage(mirr_val)
    irr_spread_label = "N/A" if irr_spread_pp is None else f"{irr_spread_pp:.1f} pp"
    mirr_spread_label = "N/A" if mirr_spread_pp is None else f"{mirr_spread_pp:.1f} pp"
    payback_label = "N/A" if payback_year is None else f"{payback_year} years"
    mult_label = "N/A" if implied_multiple is None else f"{implied_multiple:.1f}x"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                        border-radius:1rem;padding:1.05rem 1.2rem;">
                <div style="font-size:0.68rem;text-transform:uppercase;color:{PALETTE['text_tertiary']};
                            letter-spacing:.03em;font-weight:600;">Discount rate / Ke</div>
                <div style="font-size:1.7rem;font-weight:800;color:{PALETTE['text_primary']};margin-top:.3rem;">
                    {format_percentage(ke)}
                </div>
                <div style="font-size:0.7rem;color:{PALETTE['text_secondary']};margin-top:.4rem;">
                    Model hurdle rate
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                        border-radius:1rem;padding:1.05rem 1.2rem;">
                <div style="font-size:0.68rem;text-transform:uppercase;color:{PALETTE['text_tertiary']};
                            letter-spacing:.03em;font-weight:600;">NPV @ Ke</div>
                <div style="font-size:1.7rem;font-weight:800;color:{PALETTE['text_primary']};margin-top:.3rem;">
                    {format_currency(npv_val)}
                </div>
                <div style="font-size:0.7rem;color:{PALETTE['text_secondary']};margin-top:.4rem;">
                    Present value of FCF
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        # tarjeta con IRR y MIRR y sus spreads REALES
        st.markdown(
            f"""
            <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                        border-radius:1rem;padding:1.05rem 1.2rem;">
                <div style="font-size:0.68rem;text-transform:uppercase;color:{PALETTE['text_tertiary']};
                            letter-spacing:.03em;font-weight:600;">Return vs. hurdle</div>
                <div style="display:flex;gap:1.4rem;margin-top:.6rem;">
                    <div>
                        <div style="font-size:.6rem;color:{PALETTE['text_secondary']};text-transform:uppercase;">IRR</div>
                        <div style="font-size:1.05rem;font-weight:700;color:{PALETTE['text_primary']};">
                            {irr_label}
                        </div>
                        <div style="font-size:.6rem;color:{PALETTE['text_secondary']};">
                            Spread: {irr_spread_label}
                        </div>
                    </div>
                    <div>
                        <div style="font-size:.6rem;color:{PALETTE['text_secondary']};text-transform:uppercase;">MIRR</div>
                        <div style="font-size:1.05rem;font-weight:700;color:{PALETTE['text_primary']};">
                            {mirr_label}
                        </div>
                        <div style="font-size:.6rem;color:{PALETTE['text_secondary']};">
                            Spread: {mirr_spread_label}
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f"""
            <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                        border-radius:1rem;padding:1.05rem 1.2rem;">
                <div style="font-size:0.68rem;text-transform:uppercase;color:{PALETTE['text_tertiary']};
                            letter-spacing:.03em;font-weight:600;">Payback & multiple</div>
                <div style="font-size:1.25rem;font-weight:800;color:{PALETTE['text_primary']};margin-top:.35rem;">
                    {payback_label}
                </div>
                <div style="font-size:0.7rem;color:{PALETTE['text_secondary']};margin-top:.35rem;">
                    Implied EV/EBITDA: <b>{mult_label}</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # -----------------------------------------------------
    # 3. INTERPRETATION – automated, no “how to read”
    # -----------------------------------------------------
    if irr_val is None:
        irr_sentence = "Internal rate of return could not be derived from the current cash-flow pattern."
    else:
        irr_sentence = (
            f"Internal rate of return stands at {format_percentage(irr_val)}, which implies an "
            f"absolute spread of {irr_spread_label} over the model discount rate ({format_percentage(ke)})."
        )

    if mirr_val is None:
        mirr_sentence = "Modified IRR (MIRR) could not be computed with current inputs."
    else:
        mirr_sentence = (
            f"Modified IRR, assuming financing and reinvestment at {format_percentage(ke)}, is {format_percentage(mirr_val)}, "
            f"equivalent to a spread of {mirr_spread_label} over the hurdle. This is the more conservative profitability indicator."
        )

    if implied_multiple is None:
        mult_sentence = (
            "No EV/EBITDA multiple is shown because EBITDA is not positive or not available in this run."
        )
    elif implied_multiple < 2:
        mult_sentence = (
            f"The implied EV/EBITDA multiple of {implied_multiple:.1f}x sits clearly below outpatient healthcare references (6–10x), "
            f"which is consistent with a discounted valuation or with early-stage cash-flow volatility."
        )
    else:
        mult_sentence = (
            f"The implied EV/EBITDA multiple of {implied_multiple:.1f}x is within an acceptable band for healthcare delivery assets."
        )

    payback_sentence = (
        "Payback is not reached within the explicit forecast horizon."
        if payback_year is None
        else f"Capital is recovered in year {payback_year}, consistent with a health-services operating project."
    )

    st.markdown(
        create_insight_box(
            "1",
            "DCF VALUATION ANALYSIS",
            (
                f"<b>NPV at current Ke:</b> {format_currency(npv_val)}.<br><br>"
                f"<b>Return profile:</b> {irr_sentence}<br><br>"
                f"<b>Conservative return (MIRR):</b> {mirr_sentence}<br><br>"
                f"<b>Market view:</b> {mult_sentence}<br><br>"
                f"<b>Liquidity:</b> {payback_sentence}"
            ),
        ),
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # 4. NPV SENSITIVITY (Growth × Discount) – no numbers
    # -----------------------------------------------------
    st.markdown(
        '<div class="section-header"><h2 class="section-title">NPV Sensitivity (Growth × Discount Rate)</h2></div>',
        unsafe_allow_html=True
    )

    # rangos dinámicos alrededor de los valores del sidebar
    dr_low = max(0.08, ke - 0.06)
    dr_high = ke + 0.06
    discount_rates_val = np.round(np.linspace(dr_low, dr_high, 7), 4)

    gr_low = max(-0.05, rev_growth - 0.08)
    gr_high = rev_growth + 0.15
    growth_rates_val = np.round(np.linspace(gr_low, gr_high, 9), 4)

    npv_matrix_val = np.zeros((len(discount_rates_val), len(growth_rates_val)))
    for i, dr in enumerate(discount_rates_val):
        for j, gr in enumerate(growth_rates_val):
            # reconstruimos flujo con ese growth
            cf_temp = np.array([cf0, cf1])
            for _ in range(4):
                cf_temp = np.append(cf_temp, cf_temp[-1] * (1 + gr))
            npv_matrix_val[i, j] = npv_calc(dr, cf_temp)

    fig_heatmap_val = go.Figure(
        data=go.Heatmap(
            z=npv_matrix_val,
            x=[f"{g*100:.0f}%" for g in growth_rates_val],
            y=[f"{d*100:.1f}%" for d in discount_rates_val],
            colorscale=[
                [0, "#E2E8F0"],
                [0.4, "#BFDBFE"],
                [1, "#1D4ED8"],
            ],
            zmid=0,
            showscale=True,
            hovertemplate=f"<b>Scenario</b><br>Growth: %{{x}}<br>Discount: %{{y}}<br>NPV: {currency_symbol}%{{z:,.0f}}k<extra></extra>",
            colorbar=dict(title=f"NPV ({currency_label})", len=0.65, thickness=14)
        )
    )
    apply_chart_layout(fig_heatmap_val, height=400)
    fig_heatmap_val.update_layout(
        xaxis=dict(title="Growth rate"),
        yaxis=dict(title="Discount rate"),
    )
    st.plotly_chart(fig_heatmap_val, use_container_width=True)

    # interpretación automática de la matriz
    npv_min = float(npv_matrix_val.min())
    npv_max = float(npv_matrix_val.max())
    npv_span = npv_max - npv_min

    nearest_dr_idx = int(np.argmin(np.abs(discount_rates_val - ke)))
    nearest_gr_idx = int(np.argmin(np.abs(growth_rates_val - rev_growth)))
    npv_model_cell = float(npv_matrix_val[nearest_dr_idx, nearest_gr_idx])

    st.markdown(
        create_insight_box(
            "2",
            "VALUATION SENSITIVITY INTERPRETATION",
            (
                f"Current modelling point (growth {rev_growth*100:.0f}%, discount {ke*100:.1f}%) "
                f"yields an NPV of <b>{format_currency(npv_model_cell)}</b> inside the tested grid.<br><br>"
                f"Across the range, NPV moves from {format_currency(npv_min)} to {format_currency(npv_max)} "
                f"(spread of {format_currency(npv_span)}), indicating normal sensitivity to growth and to the cost of capital."
            ),
        ),
        unsafe_allow_html=True,
    )

# =========================================================
# TAB 5: STRATEGIC ANALYSIS
# =========================================================
with tab_analysis:
    st.markdown(
        '<div class="section-header"><h2 class="section-title">Executive Strategic Analysis</h2></div>',
        unsafe_allow_html=True
    )

    scenarios_strat, base_ebitda_strat, base_margin_strat = generate_stress_scenarios(
        patients, tariff, mix_low_pct, low_tariff,
        clinical_y, drugs_y, labs_y, admin_y, other_y, stress_costs
    )

    # ✅ ROIC proxy sobre la inversión real
    roic_proxy = safe_divide(ebitda_y, initial_investment)

    # ===== CARD 1: STRATEGIC POSITIONING =====
    if ebitda_margin >= 0.35 and mos_pct >= 0.5 and revenue_per_dollar_cost >= 1.5:
        strategic_position = "MARKET LEADER"
        position_color = "positive"
        position_desc = "Superior economics and robust margins position this as a market leader with sustainable competitive advantages."
    elif ebitda_margin >= 0.25 and mos_pct >= 0.3 and revenue_per_dollar_cost >= 1.3:
        strategic_position = "STRONG PERFORMER"
        position_color = "positive"
        position_desc = "Above-market performance indicates strong competitive positioning with opportunities for further optimization."
    elif ebitda_margin >= 0.15 and mos_pct >= 0.2 and revenue_per_dollar_cost >= 1.2:
        strategic_position = "MARKET PARTICIPANT"
        position_color = ""
        position_desc = "Adequate performance meets market standards but lacks differentiation. Strategic initiatives required to build defensible moats."
    else:
        strategic_position = "CHALLENGED POSITION"
        position_color = "warning"
        position_desc = "Below-market performance across multiple dimensions signals structural challenges requiring fundamental strategic repositioning."

    content_pos = (
        f'<span class="insight-tag {position_color}">{strategic_position}</span><br><br>'
        f'{position_desc}<br><br>'
        '<b>Core performance metrics:</b>'
        '<ul>'
        f'<li><b>EBITDA margin:</b> {format_percentage(ebitda_margin)} vs. industry benchmark 25–35%</li>'
        f'<li><b>Safety margin:</b> {format_percentage(mos_pct) if not np.isnan(mos_pct) else "N/A"} cushion above break-even</li>'
        f'<li><b>Revenue efficiency:</b> {currency_symbol}{revenue_per_dollar_cost:.2f} revenue per {currency_symbol}1 of cost</li>'
        f'<li><b>ROIC (proxy):</b> {format_percentage(roic_proxy) if initial_investment > 0 else "N/A"} return on invested capital</li>'
        '</ul>'
        f'<b>Competitive assessment:</b> The business demonstrates '
        f'{"strong" if ebitda_margin >= 0.25 else "moderate" if ebitda_margin >= 0.15 else "weak"} '
        f'competitive positioning based on profitability, efficiency, and resilience metrics.'
    )
    st.markdown(
        create_insight_box("1", "STRATEGIC POSITIONING", content_pos),
        unsafe_allow_html=True
    )

    # ===== Lógica de recomendación (se reutiliza abajo) =====
    if (
        npv_val > 500
        and ebitda_margin >= 0.25
        and (not np.isnan(mos_pct) and mos_pct >= 0.40)
        and (irr_val and irr_val > ke + 0.05)
    ):
        recommendation = "STRONG BUY"
        rec_class = "positive"
        rec_text = "Superior performance across all metrics supports immediate investment with high confidence."
    elif npv_val > 0 and ebitda_margin >= 0.18 and (not np.isnan(mos_pct) and mos_pct >= 0.25):
        recommendation = "BUY"
        rec_class = "positive"
        rec_text = "Solid fundamentals and positive value creation support investment thesis with standard risk management."
    elif npv_val > -200 and ebitda_margin >= 0.12:
        recommendation = "CONDITIONAL"
        rec_class = ""
        rec_text = "Marginal value creation warrants careful evaluation and may require operational improvements as investment condition."
    else:
        recommendation = "AVOID"
        rec_class = "negative"
        rec_text = "Weak performance and negative value creation do not support investment at current parameters."

    ev_ebitda = safe_divide(npv_val, ebitda_y)

    # ===== CARD 2: EXECUTIVE SUMMARY & RECOMMENDATION =====
    content_exec = (
        "<p><b>FINANCIAL PROFILE:</b></p>"
        "<ul>"
        f"<li>Revenue: <b>{format_currency(rev_y)}</b> from {patients} patients at {format_currency(tariff)}</li>"
        f"<li>EBITDA: <b>{format_currency(ebitda_y)}</b> ({format_percentage(ebitda_margin)} margin)</li>"
        f"<li>Net Profit: <b>{format_currency(net_y)}</b> ({format_percentage(net_margin)} after {format_percentage(tax_rate)} tax)</li>"
        f"<li>Free Cash Flow: <b>{format_currency(net_y * fcf_factor)}</b> ({format_percentage(fcf_factor)} conversion)</li>"
        "</ul>"
        "<p><b>INVESTMENT METRICS:</b></p>"
        "<ul>"
        f"<li>NPV @ {format_percentage(ke)}: <b>{format_currency(npv_val)}</b></li>"
        f"<li>IRR: <b>{format_percentage(irr_val) if irr_val else 'N/A'}</b></li>"
        f"<li>Payback: <b>{payback_year if payback_year else 'N/A'} years</b> | "
        f"EV/EBITDA: <b>{f'{ev_ebitda:.1f}x' if not np.isnan(ev_ebitda) and ev_ebitda > 0 else 'N/A'}</b></li>"
        "</ul>"
        "<p><b>RISK PROFILE:</b></p>"
        "<ul>"
        f"<li>Break-even: <b>{f'{be_patients:,.0f} patients' if not np.isnan(be_patients) else 'N/A'}</b></li>"
        f"<li>Safety margin: <b>{format_percentage(mos_pct) if not np.isnan(mos_pct) else 'N/A'}</b></li>"
        f"<li>Downside EBITDA: <b>{format_currency(scenarios_strat[-1]['ebitda'])}</b> "
        f"({scenarios_strat[-1]['impact_pct']:+.1f}% under combined stress)</li>"
        "</ul>"
        "<p><b>INVESTMENT RECOMMENDATION:</b><br>"
        f"<span class='insight-tag {rec_class}'>{recommendation}</span> {rec_text}"
        "</p>"
        "<p><b>FINAL ASSESSMENT:</b><br>"
        f"This outpatient clinic generates <b>{format_currency(ebitda_y)}</b> in annual EBITDA with "
        f"{format_percentage(mos_pct) if not np.isnan(mos_pct) else 'a limited'} margin of safety. "
        f"{'Positive NPV of <b>' + format_currency(npv_val) + '</b> and IRR above the hurdle rate support the investment thesis, provided execution discipline and continuous monitoring.' if npv_val > 0 else 'Current parameters do not create value; restructuring of tariff, volume, or cost base is recommended before investing.'}"
        "</p>"
    )

    st.markdown(
        create_insight_box("2", "EXECUTIVE SUMMARY & RECOMMENDATION", content_exec),
        unsafe_allow_html=True
    )

# =========================================================
# PROFESSIONAL REPORT EXPORT - CONSULTANT-GRADE STRUCTURE
# Place this code right before the footer, after all tabs
# =========================================================
from datetime import datetime
import io

def df_to_html_custom(df: pd.DataFrame, title: str, show_index: bool = False) -> str:
    """Convert DataFrame to styled HTML table"""
    return f"""
    <h2 class="section-title">{title}</h2>
    {df.to_html(index=show_index, border=0, classes='report-table', justify='left')}
    """

def fig_to_html_safe(fig, title: str) -> str:
    """Safely convert Plotly figure to HTML"""
    if fig is None:
        return ""
    try:
        return f"""
        <h2 class="section-title">{title}</h2>
        <div class="chart-container">
            {pio.to_html(fig, include_plotlyjs="cdn", full_html=False, config={"displayModeBar": False})}
        </div>
        """
    except:
        return ""

def create_kpi_card(label: str, value: str, meta: str = "") -> str:
    """Generate HTML for a KPI card"""
    meta_html = f'<div class="kpi-meta">{meta}</div>' if meta else ''
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {meta_html}
    </div>
    """

def create_insight_section(number: str, title: str, content: str) -> str:
    """Generate styled insight box"""
    return f"""
    <div class="insight-box">
        <div class="insight-header">
            <span class="insight-number">{number}</span>
            <span class="insight-title">{title}</span>
        </div>
        <div class="insight-content">{content}</div>
    </div>
    """

# =========================================================
# COLLECT ALL NECESSARY DATA SAFELY
# =========================================================

# Core metrics (always available)
report_date = datetime.now().strftime("%B %d, %Y at %H:%M")
report_filename = datetime.now().strftime('%Y%m%d_%H%M')

# Investment recommendation logic (from Tab 5)
if npv_val > 500 and ebitda_margin >= 0.25 and (not np.isnan(mos_pct) and mos_pct >= 0.40) and (irr_val and irr_val > ke + 0.05):
    recommendation = "STRONG BUY"
    rec_class = "positive"
    rec_text = "Superior performance across all metrics supports immediate investment with high confidence."
elif npv_val > 0 and ebitda_margin >= 0.18 and (not np.isnan(mos_pct) and mos_pct >= 0.25):
    recommendation = "BUY"
    rec_class = "positive"
    rec_text = "Solid fundamentals and positive value creation support investment thesis with standard risk management."
elif npv_val > -200 and ebitda_margin >= 0.12:
    recommendation = "CONDITIONAL"
    rec_class = "warning"
    rec_text = "Marginal value creation warrants careful evaluation and may require operational improvements as investment condition."
else:
    recommendation = "AVOID"
    rec_class = "negative"
    rec_text = "Weak performance and negative value creation do not support investment at current parameters."

# Strategic positioning (from Tab 5)
if ebitda_margin >= 0.35 and mos_pct >= 0.5 and revenue_per_dollar_cost >= 1.5:
    strategic_position = "MARKET LEADER"
    position_class = "positive"
elif ebitda_margin >= 0.25 and mos_pct >= 0.3 and revenue_per_dollar_cost >= 1.3:
    strategic_position = "STRONG PERFORMER"
    position_class = "positive"
elif ebitda_margin >= 0.15 and mos_pct >= 0.2 and revenue_per_dollar_cost >= 1.2:
    strategic_position = "MARKET PARTICIPANT"
    position_class = "neutral"
else:
    strategic_position = "CHALLENGED POSITION"
    position_class = "warning"

# EV/EBITDA multiple
ev_ebitda = safe_divide(npv_val, ebitda_y)
ev_ebitda_str = f"{ev_ebitda:.1f}x" if not np.isnan(ev_ebitda) and ev_ebitda > 0 else "N/A"

# Stress scenarios (safely)
try:
    scenarios_report, _, _ = generate_stress_scenarios(
        patients, tariff, mix_low_pct, low_tariff,
        clinical_y, drugs_y, labs_y, admin_y, other_y, stress_costs
    )
    stress_df_report = pd.DataFrame(scenarios_report)
    worst_ebitda = stress_df_report.iloc[-1]["ebitda"]
    worst_impact = stress_df_report.iloc[-1]["impact_pct"]
    has_stress_data = True
except:
    has_stress_data = False
    worst_ebitda = 0
    worst_impact = 0

# ROIC proxy
roic_proxy = safe_divide(ebitda_y, initial_investment)

# Safe formatting helpers for conditional values
be_patients_str = f"{be_patients:,.0f}" if not np.isnan(be_patients) else "N/A"
be_revenue_str = format_currency(be_revenue) if not np.isnan(be_revenue) else "N/A"
mos_pct_str = format_percentage(mos_pct) if not np.isnan(mos_pct) else "N/A"
mos_pat_str = f"{mos_pat:,.0f}" if not np.isnan(mos_pat) else "N/A"
irr_str = format_percentage(irr_val) if irr_val else "N/A"
payback_str = f"{payback_year} years" if payback_year else "N/A"

# Logo handling for report
logo_html = ""
if logo_b64:
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" alt="Colombiana de Trasplantes" style="max-height: 60px; margin-bottom: 1rem;">'

# =========================================================
# BUILD COMPLETE HTML REPORT
# =========================================================

report_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Analysis Report - Colombiana de Trasplantes</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #f8fafc;
            color: #0f172a;
            line-height: 1.6;
            padding: 0;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
        }}
        
        /* HEADER */
        .header {{
            background: linear-gradient(135deg, {PALETTE["primary"]} 0%, {PALETTE["primary_dark"]} 100%);
            color: white;
            padding: 2.5rem 3rem 2.5rem 3rem;
            border-bottom: 4px solid {PALETTE["primary_dark"]};
        }}
        
        .header-logo {{
            margin-bottom: 1.25rem;
        }}
        
        .header h1 {{
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin-bottom: 0.75rem;
        }}
        
        .header .subtitle {{
            font-size: 1rem;
            opacity: 0.95;
            font-weight: 400;
        }}
        
        .header .meta {{
            font-size: 0.82rem;
            opacity: 0.8;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(255,255,255,0.2);
        }}
        
        /* CONTENT */
        .content {{
            padding: 2.5rem 3rem 4rem 3rem;
        }}
        
        .section {{
            margin-bottom: 3.5rem;
            page-break-inside: avoid;
        }}
        
        .section-title {{
            font-size: 1.4rem;
            font-weight: 700;
            color: {PALETTE["text_primary"]};
            margin-bottom: 1.2rem;
            padding-bottom: 0.6rem;
            border-bottom: 3px solid {PALETTE["primary"]};
        }}
        
        .subsection-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: {PALETTE["text_primary"]};
            margin: 2rem 0 1rem 0;
        }}
        
        /* KPI GRID */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.25rem;
            margin: 1.5rem 0 2.5rem 0;
        }}
        
        .kpi-card {{
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.3rem 1.4rem;
            box-shadow: 0 2px 8px rgba(15,23,42,0.04);
            position: relative;
            overflow: hidden;
        }}
        
        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, {PALETTE["primary"]}, {PALETTE["secondary"]});
        }}
        
        .kpi-label {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: {PALETTE["text_tertiary"]};
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        
        .kpi-value {{
            font-size: 1.6rem;
            font-weight: 800;
            color: {PALETTE["text_primary"]};
            margin-bottom: 0.3rem;
        }}
        
        .kpi-meta {{
            font-size: 0.75rem;
            color: {PALETTE["text_secondary"]};
        }}
        
        /* TABLES */
        table.report-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            overflow: hidden;
            margin: 1rem 0 2rem 0;
            font-size: 0.85rem;
        }}
        
        table.report-table thead th {{
            background: {PALETTE["primary"]};
            color: white;
            text-align: left;
            padding: 0.7rem 0.9rem;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            font-weight: 600;
        }}
        
        table.report-table tbody td {{
            padding: 0.65rem 0.9rem;
            border-bottom: 1px solid #f1f5f9;
        }}
        
        table.report-table tbody tr:last-child td {{
            border-bottom: none;
        }}
        
        table.report-table tbody tr:hover {{
            background: #f8fafc;
        }}
        
        /* INSIGHT BOXES */
        .insight-box {{
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            box-shadow: 0 2px 8px rgba(15,23,42,0.03);
        }}
        
        .insight-header {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }}
        
        .insight-number {{
            background: {PALETTE["primary"]};
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 700;
        }}
        
        .insight-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: {PALETTE["text_primary"]};
        }}
        
        .insight-content {{
            font-size: 0.85rem;
            line-height: 1.7;
            color: {PALETTE["text_secondary"]};
        }}
        
        .insight-content ul {{
            margin: 0.75rem 0;
            padding-left: 1.5rem;
        }}
        
        .insight-content li {{
            margin: 0.4rem 0;
        }}
        
        .insight-content b {{
            color: {PALETTE["text_primary"]};
            font-weight: 600;
        }}
        
        .insight-content p {{
            margin: 0.75rem 0;
        }}
        
        /* TAGS */
        .tag {{
            display: inline-block;
            padding: 0.25rem 0.65rem;
            border-radius: 999px;
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            font-weight: 600;
            margin: 0 0.25rem 0.25rem 0;
        }}
        
        .tag.positive {{
            background: rgba(16,185,129,0.12);
            color: #065f46;
        }}
        
        .tag.warning {{
            background: rgba(245,158,11,0.12);
            color: #92400e;
        }}
        
        .tag.negative {{
            background: rgba(239,68,68,0.12);
            color: #7f1d1d;
        }}
        
        .tag.neutral {{
            background: rgba(99,102,241,0.1);
            color: #3730a3;
        }}
        
        /* RECOMMENDATION BOX */
        .recommendation-box {{
            background: linear-gradient(135deg, {PALETTE["surface"]} 0%, {PALETTE["surface_alt"]} 100%);
            border: 2px solid {PALETTE["primary"]};
            border-radius: 16px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 8px 24px rgba(30,64,175,0.08);
        }}
        
        .recommendation-box .rec-label {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: {PALETTE["text_tertiary"]};
            font-weight: 600;
            margin-bottom: 0.75rem;
        }}
        
        .recommendation-box .rec-value {{
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 1rem;
        }}
        
        .recommendation-box .rec-text {{
            font-size: 0.9rem;
            line-height: 1.6;
            color: {PALETTE["text_secondary"]};
        }}
        
        /* CHARTS */
        .chart-container {{
            margin: 1.5rem 0 2.5rem 0;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1rem;
        }}
        
        /* PARAMETER GRID */
        .param-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0.75rem;
            background: {PALETTE["surface_alt"]};
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1.5rem 0;
        }}
        
        .param-item {{
            font-size: 0.78rem;
        }}
        
        .param-item .label {{
            color: {PALETTE["text_tertiary"]};
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            font-weight: 600;
        }}
        
        .param-item .value {{
            color: {PALETTE["text_primary"]};
            font-weight: 700;
            font-size: 0.9rem;
            margin-top: 0.2rem;
        }}
        
        /* FOOTER */
        .footer {{
            background: {PALETTE["surface_alt"]};
            padding: 2rem 3rem;
            text-align: center;
            font-size: 0.75rem;
            color: {PALETTE["text_tertiary"]};
            border-top: 1px solid #e2e8f0;
        }}
        
        /* PRINT STYLES */
        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
            .section {{
                page-break-inside: avoid;
            }}
            .chart-container {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="header">
            <div class="header-logo">
                {logo_html}
            </div>
            <h1>Clinic P&L Financial Analysis Report</h1>
            <div class="subtitle">Colombiana de Trasplantes · Outpatient Follow-up Division</div>
            <div class="meta">Generated on {report_date} · All figures in thousands {currency} ({currency_label})</div>
        </div>
        
        <div class="content">
            <!-- ========================================== -->
            <!-- SECTION 1: EXECUTIVE SUMMARY -->
            <!-- ========================================== -->
            <div class="section">
                <h2 class="section-title">1. Executive Summary & Investment Recommendation</h2>
                
                <div class="recommendation-box">
                    <div class="rec-label">Investment Recommendation</div>
                    <div class="rec-value">
                        <span class="tag {rec_class}" style="font-size: 1.1rem; padding: 0.4rem 1rem;">
                            {recommendation}
                        </span>
                    </div>
                    <div class="rec-text">{rec_text}</div>
                </div>
                
                <h3 class="subsection-title">Financial Profile</h3>
                <div class="kpi-grid">
                    {create_kpi_card("Annual Revenue", format_currency(rev_y), f"{patients} pts × {format_currency(tariff)}")}
                    {create_kpi_card("EBITDA", format_currency(ebitda_y), f"{format_percentage(ebitda_margin)} margin")}
                    {create_kpi_card("Net Profit", format_currency(net_y), f"{format_percentage(net_margin)} after tax")}
                    {create_kpi_card("Free Cash Flow", format_currency(net_y * fcf_factor), f"{format_percentage(fcf_factor)} conversion")}
                </div>
                
                <h3 class="subsection-title">Investment Metrics</h3>
                <div class="kpi-grid">
                    {create_kpi_card("NPV", format_currency(npv_val), f"@ {format_percentage(ke)} discount rate")}
                    {create_kpi_card("IRR", irr_str, f"vs {format_percentage(ke)} hurdle")}
                    {create_kpi_card("Payback Period", payback_str, f"EV/EBITDA: {ev_ebitda_str}")}
                    {create_kpi_card("ROIC (proxy)", format_percentage(roic_proxy), f"on {format_currency(initial_investment)} invested")}
                </div>
                
                <h3 class="subsection-title">Risk Profile</h3>
                <div class="kpi-grid">
                    {create_kpi_card("Break-Even Volume", f"{be_patients_str} pts", f"Current: {patients} pts")}
                    {create_kpi_card("Margin of Safety", mos_pct_str, f"{mos_pat_str} patient buffer")}
                    {create_kpi_card("Strategic Position", strategic_position, f"vs industry benchmarks")}
                    {create_kpi_card("Stress EBITDA", format_currency(worst_ebitda) if has_stress_data else "N/A", f"{worst_impact:+.1f}% worst case" if has_stress_data else "N/A")}
                </div>
                
                {create_insight_section(
                    "1",
                    "Executive Assessment",
                    f'''<p>This outpatient clinic generates <b>{format_currency(ebitda_y)}</b> in annual EBITDA 
                    with a <b>{format_percentage(ebitda_margin)}</b> margin on <b>{format_currency(rev_y)}</b> of revenue 
                    from {patients} patients. The business is positioned as a <span class="tag {position_class}">{strategic_position}</span> 
                    within the specialized healthcare services sector.</p>
                    
                    <p><b>Value creation:</b> {'Positive NPV of <b>' + format_currency(npv_val) + '</b> and IRR of <b>' + irr_str + '</b> (above the ' + format_percentage(ke) + ' hurdle rate) support the investment thesis.' if npv_val > 0 and irr_val and irr_val > ke else 'Current parameters do not create sufficient value; operational improvements or structural changes required before investment.'}</p>
                    
                    <p><b>Risk assessment:</b> The model maintains a <b>{mos_pct_str}</b> 
                    margin of safety, breaking even at <b>{be_patients_str} patients</b>. 
                    {'Resilience to downside scenarios is adequate for healthcare operations.' if not np.isnan(mos_pct) and mos_pct >= 0.3 else 'Limited buffer requires tight operational discipline and continuous monitoring.'}</p>
                    
                    <p><b>Strategic implications:</b> Revenue efficiency of <b>{currency_symbol}{revenue_per_dollar_cost:.2f}</b> per {currency_symbol}1 of cost 
                    and an implied <b>{ev_ebitda_str}</b> EV/EBITDA multiple {'aligns with market valuations for specialized outpatient facilities (6–10x benchmark).' if ev_ebitda and 5 <= ev_ebitda <= 12 else 'suggests reassessment of operating model or exit strategy.'}</p>'''
                )}
            </div>
            
            <!-- ========================================== -->
            <!-- SECTION 2: BASE CASE FINANCIAL MODEL -->
            <!-- ========================================== -->
            <div class="section">
                <h2 class="section-title">2. Base Case Financial Model</h2>
                
                <h3 class="subsection-title">Model Parameters</h3>
                <div class="param-grid">
                    <div class="param-item">
                        <div class="label">Volume</div>
                        <div class="value">{patients} patients/year</div>
                    </div>
                    <div class="param-item">
                        <div class="label">Tariff</div>
                        <div class="value">{format_currency(tariff)}</div>
                    </div>
                    <div class="param-item">
                        <div class="label">Tax Rate</div>
                        <div class="value">{format_percentage(tax_rate)}</div>
                    </div>
                    <div class="param-item">
                        <div class="label">Growth Rate</div>
                        <div class="value">{format_percentage(rev_growth)}</div>
                    </div>
                    <div class="param-item">
                        <div class="label">Discount Rate</div>
                        <div class="value">{format_percentage(ke)}</div>
                    </div>
                    <div class="param-item">
                        <div class="label">Initial Investment</div>
                        <div class="value">{format_currency(initial_investment)}</div>
                    </div>
                </div>
                
                <h3 class="subsection-title">Profit & Loss Statement</h3>
                {df_to_html_custom(pnl_df, "", False)}
                
                {create_insight_section(
                    "2",
                    "P&L Structure Analysis",
                    f'''<p>{interpret_margin(ebitda_margin, 'EBITDA')}</p>
                    <p>{interpret_margin(net_margin, 'Net')}</p>
                    <p><b>Profitability cascade:</b> For every dollar of revenue, <b>{gross_margin*100:.1f}%</b> remains 
                    after direct costs, <b>{ebitda_margin*100:.1f}%</b> after operating expenses, and 
                    <b>{net_margin*100:.1f}%</b> flows to bottom line.</p>
                    <p><b>Cost efficiency:</b> The business generates <b>{currency_symbol}{revenue_per_dollar_cost:.2f}</b> of revenue 
                    for every dollar of total costs {'(excellent efficiency)' if revenue_per_dollar_cost >= 1.5 else '(good efficiency)' if revenue_per_dollar_cost >= 1.3 else '(adequate efficiency)' if revenue_per_dollar_cost >= 1.2 else '(low efficiency - requires attention)'}.</p>'''
                )}
            </div>
            
            <!-- ========================================== -->
            <!-- SECTION 3: UNIT ECONOMICS & COST STRUCTURE -->
            <!-- ========================================== -->
            <div class="section">
                <h2 class="section-title">3. Unit Economics & Cost Structure</h2>
                
                <h3 class="subsection-title">Cost Breakdown</h3>
                <div class="kpi-grid">
                    {create_kpi_card("Clinical Staff", format_currency(clinical_y), f"{format_percentage(clinical_y/rev_y)} of revenue")}
                    {create_kpi_card("Drugs (w/ contingency)", format_currency(drugs_y), f"{format_percentage(drugs_y/rev_y)} of revenue")}
                    {create_kpi_card("Labs & Imaging", format_currency(labs_y), f"{format_percentage(labs_y/rev_y)} of revenue")}
                    {create_kpi_card("Administrative", format_currency(admin_y), f"{format_percentage(admin_y/rev_y)} of revenue")}
                    {create_kpi_card("Other OpEx", format_currency(other_y), f"{format_percentage(other_y/rev_y)} of revenue")}
                    {create_kpi_card("Total Costs", format_currency(clinical_y + drugs_y + labs_y + admin_y + other_y), f"{format_percentage((clinical_y+drugs_y+labs_y+admin_y+other_y)/rev_y)} of revenue")}
                </div>
                
                <h3 class="subsection-title">Fixed vs Variable Analysis</h3>
                <div class="kpi-grid">
                    {create_kpi_card("Fixed Costs", format_currency(fixed_y), f"{format_percentage(fixed_ratio)} of revenue")}
                    {create_kpi_card("Variable Costs", format_currency(drugs_y + labs_y), f"{format_percentage(var_ratio)} of revenue")}
                    {create_kpi_card("Contribution/Patient", format_currency(contrib_pp), f"{format_percentage(contrib_pp/tariff)} of tariff")}
                    {create_kpi_card("EBITDA/Patient", format_currency(ebitda_per_patient), f"from {format_currency(tariff)} tariff")}
                </div>
                
                {create_insight_section(
                    "3",
                    "Cost Structure & Unit Economics",
                    interpret_cost_structure(fixed_ratio, var_ratio, clinical_y, admin_y) + "<br><br>" +
                    interpret_unit_economics(contrib_pp, ebitda_per_patient, tariff)
                )}
            </div>
            
            <!-- ========================================== -->
            <!-- SECTION 4: VALUATION & DCF MODEL -->
            <!-- ========================================== -->
            <div class="section">
                <h2 class="section-title">4. DCF Valuation Model</h2>
                
                <h3 class="subsection-title">5-Year Cash Flow Projection</h3>
                {df_to_html_custom(cf_df, "", False)}
                
                <h3 class="subsection-title">Valuation Metrics</h3>
                <div class="kpi-grid">
                    {create_kpi_card("Discount Rate (Ke)", format_percentage(ke), "Cost of equity / hurdle rate")}
                    {create_kpi_card("Net Present Value", format_currency(npv_val), "Present value of FCF")}
                    {create_kpi_card("Internal Rate of Return", irr_str, f"Spread: {format_percentage(irr_val - ke) if irr_val else 'N/A'} vs hurdle")}
                    {create_kpi_card("Payback & Multiple", payback_str, f"EV/EBITDA: {ev_ebitda_str}")}
                </div>
                
                {create_insight_section(
                    "4",
                    "DCF Valuation Analysis",
                    interpret_valuation(npv_val, irr_val, payback_year, ebitda_y, ke)
                )}
            </div>
            
            <!-- ========================================== -->
            <!-- SECTION 5: SENSITIVITY & RISK ANALYSIS -->
            <!-- ========================================== -->
            <div class="section">
                <h2 class="section-title">5. Sensitivity & Risk Analysis</h2>
                
                <h3 class="subsection-title">Break-Even Analysis</h3>
                <div class="kpi-grid">
                    {create_kpi_card("Unit Contribution", format_currency(contrib_pp), f"{format_percentage(contrib_pp/tariff)} of tariff")}
                    {create_kpi_card("Break-Even Volume", f"{be_patients_str} pts", f"Revenue: {be_revenue_str}")}
                    {create_kpi_card("Margin of Safety", mos_pct_str, f"{mos_pat_str} patient buffer")}
                    {create_kpi_card("Fixed Cost Share", format_percentage(fixed_ratio), f"{format_currency(fixed_y)} annual")}
                </div>
                
                {create_insight_section(
                    "5",
                    "Break-Even & CVP Analysis",
                    interpret_breakeven(patients, be_patients, mos_pct)
                )}
                
                {"<h3 class='subsection-title'>Downside Stress Testing</h3>" + df_to_html_custom(stress_df_report[['name', 'ebitda', 'margin', 'impact_pct']].rename(columns={'name': 'Scenario', 'ebitda': f'EBITDA ({currency_label})', 'margin': 'Margin', 'impact_pct': 'Δ%'}), "", False) if has_stress_data else ""}
                
                {create_insight_section(
                    "6",
                    "Risk Assessment",
                    f'''<p><b>Downside resilience:</b> Under combined adverse scenarios (payer mix erosion, volume decline, cost inflation), 
                    EBITDA {'remains positive at <b>' + format_currency(worst_ebitda) + '</b>, representing a <b>' + str(abs(worst_impact)) + '%</b> reduction from baseline.' if has_stress_data and worst_ebitda > 0 else 'falls below break-even, indicating vulnerability to simultaneous adverse shocks.' if has_stress_data else 'has not been fully stress-tested in this analysis.'}</p>
                    
                    <p><b>Primary risk factors:</b></p>
                    <ul>
                        <li><b>Volume risk:</b> High fixed-cost base ({format_percentage(fixed_ratio)} of revenue) creates operating leverage—profits are highly sensitive to patient volume changes</li>
                        <li><b>Payer mix risk:</b> Tariff erosion or shift to lower-reimbursement payers directly impacts unit economics</li>
                        <li><b>Cost inflation risk:</b> Clinical labor represents {format_percentage(clinical_y/(clinical_y+admin_y))} of payroll—wage inflation could pressure margins</li>
                    </ul>
                    
                    <p><b>Mitigation strategies:</b> Maintain diversified payer contracts with minimum reimbursement floors, implement systematic referral network development, negotiate multi-year supply contracts, and establish quarterly stress testing protocols.</p>'''
                ) if has_stress_data else ""}
            </div>
            
            <!-- ========================================== -->
            <!-- SECTION 6: STRATEGIC POSITIONING -->
            <!-- ========================================== -->
            <div class="section">
                <h2 class="section-title">6. Strategic Positioning & Market Context</h2>
                
                <h3 class="subsection-title">Competitive Position</h3>
                <div class="param-grid">
                    <div class="param-item">
                        <div class="label">Classification</div>
                        <div class="value">
                            <span class="tag {position_class}">{strategic_position}</span>
                        </div>
                    </div>
                    <div class="param-item">
                        <div class="label">EBITDA Margin</div>
                        <div class="value">{format_percentage(ebitda_margin)}</div>
                        <div style="font-size:0.7rem;color:#64748b;margin-top:0.2rem;">vs 25-35% benchmark</div>
                    </div>
                    <div class="param-item">
                        <div class="label">Safety Margin</div>
                        <div class="value">{mos_pct_str}</div>
                        <div style="font-size:0.7rem;color:#64748b;margin-top:0.2rem;">above break-even</div>
                    </div>
                    <div class="param-item">
                        <div class="label">Revenue Efficiency</div>
                        <div class="value">{currency_symbol}{revenue_per_dollar_cost:.2f}</div>
                        <div style="font-size:0.7rem;color:#64748b;margin-top:0.2rem;">per dollar of cost</div>
                    </div>
                    <div class="param-item">
                        <div class="label">ROIC (proxy)</div>
                        <div class="value">{format_percentage(roic_proxy)}</div>
                        <div style="font-size:0.7rem;color:#64748b;margin-top:0.2rem;">return on invested capital</div>
                    </div>
                    <div class="param-item">
                        <div class="label">EV/EBITDA Multiple</div>
                        <div class="value">{ev_ebitda_str}</div>
                        <div style="font-size:0.7rem;color:#64748b;margin-top:0.2rem;">vs 6-10x benchmark</div>
                    </div>
                </div>
                
                {create_insight_section(
                    "7",
                    "Strategic Assessment",
                    f'''<p><b>Market positioning:</b> The business demonstrates 
                    {"strong" if ebitda_margin >= 0.25 else "moderate" if ebitda_margin >= 0.15 else "weak"} 
                    competitive positioning within the specialized healthcare delivery sector. Operating margins 
                    {'exceed' if ebitda_margin > 0.30 else 'align with' if ebitda_margin >= 0.20 else 'fall below'} 
                    industry benchmarks for outpatient facilities (25–35%).</p>
                    
                    <p><b>Competitive advantages:</b></p>
                    <ul>
                        <li>Specialized transplant follow-up creates referral barriers and clinical expertise moats</li>
                        <li>{'Strong' if revenue_per_dollar_cost >= 1.5 else 'Adequate' if revenue_per_dollar_cost >= 1.3 else 'Limited'} 
                        operational efficiency with {currency_symbol}{revenue_per_dollar_cost:.2f} revenue per cost {currency_symbol}1</li>
                        <li>{'Robust' if not np.isnan(mos_pct) and mos_pct >= 0.4 else 'Moderate' if not np.isnan(mos_pct) and mos_pct >= 0.25 else 'Limited'} 
                        margin of safety provides operational flexibility</li>
                    </ul>
                    
                    <p><b>Strategic imperatives:</b></p>
                    <ul>
                        <li><b>Volume growth:</b> With {format_percentage(fixed_ratio)} fixed costs, incremental patients are highly accretive—focus on referral network expansion</li>
                        <li><b>Payer optimization:</b> Current {format_currency(tariff)} tariff must be defended; shift payer mix toward higher-reimbursement contracts</li>
                        <li><b>Cost discipline:</b> Variable costs at {format_percentage(var_ratio)} provide some flexibility, but clinical labor inflation must be monitored</li>
                        <li><b>Scale benefits:</b> Break-even at {be_patients_str} patients vs {patients} current—operating leverage supports expansion</li>
                    </ul>
                    
                    <p><b>Investment thesis:</b> {'This asset creates value through a combination of specialized clinical positioning, operating scale, and favorable unit economics. The <b>' + format_currency(npv_val) + '</b> NPV and <b>' + irr_str + '</b> IRR support investment at current parameters.' if npv_val > 0 and irr_val and irr_val > ke else 'Current operating parameters do not generate sufficient returns. Structural improvements in volume, tariff, or cost structure are required before investment is recommended.'}</p>'''
                )}
            </div>
            
        </div>
        
        <!-- FOOTER -->
        <div class="footer">
            <p><b>Colombiana de Trasplantes</b> · Outpatient Follow-up Division Financial Analysis</p>
            <p>Report generated automatically from Streamlit financial model · {report_date}</p>
            <p style="margin-top:0.5rem;font-size:0.7rem;">
                This analysis is based on current operating assumptions and market conditions. 
                Actual results may vary. All projections are subject to execution risk and market dynamics.
            </p>
        </div>
    </div>
</body>
</html>
"""

# =========================================================
# DOWNLOAD BUTTON IN SIDEBAR
# =========================================================
st.sidebar.markdown("---")
st.sidebar.markdown(
    '<div style="font-size:0.75rem;font-weight:600;text-transform:uppercase;'
    'letter-spacing:0.05em;color:#E2E8F0;margin-bottom:0.8rem;">Export Options</div>',
    unsafe_allow_html=True
)

st.sidebar.download_button(
    label="Download Full Report\n(HTML)",
    data=report_html,
    file_name=f"Clinic_Financial_Report_{report_filename}.html",
    mime="text/html",
    help="Download complete financial analysis report with all charts and interpretations",
    use_container_width=True
)

st.sidebar.markdown(
    '<div style="font-size:0.68rem;color:rgba(255,255,255,0.7);margin-top:0.5rem;line-height:1.4;">'
    'Professional-grade report includes Executive Summary, Base Case Model, Unit Economics, '
    'DCF Valuation, Risk Analysis, and Strategic Positioning.'
    '</div>',
    unsafe_allow_html=True
)

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
footer_html = """
<div class="footer">
    <b>Clinic P&L Financial Model</b> | Colombiana de Trasplantes<br>
    Strategic Financial Analysis Dashboard | For Internal Use Only<br>
    Model Version 2.0 | All figures in thousands USD unless otherwise noted
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
