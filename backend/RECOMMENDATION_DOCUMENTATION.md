# AgriSense-AI: Smart Farming Recommendation System (Phase 7)
## Agronomic Rules, Evidence Base, Weather Integration & Technical Documentation

---

### 1. Architectural Overview & System Classification

AgriSense-AI provides two distinct, non-conflated intelligence services:
1. **Machine Learning Pipeline (Phases 3–5):** Continuous statistical regression using Scikit-Learn Random Forest (`RandomForestRegressor`) estimating harvest paddy yield in tonnes per hectare from historical agro-climatic distributions.
2. **Agronomic Expert Rule Engine (Phase 7):** Deterministic, explainable, stage-aware rule system grounded in verified agricultural practices published by the **Tamil Nadu Agricultural University (TNAU)**.

To maintain scientific integrity and prevent hallucinated farming advice:
- Recommendations are tagged with `"rule_type": "agronomic_expert_system"`.
- Fertilizer doses, soil amendments, and water levels adhere strictly to the TNAU Crop Production Guide (Paddy).
- The system includes a mandatory disclaimer that recommendations do not guarantee yield increases and must be corroborated by local Krishi Vigyan Kendra (KVK) advisors.

---

### 2. Authoritative Agronomic Sources

All implemented thresholds, nutrient splits, and chemical/bio-control measures are derived from:
1. **Tamil Nadu Agricultural University (TNAU)**: *Crop Production Guide — Agriculture (Paddy)*, Department of Agriculture, Government of Tamil Nadu.
2. **TNAU Agritech Portal**: *Water Management (AWD)*, *Nutrient Management*, and *Crop Protection (Paddy)*.
3. **National Rice Research Institute (ICAR-NRRI)**: Guidelines for Alternate Wetting and Drying (AWD) and Integrated Pest Management (IPM).

---

### 3. Detailed Agronomic Rules & Decision Tables

#### A. Irrigation Management & Water Conservation
| Stage | Soil Moisture (%) | Environmental Condition | Recommended Action | Urgency | Rationale (TNAU) |
|---|---|---|---|---|---|
| **Vegetative Tillering** | $> 80\%$ | Any | Withhold irrigation; let water recede 15 cm below surface | `ROUTINE` | Safe Alternate Wetting & Drying (AWD) improves root aeration and tillering vigor. |
| **Vegetative Tillering** | $60\% - 80\%$ | No storm forecast | Monitor perforated field water tube (pani pipe) | `ROUTINE` | Moisture is within safe AWD range; prevents over-pumping. |
| **Vegetative Tillering** | $< 60\%$ | Rain $< 20$ mm | Re-irrigate field to 5 cm depth | `ADVISORY` | Field approaches lower AWD threshold; cyclic wetting required. |
| **Vegetative Tillering** | $< 60\%$ | Rain forecast $\ge 20$ mm / prob $\ge 70\%$ | **Postpone irrigation 24–48h; clear drainage channels** | `WARNING` | **Conflict Resolution**: Avoids waterlogging and wasting canal/groundwater before heavy rainfall. |
| **Panicle Initiation & Flowering** | $< 70\%$ | Any | **Irrigate immediately to maintain 2.5–5.0 cm continuous standing water** | `CRITICAL` | Flowering is the most moisture-critical window. Stress causes pollen abortion and empty spikelets. AWD is strictly forbidden during flowering. |
| **Panicle Initiation & Flowering** | $\ge 70\%$ | Any | Maintain 2.5 cm standing water layer | `ROUTINE` | Continuous water layer suppresses spikelet sterility. |
| **Grain Filling & Maturity** | Any | Approaching harvest | Terminal drainage 10–15 days before harvest | `ADVISORY` | Hardens soil for combine harvesters, synchronizes ripening, and prevents grain mold. |
| **Nursery** | Any | Seedbed phase | Maintain shallow 1–2 cm standing water | `ROUTINE` | Prevents desiccation while ensuring seedling leaf emergence. |

---

#### B. Fertilizer Scheduling & Nutrient Balance
Baseline N-P-K benchmarks (TNAU Crop Production Guide):
- **Kuruvai (Short duration 105–120 days):** 120 : 40 : 40 kg N : P₂O₅ : K₂O per ha
- **Samba / Thaladi (Medium/Long duration 135–160 days):** 150 : 50 : 50 kg N : P₂O₅ : K₂O per ha
- **Navarai (Summer dry season):** 120 : 40 : 40 kg N : P₂O₅ : K₂O per ha

| Stage | Trigger Condition | Recommended Action | Urgency | Warning / Limitation |
|---|---|---|---|---|
| **Tillering (20–25 DAT)** | Balanced soil N ($90–180$ kg/ha) | Apply second split: 50% seasonal N (~60–75 kg N/ha, approx. 130–160 kg Urea/ha) | `ROUTINE` | Apply with thin water layer after hand weeding. |
| **Tillering (20–25 DAT)** | Soil N deficient ($< 90$ kg/ha) | Increase tillering split by +15 kg N/ha + apply 25 kg ZnSO₄/ha | `ADVISORY` | Zinc deficiency causes 'Khaira' rust-brown spotting in calcareous delta soils. |
| **Tillering (20–25 DAT)** | Soil N excessive ($> 180$ kg/ha) | Reduce tillering split to max 15–20 kg N; withhold excess urea | `WARNING` | Excess vegetative growth promotes plant lodging and triggers blast/BPH outbreaks. |
| **Tillering / Panicle** | **Heavy rain forecast ($\ge 15$ mm or prob $\ge 65\%$)** | **Postpone chemical urea top-dressing for 48 hours** | `WARNING` | **Conflict Resolution**: Soluble urea dissolves and leaches into waterways, causing fertilizer loss and groundwater contamination. |
| **Panicle Initiation (40–45 DAT)** | Normal conditions | Apply third split: 25% N (~30–38 kg N/ha) + 50% K₂O (~25 kg MOP/ha) | `ADVISORY` | Potassium at panicle initiation strengthens culms, reduces lodging, and increases grain filling weight. |
| **Flowering / Heading** | Any | **Do not apply soil urea or chemical fertilizers** | `ROUTINE` | Heading-stage soil nitrogen triggers vegetative resurgence and attracts gundhi bugs. If leaf chlorosis occurs, apply 1% foliar urea spray. |
| **Any Stage** | Soil P $< 25$ kg/ha | Incorporate 50 kg/ha SSP + 2 kg/ha Phosphobacteria biofertilizer | `ADVISORY` | Fixation occurs in acidic or sodic soils; biofertilizers solubilize bound phosphates. |

---

#### C. Soil Health & Chemical Amendments
| Soil Indicator | Range | Recommended Amendment | Urgency | Rationale |
|---|---|---|---|---|
| **Acidic Reaction** | $\text{pH} < 6.0$ | Apply Agricultural Lime ($\text{CaCO}_3$) @ 500 kg/ha or Dolomite during ploughing | `WARNING` | Corrects aluminum/iron toxicity; prevents phosphorus fixation. Must be incorporated 2 weeks before chemical fertilizers. |
| **Optimal Reaction** | $6.0 \le \text{pH} \le 7.8$ | Incorporate green manure (*Sesbania aculeata* / Daincha) @ 6.25 t/ha or FYM @ 12.5 t/ha | `ROUTINE` | Maintains microbial soil health and cation exchange capacity. |
| **Alkaline / Sodic** | $\text{pH} > 8.0$ | Apply Agricultural Gypsum ($\text{CaSO}_4 \cdot 2\text{H}_2\text{O}$) @ 500–1000 kg/ha followed by flooding and leaching | `WARNING` | Replaces exchangeable sodium ions on clay colloids with calcium, improving soil porosity. |
| **Coastal Saline** | Coastal districts (*Nagapattinam, Cuddalore*) | Maintain continuous shallow water layer (2 cm); apply FYM | `ADVISORY` | Suppresses capillary rise of subsoil saline water tables during sunny intervals. |

---

#### D. Pest & Disease Surveillance (Integrated Pest Management)
| Pest / Disease | Microclimate & Farm Triggers | Action & Management (TNAU IPM) | Urgency |
|---|---|---|---|
| **Rice Blast** (*Pyricularia oryzae*) | Relative humidity $\ge 85\%$, Temp $\le 29^\circ\text{C}$, Nitrogen $\ge 145$ kg/ha | Foliar spray *Pseudomonas fluorescens* (0.2%) @ 2.5 kg/ha or Tricyclazole 75% WP @ 500 g/ha. Withhold urea application. | `WARNING` |
| **Brown Planthopper (BPH)** (*Nilaparvata lugens*) | Nitrogen $\ge 160$ kg/ha, Humidity $\ge 80\%$, tillering/panicle stage | Intermittent field draining (3 days dry tiller bases); spray Neem Oil (3%) @ 15 L/ha; cut 30 cm alleyways every 2.5 meters. | `WARNING` |
| **Yellow Stem Borer** (*Scirpophaga incertulas*) | Vegetative tillering or panicle stage | Install sex pheromone traps @ 12/ha; release egg parasitoid *Trichogramma japonicum* @ 100,000/ha. | `ROUTINE` |

---

### 4. Conflict Resolution Rules

Conflicting conditions frequently occur in tropical monsoon agriculture:
1. **Moisture Deficit vs. Imminent Precipitation:**
   - *Conflict:* Soil moisture $< 60\%$ (irrigation normally advised), but 48-hour forecast predicts $\ge 20$ mm rain or $\ge 70\%$ rain probability.
   - *Resolution:* Engine blocks the irrigation trigger, logs a conflict notice, and emits a `WARNING` advisory advising the farmer to postpone tube well pumping and clear drainage gates to harvest upcoming rainwater.
2. **Scheduled Chemical Top-Dressing vs. Heavy Downpour:**
   - *Conflict:* Crop phenology indicates tillering/panicle split, but 48-hour rainfall forecast is $\ge 15$ mm.
   - *Resolution:* Engine suppresses chemical fertilizer application, adds an advisory warning that top-dressing urea before downpours causes extensive nitrogen leaching and runoff, and schedules application 48 hours post-storm.

---

### 5. Weather Integration & Handling Missing Data

- **Live Integration:** When environmental indicators (`temperature_c`, `humidity_pct`, `forecast_rain_expected_mm`, `forecast_rain_prob_pct`) are omitted from client requests, the endpoint automatically resolves the farm's district coordinates against the Open-Meteo API.
- **Fail-Safe Fallbacks:** If external weather APIs are unreachable, time out, or network connections fail:
  - The engine does **not** crash or guess arbitrary weather metrics.
  - Soil and crop stage rules execute deterministically.
  - The response transparently logs exact limitations in `data_limitations` (e.g., `"Live weather lookup was unavailable; recommendations generated using available soil and stage metrics."`).

---

### 6. API Interface

#### Endpoint: `POST /recommendations` (also available via `POST /api/v1/recommendations/`)

##### Sample Request Body:
```json
{
  "district": "Thanjavur",
  "season": "Samba",
  "growth_stage": "vegetative_tillering",
  "soil_type": "Alluvial",
  "soil_ph": 5.4,
  "soil_moisture_pct": 52.0,
  "nitrogen_kg_ha": 175.0,
  "phosphorus_kg_ha": 18.0,
  "potassium_kg_ha": 45.0,
  "temperature_c": 28.0,
  "humidity_pct": 88.0,
  "forecast_rain_expected_mm": 35.0,
  "forecast_rain_prob_pct": 80
}
```

##### Sample Response Body:
```json
{
  "rule_type": "agronomic_expert_system",
  "district": "Thanjavur",
  "season": "Samba",
  "growth_stage": "vegetative_tillering",
  "irrigation_advisory": [
    {
      "category": "irrigation",
      "title": "Postpone Irrigation: Impending Rainfall",
      "action": "Withhold tube well / canal irrigation for 24-48 hours. Clear drainage gates to store incoming rainwater.",
      "reason": "Current soil moisture is 52.0%, but 35.0mm rain is expected with 80% probability.",
      "urgency": "warning",
      "conditions_triggered": {
        "soil_moisture_pct": 52.0,
        "forecast_rain_mm": 35.0,
        "rain_prob_pct": 80
      },
      "warnings": "Do not pump groundwater when heavy monsoon downpours are forecast to prevent root lodging and waterlogging."
    }
  ],
  "fertilizer_advisory": [
    {
      "category": "fertilizer",
      "title": "Withhold Nitrogen (Urea) Top-Dressing Due to Rain",
      "action": "Postpone urea / chemical fertilizer top-dressing for 48 hours until rain ceases.",
      "reason": "Forecast indicates 35.0mm rain (80% probability). Soluble urea applied before rain suffers heavy leaching and runoff into drainage channels.",
      "urgency": "warning",
      "conditions_triggered": {
        "forecast_rain_mm": 35.0,
        "rain_prob_pct": 80,
        "growth_stage": "vegetative_tillering"
      },
      "warnings": "Top-dress urea only when soil has a thin film of water and no downpours are forecast within 24 hours."
    },
    {
      "category": "fertilizer",
      "title": "Soil Phosphorus Deficit Detected",
      "action": "Incorporate 50 kg/ha Single Superphosphate (SSP) and apply Phosphobacteria biofertilizer @ 2 kg/ha.",
      "reason": "Available soil Phosphorus (18.0 kg/ha) is below critical limit (25 kg/ha). Restricts root elongation and energy transfer.",
      "urgency": "advisory",
      "conditions_triggered": {
        "phosphorus_kg_ha": 18.0
      },
      "warnings": null
    }
  ],
  "soil_health_advisory": [
    {
      "category": "soil_health",
      "title": "Acidic Soil Condition - Lime Amendment Required",
      "action": "Apply Agricultural Lime (CaCO3) @ 500 kg/ha or Dolomite during dry ploughing before puddling.",
      "reason": "Soil pH is 5.4 (acidic). Acidity causes phosphorus fixation and aluminum/iron toxicity in paddy roots.",
      "urgency": "warning",
      "conditions_triggered": {
        "soil_ph": 5.4
      },
      "warnings": "Incorporate lime at least 2 weeks before chemical fertilizer application to prevent ammonia volatilization."
    }
  ],
  "pest_monitoring_alerts": [
    {
      "category": "pest_disease",
      "title": "Rice Blast Disease Alert (High Risk)",
      "action": "Foliar spray of bio-agent Pseudomonas fluorescens (0.2%) @ 2.5 kg/ha or Tricyclazole 75% WP @ 500 g/ha.",
      "reason": "High humidity (88.0%), moderate temperature (28.0°C), and elevated nitrogen (175.0 kg/ha) create optimal conditions for blast sporulation.",
      "urgency": "warning",
      "conditions_triggered": {
        "humidity_pct": 88.0,
        "temperature_c": 28.0,
        "nitrogen_kg_ha": 175.0
      },
      "warnings": "Do not apply nitrogen top-dressing while blast lesions are active on leaf blades."
    },
    {
      "category": "pest_disease",
      "title": "Brown Planthopper (BPH / புகையான்) Monitoring Alert",
      "action": "Practice intermittent draining (drain water for 3 days to dry tiller bases). Spray Neem Oil (3%) @ 15 L/ha or NSKE (5%).",
      "reason": "Heavy canopy closure, high nitrogen, and stagnant water attract hoppers to the base of tillers causing hopper burn.",
      "urgency": "warning",
      "conditions_triggered": {
        "nitrogen_kg_ha": 175.0,
        "growth_stage": "vegetative_tillering",
        "humidity_pct": 88.0
      },
      "warnings": "Form alleyways (30cm pathway every 2-3 meters) to allow sunlight penetration and aeration."
    },
    {
      "category": "pest_disease",
      "title": "Stem Borer Surveillance (Dead Heart / White Earhead)",
      "action": "Install pheromone traps @ 12 traps/ha for monitoring. Release Trichogramma japonicum parasitoid @ 100,000/ha twice.",
      "reason": "Stem borer larvae bore into the central shoot causing dead hearts in vegetative stage and white ears at heading.",
      "urgency": "routine",
      "conditions_triggered": {
        "growth_stage": "vegetative_tillering"
      },
      "warnings": null
    }
  ],
  "conflicts_detected": [
    "Conflict: Field soil moisture is low, but significant rainfall is forecast within 48h.",
    "Conflict: Nitrogen top-dressing scheduled, but heavy rainfall is forecast within 48h."
  ],
  "data_limitations": [],
  "authoritative_source": "Tamil Nadu Agricultural University (TNAU) Crop Production Guide (Paddy) & Agritech Portal",
  "disclaimer": "Agricultural Advisory Disclaimer: Recommendations are rule-based expert guidelines aligned with TNAU benchmarks. They do not guarantee increased crop yield and must be cross-verified with local field observations and Krishi Vigyan Kendra (KVK) advisors."
}
```

---

### 7. Limitations & Ethical Boundary Rules

1. **No Absolute Yield Guarantees:** Biological agricultural outcomes depend heavily on unmodeled stochastic factors (cyclonic flooding, localized pests, saline water intrusions). Advice is provided solely as management recommendations.
2. **Crop Phenology Dependency:** Stage-specific rules require honest input of the current field stage (`vegetative_tillering`, `panicle_initiation`, `flowering_heading`, `grain_filling_maturity`, `nursery`).
3. **No Fabricated Dosages:** If a pest or deficiency is not matched by verified TNAU research trials, no recommendation is invented; the engine directs the user to consult the nearest KVK center.
