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

![AG2 Workflow](../figs/AG2_flowchart_MIT_vertical.png)

**Logical flow (vertical):**  
`User → Scientist → Planner → Coordinator → Coder → Writer`  
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
| **Coordinator** | B | Gateway A→B (validate/normalize payloads) | Outputs A | Payloads B |
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
      "lat": 0.0, "lon": 0.0,
      "p_ignition": 0.0,
      "top_drivers": ["low_humidity","camp_area","high_slope"],
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
  "hotspots": [{"center": "POINT(...)", "p_ignition": 0.0, "reason": "string"}],
  "analogs": [{"fire_id": "H-YYYY-XXX", "sim": 0.0, "top_factors": ["..."]}]
}
