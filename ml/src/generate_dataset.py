"""
Synthetic Agricultural Dataset Generator for Tamil Nadu Paddy Farming.
STRICT DISCLAIMER: This script generates SYNTHETIC proxy data for software development,
testing, and pipeline benchmarking only. It does NOT represent real-world ground-truth
field trial measurements.
"""

import os
import numpy as np
import pandas as pd
from typing import Dict, Any

# Reproducible random seed
np.random.seed(42)

def generate_synthetic_paddy_dataset(
    n_samples: int = 2000,
    inject_dirty_samples: bool = True,
    output_path: str = "ml/data/raw/synthetic_paddy_yield_tn.csv"
) -> pd.DataFrame:
    """
    Generates a realistic synthetic dataset simulating agro-climatic conditions
    and paddy yield responses in Tamil Nadu.
    
    Args:
        n_samples: Number of sample records to generate.
        inject_dirty_samples: If True, injects minor missing values and outliers to test preprocessing.
        output_path: CSV filepath destination.
        
    Returns:
        pd.DataFrame: Generated dataset.
    """
    districts = [
        "Thanjavur", "Tiruvarur", "Nagapattinam", "Mayiladuthurai",
        "Cuddalore", "Villupuram", "Tiruchirappalli", "Madurai",
        "Tirunelveli", "Kancheepuram", "Thiruvallur", "Erode"
    ]
    # Probabilities reflecting rice cultivation area share in TN
    district_probs = [0.18, 0.16, 0.12, 0.12, 0.09, 0.07, 0.07, 0.05, 0.04, 0.04, 0.03, 0.03]
    
    seasons = ["Samba", "Kuruvai", "Thaladi", "Navarai"]
    season_probs = [0.45, 0.30, 0.15, 0.10]
    
    district_choices = np.random.choice(districts, size=n_samples, p=district_probs)
    season_choices = np.random.choice(seasons, size=n_samples, p=season_probs)
    
    # Soil type assignment conditioned on district
    soil_types = []
    for d in district_choices:
        if d in ["Thanjavur", "Mayiladuthurai", "Tiruchirappalli"]:
            soil_types.append(np.random.choice(["Alluvial", "Clayey", "Red Loam"], p=[0.70, 0.25, 0.05]))
        elif d in ["Tiruvarur", "Cuddalore", "Villupuram"]:
            soil_types.append(np.random.choice(["Clayey", "Alluvial", "Red Loam"], p=[0.65, 0.25, 0.10]))
        elif d in ["Nagapattinam"]:
            soil_types.append(np.random.choice(["Coastal Saline", "Clayey", "Alluvial"], p=[0.55, 0.35, 0.10]))
        else:
            soil_types.append(np.random.choice(["Red Loam", "Clayey", "Alluvial"], p=[0.55, 0.30, 0.15]))
            
    soil_choices = np.array(soil_types)
    
    # Climatic Variables (dependent on season and district)
    rainfall = []
    temperature = []
    humidity = []
    
    for s, d in zip(season_choices, district_choices):
        if s == "Samba":  # Northeast Monsoon period (Oct - Dec)
            rf = np.random.normal(loc=1150, scale=180)
            temp = np.random.normal(loc=29.5, scale=2.0)
            hum = np.random.normal(loc=82, scale=5)
        elif s == "Kuruvai":  # Southwest Monsoon / Summer (Jun - Sep)
            rf = np.random.normal(loc=650, scale=120)
            temp = np.random.normal(loc=33.5, scale=2.2)
            hum = np.random.normal(loc=72, scale=6)
        elif s == "Thaladi":  # Late monsoon / winter
            rf = np.random.normal(loc=850, scale=140)
            temp = np.random.normal(loc=28.5, scale=1.8)
            hum = np.random.normal(loc=78, scale=5)
        else:  # Navarai (Dry summer)
            rf = np.random.normal(loc=380, scale=90)
            temp = np.random.normal(loc=35.0, scale=2.5)
            hum = np.random.normal(loc=64, scale=7)
            
        rainfall.append(max(150.0, rf))
        temperature.append(np.clip(temp, 18.0, 44.0))
        humidity.append(np.clip(hum, 30.0, 98.0))
        
    rainfall = np.array(rainfall)
    temperature = np.array(temperature)
    humidity = np.array(humidity)
    
    # Soil Chemistry and Moisture
    soil_ph = []
    soil_moisture = []
    for st in soil_choices:
        if st == "Alluvial":
            ph = np.random.normal(6.9, 0.4)
            moist = np.random.normal(76, 6)
        elif st == "Clayey":
            ph = np.random.normal(7.2, 0.5)
            moist = np.random.normal(82, 5)
        elif st == "Coastal Saline":
            ph = np.random.normal(7.8, 0.6)
            moist = np.random.normal(78, 6)
        else: # Red Loam
            ph = np.random.normal(6.2, 0.5)
            moist = np.random.normal(68, 7)
            
        soil_ph.append(np.clip(ph, 4.5, 9.0))
        soil_moisture.append(np.clip(moist, 35.0, 95.0))
        
    soil_ph = np.array(soil_ph)
    soil_moisture = np.array(soil_moisture)
    
    # Primary Macronutrients N-P-K (kg/ha)
    # TNAU baselines: N: 120-150, P: 40-50, K: 40-50
    nitrogen = np.clip(np.random.normal(loc=135, scale=25, size=n_samples), 40, 240)
    phosphorus = np.clip(np.random.normal(loc=45, scale=12, size=n_samples), 15, 90)
    potassium = np.clip(np.random.normal(loc=44, scale=10, size=n_samples), 15, 85)
    
    # Previous Season Crop Yield (tonnes/ha)
    previous_yield = np.clip(np.random.normal(loc=4.4, scale=0.65, size=n_samples), 2.2, 6.8)
    
    # Actual Crop Yield (tonnes/ha) Modeling based on Agronomic response
    base_yields = {"Samba": 5.1, "Kuruvai": 4.7, "Thaladi": 4.6, "Navarai": 4.1}
    soil_multipliers = {"Alluvial": 1.05, "Clayey": 1.02, "Red Loam": 0.94, "Coastal Saline": 0.88}
    
    actual_yields = []
    for i in range(n_samples):
        by = base_yields[season_choices[i]]
        sm = soil_multipliers[soil_choices[i]]
        
        # Nutrient response (Mitscherlich curve simulation)
        n_factor = 0.55 + 0.45 * (1 - np.exp(-0.02 * nitrogen[i]))
        p_factor = 0.70 + 0.30 * (1 - np.exp(-0.04 * phosphorus[i]))
        k_factor = 0.75 + 0.25 * (1 - np.exp(-0.04 * potassium[i]))
        nutrient_eff = (n_factor * 0.5) + (p_factor * 0.25) + (k_factor * 0.25)
        
        # Climate stress factors
        temp_stress = 1.0
        if temperature[i] > 35.0:
            temp_stress = 1.0 - (temperature[i] - 35.0) * 0.03
            
        rain_factor = 1.0
        if rainfall[i] < 450.0:
            rain_factor = 0.85
        elif rainfall[i] > 1800.0:
            rain_factor = 0.92  # Submergence stress
            
        # pH stress
        ph_factor = 1.0
        if soil_ph[i] < 5.8:
            ph_factor = 0.90
        elif soil_ph[i] > 8.0:
            ph_factor = 0.88
            
        # Autocorrelation with previous yield (farm fertility inertia)
        prior_factor = 0.20 * (previous_yield[i] / 4.4)
        
        # Combined yield estimate
        expected = by * sm * nutrient_eff * temp_stress * rain_factor * ph_factor * 0.80 + (by * prior_factor)
        noise = np.random.normal(loc=0.0, scale=0.18)
        simulated_yield = np.clip(expected + noise, 1.8, 7.2)
        actual_yields.append(round(float(simulated_yield), 2))
        
    actual_yields = np.array(actual_yields)
    
    # Construct DataFrame
    df = pd.DataFrame({
        "district": district_choices,
        "season": season_choices,
        "soil_type": soil_choices,
        "rainfall_mm": np.round(rainfall, 1),
        "temperature_c": np.round(temperature, 1),
        "humidity_pct": np.round(humidity, 1),
        "soil_ph": np.round(soil_ph, 2),
        "soil_moisture_pct": np.round(soil_moisture, 1),
        "nitrogen_kg_ha": np.round(nitrogen, 1),
        "phosphorus_kg_ha": np.round(phosphorus, 1),
        "potassium_kg_ha": np.round(potassium, 1),
        "previous_yield_tonnes_per_hectare": np.round(previous_yield, 2),
        "yield_tonnes_per_hectare": actual_yields
    })
    
    # Inject dirty samples to test pipeline robustness
    if inject_dirty_samples:
        n_dirty = int(n_samples * 0.015)  # 1.5% dirty values
        dirty_indices = np.random.choice(df.index, size=n_dirty, replace=False)
        
        # A few NaNs in environmental & nutrient features
        for idx in dirty_indices[:n_dirty // 3]:
            col = np.random.choice(["rainfall_mm", "humidity_pct", "nitrogen_kg_ha", "soil_moisture_pct"])
            df.loc[idx, col] = np.nan
            
        # A few duplicate rows
        duplicates = df.iloc[dirty_indices[n_dirty // 3 : 2 * n_dirty // 3]].copy()
        df = pd.concat([df, duplicates], ignore_index=True)
        
        # A couple of out-of-range records (e.g. negative rainfall or typo pH)
        typo_idx = dirty_indices[-2:]
        if len(typo_idx) >= 2:
            df.loc[typo_idx[0], "rainfall_mm"] = -25.0
            df.loc[typo_idx[1], "soil_ph"] = 14.5
            
    # Save CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated synthetic dataset with {len(df)} records saved to: {output_path}")
    return df

if __name__ == "__main__":
    generate_synthetic_paddy_dataset()
