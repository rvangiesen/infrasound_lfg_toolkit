# Verklarende Handleiding: Infrasound & Laagfrequent Geluid Meettoolkit
*Bestemd voor omwonenden van windturbines ten behoeve van bewijsvoering en handhaving*

Deze handleiding legt uit hoe u de meettoolkit configureert, hoe u de grafieken en tabellen interpreteert, en hoe u de verzamelde data kunt inzetten in discussies met exploitanten, omgevingsdiensten en akoestische meetinstituten.

---

## 🎯 Doel van deze Meettoolkit
Traditionele geluidsmetingen (zoals uitgevoerd door officiële instanties in opdracht van exploitanten) meten vaak in **dB(A)** en middelen het geluid over langere periodes (bijvoorbeeld Lden: *Level Day-Evening-Night*). Dit verhult de twee grootste hinderfactoren van windturbines:
1.  **Infrasound (IS, < 20 Hz) en Laagfrequent Geluid (LFG, 10 - 100 Hz):** Dit dringt moeiteloos door muren en dubbel glas heen en veroorzaakt resonantie in woningen (lichamelijk voelbaar als trillingen of druk op de oren).
2.  **Modulatie en Tonaliteit:** Het periodieke 'zwiepende' of brommende geluid (veroorzaakt door de bladen die langs de mast passeren of door de tandwielkast/generator) is veel hinderlijker dan constant achtergrondruis.

Deze toolkit meet **smalbandig** (frequentie voor frequentie) en maakt gebruik van de lineaire **dB(Z)** weging om de werkelijke drukbelasting in kaart te brengen, inclusief een automatische tonaliteitsdetectie volgens de internationale norm **IEC 61400-11**.

---

## 1. De Linkerkolom: Instellingen & Configuratie

De sidebar aan de linkerkant regelt hoe de sensoren worden uitgelezen en gekalibreerd.

| Instelling | Betekenis & Uitleg | Richtlijn voor Windturbinemetingen |
| :--- | :--- | :--- |
| **▶️ Start Meting / ⏹️ Stop Meting** | Hiermee start of stopt u de actieve data-acquisitie en logging. | Gebruik dit om gerichte metingen te starten tijdens hinderperiodes (bijvoorbeeld 's nachts bij specifieke windrichtingen). |
| **Simulatiemodus (Mock)** | Indien ingeschakeld, genereert de software realistische testdata. Handig om de werking van de interface te begrijpen zonder dat er sensoren zijn aangesloten. | **Uitschakelen** voor daadwerkelijke metingen. |
| **Geluidskaart Input** | Selecteert de audio-ingang waar uw **Dayton iMM-6C** microfoon op is aangesloten (meestal de microfoon/lijningang of een USB-C audio-adapter). | Selecteer de ingang die hoort bij de aangesloten Dayton microfoon. |
| **Microfoon Gevoeligheid (dBFS op 94dB)** | De Dayton microfoon levert een analoog signaal aan de geluidskaart. Deze waarde kalibreert de relatie tussen het digitale signaal (dBFS) en de werkelijke geluidsdruk. 94 dB komt exact overeen met een druk van 1 Pascal (Pa). | De standaardwaarde van `-18.5 dBFS` is een representatieve fabriekskalibratie voor de Dayton iMM-6. Indien u een specifiek kalibratie-apparaat (pistonfoon) heeft gebruikt, vult u de hieruit verkregen waarde in. |
| **Kalibratiemethode (Dayton)** | **Vlakke Respons:** Geen correctie.<br>**Bestand Selecteren:** Upload het `.cal`-bestand dat u bij de Dayton microfoon heeft gedownload.<br>**Pad opgeven:** Direct pad naar het bestand op uw pc. | **Bestand Selecteren** of **Pad opgeven**. De iMM-6C heeft een individueel kalibratiebestand nodig om metingen onder de 50 Hz exact te corrigeren. Dit is cruciaal voor laagfrequent geluid (10 - 50 Hz). |
| **Verbindingsmethode (Dracal)** | **usb:** De app roept de Dracal command-line tool `dracal-usb-get.exe` aan.<br>**vcp:** De app leest de barometer uit als een virtuele COM-poort (Virtual COM Port). | Kies **usb** als u de standaard Dracal software heeft geïnstalleerd. Vul het juiste pad in (meestal `C:\Program Files\Dracal\Cmd\dracal-usb-get.exe`). |
| **Meetsnelheid Barometer (Hz)** | Het aantal drukmetingen per seconde dat de barometer uitvoert. | Stel in op **50 Hz** of **100 Hz** voor voldoende resolutie in het infrasoundgebied (tot 20 Hz). |
| **Dracal Uitleeskanaal** | Bepaalt welk sensor-kanaal wordt uitgelezen. | Standaard **0** (dit is het kanaal voor de absolute luchtdruk). |
| **Map voor CSV logs** | De map op uw computer waar de metingen automatisch worden opgeslagen als CSV-bestanden. | Kies een makkelijk vindbare map, bijvoorbeeld `./logs` of uw documentenmap. |
| **Log Interval (seconden)** | Bepaalt hoe vaak er een regel met samengevatte meetwaarden (gemiddelde niveaus, piekfrequenties, actieve tonen) naar het logbestand wordt geschreven. | Stel in op **60 seconden** (1 minuut) of **10 seconden** voor gedetailleerde handhavingsrapportages. |

---

## 2. Wat kunt u waarnemen in de Grafieken?

Het dashboard is verdeeld over vier tabbladen:

### Tab 1: Live Spectrogrammen
Dit tabblad toont de verdeling van de geluidsenergie over de verschillende frequenties.

#### A. Infrasound Frequentiespectrum (3 - 20 Hz) — *Dracal Barometer*
*   **Wat u ziet:** Een rode lijn die het geluidsdrukniveau in **dB(Z)** (lineaire schaal) toont voor de diepste tonen die de mens niet kan horen, maar het lichaam wel kan registreren.
*   **Turbine-specifiek gedrag:** 
    *   Windturbines veroorzaken periodieke drukgolven telkens wanneer een blad de mast passeert. Dit heet de **Bladpassagefrequentie (BPF)**.
    *   Voor een 3-bladige turbine die draait op 15 RPM (omwentelingen per minuut) is de BPF: $\frac{15 \text{ RPM} \times 3 \text{ bladen}}{60 \text{ seconden}} = 0.75 \text{ Hz}$.
    *   U zult in de grafiek vaak een duidelijke piek zien rond de BPF (bijvoorbeeld 0.8 Hz) en de bijbehorende harmonischen (bijvoorbeeld 1.6 Hz, 2.4 Hz, 3.2 Hz, etc.).
    *   Een gele ster markeert automatisch de hoogste piek in dit infrasoundgebied.

#### B. Laagfrequent Frequentiespectrum (10 - 250 Hz) — *Dayton Microfoon*
*   **Wat u ziet:** Twee lijnen: een blauwe lijn (**dB(Z) - Lineair**) en een gestreepte oranje lijn (**dB(A) - A-gewogen**).
*   **Waarom dit belangrijk is:**
    *   De **dB(A)** weging dempt lage frequenties zeer sterk omdat het menselijk gehoor hier minder gevoelig voor is. Bij 20 Hz trekt dB(A) er bijvoorbeeld maar liefst **50 dB** vanaf!
    *   Als een windturbine een zware bromtoon produceert op 40 Hz met een sterkte van **60 dB(Z)** (fysische druk), rapporteert de officiële dB(A)-meter slechts circa **35 dB(A)**. Dit wordt door handhavers vaak weggezet als "binnen de norm", terwijl de bewoner de bromtoon binnenshuis duidelijk hoort en voelt trillen.
    *   **Het bewijs:** Het verschil tussen de blauwe lijn (dBZ) en de oranje lijn (dBA) laat direct zien hoeveel laagfrequente energie aanwezig is die door de officiële A-weging wordt genegeerd.

---

### Tab 2: Drukgolven (Tijddomein)
Dit tabblad functioneert als een oscilloscoop en toont de drukgolven zoals ze door de ruimte reizen.

#### 1. Ruwe Druk (Atmosfeer + Dynamiek)
*   **Wat u ziet:** De absolute luchtdruk in Pascal (bijvoorbeeld rond de 101300 Pa). Deze grafiek golft langzaam op en neer door windvlagen en atmosferische schommelingen.

#### 2. Gefilterde Infrasoundgolf (>0.5 Hz High-pass)
*   **Wat u ziet:** De wisselspanning (AC-component) van de druk nadat de trage windschommelingen en de statische luchtdruk zijn weggefilterd. Hier blijft alleen de pure akoestische infrasoundgolf over.
*   **Turbine-specifiek gedrag:**
    *   Bij hinder van een windturbine ziet u hier vaak een repeterend pulserend patroon. Elke "piek" of "dal" in de golfbeweging vertegenwoordigt een turbineblad dat de mast passeert en een drukgolf richting uw woning duwt.
    *   Als dit patroon zeer regelmatig is (bijvoorbeeld exact elke 1.2 seconden een puls), is dit het onomstotelijke fysieke bewijs van turbine-invloed, aangezien natuurlijke windturbulentie grillig en niet-periodiek is.

---

### Tab 3: Tonaliteit (IEC 61400-11)
Dit tabblad voert de officiële tonaliteitsanalyse uit op de microfoondata.

*   **Wat is Tonaliteit?** Geluid van windturbines is extra hinderlijk als er een duidelijke 'brom' of 'piep' in zit (een tonale component, zoals het janken van een tandwielkast). 
*   **Hoe werkt de tabel?**
    *   Het algoritme zoekt naar pieken in het spectrum en vergelijkt het niveau van de piek met het omringende achtergrondgeluid binnen de zogenaamde **kritieke bandbreedte** (het frequentiegebied dat het menselijk oor als één geheel filtert).
    *   **Hoorbaarheid ($\Delta L_{ta}$):** Dit is het verschil tussen de toon en het maskerende achtergrondgeluid.
    *   **Straffactor (Penalty):** Volgens de norm krijgt een geluidsbron een 'straf' (penalty) als er een prominente toon aanwezig is.
        *   Als $\Delta L_{ta} \ge 4 \text{ dB}$, is de toon prominent (er verschijnt een gele/oranje waarschuwing in het dashboard). Er geldt dan een toeslag (penalty) tussen de 1 en 6 dB.
        *   Als $\Delta L_{ta} \ge 10 \text{ dB}$, is de toon zeer luid en krijgt de turbine de maximale straftoeslag van **6 dB** op de totale geluidsbelasting.
*   **Toepassing voor handhaving:** Akoestische rapporten van exploitanten beweren vrijwel altijd dat er "geen sprake is van tonaliteit". Met deze tabel kunt u aantonen dat er op specifieke momenten (bijvoorbeeld bij bepaalde windsnelheden of lagere achtergrondgeluiden 's nachts) wel degelijk sprake is van prominente tonen, wat juridisch gezien betekent dat er 6 dB bij de gemeten geluidswaarde opgeteld moet worden!

---

### Tab 4: Historie & Logs
Dit tabblad toont de langetermijntrend van uw metingen.

*   **Tabel met laatste metingen:** Hier ziet u de exacte waarden die elke minuut (of ingesteld interval) zijn opgeslagen.
*   **Verloopgrafiek:** Toont het verloop van het Infrasoundniveau (dBZ) en Laagfrequent/Hoorbaar geluid over de tijd. Hiermee kunt u trends aantonen (bijvoorbeeld: het geluid stijgt fors zodra de windkracht toeneemt of wanneer de turbine inschakelt).
*   **📥 Download Huidige Meting (CSV):** Hiermee exporteert u de gehele meetreeks naar een Excel-compatibel CSV-bestand.

---

## 3. Strategische gids voor discussies met Akoestische Meetbureaus
Als omwonende staat u vaak 1-0 achter tegenover professionele meetbureaus die door de exploitant worden ingehuurd. Zij gebruiken vaak de volgende argumenten, die u met deze toolkit kunt weerleggen:

### Argument 1: *"De metingen voldoen aan de dBA-jaargemiddelde normen."*
*   **Uw weerwoord:** "Een jaargemiddelde verhult de hinder op specifieke momenten. Onze data toont aan dat gedurende specifieke uren (bijvoorbeeld tussen 23:00 en 05:00 uur bij oostenwind) de laagfrequente drukbelasting in dB(Z) met meer dan 20 dB stijgt ten opzichte van het normale achtergrondniveau. Handhaving dient plaats te vinden op de piekmomenten van de hinder, niet op een jaargemiddelde."

### Argument 2: *"Er is geen tonaliteit (bromtoon) aanwezig."*
*   **Uw weerwoord:** "Onze smalbandige FFT-analyse volgens de IEC 61400-11 richtlijn toont op [Datum/Tijd] een duidelijke toon aan op [Frequentie, bijv. 120 Hz] met een hoorbaarheid ($\Delta L_{ta}$) van [bijv. 6.5 dB]. Dit kwalificeert volgens de norm als een prominente toon, waardoor er een straftoeslag van [bijv. 4 dB] op de geluidsbelasting moet worden toegepast. Wij eisen dat uw metingen ook smalbandig worden geanalyseerd op deze specifieke hinderfrequentie."

### Argument 3: *"De windturbine draaide tijdens onze controlemeting conform de voorschriften."*
*   **Uw weerwoord:** "Akoestische meetbureaus testen windturbines bij voorkeur tijdens 'vollast' overdag om een stabiel beeld te krijgen. De meeste hinder voor omwonenden treedt echter op bij stabiele nachtelijke atmosferische omstandigheden (waarbij de windsnelheid op ashoogte hoog is, maar het windgeruis op de grond laag is). Vergelijk uw logbestanden (CSV) met de openbare windgegevens (KNMI) en de operationele data van de turbine (indien opvraagbaar) om aan te tonen dat de hinder optreedt onder specifieke atmosferische condities die door het meetbureau niet zijn onderzocht."

---

## 4. Laptop Setup & InfraView Waterfall Systeem

### A. 100% Automatische Laptop Overname
Indien u dit project overneemt op uw laptop via AntiGravity of Git:
1. Dubbelklik in de projectmap op `start_app.bat`.
2. Het systeem installeert automatisch alle vereiste Python bibliotheken en start de applicatie op uw laptop.
3. U kunt ook via de GUI in de zijbalk onder **`🛠️ Laptop Setup & System Check`** op **`⚡ Run Full Laptop Setup Script`** klikken.

### B. InfraView Spectrogram & External Launcher
In het tabblad **`🔍 InfraView Inspector & Waterfall`**:
- **3D & 2D Waterval:** Bekijk de temporele ontwikkeling van frequenties en geluidsdrukniveaus.
- **1-Klik External Software Launch:** Met de knop **`🚀 Open External InfraView`** opent u direct de losse DracalView/InfraView software.
- **Automatische Software Installatie:** Indien de Dracal software nog niet geïnstalleerd is op de laptop, gebruikt u de knop **`📦 Installeer InfraView Software`** om `DracalUtilities-3.7.0.exe` direct uit te voeren.
