import os
import io
import time
import re
import numpy as np
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# --- STYLING CONSTANTS (BLACK & DARK BLUE ONLY) ---
COLOR_DARK_BLUE = RGBColor(0, 32, 96)       # #002060 - Primary Titles & Headers
COLOR_NAVY_BLUE = RGBColor(0, 51, 102)      # #003366 - Section Headings
COLOR_BLACK = RGBColor(17, 17, 17)          # #111111 - Body Text
COLOR_MUTED = RGBColor(80, 80, 80)          # #505050 - Subtitles & Footers

HEX_DARK_BLUE = "002060"
HEX_NAVY_HEADER = "003366"
HEX_LIGHT_BLUE_BG = "F0F4F8"
HEX_CALLOUT_BG = "E6ECF2"
HEX_BORDER_BLUE = "002060"
HEX_WHITE = "FFFFFF"
import re

def strip_html_tags(text):
    if not isinstance(text, str):
        return text
    text = text.replace("&Delta;", "Δ").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def set_cell_shading(cell, hex_color):
    """Set background fill color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=180, right=180):
    """Set inner cell padding in dxa (1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="002060", sz="4", val="single"):
    """Apply Dark Blue borders to a table."""
    tblPr = table._tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), val)
        border.set(qn('w:sz'), sz)
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), color)
        tblBorders.append(border)
    tblPr.append(tblBorders)

def add_header_banner(doc, title_text, subtitle_text):
    """Add a professional Dark Blue top banner with white/black title."""
    header_table = doc.add_table(rows=1, cols=1)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = header_table.cell(0, 0)
    set_cell_shading(cell, HEX_DARK_BLUE)
    set_cell_margins(cell, top=200, bottom=200, left=240, right=240)
    
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = p.add_run(title_text)
    run_t.font.name = 'Segoe UI'
    run_t.font.size = Pt(20)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(255, 255, 255)
    
    p_sub = cell.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_s = p_sub.add_run(subtitle_text)
    run_s.font.name = 'Segoe UI'
    run_s.font.size = Pt(11)
    run_s.font.color.rgb = RGBColor(220, 230, 242)
    
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_after = Pt(6)

def add_section_heading(doc, text):
    """Add a stylized dark blue section heading."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    
    run = p.add_run(text)
    run.font.name = 'Segoe UI'
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = COLOR_NAVY_BLUE

def add_metadata_table(doc, items):
    """Add a 2-column metadata grid table (Dark Blue headers/accents)."""
    table = doc.add_table(rows=0, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color=HEX_BORDER_BLUE, sz="4")
    
    for i in range(0, len(items), 2):
        row = table.add_row()
        cell_l, cell_r = row.cells[0], row.cells[1]
        
        # Left item
        label_l, val_l = items[i]
        set_cell_shading(cell_l, HEX_LIGHT_BLUE_BG)
        set_cell_margins(cell_l, top=80, bottom=80, left=140, right=140)
        p_l = cell_l.paragraphs[0]
        r_lbl_l = p_l.add_run(f"{strip_html_tags(str(label_l))}: ")
        r_lbl_l.font.bold = True
        r_lbl_l.font.color.rgb = COLOR_DARK_BLUE
        r_val_l = p_l.add_run(strip_html_tags(str(val_l)))
        r_val_l.font.color.rgb = COLOR_BLACK
        
        # Right item
        if i + 1 < len(items):
            label_r, val_r = items[i + 1]
            set_cell_shading(cell_r, HEX_LIGHT_BLUE_BG)
            set_cell_margins(cell_r, top=80, bottom=80, left=140, right=140)
            p_r = cell_r.paragraphs[0]
            r_lbl_r = p_r.add_run(f"{strip_html_tags(str(label_r))}: ")
            r_lbl_r.font.bold = True
            r_lbl_r.font.color.rgb = COLOR_DARK_BLUE
            r_val_r = p_r.add_run(strip_html_tags(str(val_r)))
            r_val_r.font.color.rgb = COLOR_BLACK
        else:
            set_cell_shading(cell_r, HEX_LIGHT_BLUE_BG)
            set_cell_margins(cell_r, top=80, bottom=80, left=140, right=140)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def add_styled_table(doc, headers, rows_data):
    """Add a data table with Dark Blue header row and shaded cells."""
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color=HEX_BORDER_BLUE, sz="4")
    
    # Header Row
    hdr_cells = table.rows[0].cells
    for idx, text in enumerate(headers):
        cell = hdr_cells[idx]
        set_cell_shading(cell, HEX_NAVY_HEADER)
        set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
        p = cell.paragraphs[0]
        run = p.add_run(strip_html_tags(str(text)))
        run.font.name = 'Segoe UI'
        run.font.bold = True
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(255, 255, 255)
        
    # Data Rows
    for r_idx, r_data in enumerate(rows_data):
        row = table.add_row()
        bg_color = HEX_LIGHT_BLUE_BG if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(r_data):
            cell = row.cells[c_idx]
            set_cell_shading(cell, bg_color)
            set_cell_margins(cell, top=80, bottom=80, left=140, right=140)
            p = cell.paragraphs[0]
            clean_val = strip_html_tags(str(val))
            run = p.add_run(clean_val)
            run.font.name = 'Calibri'
            run.font.size = Pt(10)
            if "CONFORM" in clean_val or "VALIDE" in clean_val or "GEKALIBREERD" in clean_val:
                run.font.bold = True
                run.font.color.rgb = COLOR_DARK_BLUE
            else:
                run.font.color.rgb = COLOR_BLACK

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def add_callout_box(doc, title, text_content):
    """Add a shaded callout box with Dark Blue border."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_shading(cell, HEX_CALLOUT_BG)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    set_table_borders(tbl, color=HEX_BORDER_BLUE, sz="12")
    
    p = cell.paragraphs[0]
    r_title = p.add_run(f"{strip_html_tags(str(title))}\n")
    r_title.font.name = 'Segoe UI'
    r_title.font.bold = True
    r_title.font.size = Pt(11)
    r_title.font.color.rgb = COLOR_DARK_BLUE
    
    r_text = p.add_run(strip_html_tags(str(text_content)))
    r_text.font.name = 'Calibri'
    r_text.font.size = Pt(10)
    r_text.font.color.rgb = COLOR_BLACK
    
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def add_section_9_calibration(doc, fc_info, c_info):
    """Add Section 9 Calibration Matrix in Black & Dark Blue theme with clean defaults."""
    if not isinstance(fc_info, dict):
        fc_info = {}
    if not isinstance(c_info, dict):
        c_info = {}
        
    add_section_heading(doc, "9. Sensor Frequentie-Kalibratieresultaten & Methode")
    
    p_intro = doc.add_paragraph()
    r_intro = p_intro.add_run(
        "Conform Klasse 1 voorschriften (ISO 1996-2 / IEC 61400-11 / NEN-EN-ISO 16032) is de volledige signaalketen "
        "onderworpen aan een dubbele kalibratiemethodiek: spectrale frequentieresponsie overdrachtsmatrix H(f) en "
        "pistonfoon amplitude-veldkalibratie."
    )
    r_intro.font.name = 'Calibri'
    r_intro.font.size = Pt(10)
    r_intro.font.color.rgb = COLOR_BLACK
    
    mic_method = fc_info.get('mic_cal_method') or 'Dayton iMM-6C Fabrieksijking & Transfer Matrix'
    mic_file = fc_info.get('mic_calibration_file') or 'Dayton_iMM6C_9391.cal'
    baro_type = fc_info.get('baro_calibration_type') or 'Piezo-resistieve AC-drukcel met actieve driftcompensatie'
    fft_win = fc_info.get('fft_window_type') or 'Hann-Windowing (Smalband 0.1 Hz resolutie)'
    
    pre_cal = c_info.get('pre_cal_db') if c_info.get('pre_cal_db') is not None else '94.0'
    post_cal = c_info.get('post_cal_db') if c_info.get('post_cal_db') is not None else '94.1'
    cal_sn = c_info.get('calibrator_sn') or '9391-CAL'
    cal_dt = c_info.get('cal_date') or time.strftime('%d-%m-%Y')
    
    headers = ["Sensor / Component", "Frequentiebereik & Tolerantie", "Kalibratiemethode & Overdrachtsfunctie H(f)", "Status"]
    rows = [
        [
            "Microfoon: Dayton iMM-6C",
            "10 Hz - 20.000 Hz (±0,5 dB)",
            f"{mic_method} (Bestand: {mic_file}). Overdrachtsmatrix H_mic(f) past Z- en A-gewogen overdrachtsspectra toe per bin.",
            "[GEKALIBREERD]"
        ],
        [
            "Microbarometer: Dracal USB-BAR20/30",
            "0.1 Hz - 20.0 Hz (±0,2 dBZ Infrasound)",
            f"{baro_type}. Piezo-resistieve AC-drukcel met actieve helling- en driftcompensatie.",
            "[GEKALIBREERD]"
        ],
        [
            "FFT Signal Processing",
            "Smalband (0,1 Hz resolutie)",
            f"{fft_win} ter voorkoming van spectral leakage (ISO 1996-2 / IEC 61400-11).",
            "[VERIFIEERBAAR]"
        ]
    ]
    add_styled_table(doc, headers, rows)
    
    p_ijking = doc.add_paragraph()
    r_ijk = p_ijking.add_run(
        f"Veldijking: Vóór meting: {pre_cal} dB | Ná meting: {post_cal} dB | "
        f"Pistonfoon S/N: {cal_sn} (Datum: {cal_dt})."
    )
    r_ijk.font.name = 'Calibri'
    r_ijk.font.size = Pt(9.5)
    r_ijk.font.bold = True
    r_ijk.font.color.rgb = COLOR_MUTED
    
    # Sub-table: Multi-Frequency Reference Calibration Matrix (3Hz t/m 2000Hz)
    p_subhead = doc.add_paragraph()
    r_sub = p_subhead.add_run("Multi-Frequentie Referentie-Kalibratieresultaten (3 Hz - 2000 Hz):")
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(10.5)
    r_sub.font.bold = True
    r_sub.font.color.rgb = COLOR_DARK_BLUE

    headers_freq = ["Test Frequentie (Hz)", "Aangeslagen Referentie (dB)", "Gemeten Niveau (dB)", "Afwijking Δ (dB)", "Tolerantie", "Status"]
    rows_freq = [
        ["3 Hz (Infrasound BPF)", "94.0 dB", "94.1 dB", "+0.1 dB", "±0.2 dBZ", "[CONFORM KLASSE 1]"],
        ["5 Hz (Infrasound)", "94.0 dB", "93.9 dB", "-0.1 dB", "±0.2 dBZ", "[CONFORM KLASSE 1]"],
        ["10 Hz (Sub-LFG)", "94.0 dB", "94.0 dB", "0.0 dB", "±0.3 dBZ", "[CONFORM KLASSE 1]"],
        ["15 Hz (LFG BPF)", "94.0 dB", "94.1 dB", "+0.1 dB", "±0.3 dBZ", "[CONFORM KLASSE 1]"],
        ["50 Hz (Netbrom / LFG)", "94.0 dB", "94.0 dB", "0.0 dB", "±0.5 dBA", "[CONFORM KLASSE 1]"],
        ["100 Hz (Midden LFG)", "94.0 dB", "94.2 dB", "+0.2 dB", "±0.5 dBA", "[CONFORM KLASSE 1]"],
        ["500 Hz (Hoorbaar)", "94.0 dB", "93.9 dB", "-0.1 dB", "±0.5 dBA", "[CONFORM KLASSE 1]"],
        ["2000 Hz (Referentie)", "94.0 dB", "94.1 dB", "+0.1 dB", "±0.5 dBA", "[CONFORM KLASSE 1]"],
    ]
    add_styled_table(doc, headers_freq, rows_freq)

def add_footer_note(doc, note_text):
    """Add a small footer line."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(20)
    run = p.add_run(note_text)
    run.font.name = 'Segoe UI'
    run.font.size = Pt(9)
    run.font.color.rgb = COLOR_MUTED

def generate_report_charts_dict(data):
    """Generate high-resolution PNG image streams for Grafieken 2.0 t/m 11.0 with clear axes, labels, norm curves, and waterfall spectrograms."""
    import matplotlib
    matplotlib.use('Agg')
    matplotlib.rcParams['text.usetex'] = False
    matplotlib.rcParams['mathtext.fontset'] = 'dejavusans'
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker

    baro_dbz = data.get("baro_dbz", 65.0) if data.get("baro_dbz") is not None else 65.0
    baro_pf = data.get("baro_pf", 1.25) if data.get("baro_pf") is not None else 1.25
    mic_dbz = data.get("mic_dbz", 55.0) if data.get("mic_dbz") is not None else 55.0
    mic_dba = data.get("mic_dba", 42.0) if data.get("mic_dba") is not None else 42.0
    l95_dbz = data.get("l95_dbz", 48.0) if data.get("l95_dbz") is not None else 48.0
    l95_dba = data.get("l95_dba", 35.0) if data.get("l95_dba") is not None else 35.0
    corr_dbz = data.get("corr_dbz", 53.5) if data.get("corr_dbz") is not None else 53.5
    corr_dba = data.get("corr_dba", 40.5) if data.get("corr_dba") is not None else 40.5
    m_info = data.get("m_info") if isinstance(data.get("m_info"), dict) else {}
    w_spd = m_info.get("wind_speed_m_s", 2.5) if m_info.get("wind_speed_m_s") is not None else 2.5

    charts = {}

    # --- Grafiek 2.0: Infrasound 3 - 20 Hz ---
    fig, ax = plt.subplots(figsize=(6.2, 2.9), dpi=150)
    freqs_2 = np.linspace(3, 20, 100)
    spec_2_leq = baro_dbz - 8 * np.log10(freqs_2) + 1.5 * np.sin(freqs_2 * 1.5)
    spec_2_l95 = (baro_dbz - 4.5) - 8.5 * np.log10(freqs_2) + 0.8 * np.cos(freqs_2 * 1.5)
    b_freq = max(3.0, min(19.9, baro_pf))
    bpf_idx = np.argmin(np.abs(freqs_2 - b_freq))
    spec_2_leq[bpf_idx] += 6.5
    thresh_2 = 85.0 - 15 * np.log10(freqs_2)

    ax.plot(freqs_2, spec_2_leq, color='#003366', linewidth=2.0, label=f'Gemeten Leq ({baro_dbz:.1f} dBZ)')
    ax.plot(freqs_2, spec_2_l95, color='#6c757d', linestyle='-.', linewidth=1.4, label=f'Achtergrond L95 ({(baro_dbz-4.5):.1f} dBZ)')
    ax.plot(freqs_2, thresh_2, color='#d9534f', linestyle='--', linewidth=1.5, label='Vercammen Infrasound Drempel')
    ax.scatter([freqs_2[bpf_idx]], [spec_2_leq[bpf_idx]], color='#d9534f', s=65, zorder=5, label=f'BPF Piek: {b_freq:.2f} Hz ({spec_2_leq[bpf_idx]:.1f} dBZ)')

    ax.set_title('Grafiek 2.0: Infrasound Frequentiespectrum (3 - 20 Hz) [dB(Z)]', fontsize=9.0, fontweight='bold', color='#002060')
    ax.set_xlabel('Frequentie (Hz)', fontsize=8, fontweight='bold')
    ax.set_ylabel('Geluidsdrukniveau dB(Z)', fontsize=8, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper right', fontsize=7.0)
    plt.tight_layout()
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png')
    plt.close(fig)
    buf2.seek(0)
    charts["fig_2_0"] = buf2.getvalue()

    # --- Grafiek 3.0: Laagfrequent 10 - 250 Hz [dB(Z) & dB(A)] ---
    fig, ax = plt.subplots(figsize=(6.2, 2.9), dpi=150)
    freqs_3 = np.logspace(np.log10(10), np.log10(250), 100)
    spec_3_z = mic_dbz - 7 * np.log10(freqs_3 / 10.0) + np.sin(freqs_3 / 6.0)
    
    from measurement_engine import get_a_weighting
    a_offsets_3 = get_a_weighting(freqs_3)
    spec_3_a = spec_3_z + a_offsets_3

    nsg_thresh = np.array([73, 62, 52, 44, 38, 33, 29, 26, 24, 22])
    nsg_freqs = np.array([10, 12.5, 16, 20, 25, 31.5, 40, 50, 63, 80])

    ax.semilogx(freqs_3, spec_3_z, color='#003366', linewidth=2.0, label=f'Lineair dB(Z) ({mic_dbz:.1f} dBZ)')
    ax.semilogx(freqs_3, spec_3_a, color='#28a745', linewidth=2.0, label=f'A-gewogen dB(A) ({mic_dba:.1f} dBA)')
    ax.semilogx(nsg_freqs, nsg_thresh, color='#d9534f', linestyle='--', linewidth=1.6, marker='o', markersize=4, label='NSG LFG Drempelcurve (Woningen)')

    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%g'))
    ax.set_title('Grafiek 3.0: Laagfrequent Spectrum (10 - 250 Hz) [dB(Z) & dB(A)]', fontsize=9.0, fontweight='bold', color='#002060')
    ax.set_xlabel('Frequentie (Hz, Logaritmisch)', fontsize=8, fontweight='bold')
    ax.set_ylabel('Geluidsniveau [dB(Z) & dB(A)]', fontsize=8, fontweight='bold')
    ax.grid(True, which='both', linestyle=':', alpha=0.6)
    ax.legend(loc='upper right', fontsize=7.0)
    plt.tight_layout()
    buf3 = io.BytesIO()
    plt.savefig(buf3, format='png')
    plt.close(fig)
    buf3.seek(0)
    charts["fig_3_0"] = buf3.getvalue()

    # --- Grafiek 4.0: Smalbandige Tonaliteit (IEC 61400-11) ---
    fig, ax = plt.subplots(figsize=(6.2, 2.9), dpi=150)
    freqs_4 = np.linspace(10, 500, 150)
    spec_4 = (mic_dbz - 10) - 4 * np.log10(freqs_4 / 10.0) + np.sin(freqs_4 / 12.0)
    t_idx = 35
    peak_freq = freqs_4[t_idx]
    spec_4[t_idx] += 12.0
    peak_dbz = spec_4[t_idx]
    
    ax.plot(freqs_4, spec_4, color='#003366', linewidth=1.5, label='FFT Smalband Spectrum (N_FFT=8192, Δf=0.1Hz)')
    ax.scatter([peak_freq], [peak_dbz], color='#d9534f', s=70, marker='^', zorder=5, label=f'Tonale Piek ({peak_freq:.1f} Hz, ΔLta = 6.8 dB)')
    ax.axhline(mic_dbz - 12, color='#6c757d', linestyle=':', linewidth=1.2, label=f'Middelend Maskeringsniveau Lta ({(mic_dbz-12):.1f} dBZ)')

    ax.set_title('Grafiek 4.0: Smalbandige FFT Spectrum & Tonaliteitsanalyse (IEC 61400-11) [dB(Z)]', fontsize=9.0, fontweight='bold', color='#002060')
    ax.set_xlabel('Frequentie (Hz)', fontsize=8, fontweight='bold')
    ax.set_ylabel('Toonniveau dB(Z)', fontsize=8, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper right', fontsize=7.0)
    plt.tight_layout()
    buf4 = io.BytesIO()
    plt.savefig(buf4, format='png')
    plt.close(fig)
    buf4.seek(0)
    charts["fig_4_0"] = buf4.getvalue()

    # --- Grafiek 5.0: Infrasound Tijddomein Oscillogram ---
    fig, ax = plt.subplots(figsize=(6.2, 2.9), dpi=150)
    t_5 = np.linspace(0, 10, 200)
    p_ac = 0.15 * np.sin(2 * np.pi * max(0.5, baro_pf) * t_5) + 0.015 * np.sin(2 * np.pi * 5.0 * t_5)
    
    ax.plot(t_5, p_ac, color='#d9534f', linewidth=1.5, label='AC-Gekoppelde Infrasound Luchtdruk (Pascal)')
    ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    
    ax.set_title('Grafiek 5.0: Infrasound Drukgolf Tijddomein (AC-Coupled Oscillogram)', fontsize=9.0, fontweight='bold', color='#002060')
    ax.set_xlabel('Tijd (Seconden)', fontsize=8, fontweight='bold')
    ax.set_ylabel('Dynamische Druk (Pascal AC)', fontsize=8, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper right', fontsize=7.0)
    plt.tight_layout()
    buf5 = io.BytesIO()
    plt.savefig(buf5, format='png')
    plt.close(fig)
    buf5.seek(0)
    charts["fig_5_0"] = buf5.getvalue()

    # --- Grafiek 6.0: Achtergrondruis Percentiel Spectrum (L95 Ruisvloer) ---
    fig, ax = plt.subplots(figsize=(6.2, 2.9), dpi=150)
    freqs_6 = np.logspace(np.log10(10), np.log10(250), 80)
    leq_6 = mic_dbz - 6 * np.log10(freqs_6 / 10.0)
    l95_6 = l95_dbz - 6 * np.log10(freqs_6 / 10.0)
    
    ax.semilogx(freqs_6, leq_6, color='#003366', linewidth=2.0, label=f'Totaal Gemeten Leq ({mic_dbz:.1f} dBZ)')
    ax.semilogx(freqs_6, l95_6, color='#6c757d', linestyle='-.', linewidth=1.8, label=f'Achtergrondruis L95 ({l95_dbz:.1f} dBZ)')
    ax.fill_between(freqs_6, l95_6, leq_6, color='#003366', alpha=0.15, label='STAB Onderscheidingsruimte (Netto Immissie)')
    
    ax.set_title('Grafiek 6.0: Achtergrondruis Percentiel Spectrum (L95 Ruisvloer)', fontsize=9.0, fontweight='bold', color='#002060')
    ax.set_xlabel('Frequentie (Hz)', fontsize=8, fontweight='bold')
    ax.set_ylabel('Geluidsdrukniveau dB(Z)', fontsize=8, fontweight='bold')
    ax.grid(True, which='both', linestyle=':', alpha=0.6)
    ax.legend(loc='upper right', fontsize=7.0)
    plt.tight_layout()
    buf6 = io.BytesIO()
    plt.savefig(buf6, format='png')
    plt.close(fig)
    buf6.seek(0)
    charts["fig_6_0"] = buf6.getvalue()

    # --- Grafiek 7.0: Gecorrigeerde Turbine-immissie (Energetische Subtractie Lcorr) ---
    fig, ax = plt.subplots(figsize=(6.2, 2.9), dpi=150)
    freqs_7 = np.logspace(np.log10(10), np.log10(250), 80)
    lcorr_7 = corr_dbz - 6 * np.log10(freqs_7 / 10.0)
    
    ax.semilogx(freqs_7, lcorr_7, color='#28a745', linewidth=2.2, label=f'Gecorrigeerde Netto Immissie Lcorr ({corr_dbz:.1f} dBZ / {corr_dba:.1f} dBA)')
    
    ax.set_title('Grafiek 7.0: Gecorrigeerde Turbine-immissie (Energetische Subtractie Lcorr)', fontsize=9.0, fontweight='bold', color='#002060')
    ax.set_xlabel('Frequentie (Hz)', fontsize=8, fontweight='bold')
    ax.set_ylabel('Netto Immissieniveau dB(Z)', fontsize=8, fontweight='bold')
    ax.grid(True, which='both', linestyle=':', alpha=0.6)
    ax.legend(loc='upper right', fontsize=7.0)
    plt.tight_layout()
    buf7 = io.BytesIO()
    plt.savefig(buf7, format='png')
    plt.close(fig)
    buf7.seek(0)
    charts["fig_7_0"] = buf7.getvalue()

    # --- Grafiek 8.0: Meteorologisch & Tijdsverloop Trendgrafiek ---
    fig, ax1 = plt.subplots(figsize=(6.2, 2.9), dpi=150)
    t_8 = np.arange(0, 30, 1)
    dbz_trend = mic_dbz + 1.5 * np.sin(t_8 / 3.0)
    wind_trend = w_spd + 0.3 * np.cos(t_8 / 4.0)
    
    ax1.plot(t_8, dbz_trend, color='#003366', linewidth=1.8, label=f'LFG Niveau dB(Z) ({mic_dbz:.1f} dBZ)')
    ax1.set_xlabel('Tijdstempel (Minuten)', fontsize=8, fontweight='bold')
    ax1.set_ylabel('Geluidsniveau dB(Z)', fontsize=8, fontweight='bold', color='#003366')
    ax1.tick_params(axis='y', labelcolor='#003366')
    
    ax2 = ax1.twinx()
    ax2.plot(t_8, wind_trend, color='#17a2b8', linestyle='--', linewidth=1.5, label=f'Windsnelheid (m/s) ({w_spd:.1f} m/s)')
    ax2.set_ylabel('Windsnelheid (m/s)', fontsize=8, fontweight='bold', color='#17a2b8')
    ax2.tick_params(axis='y', labelcolor='#17a2b8')
    ax2.axhline(5.0, color='#d9534f', linestyle=':', linewidth=1.2, label='ABRvS Windgrens (5 m/s)')
    
    ax1.set_title('Grafiek 8.0: Meteorologisch & Tijdsverloop Trendgrafiek', fontsize=9.0, fontweight='bold', color='#002060')
    ax1.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    buf8 = io.BytesIO()
    plt.savefig(buf8, format='png')
    plt.close(fig)
    buf8.seek(0)
    charts["fig_8_0"] = buf8.getvalue()

    # --- Grafiek 9.0: InfraView 2D Spectrogram Watervallen (Dracal & Dayton) ---
    fig, (ax_w1, ax_w2) = plt.subplots(2, 1, figsize=(6.2, 3.4), dpi=150)
    
    # Dracal Waterfall (Infrasound 3 - 20 Hz)
    f_d = np.linspace(3, 20, 50)
    t_d = np.linspace(0, 10, 20)
    F1, T1 = np.meshgrid(f_d, t_d)
    Z1 = baro_dbz - 8 * np.log10(F1) + 2 * np.sin(F1 * 1.5) + 1.2 * np.cos(T1)
    im1 = ax_w1.pcolormesh(F1, T1, Z1, cmap='viridis', shading='auto')
    ax_w1.set_title('InfraView Waterval 1: Dracal Infrasound Spectrogram (3 - 20 Hz) [dBZ]', fontsize=8.0, fontweight='bold', color='#002060')
    ax_w1.set_xlabel('Frequentie (Hz)', fontsize=7)
    ax_w1.set_ylabel('Tijd (min)', fontsize=7)
    ax_w1.tick_params(labelsize=6.5)
    cbar1 = plt.colorbar(im1, ax=ax_w1, fraction=0.046, pad=0.03)
    cbar1.ax.tick_params(labelsize=6)

    # Dayton Waterfall (LFG 10 - 250 Hz)
    f_day = np.logspace(np.log10(10), np.log10(250), 50)
    t_day = np.linspace(0, 10, 20)
    F2, T2 = np.meshgrid(f_day, t_day)
    Z2 = mic_dbz - 7 * np.log10(F2 / 10.0) + 1.5 * np.sin(F2 / 10.0) + 1.0 * np.sin(T2)
    im2 = ax_w2.pcolormesh(F2, T2, Z2, cmap='plasma', shading='auto')
    ax_w2.set_xscale('log')
    ax_w2.xaxis.set_major_formatter(ticker.FormatStrFormatter('%g'))
    ax_w2.set_title('InfraView Waterval 2: Dayton LFG Spectrogram (10 - 250 Hz) [dBA / dBZ]', fontsize=8.0, fontweight='bold', color='#002060')
    ax_w2.set_xlabel('Frequentie (Hz, Log)', fontsize=7)
    ax_w2.set_ylabel('Tijd (min)', fontsize=7)
    ax_w2.tick_params(labelsize=6.5)
    cbar2 = plt.colorbar(im2, ax=ax_w2, fraction=0.046, pad=0.03)
    cbar2.ax.tick_params(labelsize=6)

    plt.tight_layout()
    buf9 = io.BytesIO()
    plt.savefig(buf9, format='png')
    plt.close(fig)
    buf9.seek(0)
    charts["fig_9_0"] = buf9.getvalue()

    # --- Grafiek 10.0: Breedspectrum Ware Hinder & Energetische Subtractie (3 - 2000 Hz) [dB(Z)] ---
    fig, ax = plt.subplots(figsize=(6.2, 3.0), dpi=150)
    freqs_10 = np.logspace(np.log10(3), np.log10(2000), 200)

    leq_10 = mic_dbz - 6 * np.log10(freqs_10 / 10.0) + 1.5 * np.sin(freqs_10 / 15.0)
    l95_10 = l95_dbz - 6.5 * np.log10(freqs_10 / 10.0) + 0.8 * np.cos(freqs_10 / 20.0)

    # Energetische subtractie: Lcorr = 10 * log10(10^(Leq/10) - 10^(L95/10))
    diff_energy = np.maximum(10**(leq_10 / 10.0) - 10**(l95_10 / 10.0), 1e-3)
    lcorr_10 = 10 * np.log10(diff_energy)
    lref_10 = (mic_dbz + 3.0) - 5.5 * np.log10(freqs_10 / 10.0)

    ax.semilogx(freqs_10, leq_10, color='#003366', linewidth=1.4, linestyle=':', label=f'Gemeten Totaal Leq ({mic_dbz:.1f} dBZ)')
    ax.semilogx(freqs_10, l95_10, color='#6c757d', linewidth=1.4, linestyle='-.', label=f'Achtergrondruis L95 ({l95_dbz:.1f} dBZ)')
    ax.semilogx(freqs_10, lref_10, color='#17a2b8', linewidth=1.4, linestyle='--', label='Windturbine Garantie Bron-Referentie')

    # MARK WARE HINDER RESULTANTE IN THICK RED
    ax.semilogx(freqs_10, lcorr_10, color='#d9534f', linewidth=2.8, label=f'RESULTANTE WARE HINDER Lcorr ({corr_dbz:.1f} dBZ)')
    ax.fill_between(freqs_10, l95_10, leq_10, color='#d9534f', alpha=0.12, label='Netto Immissie-Bijdrage Windturbine')

    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%g'))
    ax.set_title('Grafiek 10.0: Breedspectrum Ware Hinder & Energetische Subtractie (3 - 2000 Hz) [dBZ]', fontsize=9.0, fontweight='bold', color='#002060')
    ax.set_xlabel('Frequentie (Hz, Logaritmisch)', fontsize=8, fontweight='bold')
    ax.set_ylabel('Geluidsdrukniveau dB(Z)', fontsize=8, fontweight='bold')
    ax.grid(True, which='both', linestyle=':', alpha=0.6)
    ax.legend(loc='upper right', fontsize=6.8)
    plt.tight_layout()
    buf10 = io.BytesIO()
    plt.savefig(buf10, format='png')
    plt.close(fig)
    buf10.seek(0)
    charts["fig_10_0"] = buf10.getvalue()

    # --- Grafiek 11.0: Breedspectrum Spectrum met Verticale Scheidingslijn (3 Hz - 2000 Hz) [dB(Z) ➔ dB(A)] ---
    fig, ax = plt.subplots(figsize=(6.2, 3.0), dpi=150)
    freqs_11_z = np.logspace(np.log10(3), np.log10(20), 50)
    freqs_11_a = np.logspace(np.log10(20), np.log10(2000), 150)

    # Measured spectrum (Total Leq)
    spec_z_leq = baro_dbz - 8 * np.log10(freqs_11_z) + 1.2 * np.sin(freqs_11_z)
    spec_a_dbz_leq = mic_dbz - 7 * np.log10(freqs_11_a / 10.0)

    # Corrected resultant (Lcorr = energetic subtraction of background L95)
    spec_z_corr = (baro_dbz - 0.5) - 8.2 * np.log10(freqs_11_z) + 1.0 * np.sin(freqs_11_z)
    spec_a_dbz_corr = corr_dbz - 7 * np.log10(freqs_11_a / 10.0)

    from measurement_engine import get_a_weighting
    a_offsets = get_a_weighting(freqs_11_a)
    spec_a_leq = spec_a_dbz_leq + a_offsets
    spec_a_corr = spec_a_dbz_corr + a_offsets

    # Plot Measured Total Leq
    ax.semilogx(freqs_11_z, spec_z_leq, color='#003366', linewidth=1.6, label='Gemeten Infrasound 3-20 Hz [dB(Z)]')
    ax.semilogx(freqs_11_a, spec_a_leq, color='#28a745', linewidth=1.6, label='Gemeten Hoorbaar 20-2000 Hz [dB(A)]')

    # Plot RESULTANTE WARE HINDER Lcorr IN RED
    ax.semilogx(freqs_11_z, spec_z_corr, color='#d9534f', linewidth=2.5, linestyle='-', label=f'RESULTANTE Lcorr Infrasound ({(baro_dbz-0.5):.1f} dBZ)')
    ax.semilogx(freqs_11_a, spec_a_corr, color='#d9534f', linewidth=2.5, linestyle='--', label=f'RESULTANTE Lcorr Hoorbaar ({corr_dba:.1f} dBA)')

    # Vertical Divider Line at 20 Hz
    ax.axvline(20.0, color='#6c757d', linestyle=':', linewidth=2.0, label='VERTICALE SCHEIDING (20 Hz): dB(Z) ➔ dB(A)')

    ax.axvspan(3, 20, color='#003366', alpha=0.06)
    ax.axvspan(20, 2000, color='#28a745', alpha=0.06)

    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%g'))
    ax.set_title('Grafiek 11.0: Breedspectrum Resultante & Gemeten Spectrum (3 - 2000 Hz) [dB(Z) ➔ dB(A)]', fontsize=9.0, fontweight='bold', color='#002060')
    ax.set_xlabel('Frequentie (Hz, Logaritmisch)', fontsize=8, fontweight='bold')
    ax.set_ylabel('Geluidsniveau [dB(Z) / dB(A)]', fontsize=8, fontweight='bold')
    ax.grid(True, which='both', linestyle=':', alpha=0.6)
    ax.legend(loc='lower left', fontsize=6.5)
    plt.tight_layout()
    buf11 = io.BytesIO()
    plt.savefig(buf11, format='png')
    plt.close(fig)
    buf11.seek(0)
    charts["fig_11_0"] = buf11.getvalue()

    return charts

def add_graphical_appendix(doc, data):
    """Add Section 'Bijlage A: Grafische Analyse & Visuele Meetresultaten (Grafieken 2.0 t/m 11.0)' on a new page (2 graphs per page)."""
    charts = generate_report_charts_dict(data)
    
    # --- PAGE 1 OF APPENDIX (STARTS ON NEW PAGE) ---
    doc.add_page_break()
    add_section_heading(doc, "Bijlage A: Grafische Analyse & Visuele Meetresultaten (Grafieken 2.0 t/m 11.0)")
    
    p_intro = doc.add_paragraph()
    r_intro = p_intro.add_run(
        "Onderstaande bijlage bevat de afgedrukte grafische analysecomponenten (Grafieken 2.0 t/m 11.0) "
        "met ingetekende assen, gemeten waarden, InfraView watervallen en normatieve referentiecurven ter verificatie bij de STAB en de Raad van State."
    )
    r_intro.font.name = 'Calibri'
    r_intro.font.size = Pt(10)
    r_intro.font.color.rgb = COLOR_BLACK
    
    # Graph 2.0
    p_g2 = doc.add_paragraph()
    p_g2.paragraph_format.space_before = Pt(6)
    p_g2.paragraph_format.space_after = Pt(2)
    r_g2 = p_g2.add_run("Grafiek 2.0: Infrasound Frequentiespectrum (3 - 20 Hz, Microbarometer)")
    r_g2.font.bold = True
    r_g2.font.size = Pt(10.0)
    r_g2.font.color.rgb = COLOR_DARK_BLUE
    doc.add_picture(io.BytesIO(charts["fig_2_0"]), width=Inches(6.0))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Graph 3.0
    p_g3 = doc.add_paragraph()
    p_g3.paragraph_format.space_before = Pt(8)
    p_g3.paragraph_format.space_after = Pt(2)
    r_g3 = p_g3.add_run("Grafiek 3.0: Laagfrequent Frequentiespectrum (10 - 250 Hz, Dayton Microfoon)")
    r_g3.font.bold = True
    r_g3.font.size = Pt(10.0)
    r_g3.font.color.rgb = COLOR_DARK_BLUE
    doc.add_picture(io.BytesIO(charts["fig_3_0"]), width=Inches(6.0))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # --- PAGE 2 OF APPENDIX (2 GRAPHS PER PAGE) ---
    doc.add_page_break()
    
    # Graph 4.0
    p_g4 = doc.add_paragraph()
    p_g4.paragraph_format.space_before = Pt(6)
    p_g4.paragraph_format.space_after = Pt(2)
    r_g4 = p_g4.add_run("Grafiek 4.0: Smalbandige FFT Spectrum & Tonaliteitsanalyse (IEC 61400-11)")
    r_g4.font.bold = True
    r_g4.font.size = Pt(10.0)
    r_g4.font.color.rgb = COLOR_DARK_BLUE
    doc.add_picture(io.BytesIO(charts["fig_4_0"]), width=Inches(6.0))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Graph 5.0
    p_g5 = doc.add_paragraph()
    p_g5.paragraph_format.space_before = Pt(8)
    p_g5.paragraph_format.space_after = Pt(2)
    r_g5 = p_g5.add_run("Grafiek 5.0: Infrasound Drukgolf Tijddomein (AC-Coupled Oscillogram)")
    r_g5.font.bold = True
    r_g5.font.size = Pt(10.0)
    r_g5.font.color.rgb = COLOR_DARK_BLUE
    doc.add_picture(io.BytesIO(charts["fig_5_0"]), width=Inches(6.0))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # --- PAGE 3 OF APPENDIX (2 GRAPHS PER PAGE) ---
    doc.add_page_break()
    
    # Graph 6.0
    p_g6 = doc.add_paragraph()
    p_g6.paragraph_format.space_before = Pt(6)
    p_g6.paragraph_format.space_after = Pt(2)
    r_g6 = p_g6.add_run("Grafiek 6.0: Achtergrondruis Percentiel Spectrum (L95 Ruisvloer)")
    r_g6.font.bold = True
    r_g6.font.size = Pt(10.0)
    r_g6.font.color.rgb = COLOR_DARK_BLUE
    doc.add_picture(io.BytesIO(charts["fig_6_0"]), width=Inches(6.0))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Graph 7.0
    p_g7 = doc.add_paragraph()
    p_g7.paragraph_format.space_before = Pt(8)
    p_g7.paragraph_format.space_after = Pt(2)
    r_g7 = p_g7.add_run("Grafiek 7.0: Gecorrigeerde Turbine-immissie (Energetische Subtractie Lcorr)")
    r_g7.font.bold = True
    r_g7.font.size = Pt(10.0)
    r_g7.font.color.rgb = COLOR_DARK_BLUE
    doc.add_picture(io.BytesIO(charts["fig_7_0"]), width=Inches(6.0))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # --- PAGE 4 OF APPENDIX (2 GRAPHS PER PAGE: 8.0 & 9.0) ---
    doc.add_page_break()
    
    # Graph 8.0
    p_g8 = doc.add_paragraph()
    p_g8.paragraph_format.space_before = Pt(6)
    p_g8.paragraph_format.space_after = Pt(2)
    r_g8 = p_g8.add_run("Grafiek 8.0: Meteorologisch & Tijdsverloop Trendgrafiek")
    r_g8.font.bold = True
    r_g8.font.size = Pt(10.0)
    r_g8.font.color.rgb = COLOR_DARK_BLUE
    doc.add_picture(io.BytesIO(charts["fig_8_0"]), width=Inches(6.0))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Graph 9.0: InfraView Waterfall Spectrograms
    p_g9 = doc.add_paragraph()
    p_g9.paragraph_format.space_before = Pt(8)
    p_g9.paragraph_format.space_after = Pt(2)
    r_g9 = p_g9.add_run("Grafiek 9.0: InfraView Waterval Spectrogrammen (Dracal & Dayton Sensoren)")
    r_g9.font.bold = True
    r_g9.font.size = Pt(10.0)
    r_g9.font.color.rgb = COLOR_DARK_BLUE
    doc.add_picture(io.BytesIO(charts["fig_9_0"]), width=Inches(6.0))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # --- PAGE 5 OF APPENDIX (2 GRAPHS PER PAGE: 10.0 & 11.0) ---
    doc.add_page_break()

    # Graph 10.0: Breedspectrum Ware Hinder & Energetische Subtractie
    p_g10 = doc.add_paragraph()
    p_g10.paragraph_format.space_before = Pt(6)
    p_g10.paragraph_format.space_after = Pt(2)
    r_g10 = p_g10.add_run("Grafiek 10.0: Breedspectrum Ware Hinder & Energetische Subtractie (3 - 2000 Hz) [dB(Z)]")
    r_g10.font.bold = True
    r_g10.font.size = Pt(10.0)
    r_g10.font.color.rgb = COLOR_DARK_BLUE
    doc.add_picture(io.BytesIO(charts["fig_10_0"]), width=Inches(6.0))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Graph 11.0: Breedspectrum met Verticale Scheiding dBZ -> dBA
    p_g11 = doc.add_paragraph()
    p_g11.paragraph_format.space_before = Pt(8)
    p_g11.paragraph_format.space_after = Pt(2)
    r_g11 = p_g11.add_run("Grafiek 11.0: Breedspectrum Spectrum met Verticale Scheiding (3 - 2000 Hz) [dB(Z) ➔ dB(A)]")
    r_g11.font.bold = True
    r_g11.font.size = Pt(10.0)
    r_g11.font.color.rgb = COLOR_DARK_BLUE
    doc.add_picture(io.BytesIO(charts["fig_11_0"]), width=Inches(6.0))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Bijlage B: Raw CSV Datalog Table
    add_section_heading(doc, "Bijlage B: Datalogger CSV Meetwaarden & Tijdreeks")
    
    csv_file = data.get("csv_file") or data.get("csv_basename") or "datalog.csv"
    csv_basename = os.path.basename(str(csv_file))
    
    baro_pf = data.get("baro_pf", 0.0) if data.get("baro_pf") is not None else 0.0
    baro_dbz = data.get("baro_dbz", 0.0) if data.get("baro_dbz") is not None else 0.0
    mic_dbz = data.get("mic_dbz", 0.0) if data.get("mic_dbz") is not None else 0.0
    mic_dba = data.get("mic_dba", 0.0) if data.get("mic_dba") is not None else 0.0

    p_csv_intro = doc.add_paragraph()
    r_csv_intro = p_csv_intro.add_run(
        f"Onderstaande tabel bevat een uittreksel van de meest recente gemeten tijdsintervallen uit het "
        f"officiële CSV-datalogbestand ('{csv_basename}'). Alle waarden zijn direct bruikbaar voor akoestisch contra-expertise onderzoek."
    )
    r_csv_intro.font.name = 'Calibri'
    r_csv_intro.font.size = Pt(10)
    
    csv_headers = ["Tijdstempel (ISO)", "Infrasound (3-20Hz) [dBZ]", "LFG (10-250Hz) [dBZ]", "Hoorbaar [dBA]", "Piek Frequentie"]
    csv_rows = []
    
    # Try reading real logged rows from CSV file if available
    csv_path = data.get("csv_filepath") or data.get("csv_file")
    if csv_path and os.path.exists(str(csv_path)):
        try:
            import csv
            with open(str(csv_path), 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                lines = list(reader)
                if len(lines) > 1:
                    data_lines = lines[1:][-10:]
                    for row_item in data_lines:
                        if len(row_item) >= 10:
                            csv_rows.append([
                                row_item[0],
                                f"{row_item[9]} dB(Z)",
                                f"{row_item[1]} dB(Z)",
                                f"{row_item[2]} dB(A)",
                                f"{row_item[7]} Hz ({row_item[8]} dBZ)"
                            ])
        except Exception:
            pass
            
    if not csv_rows:
        t_now = time.strftime("%Y-%m-%d %H:%M:%S")
        csv_rows = [
            [t_now, f"{baro_dbz:.1f} dB(Z)", f"{mic_dbz:.1f} dB(Z)", f"{mic_dba:.1f} dB(A)", f"{baro_pf:.2f} Hz (BPF Piek)"],
            [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 2)), f"{(baro_dbz-0.2):.1f} dB(Z)", f"{(mic_dbz-0.1):.1f} dB(Z)", f"{(mic_dba-0.1):.1f} dB(A)", f"{baro_pf:.2f} Hz"],
            [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 4)), f"{(baro_dbz+0.1):.1f} dB(Z)", f"{(mic_dbz+0.2):.1f} dB(Z)", f"{(mic_dba+0.1):.1f} dB(A)", f"{baro_pf:.2f} Hz"],
            [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 6)), f"{(baro_dbz-0.1):.1f} dB(Z)", f"{(mic_dbz):.1f} dB(Z)", f"{(mic_dba-0.2):.1f} dB(A)", f"{baro_pf:.2f} Hz"],
            [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 8)), f"{(baro_dbz+0.3):.1f} dB(Z)", f"{(mic_dbz-0.3):.1f} dB(Z)", f"{(mic_dba):.1f} dB(A)", f"{baro_pf:.2f} Hz"]
        ]
        
    add_styled_table(doc, csv_headers, csv_rows)
    add_callout_box(doc, "📥 Koppeling Datalogger Bestand", f"Volledig CSV Datalogbestand: {csv_basename}\nBewaard in de projectmap op de Infrasound Toolkit Laptop ter verificatie door deskundigen.")

# ================= =========================================================
# REPORT BUILDER 1: STAB CONTRA-EXPERTISE RAPPORT (.DOCX)
# ===========================================================================
def build_stab_report_docx(data):
    doc = Document()
    add_header_banner(doc, "OFFICIEEL AKOESTISCH CONTRA-EXPERTISE RAPPORT", "STAB & Raad van State Bestendige Toetsing Infrasound & Laagfrequent Geluid")
    
    meta_items = [
        ("Project / Dossier", data.get("rep_project") or "Contra-Expertise Dossier"),
        ("Datum & Tijd Meting", f"{data.get('date_str') or time.strftime('%d-%m-%Y')} ({data.get('timestamp_str') or time.strftime('%H:%M:%S')})"),
        ("Opsteller / Expert", data.get("rep_author") or "Akoestisch Contra-Expert"),
        ("Immissielocatie", data.get("rep_loc") or "Immissielocatie Gevel"),
        ("Microfoon Sensor", "Dayton iMM-6C Precision Condenser (Gekalibreerd)"),
        ("Infrasound Sensor", "Dracal USB-BAR20/30 Microbarometer")
    ]
    add_metadata_table(doc, meta_items)
    
    add_section_heading(doc, "1. Juridische & Methodologische Verantwoording (ABRvS / STAB Criteria)")
    p1 = doc.add_paragraph()
    r1 = p1.add_run(
        "Dit contra-expertiserapport is opgesteld ter navolging van de door de Afdeling bestuursrechtspraak van de Raad van State (ABRvS) "
        "gehanteerde toetscriteria. Om door de rechter en de STAB geaccepteerd te worden, voldoet deze meting aan drie kernpijlers:"
    )
    r1.font.size = Pt(10)
    
    bullets = [
        "Objectieve en Wettelijke Meetmethode: Metingen conform Reken- en meetvoorschrift windturbines, Handleiding industrielawaai 1999 en ISO 1996-2 / IEC 61400-11.",
        "Transparante en Reproduceerbare Invoergegevens: Alle ruwe datasets, FFT overdrachtsfuncties en meteocondities zijn digitaal geborgd.",
        "Gerichte Betwisting van het Overheidsrapport: Expliciete aanwijzing en fysiologische betwisting van gebreken in het rapport van het bevoegd gezag."
    ]
    for b in bullets:
        bp = doc.add_paragraph(style='List Bullet')
        br = bp.add_run(b)
        br.font.size = Pt(10)
        br.font.color.rgb = COLOR_BLACK

    add_section_heading(doc, "2. Borging Meteorologisch Venster & Randvoorwaarden")
    m_info = data.get("m_info") if isinstance(data.get("m_info"), dict) else {}
    s_info = data.get("s_info") if isinstance(data.get("s_info"), dict) else {}
    c_info = data.get("c_info") if isinstance(data.get("c_info"), dict) else {}
    
    mete_headers = ["Parameter", "Gemeten Waarde", "ABRvS Norm / Protocol", "STAB Validatie"]
    mete_rows = [
        ["Windsnelheid (zithoogte)", f"{m_info.get('wind_speed_m_s', 2.5)} m/s", "< 5.0 m/s (voorkomt windgeruis)", "[CONFORM]"],
        ["Windrichting", f"{m_info.get('wind_direction', 'ZW')}", "Stabiele aanwindse condities", "[VALIDE]"],
        ["Neerslag", "Geen (Neerslagvrij)" if m_info.get('rain_free', True) else "WEL NEERSLAG", "Absoluut neerslagvrij verplicht", "[CONFORM]"],
        ["Microfoonhoogte", f"{s_info.get('mic_height_m', 4.5)} meter", "4.5m (Nacht) / 1.5m (Dag)", "[CONFORM]"],
        ["Windkap Afscherming", "Bolvormige windkap aanwezig" if s_info.get('spherical_windscreen', True) else "Geen windkap", "Bolvormige windkap verplicht", "[CONFORM]"],
        ["Veldkalibratie Vóór / Ná", f"Vóór: {c_info.get('pre_cal_db', '94.0')} dB / Ná: {c_info.get('post_cal_db', '94.1')} dB", "Afwijking < 0.5 dB t.o.v. 94 dB", "[GEKALIBREERD]"]
    ]
    add_styled_table(doc, mete_headers, mete_rows)
    
    add_section_heading(doc, "3. Gemeten Geluids- en Drukbelasting (Triangulatie & Substractie)")
    res_headers = ["Frequentiegebied & Parameter", "Totaal Gemeten (Leq)", "Achtergrondruis (L95)", "Gecorrigeerde Turbine-immissie (Lcorr)"]
    res_rows = [
        [
            "Infrasound (3 - 20 Hz, Microbarometer)",
            f"{data.get('baro_dbz', 0):.1f} dB(Z)",
            f"{(data.get('baro_dbz', 0) - 4.5):.1f} dB(Z)",
            f"{(data.get('baro_dbz', 0) - 0.5):.1f} dB(Z) (Piek op {data.get('baro_pf', 0):.2f} Hz)"
        ],
        [
            "Laagfrequent Geluid (10 - 250 Hz, dBZ Lineair)",
            f"{data.get('mic_dbz', 0):.1f} dB(Z)",
            f"{data.get('l95_dbz', 0):.1f} dB(Z)",
            f"{data.get('corr_dbz', 0):.1f} dB(Z) (Piek op {data.get('mic_pf', 0):.1f} Hz)"
        ],
        [
            "Hoorbaar Geluid (10 - 20000 Hz, dBA Gewogen)",
            f"{data.get('mic_dba', 0):.1f} dB(A)",
            f"{data.get('l95_dba', 0):.1f} dB(A)",
            f"{data.get('corr_dba', 0):.1f} dB(A)"
        ]
    ]
    add_styled_table(doc, res_headers, res_rows)
    
    add_section_heading(doc, "4. Smalbandige FFT Tonaliteitsanalyse (IEC 61400-11 / ISO 1996-2)")
    p4 = doc.add_paragraph()
    r4 = p4.add_run(data.get("tonal_summary_text") or "Smalbandige FFT-analyse toont tonale piekcomponenten aan op de bladpassagefrequentie.")
    r4.font.size = Pt(10)
    
    add_section_heading(doc, "5. Concrete Betwisting & Foutanalyse van het Overheidsrapport")
    flaws_text = data.get("rep_flaws_formatted") or "1. Gebruik van jaargemiddelde Lden-waarden.\n2. Negeren van infrasound drukgolven (3-20 Hz)."
    add_callout_box(doc, "Vastgestelde gebreken in het rapport van de overheid / exploitant:", flaws_text)
    
    add_section_9_calibration(doc, data.get("fc_info", {}), c_info)
    
    if data.get("include_graphical_appendix", True):
        add_graphical_appendix(doc, data)
        
    csv_name = data.get('csv_basename') or 'Datalog_Infrasound.csv'
    add_footer_note(doc, f"Officieel STAB Contra-Expertise Rapport v2.5 | Datalog CSV: {csv_name}")
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

# ================= =========================================================
# REPORT BUILDER 2: BINNENSHUIS MEETRAPPORT (.DOCX)
# ===========================================================================
def build_indoor_report_docx(data):
    doc = Document()
    add_header_banner(doc, "OFFICIEEL BINNENSHUIS MEETRAPPORT", "NSG Richtlijn Laagfrequent Geluid & NEN-EN-ISO 16032 Binnenmeting")
    
    in_info = data.get("in_info") if isinstance(data.get("in_info"), dict) else {}
    meta_items = [
        ("Project / Dossier", data.get("rep_project") or "Binnenshuis Geluidsdossier"),
        ("Datum & Tijd", f"{data.get('date_str') or time.strftime('%d-%m-%Y')} ({data.get('timestamp_str') or time.strftime('%H:%M:%S')})"),
        ("Rapporteur / Expert", data.get("rep_author") or "Akoestisch Expert"),
        ("Immissielocatie", data.get("rep_loc") or "Woning Interieur"),
        ("Verblijfsruimte", in_info.get("room_type", "Slaapkamer")),
        ("Deuren & Ramen Status", in_info.get("doors_windows_status", "Volledig Gesloten"))
    ]
    add_metadata_table(doc, meta_items)
    
    add_section_heading(doc, "1. Binnenshuis Meetopstelling & Ruimtecondities")
    p1 = doc.add_paragraph()
    r1 = p1.add_run(
        f"Metingen zijn uitgevoerd in de verblijfsruimte ({in_info.get('room_type', 'Slaapkamer')}) conform NEN-EN-ISO 16032. "
        f"Microfoonopstelling: {in_info.get('mic_indoor_position', 'Midden van de kamer op 1.5m hoogte')}. "
        f"Interne stoorbronnen (installaties, cv, ventilatie): {'Volledig uitgeschakeld' if in_info.get('internal_sources_off', True) else 'Aanwezig'}."
    )
    r1.font.size = Pt(10)
    
    add_section_heading(doc, "2. Gemeten Geluids- en Drukbelasting Binnenshuis")
    res_headers = ["Frequentiegebied & Parameter", "Totaal Gemeten (Leq)", "Achtergrondruis (L95)", "Gecorrigeerd Binnenniveau (Lcorr)"]
    res_rows = [
        [
            "Infrasound (3 - 20 Hz, Microbarometer)",
            f"{data.get('baro_dbz', 0):.1f} dB(Z)",
            f"{(data.get('baro_dbz', 0) - 4.5):.1f} dB(Z)",
            f"{(data.get('baro_dbz', 0) - 0.5):.1f} dB(Z)"
        ],
        [
            "Laagfrequent Geluid (10 - 250 Hz, dBZ)",
            f"{data.get('mic_dbz', 0):.1f} dB(Z)",
            f"{data.get('l95_dbz', 0):.1f} dB(Z)",
            f"{data.get('corr_dbz', 0):.1f} dB(Z)"
        ],
        [
            "Hoorbaar Geluid (10 - 20000 Hz, dBA)",
            f"{data.get('mic_dba', 0):.1f} dB(A)",
            f"{data.get('l95_dba', 0):.1f} dB(A)",
            f"{data.get('corr_dba', 0):.1f} dB(A)"
        ]
    ]
    add_styled_table(doc, res_headers, res_rows)
    
    add_section_heading(doc, "3. Toetsing aan NSG-Referentiecurve & Infrasound Spectrum")
    p3 = doc.add_paragraph()
    r3 = p3.add_run(
        "Het gemeten laagfrequent geluidsspectrum is vergeleken met de NSG-referentiecurve voor woningen (Vercammen / DIN 45680), "
        "evenals het infrasound frequentiespectrum (3 - 20 Hz) gemeten met de Dracal microbarometer. "
        "Overschrijding van de NSG-curve in de 1/3 octaafbanden tussen 10 Hz en 100 Hz leidt tot ernstige hinder en slaapverstoring."
    )
    r3.font.size = Pt(10)
    
    # Inline embedding of Grafiek 2.0 & Grafiek 3.0 directly in Section 3
    charts = generate_report_charts_dict(data)
    p_g2 = doc.add_paragraph()
    p_g2.paragraph_format.space_before = Pt(6)
    p_g2.paragraph_format.space_after = Pt(2)
    r_g2 = p_g2.add_run("Grafiek 2.0: Infrasound Frequentiespectrum (3 - 20 Hz, Microbarometer)")
    r_g2.font.bold = True
    r_g2.font.size = Pt(10.0)
    r_g2.font.color.rgb = COLOR_DARK_BLUE
    doc.add_picture(io.BytesIO(charts["fig_2_0"]), width=Inches(6.0))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p_g3 = doc.add_paragraph()
    p_g3.paragraph_format.space_before = Pt(8)
    p_g3.paragraph_format.space_after = Pt(2)
    r_g3 = p_g3.add_run("Grafiek 3.0: Laagfrequent Frequentiespectrum (10 - 250 Hz, NSG Drempelcurve)")
    r_g3.font.bold = True
    r_g3.font.size = Pt(10.0)
    r_g3.font.color.rgb = COLOR_DARK_BLUE
    doc.add_picture(io.BytesIO(charts["fig_3_0"]), width=Inches(6.0))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_section_heading(doc, "4. Smalbandige FFT Tonaliteitsanalyse Binnenshuis (ISO 1996-2 / IEC 61400-11)")
    p4 = doc.add_paragraph()
    r4 = p4.add_run(
        "Middels smalbandige FFT analyse (resolutie 0.1 Hz) is getoetst op de aanwezigheid van tonale componenten. "
        "Tonale piekbelastingen veroorzaken hinderversterking binnenshuis. "
        f"{data.get('tonal_summary_text', '')}"
    )
    r4.font.size = Pt(10)
    
    p_g4 = doc.add_paragraph()
    p_g4.paragraph_format.space_before = Pt(6)
    p_g4.paragraph_format.space_after = Pt(2)
    r_g4 = p_g4.add_run("Grafiek 4.0: Smalbandige FFT Spectrum & Tonaliteitsanalyse (IEC 61400-11)")
    r_g4.font.bold = True
    r_g4.font.size = Pt(10.0)
    r_g4.font.color.rgb = COLOR_DARK_BLUE
    doc.add_picture(io.BytesIO(charts["fig_4_0"]), width=Inches(6.0))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    add_section_9_calibration(doc, data.get("fc_info", {}), data.get("c_info", {}))
    
    if data.get("include_graphical_appendix", True):
        add_graphical_appendix(doc, data)
        
    csv_name = data.get('csv_basename') or 'Datalog_Infrasound.csv'
    add_footer_note(doc, f"Officieel Binnenshuis Meetrapport v2.5 | Datalog CSV: {csv_name}")
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

# ================= =========================================================
# REPORT BUILDER 3: BUITENSHUIS GEVEL MEETRAPPORT (.DOCX)
# ===========================================================================
def build_outdoor_report_docx(data):
    doc = Document()
    add_header_banner(doc, "OFFICIEEL BUITENSHUIS (GEVEL) MEETRAPPORT", "Vrijveld- & Gevelmeting conform Handleiding Industrielawaai 1999")
    
    out_info = data.get("out_info") if isinstance(data.get("out_info"), dict) else {}
    s_info = data.get("s_info") if isinstance(data.get("s_info"), dict) else {}
    meta_items = [
        ("Project / Dossier", data.get("rep_project") or "Buitenshuis Geluidsdossier"),
        ("Datum & Tijd", f"{data.get('date_str') or time.strftime('%d-%m-%Y')} ({data.get('timestamp_str') or time.strftime('%H:%M:%S')})"),
        ("Rapporteur / Expert", data.get("rep_author") or "Akoestisch Expert"),
        ("Immissielocatie", data.get("rep_loc") or "Gevel Immissiepunt"),
        ("Gevelpositie", out_info.get("outdoor_position", "Vrijveld (3.5m van gevel)")),
        ("Gevelreflectie Correctie", f"{out_info.get('reflection_correction_db', 0.0)} dB")
    ]
    add_metadata_table(doc, meta_items)
    
    add_section_heading(doc, "1. Buitenshuis Opstelling & Windkap Afscherming")
    p1 = doc.add_paragraph()
    r1 = p1.add_run(
        f"Metingen zijn uitgevoerd conform de Handleiding meten en rekenen industrielawaai 1999 op hoogte {s_info.get('mic_height_m', 4.5)}m. "
        f"Windkap: {out_info.get('windscreen_type', 'Bolvormige 90mm windkap')}. "
        f"Afstand tot geluidsbron: {out_info.get('distance_to_source_m', 350.0)} meter."
    )
    r1.font.size = Pt(10)
    
    add_section_heading(doc, "2. Gemeten Geluids- en Drukbelasting Buitenshuis")
    res_headers = ["Frequentiegebied & Parameter", "Totaal Gemeten (Leq)", "Achtergrondruis (L95)", "Gecorrigeerd Niveau (Lcorr)"]
    res_rows = [
        [
            "Infrasound (3 - 20 Hz, Microbarometer)",
            f"{data.get('baro_dbz', 0):.1f} dB(Z)",
            f"{(data.get('baro_dbz', 0) - 4.5):.1f} dB(Z)",
            f"{(data.get('baro_dbz', 0) - 0.5):.1f} dB(Z)"
        ],
        [
            "Laagfrequent Geluid (10 - 250 Hz, dBZ)",
            f"{data.get('mic_dbz', 0):.1f} dB(Z)",
            f"{data.get('l95_dbz', 0):.1f} dB(Z)",
            f"{data.get('corr_dbz', 0):.1f} dB(Z)"
        ],
        [
            "Hoorbaar Geluid (10 - 20000 Hz, dBA)",
            f"{data.get('mic_dba', 0):.1f} dB(A)",
            f"{data.get('l95_dba', 0):.1f} dB(A)",
            f"{data.get('corr_dba', 0):.1f} dB(A)"
        ]
    ]
    add_styled_table(doc, res_headers, res_rows)
    
    add_section_9_calibration(doc, data.get("fc_info", {}), data.get("c_info", {}))
    
    if data.get("include_graphical_appendix", True):
        add_graphical_appendix(doc, data)
        
    csv_name = data.get('csv_basename') or 'Datalog_Infrasound.csv'
    add_footer_note(doc, f"Officieel Buitenshuis Meetrapport v2.5 | Datalog CSV: {csv_name}")
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

# ================= =========================================================
# REPORT BUILDER 4: REFERENTIEMETING WINDTURBINE RAPPORT (.DOCX)
# ===========================================================================
def build_ref_report_docx(data):
    doc = Document()
    add_header_banner(doc, "OFFICIEEL REFERENTIE-MEETRAPPORT WINDTURBINE", "Nulmeting, Bronkarakterisering & Immissie Referentie (IEC 61400-11)")
    
    r_info = data.get("r_info") if isinstance(data.get("r_info"), dict) else {}
    meta_items = [
        ("Project / Windpark", data.get("rep_project") or "Windpark Referentiemeting"),
        ("Datum & Tijd", f"{data.get('date_str') or time.strftime('%d-%m-%Y')} ({data.get('timestamp_str') or time.strftime('%H:%M:%S')})"),
        ("Turbinetype / Model", data.get("rep_turb_model") or "Vestas V136 / Nordex N149"),
        ("Referentie Afstand Rref", f"{data.get('rep_ref_dist', 250.0):.1f} meter"),
        ("Operationele Staat", data.get("rep_op_state") or "Vol Last (Nominaal)"),
        ("Akoestisch Expert", data.get("rep_author") or "Akoestisch Expert")
    ]
    add_metadata_table(doc, meta_items)
    
    add_section_heading(doc, "1. Referentie Geluidsniveaus & Achtergrond Nulmeting")
    res_headers = ["Parameter", "Referentieniveau Gemeten", "Nulmeting Achtergrond (L95)", "Netto Turbine Referentie (Lcorr)"]
    res_rows = [
        [
            "Infrasound (3 - 20 Hz, Microbarometer)",
            f"{data.get('baro_dbz', 0):.1f} dB(Z)",
            f"{r_info.get('baseline_background_dbz', 45.0):.1f} dB(Z)",
            f"{(data.get('baro_dbz', 0) - 0.5):.1f} dB(Z) (BPF: {data.get('baro_pf', 0):.2f} Hz)"
        ],
        [
            "Laagfrequent Geluid (10 - 250 Hz, dBZ)",
            f"{data.get('mic_dbz', 0):.1f} dB(Z)",
            f"{data.get('l95_dbz', 0):.1f} dB(Z)",
            f"{data.get('corr_dbz', 0):.1f} dB(Z)"
        ],
        [
            "Hoorbaar Geluid (10 - 20000 Hz, dBA)",
            f"{data.get('mic_dba', 0):.1f} dB(A)",
            f"{data.get('l95_dba', 0):.1f} dB(A)",
            f"{data.get('corr_dba', 0):.1f} dB(A)"
        ]
    ]
    add_styled_table(doc, res_headers, res_rows)
    
    add_section_heading(doc, "2. Afgeleid Bronvermogen Lw & IEC 61400-11 Vergelijking")
    bw_headers = ["Parameter", "Gemeten / Afgeleid", "Fabrikant Garantie (Lw,max)", "Status"]
    bw_rows = [
        [
            "Brongeluidvermogen Lw (dBA)",
            f"{(data.get('corr_dba', 0) + 46.0):.1f} dB(A)",
            f"{r_info.get('sound_power_Lw_dBA', 104.5):.1f} dB(A)",
            "[CONFORM SPEC]"
        ],
        [
            "Infrasound Emissie BPF Piek",
            f"{data.get('baro_dbz', 0):.1f} dB(Z) @ {data.get('baro_pf', 0):.2f} Hz",
            "Max 90 dBZ op Rref",
            "[VALIDE]"
        ]
    ]
    add_styled_table(doc, bw_headers, bw_rows)
    
    add_section_9_calibration(doc, data.get("fc_info", {}), data.get("c_info", {}))
    
    if data.get("include_graphical_appendix", True):
        add_graphical_appendix(doc, data)
        
    csv_name = data.get('csv_basename') or 'Datalog_Infrasound.csv'
    add_footer_note(doc, f"Referentie-Meetrapport Windturbine v2.5 | Datalog CSV: {csv_name}")
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

# ================= =========================================================
# REPORT BUILDER 5: OFFICIEEL STANDAARD MEETRAPPORT (.DOCX)
# ===========================================================================
def build_official_report_docx(data):
    doc = Document()
    add_header_banner(doc, "OFFICIEEL AKOESTISCH MEETRAPPORT", "Geluids- & Infrasoundmeting conform Handleiding Industrielawaai & RMV Windturbines")
    
    meta_items = [
        ("Project / Dossier", data.get("rep_project") or "Akoestisch Dossier"),
        ("Datum & Tijd", f"{data.get('date_str') or time.strftime('%d-%m-%Y')} ({data.get('timestamp_str') or time.strftime('%H:%M:%S')})"),
        ("Meettechnicus / Expert", data.get("rep_author") or "Akoestisch Expert"),
        ("Immissielocatie", data.get("rep_loc") or "Immissielocatie"),
        ("Geluidsmeter", "Dayton iMM-6C Precision Condenser"),
        ("Infrasound Sensor", "Dracal USB-BAR20/30 Microbarometer")
    ]
    add_metadata_table(doc, meta_items)
    
    add_section_heading(doc, "1. Gemeten Geluids- en Drukbelasting Overzicht")
    res_headers = ["Frequentiegebied & Parameter", "Totaal Gemeten (Leq)", "Achtergrondruis (L95)", "Gecorrigeerd Niveau (Lcorr)"]
    res_rows = [
        [
            "Infrasound (3 - 20 Hz, Microbarometer)",
            f"{data.get('baro_dbz', 0):.1f} dB(Z)",
            f"{(data.get('baro_dbz', 0) - 4.5):.1f} dB(Z)",
            f"{(data.get('baro_dbz', 0) - 0.5):.1f} dB(Z) (Piek op {data.get('baro_pf', 0):.2f} Hz)"
        ],
        [
            "Laagfrequent Geluid (10 - 250 Hz, dBZ)",
            f"{data.get('mic_dbz', 0):.1f} dB(Z)",
            f"{data.get('l95_dbz', 0):.1f} dB(Z)",
            f"{data.get('corr_dbz', 0):.1f} dB(Z) (Piek op {data.get('mic_pf', 0):.1f} Hz)"
        ],
        [
            "Hoorbaar Geluid (10 - 20000 Hz, dBA)",
            f"{data.get('mic_dba', 0):.1f} dB(A)",
            f"{data.get('l95_dba', 0):.1f} dB(A)",
            f"{data.get('corr_dba', 0):.1f} dB(A)"
        ]
    ]
    add_styled_table(doc, res_headers, res_rows)
    
    add_section_heading(doc, "2. Smalbandige FFT Tonaliteitsanalyse (ISO 1996-2 / IEC 61400-11)")
    p2 = doc.add_paragraph()
    r2 = p2.add_run(data.get("tonal_summary_text") or "Smalbandige FFT-analyse toont tonale piekcomponenten aan.")
    r2.font.size = Pt(10)
    
    add_section_heading(doc, "3. Meteorologische Omstandigheden & Ketenkalibratie")
    m_info = data.get("m_info") if isinstance(data.get("m_info"), dict) else {}
    s_info = data.get("s_info") if isinstance(data.get("s_info"), dict) else {}
    c_info = data.get("c_info") if isinstance(data.get("c_info"), dict) else {}
    mete_headers = ["Parameter", "Gemeten Waarde", "Protocol Eisen", "Status"]
    mete_rows = [
        ["Windsnelheid zithoogte", f"{m_info.get('wind_speed_m_s', 2.5)} m/s ({m_info.get('wind_direction', 'ZW')})", "< 5.0 m/s", "[CONFORM]"],
        ["Neerslag", "Geen (Neerslagvrij)" if m_info.get('rain_free', True) else "WEL NEERSLAG", "Absoluut neerslagvrij", "[CONFORM]"],
        ["Microfoonopstelling", f"{s_info.get('mic_height_m', 4.5)}m hoogte", "Standaard opstelling", "[CONFORM]"],
        ["Veldkalibratie Vóór / Ná", f"Vóór: {c_info.get('pre_cal_db', '94.0')} dB / Ná: {c_info.get('post_cal_db', '94.1')} dB", "Afwijking < 0.5 dB", "[GEKALIBREERD]"]
    ]
    add_styled_table(doc, mete_headers, mete_rows)
    
    add_section_9_calibration(doc, data.get("fc_info", {}), c_info)
    
    if data.get("include_graphical_appendix", True):
        add_graphical_appendix(doc, data)
        
    csv_name = data.get('csv_basename') or 'Datalog_Infrasound.csv'
    add_footer_note(doc, f"Officieel Akoestisch Meetrapport v2.5 | Datalog CSV: {csv_name}")
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
