# 🔊 Infrasound & Low-Frequency Noise (LGF) Meetstation

Geavanceerde dual-channel realtime analyse-applicatie voor **Infrageluid (3 - 20 Hz)** en **Laagfrequent Geluid (10 - 250 Hz)** met ondersteuning voor de **Dayton iMM-6C USB/Analoge Microfoon** en de **Dracal USB-BAR20/30 Microbarometer**.

Conform de richtlijnen voor geluidsbeoordeling (**IEC 61400-11** tonale toeslagberekening en Deense/VNS-infrasoundnormen).

---

## 🚀 Laptop Quickstart (100% Automatisch Overneembaar)

Wanneer u dit project op een laptop heeft gekloond via AntiGravity of Git, kunt u de gehele omgeving met 1 klik installeren en starten:

### Optie 1: 1-Klik Startbestand (Aanbevolen)
Dubbelklik op:
```cmd
start_app.bat
```
Dit script voert automatisch het volgende uit:
1. Controleert en installeert alle vereiste Python bibliotheken (`requirements.txt`).
2. Detecteert of Dracal sensordrivers/software aanwezig zijn.
3. Start de Streamlit Web-GUI op `http://localhost:8501`.

### Optie 2: Handmatig via Terminal
```powershell
pip install -r requirements.txt
python setup_laptop.py
python -m streamlit run app.py
```

---

## 🔍 InfraView Integratie & 3D Waterfall Analyzer

Het meetstation bevat een **100% geïntegreerd InfraView systeem**:

1. **In-App 3D Waterfall Spectrogram (`InfraView Inspector`)**:
   - Visualiseert live & historische spectra over de tijd assen (Tijd x Frequentie x dBZ).
   - Ondersteunt 2D Heatmaps & 3D Surface waterval-weergaves met aanpasbare kleurenschema's (Viridis, Plasma, Inferno, Thermal).
2. **1-Klik External InfraView / DracalView Launcher**:
   - In de zijbalk en de InfraView-tab bevindt zich een directe knop: **`🚀 Start External InfraView / DracalView`**.
   - Indien software ontbreekt, kunt u met **`📦 Installeer Dracal & InfraView Tools`** direct het meegeleverde installatieprogramma `DracalUtilities-3.7.0.exe` starten.

---

## 🛠️ Sensoren & Hardware Ondersteuning

| Sensor | Signaaltype | Frequentiebereik | Aansluiting / Driver |
| :--- | :--- | :--- | :--- |
| **Dracal USB-BAR20/30** | Atmosferische Micro-luchtdruk | **3 - 20 Hz** | Direct via `dracal-usb-get.exe` (USB CLI) of Virtuele COM-poort (VCP). |
| **Dayton iMM-6C** | Akoestische Geluidsdruk | **10 - 250 Hz (tot 20 kHz)** | PC Geluidskaart Input / USB Audio. Ondersteunt `.cal` kalibratiebestanden. |

---

## 🎯 Belangrijkste Functionaliteiten

- **Realtime FFT & Spectrogrammen**: Dual-channel spectraalanalyse met piekdetectie voor zowel infrageluid als hoorbaar/laagfrequent geluid.
- **IEC 61400-11 Tonaliteitsanalyse**: Automatische detectie van prominente tonale pieken en berekening van de straffactor (penalty up to 6 dB).
- **Oscilloscope Tijddomein Weergave**: Scheiding van ruwe atmosferische druk (incl. DC drift) en gefilterde infrasound luchtdrukgolven (>0.5 Hz high-pass).
- **Automated CSV Datalogger**: Exporteert automatisch minuutwaarden en verloopgrafieken naar `.csv`.

---

## 📄 Licentie & Documentatie
Zie de meegeleverde `Handleiding_Infrasound_LFG.md` voor de volledige gebruikershandleiding en hardware-kalibratie instructies.
