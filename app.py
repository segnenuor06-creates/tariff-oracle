import streamlit as st
import os
from google import genai
from google.genai import types
from matrix import TARIFF_MATRIX, calculate_landed_cost

# Initialize configuration with custom page title
st.set_page_config(page_title="Tariff Oracle Engine", page_icon="⚡", layout="wide")

# Fetch securely from local secrets configuration
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))

# Initialize Session State Data Loggers
if "history" not in st.session_state:
    st.session_state.history = []

# HARDCORE THEME INJECTION: Transforming the app into a premium executive dark terminal
st.markdown("""
    <style>
    /* Global App Canvas Background */
    .stApp {
        background: linear-gradient(145deg, #0b0f17 0%, #111622 100%) !important;
    }
    
    /* Global Text Styling Adjustments */
    html, body, [data-testid="stWidgetLabel"] p {
        font-family: 'Inter', -apple-system, sans-serif !important;
        color: #c9d1d9 !important;
        font-size: 14px;
        font-weight: 500;
    }
    
    /* Main Dashboard Header Customization */
    .main-title {
        font-size: 32px !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #10b981, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px !important;
    }
    
    /* Subtitle Metrics Styling */
    .sub-title {
        color: #8b949e !important;
        font-size: 14px !important;
        margin-bottom: 25px !important;
    }

    /* Glassmorphism Input & Panel Containers */
    div[data-testid="stBlock"] {
        border-radius: 0px;
    }
    .custom-section {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid #30363d;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    /* Premium Metric Card Grid */
    .premium-card {
        background: #161b22;
        border: 1px solid #21262d;
        border-left: 4px solid #8b949e;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    }
    .premium-card-total {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-left: 5px solid #10b981;
        padding: 22px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.1);
    }
    .card-label {
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #8b949e;
        margin-bottom: 5px;
    }
    .card-value {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #f0f6fc;
    }
    .card-value-highlight {
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #10b981;
    }
    
    /* Action Premium Button Makeover */
    .stButton>button {
        background: linear-gradient(90deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 14px 20px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25) !important;
        transition: all 0.2s ease;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
    }
    
    /* Native Input Element Overrides for Seamless Dark Style */
    input, textarea, select {
        background-color: #0d1117 !important;
        color: #f0f6fc !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
    }
    
    /* Mobile-First Table View Tweak */
    .responsive-table {
        overflow-x: auto;
    }
    </style>
    """, unsafe_allow_html=True)

# App Core Title Section
st.markdown('<div class="main-title">⚡ TARIFF ORACLE ENGINE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">AI-Powered Customs Assessment Matrix • Ghana Port Corridor (2026 Act 1151 Compliant)</div>', unsafe_allow_html=True)

# Main Application Structure Split
col_input, col_display = st.columns([1, 1.1], gap="large")

with col_input:
    st.markdown('<div class="custom-section">', unsafe_allow_html=True)
    st.markdown('<h3 style="margin-top:0;margin-bottom:20px;font-size:18px;color:#f0f6fc;">📋 Cargo Configuration</h3>', unsafe_allow_html=True)
    
    # Grid for numerical pricing values
    sub_col1, sub_col2, sub_col3 = st.columns(3)
    with sub_col1:
        fx_rate = st.number_input("Exchange Rate (GHS)", min_value=1.0, value=15.20, step=0.10)
    with sub_col2:
        fob_usd = st.number_input("FOB Value (USD)", min_value=0.0, value=5000.0, step=100.0)
    with sub_col3:
        freight_usd = st.number_input("Freight Cost (USD)", min_value=0.0, value=1200.0, step=50.0)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    manifest_raw = st.text_area(
        "Describe cargo manifest details:",
        placeholder="e.g., 45 crates of industrial grade solar inverters and lithium power packs from Guangzhou...",
        height=110
    )
    
    calculate_trigger = st.button("Run AI Assessment Engine")
    st.markdown('</div>', unsafe_allow_html=True)

with col_display:
    st.markdown('<div class="custom-section" style="min-height: 425px;">', unsafe_allow_html=True)
    st.markdown('<h3 style="margin-top:0;margin-bottom:20px;font-size:18px;color:#f0f6fc;">📊 Calculated Financial Obligations</h3>', unsafe_allow_html=True)
    
    if calculate_trigger and manifest_raw:
        if not api_key:
            st.error("Missing Security Credential: Place a valid GEMINI_API_KEY inside your local configuration dashboard.")
        else:
            try:
                client = genai.Client(api_key=api_key)
                system_instruction = (
                    "You are an expert customs classifier. Analyze the user cargo input and output "
                    f"EXACTLY one of these literal keys: {list(TARIFF_MATRIX.keys())}. "
                    "Output ONLY the key name, followed by a pipeline symbol (|) and a short sentence detailing why it fits. No markdown."
                )
                
                with st.spinner("Analyzing cargo parameters against target matrix..."):
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=manifest_raw,
                        config=types.GenerateContentConfig(system_instruction=system_instruction)
                    )
                    
                    ai_output = response.text.strip().split("|")
                    matched_key = ai_output[0].strip()
                    rationale = ai_output[1].strip() if len(ai_output) > 1 else "Optimized pattern allocation matched."
                
                if matched_key in TARIFF_MATRIX:
                    results = calculate_landed_cost(matched_key, fob_usd, freight_usd, fx_rate)
                    
                    # AI Context Callouts
                    st.markdown(f"<div style='background:rgba(56, 139, 253, 0.15); border:1px solid #388bfd; padding:12px; border-radius:6px; margin-bottom:20px; color:#58a6ff;'><strong>Matched Sector:</strong> {matched_key} (HS: {results['hs_code']})<br><small style='color:#c9d1d9;'>{rationale}</small></div>", unsafe_allow_html=True)
                    
                    # Sleek Layout Cards
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        st.markdown(f'<div class="premium-card"><div class="card-label">Import Duty</div><div class="card-value">₵ {results["import_duty_ghs"]:,}</div></div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="premium-card"><div class="card-label">Unified VAT (15%)</div><div class="card-value">₵ {results["vat_ghs"]:,}</div></div>', unsafe_allow_html=True)
                    with m_col2:
                        combined_port_levies = round(results["other_levies_ghs"] + results["nhil_ghs"] + results["getfund_ghs"], 2)
                        st.markdown(f'<div class="premium-card"><div class="card-label">Port Fees & Statutory Levies</div><div class="card-value">₵ {combined_port_levies:,}</div></div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="premium-card-total"><div class="card-label" style="color:#10b981;">Total Estimated Obligations</div><div class="card-value-highlight">₵ {results["final_total_ghs"]:,}</div></div>', unsafe_allow_html=True)
                    
                    # Update History Records
                    log_entry = {
                        "Cargo Manifest": manifest_raw[:35] + "...",
                        "Assigned Category": matched_key,
                        "CIF Base Value": f"₵ {results['cif_ghs']:,}",
                        "Total Port Cost": f"₵ {results['total_taxes_ghs']:,}"
                    }
                    st.session_state.history.insert(0, log_entry)
                else:
                    st.error("AI engine layout classification mapping error. Please clarify your item descriptions.")
            except Exception as e:
                st.error(f"Engine Processing Interruption: {e}")
    else:
        st.markdown('<div style="color:#8b949e; text-align:center; padding-top:100px; font-size:15px;">📥 Enter parameters and select Run Engine to trigger live pricing data cards.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Session Log Execution View
st.divider()
st.markdown('<h3 style="font-size:18px;color:#f0f6fc;margin-bottom:15px;">🗄️ Recent Assessments (Session Memory)</h3>', unsafe_allow_html=True)
if st.session_state.history:
    st.markdown('<div class="responsive-table">', unsafe_allow_html=True)
    st.table(st.session_state.history[:3])
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.caption("Active workspace memory log is currently empty.")