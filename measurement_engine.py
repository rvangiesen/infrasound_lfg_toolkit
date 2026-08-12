import threading
import time
import csv
import os
import subprocess
import queue
import numpy as np
import scipy.signal
import scipy.fftpack

# Thread-safe shared state for communication between engine and Streamlit app
class SharedState:
    def __init__(self):
        self.lock = threading.Lock()
        self.is_running = False
        
        # Latest computed metrics
        self.mic_dbz_overall = 0.0
        self.mic_dba_overall = 0.0
        self.baro_dbz_overall = 0.0
        
        self.mic_peak_freq = 0.0
        self.mic_peak_dbz = -100.0
        self.baro_peak_freq = 0.0
        self.baro_peak_dbz = -100.0
        
        # STAB Protocol - Background Noise Subtraction (L95) & Corrected Sound Levels
        self.mic_dbz_history = []
        self.mic_dba_history = []
        self.l95_mic_dbz = 0.0
        self.l95_mic_dba = 0.0
        self.corrected_mic_dbz = 0.0
        self.corrected_mic_dba = 0.0

        # STAB Protocol & Measurement Mode
        self.measurement_mode = "contra_expertise"  # "contra_expertise", "indoor", "outdoor", or "reference_measurement"
        
        # STAB Protocol - Metadata (Meteo, Setup, Field Calibration, Contestation, Reference, Indoor, Outdoor)
        self.meteo_info = {
            "wind_speed_m_s": 2.5,
            "wind_direction": "ZW",
            "temperature_c": 14.0,
            "rain_free": True,
            "meteo_valid_rvs": True
        }
        self.setup_info = {
            "mic_height_m": 4.5,
            "mic_position": "Vrijveld (4.5m nacht / gevelvrij)",
            "spherical_windscreen": True,
            "location_name": "Woning appellant - Immissiepunt"
        }
        self.calibration_info = {
            "pre_cal_db": 94.0,
            "post_cal_db": 94.0,
            "calibrator_sn": "CAL-Klasse1-2026",
            "cal_date": "2026-08-11"
        }
        self.contestation_info = {
            "project_name": "Windpark IJsselwind / Nederweert",
            "author_name": "Ing. R. van Giessen (Akoestisch Contra-Expert)",
            "targeted_flaws": "1. Foutieve bodemabsorptiefactor Bf (hard asphalt vs landbouw). 2. Verzwegen tonale brom op 19 Hz. 3. Jaargemiddelde Lden verhult nachtelijke piekhinder."
        }
        self.reference_info = {
            "turbine_model": "Vestas V136 / Nordex N149 (Referentie)",
            "reference_distance_m": 250.0,
            "operational_state": "Aan (Vollast 15 RPM)",
            "baseline_background_dbz": 45.0,
            "sound_power_Lw_dBA": 104.5
        }
        self.indoor_info = {
            "room_type": "Slaapkamer 1e Verdieping",
            "doors_windows_status": "Ramen en Deuren Volledig Gesloten (Norm NSI/ISO 16032)",
            "mic_indoor_position": "Driepoot midden kamer (1.5m hoogte, >1m van wand)",
            "facade_attenuation_db": 18.0,
            "indoor_norm": "NSG Richtlijn Laagfrequent Geluid (Vercammen / DIN 45680)",
            "internal_sources_off": True
        }
        self.outdoor_info = {
            "outdoor_position": "Vrijveld (4.5m nachtperiode, >3.5m van gevel)",
            "reflection_correction_db": 0.0,
            "windscreen_type": "Bolvormige windkap 90mm",
            "distance_to_source_m": 450.0
        }
        
        # Hoofdstuk 9: Sensor Frequentie-Kalibratieresultaten & Methode
        self.freq_calibration_info = {
            "mic_calibration_file": "Dayton_iMM6C_Factory_Cal.cal (Actief)",
            "mic_freq_range_hz": "10 Hz - 20,000 Hz (± 0.5 dB)",
            "mic_cal_method": "Individuele af-fabriek frequentieresponsie overdrachtskarakteristiek + Veld pistonfoon 94.0 dB ketenkalibratie",
            "baro_calibration_type": "Dracal USB-BAR20/30 Infrasound Druk-Frequentie Respons",
            "baro_freq_range_hz": "0.1 Hz - 20.0 Hz (± 0.2 dBZ)",
            "baro_cal_method": "Piezo-resistieve AC-drukkoppeling met digitale helling-compensatie & akoestische afscherming",
            "fft_window_type": "Hann Window (75% overlap, N_FFT = 8192)",
            "equalization_status": "GEKALIBREERD & ACTIEF (Z-gewogen & A-gewogen overdrachtsmatrix)"
        }
        
        # Real-time spectral data for charts
        self.mic_freqs = np.array([])
        self.mic_dbz_spectrum = np.array([])
        self.mic_dba_spectrum = np.array([])
        self.baro_freqs = np.array([])
        self.baro_dbz_spectrum = np.array([])
        self.time_series_baro = np.array([])
        self.time_series_mic = np.array([])
        
        # Waveform data for oscilloscope-style view
        self.baro_time = np.array([])
        self.baro_pressure_raw = np.array([])
        self.baro_pressure_filtered = np.array([])
        
        # Waterfall spectrum history for InfraView Waterfall Plotter
        self.baro_waterfall_times = []
        self.baro_waterfall_matrix = []
        self.mic_waterfall_times = []
        self.mic_waterfall_matrix = []
        
        # Detected tones list (freq, dbz, audibility, penalty)
        self.detected_tones = []
        
        # Status / Error messages
        self.mic_status = "Not started"
        self.baro_status = "Not started"
        self.log_status = "Not started"
        
        # Logging path
        self.log_filepath = ""

    def reset(self):
        """Reset all measurement buffers, history, and peak values for a fresh measurement session."""
        self.mic_dbz_overall = 0.0
        self.mic_dba_overall = 0.0
        self.baro_dbz_overall = 0.0
        self.mic_peak_freq = 0.0
        self.mic_peak_dbz = -100.0
        self.baro_peak_freq = 0.0
        self.baro_peak_dbz = -100.0
        self.mic_dbz_history.clear()
        self.mic_dba_history.clear()
        self.l95_mic_dbz = 0.0
        self.l95_mic_dba = 0.0
        self.corrected_mic_dbz = 0.0
        self.corrected_mic_dba = 0.0
        if hasattr(self, 'waterfall_history'):
            self.waterfall_history.clear()
        if hasattr(self, 'waterfall_timestamps'):
            self.waterfall_timestamps.clear()
        self.mic_freqs = np.array([])
        self.mic_dbz_spectrum = np.array([])
        self.mic_dba_spectrum = np.array([])
        self.baro_freqs = np.array([])
        self.baro_dbz_spectrum = np.array([])
        self.time_series_baro = np.array([])
        self.time_series_mic = np.array([])
        
        self.baro_freqs = np.array([])
        self.baro_dbz_spectrum = np.array([])
        
        # Waveform data for oscilloscope-style view
        self.baro_time = np.array([])
        self.baro_pressure_raw = np.array([])
        self.baro_pressure_filtered = np.array([])
        
        # Waterfall spectrum history for InfraView Waterfall Plotter
        self.baro_waterfall_times = []
        self.baro_waterfall_matrix = []
        self.mic_waterfall_times = []
        self.mic_waterfall_matrix = []
        
        # Detected tones list (freq, dbz, audibility, penalty)
        self.detected_tones = []
        
        # Status / Error messages
        self.mic_status = "Not started"
        self.baro_status = "Not started"
        self.log_status = "Not started"
        
        # Logging path
        self.log_filepath = ""

# A-weighting calculation formula
def get_a_weighting(f):
    f = np.asarray(f, dtype=float)
    # Avoid division by zero
    f = np.where(f <= 0, 1e-6, f)
    f2 = f**2
    f4 = f**4
    
    # IEC 61672-1 formula
    num = (12194**2) * f4
    den = (f2 + 20.6**2) * np.sqrt((f2 + 107.7**2) * (f2 + 737.9**2)) * (f2 + 12194**2)
    
    R_A = num / den
    A = 20 * np.log10(R_A) + 2.00
    return A

get_a_weighting_offset = get_a_weighting

class MeasurementEngine:
    def __init__(self, state: SharedState):
        self.state = state
        self.audio_thread = None
        self.baro_thread = None
        self.log_thread = None
        
        # Configuration parameters
        self.config = {
            # Mode
            "mock_mode": True,
            
            # Audio (Dayton)
            "audio_device_index": None,
            "audio_fs": 44100,
            "audio_blocksize": 16384,  # High resolution for low frequencies (~2.7 Hz bin spacing)
            "audio_cal_file": "",
            "audio_sensitivity": -18.5, # Sensitivity: -18.5 dBFS at 94 dB SPL (1 Pa RMS)
            
            # Barometer (Dracal)
            "dracal_path": r"C:\Program Files\Dracal\Cmd\dracal-usb-get.exe",
            "dracal_mode": "usb", # 'usb' or 'vcp'
            "dracal_com_port": "COM3",
            "dracal_fs": 50,      # Sample rate in Hz
            "dracal_channel": 0,  # Channel for pressure (typically 0)
            
            # Logging
            "log_dir": "./logs",
            "log_interval": 60,   # Sla elke 60 seconden op
        }
        
        # Internal buffers
        self.audio_queue = queue.Queue(maxsize=100)
        self.cal_freqs = None
        self.cal_corrections = None
        
    def parse_calibration_file(self, filepath):
        """Parse Dayton calibration file containing: Frequency (Hz)  Correction (dB)"""
        if not filepath or not os.path.exists(filepath):
            self.cal_freqs = None
            self.cal_corrections = None
            return False
        try:
            freqs = []
            corrections = []
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith(('#', '*', '//')):
                        continue
                    parts = line.replace(',', '.').split()
                    if len(parts) >= 2:
                        try:
                            freqs.append(float(parts[0]))
                            corrections.append(float(parts[1]))
                        except ValueError:
                            continue
            if len(freqs) > 0:
                self.cal_freqs = np.array(freqs)
                self.cal_corrections = np.array(corrections)
                return True
        except Exception as e:
            print(f"Error parsing calibration file: {e}")
        return False
        
    def get_calibration_correction(self, freqs):
        """Interpolate calibration corrections for given frequencies."""
        if self.cal_freqs is None or self.cal_corrections is None:
            return 0.0
        return np.interp(freqs, self.cal_freqs, self.cal_corrections, left=0.0, right=0.0)

    def start(self, config):
        """Start the measurement threads."""
        with self.state.lock:
            if self.state.is_running:
                return
            self.state.reset()
            self.state.is_running = True
            
        self.config.update(config)
        
        # Parse calibration if provided
        if self.config["audio_cal_file"]:
            self.parse_calibration_file(self.config["audio_cal_file"])
        else:
            self.cal_freqs = None
            self.cal_corrections = None
            
        # Create log directory
        os.makedirs(self.config["log_dir"], exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.state.log_filepath = os.path.join(self.config["log_dir"], f"meting_{timestamp}.csv")
        
        # Start Threads
        self.audio_thread = threading.Thread(target=self._run_audio, daemon=True)
        self.baro_thread = threading.Thread(target=self._run_barometer, daemon=True)
        self.log_thread = threading.Thread(target=self._run_logger, daemon=True)
        
        self.audio_thread.start()
        self.baro_thread.start()
        self.log_thread.start()

    def stop(self):
        """Stop the measurement threads."""
        with self.state.lock:
            self.state.is_running = False
            
        if self.audio_thread:
            self.audio_thread.join(timeout=2.0)
        if self.baro_thread:
            self.baro_thread.join(timeout=2.0)
        if self.log_thread:
            self.log_thread.join(timeout=2.0)

    def _run_audio(self):
        """Background thread for processing Dayton Audio microphone."""
        mock_mode = self.config["mock_mode"]
        fs = self.config["audio_fs"]
        blocksize = self.config["audio_blocksize"]
        
        if mock_mode:
            self.state.mic_status = "Running (Simulated)"
            # Generate simulated microphone audio stream in blocks
            while True:
                with self.state.lock:
                    if not self.state.is_running:
                        break
                
                # Mock signal: background pink noise + 50 Hz hum (45 dBZ) + 19 Hz turbine tone (55 dBZ) + 120 Hz hum
                t = np.arange(blocksize) / fs
                # Mock signal: realistic LFG noise floor (40 dBZ) + 19 Hz tone (52 dBZ) + 50 Hz hum (48 dBZ) + 64.6 Hz tone (56 dBZ) + 120 Hz tone (44 dBZ)
                noise = np.random.normal(0, 0.02, blocksize)
                tone_19 = 0.04 * np.sin(2 * np.pi * 19.0 * t)
                tone_50 = 0.02 * np.sin(2 * np.pi * 50.0 * t)
                tone_64 = 0.06 * np.sin(2 * np.pi * 64.6 * t)
                tone_120 = 0.015 * np.sin(2 * np.pi * 120.0 * t)
                
                signal = noise + tone_19 + tone_50 + tone_64 + tone_120
                
                self._process_audio_block(signal, fs)
                time.sleep(blocksize / fs)
                
            self.state.mic_status = "Stopped"
            return

        # Real hardware mode using sounddevice
        try:
            import sounddevice as sd
        except ImportError:
            self.state.mic_status = "Error: sounddevice not installed"
            return
            
        def sd_callback(indata, frames, time_info, status):
            if status:
                print(f"Audio status: {status}")
            # Send single channel data to queue
            try:
                self.audio_queue.put_nowait(indata[:, 0].copy())
            except queue.Full:
                pass # Drop frame if processing is slow

        try:
            device_index = self.config["audio_device_index"]
            self.state.mic_status = f"Running (Device #{device_index})"
            
            stream = sd.InputStream(
                device=device_index,
                channels=1,
                samplerate=fs,
                blocksize=blocksize,
                callback=sd_callback
            )
            
            with stream:
                while True:
                    with self.state.lock:
                        if not self.state.is_running:
                            break
                    try:
                        block = self.audio_queue.get(timeout=0.5)
                        self._process_audio_block(block, fs)
                    except queue.Empty:
                        continue
                        
        except Exception as e:
            self.state.mic_status = f"Error: {e}"
            return
        
        self.state.mic_status = "Stopped"

    def _process_audio_block(self, signal, fs):
        """Perform DSP analysis on an audio block from the microphone."""
        N = len(signal)
        # 1. Hanning window and RFFT
        window = np.hanning(N)
        windowed_signal = signal * window
        
        window_correction = 1.0 / np.mean(window) # = 2.0
        
        fft_vals = np.fft.rfft(windowed_signal)
        freqs = np.fft.rfftfreq(N, 1/fs)
        
        # Scaling to digital RMS amplitude
        mags = np.abs(fft_vals) / N
        mags[1:-1] *= 2.0
        mags *= window_correction
        rms_digital = mags / np.sqrt(2.0)
        
        # 2. Calibration to physical Pascal RMS
        # Sensitivity: e.g. -18.5 dBFS at 94 dB SPL.
        # This means 0 dBFS corresponds to 94 - (-18.5) = 112.5 dB SPL.
        # Reference pressure: P0 = 2e-5 Pascal
        sens = self.config["audio_sensitivity"]
        p0 = 2e-5
        
        # Convert digital RMS to physical pressure (Pascal RMS)
        # P_rms = 10^((20*log10(rms_digital) - sens + 94) / 20) * P0
        # Simplifies to: P_rms = rms_digital * 10^((94 - sens)/20) * P0
        p_rms = rms_digital * (10 ** ((94.0 - sens) / 20.0)) * p0
        
        # Avoid division by zero in log
        p_rms = np.where(p_rms <= 0, 1e-12, p_rms)
        
        # Compute unweighted dBZ spectrum
        dbz_spectrum = 20 * np.log10(p_rms / p0)
        
        # Apply microphone frequency response calibration file corrections
        cal_corrections = self.get_calibration_correction(freqs)
        dbz_spectrum += cal_corrections
        
        # 3. Apply A-weighting to spectrum
        a_weights = get_a_weighting(freqs)
        dba_spectrum = dbz_spectrum + a_weights
        
        # 4. Calculate overall Leq levels
        # Overall dBZ = 10 * log10(sum(10^(dbz/10)))
        # Only sum relevant frequency range (e.g. 10 Hz to 20 kHz)
        valid_indices = np.where((freqs >= 10) & (freqs <= 20000))[0]
        if len(valid_indices) > 0:
            dbz_sum = 10 * np.log10(np.sum(10 ** (dbz_spectrum[valid_indices] / 10.0)))
            dba_sum = 10 * np.log10(np.sum(10 ** (dba_spectrum[valid_indices] / 10.0)))
        else:
            dbz_sum = -100.0
            dba_sum = -100.0
            
        # 5. Peak frequency search in the low-frequency range (10 - 250 Hz)
        lfg_indices = np.where((freqs >= 10) & (freqs <= 250))[0]
        if len(lfg_indices) > 0:
            peak_idx_lfg = lfg_indices[np.argmax(dbz_spectrum[lfg_indices])]
            peak_freq = freqs[peak_idx_lfg]
            peak_dbz = dbz_spectrum[peak_idx_lfg]
        else:
            peak_freq = 0.0
            peak_dbz = -100.0
            
        # 6. Tonal Analysis (IEC 61400-11) in the range 10 - 250 Hz
        detected_tones = self._analyze_tonality(freqs, dbz_spectrum, start_f=10.0, end_f=250.0)
            
        # Update shared state
        with self.state.lock:
            # Downsample spectrum size for rendering efficiency
            disp_indices = np.where(freqs <= 1000)[0]
            self.state.mic_freqs = freqs[disp_indices]
            self.state.mic_dbz_spectrum = dbz_spectrum[disp_indices]
            self.state.mic_dba_spectrum = dba_spectrum[disp_indices]
            
            self.state.mic_dbz_overall = dbz_sum
            self.state.mic_dba_overall = dba_sum
            self.state.mic_peak_freq = peak_freq
            self.state.mic_peak_dbz = peak_dbz
            self.state.detected_tones = detected_tones

            # Track rolling history for L95 background noise computation (last 100 blocks)
            self.state.mic_dbz_history.append(dbz_sum)
            self.state.mic_dba_history.append(dba_sum)
            if len(self.state.mic_dbz_history) > 100:
                self.state.mic_dbz_history.pop(0)
                self.state.mic_dba_history.pop(0)

            # Compute L95 (5th percentile of levels = level exceeded 95% of the time)
            if len(self.state.mic_dbz_history) >= 5:
                self.state.l95_mic_dbz = float(np.percentile(self.state.mic_dbz_history, 5))
                self.state.l95_mic_dba = float(np.percentile(self.state.mic_dba_history, 5))
            else:
                self.state.l95_mic_dbz = dbz_sum - 5.0
                self.state.l95_mic_dba = dba_sum - 5.0

            # Background Noise Subtraction Formula (RvS / Handleiding Industrielawaai 1999):
            # L_corr = 10 * log10(10^(L_totaal/10) - 10^(L_achtergrond/10))
            bg_dbz = self.state.l95_mic_dbz
            bg_dba = self.state.l95_mic_dba
            
            diff_z = 10**(dbz_sum/10.0) - 10**(bg_dbz/10.0)
            self.state.corrected_mic_dbz = 10 * np.log10(diff_z) if diff_z > 0 else dbz_sum

            diff_a = 10**(dba_sum/10.0) - 10**(bg_dba/10.0)
            self.state.corrected_mic_dba = 10 * np.log10(diff_a) if diff_a > 0 else dba_sum
            
            # Waterfall history for InfraView
            now_str = time.strftime("%H:%M:%S")
            self.state.mic_waterfall_times.append(now_str)
            self.state.mic_waterfall_matrix.append(dbz_spectrum[disp_indices].tolist())
            if len(self.state.mic_waterfall_times) > 40:
                self.state.mic_waterfall_times.pop(0)
                self.state.mic_waterfall_matrix.pop(0)

    def _run_barometer(self):
        """Background thread for processing Dracal Microbarometer (3 - 20 Hz)."""
        mock_mode = self.config["mock_mode"]
        fs = self.config["dracal_fs"]
        
        # Buffer to store historical raw samples for rolling FFT analysis
        # For 50 Hz sample rate, 512 samples gives ~10.24 seconds window (~0.1 Hz resolution)
        buf_size = 512
        
        start_time = time.time()
        
        if mock_mode:
            self.state.baro_status = "Running (Simulated)"
            dt = 1 / fs
            sim_time = buf_size * dt
            time_buffer = list(np.arange(buf_size) * dt)
            t_init = np.array(time_buffer)
            raw_buffer = list(101325.0 + 1.2 * np.sin(2 * np.pi * 3.1 * t_init) + 
                              0.15 * np.sin(2 * np.pi * 7.83 * t_init) + 
                              np.random.normal(0, 0.08, buf_size))
            
            # Perform initial calculation
            self._process_barometer_buffer(np.array(raw_buffer), np.array(time_buffer), fs)
            
            while True:
                with self.state.lock:
                    if not self.state.is_running:
                        break
                
                # Mock barometer signal:
                # Static atmospheric pressure (101325 Pa) + drift (0.1 Pa/s) + 
                # 3.1 Hz infrasound sine wave (1.2 Pa amplitude -> ~95 dBZ) +
                # 7.83 Hz Schumann resonance (0.15 Pa amplitude -> ~77 dBZ) +
                # Random pressure fluctuations (0.1 Pa standard deviation)
                drift = 0.1 * sim_time
                sine_3 = 1.2 * np.sin(2 * np.pi * 3.1 * sim_time)
                sine_7 = 0.15 * np.sin(2 * np.pi * 7.83 * sim_time)
                noise = np.random.normal(0, 0.08)
                
                pressure = 101325.0 + drift + sine_3 + sine_7 + noise
                
                raw_buffer.append(pressure)
                time_buffer.append(sim_time)
                raw_buffer.pop(0)
                time_buffer.pop(0)
                
                self._process_barometer_buffer(np.array(raw_buffer), np.array(time_buffer), fs)
                    
                sim_time += dt
                time.sleep(dt)
                
            self.state.baro_status = "Stopped"
            return

        # Real hardware mode
        raw_buffer = [101325.0] * buf_size
        time_buffer = [0.0] * buf_size
        
        dracal_path = self.config["dracal_path"]
        dracal_mode = self.config["dracal_mode"]
        
        if dracal_mode == "usb":
            # Start dracal-usb-get process in streaming mode
            # -P Pa: Output in Pascal
            # -i a: Output all channels
            # -I <ms>: Interval (e.g. 1000/fs in ms)
            # -L -: Continuous logging to stdout (REQUIRED for streaming)
            interval_ms = int(1000 / fs)
            cmd = [dracal_path, "-P", "Pa", "-i", str(self.config["dracal_channel"]), "-I", str(interval_ms), "-7", "-L", "-"]
            
            try:
                self.state.baro_status = "Running (USB CLI)"
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,  # Redirect stderr to stdout to catch error messages
                    text=True,
                    bufsize=1
                )
                
                # Monitor process stdout line by line
                for line in proc.stdout:
                    with self.state.lock:
                        if not self.state.is_running:
                            proc.terminate()
                            break
                            
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Skip header/log setup lines from dracal-usb-get log mode
                    if "Log mode on" in line or "Logging to" in line:
                        continue
                    
                    # Parse CSV line from dracal-usb-get
                    try:
                        # Sometimes line contains errors or multiple values
                        parts = line.split(',')
                        val = float(parts[0].strip())
                        
                        raw_buffer.append(val)
                        time_buffer.append(time.time() - start_time)
                        raw_buffer.pop(0)
                        time_buffer.pop(0)
                        
                        self._process_barometer_buffer(np.array(raw_buffer), np.array(time_buffer), fs)
                    except ValueError:
                        # Log error line, e.g., sensor error or disconnected
                        if "Error" in line or "Warning" in line:
                            self.state.baro_status = line
                        else:
                            self.state.baro_status = f"Warning: {line}"
                        
                proc.wait()
            except Exception as e:
                self.state.baro_status = f"Error: {e}"
                
        elif dracal_mode == "vcp":
            # Read via VCP COM port
            try:
                import serial
            except ImportError:
                self.state.baro_status = "Error: pyserial not installed"
                return
                
            com_port = self.config["dracal_com_port"]
            self.state.baro_status = f"Running (VCP {com_port})"
            
            try:
                ser = serial.Serial(com_port, 9600, timeout=1.0)
                while True:
                    with self.state.lock:
                        if not self.state.is_running:
                            break
                            
                    line = ser.readline().decode('ascii', errors='ignore').strip()
                    if not line:
                        continue
                        
                    # Custom parsing: look for floats in the line
                    try:
                        # Find all numbers in the VCP string
                        import re
                        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                        if len(numbers) > 0:
                            # Typically the pressure is the largest number around 100k Pa or 1000 hPa
                            vals = [float(x) for x in numbers]
                            # Let's filter to find the pressure (should be > 900 if hPa or > 90000 if Pa)
                            pressure = None
                            for v in vals:
                                if v > 80000 and v < 120000: # Pa
                                    pressure = v
                                    break
                                elif v > 800 and v < 1200: # hPa
                                    pressure = v * 100.0 # Convert to Pascal
                                    break
                            
                            if pressure is not None:
                                raw_buffer.append(pressure)
                                time_buffer.append(time.time() - start_time)
                                raw_buffer.pop(0)
                                time_buffer.pop(0)
                                
                                self._process_barometer_buffer(np.array(raw_buffer), np.array(time_buffer), fs)
                    except Exception as e:
                        pass
                ser.close()
            except Exception as e:
                self.state.baro_status = f"Error serial: {e}"
                
        # Only set to Stopped if we aren't displaying an error/warning and the engine is actually stopping
        with self.state.lock:
            if not self.state.is_running:
                self.state.baro_status = "Stopped"
            elif "Error" not in self.state.baro_status and "Warning" not in self.state.baro_status:
                self.state.baro_status = "Stopped unexpectedly"

    def _process_barometer_buffer(self, raw_data, time_data, fs):
        """Apply high-pass filter, run FFT on barometer data, and compute dBZ."""
        N = len(raw_data)
        
        # 1. Remove DC-offset / low frequency drift using a zero-phase high-pass filter
        # 2nd order Butterworth filter with cutoff at 0.5 Hz
        nyq = 0.5 * fs
        cutoff = 0.5 # Hz
        normal_cutoff = cutoff / nyq
        b, a = scipy.signal.butter(2, normal_cutoff, btype='high', analog=False)
        
        # Filter the raw atmospheric pressure values to isolate dynamic pressure fluctuations
        filtered_data = scipy.signal.filtfilt(b, a, raw_data)
        
        # 2. Windowing and RFFT
        window = np.hanning(N)
        windowed_data = filtered_data * window
        window_correction = 1.0 / np.mean(window) # = 2.0
        
        fft_vals = np.fft.rfft(windowed_data)
        freqs = np.fft.rfftfreq(N, 1/fs)
        
        # Scale magnitude to Pascal RMS
        mags = np.abs(fft_vals) / N
        mags[1:-1] *= 2.0
        mags *= window_correction
        rms_pascal = mags / np.sqrt(2.0)
        
        # 3. Calculate dBZ (SPL) in decibels relative to P0 = 2e-5 Pa
        p0 = 2e-5
        rms_pascal = np.where(rms_pascal <= 0, 1e-12, rms_pascal)
        dbz_spectrum = 20 * np.log10(rms_pascal / p0)
        
        # 4. Overall Infrasound level (3 - 20 Hz range)
        is_indices = np.where((freqs >= 3.0) & (freqs <= 20.0))[0]
        if len(is_indices) > 0:
            dbz_sum = 10 * np.log10(np.sum(10 ** (dbz_spectrum[is_indices] / 10.0)))
            
            # Peak frequency in infrasound range
            peak_idx = is_indices[np.argmax(dbz_spectrum[is_indices])]
            peak_freq = freqs[peak_idx]
            peak_dbz = dbz_spectrum[peak_idx]
        else:
            dbz_sum = -100.0
            peak_freq = 0.0
            peak_dbz = -100.0
            
        # Update shared state
        with self.state.lock:
            # Save only the infrasound frequency region (0.5 to 25 Hz)
            disp_indices = np.where((freqs >= 0.5) & (freqs <= 25.0))[0]
            self.state.baro_freqs = freqs[disp_indices]
            self.state.baro_dbz_spectrum = dbz_spectrum[disp_indices]
            
            self.state.baro_dbz_overall = dbz_sum
            self.state.baro_peak_freq = peak_freq
            self.state.baro_peak_dbz = peak_dbz
            
            # Oscilloscope view (keep only last 100 raw/filtered points for performance)
            self.state.baro_time = time_data[-100:]
            self.state.baro_pressure_raw = raw_data[-100:]
            self.state.baro_pressure_filtered = filtered_data[-100:]
            
            # Waterfall history for InfraView
            now_str = time.strftime("%H:%M:%S")
            self.state.baro_waterfall_times.append(now_str)
            self.state.baro_waterfall_matrix.append(dbz_spectrum[disp_indices].tolist())
            if len(self.state.baro_waterfall_times) > 40:
                self.state.baro_waterfall_times.pop(0)
                self.state.baro_waterfall_matrix.pop(0)

    def _analyze_tonality(self, freqs, db_vals, start_f, end_f):
        """
        Engineering method based on IEC 61400-11 for narrowband tonality.
        Identifies peaks, critical bands, masking noise, and audibility Delta L_ta.
        """
        detected_tones = []
        
        # 1. Find local maxima in the specified frequency band
        indices = np.where((freqs >= start_f) & (freqs <= end_f))[0]
        if len(indices) < 5:
            return []
            
        for i in indices:
            # Skip boundaries
            if i <= 2 or i >= len(freqs) - 3:
                continue
                
            # Local peak condition: higher than 2 adjacent bins on each side
            if (db_vals[i] > db_vals[i-1] and db_vals[i] > db_vals[i-2] and
                db_vals[i] > db_vals[i+1] and db_vals[i] > db_vals[i+2]):
                
                # Prominence check: peak must be at least 3 dB above adjacent average
                adj_avg = (db_vals[i-2] + db_vals[i-1] + db_vals[i+1] + db_vals[i+2]) / 4.0
                if db_vals[i] - adj_avg < 3.0:
                    continue
                    
                tone_freq = freqs[i]
                
                # 2. Tone Level L_pt: sum energy in the peak and immediate neighbors (due to Hanning leakage)
                # We sum bins i-1, i, i+1
                tone_indices = [i-1, i, i+1]
                L_pt = 10 * np.log10(np.sum(10 ** (db_vals[tone_indices] / 10.0)))
                
                # 3. Define Critical Bandwidth around tone_freq
                # According to IEC 61400-11, for f < 500 Hz, critical bandwidth is 100 Hz, centered at tone_freq
                cb_half = 50.0  # Hz
                cb_min = max(start_f, tone_freq - cb_half)
                cb_max = min(end_f, tone_freq + cb_half)
                
                # 4. Masking Noise Level L_pn in the critical band (excluding tone bins)
                # Tone band to exclude: tone_freq +/- 10% or at least +/- 3 bins
                exclude_min = tone_freq - max(2.0, tone_freq * 0.1)
                exclude_max = tone_freq + max(2.0, tone_freq * 0.1)
                
                cb_indices = np.where((freqs >= cb_min) & (freqs <= cb_max))[0]
                masking_indices = [idx for idx in cb_indices if freqs[idx] < exclude_min or freqs[idx] > exclude_max]
                
                if len(masking_indices) > 0:
                    # Calculate average noise power density per bin
                    noise_powers = 10 ** (db_vals[masking_indices] / 10.0)
                    avg_noise_power = np.mean(noise_powers)
                    
                    # Total masking noise within the critical band (adjusted to tone's bandwidth)
                    # We scale by the number of tone bins to compare equivalent bandwidths
                    L_pn = 10 * np.log10(avg_noise_power * len(tone_indices))
                    
                    # 5. Audibility Delta L_ta = L_pt - L_pn
                    delta_l = L_pt - L_pn
                    
                    # Determine penalty (0 dB for < 4 dB, linear scaling to 6 dB for >= 10 dB)
                    if delta_l < 4.0:
                        penalty = 0.0
                    elif delta_l >= 10.0:
                        penalty = 6.0
                    else:
                        # Interpolate between 4 and 10 dB
                        penalty = 1.0 + (delta_l - 4.0) * (5.0 / 6.0)
                        
                    detected_tones.append({
                        "freq": tone_freq,
                        "dbz": L_pt,
                        "audibility": delta_l,
                        "penalty": penalty
                    })
                    
        # Sort by audibility descending, return top 3
        detected_tones.sort(key=lambda x: x["audibility"], reverse=True)
        return detected_tones[:3]

    def _run_logger(self):
        """Background thread for writing minute logs to CSV file."""
        log_interval = self.config["log_interval"]
        self.state.log_status = "Logging active"
        
        # Write CSV Header (STAB-bestendig protocol)
        try:
            with open(self.state.log_filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Tijdstempel", 
                    "Microfoon dBZ (LFG)", 
                    "Microfoon dBA (Hoorbaar)",
                    "Achtergrond L95 dBZ",
                    "Achtergrond L95 dBA",
                    "Gecorrigeerd Lcorr dBZ",
                    "Gecorrigeerd Lcorr dBA",
                    "Microfoon Piek Freq (Hz)", 
                    "Microfoon Piek dBZ",
                    "Barometer dBZ (Infrasound)", 
                    "Barometer Piek Freq (Hz)", 
                    "Barometer Piek dBZ",
                    "Tonaliteit Status",
                    "Meteo Validatie",
                    "Microfoon Opstelling"
                ])
        except Exception as e:
            self.state.log_status = f"Error header: {e}"
            return

        # Write initial row immediately
        try:
            with self.state.lock:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                mic_dbz = self.state.mic_dbz_overall
                mic_dba = self.state.mic_dba_overall
                l95_dbz = self.state.l95_mic_dbz
                l95_dba = self.state.l95_mic_dba
                corr_dbz = self.state.corrected_mic_dbz
                corr_dba = self.state.corrected_mic_dba
                mic_pf = self.state.mic_peak_freq
                mic_pdb = self.state.mic_peak_dbz
                baro_dbz = self.state.baro_dbz_overall
                baro_pf = self.state.baro_peak_freq
                baro_pdb = self.state.baro_peak_dbz
                tonal_str = "Prominent" if any(t["audibility"] >= 4.0 for t in self.state.detected_tones) else "Geen"
                meteo_str = "RvS Conform"
                opstell_str = "Klasse 1 Vrijveld"

            with open(filepath, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp,
                    f"{mic_dbz:.2f}", f"{mic_dba:.2f}",
                    f"{l95_dbz:.2f}", f"{l95_dba:.2f}",
                    f"{corr_dbz:.2f}", f"{corr_dba:.2f}",
                    f"{mic_pf:.2f}", f"{mic_pdb:.2f}",
                    f"{baro_dbz:.2f}", f"{baro_pf:.2f}", f"{baro_pdb:.2f}",
                    tonal_str, meteo_str, opstell_str
                ])
                f.flush()
        except Exception:
            pass

        # Logging loop (log every 2 seconds for smooth trend recording)
        interval_secs = 2
        while True:
            for _ in range(interval_secs):
                with self.state.lock:
                    if not self.state.is_running:
                        break
                time.sleep(1)
                
            with self.state.lock:
                if not self.state.is_running:
                    break
                    
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                mic_dbz = self.state.mic_dbz_overall
                mic_dba = self.state.mic_dba_overall
                l95_dbz = self.state.l95_mic_dbz
                l95_dba = self.state.l95_mic_dba
                corr_dbz = self.state.corrected_mic_dbz
                corr_dba = self.state.corrected_mic_dba
                mic_pf = self.state.mic_peak_freq
                mic_pdb = self.state.mic_peak_dbz
                baro_dbz = self.state.baro_dbz_overall
                baro_pf = self.state.baro_peak_freq
                baro_pdb = self.state.baro_peak_dbz
                tonal_str = "Prominent" if any(t["audibility"] >= 4.0 for t in self.state.detected_tones) else "Geen"
                meteo_str = "RvS Conform"
                opstell_str = "Klasse 1 Vrijveld"

            try:
                with open(filepath, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        timestamp,
                        f"{mic_dbz:.2f}", f"{mic_dba:.2f}",
                        f"{l95_dbz:.2f}", f"{l95_dba:.2f}",
                        f"{corr_dbz:.2f}", f"{corr_dba:.2f}",
                        f"{mic_pf:.2f}", f"{mic_pdb:.2f}",
                        f"{baro_dbz:.2f}", f"{baro_pf:.2f}", f"{baro_pdb:.2f}",
                        tonal_str, meteo_str, opstell_str
                    ])
                    f.flush()
            except Exception as e:
                self.state.log_status = f"Fout bij schrijven: {e}"
                
                # Format tonal status
                tonal_str = "Geen"
                if len(self.state.detected_tones) > 0:
                    top_tone = self.state.detected_tones[0]
                    if top_tone["audibility"] >= 4.0:
                        tonal_str = f"Toon {top_tone['freq']:.1f}Hz (Aud: {top_tone['audibility']:.1f}dB, Straf: {top_tone['penalty']:.1f}dB)"
                
                meteo_str = f"Wind {self.state.meteo_info.get('wind_speed_m_s', 0)}m/s {self.state.meteo_info.get('wind_direction', '')} ({'CONFORM RvS' if self.state.meteo_info.get('meteo_valid_rvs', True) else 'ONGELDIG'})"
                setup_str = f"H={self.state.setup_info.get('mic_height_m', 4.5)}m ({self.state.setup_info.get('mic_position', '')})"
                        
            # Write to CSV
            try:
                with open(self.state.log_filepath, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        timestamp,
                        f"{mic_dbz:.1f}",
                        f"{mic_dba:.1f}",
                        f"{l95_dbz:.1f}",
                        f"{l95_dba:.1f}",
                        f"{corr_dbz:.1f}",
                        f"{corr_dba:.1f}",
                        f"{mic_pf:.1f}",
                        f"{mic_pdb:.1f}",
                        f"{baro_dbz:.1f}",
                        f"{baro_pf:.1f}",
                        f"{baro_pdb:.1f}",
                        tonal_str,
                        meteo_str,
                        setup_str
                    ])
                self.state.log_status = f"Logged at {time.strftime('%H:%M:%S')}"
            except Exception as e:
                self.state.log_status = f"Error writing log: {e}"
                
        self.state.log_status = "Logging stopped"
