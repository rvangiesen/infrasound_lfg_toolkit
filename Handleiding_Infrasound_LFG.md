# Uitgebreide Verklarende Handleiding: Infrasound & Laagfrequent Geluid Meetstation
*STAB-Bestendige Contra-Expertise, Parameterverantwoording & Analyseprotocol voor Procedures bij de Raad van State (ABRvS)*

Deze handleiding is de uitbreidende gids voor het bedienen van de **Infrasound & LGF Meettoolkit**, het instellen van de parameters, het interpreteren van de 11 grafische analysecomponenten, en het opstellen van een juridisch onomstotelijk **STAB-bestendig contra-expertiserapport**.

---

## 🎯 Doel van deze Meettoolkit & Legal Protocol

Traditionele geluidsmetingen en rekenmodellen (zoals ingezet door de overheid en exploitanten) gebruiken vaak de **dB(A)** weging en jaargemiddelden (**Lden**). Dit verhult de twee grootste hinderfactoren van windturbines:
1. **Infrasound (3 - 20 Hz) en Laagfrequent Geluid (10 - 250 Hz):** Dit dringt moeiteloos door muren en dubbel glas heen en veroorzaakt resonantie/kamermodi in woningen.
2. **Modulatie en Tonaliteit:** Het periodieke 'zwiepende' of brommende geluid is veel hinderlijker dan constant achtergrondruis.

Om een succesvol tegenrapport in te dienen dat standhoudt bij de **Stichting Advisering Bestuursrechtspraak (STAB)** en de **Raad van State (ABRvS)**, moet het rapport voldoen aan de eisen uit de richtlijn *"Waar moet een succesvol tegenrapport aan voldoen"*.

---

## ⚖️ De 7 Pijlers van de STAB-Bestendige Meetmethode

Om door de STAB en de ABRvS geaccepteerd te worden als valide contra-expertise, volgt de toolkit exact de volgende 7 pijlers:

### 1. Borging Meteorologisch Venster (Meteo Validation)
* **Windsnelheid op zithoogte < 5.0 m/s:** Voorkomt dat windgeruis langs de microfoon vals geluid veroorzaakt.
* **Neerslagvrij:** Geen regen of hagel tijdens de meetperiode.
* **Controle:** De applicatie valideert automatisch dit meteovenster en geeft een groene indicatie **`✓ RvS CONFORM`**.

### 2. Microfoonopstelling & Windkap Afscherming
* **Microfoonhoogte:** Standaard op **4.5 meter** (verplicht voor de nachtperiode) of 1.5 meter (dag).
* **Afscherming:** Verplichte toepassing van een goedgekeurde **bolvormige windkap (90mm)** om microfoon-turbulentie te elimineren.
* **Posities:** Keuze uit vrijveldmeting (gevelvrij) of gevelmeting (waarbij 3 dB gevelreflectie wordt gecorrigeerd).

### 3. Traceerbare Veldkalibratie (Vóór & Ná)
* **Klasse 1 Pistonfoon:** Veldkalibratie wordt uitgevoerd vóór en na de meetreeks met een 94 dB / 114 dB kalibrator.
* **Certificering:** Serienummer en certificaatdatum van de kalibrator worden in de data-envelope vastgelegd.

### 4. Fysische Drukbelasting dB(Z) vs dB(A)
* De toolkit registreert ongewogen lineaire geluidsdruk **dB(Z)**.
* dB(A) trekt bij 20 Hz maar liefst 50 dB af van het geluidsniveau. dB(Z) toont de werkelijke fysische krachten die resonantie in de woning veroorzaken.

### 5. Achtergrondruis Substractie ($L_{95}$)
* Om turbinegeluid te scheiden van omgevingsruis berekent de toolkit continu het $L_{95}$-niveau (het achtergrondgeluidsniveau dat 95% van de tijd wordt overschreden).
* Conform de *Handleiding meten en rekenen industrielawaai 1999* past de engine de officiële substractieformule toe:
  $$L_{\text{corr}} = 10 \cdot \log_{10}\left(10^{L_{\text{totaal}}/10} - 10^{L_{\text{achtergrond}}/10}\right)$$

### 6. Smalbandige FFT Tonaliteitsanalyse (IEC 61400-11 / ISO 1996-2)
* De engine scant het spectrum (10 - 250 Hz) op tonale pieken en vergelijkt deze met het maskerend geluid in de kritieke band.
* Bij een hoorbaarheid $\Delta L_{ta} \ge 4.0\text{ dB}$ geldt een wettelijke toeslag (penalty) van **+1 tot +6 dB** op het tot geluid te rekenen niveau.

### 7. Gerichte Betwisting van het Overheidsrapport
* Het rapport richt zich haarscherp op de fouten in de overheidsrapportage, zoals:
  * Foutief geanticipeerde bodemabsorptiefactor ($B_f$).
  * Het verhullen van nachtelijke piekbelasting door $L_{den}$ jaargemiddelden.
  * Het negeren van tonale bromtonen.

---

## ⚙️ HOOFDSTUK 2: Diepgaande Verantwoording van alle Sidebar-Instellingen

In dit hoofdstuk wordt per instelling uitgelegd **waarom** u deze invoert, **wat** het algoritme ermee doet, **wat** het verwachte resultaat is, en **hoe** de akoestisch expert dit gebruikt bij de STAB en de Raad van State.

| Instelling / Parameter | 1. Waarom instellen? | 2. Wat doet de Engine hiermee? | 3. Wat is het Resultaat? | 4. Wat ziet de Expert? | 5. Gebruik bij Raad van State / STAB |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Windsnelheid op zithoogte (m/s)** | Voldoen aan ABRvS richtlijn; wind > 5 m/s veroorzaakt windgeruis op het microfoonmembraan. | Filtert/vlagt periodes met te hoge winddruk op zithoogte en kent de status `✅ RvS CONFORM` of `⚠️ WIND TE HOOG` toe. | Voorkomt dat turbulentie op het membraan wordt aangezien voor turbine-geluid. | Zekerheid dat gemeten infrasound pieken van de turbine komen en niet van lokaal gewaai. | Elimineert het primaire verweer van de tegenpartij dat metingen beïnvloed zijn door windruis. |
| **Windrichting (bijv. ZW / N)** | Vastleggen of de immissielocatie benedenwinds (downwind) van het windpark ligt. | Berekent of de geluidsuitbreiding optimaal richting de woning plaatsvindt conform ISO 9613-2. | Valideert dat de hoogste immissieconditie is gemeten. | Bevestiging van de maximale geluidsoverdracht tussen turbine en gevel. | Bewijst dat de meting is uitgevoerd onder representatieve maximale immissie-omstandigheden. |
| **Neerslagvrij (Vinkje)** | Regen/hagel veroorzaakt valse breedbandige piekbelasting op de sensor. | Controleert neerslagvrijheid en blokkeert ongeldige gegevens in de juridische export. | Garandeert schone spectrale data zonder regentikken. | Ruw spectrum zonder stoorpulsen van neerslag. | Voldoet aan de strikte eis van de Handleiding 1999 dat metingen neerslagvrij moeten zijn. |
| **Microfoonhoogte (4.5m / 1.5m)** | Nachtperiode vereist 4.5m hoogte om bodemafscherming te omzeilen; dagperiode 1.5m. | Past de correctiefactor voor microfoonhoogte toe op het gemeten spectrale niveau. | Gestandaardiseerd immissieniveau conform het Meetvoorschrift. | Vergelijking tussen dag- en nachtbelasting op de gevel. | Voorkomt dat de tegenpartij de meting ongeldig verklaart wegens verkeerde opstelhoogte. |
| **Gevelreflectie Aftrek (3.0 dB)** | Geluid dat op de gevel invalt reflecteert en verhoogt de gemeten waarde met 3 dB. | Trekt automatisch $3.0\text{ dB}$ af van het gemeten niveau bij opstelling direct op de gevel. | Vrijveld-equivalent geluidsdrukniveau ($L_{\text{vrijveld}}$). | Zuivere immissiewaarde zoals die in rekenmodellen gebruikt wordt. | Maakt de meting 1-op-1 vergelijkbaar met berekende immissiewaarden van het bevoegd gezag. |
| **Bolvormige Windkap (90mm)** | Vermindert lokaal windgeruis tot frequenties onder 10 Hz. | Bevestigt in de rapportage-envelope dat fysieke windafscherming aanwezig was. | Hoge signaal-ruisverhouding bij de microfoon. | Schoon laagfrequent spectrum (10 - 250 Hz). | Voldoet aan de IEC 61400-11 en ISO 1996-2 vereisten voor outdoor metingen. |
| **Veldkalibratie Vóór & Ná (94 dB)** | Aantonen van de kwantitatieve nauwkeurigheid van de signaalketen. | Berekent het verloop ($\Delta$) tussen pre- en post-kalibratie. Geaccepteerd indien $\Delta < 0.5\text{ dB}$. | Gegarandeerde amplitude-nauwkeurigheid van de meting. | Traceerbare veld-ijking ingebed in de rapportage. | Voldoet aan de Klasse-1 vereisten en maakt metingen juridisch onbetwistbaar. |
| **Binnenshuis Verblijfsruimte & Status Ramen/Deuren** | NEN-EN-ISO 16032 vereist gesloten deuren/ramen en uitgeschakelde interne bronnen. | Verwerkt ruimte-eigenschappen voor de binnen-toetsing aan de NSG-drempelcurve. | Zuiver binnenshuis immissieniveau zonder stoorbronnen (zoals cv of ventilatie). | Zichtbaarheid van kamermodi en staande golven veroorzaakt door het infrasound van buiten. | Onomstotelijk bewijs van binnenshuis hinder en slaapverstoring bij de Raad van State. |

---

## 📊 HOOFDSTUK 3: Uitgebreide Verklaring van de 11 Grafische Visualisaties

De rapportage-engine genereert **11 gespecialiseerde grafieken** (Grafiek 2.0 t/m 11.0). Hieronder staat de gedetailleerde toelichting per grafiek:

### Grafiek 2.0: Infrasound Frequentiespectrum (3 - 20 Hz) [dB(Z)]
* **Wat staat er in de grafiek?**
  * **Gemeten $L_{eq}$** (Donkerblauwe lijn): Het totale gemeten infrasounddrukniveau per frequentiebin.
  * **Achtergrondruis $L_{95}$** (Grijze dash-dot lijn): De omgevingsruisvloer.
  * **Vercammen Infrasound Drempel** (Rode gestreepte lijn): De bekende hinderdrempel voor infrasound.
  * **BPF Piek Marker** (Rode stip): De geïdentificeerde Bladpassagefrequentie (bijv. op $0.85\text{ Hz}$ of $1.7\text{ Hz}$).
* **Wat ziet de expert?** Direct de dominante infrasound pieken die samenvallen met het toerental van de windturbine.
* **Gebruik bij Raad van State:** Bewijst dat de onhoorbare luchtdrukpulsen ver boven de natuurlijke achtergrondruis uitsteken en direct veroorzaakt worden door de voorbijkomende wieken.

### Grafiek 3.0: Laagfrequent Spectrum (10 - 250 Hz) [dB(Z) & dB(A)]
* **Wat staat er in de grafiek?**
  * **Lineair dB(Z)** (Donkerblauw): De werkelijke fysische geluidsdruk.
  * **A-gewogen dB(A)** (Groen): Het door het menselijk oor waargenomen niveau.
  * **NSG LFG Drempelcurve** (Rode gestippelde curve met markers op de 1/3 octaafbanden 10 Hz t/m 80 Hz).
* **Wat ziet de expert?** Het enorme gat tussen dB(Z) en dB(A) in het laagfrequente gebied, en eventuele overschrijdingen van de NSG-hinderdrempel voor woningen.
* **Gebruik bij Raad van State:** Toont aan dat een bevoegd gezag dat alleen in dB(A) toetst, ernstige laagfrequente hinder binnenshuis (zoals brommen en trillingen) volledig verbergt.

### Grafiek 4.0: Smalbandige FFT Spectrum & Tonaliteitsanalyse (IEC 61400-11 / ISO 1996-2) [dB(Z)]
* **Wat staat er in de grafiek?** Hoge resolutie FFT-spectrum ($\Delta f = 0.1\text{ Hz}$) met de gedetecteerde tonale piek ($\Delta L_{ta}$) en het gemiddelde maskeringsniveau $L_{ta}$.
* **Wat ziet de expert?** Of er sprake is van een 'pure toon' (bijvoorbeeld veroorzaakt door de tandwielkast of generator van de turbine).
* **Gebruik bij Raad van State:** Bij $\Delta L_{ta} \ge 4.0\text{ dB}$ is wettelijk een straftoeslag van **+1 tot +6 dB** verplicht. Dit kan een schijnbare naleving doen omslaan in een overtreding.

### Grafiek 5.0: Infrasound Drukgolf Tijddomein (AC-Coupled Oscillogram)
* **Wat staat er in de grafiek?** De dynamische luchtdrukwisselingen (in Pascal AC) als functie van de tijd.
* **Wat ziet de expert?** Scherpe drukpulsen die zich exact om de $0.6 - 1.2$ seconden herhalen (overeenkomend met de wiekpassages langs de mast).
* **Gebruik bij Raad van State:** Biedt visueel "oscilloscope"-bewijs dat er sprake is van periodieke infrasound stoten die gebouwconstructies laten resoneren.

### Grafiek 6.0: Achtergrondruis Percentiel Spectrum ($L_{95}$) vs Gemeten Totaal ($L_{eq}$)
* **Wat staat er in de grafiek?** Vergelijking tussen de $L_{eq}$ (totaal geluid) en $L_{95}$ (ruisvloer zonder turbine-invloed).
* **Wat ziet de expert?** De signaal-ruisverhouding per frequentieband.
* **Gebruik bij Raad van State:** Bewijst dat de verhoogde geluidsdruk niet wordt veroorzaakt door algemeen omgevingsgeluid, maar door een specifieke puntbron.

### Grafiek 7.0: Gecorrigeerde Turbine-immissie $L_{\text{corr}}$ per Frequentieband
* **Wat staat er in de grafiek?** De netto turbine-immissie na logaritmische subtractie van de achtergrondruis:
  $$L_{\text{corr}} = 10 \cdot \log_{10}(10^{L_{eq}/10} - 10^{L_{95}/10})$$
* **Wat ziet de expert?** Het 'zuivere' geluidsspectrum dat uitsluitend aan de windturbine wordt toegeschreven.
* **Gebruik bij Raad van State:** Elimineert elke twijfel of de gemeten waarden door omgevingsruis zijn beïnvloed.

### Grafiek 8.0: Meteorologisch & Tijdsverloop Trendgrafiek
* **Wat staat er in de grafiek?** Geluidsdrukniveau dB(Z) en windsnelheid (m/s) synchroon uitgezet over de tijd.
* **Wat ziet de expert?** Of stijgingen in het geluidsniveau parallel lopen met het opstarten of optoeren van de turbine, terwijl de windsnelheid op zithoogte laag blijft.
* **Gebruik bij Raad van State:** Bewijst het causale verband tussen de werking van de turbine en de hinder bij de woning.

### Grafiek 9.0: InfraView Waterval Spectrogrammen (Matrix Dracal & Dayton)
* **Wat staat er in de grafiek?** 2D/3D watervalspectrogrammen van de Dracal (3 - 20 Hz) en Dayton (10 - 250 Hz) sensoren. Tijd staat op de Y-as, frequentie op de X-as, en kleurgradiënt geeft de geluidsintensiteit aan.
* **Wat ziet de expert?** Continue 'sporen' (verticale kleurlijnen) over de tijd die het aanhouden van specifieke bromtonen of infrasound-frequenties aantonen.
* **Gebruik bij Raad van State:** Visualiseert de continuïteit en duur van de hinderperiode; laat zien dat het geen incidentele piek was maar een aanhoudend fenomeen.

### Grafiek 10.0: Breedspectrum Ware Hinder & Energetische Subtractie (3 - 2000 Hz) [dB(Z)]
* **Wat staat er in de grafiek?** Breedspectrum overzicht ($3\text{ Hz} - 2000\text{ Hz}$) bevattende:
  1. Gemeten Totaal $L_{eq}$ (blauw gestippeld)
  2. Achtergrondruis $L_{95}$ (grijs gestreept)
  3. Windturbine Bron-Garantie Referentie (cyaan gestreept)
  4. **RESULTANTE WARE HINDER ($L_{\text{corr}}$)**: **OPVALLENDE DIKKE RODE LIJN** met rood gearceerd immissievlak.
* **Wat ziet de expert?** Het absolute overzichtsbeeld van de netto turbine-immissie ten opzichte van de referentiecurve over het volledige relevante bereik.
* **Gebruik bij Raad van State:** HET centrale bewijsstuk in contra-expertise verslagen om de Raad van State in één oogopslag de werkelijke nettobelasting te tonen.

### Grafiek 11.0: Breedspectrum Spectrum met Verticale Scheiding (3 - 2000 Hz) [dB(Z) ➔ dB(A)]
* **Wat staat er in de grafiek?** Breedspectrum met een **verticale gestreepte scheidingslijn op 20 Hz**:
  * **Linkerkant (3 - 20 Hz)**: Infrasound zone in **dB(Z)** (Lineair / Onhoorbaar).
  * **Rechterkant (20 - 2000 Hz)**: Hoorbaar & LFG spectrum in **dB(A)** (A-gewogen).
  * **Rode Resultante Lcorr Lijn**: Loopt over het hele spectrum door in de respectievelijke eenheden.
* **Wat ziet de expert?** Hoe de fysische energie in het infrasoundbereik (dBZ) aansluit op het gehoormatige bereik (dBA).
* **Gebruik bij Raad van State:** Maakt voor rechters en deskundigen direct inzichtelijk waarom de dB(A)-norm tekortschiet bij infrasound, en toont de continuïteit van de energieband.

---

## 📄 HOOFDSTUK 4: Rapporteringsstructuur & Certificering

De applicatie exporteert rapporten in **HTML** (live preview) en **Word (`.docx`)**:

1. **⚖️ STAB Contra-Expertise Rapport**: Bevat de juridische verantwoording en de 7 pijlers. **Grafieken 2.0 t/m 11.0** zijn per 2 grafieken per pagina ingedeeld in **Bijlage A**.
2. **🏠 Binnenshuis Meetrapport (NSG & ISO 16032)**: Bevat **Grafiek 2.0, 3.0 en 4.0** direct in het hoofddeel (Sectie 2 & 3) voor directe toetsing binnenshuis, evenals de volledige bijlage.
3. **🌳 Buitenshuis Gevel Meetrapport**: Vrijveld- en gevelmetingen met windkapborging en reflectie-aftrek.
4. **🎯 Referentiemeting Windturbine Rapport**: Bronreferentie conform IEC 61400-11.

---

## 🛠️ HOOFDSTUK 5: Traceerbare Signaalketen & Kalibratiematrix

| Parameter / Component | Infrasound (Dracal Barometer) | Laagfrequent & Hoorbaar (Dayton Mic) |
| :--- | :--- | :--- |
| **Frequentiebereik** | 0.1 Hz - 20.0 Hz | 10 Hz - 20,000 Hz |
| **Kalibratiemethode** | AC-drukkoppeling + Helling-compensatie | Individueel `.cal` bestand + Pistonfoon 94dB |
| **FFT Venster** | Hann Window (75% overlap, N=8192) | Hann Window (75% overlap, N=8192) |
| **Bordings-norm** | ISO 1996-2 / IEC 61400-11 | NEN-EN-ISO 16032 / DIN 45680 / NSG |
| **Traceerbaarheid** | Gekalibreerde drukcel met driftcheck | ISO 17025 gecertificeerde Klasse 1 Pistonfoon |

---

## ⚖️ HOOFDSTUK 6: Strategische gids voor discussies bij de Raad van State

Met dit contra-expertiserapport weerlegt u de 3 meest voorkomende verweren van exploitanten:

### Argument 1: *"De berekende jaargemiddelde Lden-waarde blijft binnen de norm."*
* **Uw weerwoord:** "Jaargemiddelden verhullen nachtelijke piekhinder. Onze metingen tonen aan dat gedurende specifieke uren de gecorrigeerde fysische drukbelasting $L_{\text{corr}}$ in dB(Z) met ruim 20 dB stijgt. Handhaving dient plaats te vinden op de hinderpieken."

### Argument 2: *"Er is geen sprake van tonaliteit."*
* **Uw weerwoord:** "De smalbandige FFT-analyse conform IEC 61400-11 (zie Grafiek 4.0) toont op frequentie X Hz een hoorbaarheid $\Delta L_{ta} \ge 4.0\text{ dB}$ aan. Dit kwalificeert als een prominente toon waarop wettelijk +6 dB toeslag moet worden toegepast."

### Argument 3: *"De meting is beïnvloed door omgevingswind."*
* **Uw weerwoord:** "De meetdata (zie Grafiek 8.0) bewijst dat de windsnelheid op zithoogte gedurende de gehele meetperiode onder de 5.0 m/s bleef, de microfoon op 4.5m hoogte was uitgerust met een bolvormige windkap, en het $L_{95}$-achtergrondniveau is afgetrokken."
