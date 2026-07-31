import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import os
import sys
import subprocess

# Ensure the app directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from measurement_engine import SharedState, MeasurementEngine

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
    
    /* Enhance visibility for all labels, help texts, and options in the sidebar */
    .css-1dp5yyx, .css-81oif8, .stWidgetLabel, label, p {
        color: #c9d1d9 !important;
    }
    
    .stMarkdown p, .stMarkdown li, span {
        color: #c9d1d9;
    }
    
    /* Small help tooltips and description texts */
    .stMarkdown p > em, .stMarkdown p > small, .css-1pq4zsx, [data-testid="stWidgetLabel-help"] {
        color: #8b949e !important;
    }

    /* Target Streamlit tab buttons for visibility */
    button[data-baseweb="tab"] {
        color: #8b949e !important;
    }
    button[data-baseweb="tab"] p, button[data-baseweb="tab"] span {
        color: #8b949e !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #58a6ff !important;
        font-weight: bold !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] p, button[data-baseweb="tab"][aria-selected="true"] span {
        color: #58a6ff !important;
        font-weight: bold !important;
        border-bottom-color: #58a6ff !important;
    }
    button[data-baseweb="tab"]:hover, button[data-baseweb="tab"]:hover p, button[data-baseweb="tab"]:hover span {
        color: #c9d1d9 !important;
    }

    /* Target disabled forms / sidebars */
    [disabled], .stWidgetForm [disabled], [data-testid="stSidebar"] [disabled] {
        color: #8b949e !important;
        -webkit-text-fill-color: #8b949e !important;
        opacity: 0.65 !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to locate external InfraView / Dracal executables
def find_infraview_exe():
    candidates = [
        r"C:\Program Files\Dracal\DracalView.exe",
        r"C:\Program Files (x86)\Dracal\DracalView.exe",
        r"C:\Program Files\Dracal\Cmd\dracal-usb-get.exe",
        r"C:\Program Files (x86)\Dracal\Cmd\dracal-usb-get.exe",
        r"C:\Program Files\IrfanView\i_view64.exe",
        r"C:\Program Files (x86)\IrfanView\i_view32.exe"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

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

# --- SIDEBAR CONFIGURATION ---
st.sidebar.markdown("## 🛠️ Besturing & Configuratie")

# Start/Stop Button
if not state.is_running:
    start_btn = st.sidebar.button("▶️ Start Meting", type="primary", use_container_width=True)
    stop_btn = False
else:
    start_btn = False
    stop_btn = st.sidebar.button("⏹️ Stop Meting", type="secondary", use_container_width=True)

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

# --- INFRAVIEW & EXTERNAL TOOLS SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 InfraView & Software Launchers")
infra_exe = find_infraview_exe()
if infra_exe:
    st.sidebar.success(f"Detectie: {os.path.basename(infra_exe)}")
    if st.sidebar.button("🚀 Start External InfraView / DracalView", use_container_width=True):
        try:
            subprocess.Popen([infra_exe])
            st.sidebar.info("InfraView / DracalView gestart!")
        except Exception as e:
            st.sidebar.error(f"Fout bij starten: {e}")
else:
    st.sidebar.warning("DracalView / InfraView executable niet gedetecteerd.")
    if st.sidebar.button("📦 Installeer Dracal & InfraView Tools", use_container_width=True):
        inst_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DracalUtilities-3.7.0.exe")
        if os.path.exists(inst_path):
            try:
                subprocess.Popen([inst_path])
                st.sidebar.info("Installer gestart! Volg de stappen op het scherm van uw laptop.")
            except Exception as e:
                st.sidebar.error(f"Fout: {e}")
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
    st.markdown("##### 💾 Datalogger")
    status_str = ""
    with state.lock:
        status_str = state.log_status
    if "Logged" in status_str or "active" in status_str:
        st.markdown(f'<span class="status-badge status-running">{status_str}</span>', unsafe_allow_html=True)
    elif "Error" in status_str:
        st.markdown(f'<span class="status-badge status-stopped">{status_str}</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'<span class="status-badge status-stopped">{status_str}</span>', unsafe_allow_html=True)

st.markdown("---")

# 2. Row: Metrics Cards
cols_metrics = st.columns(4)

with cols_metrics[0]:
    val_str = "---"
    with state.lock:
        if state.is_running:
            val_str = f"{state.baro_dbz_overall:.1f} dBZ"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Infrasound Niveau (3 - 20 Hz)</div>
        <div class="metric-val">{val_str}</div>
    </div>
    """, unsafe_allow_html=True)

with cols_metrics[1]:
    val_str = "---"
    with state.lock:
        if state.is_running:
            val_str = f"{state.baro_peak_freq:.2f} Hz"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Infrasound Piekfrequentie</div>
        <div class="metric-val" style="color: #ff7b72;">{val_str}</div>
    </div>
    """, unsafe_allow_html=True)

with cols_metrics[2]:
    val_str = "---"
    with state.lock:
        if state.is_running:
            val_str = f"{state.mic_dbz_overall:.1f} dBZ / {state.mic_dba_overall:.1f} dBA"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Laagfrequent (Dayton, >=10 Hz)</div>
        <div class="metric-val" style="color: #79c0ff;">{val_str}</div>
    </div>
    """, unsafe_allow_html=True)

with cols_metrics[3]:
    val_str = "---"
    with state.lock:
        if state.is_running:
            val_str = f"{state.mic_peak_freq:.1f} Hz"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Laagfrequent Piekfrequentie</div>
        <div class="metric-val" style="color: #d29922;">{val_str}</div>
    </div>
    """, unsafe_allow_html=True)

# 3. Main Dashboard Tabs
tabs = st.tabs([
    "📊 Live Spectrogrammen", 
    "🔍 InfraView Inspector & Waterfall", 
    "📈 Drukgolven (Tijddomein)", 
    "🎯 Tonaliteit (IEC 61400-11)", 
    "📂 Historie & Logs"
])

# Tab 1: Live Spectrograms
with tabs[0]:
    col_chart_left, col_chart_right = st.columns(2)
    
    with col_chart_left:
        st.subheader("Infrasound Frequentiespectrum (3 - 20 Hz)")
        st.markdown("*Gemeten met de Dracal microbarometer*")
        
        fig_baro = go.Figure()
        
        freqs_baro = np.array([])
        dbz_baro = np.array([])
        with state.lock:
            freqs_baro = state.baro_freqs.copy()
            dbz_baro = state.baro_dbz_spectrum.copy()
            
        if len(freqs_baro) > 0 and len(dbz_baro) > 0:
            fig_baro.add_trace(go.Scatter(
                x=freqs_baro, 
                y=dbz_baro, 
                mode='lines',
                line=dict(color='#ff7b72', width=2),
                name='dBZ (Lineair)'
            ))
            
            peak_f = 0.0
            peak_db = -100.0
            with state.lock:
                peak_f = state.baro_peak_freq
                peak_db = state.baro_peak_dbz
            if peak_f > 0:
                fig_baro.add_trace(go.Scatter(
                    x=[peak_f],
                    y=[peak_db],
                    mode='markers',
                    marker=dict(color='yellow', size=10, symbol='star'),
                    name=f'Piek: {peak_f:.2f} Hz ({peak_db:.1f} dBZ)'
                ))
        else:
            fig_baro.add_annotation(text="Start meting om spectraaldata te tonen", showarrow=False, font=dict(size=16, color="#8b949e"))
            
        fig_baro.update_layout(
            template="plotly_dark",
            font=dict(color='#c9d1d9'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=20, t=10, b=40),
            xaxis=dict(title="Frequentie (Hz)", range=[0.5, 25.0], showgrid=True, gridcolor='#30363d'),
            yaxis=dict(title="Geluidsdrukniveau (dBZ ref 2e-5 Pa)", range=[30, 110], showgrid=True, gridcolor='#30363d'),
            height=450,
            showlegend=True
        )
        st.plotly_chart(fig_baro, use_container_width=True, theme=None, key="baro_spec_chart")
        
    with col_chart_right:
        st.subheader("Laagfrequent Frequentiespectrum (10 - 250 Hz)")
        st.markdown("*Gemeten met de Dayton iMM-6C microfoon*")
        
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
                fig_mic.add_trace(go.Scatter(
                    x=freqs_mic[disp_idx], 
                    y=dbz_mic[disp_idx], 
                    mode='lines',
                    line=dict(color='#58a6ff', width=2),
                    name='dBZ (Lineair)'
                ))
                fig_mic.add_trace(go.Scatter(
                    x=freqs_mic[disp_idx], 
                    y=dba_mic[disp_idx], 
                    mode='lines',
                    line=dict(color='#d29922', width=1.5, dash='dash'),
                    name='dBA (A-gewogen)'
                ))
                
                pf = 0.0
                pdb = -100.0
                with state.lock:
                    pf = state.mic_peak_freq
                    pdb = state.mic_peak_dbz
                if pf > 0:
                    fig_mic.add_trace(go.Scatter(
                        x=[pf],
                        y=[pdb],
                        mode='markers',
                        marker=dict(color='yellow', size=10, symbol='star'),
                        name=f'Piek: {pf:.1f} Hz ({pdb:.1f} dBZ)'
                    ))
        else:
            fig_mic.add_annotation(text="Start meting om spectraaldata te tonen", showarrow=False, font=dict(size=16, color="#8b949e"))
            
        fig_mic.update_layout(
            template="plotly_dark",
            font=dict(color='#c9d1d9'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=20, t=10, b=40),
            xaxis=dict(title="Frequentie (Hz)", range=[10.0, 250.0], showgrid=True, gridcolor='#30363d'),
            yaxis=dict(title="Geluidsdrukniveau (dB ref 2e-5 Pa)", range=[10, 80], showgrid=True, gridcolor='#30363d'),
            height=450,
            showlegend=True
        )
        st.plotly_chart(fig_mic, use_container_width=True, theme=None, key="mic_spec_chart")

# Tab 2: InfraView Inspector & Waterfall Plotter
with tabs[1]:
    st.subheader("🔍 InfraView Waterfall Spectrogram & Multi-dimensional Analysis")
    st.markdown("Geavanceerde waterval-visualisatie (Tijd x Frequentie x dBZ) voor het opsporen van constante tonen en temporele variaties.")
    
    # Action Bar for External InfraView
    col_infra1, col_infra2 = st.columns([3, 1])
    with col_infra1:
        st.info("💡 **InfraView Integratie:** U kunt dit in-app 3D waterfall-systeem gebruiken óf met 1-klik de externe DracalView/InfraView applicatie starten.")
    with col_infra2:
        if infra_exe:
            if st.button("🚀 Open External InfraView", type="primary", use_container_width=True):
                try:
                    subprocess.Popen([infra_exe])
                    st.success("InfraView gestart!")
                except Exception as e:
                    st.error(f"Fout: {e}")
        else:
            if st.button("📦 Installeer InfraView Software", use_container_width=True):
                inst_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DracalUtilities-3.7.0.exe")
                if os.path.exists(inst_path):
                    subprocess.Popen([inst_path])
                    st.info("Installer gestart!")

    st.markdown("---")
    
    # Controls for Waterfall
    col_w_ctrl1, col_w_ctrl2, col_w_ctrl3 = st.columns(3)
    with col_w_ctrl1:
        wf_channel = st.selectbox("Selecteer Signaalkanaal", ["Dracal Microbarometer (3 - 20 Hz Infrasound)", "Dayton iMM-6 Microfoon (10 - 250 Hz LFG)"])
    with col_w_ctrl2:
        wf_render_mode = st.selectbox("Visualisatietype", ["2D Heatmap Spectrogram", "3D Surface Waterfall"])
    with col_w_ctrl3:
        colorscale_choice = st.selectbox("Kleurenpalet (Colorscale)", ["Viridis", "Plasma", "Inferno", "Turbo", "Thermal"])

    # Prepare data for Waterfall
    wf_times = []
    wf_matrix = []
    wf_freqs = []
    
    with state.lock:
        if "Dracal" in wf_channel:
            wf_times = list(state.baro_waterfall_times)
            wf_matrix = list(state.baro_waterfall_matrix)
            wf_freqs = list(state.baro_freqs)
        else:
            wf_times = list(state.mic_waterfall_times)
            wf_matrix = list(state.mic_waterfall_matrix)
            wf_freqs = list(state.mic_freqs)

    if len(wf_matrix) > 0 and len(wf_freqs) > 0:
        z_data = np.array(wf_matrix)
        
        if wf_render_mode == "2D Heatmap Spectrogram":
            fig_wf = go.Figure(data=go.Heatmap(
                z=z_data,
                x=wf_freqs,
                y=wf_times,
                colorscale=colorscale_choice.lower(),
                colorbar=dict(title="dBZ Niveau")
            ))
            fig_wf.update_layout(
                template="plotly_dark",
                font=dict(color='#c9d1d9'),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=50, r=20, t=10, b=50),
                xaxis=dict(title="Frequentie (Hz)", showgrid=True, gridcolor='#30363d'),
                yaxis=dict(title="Tijdstempel (Verstreken)", showgrid=True, gridcolor='#30363d'),
                height=500
            )
        else:
            fig_wf = go.Figure(data=[go.Surface(
                z=z_data,
                x=wf_freqs,
                y=np.arange(len(wf_times)),
                colorscale=colorscale_choice.lower()
            )])
            fig_wf.update_layout(
                template="plotly_dark",
                font=dict(color='#c9d1d9'),
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10),
                scene=dict(
                    xaxis_title='Frequentie (Hz)',
                    yaxis_title='Tijd (Samples)',
                    zaxis_title='Geluidsniveau (dBZ)',
                    camera=dict(eye=dict(x=1.5, y=-1.5, z=1.2))
                ),
                height=550
            )
            
        st.plotly_chart(fig_wf, use_container_width=True, theme=None, key="infraview_wf_chart")
    else:
        st.info("💡 Start de meting via het zijpaneel om live data op te bouwen in de InfraView waterfall-spectrogram.")

# Tab 3: Waveform Oscilloscope
with tabs[2]:
    st.subheader("Micro-drukschommelingen in Infrasoundgebied (Tijddomein)")
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
            fig_w_raw.add_trace(go.Scatter(
                x=t_baro, 
                y=p_raw, 
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
                yaxis=dict(title="Absolute Druk (Pascal)", tickformat=".2f", showgrid=True, gridcolor='#30363d'),
                height=350
            )
        else:
            fig_w_raw.add_annotation(text="Start meting om data te tonen", showarrow=False, font=dict(color="#8b949e"))
        st.plotly_chart(fig_w_raw, use_container_width=True, theme=None, key="raw_wave_chart")
        
    with col_w2:
        st.markdown("#### 2. Gefilterde Infrasoundgolf (>0.5 Hz High-pass)")
        fig_w_filt = go.Figure()
        if len(t_baro) > 0 and len(p_filt) > 0:
            fig_w_filt.add_trace(go.Scatter(
                x=t_baro, 
                y=p_filt, 
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
                yaxis=dict(title="Dynamische Druk (Pascal AC)", tickformat=".4f", showgrid=True, gridcolor='#30363d'),
                height=350
            )
        else:
            fig_w_filt.add_annotation(text="Start meting om data te tonen", showarrow=False, font=dict(color="#8b949e"))
        st.plotly_chart(fig_w_filt, use_container_width=True, theme=None, key="filt_wave_chart")

# Tab 4: Tonality Analysis (IEC 61400-11)
with tabs[3]:
    st.subheader("Smalbandige Tonaliteitsanalyse conform IEC 61400-11")
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
                st.warning(f"⚠️ **PROMINENTE TOON GEDETECTEERD!** Frequentie: **{pt['freq']:.1f} Hz** | Hoorbaarheid ($\Delta L_{{ta}}$): **{pt['audibility']:.1f} dB** | Straffactor (Penalty): **{pt['penalty']:.1f} dB**")
        else:
            st.success("✅ Geen prominente tonale componenten gedetecteerd (alle gedetecteerde pieken hebben $\Delta L_{ta} < 4$ dB).")
            
        df_tones = pd.DataFrame(tones_list)
        df_tones.columns = ["Frequentie (Hz)", "Toonniveau (dBZ)", "Hoorbaarheid Delta L_ta (dB)", "Toeslag / Penalty (dB)"]
        df_tones = df_tones.round(2)
        
        st.dataframe(df_tones, use_container_width=True, hide_index=True)
    else:
        st.info("Start meting en zorg dat de Dayton microfoon live data ontvangt om de tonaliteitsanalyse uit te voeren.")

# Tab 5: History & Logs
with tabs[4]:
    st.subheader("Historische logs en CSV Export")
    
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
                
                st.markdown("### Verloop over de tijd")
                fig_hist = go.Figure()
                
                fig_hist.add_trace(go.Scatter(
                    x=df_log["Tijdstempel"],
                    y=df_log["Barometer dBZ (Infrasound)"],
                    mode='lines+markers',
                    line=dict(color='#ff7b72', width=2),
                    name='Infrasound (3-20 Hz) [dBZ]'
                ))
                
                fig_hist.add_trace(go.Scatter(
                    x=df_log["Tijdstempel"],
                    y=df_log["Microfoon dBZ (LFG)"],
                    mode='lines+markers',
                    line=dict(color='#58a6ff', width=1.5),
                    name='Microfoon dBZ (LFG)'
                ))
                
                fig_hist.add_trace(go.Scatter(
                    x=df_log["Tijdstempel"],
                    y=df_log["Microfoon dBA (Hoorbaar)"],
                    mode='lines+markers',
                    line=dict(color='#d29922', width=1.5),
                    name='Microfoon dBA'
                ))
                
                fig_hist.update_layout(
                    template="plotly_dark",
                    font=dict(color='#c9d1d9'),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=40, r=20, t=10, b=40),
                    xaxis=dict(title="Tijdstempel", showgrid=True, gridcolor='#30363d'),
                    yaxis=dict(title="Geluidsniveau (dB)", showgrid=True, gridcolor='#30363d'),
                    height=400,
                    showlegend=True
                )
                st.plotly_chart(fig_hist, use_container_width=True, theme=None, key="hist_trend_chart")
                
        except Exception as e:
            st.error(f"Fout bij openen logbestand: {e}")
    else:
        st.info("Logbestanden verschijnen hier zodra de meting is gestart en de eerste logging-minuut is verstreken.")

# --- AUTO-REFRESH SCRIPT LOOP ---
is_running_now = False
with state.lock:
    is_running_now = state.is_running
    
if is_running_now:
    time.sleep(0.3)
    st.rerun()
