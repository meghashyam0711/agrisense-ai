# AgriSense-AI: Agricultural Dataset & Preprocessing Documentation

## 1. Strict Dataset Nature & Disclaimer

> [!CAUTION]
> **Synthetic Dataset Notice for Testing and Demonstration Only:**
> The primary raw dataset provided in `ml/data/raw/synthetic_paddy_yield_tn.csv` is a **synthetically generated proxy dataset** constructed using mathematical models, crop growth parameters, and agro-climatic boundaries informed by the **Tamil Nadu Agricultural University (TNAU) Agritech Portal**.
> 
> This dataset has been engineered specifically for system architecture validation, feature pipeline development, and machine learning pipeline benchmarking. **It must NOT be claimed as certified real-world agronomic observations or used for commercial farming decisions without calibration against empirical Krishi Vigyan Kendra (KVK) field trial records.**

---

## 2. Feature Schema & Unit Definitions

The dataset models seasonal paddy (*Oryza sativa*) production across **12 rice-growing districts** of Tamil Nadu across the **4 standard cropping seasons** (*Samba, Kuruvai, Thaladi, Navarai*).

| Feature Name | Data Type | Physical Unit | Valid Range | Agronomic Meaning & Role |
| :--- | :--- | :--- | :--- | :--- |
| `district` | String (Categorical) | N/A | 12 TN Districts | Geographical zone (Cauvery Delta, Northern, Southern coastal, Western). |
| `season` | String (Categorical) | N/A | 4 Agro-seasons | Cropping season (*Kuruvai, Samba, Thaladi, Navarai*) dictating solar radiation and duration. |
| `soil_type` | String (Categorical) | N/A | 4 Soil types | Dominant soil classification (*Alluvial, Clayey, Red Loam, Coastal Saline*). |
| `rainfall_mm` | Float | Millimeters (mm) | 100.0 – 3,500.0 | Cumulative seasonal precipitation during the crop growth cycle. |
| `temperature_c` | Float | Celsius (°C) | 15.0 – 48.0 | Mean diurnal ambient air temperature during vegetative and heading stages. |
| `humidity_pct` | Float | Percentage (%) | 20.0 – 100.0 | Relative atmospheric humidity influencing evapotranspiration and disease pressure. |
| `soil_ph` | Float | pH scale | 4.0 – 9.5 | Soil active acidity/alkalinity. Ideal paddy neutral range is 6.0 – 7.5. |
| `soil_moisture_pct` | Float | Percentage (%) | 15.0 – 100.0 | Volumetric field soil moisture content in the top 20cm root zone. |
| `nitrogen_kg_ha` | Float | kg / hectare | 10.0 – 300.0 | Available or applied soil Nitrogen (N) for vegetative tillering and leaf development. |
| `phosphorus_kg_ha` | Float | kg / hectare | 5.0 – 150.0 | Available or applied soil Phosphorus ($P_2O_5$) for early root elongation and energy transfer. |
| `potassium_kg_ha` | Float | kg / hectare | 10.0 – 250.0 | Available or applied soil Potassium ($K_2O$) for disease resistance and panicle filling. |
| `previous_yield_tonnes_per_hectare` | Float | Tonnes / hectare | 1.0 – 10.0 | Historical farm yield baseline (1 Tonne = 1,000 kg = 10 Quintals). |
| **`yield_tonnes_per_hectare`** | **Float** | **Tonnes / hectare** | **1.0 – 10.0** | **Prediction Target:** Actual final harvested paddy grain yield per hectare. |

---

## 3. Preprocessing Decisions & Engineering Architecture

The preprocessing pipeline is implemented in [ml/src/preprocessing.py](file:///d:/PROJECTS/AGRI/ml/src/preprocessing.py) through the `PaddyDataPreprocessor` class.

### 3.1 Data Cleaning & Sanitation
1. **Deduplication:** Automatically identifies and drops identical row entries.
2. **Physical Boundary Enforcement:** Validates every numeric feature against known agronomic limits (`FEATURE_BOUNDS`). Anomalies (e.g. negative rainfall or typo pH values like 14.5) are replaced with `NaN` before imputation.
3. **Missing Value Imputation:**
   - **Numerical Features:** Imputed using the **median** value calculated exclusively on the training split to prevent evaluation data leakage.
   - **Categorical Features:** Imputed using the **mode**.
   - **Target Variable (`yield_tonnes_per_hectare`):** Rows with missing target values are dropped rather than imputed to avoid synthetic bias in labels.

### 3.2 Derived Agronomic Features
The module derives high-impact domain features that improve machine learning explainability:
- **`npk_total_kg_ha`:** Total primary macronutrient application ($N + P + K$).
- **`n_p_ratio` & `n_k_ratio`:** Stoichiometric nutrient balance ratios against TNAU recommended proportions (typically $3:1:1$ or $4:1:1$).
- **`heat_humidity_index`:** Thermal stress indicator computed as $\text{temperature} \times (\text{humidity} / 100)$.
- **`rainfall_temp_ratio`:** Moisture adequacy index computed as $\text{rainfall} / \text{temperature}$.
- **`ph_optimality_deviation`:** Absolute distance from optimal neutral paddy soil reaction $|pH - 6.8|$.

### 3.3 Categorical Encoding & Zero-Leakage Splitting
- Categorical features (`district`, `season`, `soil_type`) are transformed using one-hot encoding (`pd.get_dummies`).
- Training feature column structures are cached upon fitting (`encoded_feature_columns`), guaranteeing that subsequent evaluation splits or live inference payloads maintain identical dimensional schemas.
- `split_features_and_target()` separates the feature matrix $X$ and target vector $y$, ensuring no reference to `yield_tonnes_per_hectare` remains in $X$.

---

## 4. Dataset Summary Statistics

Audited from the generated dataset of **2,000 unique records** across Tamil Nadu:

| Feature | Mean | Std Dev | Min | Median | Max |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Rainfall (`rainfall_mm`)** | 881.0 mm | 309.5 mm | 175.4 mm | 880.5 mm | 1,757.9 mm |
| **Temperature (`temperature_c`)** | 31.0 °C | 3.1 °C | 21.7 °C | 30.6 °C | 41.1 °C |
| **Humidity (`humidity_pct`)** | 76.7 % | 8.1 % | 41.5 % | 77.7 % | 98.0 % |
| **Soil pH (`soil_ph`)** | 6.98 | 0.64 | 4.73 | 6.98 | 9.00 |
| **Soil Moisture (`soil_moisture_pct`)** | 77.3 % | 7.3 % | 46.8 % | 78.3 % | 95.0 % |
| **Nitrogen (`nitrogen_kg_ha`)** | 135.4 kg/ha | 25.0 kg/ha | 44.1 kg/ha | 135.4 kg/ha | 240.0 kg/ha |
| **Phosphorus (`phosphorus_kg_ha`)** | 45.3 kg/ha | 11.9 kg/ha | 15.0 kg/ha | 45.4 kg/ha | 82.2 kg/ha |
| **Potassium (`potassium_kg_ha`)** | 44.0 kg/ha | 10.1 kg/ha | 15.0 kg/ha | 44.0 kg/ha | 83.4 kg/ha |
| **Previous Yield** | 4.39 t/ha | 0.65 t/ha | 2.20 t/ha | 4.38 t/ha | 6.75 t/ha |
| **Actual Yield (Target)** | **4.59 t/ha** | **0.54 t/ha** | **2.53 t/ha** | **4.67 t/ha** | **5.79 t/ha** |

*Note: 4.59 tonnes/ha corresponds to 45.9 quintals/ha, matching the Tamil Nadu state benchmark.*

---

## 5. Execution & Verification Guide

### 1. Run Dataset Pipeline & Validation
```powershell
# From the project root directory
python -m ml.src.validate_data
```
Outputs:
- Generates raw data at `ml/data/raw/synthetic_paddy_yield_tn.csv`
- Runs the cleaning, imputation, and feature engineering steps
- Saves preprocessed dataset to `ml/data/processed/paddy_yield_processed.csv`
- Prints the comprehensive statistical audit table

### 2. Run Preprocessing Unit Tests
```powershell
python -m unittest ml/tests/test_preprocessing.py
```
Validates:
- Schema detection & duplicate counts
- Imputation of missing environmental metrics with training medians
- Outlier filtering & clipping within physical agronomic boundaries
- Agronomic feature engineering mathematical correctness
- Zero target leakage in `split_features_and_target()`
