# WildfiresAI — AG2 Architecture (Predict → Act → Choose)

**Author:** Palma Bejarano   
**Mentor:** Dr. Alireza

**Purpose:** This document describes the **AG2 architecture** of WildfiresAI, designed around a continuous **Predict → Act → Choose** cycle for wildfire prevention, containment, and mitigation.

---

## 1. Overview

WildfiresAI integrates **environmental intelligence** and **operational planning** to:
1. **Predict** ignition and propagation (based on terrain, current and forecast weather, fire history, vegetation and maintenance, and human activity).  
2. **Act** with containment and deployment strategies (rings/corridors), issuing **real-time alerts** to firefighters and the population.  
3. **Choose** (optional) optimal materials (inorganic or gel-based) to reinforce the response.

---

## 2. AG2 Dual-Framework

- **Framework A — Analysis & Planning (Think):** data ingestion, ignition risk calculation, spread forecasting, analog retrieval, and containment strategy.  
- **Framework B — Execution & Tools (Act):** technical execution (queries, simulations, logistics, materials) and reporting.

**Coordinator:** A→B bridge that packages **self-contained JSON payloads** and manages **handoffs** between agents (via tools, LLM conditions, or context state).

---

## 3. Data Flow

![AG2 Workflow](../figs/AG2_flowchart.png)



**Logical flow (vertical):**  
`User → Scientist → Planner → Coder → Writer`  
with **feedback loops** `Coder → Planner` and `Writer → Scientist`.

---

## 4. Agents (roles and I/O)

| Agent | Framework | Role | Input | Output |
|---|---|---|---|---|
| **DataAgentWildfire** | A | Ingest FIRMS/EFFIS/NIFC and weather data | APIs | Raw datasets |
| **GeoTerrainAgent** | A | Compute elevation/slope + landcover | DEM, WorldCover | `slope`, `landcover` |
| **HumanActivityAgent** | A | Human pressure (camping, holidays, outliers) | POIs, calendar | `human_outlier_score`, `camping_proximity` |
| **VegConditionAgent** | A | Vegetation/maintenance condition | NDVI/NDMI, firebreaks | `fuel_continuity`, `maintenance_proxy` |
| **FireHistoryAgent** | A | Historical wildfire database | Archives | `history_db` |
| **AnalogFinderAgent** | A | Analog search by multivariate similarity | `x_now`, `history_db` | `analog_support` |
| **IgnitionRiskAgent** | A | Ignition probability (24–48h) | Fused features | `ignition_risk.json` |
| **ForecastAgent** | A | Spread forecast (ROS, perimeter t+Δ) with analogs | State + forecast | `fire_forecast.json` |
| **StrategyAgent** | A | Containment plan (rings/corridors/priorities) | `fire_forecast`, context | `plan_containment.json` |
| **Coordinator** | Bridge | Gateway A→B (validate/normalize payloads) | Outputs A | Payloads B |
| **SwarmPlannerAgent** | B | Deployment trajectories and logistics | `plan_containment` | `deployment_plan.json` |
| **SimAgent** | B | Simulation-in-the-loop (ΔROS/area) | Plan + forecast | Validation/adjustments |
| **ActuationAgent** | B | Drone/robot/fire team interface | Plan | Commands |
| **MaterialsContextBuilder** | B | Material requirements from plan | Plan + environment | `materials_requirements.json` |
| **MaterialsAgent** | B | Select top-10 materials (MP-API) | `materials_requirements` | `materials_top10.csv` |
| **Writer/CommAgent** | B | Reports/alerts to firefighters/public | Artifacts | markdown/alerts |

---

## 5. Predict → Act → Choose (Behavior)

### 5.1 Predict (Risk + Propagation)
**Goal:** Detect imminent ignition and predict spread considering **history + weather (current and forecast) + human activity + terrain + wind + vegetation + maintenance + drought.**

**Features per cell (example):**
- History: `ignition_density_3y`, `analog_support` (k cases)  
- Weather/forecast: `temp`, `rh`, `wind_u/v`, `gust`, `rain_12h`, `Δwind`  
- Terrain/fuel: `slope`, `aspect`, `elev`, `landcover_onehot`, `fuel_continuity`  
- Vegetation/state: `NDVI`, `NDMI`, `dryness_idx`, `maintenance_proxy`  
- Human activity: `camping_proximity`, `weekend_or_holiday`, `human_outlier_score`  
- Drought: `drought_idx`

**Models (MVP):**
- *Ignition:* Calibrated GBDT → `p_ignition (24–48h)`  
- *Spread:* `ROS_base(X)` adjusted by analogs:  
  \[
  \widehat{ROS} = \alpha\,ROS_{base} + (1-\alpha)\sum \omega_i ROS_i
  \]
*Estimated ROS (alternative text):* ROŜ = α·ROS_base + (1–α)·Σ(ωᵢ·ROSᵢ)



**Replanning:** every 10–15 min or when wind changes (`Δdir≥25°`, `Δvel≥10 km/h`) or human activity spikes.

---

### 5.2 Act (Containment + Deployment + Alerts)
**Goal:** If a fire (or high risk) exists, **plan** how to **surround/stop** it and **alert** (firefighters/public), comparing **then vs now**.

**Strategy (initial heuristics):**
- Ring/corridor priority:  
  `score = w_ros*ROS + w_hum*human_risk + w_veg*fuel_continuity + w_val*protected_value`
- Thickness:  
  `thickness_mm = base + k1*ROS + k2*(1 - maintenance_level)`
- Considers analog patterns (slope + wind) **and** current human activity.

**SimAgent:** validates ROS/area reduction; if `ΔROS < 30%`, reoptimizes.

**Alerts:**  
- Firefighters: tactical actions (priority zones, ETA, estimated use).  
- Population: areas to avoid, forecasted evolution.

---

### 5.3 Choose (Materials)
**Goal:** Select optimal material(s) when required by the plan.  
- `MaterialsContextBuilder`: defines `thermal_target`, `adhesion`, `viscosity`, `reapply_hours`, **safety for public areas**.  
- `MaterialsAgent`: filters by `energy_above_hull ≤ 0.1`, presence of oxygen, density, bandgap, thermal stability, and low toxicity.

---

## 6. Payload Schemas (pydantic-friendly)

### 6.1 `reports/ignition_risk.json`
```json
{
  "generated_utc": "ISO8601",
  "horizon_h": 24,
  "grid": [
    {
      "cell_id": "str",
      "lat": 0.0,
      "lon": 0.0,
      "p_ignition": 0.0,
      "top_drivers": ["low_humidity", "camp_area", "high_slope"],
      "human_activity": {
        "camping_proximity_m": 0,
        "weekend_or_holiday": true,
        "human_outlier_score": 0.0
      },
      "veg_condition": {
        "ndvi": 0.0,
        "dryness_idx": 0.0,
        "fuel_continuity": "low|medium|high",
        "maintenance_proxy": "low|medium|high"
      }
    }
  ],
  "hotspots": [
    { "center": "POINT(...)", "p_ignition": 0.0, "reason": "string" }
  ],
  "analogs": [
    { "fire_id": "H-YYYY-XXX", "sim": 0.0, "top_factors": ["..."] }
  ]
}
```

### 6.2 `reports/fire_forecast.json`
```json
{
  "fires": [
    {
      "id": "F-YYYY-XXX",
      "now_perimeter": "GEOJSON",
      "forecast": [
        {
          "t_h": 1,
          "perimeter": "GEOJSON",
          "spread_vectors": [
            { "azimuth_deg": 0, "ros_m_min": 0.0 }
          ]
        },
        { "t_h": 3, "perimeter": "GEOJSON" }
      ],
      "uncertainty": { "p80": "GEOJSON" },
      "analog_support": {
        "k": 10,
        "weighted_ros_m_min": 0.0,
        "weighted_heading_deg": 0.0,
        "cases": [
          { "fire_id": "H-YYYY-XXX", "weight": 0.0, "ros": 0.0, "heading": 0.0 }
        ]
      }
    }
  ]
}
```

### 6.3 `reports/plan_containment.json`
```json
{
  "objectives": ["encircle", "slow_spread"],
  "rings": [
    { "geom": "GEOJSON", "width_m": 0, "priority": 1 }
  ],
  "corridors": [
    { "path": "LINESTRING(...)", "width_m": 0 }
  ],
  "constraints": {
    "no_go": "GEOJSON",
    "max_slope_deg": 35
  },
  "score_weights": {
    "w_ros": 0.4,
    "w_hum": 0.3,
    "w_veg": 0.2,
    "w_val": 0.1
  }
}
```

### 6.4 `reports/deployment_plan.json`
```json
{
  "timestamp_utc": "ISO8601",
  "planner_agent": "SwarmPlannerAgent",
  "plan_id": "D-YYYY-XXX",
  "paths": [
    {
      "unit_id": "U-01",
      "path": "LINESTRING(...)",
      "eta_min": 15,
      "fuel_use_l": 12.3,
      "priority": 1
    }
  ],
  "resources": {
    "water_l": 5000,
    "gel_kg": 150,
    "teams": 3
  }
}
```

### 6.5 `reports/materials_top10.csv`
```csv
material_id,formula,energy_above_hull,density,band_gap,stability,notes
mp-1234,AcCuO3,0.05,6.1,2.5,stable,good thermal resistance
mp-1235,AcNiO3,0.04,6.3,1.8,stable,fireproof oxide
mp-1236,AcGaO3,0.09,5.8,3.0,meta-stable,good adhesion
```

---

## 7. Future Work & Integration

### 7.1 Feedback & Continuous Learning
- Implement **retraining loops** based on new fire outcomes (`SimAgent` + `ForecastAgent` feedback).  
- Add **human-in-the-loop validation** for local authorities (manual overrides and context tagging).  
- Store successful analog cases in `history_db` for model refinement.

### 7.2 Integration with Realtime Systems
- Connect to **Open-Meteo WebSocket** for live wind and humidity streams.  
- Enable **auto-refresh** of ignition and spread predictions every 10–15 minutes.  
- Deploy `CommAgent` for live alerts to emergency networks.

### 7.3 Long-Term Extensions
- Multi-agent reinforcement loop for **autonomous planning under uncertainty**.  
- Link with drone fleet AI (`ActuationAgent`) for **smart containment gel deployment**.  
- Integration with **bio-based material database** (next-gen WildfireGel).
