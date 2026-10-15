# AgriSense-AI: Machine Learning Engine Documentation

## 1. Model Overview & Demonstration Notice

> [!CAUTION]
> **Demonstration Model Notice:**
> The trained model (`ml/saved_models/rf_paddy_yield_model.joblib`) is trained on a **synthetically generated proxy dataset** modeled after Tamil Nadu Agricultural University (TNAU) agronomic baselines. It is constructed for functional validation, inference pipeline integration, and software demonstration. **It does NOT represent verified field-trial precision and should never be used as certified commercial agricultural guidance.**

---

## 2. Model Architecture & Hyperparameters

The model uses a **Random Forest Regressor** (`sklearn.ensemble.RandomForestRegressor`) chosen for its robustness on tabular agronomic datasets, non-linear interaction modeling (e.g., rainfall $\times$ temperature heat stress, nitrogen $\times$ potassium balance), and resistance to overfitting.

| Hyperparameter | Value | Rationale |
| :--- | :--- | :--- |
| `n_estimators` | `150` | Provides smooth ensemble predictions and stable variance estimation for confidence intervals. |
| `max_depth` | `12` | Caps tree depth to avoid memorizing sample-specific stochastic noise. |
| `min_samples_split` | `4` | Requires at least 4 observations to branch an internal node. |
| `min_samples_leaf` | `2` | Smooths leaf predictions across neighboring agronomic observations. |
| `max_features` | `0.8` | Evaluates 80% of features at each split, promoting feature diversity. |
| `random_state` | `42` | Ensures deterministic, reproducible training runs. |
| `n_jobs` | `-1` | Parallel execution across all available CPU cores. |

---

## 3. Evaluation & Baseline Comparison

The model was evaluated against a standard **Dummy Regressor (Mean Predictor)** on an unseen 20% holdout test set ($n = 400$ samples) and validated using **5-Fold Cross Validation** across the entire dataset ($n = 2,000$).

| Metric | Dummy Baseline (Mean) | Random Forest Regressor | Improvement / Performance |
| :--- | :--- | :--- | :--- |
| **MAE (tonnes/ha)** | `0.4180` (4.18 Q/ha) | **`0.1536` (1.54 Q/ha)** | **63.2% error reduction** |
| **RMSE (tonnes/ha)** | `0.5495` (5.50 Q/ha) | **`0.1933` (1.93 Q/ha)** | **64.8% error reduction** |
| **$R^2$ Score (Test)** | `-0.0091` | **`0.8751`** | **87.5% variance explained** |
| **5-Fold CV $R^2$** | `N/A` | **`0.8609` ($\pm 0.0103$)** | High generalizability, low variance |

---

## 4. Feature Importance Ranking

Top 10 most predictive features derived from Gini impurity reduction across the 150 decision trees:

| Rank | Feature | Importance (%) | Agronomic Significance |
| :---: | :--- | :---: | :--- |
| 1 | `season_Navarai` | **22.35%** | Dry/summer season imposes severe heat and solar radiation variance. |
| 2 | `rainfall_mm` | **14.92%** | Primary water supply driver in wetland rice systems. |
| 3 | `season_Samba` | **14.13%** | Northeast monsoon primary crop season in the Cauvery Delta. |
| 4 | `rainfall_temp_ratio` | **10.40%** | Combined moisture adequacy index preventing water deficit. |
| 5 | `previous_yield_tonnes_per_hectare` | **9.04%** | Captures soil fertility inertia and farmer management quality. |
| 6 | `heat_humidity_index` | **7.12%** | Direct thermal comfort and microclimate disease pressure. |
| 7 | `npk_total_kg_ha` | **5.85%** | Total primary macronutrient application. |
| 8 | `nitrogen_kg_ha` | **4.21%** | Key driver of tillering and vegetative biomass. |
| 9 | `soil_moisture_pct` | **3.64%** | Root-zone field saturation. |
| 10 | `soil_ph` | **2.88%** | Soil reaction determining nutrient availability. |

---

## 5. Artifacts & Serialization

Saved to `ml/saved_models/`:
- **`rf_paddy_yield_model.joblib`**: Compressed Scikit-Learn Random Forest Regressor binary.
- **`preprocessor.joblib`**: Fitted `PaddyDataPreprocessor` containing training-set medians and categorical encoding schemas.
- **`feature_metadata.json`**: Structured metadata containing model name, version, feature column list, metrics, and disclaimer.

---

## 6. Commands to Reproduce & Test

### Train & Evaluate Model
```powershell
python -m ml.src.train
```

### Run Full Test Suite (11 Tests)
```powershell
python -m unittest discover -s ml/tests
```

### Sample Inference in Python
```python
from ml.src.inference import load_paddy_yield_predictor

predictor = load_paddy_yield_predictor()
result = predictor.predict({
    "district": "Thanjavur",
    "season": "Samba",
    "soil_type": "Alluvial",
    "rainfall_mm": 1150.0,
    "temperature_c": 29.5,
    "humidity_pct": 82.0,
    "soil_ph": 6.8,
    "soil_moisture_pct": 76.0,
    "nitrogen_kg_ha": 140.0,
    "phosphorus_kg_ha": 48.0,
    "potassium_kg_ha": 45.0,
    "previous_yield_tonnes_per_hectare": 4.5
})

print(f"Predicted Yield: {result['predicted_yield_tonnes_per_hectare']} tonnes/ha")
print(f"In Quintals:     {result['predicted_yield_quintals_per_hectare']} Q/ha")
print(f"90% Bounds:     {result['confidence_interval_90']['lower_tonnes_ha']} - {result['confidence_interval_90']['upper_tonnes_ha']} tonnes/ha")
```
