"""
AgriSense-AI: Modular Smart Farming Recommendation Engine.
Implements rule-based agronomic guidance for paddy farming in Tamil Nadu
grounded in the Tamil Nadu Agricultural University (TNAU) Crop Production Guide.
"""

from typing import List, Dict, Any, Tuple, Optional
from ..schemas.recommendations import (
    CropStage,
    RecommendationCategory,
    RecommendationUrgency,
    RecommendationItem,
    RecommendationRequest,
    RecommendationsResponse
)

# TNAU Baseline NPK recommendations (kg/ha) by season
TNAU_SEASON_NPK = {
    "Kuruvai": {"N": 120, "P": 40, "K": 40, "name": "Short Duration (Kuruvai)"},
    "Samba": {"N": 150, "P": 50, "K": 50, "name": "Medium/Long Duration (Samba)"},
    "Thaladi": {"N": 150, "P": 50, "K": 50, "name": "Late Season (Thaladi)"},
    "Navarai": {"N": 120, "P": 40, "K": 40, "name": "Dry/Summer Season (Navarai)"}
}

class AgronomicRecommendationEngine:
    """
    Expert system for generating explainable, stage-aware, rule-based recommendations.
    Completely separate from machine learning statistical regression models.
    """

    def generate_recommendations(self, request: RecommendationRequest) -> RecommendationsResponse:
        """
        Evaluates input parameters against TNAU rule bases and generates structured advisories.
        """
        irrigation_items: List[RecommendationItem] = []
        fertilizer_items: List[RecommendationItem] = []
        soil_items: List[RecommendationItem] = []
        pest_items: List[RecommendationItem] = []
        conflicts: List[str] = []
        limitations: List[str] = []

        # 1. Record any absent optional environmental data
        if request.temperature_c is None:
            limitations.append("Temperature was not provided; heat-stress and blast threshold rules used regional default.")
        if request.humidity_pct is None:
            limitations.append("Humidity was not provided; disease pressure evaluation used standard seasonal baselines.")
        if request.forecast_rain_expected_mm is None:
            limitations.append("48-hour rainfall forecast was not provided; fertilizer and irrigation rules evaluated current moisture only.")

        # 2. Evaluate Irrigation Guidance (AWD & Critical Stages)
        self._evaluate_irrigation(request, irrigation_items, conflicts)

        # 3. Evaluate Fertilizer Guidance (TNAU Split Dosage & NPK Balance)
        self._evaluate_fertilizer(request, fertilizer_items, conflicts)

        # 4. Evaluate Soil Health & Amendments
        self._evaluate_soil_health(request, soil_items)

        # 5. Evaluate Pest & Disease Monitoring Alerts
        self._evaluate_pest_alerts(request, pest_items)

        return RecommendationsResponse(
            rule_type="agronomic_expert_system",
            district=request.district,
            season=request.season,
            growth_stage=request.growth_stage,
            irrigation_advisory=irrigation_items,
            fertilizer_advisory=fertilizer_items,
            soil_health_advisory=soil_items,
            pest_monitoring_alerts=pest_items,
            conflicts_detected=conflicts,
            data_limitations=limitations,
            authoritative_source="Tamil Nadu Agricultural University (TNAU) Crop Production Guide (Paddy) & Agritech Portal",
            disclaimer=(
                "Agricultural Advisory Disclaimer: Recommendations are rule-based expert guidelines aligned with TNAU benchmarks. "
                "They do not guarantee increased crop yield and must be cross-verified with local field observations and Krishi Vigyan Kendra (KVK) advisors."
            )
        )

    def _evaluate_irrigation(
        self,
        req: RecommendationRequest,
        items: List[RecommendationItem],
        conflicts: List[str]
    ) -> None:
        """Evaluates Alternate Wetting and Drying (AWD) and critical stage irrigation."""
        stage = req.growth_stage
        moist = req.soil_moisture_pct
        rain_forecast = req.forecast_rain_expected_mm or 0.0
        rain_prob = req.forecast_rain_prob_pct or 0

        # Check for Conflict: Dry soil but heavy rain forecast
        if moist < 60.0 and (rain_forecast >= 20.0 or rain_prob >= 70):
            conflicts.append("Conflict: Field soil moisture is low, but significant rainfall is forecast within 48h.")
            items.append(RecommendationItem(
                category=RecommendationCategory.IRRIGATION,
                title="Postpone Irrigation: Impending Rainfall",
                action="Withhold tube well / canal irrigation for 24-48 hours. Clear drainage gates to store incoming rainwater.",
                reason=f"Current soil moisture is {moist}%, but {rain_forecast}mm rain is expected with {rain_prob}% probability.",
                urgency=RecommendationUrgency.WARNING,
                conditions_triggered={"soil_moisture_pct": moist, "forecast_rain_mm": rain_forecast, "rain_prob_pct": rain_prob},
                warnings="Do not pump groundwater when heavy monsoon downpours are forecast to prevent root lodging and waterlogging."
            ))
            return

        # Stage 1: Flowering / Heading (Critical Moisture Window)
        if stage in [CropStage.FLOWERING_HEADING, CropStage.PANICLE_INITIATION]:
            if moist < 70.0:
                items.append(RecommendationItem(
                    category=RecommendationCategory.IRRIGATION,
                    title="Critical Standing Water Required (Panicle / Heading Stage)",
                    action="Irrigate immediately to maintain 2.5 to 5.0 cm standing water depth continuously.",
                    reason="Panicle initiation and flowering are the most moisture-sensitive stages in paddy. Moisture stress causes pollen sterility and empty spikelets.",
                    urgency=RecommendationUrgency.CRITICAL,
                    conditions_triggered={"growth_stage": stage, "soil_moisture_pct": moist},
                    warnings="Do not practice Alternate Wetting and Drying during flowering. Continuous water film is mandatory."
                ))
            else:
                items.append(RecommendationItem(
                    category=RecommendationCategory.IRRIGATION,
                    title="Maintain Standing Water Level",
                    action="Keep 2.5 cm standing water layer in the field until heading completes.",
                    reason=f"Soil moisture is adequate ({moist}%), maintain steady water depth through heading.",
                    urgency=RecommendationUrgency.ROUTINE,
                    conditions_triggered={"growth_stage": stage, "soil_moisture_pct": moist}
                ))

        # Stage 2: Vegetative Tillering (Safe AWD Window)
        elif stage == CropStage.VEGETATIVE_TILLERING:
            if moist > 80.0:
                items.append(RecommendationItem(
                    category=RecommendationCategory.IRRIGATION,
                    title="Withhold Irrigation (Safe AWD Practice)",
                    action="Allow field water level to naturally recede 15 cm below soil surface in the perforated field pipe.",
                    reason=f"Soil moisture is high ({moist}%). Periodic drying improves root aeration and encourages deeper tillering.",
                    urgency=RecommendationUrgency.ROUTINE,
                    conditions_triggered={"growth_stage": stage, "soil_moisture_pct": moist}
                ))
            elif moist < 60.0:
                items.append(RecommendationItem(
                    category=RecommendationCategory.IRRIGATION,
                    title="AWD Irrigation Cycle: Irrigate to 5cm Depth",
                    action="Irrigate field up to 5 cm depth, then allow water to recede before next irrigation.",
                    reason=f"Soil moisture has dropped to {moist}%, approaching the AWD lower threshold.",
                    urgency=RecommendationUrgency.ADVISORY,
                    conditions_triggered={"growth_stage": stage, "soil_moisture_pct": moist}
                ))
            else:
                items.append(RecommendationItem(
                    category=RecommendationCategory.IRRIGATION,
                    title="Monitor AWD Field Tube",
                    action="Inspect perforated water pipe level. Re-irrigate when water drops 15cm below soil surface.",
                    reason=f"Current soil moisture ({moist}%) is within optimal AWD operational range.",
                    urgency=RecommendationUrgency.ROUTINE,
                    conditions_triggered={"growth_stage": stage, "soil_moisture_pct": moist}
                ))

        # Stage 3: Grain Filling & Maturity
        elif stage == CropStage.GRAIN_FILLING_MATURITY:
            items.append(RecommendationItem(
                category=RecommendationCategory.IRRIGATION,
                title="Terminal Drainage for Harvest",
                action="Completely drain field water 10 to 15 days before expected harvest date.",
                reason="Terminal drainage accelerates uniform grain ripening, hardens soil for harvester machinery, and prevents grain discoloration.",
                urgency=RecommendationUrgency.ADVISORY,
                conditions_triggered={"growth_stage": stage},
                warnings="Ensure terminal drainage is completed before combines enter field."
            ))

        # Stage 4: Nursery
        else:
            items.append(RecommendationItem(
                category=RecommendationCategory.IRRIGATION,
                title="Nursery Seedling Water Management",
                action="Maintain shallow water depth (1-2 cm) to keep soil moist without submerging seedling leaves.",
                reason="Nursery beds require shallow inundation to prevent desiccation while allowing seedling emergence.",
                urgency=RecommendationUrgency.ROUTINE,
                conditions_triggered={"growth_stage": stage}
            ))

    def _evaluate_fertilizer(
        self,
        req: RecommendationRequest,
        items: List[RecommendationItem],
        conflicts: List[str]
    ) -> None:
        """Evaluates TNAU split fertilizer scheduling and soil nutrient balance."""
        stage = req.growth_stage
        season = req.season
        n_val = req.nitrogen_kg_ha
        p_val = req.phosphorus_kg_ha
        k_val = req.potassium_kg_ha
        rain_forecast = req.forecast_rain_expected_mm or 0.0
        rain_prob = req.forecast_rain_prob_pct or 0

        baseline = TNAU_SEASON_NPK.get(season, TNAU_SEASON_NPK["Samba"])

        # Check for Weather Conflict: Imminent rain vs Nitrogen top-dressing
        if (stage in [CropStage.VEGETATIVE_TILLERING, CropStage.PANICLE_INITIATION]) and (rain_forecast >= 15.0 or rain_prob >= 65):
            conflicts.append("Conflict: Nitrogen top-dressing scheduled, but heavy rainfall is forecast within 48h.")
            items.append(RecommendationItem(
                category=RecommendationCategory.FERTILIZER,
                title="Withhold Nitrogen (Urea) Top-Dressing Due to Rain",
                action="Postpone urea / chemical fertilizer top-dressing for 48 hours until rain ceases.",
                reason=f"Forecast indicates {rain_forecast}mm rain ({rain_prob}% probability). Soluble urea applied before rain suffers heavy leaching and runoff into drainage channels.",
                urgency=RecommendationUrgency.WARNING,
                conditions_triggered={"forecast_rain_mm": rain_forecast, "rain_prob_pct": rain_prob, "growth_stage": stage},
                warnings="Top-dress urea only when soil has a thin film of water and no downpours are forecast within 24 hours."
            ))
            return

        # Stage-specific guidance
        if stage == CropStage.VEGETATIVE_TILLERING:
            # Active tillering split: 50% of Nitrogen
            recom_n = baseline["N"] * 0.50
            if n_val < 90.0:
                recom_n += 15.0  # Compensate for severe deficit
                action_text = f"Top-dress {recom_n:.0f} kg/ha Nitrogen (approx. {recom_n * 2.17:.0f} kg Urea) with 25 kg Zinc Sulphate."
                reason_text = f"Soil Nitrogen is deficient ({n_val} kg/ha vs {baseline['N']} kg/ha baseline). Increased split needed to promote tiller count."
                urgency = RecommendationUrgency.ADVISORY
            elif n_val > 180.0:
                recom_n = max(recom_n - 25.0, 15.0)
                action_text = f"Reduce tillering Nitrogen to {recom_n:.0f} kg/ha Urea. Monitor closely for blast and leaf folder."
                reason_text = f"Soil Nitrogen is excessively high ({n_val} kg/ha). Excess urea causes plant lodging and triggers disease outbreaks."
                urgency = RecommendationUrgency.WARNING
            else:
                action_text = f"Top-dress standard TNAU split of {recom_n:.0f} kg/ha Nitrogen (approx. {recom_n * 2.17:.0f} kg Urea) at 20-25 DAT."
                reason_text = f"Soil Nitrogen is balanced. Apply second split after weeding with a thin film of standing water."
                urgency = RecommendationUrgency.ROUTINE

            items.append(RecommendationItem(
                category=RecommendationCategory.FERTILIZER,
                title="Active Tillering Fertilizer Split (20-25 DAT)",
                action=action_text,
                reason=reason_text,
                urgency=urgency,
                conditions_triggered={"growth_stage": stage, "nitrogen_kg_ha": n_val, "season": season}
            ))

        elif stage == CropStage.PANICLE_INITIATION:
            # Panicle split: 25% Nitrogen + 50% Potassium
            recom_n = baseline["N"] * 0.25
            recom_k = baseline["K"] * 0.50
            items.append(RecommendationItem(
                category=RecommendationCategory.FERTILIZER,
                title="Panicle Initiation Split Dosage (40-45 DAT)",
                action=f"Apply {recom_n:.0f} kg/ha Nitrogen (Urea ~{recom_n * 2.17:.0f} kg) and {recom_k:.0f} kg/ha Potassium (MOP ~{recom_k * 1.67:.0f} kg).",
                reason="Potassium and Nitrogen at panicle initiation improve spikelet fertility, reduce grain breakage, and maximize grain weight.",
                urgency=RecommendationUrgency.ADVISORY,
                conditions_triggered={"growth_stage": stage, "potassium_kg_ha": k_val, "season": season}
            ))

        elif stage in [CropStage.FLOWERING_HEADING, CropStage.GRAIN_FILLING_MATURITY]:
            items.append(RecommendationItem(
                category=RecommendationCategory.FERTILIZER,
                title="No Soil-Applied Nitrogen Recommended",
                action="Do not apply soil urea or chemical fertilizers. If leaf color chart (LCC) shows chlorosis, apply 1% foliar Urea or 2% DAP spray.",
                reason="Soil-applied nitrogen at heading promotes vegetative resurgence, attracts earhead bugs, and increases chaffy grains.",
                urgency=RecommendationUrgency.ROUTINE,
                conditions_triggered={"growth_stage": stage}
            ))

        else: # Nursery
            items.append(RecommendationItem(
                category=RecommendationCategory.FERTILIZER,
                title="Nursery Seedbed Nutrition",
                action="Apply 10 kg DAP or 2 kg Urea per 100 sq.m nursery bed at 10-12 days after sowing if seedlings show yellowing.",
                reason="Provides phosphorus for root establishment and nitrogen for robust seedling vigor prior to uprooting.",
                urgency=RecommendationUrgency.ROUTINE,
                conditions_triggered={"growth_stage": stage}
            ))

        # Secondary nutrient Phosphorus check
        if p_val < 25.0:
            items.append(RecommendationItem(
                category=RecommendationCategory.FERTILIZER,
                title="Soil Phosphorus Deficit Detected",
                action="Incorporate 50 kg/ha Single Superphosphate (SSP) and apply Phosphobacteria biofertilizer @ 2 kg/ha.",
                reason=f"Available soil Phosphorus ({p_val} kg/ha) is below critical limit (25 kg/ha). Restricts root elongation and energy transfer.",
                urgency=RecommendationUrgency.ADVISORY,
                conditions_triggered={"phosphorus_kg_ha": p_val}
            ))

    def _evaluate_soil_health(
        self,
        req: RecommendationRequest,
        items: List[RecommendationItem]
    ) -> None:
        """Evaluates soil pH amendment and physical health."""
        ph = req.soil_ph
        soil_type = req.soil_type
        dist = req.district

        if ph < 6.0:
            items.append(RecommendationItem(
                category=RecommendationCategory.SOIL_HEALTH,
                title="Acidic Soil Condition - Lime Amendment Required",
                action="Apply Agricultural Lime (CaCO3) @ 500 kg/ha or Dolomite during dry ploughing before puddling.",
                reason=f"Soil pH is {ph:.1f} (acidic). Acidity causes phosphorus fixation and aluminum/iron toxicity in paddy roots.",
                urgency=RecommendationUrgency.WARNING,
                conditions_triggered={"soil_ph": ph},
                warnings="Incorporate lime at least 2 weeks before chemical fertilizer application to prevent ammonia volatilization."
            ))
        elif ph > 8.0:
            items.append(RecommendationItem(
                category=RecommendationCategory.SOIL_HEALTH,
                title="Alkaline/Sodic Soil Condition - Gypsum Amendment Required",
                action="Apply Agricultural Gypsum (CaSO4·2H2O) @ 500 to 1000 kg/ha followed by impounding water and leaching.",
                reason=f"Soil pH is {ph:.1f} (alkaline/sodic). High sodium causes poor soil structure, puddling dispersion, and micronutrient chlorosis.",
                urgency=RecommendationUrgency.WARNING,
                conditions_triggered={"soil_ph": ph},
                warnings="Ensure surface drainage is available to flush out displaced sodium salts after gypsum reaction."
            ))
        else:
            items.append(RecommendationItem(
                category=RecommendationCategory.SOIL_HEALTH,
                title="Soil Reaction Optimal (pH 6.0 - 7.8)",
                action="Maintain organic matter by incorporating green manure crops (Daincha / Sesbania) @ 6.25 tonnes/ha or FYM @ 12.5 t/ha.",
                reason=f"Soil pH is {ph:.1f}, perfectly situated within the optimal paddy nutrient availability zone.",
                urgency=RecommendationUrgency.ROUTINE,
                conditions_triggered={"soil_ph": ph}
            ))

        # Coastal Saline warning for delta districts
        if soil_type == "Coastal Saline" or dist in ["Nagapattinam", "Cuddalore"]:
            items.append(RecommendationItem(
                category=RecommendationCategory.SOIL_HEALTH,
                title="Coastal Salinity Management",
                action="Maintain continuous shallow water layer (2 cm) to suppress capillary rise of subsoil salts. Apply Farmyard Manure.",
                reason=f"Coastal agro-ecology in {dist} carries periodic salinity risk during dry spells.",
                urgency=RecommendationUrgency.ADVISORY,
                conditions_triggered={"soil_type": soil_type, "district": dist}
            ))

    def _evaluate_pest_alerts(
        self,
        req: RecommendationRequest,
        items: List[RecommendationItem]
    ) -> None:
        """Evaluates Integrated Pest Management (IPM) rules based on microclimate and nitrogen levels."""
        n_val = req.nitrogen_kg_ha
        hum = req.humidity_pct or 75.0
        temp = req.temperature_c or 30.0
        stage = req.growth_stage

        # Rule 1: Rice Blast (Pyricularia oryzae)
        if hum >= 85.0 and temp <= 29.0 and n_val >= 145.0:
            items.append(RecommendationItem(
                category=RecommendationCategory.PEST_DISEASE,
                title="Rice Blast Disease Alert (High Risk)",
                action="Foliar spray of bio-agent Pseudomonas fluorescens (0.2%) @ 2.5 kg/ha or Tricyclazole 75% WP @ 500 g/ha.",
                reason=f"High humidity ({hum}%), moderate temperature ({temp}°C), and elevated nitrogen ({n_val} kg/ha) create optimal conditions for blast sporulation.",
                urgency=RecommendationUrgency.WARNING,
                conditions_triggered={"humidity_pct": hum, "temperature_c": temp, "nitrogen_kg_ha": n_val},
                warnings="Do not apply nitrogen top-dressing while blast lesions are active on leaf blades."
            ))

        # Rule 2: Brown Planthopper (BPH - Nilaparvata lugens)
        if n_val >= 160.0 and hum >= 80.0 and stage in [CropStage.VEGETATIVE_TILLERING, CropStage.PANICLE_INITIATION]:
            items.append(RecommendationItem(
                category=RecommendationCategory.PEST_DISEASE,
                title="Brown Planthopper (BPH / புகையான்) Monitoring Alert",
                action="Practice intermittent draining (drain water for 3 days to dry tiller bases). Spray Neem Oil (3%) @ 15 L/ha or NSKE (5%).",
                reason="Heavy canopy closure, high nitrogen, and stagnant water attract hoppers to the base of tillers causing hopper burn.",
                urgency=RecommendationUrgency.WARNING,
                conditions_triggered={"nitrogen_kg_ha": n_val, "growth_stage": stage, "humidity_pct": hum},
                warnings="Form alleyways (30cm pathway every 2-3 meters) to allow sunlight penetration and aeration."
            ))

        # Rule 3: Yellow Stem Borer (Scirpophaga incertulas)
        if stage in [CropStage.VEGETATIVE_TILLERING, CropStage.PANICLE_INITIATION]:
            items.append(RecommendationItem(
                category=RecommendationCategory.PEST_DISEASE,
                title="Stem Borer Surveillance (Dead Heart / White Earhead)",
                action="Install pheromone traps @ 12 traps/ha for monitoring. Release Trichogramma japonicum parasitoid @ 100,000/ha twice.",
                reason="Stem borer larvae bore into the central shoot causing dead hearts in vegetative stage and white ears at heading.",
                urgency=RecommendationUrgency.ROUTINE,
                conditions_triggered={"growth_stage": stage}
            ))

# Module singleton instance
recommendation_engine = AgronomicRecommendationEngine()
