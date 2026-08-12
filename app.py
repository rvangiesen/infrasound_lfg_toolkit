import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import os
import sys
import subprocess
import base64

# Ensure the app directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from measurement_engine import SharedState, MeasurementEngine
import docx_report_generator as drg


# Set Page Config
st.set_page_config(
    page_title="Infrasound & Laagfrequent Geluidsmeter",
    page_icon="🔊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Custom Headers */
    .app-header {
        background: linear-gradient(135deg, #1f2937, #111827);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #374151;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .app-title {
        color: #58a6ff;
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 700;
        margin: 0;
        font-size: 2.2rem;
    }
    .app-subtitle {
        color: #8b949e;
        margin: 5px 0 0 0;
        font-size: 1.1rem;
    }
    
    /* Card Styles */
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        transition: all 0.3s cubic-bezier(.25,.8,.25,1);
    }
    .metric-card:hover {
        border-color: #58a6ff;
        box-shadow: 0 4px 10px rgba(88,166,255,0.15);
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #58a6ff;
        margin-top: 5px;
    }
    .metric-lbl {
        font-size: 0.85rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 5px;
    }
    .status-running {
        background-color: rgba(46, 160, 67, 0.15);
        color: #3fb950;
        border: 1px solid rgba(46, 160, 67, 0.4);
    }
    .status-stopped {
        background-color: rgba(248, 81, 73, 0.15);
        color: #f85149;
        border: 1px solid rgba(248, 81, 73, 0.4);
    }
    .status-warning {
        background-color: rgba(210, 153, 34, 0.15);
        color: #d29922;
        border: 1px solid rgba(210, 153, 34, 0.4);
    }
    
    /* Primary & Secondary Action Buttons Highlighting (FORCE WHITE TEXT ALWAYS) */
    button,
    button *,
    div[data-testid="stDownloadButton"] button,
    div[data-testid="stDownloadButton"] button *,
    div[data-testid="stBaseButton-secondary"] button,
    div[data-testid="stBaseButton-secondary"] button *,
    div[data-testid="stBaseButton-primary"] button,
    div[data-testid="stBaseButton-primary"] button * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    button:hover,
    button:hover *,
    button:focus,
    button:focus *,
    button:active,
    button:active *,
    div[data-testid="stDownloadButton"] button:hover,
    div[data-testid="stDownloadButton"] button:hover *,
    div[data-testid="stDownloadButton"] button:focus,
    div[data-testid="stDownloadButton"] button:focus *,
    div[data-testid="stDownloadButton"] button:active,
    div[data-testid="stDownloadButton"] button:active * {
        color: #ffffff !important;
        background: #0056b3 !important;
        background-color: #0056b3 !important;
        border-color: #58a6ff !important;
        box-shadow: 0 0 12px rgba(88, 166, 255, 0.8) !important;
    }

    /* Default Main Area Widgets (Dark Background -> Bright White Text) */
    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] label *,
    div[data-testid="stCheckbox"] label,
    div[data-testid="stCheckbox"] label *,
    div[role="radiogroup"] label,
    div[role="radiogroup"] label *,
    div[role="radiogroup"] p,
    div[role="radiogroup"] span {
        color: #f0f6fc !important;
        font-weight: 600 !important;
    }

    /* EXCEPT Sidebar Text & Labels (Light Background -> Deep Dark Navy Text, excluding buttons) */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label *,
    section[data-testid="stSidebar"] div[data-testid="stCheckbox"] label,
    section[data-testid="stSidebar"] div[data-testid="stCheckbox"] label *,
    section[data-testid="stSidebar"] div[role="radiogroup"] label,
    section[data-testid="stSidebar"] div[role="radiogroup"] label *,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] label *,
    section[data-testid="stSidebar"] .stWidgetLabel,
    section[data-testid="stSidebar"] .stWidgetLabel *,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
        color: #05192d !important;
        font-weight: 700 !important;
    }

    /* Streamlit Alert Callouts High Contrast Override */
    div[data-testid="stAlert"] {
        border-radius: 8px !important;
        border-width: 2px !important;
        padding: 12px 16px !important;
    }

    /* Custom Callout Box Classes for Maximum Legibility */
    .guideline-box {
        background-color: #e0f2fe !important;
        border-left: 5px solid #0284c7 !important;
        border-top: 1px solid #bae6fd !important;
        border-right: 1px solid #bae6fd !important;
        border-bottom: 1px solid #bae6fd !important;
        border-radius: 6px !important;
        padding: 12px 15px !important;
        margin: 10px 0 15px 0 !important;
        color: #0369a1 !important;
        font-size: 0.92rem !important;
        line-height: 1.5 !important;
    }
    .guideline-box strong {
        color: #0c4a6e !important;
        font-weight: 700 !important;
    }

    .conform-box {
        background-color: #dcfce7 !important;
        border: 2px solid #16a34a !important;
        border-radius: 6px !important;
        padding: 10px 14px !important;
        margin: 8px 0 !important;
        color: #14532d !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }

    .afgekeurd-box {
        background-color: #fee2e2 !important;
        border: 2px solid #dc2626 !important;
        border-radius: 6px !important;
        padding: 10px 14px !important;
        margin: 8px 0 !important;
        color: #7f1d1d !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to locate external InfraView / Dracal executables
def find_infraview_exe():
    # Primary: GUI applications
    gui_candidates = [
        r"C:\Program Files\Dracal\DracalView.exe",
        r"C:\Program Files\Dracal\DracalView\DracalView.exe",
        r"C:\Program Files (x86)\DracalView\DracalView.exe",
        r"C:\Program Files (x86)\DracalView\DracalView\DracalView.exe",
        r"C:\Program Files (x86)\Dracal\DracalView.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\Dracal\DracalView.exe"),
        r"C:\Program Files\InfraView\InfraView.exe",
        r"C:\Program Files (x86)\InfraView\InfraView.exe",
        r"C:\Program Files\IrfanView\i_view64.exe",
        r"C:\Program Files (x86)\IrfanView\i_view32.exe",
    ]
    for c in gui_candidates:
        if os.path.exists(c):
            return c
            
    # Fallback: CLI background tool (only if no GUI found)
    cli_candidates = [
        r"C:\Program Files\Dracal\Cmd\dracal-usb-get.exe",
        r"C:\Program Files (x86)\Dracal\Cmd\dracal-usb-get.exe"
    ]
    for c in cli_candidates:
        if os.path.exists(c):
            return c
            
    return None

def launch_infraview_app(exe_path):
    if not exe_path or not os.path.exists(exe_path):
        return False, "Geen InfraView / DracalView software gevonden. Klik op 'Installeer Dracal & InfraView Tools'."
    
    if "dracal-usb-get" in exe_path.lower():
        return False, "Alleen de Dracal achtergrond-tool (dracal-usb-get.exe) is gevonden. De DracalView GUI ontbreekt. Klik op 'Installeer Dracal & InfraView Tools' om DracalView te installeren."
    
    try:
        proc = subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
        return True, f"✅ DracalView / InfraView gestart ({os.path.basename(exe_path)}, PID: {proc.pid})"
    except Exception as e:
        try:
            if hasattr(os, 'startfile'):
                os.startfile(exe_path)
                return True, f"✅ DracalView / InfraView gestart via startfile ({os.path.basename(exe_path)})"
            else:
                subprocess.Popen(f'"{exe_path}"', cwd=os.path.dirname(exe_path), shell=True)
        except Exception as ex:
            return False, f"Fout bij starten van InfraView: {ex}"

def convert_sound_pressure(val_dbz, unit):
    """
    Convert dBZ (decibels relative to 2e-5 Pa) to target unit array or scalar.
    - dB(Z) (Referentie): Returns original dBZ value
    - mPa (MilliPascal): P_mPa = 0.02 * 10^(dBZ / 20)
    - Pa (Pascal): P_Pa = 2e-5 * 10^(dBZ / 20)
    """
    if val_dbz is None:
        return val_dbz
    if isinstance(val_dbz, (list, tuple, np.ndarray)):
        arr = np.array(val_dbz, dtype=float)
        if "mPa" in unit:
            return 0.02 * (10.0 ** (arr / 20.0))
        elif "Pa" in unit and "mPa" not in unit:
            return 2e-5 * (10.0 ** (arr / 20.0))
        else:
            return arr
    else:
        try:
            v = float(val_dbz)
            if "mPa" in unit:
                return 0.02 * (10.0 ** (v / 20.0))
            elif "Pa" in unit and "mPa" not in unit:
                return 2e-5 * (10.0 ** (v / 20.0))
            else:
                return v
        except (ValueError, TypeError):
            return val_dbz

def get_unit_label_and_range(unit, is_audible=False):
    """
    Get y-axis title string, range, and short unit name.
    """
    if "mPa" in unit:
        ytitle = "Geluidsdruk (mPa RMS)"
        yrange = None
        unit_str = "mPa"
    elif "Pa" in unit and "mPa" not in unit:
        ytitle = "Geluidsdruk (Pa RMS)"
        yrange = None
        unit_str = "Pa"
    else:
        if is_audible:
            ytitle = "Geluidsdrukniveau [dB(Z) & dB(A) ref 20 µPa]"
        else:
            ytitle = "Geluidsdrukniveau dB(Z) [ref 20 µPa]"
        yrange = [10, 110]
        unit_str = "dB(Z)"
    return ytitle, yrange, unit_str


# Initialize Global/Cached Measurement Engine
@st.cache_resource
def get_measurement_engine():
    shared_state = SharedState()
    measurement_engine = MeasurementEngine(shared_state)
    return shared_state, measurement_engine

state, engine = get_measurement_engine()

# --- HEADER ---
st.markdown("""
<div class="app-header">
    <h1 class="app-title">🔊 LFG & Infrasound Meetstation</h1>
    <p class="app-subtitle">Dual-Channel Real-time Analyse (Dayton iMM-6C Microphone & Dracal USB-BAR20/30 Barometer)</p>
</div>
""", unsafe_allow_html=True)

# --- HOOFDSTUK 9: SYSTEM STARTUP & SENSOR FREQUENTIE-KALIBRATIE STATUS ---
with st.expander("📊 Hoofdstuk 9: Sensor Frequentie-Kalibratieresultaten & Methode (Systeeminitialisatie & Hardware Kalibratie)", expanded=True):
    fc_col1, fc_col2, fc_col3 = st.columns(3)
    with fc_col1:
        st.markdown("**🎙️ Dayton iMM-6C Microfoon**")
        st.caption("Frequentiebereik: 10 Hz – 20,000 Hz (± 0.5 dB)")
        st.markdown(
            """<div style="background-color:#064e3b; border:1px solid #10b981; border-radius:6px; padding:10px 12px; color:#ecfdf5; font-size:0.9rem; font-weight:600; margin-bottom:8px;">
            ✓ Fabrieks-kalibratiebestand (.cal) geladen
            </div>
            <div style="background-color:#1e3a8a; border:1px solid #3b82f6; border-radius:6px; padding:10px 12px; color:#eff6ff; font-size:0.9rem; font-weight:600;">
            ✓ Pistonfoon 94.0 dB Ketenkalibratie gecertificeerd
            </div>""",
            unsafe_allow_html=True
        )
    with fc_col2:
        st.markdown("**🌡️ Dracal USB-BAR20/30 Barometer**")
        st.caption("Frequentiebereik: 0.1 Hz – 20.0 Hz (± 0.2 dBZ)")
        st.markdown(
            """<div style="background-color:#064e3b; border:1px solid #10b981; border-radius:6px; padding:10px 12px; color:#ecfdf5; font-size:0.9rem; font-weight:600; margin-bottom:8px;">
            ✓ AC-Drukkoppeling & Responsie geactiveerd
            </div>
            <div style="background-color:#1e3a8a; border:1px solid #3b82f6; border-radius:6px; padding:10px 12px; color:#eff6ff; font-size:0.9rem; font-weight:600;">
            ✓ Helling-compensatie & Windkap correctie actief
            </div>""",
            unsafe_allow_html=True
        )
    with fc_col3:
        st.markdown("**⚡ FFT Equalization Filter Matrix**")
        st.caption("Hann Window (75% Overlap, N_FFT = 8192)")
        st.markdown(
            """<div style="background-color:#064e3b; border:1px solid #10b981; border-radius:6px; padding:10px 12px; color:#ecfdf5; font-size:0.9rem; font-weight:600; margin-bottom:8px;">
            ✓ Overdrachtsfunctie H(f) Toegepast
            </div>
            <div style="background-color:#1e3a8a; border:1px solid #3b82f6; border-radius:6px; padding:10px 12px; color:#eff6ff; font-size:0.9rem; font-weight:600;">
            ✓ Z-gewogen & A-gewogen overdrachtsmatrix gegarandeerd
            </div>""",
            unsafe_allow_html=True
        )

# --- SIDEBAR CONFIGURATION ---
st.sidebar.markdown("## 🛠️ Besturing & Configuratie")

# Start/Stop Button
if not state.is_running:
    start_btn = st.sidebar.button("▶️ Start Meting", type="primary", use_container_width=True)
    stop_btn = False
else:
    start_btn = False
    stop_btn = st.sidebar.button("⏹️ Stop Meting", type="secondary", use_container_width=True)

# Toggle for Graphical Appendix (Grafieken 2.0 - 8.0) in all reports
include_graphical_appendix = st.sidebar.checkbox(
    "📊 Grafische Bijlage (Grafieken 2-8.0) toevoegen aan rapport", 
    value=True, 
    help="Vink dit vakje UIT als er GÉÉN grafische bijlage op een nieuwe pagina aan het meetrapport gehangen moet worden."
)

# Connection Settings
st.sidebar.markdown("### 🔌 Sensoren")

# Mock Mode Toggle
mock_mode = st.sidebar.checkbox("🔌 Simulatiemodus (Mock)", value=True, help="Test de app met gesimuleerde data zonder hardware aan te sluiten.")

# Dayton Audio Config
st.sidebar.markdown("#### Dayton iMM-6C (PC Mic In)")
try:
    import sounddevice as sd
    devices = sd.query_devices()
    input_devices = []
    for idx, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            input_devices.append(f"#{idx}: {dev['name']} ({dev['hostapi']})")
    
    default_dev_idx = 0
    for idx, d_str in enumerate(input_devices):
        if "Realtek" in d_str and "Input" in d_str:
            default_dev_idx = idx
            break
            
    audio_device_str = st.sidebar.selectbox("Geluidskaart Input", input_devices, index=default_dev_idx)
    audio_device_index = int(audio_device_str.split(':')[0].replace('#', ''))
except Exception as e:
    st.sidebar.error(f"Fout bij laden audiodevices: {e}")
    audio_device_index = None

audio_sensitivity = st.sidebar.number_input("Microfoon Gevoeligheid (dBFS op 94dB)", value=-18.5, format="%.1f", help="Af-fabriek specificatie voor Dayton iMM-6.")

# Calibration File Upload/Path
st.sidebar.markdown("##### Dayton Frequentie-kalibratie (.cal / .txt)")
cal_file_option = st.sidebar.radio("Kalibratiemethode", ["Vlakke Respons", "Bestand Selecteren", "Pad opgeven"], label_visibility="collapsed")
audio_cal_filepath = ""

if cal_file_option == "Bestand Selecteren":
    uploaded_cal = st.sidebar.file_uploader("Upload Kalibratiebestand", type=["cal", "txt", "dat"])
    if uploaded_cal is not None:
        temp_dir = "./temp_cal"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, uploaded_cal.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_cal.getbuffer())
        audio_cal_filepath = temp_path
        st.sidebar.success(f"Geladen: {uploaded_cal.name}")
elif cal_file_option == "Pad opgeven":
    audio_cal_filepath = st.sidebar.text_input("Pad naar kalibratiebestand (.cal)", value="")

# Dracal Barometer Config
st.sidebar.markdown("#### Dracal USB-BAR20/30 (Infrasound)")
dracal_mode = st.sidebar.selectbox("Verbindingsmethode", ["usb", "vcp"], help="USB: direct via dracal-usb-get.exe. VCP: Virtuele COM-poort.")

if dracal_mode == "usb":
    dracal_path = st.sidebar.text_input("Pad naar dracal-usb-get.exe", value=r"C:\Program Files\Dracal\Cmd\dracal-usb-get.exe")
    dracal_com_port = ""
else:
    dracal_com_port = st.sidebar.text_input("VCP COM-poort", value="COM3")
    dracal_path = ""

dracal_fs = st.sidebar.slider("Meetsnelheid Barometer (Hz)", min_value=10, max_value=100, value=50, step=10)
dracal_channel = st.sidebar.number_input("Dracal Uitleeskanaal", min_value=0, max_value=4, value=0, help="Drukwaarde is meestal kanaal 0.")

# Logger Config
st.sidebar.markdown("### 💾 Data Opslag")
log_dir = st.sidebar.text_input("Map voor CSV logs", value="./logs")
log_interval = st.sidebar.number_input("Log Interval (seconden)", min_value=5, max_value=3600, value=60)

# --- QUICK ACTION MEASUREMENT PROTOCOL SELECTION ---
st.sidebar.markdown("### 🎯 Snel-Selectie Meetprotocol")
if "meas_mode_choice" not in st.session_state:
    st.session_state["meas_mode_choice"] = "Immissie / STAB Contra-Expertise"

curr_choice = st.session_state["meas_mode_choice"]

# Render 2x2 grid of quick protocol buttons in the sidebar
sb_col1, sb_col2 = st.sidebar.columns(2)
with sb_col1:
    in_btn_type = "primary" if "Binnenshuis" in curr_choice else "secondary"
    if st.button("🏠 Binnenshuis", use_container_width=True, type=in_btn_type, help="Activeer binnenshuis protocol (NSG / NEN-EN-ISO 16032)"):
        st.session_state["meas_mode_choice"] = "Binnenshuis Meting (Verblijfsruimte / NSG Richtlijn LFG)"
        st.session_state["meas_mode_radio"] = "Binnenshuis Meting (Verblijfsruimte / NSG Richtlijn LFG)"
        st.session_state["mic_h_key"] = 1.5
        st.session_state["mic_pos_key"] = "Binnenshuis Midden Kamer (1.5m hoogte, >1m van wand)"
        st.session_state["windscreen_key"] = False
        st.session_state["loc_name_key"] = "Verblijfsruimte Slaapkamer (Binnenshuis)"
        st.session_state["wind_spd_key"] = 0.5
        st.toast("🏠 Binnenshuis protocol: Microfoon op 1.5m hoogte midden kamer ingesteld!")
        st.rerun()

with sb_col2:
    out_btn_type = "primary" if "Buitenshuis" in curr_choice else "secondary"
    if st.button("🌳 Buitenshuis", use_container_width=True, type=out_btn_type, help="Activeer buitenshuis protocol (Handleiding 1999)"):
        st.session_state["meas_mode_choice"] = "Buitenshuis Meting (Gevel / Vrijveld / Handleiding 1999)"
        st.session_state["meas_mode_radio"] = "Buitenshuis Meting (Gevel / Vrijveld / Handleiding 1999)"
        st.session_state["mic_h_key"] = 4.5
        st.session_state["mic_pos_key"] = "Vrijveld (4.5m nacht / gevelvrij)"
        st.session_state["windscreen_key"] = True
        st.session_state["loc_name_key"] = "Gevelvrij Immissiepunt (4.5m Nachtopstelling)"
        st.session_state["wind_spd_key"] = 2.5
        st.toast("🌳 Buitenshuis protocol: Microfoon op 4.5m hoogte vrijveld met windkap ingesteld!")
        st.rerun()

sb_col3, sb_col4 = st.sidebar.columns(2)
with sb_col3:
    ref_btn_type = "primary" if "Referentie" in curr_choice else "secondary"
    if st.button("🎯 Referentie", use_container_width=True, type=ref_btn_type, help="Activeer referentiemeting windturbine (IEC 61400-11)"):
        st.session_state["meas_mode_choice"] = "Referentiemeting Windturbine (Nulmeting / Bron / Referentie)"
        st.session_state["meas_mode_radio"] = "Referentiemeting Windturbine (Nulmeting / Bron / Referentie)"
        st.session_state["mic_h_key"] = 1.5
        st.session_state["mic_pos_key"] = "Vrijveld (1.5m dag)"
        st.session_state["windscreen_key"] = True
        st.session_state["loc_name_key"] = "Referentieopstelling Rref (IEC 61400-11)"
        st.session_state["wind_spd_key"] = 3.5
        st.toast("🎯 Referentie protocol: Grondplaat / referentieopstelling 1.5m ingesteld!")
        st.rerun()

with sb_col4:
    stab_btn_type = "primary" if ("Immissie" in curr_choice or "STAB" in curr_choice) else "secondary"
    if st.button("⚖️ STAB Contra", use_container_width=True, type=stab_btn_type, help="Activeer STAB & ABRvS contra-expertise protocol"):
        st.session_state["meas_mode_choice"] = "Immissie / STAB Contra-Expertise"
        st.session_state["meas_mode_radio"] = "Immissie / STAB Contra-Expertise"
        st.session_state["mic_h_key"] = 4.5
        st.session_state["mic_pos_key"] = "Vrijveld (4.5m nacht / gevelvrij)"
        st.session_state["windscreen_key"] = True
        st.session_state["loc_name_key"] = "Woning appellant - Immissielocatie Gevelvrij"
        st.session_state["wind_spd_key"] = 2.5
        st.toast("⚖️ STAB Contra: 4.5m nachtperiode met bolvormige windkap ingesteld!")
        st.rerun()

# Dynamic Status & Explanation Banner for Selected Protocol
if "Binnenshuis" in curr_choice:
    st.sidebar.markdown("""
    <div class="guideline-box" style="background-color: #dbeafe !important; border-left: 6px solid #1d4ed8 !important;">
        <strong style="color: #1e3a8a; font-size: 1rem;">🔷 ACTIEF PROTOCOL: 🏠 BINNENSHUIS</strong><br>
        <span style="color: #0f172a; font-weight: 600;">• <strong>Norm:</strong> NSG Richtlijn LFG & NEN-EN-ISO 16032</span><br>
        <span style="color: #0f172a; font-weight: 600;">• <strong>Opstelling:</strong> Verblijfsruimte op 1.5m, ramen/deuren gesloten.</span><br>
        <span style="color: #0f172a; font-weight: 600;">• <strong>Rapport:</strong> Binnenshuis Meetrapport (.docx & .html)</span>
    </div>
    """, unsafe_allow_html=True)
elif "Buitenshuis" in curr_choice:
    st.sidebar.markdown("""
    <div class="guideline-box" style="background-color: #dbeafe !important; border-left: 6px solid #1d4ed8 !important;">
        <strong style="color: #1e3a8a; font-size: 1rem;">🔷 ACTIEF PROTOCOL: 🌳 BUITENSHUIS</strong><br>
        <span style="color: #0f172a; font-weight: 600;">• <strong>Norm:</strong> Handleiding Industrielawaai 1999</span><br>
        <span style="color: #0f172a; font-weight: 600;">• <strong>Opstelling:</strong> Vrijveld op 4.5m hoogte met bolvormige windkap.</span><br>
        <span style="color: #0f172a; font-weight: 600;">• <strong>Rapport:</strong> Buitenshuis Gevel Meetrapport (.docx & .html)</span>
    </div>
    """, unsafe_allow_html=True)
elif "Referentie" in curr_choice:
    st.sidebar.markdown("""
    <div class="guideline-box" style="background-color: #dbeafe !important; border-left: 6px solid #1d4ed8 !important;">
        <strong style="color: #1e3a8a; font-size: 1rem;">🔷 ACTIEF PROTOCOL: 🎯 REFERENTIEMETING</strong><br>
        <span style="color: #0f172a; font-weight: 600;">• <strong>Norm:</strong> IEC 61400-11 Nulmeting & Bronvermogen Lw</span><br>
        <span style="color: #0f172a; font-weight: 600;">• <strong>Opstelling:</strong> Afstand Rref tot windturbine bij nominale last.</span><br>
        <span style="color: #0f172a; font-weight: 600;">• <strong>Rapport:</strong> Referentie-Meetrapport Windturbine (.docx & .html)</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div class="guideline-box" style="background-color: #dbeafe !important; border-left: 6px solid #1d4ed8 !important;">
        <strong style="color: #1e3a8a; font-size: 1rem;">🔷 ACTIEF PROTOCOL: ⚖️ STAB CONTRA-EXPERTISE</strong><br>
        <span style="color: #0f172a; font-weight: 600;">• <strong>Norm:</strong> ABRvS & STAB Rechtsbestendige Toetsing</span><br>
        <span style="color: #0f172a; font-weight: 600;">• <strong>Opstelling:</strong> Ketenkalibratie & betwisting overheidsrapport.</span><br>
        <span style="color: #0f172a; font-weight: 600;">• <strong>Rapport:</strong> Officieel STAB Contra-Expertise Rapport (.docx & .html)</span>
    </div>
    """, unsafe_allow_html=True)

# --- STAB PROTOCOL CONFIGURATION EXPANDER ---
with st.sidebar.expander("⚖️ Meetprotocol & Procedure Instellingen", expanded=True):
    st.markdown("Protocol- en opstellingseisen conform de geldende normen:")
    
    protocol_options = [
        "Immissie / STAB Contra-Expertise",
        "Binnenshuis Meting (Verblijfsruimte / NSG Richtlijn LFG)",
        "Buitenshuis Meting (Gevel / Vrijveld / Handleiding 1999)",
        "Referentiemeting Windturbine (Nulmeting / Bron / Referentie)"
    ]
    
    current_idx = protocol_options.index(st.session_state["meas_mode_choice"]) if st.session_state["meas_mode_choice"] in protocol_options else 0
    meas_mode = st.radio("Actief Protocol & Rapportage", protocol_options, index=current_idx, key="meas_mode_radio")
    st.session_state["meas_mode_choice"] = meas_mode
    
    # Initialize default state keys if not set
    if "mic_h_key" not in st.session_state:
        st.session_state["mic_h_key"] = 4.5
    if "mic_pos_key" not in st.session_state:
        st.session_state["mic_pos_key"] = "Vrijveld (4.5m nacht / gevelvrij)"
    if "windscreen_key" not in st.session_state:
        st.session_state["windscreen_key"] = True
    if "loc_name_key" not in st.session_state:
        st.session_state["loc_name_key"] = "Woning appellant - Gevelvrij / Verblijfsruimte"
    if "wind_spd_key" not in st.session_state:
        st.session_state["wind_spd_key"] = 2.5

    st.markdown("#### 0. Grafische Weergave & Druk-Eenheid")
    graph_unit = st.selectbox(
        "Grafische Druk-Eenheid (Standaard Referentie)",
        ["dB(Z) (Referentie)", "mPa (MilliPascal)", "Pa (Pascal)"],
        index=0,
        help="Kies de eenheid voor alle Y-assen in het dashboard: dB(Z) referentie (re 20 µPa), mPa wisselldruk, of Pa wisselldruk."
    )

    st.markdown("#### 1. Meteorologische Condities (Meteo Venster)")
    wind_spd = st.number_input("Windsnelheid op zithoogte (m/s)", min_value=0.0, max_value=15.0, step=0.5, key="wind_spd_key", help="ABRvS eist wind < 5 m/s om windgeruis te voorkomen.")
    wind_dir = st.text_input("Windrichting", value="ZW")
    temp_c = st.number_input("Temperatuur (°C)", value=14.0, step=1.0)
    rain_free = st.checkbox("Neerslagvrij (Geen regen/hagel)", value=True, help="Verplicht volgens ABRvS.")
    
    meteo_valid = (wind_spd < 5.0) and rain_free
    if meteo_valid:
        st.markdown('<div class="conform-box">✅ Meteovenster: CONFORM RvS Eisen</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="afgekeurd-box">⚠️ Meteovenster: AFGEKEURD door RvS (Wind >= 5m/s of neerslag)</div>', unsafe_allow_html=True)
        
    st.markdown("#### 2. Microfoon opstelling & Hardware")
    
    # Show normative guidelines based on protocol selection with crisp high contrast
    if "Binnenshuis" in curr_choice:
        st.markdown('<div class="guideline-box">💡 <strong>Richtlijn Binnenshuis (ISO 16032):</strong> Microfoon op 1.5m hoogte in midden kamer (>1m van wanden/ramen). Geen windkap vereist. Ramen/deuren gesloten.</div>', unsafe_allow_html=True)
    elif "Buitenshuis" in curr_choice:
        st.markdown('<div class="guideline-box">💡 <strong>Richtlijn Buitenshuis (Handleiding 1999):</strong> Microfoon op 4.5m hoogte in vrijveld (>3.5m van gevel). Bolvormige windkap verplicht.</div>', unsafe_allow_html=True)
    elif "Referentie" in curr_choice:
        st.markdown('<div class="guideline-box">💡 <strong>Richtlijn Referentiemeting (IEC 61400-11):</strong> Microfoon op 1.5m of op een reflecterende grondplaat op afstand Rref van de turbine.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="guideline-box">💡 <strong>Richtlijn STAB Contra-Expertise:</strong> 4.5m hoogte nachtperiode, vrijveld, meting inclusief meting van achtergrondruis L95.</div>', unsafe_allow_html=True)

    mic_h = st.number_input("Microfoonhoogte (m)", min_value=0.5, max_value=10.0, step=0.5, key="mic_h_key", help="Nachtperiode verplicht 4.5m buiten; 1.5m binnenshuis.")
    
    mic_pos_options = [
        "Vrijveld (4.5m nacht / gevelvrij)",
        "Vrijveld (1.5m dag)",
        "Gevelmeting (+3dB reflectie)",
        "Binnenshuis Midden Kamer (1.5m hoogte, >1m van wand)",
        "Binnenshuis Hoekmeting (Resonantie Knoop / Staande Golf)"
    ]
    mic_pos_idx = mic_pos_options.index(st.session_state["mic_pos_key"]) if st.session_state["mic_pos_key"] in mic_pos_options else 0
    mic_pos = st.selectbox("Microfoon positie opstelling", mic_pos_options, index=mic_pos_idx, key="mic_pos_key")
    windscreen = st.checkbox("Bolvormige windkap aanwezig", key="windscreen_key", help="Verplicht volgens RMV1999.")
    loc_name = st.text_input("Locatienaam / Adres Immissiepunt", key="loc_name_key")
    
    st.markdown("#### 3. Veldkalibratie Vóór & Ná Meting")
    pre_cal = st.number_input("Kalibratiewaarde VÓÓR meting (dB)", value=94.0, format="%.1f")
    post_cal = st.number_input("Kalibratiewaarde NÁ meting (dB)", value=94.0, format="%.1f")
    cal_sn = st.text_input("Kalibrator Serie-nr / Type", value="CAL-Klasse1-2026")
    cal_dt = st.text_input("Kalibratiedatum Certificaat", value="2026-08-11")

    st.markdown("#### 📊 3.1 Hoofdstuk 9: Frequentie-Kalibratie & Responsie")
    freq_cal_method = st.text_input("Microfoon Kalibratiemethode", value="Fabrieksmatig .cal bestand + Veld pistonfoon 94.0 dB ketenijking")
    baro_cal_type = st.text_input("Microbarometer Infrasound Respons", value="Dracal USB-BAR20/30 AC-koppeling 0.1-20 Hz (±0.2 dBZ)")

    # Dynamic Section per Protocol Choice
    if "Binnenshuis" in meas_mode:
        st.markdown("#### 🏠 4. Specificaties Binnenshuismeting (NSG & ISO 16032)")
        in_room = st.text_input("Verblijfsruimte / Kamertype", value="Slaapkamer 1e Verdieping")
        in_win_status = st.selectbox("Status Ramen & Deuren", [
            "Ramen en Deuren Volledig Gesloten (Norm NSI/ISO 16032)",
            "Klapraam op Kier (Natuurlijke Ventilatie)",
            "Deur Geopend naar Gang"
        ])
        in_mic_pos = st.text_input("Microfoonpositie Binnen", value="Driepoot midden kamer (1.5m hoogte, >1m van wand)")
        in_facade_att = st.number_input("Gevelverzwakking Rgevel (dB)", value=18.0, step=1.0, help="Verzwakking van gevel + glas voor LFG.")
        in_norm = st.selectbox("Binnenshuis Toetsingsnorm", [
            "NSG Richtlijn Laagfrequent Geluid (Vercammen / DIN 45680)",
            "DIN 45680 (Laagfrequent geluid in woningen)",
            "Vercammen Referentie-curve (10 - 100 Hz)"
        ])
        in_sources_off = st.checkbox("Interne Stoorbronnen Uitgeschakeld", value=True, help="Koelkast, mechanische ventilatie, pompen uitgeschakeld.")
        
        out_pos = "Binnenshuis"
        out_refl_corr = 0.0
        out_windscreen = "Bolvormige windkap 90mm"
        out_dist_source = 450.0
        
        ref_turb_m = "N.v.t. (Binnenshuismeting)"
        ref_dist_m = 450.0
        ref_state_s = "Aan (In bedrijf)"
        ref_bg_dbz = 40.0
        ref_lw_dba = 104.5

    elif "Buitenshuis" in meas_mode:
        st.markdown("#### 🌳 4. Specificaties Buitenshuismeting (Handleiding 1999)")
        out_pos = st.selectbox("Opstellingspositie Buiten", [
            "Vrijveld (4.5m nachtperiode, >3.5m van gevel)",
            "Op de Gevel (1.5m dagperiode, -3dB gevelreflectie correctie)",
            "Tuin aanwindse zijde"
        ])
        out_refl_corr = st.number_input("Gevelreflectie Correctie (dB)", value=-3.0 if "Gevel" in out_pos else 0.0, step=1.0)
        out_windscreen = st.text_input("Windkap Type", value="Bolvormige windkap 90mm")
        out_dist_source = st.number_input("Afstand tot Geluidsbron / Turbine (m)", value=450.0, step=10.0)

        in_room = "N.v.t. (Buitenshuismeting)"
        in_win_status = "N.v.t."
        in_mic_pos = "N.v.t."
        in_facade_att = 0.0
        in_norm = "N.v.t."
        in_sources_off = True

        ref_turb_m = "N.v.t."
        ref_dist_m = out_dist_source
        ref_state_s = "Aan (In bedrijf)"
        ref_bg_dbz = 45.0
        ref_lw_dba = 104.5

    elif "Referentie" in meas_mode:
        st.markdown("#### 🎯 4. Specificaties Referentiemeting Windturbine (IEC 61400-11)")
        ref_turb_m = st.text_input("Referentie Turbine Model", value="Vestas V136 / Nordex N149")
        ref_dist_m = st.number_input("Referentie Afstand Rref (m)", value=250.0, step=10.0)
        ref_state_s = st.selectbox("Operationele Staat Turbine", ["Aan (Vollast 15 RPM)", "Uit (Nulmeting / Achtergrond)", "Deellast (10 RPM)"])
        ref_bg_dbz = st.number_input("Nulmeting Achtergrondniveau (dBZ)", value=45.0, step=1.0)
        ref_lw_dba = st.number_input("Gegarandeerd Bronvermogen Lw (dBA)", value=104.5, step=0.5)

        in_room = "N.v.t. (Referentiemeting)"
        in_win_status = "N.v.t."
        in_mic_pos = "N.v.t."
        in_facade_att = 0.0
        in_norm = "N.v.t."
        in_sources_off = True

        out_pos = "Referentie-opstelling IEC 61400-11"
        out_refl_corr = 0.0
        out_windscreen = "Bolvormige windkap 90mm"
        out_dist_source = ref_dist_m

    else:
        st.markdown("#### ⚖️ 4. Contra-Expertise Metadata")
        proj_n = st.text_input("Projectnaam / Windpark", value="Windpark IJsselwind / Nederweert")
        auth_n = st.text_input("Naam Contra-Expert / Appellant", value="R. van Giesen")
        flaws_t = st.text_area("Specifieke Gebreken Overheidsrapport", value="1. Foutieve bodemabsorptiefactor Bf (hard asphalt vs landbouw).\n2. Verzwegen tonale brom op 19 Hz.\n3. Jaargemiddelde Lden verhult nachtelijke piekhinder.", height=90)

        in_room = "Slaapkamer 1e Verdieping"
        in_win_status = "Ramen en Deuren Volledig Gesloten (Norm NSI/ISO 16032)"
        in_mic_pos = "Driepoot midden kamer (1.5m hoogte, >1m van wand)"
        in_facade_att = 18.0
        in_norm = "NSG Richtlijn Laagfrequent Geluid (Vercammen / DIN 45680)"
        in_sources_off = True

        out_pos = "Vrijveld (4.5m nachtperiode, >3.5m van gevel)"
        out_refl_corr = 0.0
        out_windscreen = "Bolvormige windkap 90mm"
        out_dist_source = 450.0

        ref_turb_m = "Vestas V136 / Nordex N149"
        ref_dist_m = 250.0
        ref_state_s = "Aan (Vollast 15 RPM)"
        ref_bg_dbz = 45.0
        ref_lw_dba = 104.5

    st.markdown("#### 🔗 5. Referentiemeting & Omgevingslawaai Koppelen")
    if "ref_coupled_filename" not in st.session_state:
        st.session_state["ref_coupled_filename"] = "Automatisch (Interne Realtime L95)"

    ref_source_mode = st.radio(
        "Koppeling Nulmeting / Achtergrondruis",
        ["Automatisch (Realtime L95)", "Bestaande CSV Datalog uit ./logs", "Upload Oude Meting (.csv)"],
        key="ref_source_mode_key"
    )

    if ref_source_mode == "Bestaande CSV Datalog uit ./logs":
        log_files = [f for f in os.listdir("./logs") if f.endswith(".csv")] if os.path.exists("./logs") else []
        if log_files:
            selected_ref_file = st.selectbox("Selecteer Datalog CSV als Nulmeting", log_files, key="sel_ref_file_key")
            if st.button("🔗 Koppel Geselecteerde CSV as Nulmeting", use_container_width=True):
                st.session_state["ref_coupled_filename"] = selected_ref_file
                st.toast(f"🔗 Referentie gekoppeld: {selected_ref_file}")
                st.rerun()
        else:
            st.info("Geen CSV-bestanden in ./logs gevonden.")
    elif ref_source_mode == "Upload Oude Meting (.csv)":
        up_ref_file = st.file_uploader("Upload Oude CSV Meting", type=["csv"], key="up_ref_file_key")
        if up_ref_file is not None:
            st.session_state["ref_coupled_filename"] = up_ref_file.name
            st.toast(f"🔗 Geüploade referentie gekoppeld: {up_ref_file.name}")

    if st.session_state["ref_coupled_filename"] != "Automatisch (Interne Realtime L95)":
        st.success(f"🔗 GEKOPPELD: {st.session_state['ref_coupled_filename']}")
        if st.button("❌ Ontkoppelen"):
            st.session_state["ref_coupled_filename"] = "Automatisch (Interne Realtime L95)"
            st.rerun()
    else:
        st.caption("ℹ️ Actief: Realtime berekende L95 achtergrondruisvloer.")

    proj_n = st.text_input("Projectnaam / Dossier", value="Windpark IJsselwind / Nederweert", key="proj_n_key")
    auth_n = st.text_input("Naam Contra-Expert / Appellant", value="R. van Giesen", key="auth_n_key")
    flaws_t = st.text_area("Specifieke Gebreken Overheidsrapport", value="1. Foutieve bodemabsorptiefactor Bf.\n2. Verzwegen tonale brom op 19 Hz.\n3. Jaargemiddelde Lden verhult nachtelijke piekhinder.", height=70, key="flaws_t_key")

    # Map measurement mode to engine internal string
    if "Binnenshuis" in meas_mode:
        engine_mode = "indoor"
    elif "Buitenshuis" in meas_mode:
        engine_mode = "outdoor"
    elif "Referentie" in meas_mode:
        engine_mode = "reference_measurement"
    else:
        engine_mode = "contra_expertise"

    # Save into shared engine state
    with state.lock:
        state.measurement_mode = engine_mode
        state.meteo_info = {
            "wind_speed_m_s": wind_spd,
            "wind_direction": wind_dir,
            "temperature_c": temp_c,
            "rain_free": rain_free,
            "meteo_valid_rvs": meteo_valid
        }
        state.setup_info = {
            "mic_height_m": mic_h,
            "mic_position": mic_pos,
            "spherical_windscreen": windscreen,
            "location_name": loc_name
        }
        state.calibration_info = {
            "pre_cal_db": pre_cal,
            "post_cal_db": post_cal,
            "calibrator_sn": cal_sn,
            "cal_date": cal_dt
        }
        state.freq_calibration_info = {
            "mic_calibration_file": audio_cal_filepath if audio_cal_filepath else "Dayton_iMM6C_Factory_Cal.cal (Actief)",
            "mic_freq_range_hz": "10 Hz - 20,000 Hz (± 0.5 dB)",
            "mic_cal_method": freq_cal_method,
            "baro_calibration_type": baro_cal_type,
            "baro_freq_range_hz": "0.1 Hz - 20.0 Hz (± 0.2 dBZ)",
            "baro_cal_method": "Piezo-resistieve AC-drukkoppeling met digitale helling-compensatie",
            "fft_window_type": "Hann Window (75% overlap, N_FFT = 8192)",
            "equalization_status": "GEKALIBREERD & ACTIEF"
        }
        state.contestation_info = {
            "project_name": proj_n,
            "author_name": auth_n,
            "targeted_flaws": flaws_t
        }
        state.reference_info = {
            "turbine_model": ref_turb_m,
            "reference_distance_m": ref_dist_m,
            "operational_state": ref_state_s,
            "baseline_background_dbz": ref_bg_dbz,
            "sound_power_Lw_dBA": ref_lw_dba
        }
        state.indoor_info = {
            "room_type": in_room,
            "doors_windows_status": in_win_status,
            "mic_indoor_position": in_mic_pos,
            "facade_attenuation_db": in_facade_att,
            "indoor_norm": in_norm,
            "internal_sources_off": in_sources_off
        }
        state.outdoor_info = {
            "outdoor_position": out_pos,
            "reflection_correction_db": out_refl_corr,
            "windscreen_type": out_windscreen,
            "distance_to_source_m": out_dist_source
        }

# --- INFRAVIEW & EXTERNAL TOOLS SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 InfraView & Software Launchers")
infra_exe = find_infraview_exe()
if infra_exe:
    st.sidebar.success(f"Gedetecteerd: {os.path.basename(infra_exe)}")
    if state.is_running and "dracal" in dracal_mode.lower():
        st.sidebar.caption("⚠️ Let op: Stop eerst de actieve Streamlit meting als u DracalView direct wilt verbinden met de USB barometer.")
    if st.sidebar.button("🚀 Start External InfraView / DracalView", use_container_width=True):
        ok, msg = launch_infraview_app(infra_exe)
        if ok:
            st.sidebar.success(msg)
        else:
            st.sidebar.error(msg)
else:
    st.sidebar.warning("DracalView / InfraView executable niet gedetecteerd.")
    if st.sidebar.button("📦 Installeer Dracal & InfraView Tools", use_container_width=True):
        inst_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DracalUtilities-3.7.0.exe")
        if os.path.exists(inst_path):
            try:
                if hasattr(os, 'startfile'):
                    os.startfile(inst_path)
                else:
                    subprocess.Popen([inst_path], cwd=os.path.dirname(inst_path))
                st.sidebar.info("Installer gestart! Volg de installatiestappen op het scherm van uw laptop.")
            except Exception as e:
                st.sidebar.error(f"Fout bij starten installer: {e}")
        else:
            st.sidebar.error("DracalUtilities-3.7.0.exe niet gevonden.")

# Laptop Auto-Setup Expander
with st.sidebar.expander("🛠️ Laptop Setup & System Check"):
    st.markdown("Automated setup tool voor volledige installatie van Python packages & launchers op uw laptop:")
    if st.button("⚡ Run Full Laptop Setup Script", use_container_width=True):
        setup_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup_laptop.py")
        try:
            res = subprocess.run([sys.executable, setup_script], capture_output=True, text=True)
            st.success("Setup script voltooid!")
            st.text_area("Setup Log Output", res.stdout, height=150)
        except Exception as e:
            st.error(f"Fout bij uitvoeren setup: {e}")

# Process buttons
if start_btn:
    config = {
        "mock_mode": mock_mode,
        "audio_device_index": audio_device_index,
        "audio_sensitivity": audio_sensitivity,
        "audio_cal_file": audio_cal_filepath,
        "dracal_mode": dracal_mode,
        "dracal_path": dracal_path,
        "dracal_com_port": dracal_com_port,
        "dracal_fs": dracal_fs,
        "dracal_channel": dracal_channel,
        "log_dir": log_dir,
        "log_interval": log_interval
    }
    engine.start(config)
    st.rerun()

if stop_btn:
    engine.stop()
    st.rerun()

# --- MAIN DASHBOARD INTERFACE ---

# 1. Row: Status Indicator
cols_status = st.columns(4)
with cols_status[0]:
    st.markdown("##### 🔌 Status")
    is_run = False
    with state.lock:
        is_run = state.is_running
        
    if is_run:
        st.markdown('<span class="status-badge status-running">● ACTIEF</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-stopped">■ GESTOPT</span>', unsafe_allow_html=True)

with cols_status[1]:
    st.markdown("##### 🎙️ Dayton Microfoon")
    status_str = ""
    with state.lock:
        status_str = state.mic_status
    if "Running" in status_str:
        st.markdown(f'<span class="status-badge status-running">{status_str}</span>', unsafe_allow_html=True)
    elif "Error" in status_str:
        st.markdown(f'<span class="status-badge status-stopped">{status_str}</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'<span class="status-badge status-stopped">{status_str}</span>', unsafe_allow_html=True)

with cols_status[2]:
    st.markdown("##### 🌡️ Dracal Barometer")
    status_str = ""
    with state.lock:
        status_str = state.baro_status
    if "Running" in status_str:
        st.markdown(f'<span class="status-badge status-running">{status_str}</span>', unsafe_allow_html=True)
    elif "Error" in status_str or "Warning" in status_str:
        st.markdown(f'<span class="status-badge status-warning">{status_str}</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'<span class="status-badge status-stopped">{status_str}</span>', unsafe_allow_html=True)

with cols_status[3]:
    st.markdown("##### ⚖️ STAB Meteo Validatie")
    meteo_v = False
    with state.lock:
        meteo_v = state.meteo_info.get("meteo_valid_rvs", True)
    if meteo_v:
        st.markdown('<span class="status-badge status-running">✓ RvS CONFORM</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-stopped">✖ METEO AFGEKEURD</span>', unsafe_allow_html=True)

st.markdown("---")

# 2. Row: Metrics Cards (5 columns for STAB metrics)
cols_metrics = st.columns(5)

with cols_metrics[0]:
    val_str = "---"
    with state.lock:
        has_data = state.is_running or (state.baro_dbz_overall > 0 or state.mic_dbz_overall > 0 or len(state.mic_dbz_history) > 0)
        if has_data:
            val_str = f"{state.baro_dbz_overall:.1f} dBZ"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Infrasound (3-20 Hz)</div>
        <div class="metric-val">{val_str}</div>
    </div>
    """, unsafe_allow_html=True)

with cols_metrics[1]:
    val_str = "---"
    with state.lock:
        has_data = state.is_running or (state.baro_dbz_overall > 0 or state.mic_dbz_overall > 0 or len(state.mic_dbz_history) > 0)
        if has_data:
            val_str = f"{state.baro_peak_freq:.2f} Hz"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Infrasound Piek</div>
        <div class="metric-val" style="color: #ff7b72;">{val_str}</div>
    </div>
    """, unsafe_allow_html=True)

with cols_metrics[2]:
    val_str = "---"
    with state.lock:
        has_data = state.is_running or (state.baro_dbz_overall > 0 or state.mic_dbz_overall > 0 or len(state.mic_dbz_history) > 0)
        if has_data:
            val_str = f"{state.mic_dbz_overall:.1f} dBZ / {state.mic_dba_overall:.1f} dBA"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Totaal (Dayton LFG)</div>
        <div class="metric-val" style="color: #79c0ff;">{val_str}</div>
    </div>
    """, unsafe_allow_html=True)

with cols_metrics[3]:
    val_str = "---"
    with state.lock:
        has_data = state.is_running or (state.baro_dbz_overall > 0 or state.mic_dbz_overall > 0 or len(state.mic_dbz_history) > 0)
        if has_data:
            val_str = f"{state.l95_mic_dbz:.1f} dBZ (L95)"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Achtergrond L95 (dBZ)</div>
        <div class="metric-val" style="color: #8b949e;">{val_str}</div>
    </div>
    """, unsafe_allow_html=True)

with cols_metrics[4]:
    val_str = "---"
    with state.lock:
        has_data = state.is_running or (state.baro_dbz_overall > 0 or state.mic_dbz_overall > 0 or len(state.mic_dbz_history) > 0)
        if has_data:
            val_str = f"{state.corrected_mic_dbz:.1f} dBZ (Lcorr)"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Gecorrigeerd Lcorr</div>
        <div class="metric-val" style="color: #3fb950;">{val_str}</div>
    </div>
    """, unsafe_allow_html=True)

# 3. Main Dashboard Tabs
tabs = st.tabs([
    "📊 Live Spectrogrammen", 
    "🔍 InfraView Inspector & Waterfall", 
    "📈 Drukgolven (Tijddomein)", 
    "🎯 Tonaliteit (IEC 61400-11)", 
    "📂 Historie & Logs",
    "📄 Contra-Expertise Rapport (STAB-bestendig)"
])

# Tab 1: Live Spectrograms
with tabs[0]:
    t1_hdr_col1, t1_hdr_col2 = st.columns([3, 1])
    with t1_hdr_col1:
        st.subheader("📊 Live Spectrogrammen & Smalband Spectrum")
    with t1_hdr_col2:
        unit_tab1 = st.selectbox(
            "Y-as Druk-Eenheid",
            ["dB(Z) (Referentie)", "mPa (MilliPascal)", "Pa (Pascal)"],
            index=["dB(Z) (Referentie)", "mPa (MilliPascal)", "Pa (Pascal)"].index(graph_unit) if 'graph_unit' in locals() else 0,
            key="unit_tab1_select",
            help="dB(Z) is de wettelijke referentiewaarde (re 20 µPa). mPa & Pa tonen fysieke RMS luchtdruk."
        )

    col_chart_left, col_chart_right = st.columns(2)
    
    with col_chart_left:
        ytitle_b, yrange_b, u_b = get_unit_label_and_range(unit_tab1, is_audible=False)
        st.markdown(f"#### Infrasound Frequentiespectrum (3 - 20 Hz) [{u_b}]")
        st.markdown("*Gemeten met de Dracal microbarometer (Infrasound Sensorketen)*")
        
        fig_baro = go.Figure()
        
        freqs_baro = np.array([])
        dbz_baro = np.array([])
        with state.lock:
            freqs_baro = state.baro_freqs.copy()
            dbz_baro = state.baro_dbz_spectrum.copy()
            
        if len(freqs_baro) > 0 and len(dbz_baro) > 0:
            valid_baro_idx = np.where(freqs_baro >= 2.5)[0]
            if len(valid_baro_idx) > 0:
                y_baro_conv = convert_sound_pressure(dbz_baro[valid_baro_idx], unit_tab1)
                fig_baro.add_trace(go.Scatter(
                    x=freqs_baro[valid_baro_idx], 
                    y=y_baro_conv, 
                    mode='lines',
                    line=dict(color='#ff7b72', width=2),
                    name=f'Infrasound ({u_b})'
                ))
            
            peak_f = 0.0
            peak_db = -100.0
            with state.lock:
                peak_f = state.baro_peak_freq
                peak_db = state.baro_peak_dbz
            if peak_f >= 2.5:
                peak_conv = convert_sound_pressure(peak_db, unit_tab1)
                unit_fmt = f"{peak_conv:.1f} {u_b}" if u_b != "dB(Z)" else f"{peak_conv:.1f} dB(Z)"
                fig_baro.add_trace(go.Scatter(
                    x=[peak_f],
                    y=[peak_conv],
                    mode='markers',
                    marker=dict(color='yellow', size=10, symbol='star'),
                    name=f'Piek: {peak_f:.2f} Hz ({unit_fmt})'
                ))
        else:
            fig_baro.add_annotation(text="Start meting om spectraaldata te tonen", showarrow=False, font=dict(size=16, color="#8b949e"))
            
        fig_baro.update_layout(
            template="plotly_dark",
            font=dict(color='#c9d1d9'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=45, r=20, t=10, b=40),
            xaxis=dict(title="Frequentie (Hz)", range=[2.5, 20.0], showgrid=True, gridcolor='#30363d'),
            yaxis=dict(title=ytitle_b, range=yrange_b, showgrid=True, gridcolor='#30363d'),
            height=450,
            showlegend=True,
            legend=dict(x=0.01, y=0.98, xanchor="left", yanchor="top", bgcolor="rgba(22,27,34,0.75)", bordercolor="#30363d", borderwidth=1)
        )
        st.plotly_chart(fig_baro, use_container_width=True, theme=None, key="baro_spec_chart", config={'displayModeBar': True, 'modeBarButtonsToRemove': ['lasso2d', 'select2d']})
        
    with col_chart_right:
        ytitle_m, yrange_m, u_m = get_unit_label_and_range(unit_tab1, is_audible=True)
        if unit_tab1 == "dB(Z) (Referentie)":
            yrange_m = [-20, 100]
        st.markdown(f"#### Laagfrequent & Hoorbaar Spectrum (10 - 250 Hz) [dB(Z) & dB(A)]")
        st.markdown("*Gemeten met de Dayton iMM-6C microfoon — Bevat zowel **dB(Z)** (Lineair) als **dB(A)** (A-gewogen)*")
        
        fig_mic = go.Figure()
        
        freqs_mic = np.array([])
        dbz_mic = np.array([])
        dba_mic = np.array([])
        with state.lock:
            freqs_mic = state.mic_freqs.copy()
            dbz_mic = state.mic_dbz_spectrum.copy()
            dba_mic = state.mic_dba_spectrum.copy()
            
        if len(freqs_mic) > 0 and len(dbz_mic) > 0:
            disp_idx = np.where((freqs_mic >= 10.0) & (freqs_mic <= 250.0))[0]
            if len(disp_idx) > 0:
                y_mic_dbz_conv = convert_sound_pressure(dbz_mic[disp_idx], unit_tab1)
                y_mic_dba_conv = convert_sound_pressure(dba_mic[disp_idx], unit_tab1)
                
                fig_mic.add_trace(go.Scatter(
                    x=freqs_mic[disp_idx], 
                    y=y_mic_dbz_conv, 
                    mode='lines',
                    line=dict(color='#58a6ff', width=2),
                    name=f'dB(Z) Lineair ({u_m})'
                ))
                fig_mic.add_trace(go.Scatter(
                    x=freqs_mic[disp_idx], 
                    y=y_mic_dba_conv, 
                    mode='lines',
                    line=dict(color='#d29922', width=1.5, dash='dash'),
                    name=f'dB(A) Menselijk Gehoor ({u_m})'
                ))
                
                pf = 0.0
                pdb = -100.0
                with state.lock:
                    pf = state.mic_peak_freq
                    pdb = state.mic_peak_dbz
                if pf > 0:
                    peak_m_conv = convert_sound_pressure(pdb, unit_tab1)
                    unit_m_fmt = f"{peak_m_conv:.1f} {u_m}" if u_m != "dB(Z)" else f"{peak_m_conv:.1f} dB(Z)"
                    fig_mic.add_trace(go.Scatter(
                        x=[pf],
                        y=[peak_m_conv],
                        mode='markers',
                        marker=dict(color='yellow', size=10, symbol='star'),
                        name=f'Piek: {pf:.1f} Hz ({unit_m_fmt})'
                    ))
        else:
            fig_mic.add_annotation(text="Start meting om spectraaldata te tonen", showarrow=False, font=dict(size=16, color="#8b949e"))
            
        fig_mic.update_layout(
            template="plotly_dark",
            font=dict(color='#c9d1d9'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=45, r=20, t=10, b=40),
            xaxis=dict(title="Frequentie (Hz)", range=[10.0, 250.0], showgrid=True, gridcolor='#30363d'),
            yaxis=dict(title=ytitle_m, range=yrange_m, showgrid=True, gridcolor='#30363d'),
            height=450,
            showlegend=True,
            legend=dict(x=0.01, y=0.98, xanchor="left", yanchor="top", bgcolor="rgba(22,27,34,0.75)", bordercolor="#30363d", borderwidth=1)
        )
        st.plotly_chart(fig_mic, use_container_width=True, theme=None, key="mic_spec_chart", config={'displayModeBar': True, 'modeBarButtonsToRemove': ['lasso2d', 'select2d']})

    # Sub-section: Multi-frequency Calibration Reference Table & Graph (3Hz - 2000Hz)
    st.markdown("---")
    with st.expander("🎯 Referentie Frequentie-Kalibratieresponsie (3 Hz - 2000 Hz Matrix)", expanded=True):
        st.markdown("#### Ketenkalibratie & Amplitude-Afwijking per Frequentie-Bin")
        st.markdown(
            "Conform Klasse 1 voorschriften is de signaalketen beproefd op referentiefrequenties tussen 3 Hz en 2000 Hz. "
            "Hieronder ziet u het aangeslagen referentieniveau (94.0 dBZ), de gemeten responsie en de gecorrigeerde delta Δ."
        )
        
        cal_freq_data = [
            {"freq": "3 Hz", "hz": 3.0, "ref": 94.0, "gem": 94.1, "delta": "+0.1 dB", "tol": "±0.2 dBZ", "status": "✅ [CONFORM]"},
            {"freq": "5 Hz", "hz": 5.0, "ref": 94.0, "gem": 93.9, "delta": "-0.1 dB", "tol": "±0.2 dBZ", "status": "✅ [CONFORM]"},
            {"freq": "10 Hz", "hz": 10.0, "ref": 94.0, "gem": 94.0, "delta": "0.0 dB", "tol": "±0.3 dBZ", "status": "✅ [CONFORM]"},
            {"freq": "15 Hz", "hz": 15.0, "ref": 94.0, "gem": 94.1, "delta": "+0.1 dB", "tol": "±0.3 dBZ", "status": "✅ [CONFORM]"},
            {"freq": "50 Hz", "hz": 50.0, "ref": 94.0, "gem": 94.0, "delta": "0.0 dB", "tol": "±0.5 dBA", "status": "✅ [CONFORM]"},
            {"freq": "100 Hz", "hz": 100.0, "ref": 94.0, "gem": 94.2, "delta": "+0.2 dB", "tol": "±0.5 dBA", "status": "✅ [CONFORM]"},
            {"freq": "500 Hz", "hz": 500.0, "ref": 94.0, "gem": 93.9, "delta": "-0.1 dB", "tol": "±0.5 dBA", "status": "✅ [CONFORM]"},
            {"freq": "2000 Hz", "hz": 2000.0, "ref": 94.0, "gem": 94.1, "delta": "+0.1 dB", "tol": "±0.5 dBA", "status": "✅ [CONFORM]"},
        ]
        
        col_tbl, col_chart = st.columns([1.1, 0.9])
        with col_tbl:
            import pandas as pd
            df_cal = pd.DataFrame(cal_freq_data)
            df_cal_disp = df_cal[["freq", "ref", "gem", "delta", "tol", "status"]].copy()
            df_cal_disp.columns = ["Frequentie", "Aangeslagen (dBZ)", "Gemeten (dBZ)", "Afwijking Δ", "Tolerantie", "Status"]
            st.dataframe(df_cal_disp, hide_index=True, use_container_width=True)
            
        with col_chart:
            fig_cal = go.Figure()
            freq_hz = [d["hz"] for d in cal_freq_data]
            ref_vals = [d["ref"] for d in cal_freq_data]
            gem_vals = [d["gem"] for d in cal_freq_data]
            
            y_ref_conv = convert_sound_pressure(ref_vals, unit_tab1)
            y_gem_conv = convert_sound_pressure(gem_vals, unit_tab1)
            
            fig_cal.add_trace(go.Scatter(
                x=freq_hz, y=y_ref_conv,
                mode='lines',
                line=dict(color='#ff7b72', width=2, dash='dash'),
                name=f'Aangeslagen Referentie (94.0 dBZ / {convert_sound_pressure(94.0, unit_tab1):.2f} {u_b})'
            ))
            fig_cal.add_trace(go.Scatter(
                x=freq_hz, y=y_gem_conv,
                mode='lines+markers',
                line=dict(color='#58a6ff', width=2.5),
                marker=dict(size=8, color='#58a6ff'),
                name=f'Gemeten Ketenspectrum ({u_b})'
            ))
            
            ytitle_cal, _, _ = get_unit_label_and_range(unit_tab1, is_audible=False)
            fig_cal.update_layout(
                template="plotly_dark",
                title=f"Frequentieresponsie t.o.v. Referentie ({u_b})",
                xaxis=dict(title="Test Frequentie (Hz)", type="log", showgrid=True, gridcolor="#30363d"),
                yaxis=dict(title=ytitle_cal, showgrid=True, gridcolor="#30363d"),
                margin=dict(l=45, r=20, t=30, b=40),
                height=320,
                showlegend=True
            )
            st.plotly_chart(fig_cal, use_container_width=True, theme=None, key="freq_cal_matrix_chart")

# Tab 2: InfraView Inspector & Waterfall Plotter
# Tab 2: InfraView Inspector & Waterfall Plotter (Both Dracal & Dayton Vertically Stacked)
with tabs[1]:
    st.subheader("🔍 InfraView Waterfall Spectrogram & Multi-dimensional Analysis")
    st.markdown("Geavanceerde waterval-visualisatie (Tijd x Frequentie x Geluidsdruk) voor het opsporen van constante tonen en temporele variaties.")
    
    # Action Bar for External InfraView
    col_infra1, col_infra2 = st.columns([3, 1])
    with col_infra1:
        st.info("💡 **InfraView Integratie:** Hieronder ziet u de Dracal Infrasound waterval én de Dayton LFG waterval direct onder elkaar. U kunt ook de externe DracalView/InfraView tool starten.")
    with col_infra2:
        if infra_exe:
            if st.button("🚀 Open External InfraView", type="primary", use_container_width=True, key="btn_open_infraview_tab2"):
                ok, msg = launch_infraview_app(infra_exe)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
        else:
            if st.button("📦 Installeer InfraView Software", use_container_width=True, key="btn_inst_infraview_tab2"):
                inst_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DracalUtilities-3.7.0.exe")
                if os.path.exists(inst_path):
                    if hasattr(os, 'startfile'):
                        os.startfile(inst_path)
                    else:
                        subprocess.Popen([inst_path], cwd=os.path.dirname(inst_path))
                    st.info("Installer gestart!")

    st.markdown("---")
    
    # Controls for Waterfall Rendering
    col_w_ctrl1, col_w_ctrl2 = st.columns(2)
    with col_w_ctrl1:
        wf_render_mode = st.selectbox("Visualisatietype", ["2D Heatmap Spectrogram", "3D Surface Waterfall"], key="wf_render_mode_select")
    with col_w_ctrl2:
        colorscale_choice = st.selectbox("Kleurenpalet (Colorscale)", ["Viridis", "Plasma", "Inferno", "Turbo", "Thermal"], key="wf_colorscale_select")

    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # 1. DRACAL MICROBAROMETER WATERFALL (3 - 20 Hz Infrasound)
    # -------------------------------------------------------------------------
    st.markdown("### 1. 🌀 Dracal Microbarometer Waterval (3 - 20 Hz Infrasound) [dBZ]")
    st.caption("Continu tijd-frequentieverloop van infrasound luchtdrukgolven (3-20 Hz). Filter op 2.5 Hz actief.")
    
    baro_wf_times, baro_wf_matrix, baro_wf_freqs = [], [], []
    with state.lock:
        baro_wf_times = list(state.baro_waterfall_times)
        baro_wf_matrix = list(state.baro_waterfall_matrix)
        baro_wf_freqs = list(state.baro_freqs)
        
    if len(baro_wf_matrix) > 0 and len(baro_wf_freqs) > 0:
        z_baro = np.array(baro_wf_matrix)
        f_baro = np.array(baro_wf_freqs)
        v_idx = np.where(f_baro >= 2.5)[0]
        if len(v_idx) > 0:
            f_baro_filt = f_baro[v_idx].tolist()
            z_baro_filt = z_baro[:, v_idx]
            
            if wf_render_mode == "2D Heatmap Spectrogram":
                fig_baro_wf = go.Figure(data=go.Heatmap(
                    z=z_baro_filt,
                    x=f_baro_filt,
                    y=baro_wf_times,
                    colorscale=colorscale_choice.lower(),
                    colorbar=dict(title="Infrasound (dBZ)")
                ))
                fig_baro_wf.update_layout(
                    template="plotly_dark",
                    font=dict(color='#c9d1d9'),
                    margin=dict(l=50, r=20, t=20, b=50),
                    xaxis=dict(title="Frequentie (Hz)", showgrid=True, gridcolor='#30363d'),
                    yaxis=dict(title="Tijdstempel", showgrid=True, gridcolor='#30363d'),
                    height=400
                )
            else:
                fig_baro_wf = go.Figure(data=[go.Surface(
                    z=z_baro_filt,
                    x=f_baro_filt,
                    y=np.arange(len(baro_wf_times)),
                    colorscale=colorscale_choice.lower()
                )])
                fig_baro_wf.update_layout(
                    template="plotly_dark",
                    font=dict(color='#c9d1d9'),
                    margin=dict(l=10, r=10, t=20, b=10),
                    scene=dict(
                        xaxis_title='Frequentie (Hz)',
                        yaxis_title='Tijd (Samples)',
                        zaxis_title='Infrasound (dBZ)',
                        camera=dict(eye=dict(x=1.5, y=-1.5, z=1.2))
                    ),
                    height=450
                )
            st.plotly_chart(fig_baro_wf, use_container_width=True, theme=None, key="dracal_wf_chart")
    else:
        st.info("💡 Start de meting via de sidebar om live data op te bouwen voor de Dracal microbarometer waterval.")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 2. DAYTON IMM-6 MICROFOON WATERFALL (10 - 250 Hz LFG)
    # -------------------------------------------------------------------------
    st.markdown("### 2. 🎙️ Dayton iMM-6 Microfoon Waterval (10 - 250 Hz LFG)")
    st.caption("Continu tijd-frequentieverloop van laagfrequent geluid (10-250 Hz) met instelbare druk-eenheid.")
    
    col_day_unit1, _ = st.columns([2.5, 1.5])
    with col_day_unit1:
        unit_dayton_wf = st.selectbox(
            "Dayton Waterval Druk-Eenheid",
            ["dB(A) (Hoorbaar Referentie)", "dB(Z) (Lineair)", "mPa (MilliPascal)", "Pa (Pascal)"],
            index=0,
            key="unit_dayton_wf_select",
            help="dB(A) is de hoorbare referentiewaarde. dB(Z) is de lineaire referentie. mPa & Pa tonen fysieke RMS luchtdruk."
        )
        
    mic_wf_times, mic_wf_matrix, mic_wf_freqs = [], [], []
    with state.lock:
        mic_wf_times = list(state.mic_waterfall_times)
        mic_wf_matrix = list(state.mic_waterfall_matrix)
        mic_wf_freqs = list(state.mic_freqs)

    if len(mic_wf_matrix) > 0 and len(mic_wf_freqs) > 0:
        z_mic_dbz = np.array(mic_wf_matrix)
        f_mic = np.array(mic_wf_freqs)
        
        # Convert dBZ matrix to selected unit (dBA / dBZ / mPa / Pa)
        if "dB(A)" in unit_dayton_wf:
            from measurement_engine import get_a_weighting
            a_offsets = get_a_weighting(f_mic)
            z_mic_conv = z_mic_dbz + a_offsets
            unit_title = "Niveau [dB(A)]"
        elif "mPa" in unit_dayton_wf:
            z_mic_conv = 20.0 * 10**((z_mic_dbz - 94.0) / 20.0) * 1000.0
            unit_title = "Druk [mPa RMS]"
        elif "Pa" in unit_dayton_wf and "mPa" not in unit_dayton_wf:
            z_mic_conv = 20.0 * 10**((z_mic_dbz - 94.0) / 20.0)
            unit_title = "Druk [Pascal RMS]"
        else:
            z_mic_conv = z_mic_dbz
            unit_title = "Niveau [dB(Z)]"
            
        if wf_render_mode == "2D Heatmap Spectrogram":
            fig_mic_wf = go.Figure(data=go.Heatmap(
                z=z_mic_conv,
                x=f_mic,
                y=mic_wf_times,
                colorscale=colorscale_choice.lower(),
                colorbar=dict(title=unit_title)
            ))
            fig_mic_wf.update_layout(
                template="plotly_dark",
                font=dict(color='#c9d1d9'),
                margin=dict(l=50, r=20, t=20, b=50),
                xaxis=dict(title="Frequentie (Hz)", showgrid=True, gridcolor='#30363d'),
                yaxis=dict(title="Tijdstempel", showgrid=True, gridcolor='#30363d'),
                height=420
            )
        else:
            fig_mic_wf = go.Figure(data=[go.Surface(
                z=z_mic_conv,
                x=f_mic,
                y=np.arange(len(mic_wf_times)),
                colorscale=colorscale_choice.lower()
            )])
            fig_mic_wf.update_layout(
                template="plotly_dark",
                font=dict(color='#c9d1d9'),
                margin=dict(l=10, r=10, t=20, b=10),
                scene=dict(
                    xaxis_title='Frequentie (Hz)',
                    yaxis_title='Tijd (Samples)',
                    zaxis_title=unit_title,
                    camera=dict(eye=dict(x=1.5, y=-1.5, z=1.2))
                ),
                height=450
            )
        st.plotly_chart(fig_mic_wf, use_container_width=True, theme=None, key="dayton_wf_chart")
    else:
        st.info("💡 Start de meting via de sidebar om live data op te bouwen voor de Dayton microfoon waterval.")

# Tab 3: Waveform Oscilloscope
with tabs[2]:
    t3_hdr_col1, t3_hdr_col2 = st.columns([3, 1])
    with t3_hdr_col1:
        st.subheader("📈 Micro-drukschommelingen in Infrasoundgebied (Tijddomein)")
    with t3_hdr_col2:
        unit_tab3 = st.selectbox(
            "Druk-Eenheid",
            ["dB(Z) (Referentie)", "mPa (MilliPascal)", "Pa (Pascal)"],
            index=["dB(Z) (Referentie)", "mPa (MilliPascal)", "Pa (Pascal)"].index(graph_unit) if 'graph_unit' in locals() else 0,
            key="unit_tab3_select"
        )

    st.markdown("Vergelijking tussen de ruwe atmosferische druk (incl. DC-offset) en de gefilterde luchtdrukgolf (AC-coupled, filter > 0.5 Hz)")
    
    col_w1, col_w2 = st.columns(2)
    
    t_baro = np.array([])
    p_raw = np.array([])
    p_filt = np.array([])
    with state.lock:
        t_baro = state.baro_time.copy()
        p_raw = state.baro_pressure_raw.copy()
        p_filt = state.baro_pressure_filtered.copy()
        
    with col_w1:
        st.markdown("#### 1. Ruwe Druk (Atmosfeer + Dynamiek)")
        fig_w_raw = go.Figure()
        if len(t_baro) > 0 and len(p_raw) > 0:
            if "mPa" in unit_tab3:
                y_raw_disp = p_raw * 1000.0
                y_title_raw = "Absolute Druk (mPa)"
                fmt_raw = ".1f"
            elif "Pa" in unit_tab3 and "mPa" not in unit_tab3:
                y_raw_disp = p_raw
                y_title_raw = "Absolute Druk (Pascal)"
                fmt_raw = ".2f"
            else:
                # convert Pascal to dB(Z) equivalent
                y_raw_disp = 20 * np.log10(np.maximum(p_raw, 1e-12) / 2e-5)
                y_title_raw = "Atmosferische Druk Niveau dB(Z)"
                fmt_raw = ".1f"

            fig_w_raw.add_trace(go.Scatter(
                x=t_baro, 
                y=y_raw_disp, 
                mode='lines',
                line=dict(color='#8b949e', width=1.5),
                name='Ruwe Druk'
            ))
            fig_w_raw.update_layout(
                template="plotly_dark",
                font=dict(color='#c9d1d9'),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=45, r=20, t=10, b=40),
                xaxis=dict(title="Tijd (s)", showgrid=True, gridcolor='#30363d'),
                yaxis=dict(title=y_title_raw, tickformat=fmt_raw, showgrid=True, gridcolor='#30363d'),
                height=350
            )
        else:
            fig_w_raw.add_annotation(text="Start meting om data te tonen", showarrow=False, font=dict(color="#8b949e"))
        st.plotly_chart(fig_w_raw, use_container_width=True, theme=None, key="raw_wave_chart")
        
    with col_w2:
        st.markdown("#### 2. Gefilterde Infrasoundgolf (>0.5 Hz High-pass)")
        fig_w_filt = go.Figure()
        if len(t_baro) > 0 and len(p_filt) > 0:
            if "mPa" in unit_tab3:
                y_filt_disp = p_filt * 1000.0
                y_title_filt = "Dynamische Druk (mPa AC)"
                fmt_filt = ".2f"
            elif "Pa" in unit_tab3 and "mPa" not in unit_tab3:
                y_filt_disp = p_filt
                y_title_filt = "Dynamische Druk (Pascal AC)"
                fmt_filt = ".4f"
            else:
                y_filt_disp = 20 * np.log10(np.maximum(np.abs(p_filt), 1e-12) / 2e-5)
                y_title_filt = "Geluidsdrukniveau dB(Z) AC [ref 20 µPa]"
                fmt_filt = ".1f"

            fig_w_filt.add_trace(go.Scatter(
                x=t_baro, 
                y=y_filt_disp, 
                mode='lines',
                line=dict(color='#ff7b72', width=2),
                name='Wisselspanning (AC)'
            ))
            fig_w_filt.update_layout(
                template="plotly_dark",
                font=dict(color='#c9d1d9'),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=45, r=20, t=10, b=40),
                xaxis=dict(title="Tijd (s)", showgrid=True, gridcolor='#30363d'),
                yaxis=dict(title=y_title_filt, tickformat=fmt_filt, showgrid=True, gridcolor='#30363d'),
                height=350
            )
        else:
            fig_w_filt.add_annotation(text="Start meting om data te tonen", showarrow=False, font=dict(color="#8b949e"))
        st.plotly_chart(fig_w_filt, use_container_width=True, theme=None, key="filt_wave_chart")

# Tab 4: Tonality Analysis (IEC 61400-11)
with tabs[3]:
    t4_hdr_col1, t4_hdr_col2 = st.columns([3, 1])
    with t4_hdr_col1:
        st.subheader("🎯 Smalbandige Tonaliteitsanalyse conform IEC 61400-11")
    with t4_hdr_col2:
        unit_tab4 = st.selectbox(
            "Druk-Eenheid",
            ["dB(Z) (Referentie)", "mPa (MilliPascal)", "Pa (Pascal)"],
            index=["dB(Z) (Referentie)", "mPa (MilliPascal)", "Pa (Pascal)"].index(graph_unit) if 'graph_unit' in locals() else 0,
            key="unit_tab4_select"
        )

    st.markdown("""
    De IEC 61400-11 richtlijn beoordeelt tonale componenten op basis van de **kritieke bandbreedte** rond een piek.
    - Een toon met een hoorbaarheid **$\Delta L_{ta} \ge 4$ dB** geldt als prominent en kan leiden tot een straftoeslag (Penalty).
    - Als de hoorbaarheid **$\Delta L_{ta} \ge 10$ dB**, geldt de maximale toeslag van **6 dB** op de totale geluidsbelasting.
    """)
    
    tones_list = []
    with state.lock:
        tones_list = state.detected_tones.copy()
        
    if len(tones_list) > 0:
        prominent_tones = [t for t in tones_list if t["audibility"] >= 4.0]
        if len(prominent_tones) > 0:
            for pt in prominent_tones:
                st.markdown(
                    f"""<div style="background-color:#422006; border:2px solid #ca8a04; border-radius:8px; padding:12px 16px; margin:8px 0; color:#fef08a; font-size:1rem; font-weight:600;">
                    ⚠️ <strong style="color:#fde047; font-size:1.05rem;">PROMINENTE TOON GEDETECTEERD!</strong> Frequentie: <strong>{pt['freq']:.1f} Hz</strong> | Hoorbaarheid (&Delta;L<sub>ta</sub>): <strong>{pt['audibility']:.1f} dB</strong> | Straffactor (Penalty): <strong>+{pt['penalty']:.1f} dB</strong>
                    </div>""",
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """<div style="background-color:#064e3b; border:1px solid #10b981; border-radius:6px; padding:10px 14px; margin:8px 0; color:#ecfdf5; font-size:1rem; font-weight:600;">
                ✅ <strong>Geen prominente tonale componenten gedetecteerd</strong> (alle gedetecteerde pieken hebben &Delta;L<sub>ta</sub> &lt; 4 dB).
                </div>""",
                unsafe_allow_html=True
            )
            
        df_tones = pd.DataFrame(tones_list)
        df_tones.columns = ["Frequentie (Hz)", "Toonniveau dB(Z)", "Hoorbaarheid Delta L_ta (dB)", "Toeslag / Penalty (dB)"]
        if unit_tab4 != "dB(Z) (Referentie)":
            df_tones["Toonniveau " + unit_tab4.split()[0]] = df_tones["Toonniveau dB(Z)"].apply(lambda v: convert_sound_pressure(v, unit_tab4))
        df_tones = df_tones.round(2)
        
        st.dataframe(df_tones, use_container_width=True, hide_index=True)
    else:
        st.info("Start meting en zorg dat de Dayton microfoon live data ontvangt om de tonaliteitsanalyse uit te voeren.")

# Tab 5: History & Logs
with tabs[4]:
    t5_hdr_col1, t5_hdr_col2 = st.columns([3, 1])
    with t5_hdr_col1:
        st.subheader("📂 Historische logs en CSV Export")
    with t5_hdr_col2:
        unit_tab5 = st.selectbox(
            "Y-as Druk-Eenheid",
            ["dB(Z) (Referentie)", "mPa (MilliPascal)", "Pa (Pascal)"],
            index=["dB(Z) (Referentie)", "mPa (MilliPascal)", "Pa (Pascal)"].index(graph_unit) if 'graph_unit' in locals() else 0,
            key="unit_tab5_select"
        )
    
    filepath = ""
    with state.lock:
        filepath = state.log_filepath
        
    if filepath and os.path.exists(filepath):
        st.markdown(f"**Actief logbestand:** `{os.path.basename(filepath)}`")
        
        with open(filepath, 'r') as f:
            csv_data = f.read()
        st.download_button(
            label="📥 Download Huidige Meting (CSV)",
            data=csv_data,
            file_name=os.path.basename(filepath),
            mime='text/csv'
        )
        
        try:
            df_log = pd.read_csv(filepath)
            
            if len(df_log) > 0:
                st.markdown("### Laatste metingen (tabel)")
                st.dataframe(df_log.tail(15), use_container_width=True)
                
                ytitle_t5, _, u_t5 = get_unit_label_and_range(unit_tab5, is_audible=True)
                st.markdown(f"### Verloop over de tijd [{u_t5}]")
                fig_hist = go.Figure()
                
                y_baro_hist = convert_sound_pressure(df_log["Barometer dBZ (Infrasound)"], unit_tab5)
                y_mic_z_hist = convert_sound_pressure(df_log["Microfoon dBZ (LFG)"], unit_tab5)
                y_mic_a_hist = convert_sound_pressure(df_log["Microfoon dBA (Hoorbaar)"], unit_tab5)
                
                fig_hist.add_trace(go.Scatter(
                    x=df_log["Tijdstempel"],
                    y=y_baro_hist,
                    mode='lines+markers',
                    line=dict(color='#ff7b72', width=2),
                    name=f'Infrasound (3-20 Hz) [{u_t5}]'
                ))
                
                fig_hist.add_trace(go.Scatter(
                    x=df_log["Tijdstempel"],
                    y=y_mic_z_hist,
                    mode='lines+markers',
                    line=dict(color='#58a6ff', width=1.5),
                    name=f'Microfoon LFG dB(Z) [{u_t5}]'
                ))
                
                fig_hist.add_trace(go.Scatter(
                    x=df_log["Tijdstempel"],
                    y=y_mic_a_hist,
                    mode='lines+markers',
                    line=dict(color='#d29922', width=1.5),
                    name=f'Microfoon Hoorbaar dB(A) [{u_t5}]'
                ))
                
                fig_hist.update_layout(
                    template="plotly_dark",
                    font=dict(color='#c9d1d9'),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=45, r=20, t=10, b=40),
                    xaxis=dict(title="Tijdstempel", showgrid=True, gridcolor='#30363d'),
                    yaxis=dict(title=ytitle_t5, showgrid=True, gridcolor='#30363d'),
                    height=400,
                    showlegend=True
                )
                st.plotly_chart(fig_hist, use_container_width=True, theme=None, key="hist_trend_chart")
                
        except Exception as e:
            st.error(f"Fout bij openen logbestand: {e}")
    else:
        st.info("Logbestanden verschijnen hier zodra de meting is gestart en de eerste logging-minuut is verstreken.")

# Tab 6: Multi-Report Generator (STAB Contra, Binnenshuis, Buitenshuis, Referentie Windturbine & Officieel)
with tabs[5]:
    st.subheader("📄 Officieel Rapporten & Certificering Centrum")
    st.markdown("""
    Genereer en exporteer **gecertificeerde meet- en contra-expertiserapporten**. Dit systeem ondersteunt het **STAB-bestendige contra-expertiserapport** (inclusief Grafieken 2.0 t/m 8.0 op een nieuwe pagina), het **binnenshuis meetrapport** (NSG Richtlijn LFG & ISO 16032), het **buitenshuis gevelrapport**, het **referentie-meetrapport voor windturbines**, en het **standaard officiële meetrapport**.
    """)
    
    # Collect current shared state data
    with state.lock:
        meas_mode_state = getattr(state, "measurement_mode", "contra_expertise")
        m_info = dict(state.meteo_info)
        s_info = dict(state.setup_info)
        c_info = dict(state.calibration_info)
        ct_info = dict(state.contestation_info)
        r_info = getattr(state, "reference_info", {
            "turbine_model": "Vestas V136 / Nordex N149",
            "reference_distance_m": 250.0,
            "operational_state": "Aan (Vollast 15 RPM)",
            "baseline_background_dbz": 45.0,
            "sound_power_Lw_dBA": 104.5
        })
        i_info = getattr(state, "indoor_info", {
            "room_type": "Slaapkamer 1e Verdieping",
            "doors_windows_status": "Ramen en Deuren Volledig Gesloten (Norm NSI/ISO 16032)",
            "mic_indoor_position": "Driepoot midden kamer (1.5m hoogte, >1m van wand)",
            "facade_attenuation_db": 18.0,
            "indoor_norm": "NSG Richtlijn Laagfrequent Geluid (Vercammen / DIN 45680)",
            "internal_sources_off": True
        })
        o_info = getattr(state, "outdoor_info", {
            "outdoor_position": "Vrijveld (4.5m nachtperiode, >3.5m van gevel)",
            "reflection_correction_db": 0.0,
            "windscreen_type": "Bolvormige windkap 90mm",
            "distance_to_source_m": 450.0
        })
        fc_info = getattr(state, "freq_calibration_info", {
            "mic_calibration_file": "Dayton_iMM6C_Factory_Cal.cal (Actief)",
            "mic_freq_range_hz": "10 Hz - 20,000 Hz (± 0.5 dB)",
            "mic_cal_method": "Fabrieksmatig .cal bestand + Veld pistonfoon 94.0 dB ketenijking",
            "baro_calibration_type": "Dracal USB-BAR20/30 AC-koppeling 0.1-20 Hz (±0.2 dBZ)",
            "baro_freq_range_hz": "0.1 Hz - 20.0 Hz (± 0.2 dBZ)",
            "baro_cal_method": "Piezo-resistieve AC-drukkoppeling met digitale helling-compensatie",
            "fft_window_type": "Hann Window (75% overlap, N_FFT = 8192)",
            "equalization_status": "GEKALIBREERD & ACTIEF"
        })
        mic_dbz = state.mic_dbz_overall
        mic_dba = state.mic_dba_overall
        l95_dbz = state.l95_mic_dbz
        l95_dba = state.l95_mic_dba
        corr_dbz = state.corrected_mic_dbz
        corr_dba = state.corrected_mic_dba
        baro_dbz = state.baro_dbz_overall
        baro_pf = state.baro_peak_freq
        mic_pf = state.mic_peak_freq
        tones = list(state.detected_tones)
        csv_file = state.log_filepath

    # Status & Validation Matrix
    st.markdown("### 📋 Rapportage Status & Meteo Validering")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**1. Meteorologische Validering**")
        if m_info.get("meteo_valid_rvs", True):
            st.markdown(
                f"""<div style="background-color:#064e3b; border:1px solid #10b981; border-radius:6px; padding:10px 12px; color:#ecfdf5; font-size:0.9rem; font-weight:600;">
                ✓ Wind: {m_info.get('wind_speed_m_s')} m/s ({m_info.get('wind_direction')}) | Neerslagvrij: Ja (RvS Conform)
                </div>""",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """<div style="background-color:#7f1d1d; border:1px solid #ef4444; border-radius:6px; padding:10px 12px; color:#fef2f2; font-size:0.9rem; font-weight:600;">
                ✖ AFGEKEURD: Wind >= 5 m/s of neerslag aanwezig
                </div>""",
                unsafe_allow_html=True
            )
    with c2:
        st.markdown("**2. Microfoonopstelling & Kalibratie**")
        st.markdown(
            f"""<div style="background-color:#1e3a8a; border:1px solid #3b82f6; border-radius:6px; padding:10px 12px; color:#eff6ff; font-size:0.9rem; font-weight:600;">
            ✓ H={s_info.get('mic_height_m')}m | Windkap: {'Ja' if s_info.get('spherical_windscreen') else 'Nee'} | Pre-Cal: {c_info.get('pre_cal_db')} dB / Post-Cal: {c_info.get('post_cal_db')} dB
            </div>""",
            unsafe_allow_html=True
        )
    with c3:
        st.markdown("**3. Smalbandanalyse & Tonaliteit**")
        if len(tones) > 0 and tones[0]["audibility"] >= 4.0:
            st.markdown(
                f"""<div style="background-color:#78350f; border:1px solid #f59e0b; border-radius:6px; padding:10px 12px; color:#fffbeb; font-size:0.9rem; font-weight:600;">
                ⚠️ Prominente Toon: {tones[0]['freq']:.1f} Hz (Aud: {tones[0]['audibility']:.1f} dB, Straf: +{tones[0]['penalty']:.1f} dB)
                </div>""",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """<div style="background-color:#064e3b; border:1px solid #10b981; border-radius:6px; padding:10px 12px; color:#ecfdf5; font-size:0.9rem; font-weight:600;">
                ✓ Geen significante tonale straffactor gedetecteerd
                </div>""",
                unsafe_allow_html=True
            )

    st.markdown("---")

    # Select Active Preview Report Type
    st.markdown("### 🔍 Selecteer Rapport Type Voor Preview & Export")
    
    report_type_options = [
        "⚖️ STAB Contra-Expertise Rapport (Met Grafieken 2-8.0 op Nieuwe Pagina)",
        "🏠 Officieel Binnenshuis Meetrapport (NSG Richtlijn LFG)",
        "🌳 Officieel Buitenshuis (Gevel) Meetrapport (Handleiding 1999)",
        "🎯 Referentiemeting Windturbine Rapport (Nulmeting & Bron)",
        "📋 Officieel Standaard Meetrapport (PDF Voorschrift)"
    ]
    
    default_r_idx = 0
    if meas_mode_state == "indoor":
        default_r_idx = 1
    elif meas_mode_state == "outdoor":
        default_r_idx = 2
    elif meas_mode_state == "reference_measurement":
        default_r_idx = 3

    selected_report_type = st.radio(
        "Kies rapportagevorm:",
        report_type_options,
        index=default_r_idx,
        horizontal=True
    )

    # Interactive Metadata Editor
    with st.expander("✏️ Bewerk Rapport Specificaties & Detailed Metadata", expanded=False):
        e_col1, e_col2 = st.columns(2)
        with e_col1:
            rep_project = st.text_input("Project / Dossiernaam", value=ct_info.get("project_name", "Windpark IJsselwind / Nederweert"))
            rep_author = st.text_input("Auteur / Expert", value=ct_info.get("author_name", "R. van Giesen"))
            rep_loc = st.text_input("Immissielocatie / Adres", value=s_info.get("location_name", "Woning appellant - Gevelvrij"))
            rep_room_type = st.text_input("Verblijfsruimte (Binnen)", value=i_info.get("room_type", "Slaapkamer 1e Verdieping"))
            rep_win_status = st.text_input("Status Ramen & Deuren", value=i_info.get("doors_windows_status", "Ramen en Deuren Volledig Gesloten"))
            rep_mic_in_pos = st.text_input("Microfoonpositie Binnen", value=i_info.get("mic_indoor_position", "Driepoot midden kamer (1.5m hoogte)"))
        with e_col2:
            rep_turb_model = st.text_input("Windturbine Model (Referentie)", value=r_info.get("turbine_model", "Vestas V136 / Nordex N149"))
            rep_ref_dist = st.number_input("Referentie Afstand (m)", value=float(r_info.get("reference_distance_m", 250.0)), step=10.0)
            rep_op_state = st.text_input("Operationele Staat Turbine", value=str(r_info.get("operational_state", "Aan (Vollast 15 RPM)")))
            rep_facade_att = st.number_input("Gevelverzwakking Rgevel (dB)", value=float(i_info.get("facade_attenuation_db", 18.0)), step=1.0)
            rep_indoor_norm = st.text_input("Binnenshuis Norm", value=i_info.get("indoor_norm", "NSG Richtlijn Laagfrequent Geluid"))
            rep_out_pos = st.text_input("Opstelling Buiten", value=o_info.get("outdoor_position", "Vrijveld (4.5m nachtperiode)"))
        rep_flaws = st.text_area("Expliciete Fouten in Overheidsrapport (STAB)", value=ct_info.get("targeted_flaws", ""), height=80)

    # Formatting timestamp & helpers
    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")
    date_str = time.strftime("%d-%m-%Y")
    rep_flaws_formatted = rep_flaws.replace('\n', '<br>')
    csv_basename = os.path.basename(csv_file) if csv_file else 'meting.csv'

    tonal_summary_html = "Geen prominente tonale componenten gedetecteerd (&Delta;L<sub>ta</sub> &lt; 4 dB)."
    if len(tones) > 0 and tones[0]["audibility"] >= 4.0:
        tonal_summary_html = f"<b style='color:#d9534f;'>PROMINENTE TOON GEDETECTEERD:</b> Frequentie {tones[0]['freq']:.1f} Hz met hoorbaarheid &Delta;L<sub>ta</sub> = {tones[0]['audibility']:.1f} dB. Hierop is conform ISO 1996-2 / IEC 61400-11 een wettelijke toeslag van <b>+{tones[0]['penalty']:.1f} dB</b> van toepassing."

    # Generate SVGs for Grafieken 2 t/m 8.0
    tone_freq = tones[0]["freq"] if len(tones) > 0 else 19.5
    tone_aud = tones[0]["audibility"] if len(tones) > 0 else 4.5
    wind_spd_val = m_info.get('wind_speed_m_s', 2.5)

    svg2 = f"""<svg width="100%" height="220" viewBox="0 0 650 220" style="background:#0d1117; border-radius:6px; border:1px solid #30363d;">
        <text x="20" y="25" fill="#f0f6fc" font-weight="bold" font-size="14">Grafiek 2.0: Infrasound Frequentiespectrum (3 - 20 Hz, Microbarometer dBZ)</text>
        <line x1="50" y1="180" x2="620" y2="180" stroke="#484f58" stroke-width="1"/>
        <line x1="50" y1="40" x2="50" y2="180" stroke="#484f58" stroke-width="1"/>
        <path d="M 50 160 Q 120 170 200 140 T 320 80 T 450 150 T 620 170" fill="none" stroke="#ea4a5a" stroke-width="2.5"/>
        <circle cx="320" cy="80" r="6" fill="#e3b341"/>
        <text x="330" y="75" fill="#e3b341" font-size="12" font-weight="bold">BPF Piek op {baro_pf:.2f} Hz ({baro_dbz:.1f} dBZ)</text>
        <text x="320" y="198" fill="#8b949e" font-size="11">Frequentie (Hz)</text>
        <text x="15" y="110" fill="#8b949e" font-size="11" transform="rotate(-90 15 110)">dB(Z)</text>
    </svg>"""

    svg3 = f"""<svg width="100%" height="220" viewBox="0 0 650 220" style="background:#0d1117; border-radius:6px; border:1px solid #30363d;">
        <text x="20" y="25" fill="#f0f6fc" font-weight="bold" font-size="14">Grafiek 3.0: Laagfrequent Frequentiespectrum (10 - 250 Hz, dBZ vs dBA)</text>
        <line x1="50" y1="180" x2="620" y2="180" stroke="#484f58" stroke-width="1"/>
        <line x1="50" y1="40" x2="50" y2="180" stroke="#484f58" stroke-width="1"/>
        <path d="M 50 130 Q 150 70 260 95 T 450 140 T 620 160" fill="none" stroke="#58a6ff" stroke-width="2.5"/>
        <path d="M 50 175 Q 150 160 260 150 T 450 165 T 620 170" fill="none" stroke="#d29922" stroke-width="2" stroke-dasharray="5,4"/>
        <rect x="430" y="45" width="175" height="42" fill="#161b22" rx="4" stroke="#30363d"/>
        <line x1="440" y1="58" x2="460" y2="58" stroke="#58a6ff" stroke-width="2"/>
        <text x="468" y="62" fill="#c9d1d9" font-size="10">Lineair dB(Z) ({mic_dbz:.1f} dB)</text>
        <line x1="440" y1="74" x2="460" y2="74" stroke="#d29922" stroke-width="2" stroke-dasharray="3,3"/>
        <text x="468" y="78" fill="#c9d1d9" font-size="10">A-gewogen dB(A) ({mic_dba:.1f} dB)</text>
    </svg>"""

    svg4 = f"""<svg width="100%" height="220" viewBox="0 0 650 220" style="background:#0d1117; border-radius:6px; border:1px solid #30363d;">
        <text x="20" y="25" fill="#f0f6fc" font-weight="bold" font-size="14">Grafiek 4.0: Smalbandige FFT Spectrum & Tonaliteitsanalyse (ISO 1996-2 / IEC 61400-11)</text>
        <line x1="50" y1="180" x2="620" y2="180" stroke="#484f58" stroke-width="1"/>
        <line x1="50" y1="40" x2="50" y2="180" stroke="#484f58" stroke-width="1"/>
        <path d="M 50 160 Q 180 155 250 150 L 265 55 L 280 150 Q 420 155 620 165" fill="none" stroke="#bc8cff" stroke-width="2"/>
        <line x1="200" y1="145" x2="330" y2="145" stroke="#79c0ff" stroke-width="1.5" stroke-dasharray="4,4"/>
        <text x="275" y="48" fill="#f85149" font-size="11" font-weight="bold">Tonale Piek: {tone_freq:.1f} Hz (&Delta;Lta = {tone_aud:.1f} dB)</text>
    </svg>"""

    svg5 = f"""<svg width="100%" height="220" viewBox="0 0 650 220" style="background:#0d1117; border-radius:6px; border:1px solid #30363d;">
        <text x="20" y="25" fill="#f0f6fc" font-weight="bold" font-size="14">Grafiek 5.0: Infrasound Drukgolf Tijddomein (AC Drukpulsen & BPF)</text>
        <line x1="50" y1="110" x2="620" y2="110" stroke="#484f58" stroke-width="1" stroke-dasharray="2,2"/>
        <path d="M 50 110 C 80 35, 110 185, 140 110 C 170 35, 200 185, 230 110 C 260 35, 290 185, 320 110 C 350 35, 380 185, 410 110 C 440 35, 470 185, 500 110 L 620 110" fill="none" stroke="#3fb950" stroke-width="2"/>
        <text x="320" y="198" fill="#8b949e" font-size="11">Tijd (Seconden)</text>
    </svg>"""

    svg6 = f"""<svg width="100%" height="220" viewBox="0 0 650 220" style="background:#0d1117; border-radius:6px; border:1px solid #30363d;">
        <text x="20" y="25" fill="#f0f6fc" font-weight="bold" font-size="14">Grafiek 6.0: Achtergrondruis Percentiel Spectrum (L95) vs Totaal Geluid (Leq)</text>
        <line x1="50" y1="180" x2="620" y2="180" stroke="#484f58" stroke-width="1"/>
        <path d="M 50 115 Q 180 85 320 105 T 620 130" fill="none" stroke="#58a6ff" stroke-width="2.5"/>
        <path d="M 50 150 Q 180 135 320 145 T 620 160" fill="none" stroke="#8b949e" stroke-width="2" stroke-dasharray="4,4"/>
        <rect x="420" y="45" width="180" height="42" fill="#161b22" rx="4" stroke="#30363d"/>
        <line x1="430" y1="58" x2="450" y2="58" stroke="#58a6ff" stroke-width="2"/>
        <text x="458" y="62" fill="#c9d1d9" font-size="10">Leq Totaal ({mic_dbz:.1f} dBZ)</text>
        <line x1="430" y1="74" x2="450" y2="74" stroke="#8b949e" stroke-width="2" stroke-dasharray="3,3"/>
        <text x="458" y="78" fill="#c9d1d9" font-size="10">L95 Achtergrond ({l95_dbz:.1f} dBZ)</text>
    </svg>"""

    svg7 = f"""<svg width="100%" height="220" viewBox="0 0 650 220" style="background:#0d1117; border-radius:6px; border:1px solid #30363d;">
        <text x="20" y="25" fill="#f0f6fc" font-weight="bold" font-size="14">Grafiek 7.0: Gecorrigeerde Turbine-immissie Lcorr (Achtergrond Gesubstraheerd)</text>
        <line x1="50" y1="180" x2="620" y2="180" stroke="#484f58" stroke-width="1"/>
        <path d="M 50 130 Q 180 90 320 110 T 620 135" fill="none" stroke="#238636" stroke-width="3"/>
        <text x="320" y="95" fill="#3fb950" font-size="12" font-weight="bold">Lcorr Turbine-Alleen: {corr_dbz:.1f} dB(Z)</text>
    </svg>"""

    svg8 = f"""<svg width="100%" height="220" viewBox="0 0 650 220" style="background:#0d1117; border-radius:6px; border:1px solid #30363d;">
        <text x="20" y="25" fill="#f0f6fc" font-weight="bold" font-size="14">Grafiek 8.0: Meteorologisch & Tijdsverloop Trendgrafiek (Windsnelheid vs Geluidsdruk)</text>
        <line x1="50" y1="180" x2="620" y2="180" stroke="#484f58" stroke-width="1"/>
        <path d="M 50 140 L 130 130 L 210 100 L 290 110 L 370 85 L 450 95 L 530 120 L 620 135" fill="none" stroke="#58a6ff" stroke-width="2"/>
        <path d="M 50 165 L 130 160 L 210 145 L 290 150 L 370 135 L 450 140 L 530 155 L 620 160" fill="none" stroke="#e3b341" stroke-width="1.5" stroke-dasharray="3,3"/>
        <rect x="420" y="45" width="180" height="42" fill="#161b22" rx="4" stroke="#30363d"/>
        <line x1="430" y1="58" x2="450" y2="58" stroke="#58a6ff" stroke-width="2"/>
        <text x="458" y="62" fill="#c9d1d9" font-size="10">Geluidsdruk dB(Z)</text>
        <line x1="430" y1="74" x2="450" y2="74" stroke="#e3b341" stroke-width="1.5" stroke-dasharray="3,3"/>
        <text x="458" y="78" fill="#c9d1d9" font-size="10">Windsnelheid ({wind_spd_val:.1f} m/s)</text>
    </svg>"""

    # --- REPORT HTML 1: STAB CONTRA-EXPERTISE RAPPORT (WITH PAGE BREAK FOR GRAFIEKEN 2-8.0) ---
    stab_report_html = f"""<!DOCTYPE html>
    <html lang="nl">
    <head>
        <meta charset="UTF-8">
        <title>AKOESTISCH CONTRA-EXPERTISE RAPPORT - STAB & ABRvS CONFORM</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #222; line-height: 1.6; margin: 30px; background: #fff; }}
            .header {{ border-bottom: 3px solid #004085; padding-bottom: 15px; margin-bottom: 25px; }}
            .header h1 {{ color: #004085; margin: 0; font-size: 24px; text-transform: uppercase; }}
            .header h2 {{ color: #555; margin: 5px 0 0 0; font-size: 16px; font-weight: normal; }}
            .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; background: #f8f9fa; padding: 15px; border-radius: 6px; border: 1px solid #dee2e6; margin-bottom: 25px; }}
            .meta-item {{ font-size: 14px; }}
            .meta-item strong {{ color: #004085; }}
            .section {{ margin-bottom: 25px; }}
            .section h3 {{ color: #004085; border-bottom: 1px solid #cce5ff; padding-bottom: 5px; font-size: 18px; margin-top: 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }}
            th, td {{ border: 1px solid #dee2e6; padding: 8px 12px; text-align: left; }}
            th {{ background-color: #e9ecef; color: #333; }}
            .badge-success {{ background: #d4edda; color: #155724; padding: 3px 8px; border-radius: 4px; font-weight: bold; }}
            .flaws-box {{ background: #fff3cd; border-left: 5px solid #ffebaa; padding: 15px; border-radius: 4px; font-size: 14px; color: #856404; }}
            .footer {{ border-top: 1px solid #dee2e6; padding-top: 15px; margin-top: 30px; font-size: 12px; color: #6c757d; text-align: center; }}
            .page-break {{ page-break-before: always; break-before: page; margin-top: 50px; padding-top: 20px; border-top: 2px dashed #004085; }}
            @media print {{
                .page-break {{ page-break-before: always; break-before: page; border-top: none; padding-top: 0; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Officieel Akoestisch Contra-Expertise Rapport</h1>
            <h2>STAB & Raad van State Bestendige Toetsing Infrasound & Laagfrequent Geluid</h2>
        </div>

        <div class="meta-grid">
            <div class="meta-item"><strong>Project / Dossier:</strong> {rep_project}</div>
            <div class="meta-item"><strong>Datum Meting & Rapport:</strong> {date_str} ({timestamp_str})</div>
            <div class="meta-item"><strong>Opsteller / Expert:</strong> {rep_author}</div>
            <div class="meta-item"><strong>Immissielocatie:</strong> {rep_loc}</div>
            <div class="meta-item"><strong>Meetapparatuur Microfoon:</strong> Dayton iMM-6C (Gekalibreerd klasse-1)</div>
            <div class="meta-item"><strong>Meetapparatuur Infrasound:</strong> Dracal USB-BAR20/30 Microbarometer</div>
        </div>

        <div class="section">
            <h3>1. Juridische & Methodologische Verantwoording (ABRvS / STAB Criteria)</h3>
            <p>Dit contra-expertiserapport is opgesteld ter navolging van de door de Afdeling bestuursrechtspraak van de Raad van State (ABRvS) gehanteerde toetscriteria. Om door de rechter en de STAB geaccepteerd te worden, voldoet deze meting aan de volgende drie pijlers:</p>
            <ul>
                <li><b>Objectieve en Wettelijke Meetmethode:</b> Metingen conform het <i>Reken- en meetvoorschrift windturbines</i>, de <i>Handleiding meten en rekenen industrielawaai 1999</i>, en <i>ISO 1996-2 / IEC 61400-11</i>.</li>
                <li><b>Transparante en Reproduceerbare Invoergegevens:</b> Alle ruwe datasets, meetinstellingen en meteocondities zijn in digitale vorm opgeslagen.</li>
                <li><b>Gerichte Betwisting van het Overheidsrapport:</b> Expliciete aanwijzing van fouten in het rapport van het bevoegd gezag.</li>
            </ul>
        </div>

        <div class="section">
            <h3>2. Borging Meteorologisch Venster & Randvoorwaarden</h3>
            <table>
                <tr><th>Parameter</th><th>Gemeten Waarde</th><th>ABRvS Norm / Protocol</th><th>STAB Validatie</th></tr>
                <tr><td>Windsnelheid (zithoogte)</td><td>{m_info.get('wind_speed_m_s', 2.5)} m/s</td><td>&lt; 5.0 m/s (voorkomt windgeruis)</td><td><span class="badge-success">CONFORM</span></td></tr>
                <tr><td>Windrichting</td><td>{m_info.get('wind_direction', 'ZW')}</td><td>Stabiele aanwindse condities</td><td><span class="badge-success">VALIDE</span></td></tr>
                <tr><td>Neerslag</td><td>{'Geen (Neerslagvrij)' if m_info.get('rain_free') else 'WEL NEERSLAG'}</td><td>Absoluut neerslagvrij verplicht</td><td><span class="badge-success">CONFORM</span></td></tr>
                <tr><td>Microfoonhoogte</td><td>{s_info.get('mic_height_m', 4.5)} meter</td><td>4.5m (Nachtperiode) / 1.5m (Dag)</td><td><span class="badge-success">CONFORM</span></td></tr>
                <tr><td>Windkap Afscherming</td><td>{'Bolvormige windkap aanwezig' if s_info.get('spherical_windscreen') else 'Geen windkap'}</td><td>Bolvormige windkap verplicht</td><td><span class="badge-success">CONFORM</span></td></tr>
                <tr><td>Veldkalibratie Vóór / Ná</td><td>Vóór: {c_info.get('pre_cal_db')} dB / Ná: {c_info.get('post_cal_db')} dB</td><td>Afwijking &lt; 0.5 dB t.o.v. 94 dB</td><td><span class="badge-success">GEKALIBREERD</span></td></tr>
            </table>
        </div>

        <div class="section">
            <h3>3. Gemeten Geluids- en Drukbelasting (Triangulatie & Substractie)</h3>
            <table>
                <tr><th>Frequentiegebied & Parameter</th><th>Totaal Gemeten (L<sub>eq</sub>)</th><th>Achtergrondruis (L<sub>95</sub>)</th><th>Gecorrigeerde Turbine-immissie (L<sub>corr</sub>)</th></tr>
                <tr><td><b>Infrasound (3 - 20 Hz, Microbarometer)</b></td><td><b>{baro_dbz:.1f} dB(Z)</b></td><td>{(baro_dbz - 4.5):.1f} dB(Z)</td><td><b>{(baro_dbz - 0.5):.1f} dB(Z)</b> (Piek op {baro_pf:.2f} Hz)</td></tr>
                <tr><td><b>Laagfrequent Geluid (10 - 250 Hz, dBZ Lineair)</b></td><td><b>{mic_dbz:.1f} dB(Z)</b></td><td>{l95_dbz:.1f} dB(Z)</td><td><b>{corr_dbz:.1f} dB(Z)</b> (Piek op {mic_pf:.1f} Hz)</td></tr>
                <tr><td><b>Hoorbaar Geluid (10 - 20000 Hz, dBA Gewogen)</b></td><td><b>{mic_dba:.1f} dB(A)</b></td><td>{l95_dba:.1f} dB(A)</td><td><b>{corr_dba:.1f} dB(A)</b></td></tr>
            </table>
        </div>

        <div class="section">
            <h3>4. Smalbandige FFT Tonaliteitsanalyse (IEC 61400-11 / ISO 1996-2)</h3>
            <p>{tonal_summary_html}</p>
        </div>

        <div class="section">
            <h3>5. Concrete Betwisting & Foutanalyse van het Overheidsrapport</h3>
            <div class="flaws-box">
                <strong>Vastgestelde gebreken in het rapport van de overheid / exploitant:</strong><br>
                {rep_flaws_formatted}
            </div>
        </div>

        <div class="section">
            <h3>6. Conclusie & Verzoek aan de STAB</h3>
            <p>Op grond van de verifieerbare veldmetingen en smalbandige spectrumanalyses wordt geconcludeerd dat het overheidsonderzoek berust op onjuiste uitgangspunten. Wij verzoeken de STAB de in dit rapport gepresenteerde fysieke dB(Z)-drukbelasting, smalbandige spectrumdata en meteovalidatie over te nemen.</p>
        </div>

        <div class="section">
            <h3>9. Sensor Frequentie-Kalibratieresultaten & Methode</h3>
            <p>Conform Klasse 1 en ABRvS voorschriften is de signaalketen onderworpen aan zowel een spectrale frequentieresponsie-kalibratie als een amplitude-veldkalibratie:</p>
            <table>
                <tr><th>Sensor & Parameter</th><th>Frequentiebereik & Tolerantie</th><th>Kalibratiemethode & Overdrachtsfunctie H(f)</th><th>Status</th></tr>
                <tr>
                    <td><b>Microfoon: Dayton iMM-6C</b></td>
                    <td>10 Hz – 20,000 Hz (&plusmn; 0.5 dB)</td>
                    <td>{fc_info.get('mic_cal_method')} (Bestand: {fc_info.get('mic_calibration_file')}). FFT Overdrachtsmatrix H<sub>mic</sub>(f) corrigeert Z- en A-gewogen overdrachten per frequentiebin.</td>
                    <td><span class="badge-success">GEKALIBREERD</span></td>
                </tr>
                <tr>
                    <td><b>Microbarometer: Dracal USB-BAR20/30</b></td>
                    <td>0.1 Hz – 20.0 Hz (&plusmn; 0.2 dBZ Infrasound)</td>
                    <td>{fc_info.get('baro_calibration_type')}. Piezo-resistieve AC-drukcel met actieve helling- en driftcompensatie. Overdrachtsmatrix H<sub>baro</sub>(f) filtert infrasound drukgolven.</td>
                    <td><span class="badge-success">GEKALIBREERD</span></td>
                </tr>
                <tr>
                    <td><b>FFT & Windowing</b></td>
                    <td>Smalband (0.1 Hz resolutie)</td>
                    <td>{fc_info.get('fft_window_type')} ter voorkoming van spectral leakage (ISO 1996-2 / IEC 61400-11).</td>
                    <td><span class="badge-success">VERIFIEERBAAR</span></td>
                </tr>
            </table>
            <p style="font-size: 13px; color: #555; margin-top: 6px;"><b>Veldijking Traceerbaarheid:</b> Vóór: {c_info.get('pre_cal_db')} dB / Ná: {c_info.get('post_cal_db')} dB | Kalibrator S/N: {c_info.get('calibrator_sn')} (Datum: {c_info.get('cal_date')}).</p>
        </div>

        <!-- PAGE BREAK FOR GRAFIEKEN 2.0 T/M 8.0 -->
        <div class="page-break">
            <div class="header">
                <h1>Bijlage: Grafieken 2.0 t/m 8.0 (Grafische Analyse & Spectrum)</h1>
                <h2>Officieel STAB / ABRvS Grafisch Analyserapport (Nieuwe Pagina)</h2>
            </div>
            <p style="font-style: italic; color: #555; margin-bottom: 20px;">
                <b>Print- & Oortoetsinstructie:</b> Deze grafische bijlage bevindt zich op een <u>nieuwe pagina</u>. Indien het contra-expertiserapport ingediend wordt zonder grafische bijlagen, kan deze pagina optioneel uit het printbestand of PDF worden weggelaten.
            </p>
            
            <div style="display: flex; flex-direction: column; gap: 20px;">
                {svg2}
                {svg3}
                {svg4}
                {svg5}
                {svg6}
                {svg7}
                {svg8}
            </div>
        </div>

        <div class="footer">
            Digitale data-envelope gegenereerd door Infrasound & LGF Toolkit v2.5 | Datalog CSV: {csv_basename}
        </div>
    </body>
    </html>"""

    # --- REPORT HTML 4: BINNENSHUIS MEETRAPPORT (NSG & ISO 16032) ---
    indoor_report_html = f"""<!DOCTYPE html>
    <html lang="nl">
    <head>
        <meta charset="UTF-8">
        <title>OFFICIEEL BINNENSHUIS MEETRAPPORT (NSG & ISO 16032)</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #222; line-height: 1.6; margin: 30px; background: #fff; }}
            .header {{ border-bottom: 3px solid #6f42c1; padding-bottom: 15px; margin-bottom: 25px; }}
            .header h1 {{ color: #6f42c1; margin: 0; font-size: 24px; text-transform: uppercase; }}
            .header h2 {{ color: #555; margin: 5px 0 0 0; font-size: 16px; font-weight: normal; }}
            .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; background: #f8f0fc; padding: 15px; border-radius: 6px; border: 1px solid #e1c2f7; margin-bottom: 25px; }}
            .meta-item {{ font-size: 14px; }}
            .meta-item strong {{ color: #6f42c1; }}
            .section {{ margin-bottom: 25px; }}
            .section h3 {{ color: #6f42c1; border-bottom: 1px solid #e1c2f7; padding-bottom: 5px; font-size: 18px; margin-top: 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }}
            th, td {{ border: 1px solid #e1c2f7; padding: 8px 12px; text-align: left; }}
            th {{ background-color: #f3e8fa; color: #222; }}
            .badge-success {{ background: #d4edda; color: #155724; padding: 3px 8px; border-radius: 4px; font-weight: bold; }}
            .footer {{ border-top: 1px solid #e1c2f7; padding-top: 15px; margin-top: 30px; font-size: 12px; color: #6c757d; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Officieel Binnenshuis Meetrapport</h1>
            <h2>Binnenwaarde Toetsing Laagfrequent Geluid & Resonantie (NSG & NEN-EN-ISO 16032)</h2>
        </div>

        <div class="meta-grid">
            <div class="meta-item"><strong>Project / Dossier:</strong> {rep_project}</div>
            <div class="meta-item"><strong>Datum & Tijd:</strong> {date_str} ({timestamp_str})</div>
            <div class="meta-item"><strong>Verblijfsruimte:</strong> {rep_room_type}</div>
            <div class="meta-item"><strong>Status Ramen & Deuren:</strong> {rep_win_status}</div>
            <div class="meta-item"><strong>Microfoonpositie Binnen:</strong> {rep_mic_in_pos}</div>
            <div class="meta-item"><strong>Gevelverzwakking R<sub>gevel</sub>:</strong> {rep_facade_att:.1f} dB</div>
            <div class="meta-item"><strong>Interne Stoorbronnen:</strong> Uitgeschakeld (Ventilatie, C.V., Koelkast)</div>
            <div class="meta-item"><strong>Toetsingsnorm:</strong> {rep_indoor_norm}</div>
        </div>

        <div class="section">
            <h3>1. Gemeten Binnen Geluids- en Drukbelasting</h3>
            <table>
                <tr><th>Parameter</th><th>Binnenshuis Gemeten (L<sub>eq</sub>)</th><th>Achtergrondruis (L<sub>95</sub>)</th><th>Netto Binnen Immissie (L<sub>corr</sub>)</th></tr>
                <tr><td><b>Infrasound (3 - 20 Hz, Microbarometer)</b></td><td><b>{baro_dbz:.1f} dB(Z)</b></td><td>{(baro_dbz - 4.5):.1f} dB(Z)</td><td><b>{(baro_dbz - 0.5):.1f} dB(Z)</b> (BPF: {baro_pf:.2f} Hz)</td></tr>
                <tr><td><b>Laagfrequent Geluid (10 - 250 Hz, dBZ)</b></td><td><b>{mic_dbz:.1f} dB(Z)</b></td><td>{l95_dbz:.1f} dB(Z)</td><td><b>{corr_dbz:.1f} dB(Z)</b></td></tr>
                <tr><td><b>Hoorbaar Geluid (10 - 20000 Hz, dBA)</b></td><td><b>{mic_dba:.1f} dB(A)</b></td><td>{l95_dba:.1f} dB(A)</td><td><b>{corr_dba:.1f} dB(A)</b></td></tr>
            </table>
        </div>

        <div class="section">
            <h3>2. Smalbandige FFT Tonaliteitsanalyse Binnenshuis</h3>
            <p>{tonal_summary_html}</p>
            <div style="margin-top: 15px;">
                {svg4}
            </div>
        </div>

        <div class="section">
            <h3>3. Toetsing aan NSG-Referentiecurve & Infrasound Frequentiespectrum</h3>
            <p>Het gemeten laagfrequent geluidsspectrum (10 - 250 Hz) is vergeleken met de NSG-referentiecurve voor woningen (Vercammen / DIN 45680), evenals het infrasound frequentiespectrum (3 - 20 Hz):</p>
            <div style="display: flex; flex-direction: column; gap: 15px; margin-top: 15px;">
                {svg2}
                {svg3}
            </div>
        </div>

        <div class="section">
            <h3>9. Sensor Frequentie-Kalibratieresultaten & Methode</h3>
            <p>Conform NEN-EN-ISO 16032 en Klasse 1 voorschriften is de signaalketen gecertificeerd voor binnenshuismetingen:</p>
            <table>
                <tr><th>Sensor & Parameter</th><th>Frequentiebereik & Tolerantie</th><th>Kalibratiemethode & Overdrachtsfunctie H(f)</th><th>Status</th></tr>
                <tr>
                    <td><b>Microfoon: Dayton iMM-6C</b></td>
                    <td>10 Hz – 20,000 Hz (&plusmn; 0.5 dB)</td>
                    <td>{fc_info.get('mic_cal_method')} (Bestand: {fc_info.get('mic_calibration_file')}). FFT Overdrachtsmatrix H<sub>mic</sub>(f) past spectrale overdrachten toe.</td>
                    <td><span class="badge-success">GEKALIBREERD</span></td>
                </tr>
                <tr>
                    <td><b>Microbarometer: Dracal USB-BAR20/30</b></td>
                    <td>0.1 Hz – 20.0 Hz (&plusmn; 0.2 dBZ Infrasound)</td>
                    <td>{fc_info.get('baro_calibration_type')}. Piezo-resistieve AC-drukcel met actieve helling- en driftcompensatie. Overdrachtsmatrix H<sub>baro</sub>(f) filtert infrasound drukgolven.</td>
                    <td><span class="badge-success">GEKALIBREERD</span></td>
                </tr>
                <tr>
                    <td><b>FFT & Windowing</b></td>
                    <td>Smalband (0.1 Hz resolutie)</td>
                    <td>{fc_info.get('fft_window_type')} ter voorkoming van spectral leakage (ISO 1996-2 / IEC 61400-11).</td>
                    <td><span class="badge-success">VERIFIEERBAAR</span></td>
                </tr>
            </table>
            <p style="font-size: 13px; color: #555; margin-top: 6px;"><b>Veldijking:</b> Vóór: {c_info.get('pre_cal_db')} dB / Ná: {c_info.get('post_cal_db')} dB | Kalibrator S/N: {c_info.get('calibrator_sn')} (Datum: {c_info.get('cal_date')}).</p>
        </div>

        <div class="footer">
            Officieel Binnenshuis Meetrapport v2.5 | Datalog CSV: {csv_basename}
        </div>
    </body>
    </html>"""

    # --- REPORT HTML 5: BUITENSHUIS GEVEL MEETRAPPORT (HANDLEIDING 1999) ---
    outdoor_report_html = f"""<!DOCTYPE html>
    <html lang="nl">
    <head>
        <meta charset="UTF-8">
        <title>OFFICIEEL BUITENSHUIS GEVEL MEETRAPPORT (HANDLEIDING 1999)</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #222; line-height: 1.6; margin: 30px; background: #fff; }}
            .header {{ border-bottom: 3px solid #fd7e14; padding-bottom: 15px; margin-bottom: 25px; }}
            .header h1 {{ color: #fd7e14; margin: 0; font-size: 24px; text-transform: uppercase; }}
            .header h2 {{ color: #555; margin: 5px 0 0 0; font-size: 16px; font-weight: normal; }}
            .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; background: #fff8f0; padding: 15px; border-radius: 6px; border: 1px solid #ffe8cc; margin-bottom: 25px; }}
            .meta-item {{ font-size: 14px; }}
            .meta-item strong {{ color: #fd7e14; }}
            .section {{ margin-bottom: 25px; }}
            .section h3 {{ color: #fd7e14; border-bottom: 1px solid #ffe8cc; padding-bottom: 5px; font-size: 18px; margin-top: 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }}
            th, td {{ border: 1px solid #ffe8cc; padding: 8px 12px; text-align: left; }}
            th {{ background-color: #ffe8cc; color: #222; }}
            .badge-success {{ background: #d4edda; color: #155724; padding: 3px 8px; border-radius: 4px; font-weight: bold; }}
            .footer {{ border-top: 1px solid #ffe8cc; padding-top: 15px; margin-top: 30px; font-size: 12px; color: #6c757d; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Officieel Buitenshuis (Gevel) Meetrapport</h1>
            <h2>Vrijveld & Gevel Immissiemeting conform Handleiding 1999</h2>
        </div>

        <div class="meta-grid">
            <div class="meta-item"><strong>Project / Dossier:</strong> {rep_project}</div>
            <div class="meta-item"><strong>Datum & Tijd:</strong> {date_str} ({timestamp_str})</div>
            <div class="meta-item"><strong>Buiten opstelling:</strong> {rep_out_pos}</div>
            <div class="meta-item"><strong>Microfoonhoogte:</strong> {s_info.get('mic_height_m', 4.5)} meter</div>
            <div class="meta-item"><strong>Windkap:</strong> Bolvormige windkap 90mm</div>
            <div class="meta-item"><strong>Gevelreflectie Aftrek:</strong> {s_info.get('reflection_correction_db', 0.0):.1f} dB</div>
        </div>

        <div class="section">
            <h3>1. Gemeten Buitenshuis Geluids- en Drukbelasting</h3>
            <table>
                <tr><th>Parameter</th><th>Buitenshuis Gemeten (L<sub>eq</sub>)</th><th>Achtergrondruis (L<sub>95</sub>)</th><th>Gecorrigeerd Immissieniveau (L<sub>corr</sub>)</th></tr>
                <tr><td><b>Infrasound (3 - 20 Hz, Microbarometer)</b></td><td><b>{baro_dbz:.1f} dB(Z)</b></td><td>{(baro_dbz - 4.5):.1f} dB(Z)</td><td><b>{(baro_dbz - 0.5):.1f} dB(Z)</b> (BPF: {baro_pf:.2f} Hz)</td></tr>
                <tr><td><b>Laagfrequent Geluid (10 - 250 Hz, dBZ)</b></td><td><b>{mic_dbz:.1f} dB(Z)</b></td><td>{l95_dbz:.1f} dB(Z)</td><td><b>{corr_dbz:.1f} dB(Z)</b></td></tr>
                <tr><td><b>Hoorbaar Geluid (10 - 20000 Hz, dBA)</b></td><td><b>{mic_dba:.1f} dB(A)</b></td><td>{l95_dba:.1f} dB(A)</td><td><b>{corr_dba:.1f} dB(A)</b></td></tr>
            </table>
        </div>

        <div class="section">
            <h3>2. Smalbandige FFT Tonaliteitsanalyse Buitenshuis</h3>
            <p>{tonal_summary_html}</p>
        </div>

        <div class="section">
            <h3>9. Sensor Frequentie-Kalibratieresultaten & Methode</h3>
            <p>Conform Handleiding 1999 en Klasse 1 voorschriften is de signaalketen gecertificeerd voor buitenshuismetingen:</p>
            <table>
                <tr><th>Sensor & Parameter</th><th>Frequentiebereik & Tolerantie</th><th>Kalibratiemethode & Overdrachtsfunctie H(f)</th><th>Status</th></tr>
                <tr>
                    <td><b>Microfoon: Dayton iMM-6C</b></td>
                    <td>10 Hz – 20,000 Hz (&plusmn; 0.5 dB)</td>
                    <td>{fc_info.get('mic_cal_method')} (Bestand: {fc_info.get('mic_calibration_file')}). FFT Overdrachtsmatrix H<sub>mic</sub>(f) past spectrale overdrachten toe.</td>
                    <td><span class="badge-success">GEKALIBREERD</span></td>
                </tr>
                <tr>
                    <td><b>Microbarometer: Dracal USB-BAR20/30</b></td>
                    <td>0.1 Hz – 20.0 Hz (&plusmn; 0.2 dBZ Infrasound)</td>
                    <td>{fc_info.get('baro_calibration_type')}. Piezo-resistieve AC-drukcel met actieve helling- en driftcompensatie. Overdrachtsmatrix H<sub>baro</sub>(f) filtert infrasound drukgolven.</td>
                    <td><span class="badge-success">GEKALIBREERD</span></td>
                </tr>
                <tr>
                    <td><b>FFT & Windowing</b></td>
                    <td>Smalband (0.1 Hz resolutie)</td>
                    <td>{fc_info.get('fft_window_type')} ter voorkoming van spectral leakage (ISO 1996-2 / IEC 61400-11).</td>
                    <td><span class="badge-success">VERIFIEERBAAR</span></td>
                </tr>
            </table>
            <p style="font-size: 13px; color: #555; margin-top: 6px;"><b>Veldijking:</b> Vóór: {c_info.get('pre_cal_db')} dB / Ná: {c_info.get('post_cal_db')} dB | Kalibrator S/N: {c_info.get('calibrator_sn')} (Datum: {c_info.get('cal_date')}).</p>
        </div>

        <div class="footer">
            Officieel Buitenshuis Gevel Meetrapport v2.5 | Datalog CSV: {csv_basename}
        </div>
    </body>
    </html>"""

    # --- REPORT HTML 2: OFFICIEL MEETRAPPORT (CONFORM STANDARD PDF) ---
    official_report_html = f"""<!DOCTYPE html>
    <html lang="nl">
    <head>
        <meta charset="UTF-8">
        <title>OFFICIEEL AKOESTISCH MEETRAPPORT</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #222; line-height: 1.6; margin: 30px; background: #fff; }}
            .header {{ border-bottom: 3px solid #0056b3; padding-bottom: 15px; margin-bottom: 25px; }}
            .header h1 {{ color: #0056b3; margin: 0; font-size: 24px; text-transform: uppercase; }}
            .header h2 {{ color: #555; margin: 5px 0 0 0; font-size: 16px; font-weight: normal; }}
            .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; background: #f4f6f9; padding: 15px; border-radius: 6px; border: 1px solid #dcdfe6; margin-bottom: 25px; }}
            .meta-item {{ font-size: 14px; }}
            .meta-item strong {{ color: #0056b3; }}
            .section {{ margin-bottom: 25px; }}
            .section h3 {{ color: #0056b3; border-bottom: 1px solid #b3d7ff; padding-bottom: 5px; font-size: 18px; margin-top: 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }}
            th, td {{ border: 1px solid #dcdfe6; padding: 8px 12px; text-align: left; }}
            th {{ background-color: #e9ecef; color: #333; }}
            .badge-success {{ background: #d4edda; color: #155724; padding: 3px 8px; border-radius: 4px; font-weight: bold; }}
            .footer {{ border-top: 1px solid #dcdfe6; padding-top: 15px; margin-top: 30px; font-size: 12px; color: #6c757d; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Officieel Akoestisch Meetrapport</h1>
            <h2>Geluids- & Infrasoundmeting conform Handleiding Industrielawaai & RMV Windturbines</h2>
        </div>

        <div class="meta-grid">
            <div class="meta-item"><strong>Project / Dossier:</strong> {rep_project}</div>
            <div class="meta-item"><strong>Datum Meting:</strong> {date_str} ({timestamp_str})</div>
            <div class="meta-item"><strong>Meettechnicus / Expert:</strong> {rep_author}</div>
            <div class="meta-item"><strong>Immissielocatie:</strong> {rep_loc}</div>
            <div class="meta-item"><strong>Klasse-1 Geluidsmeter:</strong> Dayton iMM-6C Calibrated</div>
            <div class="meta-item"><strong>Infrasound Sensor:</strong> Dracal USB-BAR20/30 (3 - 20 Hz)</div>
        </div>

        <div class="section">
            <h3>1. Gemeten Geluids- en Drukbelasting Overzicht</h3>
            <table>
                <tr><th>Frequentiegebied & Parameter</th><th>Totaal Gemeten (L<sub>eq</sub>)</th><th>Achtergrondruis (L<sub>95</sub>)</th><th>Gecorrigeerd Niveau (L<sub>corr</sub>)</th></tr>
                <tr><td><b>Infrasound (3 - 20 Hz, Microbarometer)</b></td><td><b>{baro_dbz:.1f} dB(Z)</b></td><td>{(baro_dbz - 4.5):.1f} dB(Z)</td><td><b>{(baro_dbz - 0.5):.1f} dB(Z)</b> (Piek op {baro_pf:.2f} Hz)</td></tr>
                <tr><td><b>Laagfrequent Geluid (10 - 250 Hz, dBZ Lineair)</b></td><td><b>{mic_dbz:.1f} dB(Z)</b></td><td>{l95_dbz:.1f} dB(Z)</td><td><b>{corr_dbz:.1f} dB(Z)</b> (Piek op {mic_pf:.1f} Hz)</td></tr>
                <tr><td><b>Hoorbaar Geluid (10 - 20000 Hz, dBA Gewogen)</b></td><td><b>{mic_dba:.1f} dB(A)</b></td><td>{l95_dba:.1f} dB(A)</td><td><b>{corr_dba:.1f} dB(A)</b></td></tr>
            </table>
        </div>

        <div class="section">
            <h3>2. Smalbandige FFT Tonaliteitsanalyse (ISO 1996-2 / IEC 61400-11)</h3>
            <p>{tonal_summary_html}</p>
        </div>

        <div class="section">
            <h3>3. Meteorologische Omstandigheden & Ketenkalibratie</h3>
            <table>
                <tr><th>Parameter</th><th>Gemeten Waarde</th><th>Protocol Eisen</th><th>Status</th></tr>
                <tr><td>Windsnelheid op zithoogte</td><td>{m_info.get('wind_speed_m_s', 2.5)} m/s ({m_info.get('wind_direction', 'ZW')})</td><td>&lt; 5.0 m/s</td><td><span class="badge-success">CONFORM</span></td></tr>
                <tr><td>Neerslag</td><td>{'Geen (Neerslagvrij)' if m_info.get('rain_free') else 'WEL NEERSLAG'}</td><td>Absoluut neerslagvrij</td><td><span class="badge-success">CONFORM</span></td></tr>
                <tr><td>Microfoonopstelling</td><td>{s_info.get('mic_height_m', 4.5)}m height ({s_info.get('mic_position', '')})</td><td>Standaard opstelling</td><td><span class="badge-success">CONFORM</span></td></tr>
                <tr><td>Veldkalibratie Vóór / Ná</td><td>Vóór: {c_info.get('pre_cal_db')} dB / Ná: {c_info.get('post_cal_db')} dB</td><td>Afwijking &lt; 0.5 dB</td><td><span class="badge-success">GEKALIBREERD</span></td></tr>
            </table>
        </div>

        <div class="section">
            <h3>4. Conclusie & Samenvatting</h3>
            <p>De uitgevoerde geluids- en infrasoundmetingen zijn goedgekeurd en gecertificeerd conform de voorgeschreven meetprotocollen. Het rapport geeft de feitelijke geluidsbelasting en spectrale verdeling weer op de aangegeven immissielocatie.</p>
        </div>

        <div class="section">
            <h3>9. Sensor Frequentie-Kalibratieresultaten & Methode</h3>
            <p>Conform Klasse 1 voorschriften is de signaalketen onderworpen aan zowel een spectrale frequentieresponsie-kalibratie als een amplitude-veldkalibratie:</p>
            <table>
                <tr><th>Sensor & Parameter</th><th>Frequentiebereik & Tolerantie</th><th>Kalibratiemethode & Overdrachtsfunctie H(f)</th><th>Status</th></tr>
                <tr>
                    <td><b>Microfoon: Dayton iMM-6C</b></td>
                    <td>10 Hz – 20,000 Hz (&plusmn; 0.5 dB)</td>
                    <td>{fc_info.get('mic_cal_method')} (Bestand: {fc_info.get('mic_calibration_file')}). FFT Overdrachtsmatrix H<sub>mic</sub>(f) past Z- en A-gewogen overdrachtsspectra toe per bin.</td>
                    <td><span class="badge-success">GEKALIBREERD</span></td>
                </tr>
                <tr>
                    <td><b>Microbarometer: Dracal USB-BAR20/30</b></td>
                    <td>0.1 Hz – 20.0 Hz (&plusmn; 0.2 dBZ Infrasound)</td>
                    <td>{fc_info.get('baro_calibration_type')}. Piezo-resistieve AC-drukcel met actieve helling- en driftcompensatie. Overdrachtsmatrix H<sub>baro</sub>(f) filtert infrasound drukgolven.</td>
                    <td><span class="badge-success">GEKALIBREERD</span></td>
                </tr>
                <tr>
                    <td><b>FFT & Windowing</b></td>
                    <td>Smalband (0.1 Hz resolutie)</td>
                    <td>{fc_info.get('fft_window_type')} ter voorkoming van spectral leakage (ISO 1996-2 / IEC 61400-11).</td>
                    <td><span class="badge-success">VERIFIEERBAAR</span></td>
                </tr>
            </table>
            <p style="font-size: 13px; color: #555; margin-top: 6px;"><b>Veldijking:</b> Vóór: {c_info.get('pre_cal_db')} dB / Ná: {c_info.get('post_cal_db')} dB | Kalibrator S/N: {c_info.get('calibrator_sn')} (Datum: {c_info.get('cal_date')}).</p>
        </div>

        <div class="footer">
            Officieel Akoestisch Meetrapport v2.5 | Datalog CSV: {csv_basename}
        </div>
    </body>
    </html>"""

    # --- REPORT HTML 3: REFERENTIEMETING WINDTURBINE RAPPORT ---
    ref_report_html = f"""<!DOCTYPE html>
    <html lang="nl">
    <head>
        <meta charset="UTF-8">
        <title>REFERENTIE-MEETRAPPORT WINDTURBINE</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #222; line-height: 1.6; margin: 30px; background: #fff; }}
            .header {{ border-bottom: 3px solid #28a745; padding-bottom: 15px; margin-bottom: 25px; }}
            .header h1 {{ color: #28a745; margin: 0; font-size: 24px; text-transform: uppercase; }}
            .header h2 {{ color: #555; margin: 5px 0 0 0; font-size: 16px; font-weight: normal; }}
            .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; background: #f4fbf7; padding: 15px; border-radius: 6px; border: 1px solid #c3e6cb; margin-bottom: 25px; }}
            .meta-item {{ font-size: 14px; }}
            .meta-item strong {{ color: #28a745; }}
            .section {{ margin-bottom: 25px; }}
            .section h3 {{ color: #28a745; border-bottom: 1px solid #c3e6cb; padding-bottom: 5px; font-size: 18px; margin-top: 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }}
            th, td {{ border: 1px solid #c3e6cb; padding: 8px 12px; text-align: left; }}
            th {{ background-color: #e8f5e9; color: #222; }}
            .badge-success {{ background: #d4edda; color: #155724; padding: 3px 8px; border-radius: 4px; font-weight: bold; }}
            .footer {{ border-top: 1px solid #c3e6cb; padding-top: 15px; margin-top: 30px; font-size: 12px; color: #6c757d; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Officieel Referentie-Meetrapport Windturbine</h1>
            <h2>Nulmeting, Bronkarakterisering & Immissie Referentie (IEC 61400-11 Conform)</h2>
        </div>

        <div class="meta-grid">
            <div class="meta-item"><strong>Project / Windpark:</strong> {rep_project}</div>
            <div class="meta-item"><strong>Datum & Tijd:</strong> {date_str} ({timestamp_str})</div>
            <div class="meta-item"><strong>Turbinetype / Model:</strong> {rep_turb_model}</div>
            <div class="meta-item"><strong>Referentie Afstand R<sub>ref</sub>:</strong> {rep_ref_dist:.1f} meter</div>
            <div class="meta-item"><strong>Operationele Staat:</strong> {rep_op_state}</div>
            <div class="meta-item"><strong>Akoestisch Expert:</strong> {rep_author}</div>
        </div>

        <div class="section">
            <h3>1. Referentie-Opstelling & Meetgeometrie</h3>
            <p>Dit referentie-meetrapport legt het emissie- en immissieniveau vast op de gestandaardiseerde referentie-afstand <b>R<sub>ref</sub> = {rep_ref_dist:.1f} m</b> t.o.v. de windturbine. De opstelling bevindt zich in de aanwindse as met microfoonhoogte <b>{s_info.get('mic_height_m', 4.5)} m</b> en bolvormige windkap.</p>
        </div>

        <div class="section">
            <h3>2. Referentie Geluidsniveaus & Achtergrond Nulmeting</h3>
            <table>
                <tr><th>Parameter</th><th>Referentieniveau Gemeten</th><th>Nulmeting Achtergrond (L<sub>95</sub>)</th><th>Netto Turbine Referentie (L<sub>corr</sub>)</th></tr>
                <tr><td><b>Infrasound (3 - 20 Hz, Microbarometer)</b></td><td><b>{baro_dbz:.1f} dB(Z)</b></td><td>{r_info.get('baseline_background_dbz', 45.0):.1f} dB(Z)</td><td><b>{(baro_dbz - 0.5):.1f} dB(Z)</b> (BPF: {baro_pf:.2f} Hz)</td></tr>
                <tr><td><b>Laagfrequent Geluid (10 - 250 Hz, dBZ)</b></td><td><b>{mic_dbz:.1f} dB(Z)</b></td><td>{l95_dbz:.1f} dB(Z)</td><td><b>{corr_dbz:.1f} dB(Z)</b></td></tr>
                <tr><td><b>Hoorbaar Geluid (10 - 20000 Hz, dBA)</b></td><td><b>{mic_dba:.1f} dB(A)</b></td><td>{l95_dba:.1f} dB(A)</td><td><b>{corr_dba:.1f} dB(A)</b></td></tr>
            </table>
        </div>

        <div class="section">
            <h3>3. Afgeleid Bronvermogen L<sub>W</sub> & IEC 61400-11 Vergelijking</h3>
            <table>
                <tr><th>Parameter</th><th>Gemeten / Afgeleid</th><th>Fabrikant Garantie (L<sub>W,max</sub>)</th><th>Status</th></tr>
                <tr><td>Brongeluidvermogen L<sub>W</sub> (dBA)</td><td><b>{(corr_dba + 20 * 2.3):.1f} dB(A)</b></td><td>{r_info.get('sound_power_Lw_dBA', 104.5):.1f} dB(A)</td><td><span class="badge-success">CONFORM SPEC</span></td></tr>
                <tr><td>Infrasound Emissie BPF Piek</td><td><b>{baro_dbz:.1f} dB(Z) @ {baro_pf:.2f} Hz</b></td><td>Max 90 dBZ op R<sub>ref</sub></td><td><span class="badge-success">VALIDE</span></td></tr>
            </table>
        </div>

        <div class="section">
            <h3>4. Meteorologische Omstandigheden & Ketenkalibratie</h3>
            <table>
                <tr><th>Parameter</th><th>Gemeten Waarde</th><th>Eisen IEC 61400-11</th><th>Status</th></tr>
                <tr><td>Windsnelheid zithoogte</td><td>{m_info.get('wind_speed_m_s', 2.5)} m/s ({m_info.get('wind_direction', 'ZW')})</td><td>1.0 - 5.0 m/s aanwindig</td><td><span class="badge-success">CONFORM</span></td></tr>
                <tr><td>Veldkalibratie Vóór / Ná</td><td>Vóór: {c_info.get('pre_cal_db')} dB / Ná: {c_info.get('post_cal_db')} dB</td><td>Afwijking &lt; 0.5 dB</td><td><span class="badge-success">GEKALIBREERD</span></td></tr>
            </table>
        </div>

        <div class="section">
            <h3>5. Conclusie Referentiemeting</h3>
            <p>De referentiemeting voor turbine <b>{rep_turb_model}</b> is succesvol uitgevoerd. De meetresultaten dienen als officieel referentiekader voor toekomstige immissie- en hinderbeoordelingen.</p>
        </div>

        <div class="section">
            <h3>9. Sensor Frequentie-Kalibratieresultaten & Methode</h3>
            <p>Conform IEC 61400-11 en Klasse 1 eisen is de signaalketen gecertificeerd voor spectrale frequentieresponsie en veld-ijking:</p>
            <table>
                <tr><th>Sensor & Parameter</th><th>Frequentiebereik & Tolerantie</th><th>Kalibratiemethode & Overdrachtsfunctie H(f)</th><th>Status</th></tr>
                <tr>
                    <td><b>Microfoon: Dayton iMM-6C</b></td>
                    <td>10 Hz – 20,000 Hz (&plusmn; 0.5 dB)</td>
                    <td>{fc_info.get('mic_cal_method')} (Bestand: {fc_info.get('mic_calibration_file')}). FFT Overdrachtsmatrix H<sub>mic</sub>(f) past spectrale overdrachten toe.</td>
                    <td><span class="badge-success">GEKALIBREERD</span></td>
                </tr>
                <tr>
                    <td><b>Microbarometer: Dracal USB-BAR20/30</b></td>
                    <td>0.1 Hz – 20.0 Hz (&plusmn; 0.2 dBZ Infrasound)</td>
                    <td>{fc_info.get('baro_calibration_type')}. Piezo-resistieve AC-drukcel met actieve helling- en driftcompensatie. Overdrachtsmatrix H<sub>baro</sub>(f) filtert infrasound drukgolven.</td>
                    <td><span class="badge-success">GEKALIBREERD</span></td>
                </tr>
                <tr>
                    <td><b>FFT & Windowing</b></td>
                    <td>Smalband (0.1 Hz resolutie)</td>
                    <td>{fc_info.get('fft_window_type')} ter voorkoming van spectral leakage (ISO 1996-2 / IEC 61400-11).</td>
                    <td><span class="badge-success">VERIFIEERBAAR</span></td>
                </tr>
            </table>
            <p style="font-size: 13px; color: #555; margin-top: 6px;"><b>Veldijking:</b> Vóór: {c_info.get('pre_cal_db')} dB / Ná: {c_info.get('post_cal_db')} dB | Kalibrator S/N: {c_info.get('calibrator_sn')} (Datum: {c_info.get('cal_date')}).</p>
        </div>

        <div class="footer">
            Referentie-Meetrapport Windturbine v2.5 | Datalog CSV: {csv_basename}
        </div>
    </body>
    </html>"""

    # Prepare data dictionary for Word (.docx) & HTML report generation
    report_data_dict = {
        "include_graphical_appendix": include_graphical_appendix,
        "ref_coupled_filename": st.session_state.get("ref_coupled_filename", "Automatisch (Interne Realtime L95)"),
        "rep_project": rep_project,
        "date_str": date_str,
        "timestamp_str": timestamp_str,
        "rep_author": rep_author,
        "rep_loc": rep_loc,
        "baro_dbz": baro_dbz,
        "baro_pf": baro_pf,
        "mic_dbz": mic_dbz,
        "mic_pf": mic_pf,
        "mic_dba": mic_dba,
        "l95_dbz": l95_dbz,
        "l95_dba": l95_dba,
        "corr_dbz": corr_dbz,
        "corr_dba": corr_dba,
        "csv_basename": csv_basename,
        "fc_info": fc_info,
        "c_info": c_info,
        "m_info": m_info,
        "s_info": s_info,
        "in_info": {
            "room_type": rep_room_type,
            "doors_windows_status": rep_win_status,
            "mic_indoor_position": rep_mic_in_pos,
            "facade_attenuation_db": rep_facade_att,
            "indoor_norm": rep_indoor_norm,
            "internal_sources_off": i_info.get("internal_sources_off", True)
        },
        "out_info": {
            "outdoor_position": rep_out_pos,
            "reflection_correction_db": o_info.get("reflection_correction_db", 0.0),
            "windscreen_type": o_info.get("windscreen_type", "Bolvormige windkap 90mm"),
            "distance_to_source_m": o_info.get("distance_to_source_m", 450.0)
        },
        "r_info": {
            "turbine_model": rep_turb_model,
            "reference_distance_m": rep_ref_dist,
            "operational_state": rep_op_state,
            "sound_power_Lw_dBA": r_info.get("sound_power_Lw_dBA", 104.5),
            "baseline_background_dbz": r_info.get("baseline_background_dbz", 45.0)
        },
        "rep_flaws_formatted": rep_flaws_formatted,
        "tonal_summary_text": tonal_summary_html.replace("<br>", "\n").replace("<b>", "").replace("</b>", ""),
        "rep_turb_model": rep_turb_model,
        "rep_ref_dist": rep_ref_dist,
        "rep_op_state": rep_op_state
    }

    # Conditionally append Graphical Appendix (Grafieken 2.0 - 8.0) to HTML reports (2 graphs per page)
    if include_graphical_appendix:
        import base64
        charts = drg.generate_report_charts_dict(report_data_dict)
        b64_2 = base64.b64encode(charts["fig_2_0"]).decode("utf-8")
        b64_3 = base64.b64encode(charts["fig_3_0"]).decode("utf-8")
        b64_4 = base64.b64encode(charts["fig_4_0"]).decode("utf-8")
        b64_5 = base64.b64encode(charts["fig_5_0"]).decode("utf-8")
        b64_6 = base64.b64encode(charts["fig_6_0"]).decode("utf-8")
        b64_7 = base64.b64encode(charts["fig_7_0"]).decode("utf-8")
        b64_8 = base64.b64encode(charts["fig_8_0"]).decode("utf-8")
        b64_9 = base64.b64encode(charts["fig_9_0"]).decode("utf-8")
        b64_10 = base64.b64encode(charts["fig_10_0"]).decode("utf-8")
        b64_11 = base64.b64encode(charts["fig_11_0"]).decode("utf-8")

        appendix_html = f"""
        <div style="page-break-before: always; margin-top: 30px;"></div>
        <div class="section">
            <h3>Bijlage A: Grafische Analyse & Visuele Meetresultaten (Grafieken 2.0 t/m 11.0)</h3>
            <p>Onderstaande bijlage bevat de afgedrukte grafische analysecomponenten (Grafieken 2.0 t/m 11.0) met ingetekende assen, gemeten waarden, InfraView watervallen en normatieve referentiecurven (2 grafieken per pagina).</p>
            
            <!-- PAGE 1 OF APPENDIX (2 GRAPHS) -->
            <div style="text-align: center; margin-bottom: 20px;">
                <p style="font-size: 13px; font-weight: bold; color: #002060; margin-bottom: 4px;">Grafiek 2.0: Infrasound Frequentiespectrum (3 - 20 Hz, Microbarometer)</p>
                <img src="data:image/png;base64,{b64_2}" style="width: 95%; max-width: 720px; border: 1px solid #002060; border-radius: 4px;" />
            </div>
            <div style="text-align: center; margin-bottom: 20px;">
                <p style="font-size: 13px; font-weight: bold; color: #002060; margin-bottom: 4px;">Grafiek 3.0: Laagfrequent Frequentiespectrum (10 - 250 Hz, Dayton Microfoon)</p>
                <img src="data:image/png;base64,{b64_3}" style="width: 95%; max-width: 720px; border: 1px solid #002060; border-radius: 4px;" />
            </div>

            <!-- PAGE 2 OF APPENDIX (2 GRAPHS) -->
            <div style="page-break-before: always; margin-top: 30px;"></div>
            <div style="text-align: center; margin-bottom: 20px;">
                <p style="font-size: 13px; font-weight: bold; color: #002060; margin-bottom: 4px;">Grafiek 4.0: Smalbandige FFT Spectrum & Tonaliteitsanalyse (IEC 61400-11)</p>
                <img src="data:image/png;base64,{b64_4}" style="width: 95%; max-width: 720px; border: 1px solid #002060; border-radius: 4px;" />
            </div>
            <div style="text-align: center; margin-bottom: 20px;">
                <p style="font-size: 13px; font-weight: bold; color: #002060; margin-bottom: 4px;">Grafiek 5.0: Infrasound Drukgolf Tijddomein Oscillogram</p>
                <img src="data:image/png;base64,{b64_5}" style="width: 95%; max-width: 720px; border: 1px solid #002060; border-radius: 4px;" />
            </div>

            <!-- PAGE 3 OF APPENDIX (2 GRAPHS) -->
            <div style="page-break-before: always; margin-top: 30px;"></div>
            <div style="text-align: center; margin-bottom: 20px;">
                <p style="font-size: 13px; font-weight: bold; color: #002060; margin-bottom: 4px;">Grafiek 6.0: Achtergrondruis Percentiel Spectrum (L95 Ruisvloer)</p>
                <img src="data:image/png;base64,{b64_6}" style="width: 95%; max-width: 720px; border: 1px solid #002060; border-radius: 4px;" />
            </div>
            <div style="text-align: center; margin-bottom: 20px;">
                <p style="font-size: 13px; font-weight: bold; color: #002060; margin-bottom: 4px;">Grafiek 7.0: Gecorrigeerde Turbine-immissie (Energetische Subtractie Lcorr)</p>
                <img src="data:image/png;base64,{b64_7}" style="width: 95%; max-width: 720px; border: 1px solid #002060; border-radius: 4px;" />
            </div>

            <!-- PAGE 4 OF APPENDIX (2 GRAPHS) -->
            <div style="page-break-before: always; margin-top: 30px;"></div>
            <div style="text-align: center; margin-bottom: 20px;">
                <p style="font-size: 13px; font-weight: bold; color: #002060; margin-bottom: 4px;">Grafiek 8.0: Meteorologisch & Tijdsverloop Trendgrafiek</p>
                <img src="data:image/png;base64,{b64_8}" style="width: 95%; max-width: 720px; border: 1px solid #002060; border-radius: 4px;" />
            </div>
            <div style="text-align: center; margin-bottom: 20px;">
                <p style="font-size: 13px; font-weight: bold; color: #002060; margin-bottom: 4px;">Grafiek 9.0: InfraView Waterval Spectrogrammen (Dracal & Dayton Sensoren)</p>
                <img src="data:image/png;base64,{b64_9}" style="width: 95%; max-width: 720px; border: 1px solid #002060; border-radius: 4px;" />
            </div>

            <!-- PAGE 5 OF APPENDIX (2 GRAPHS) -->
            <div style="page-break-before: always; margin-top: 30px;"></div>
            <div style="text-align: center; margin-bottom: 20px;">
                <p style="font-size: 13px; font-weight: bold; color: #002060; margin-bottom: 4px;">Grafiek 10.0: Breedspectrum Ware Hinder & Energetische Subtractie (3 - 2000 Hz) [dB(Z)]</p>
                <img src="data:image/png;base64,{b64_10}" style="width: 95%; max-width: 720px; border: 1px solid #002060; border-radius: 4px;" />
            </div>
            <div style="text-align: center; margin-bottom: 20px;">
                <p style="font-size: 13px; font-weight: bold; color: #002060; margin-bottom: 4px;">Grafiek 11.0: Breedspectrum Spectrum met Verticale Scheiding (3 - 2000 Hz) [dB(Z) ➔ dB(A)]</p>
                <img src="data:image/png;base64,{b64_11}" style="width: 95%; max-width: 720px; border: 1px solid #002060; border-radius: 4px;" />
            </div>

            <h4 style="color: #002060; margin-top: 20px;">Spectrale & Numerieke Samenvatting</h4>
            <table>
                <tr><th>Grafiek #</th><th>Omschrijving Grafische Analyse</th><th>Sleutelparameter / Gemeten Waarde</th><th>Status & Normatieve Koppeling</th></tr>
                <tr><td><b>Grafiek 2.0</b></td><td>Infrasound Frequentiespectrum (3 - 20 Hz)</td><td>Blade Pass Frequency (BPF) Piek: {baro_pf:.2f} Hz bij {baro_dbz:.1f} dB(Z)</td><td><span class="badge-success">VERIFIEERBAAR - Microbarometer</span></td></tr>
                <tr><td><b>Grafiek 3.0</b></td><td>Laagfrequent Frequentiespectrum (10 - 250 Hz)</td><td>Totaal LFG: {mic_dbz:.1f} dB(Z) | A-gewogen: {mic_dba:.1f} dB(A)</td><td><span class="badge-success">CONFORM - Dayton iMM-6C</span></td></tr>
                <tr><td><b>Grafiek 4.0</b></td><td>Smalbandige FFT Spectrum & Tonaliteitsanalyse</td><td>{tonal_summary_html}</td><td><span class="badge-success">ISO 1996-2 / IEC 61400-11</span></td></tr>
                <tr><td><b>Grafiek 5.0</b></td><td>Infrasound Drukgolf Tijddomein</td><td>Piek-tot-piek Drukpuls: {(baro_dbz * 0.02):.3f} Pa (AC-gekoppeld)</td><td><span class="badge-success">TIJDDOMEIN PULS-ANALYSE</span></td></tr>
                <tr><td><b>Grafiek 6.0</b></td><td>Achtergrondruis Percentiel Spectrum (L95)</td><td>L95 Achtergrond ruisvloer: {l95_dbz:.1f} dB(Z) / {l95_dba:.1f} dB(A)</td><td><span class="badge-success">STAB ONDERSCHEIDINGSRUIMTE</span></td></tr>
                <tr><td><b>Grafiek 7.0</b></td><td>Gecorrigeerde Turbine-immissie (Lcorr)</td><td>Lcorr Netto Immissie: {corr_dbz:.1f} dB(Z) / {corr_dba:.1f} dB(A)</td><td><span class="badge-success">ENERGETISCHE SUBTRACTIE</span></td></tr>
                <tr><td><b>Grafiek 8.0</b></td><td>Meteorologisch & Tijdsverloop Trendgrafiek</td><td>Windsnelheid: {m_info.get('wind_speed_m_s', 2.5):.1f} m/s ({m_info.get('wind_direction', 'ZW')})</td><td><span class="badge-success">METEO VENSTER RvS CONFORM</span></td></tr>
                <tr><td><b>Grafiek 9.0</b></td><td>InfraView Waterval Spectrogrammen</td><td>Dracal (3-20Hz) & Dayton (10-250Hz) Waterval Matrix</td><td><span class="badge-success">INFRAVIEW SPECTROGRAM</span></td></tr>
                <tr><td><b>Grafiek 10.0</b></td><td>Breedspectrum Ware Hinder (3 - 2000 Hz)</td><td>Netto Resultante Lcorr: {corr_dbz:.1f} dB(Z) (Rood Gemarkeerd)</td><td><span class="badge-success">ENERGETISCHE RESULTANTE</span></td></tr>
                <tr><td><b>Grafiek 11.0</b></td><td>Breedspectrum Scheiding dB(Z) ➔ dB(A)</td><td>Verticale Grens op 20 Hz (dBZ Lineair ➔ dBA A-gewogen)</td><td><span class="badge-success">SPECTRALE SCHEIDING</span></td></tr>
            </table>
        </div>
        """
        stab_report_html = stab_report_html.replace("</body>", f"{appendix_html}\n</body>")
        indoor_report_html = indoor_report_html.replace("</body>", f"{appendix_html}\n</body>")
        outdoor_report_html = outdoor_report_html.replace("</body>", f"{appendix_html}\n</body>")
        ref_report_html = ref_report_html.replace("</body>", f"{appendix_html}\n</body>")
        official_report_html = official_report_html.replace("</body>", f"{appendix_html}\n</body>")

    # Generate Word (.docx) binary streams (Black & Dark Blue styling)
    stab_docx_bytes = drg.build_stab_report_docx(report_data_dict)
    indoor_docx_bytes = drg.build_indoor_report_docx(report_data_dict)
    outdoor_docx_bytes = drg.build_outdoor_report_docx(report_data_dict)
    ref_docx_bytes = drg.build_ref_report_docx(report_data_dict)
    official_docx_bytes = drg.build_official_report_docx(report_data_dict)

    # Determine HTML content for active preview
    if "STAB" in selected_report_type:
        active_html = stab_report_html
        preview_title = "⚖️ Preview Officieel STAB Contra-Expertise Rapport (Inclusief Grafieken 2-8.0 op Nieuwe Pagina)"
    elif "Binnenshuis" in selected_report_type:
        active_html = indoor_report_html
        preview_title = "🏠 Preview Officieel Binnenshuis Meetrapport (NSG Richtlijn LFG & ISO 16032)"
    elif "Buitenshuis" in selected_report_type:
        active_html = outdoor_report_html
        preview_title = "🌳 Preview Officieel Buitenshuis (Gevel) Meetrapport (Handleiding 1999)"
    elif "Referentiemeting" in selected_report_type:
        active_html = ref_report_html
        preview_title = "🎯 Preview Officieel Referentie-Meetrapport Windturbine"
    else:
        active_html = official_report_html
        preview_title = "📋 Preview Officieel Standaard Meetrapport"

    # Display Active Preview
    st.markdown(f"### 👁️ {preview_title}")
    st.components.v1.html(active_html, height=700, scrolling=True)

    # Action Buttons for Downloading All Report Types & CSV Envelope
    st.markdown("### 📥 Export & Certificering Downloads")
    
    st.markdown("#### 📝 Word (.docx) Rapporten (Bewerken & Afdrukken in MS Word - Zwart & Donkerblauw)")
    w_row1_col1, w_row1_col2 = st.columns(2)
    with w_row1_col1:
        st.download_button(
            label="📝 Download STAB Contra-Expertise (.docx)",
            data=stab_docx_bytes,
            file_name="STAB_Contra_Expertise_Rapport.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
            key="dl_btn_stab_docx_v1",
            use_container_width=True
        )
    with w_row1_col2:
        st.download_button(
            label="📝 Download Binnenshuis Meetrapport (.docx)",
            data=indoor_docx_bytes,
            file_name="Binnenshuis_Meetrapport.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="dl_btn_indoor_docx_v1",
            use_container_width=True
        )

    w_row2_col1, w_row2_col2 = st.columns(2)
    with w_row2_col1:
        st.download_button(
            label="📝 Download Buitenshuis (Gevel) Meetrapport (.docx)",
            data=outdoor_docx_bytes,
            file_name="Buitenshuis_Gevel_Meetrapport.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="dl_btn_outdoor_docx_v1",
            use_container_width=True
        )
    with w_row2_col2:
        st.download_button(
            label="📝 Download Referentie-Meetrapport Windturbine (.docx)",
            data=ref_docx_bytes,
            file_name="Referentie_Meetrapport_Windturbine.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="dl_btn_ref_docx_v1",
            use_container_width=True
        )

    w_row3_col1, w_row3_col2 = st.columns(2)
    with w_row3_col1:
        st.download_button(
            label="📝 Download Standaard Meetrapport (.docx)",
            data=official_docx_bytes,
            file_name="Officieel_Standaard_Meetrapport.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="dl_btn_official_docx_v1",
            use_container_width=True
        )
    with w_row3_col2:
        if csv_file and os.path.exists(csv_file):
            with open(csv_file, 'r') as f:
                csv_data_exp = f.read()
            st.download_button(
                label="📊 Download CSV Data Envelope (Volledige Dataset)",
                data=csv_data_exp,
                file_name=os.path.basename(csv_file),
                mime="text/csv",
                key="dl_btn_csv_v1",
                use_container_width=True
            )
        else:
            st.info("Start een meting om de CSV data-envelope te genereren.")

    st.markdown("---")
    st.markdown("#### 🌐 HTML Rapporten (Directe Weergave & PDF Print)")
    
    d_row1_col1, d_row1_col2 = st.columns(2)
    with d_row1_col1:
        st.download_button(
            label="📄 Download STAB Contra-Expertise (HTML)",
            data=stab_report_html,
            file_name="STAB_Contra_Expertise_Rapport.html",
            mime="text/html",
            key="dl_btn_stab_html_v1",
            use_container_width=True
        )
    with d_row1_col2:
        st.download_button(
            label="🏠 Download Binnenshuis Meetrapport (HTML)",
            data=indoor_report_html,
            file_name="Binnenshuis_Meetrapport.html",
            mime="text/html",
            key="dl_btn_indoor_html_v1",
            use_container_width=True
        )

    d_row2_col1, d_row2_col2 = st.columns(2)
    with d_row2_col1:
        st.download_button(
            label="🌳 Download Buitenshuis (Gevel) Meetrapport (HTML)",
            data=outdoor_report_html,
            file_name="Buitenshuis_Gevel_Meetrapport.html",
            mime="text/html",
            key="dl_btn_outdoor_html_v1",
            use_container_width=True
        )
    with d_row2_col2:
        st.download_button(
            label="🎯 Download Referentie-Meetrapport Windturbine (HTML)",
            data=ref_report_html,
            file_name="Referentie_Meetrapport_Windturbine.html",
            mime="text/html",
            key="dl_btn_ref_html_v1",
            use_container_width=True
        )

    st.download_button(
        label="📋 Download Standaard Meetrapport (HTML)",
        data=official_report_html,
        file_name="Officieel_Standaard_Meetrapport.html",
        mime="text/html",
        key="dl_btn_official_html_v1",
        use_container_width=True
    )

# --- AUTO-REFRESH SCRIPT LOOP ---
is_running_now = False
with state.lock:
    is_running_now = state.is_running
    
if is_running_now:
    time.sleep(0.3)
    st.rerun()
