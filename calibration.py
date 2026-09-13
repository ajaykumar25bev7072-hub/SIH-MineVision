"""
===============================================================================
MINEBOARD CAS — FLIGHT CONTROL & SAFETY RECALIBRATION MODULE
===============================================================================
Lead Systems Engineer / Flight Control AI Calibration Engine
Governs the primary safety, kinematic, and environmental thresholds.
Maps incoming sensor streams to SAFE [0], CAUTION [1], and DANGER [2] states.
===============================================================================
"""

from typing import Dict, Any, Tuple, List

# =============================================================================
# RECALIBRATION MATRIX SPECIFICATION
# =============================================================================
RECALIBRATION_MATRIX = {
    "obstacle_distance": {
        "name": "Obstacle Distance (d)",
        "sensor": "HC-SR04 / AI Camera",
        "unit": "meters (m)",
        "safe": {"rule": "d > 10.0", "threshold": 10.0, "state": 0, "label": "SAFE (NOMINAL)"},
        "caution": {"rule": "5.0 <= d <= 10.0", "min": 5.0, "max": 10.0, "state": 1, "label": "CAUTION"},
        "danger": {"rule": "d < 5.0", "threshold": 5.0, "state": 2, "label": "DANGER"}
    },
    "time_to_collision": {
        "name": "Time-to-Collision (TTC)",
        "sensor": "Kinematic Derivative (d / v_closing)",
        "unit": "seconds (s)",
        "safe": {"rule": "TTC > 10.0", "threshold": 10.0, "state": 0, "label": "SAFE (NOMINAL)"},
        "caution": {"rule": "5.0 <= TTC <= 10.0", "min": 5.0, "max": 10.0, "state": 1, "label": "CAUTION"},
        "danger": {"rule": "TTC < 5.0", "threshold": 5.0, "state": 2, "label": "DANGER"}
    },
    "vehicle_speed": {
        "name": "Vehicle Speed (v)",
        "sensor": "CAN Bus / GPS (Neo-6M)",
        "unit": "km/h",
        "safe": {"rule": "v < 10.0", "threshold": 10.0, "state": 0, "label": "SAFE (NOMINAL)"},
        "caution": {"rule": "10.0 <= v <= 15.0", "min": 10.0, "max": 15.0, "state": 1, "label": "CAUTION"},
        "danger": {"rule": "v > 15.0", "threshold": 15.0, "state": 2, "label": "DANGER"}
    },
    "relative_closing_speed": {
        "name": "Relative Closing Speed (v_rel)",
        "sensor": "Kinematic Radar / Doppler",
        "unit": "m/s",
        "safe": {"rule": "v_rel < 1.0", "threshold": 1.0, "state": 0, "label": "SAFE (NOMINAL)"},
        "caution": {"rule": "1.0 <= v_rel <= 2.0", "min": 1.0, "max": 2.0, "state": 1, "label": "CAUTION"},
        "danger": {"rule": "v_rel > 2.0", "threshold": 2.0, "state": 2, "label": "DANGER"}
    },
    "relative_humidity": {
        "name": "Relative Humidity (RH)",
        "sensor": "DHT22 Capacitive",
        "unit": "% RH",
        "safe": {"rule": "RH < 80%", "threshold": 80.0, "state": 0, "label": "SAFE (NOMINAL)"},
        "caution": {"rule": "80% <= RH <= 90%", "min": 80.0, "max": 90.0, "state": 1, "label": "CAUTION"},
        "danger": {"rule": "RH > 90%", "threshold": 90.0, "state": 2, "label": "DANGER"}
    },
    "moisture_precipitation": {
        "name": "Moisture / Precipitation",
        "sensor": "YL-83 Rain Sensor",
        "unit": "State / Intensity",
        "safe": {"rule": "Dry (Rain = False)", "state": 0, "label": "SAFE (NOMINAL)"},
        "caution": {"rule": "Rain Detected (Active)", "state": 1, "label": "CAUTION"},
        "danger": {"rule": "Heavy Rain / Flood", "state": 2, "label": "DANGER"}
    },
    "gas_concentration": {
        "name": "Gas Concentration (Exhaust Hydrocarbons)",
        "sensor": "MQ-2 ADC (10-bit Scaled)",
        "unit": "PPM",
        "safe": {"rule": "Gas < 300 PPM", "threshold": 300.0, "state": 0, "label": "SAFE (NOMINAL)"},
        "caution": {"rule": "300 <= Gas <= 500 PPM", "min": 300.0, "max": 500.0, "state": 1, "label": "CAUTION"},
        "danger": {"rule": "Gas > 500 PPM", "threshold": 500.0, "state": 2, "label": "DANGER"}
    },
    "blindspot_motion": {
        "name": "Blindspot Motion",
        "sensor": "HC-SR501 PIR + Lateral Radar",
        "unit": "Detection State & Range (m)",
        "safe": {"rule": "No Motion", "state": 0, "label": "SAFE (NOMINAL)"},
        "caution": {"rule": "Motion detected (d >= 5.0m)", "state": 1, "label": "CAUTION"},
        "danger": {"rule": "Motion AND d < 5.0m", "state": 2, "label": "DANGER"}
    }
}

STATE_NAMES = {0: "SAFE (NOMINAL)", 1: "CAUTION", 2: "DANGER"}
STATE_COLORS = {0: "#10b981", 1: "#f59e0b", 2: "#ef4444"}

# =============================================================================
# INDIVIDUAL PARAMETER EVALUATION FUNCTIONS
# =============================================================================

def eval_obstacle_distance(distance_m: float) -> Tuple[int, str]:
    """
    HC-SR04 / AI Camera:
      d > 10.0 m           -> SAFE [0]
      5.0 m <= d <= 10.0 m -> CAUTION [1]
      d < 5.0 m            -> DANGER [2]
    Boundary Rule: Exactly 10.0m is clamped to CAUTION per [5.0, 10.0].
    """
    d = float(distance_m)
    if d < 5.0:
        return 2, "DANGER"
    elif d <= 10.0:
        return 1, "CAUTION"
    else:
        return 0, "SAFE (NOMINAL)"

def eval_time_to_collision(ttc_s: float) -> Tuple[int, str]:
    """
    Kinematic Derivative (d / v_closing):
      TTC > 10.0 s          -> SAFE [0]
      5.0 s <= TTC <= 10.0 s -> CAUTION [1]
      TTC < 5.0 s           -> DANGER [2]
    """
    ttc = float(ttc_s)
    if ttc < 0:
        return 0, "SAFE (NOMINAL)"
    if ttc < 5.0:
        return 2, "DANGER"
    elif ttc <= 10.0:
        return 1, "CAUTION"
    else:
        return 0, "SAFE (NOMINAL)"

def eval_vehicle_speed(speed_kmh: float) -> Tuple[int, str]:
    """
    CAN Bus / GPS:
      v < 10.0 km/h           -> SAFE [0]
      10.0 <= v <= 15.0 km/h  -> CAUTION [1]
      v > 15.0 km/h           -> DANGER [2]
    """
    v = float(speed_kmh)
    if v > 15.0:
        return 2, "DANGER"
    elif v >= 10.0:
        return 1, "CAUTION"
    else:
        return 0, "SAFE (NOMINAL)"

def eval_relative_closing_speed(v_rel_ms: float) -> Tuple[int, str]:
    """
    Kinematic Radar / Doppler:
      v_rel < 1.0 m/s          -> SAFE [0]
      1.0 <= v_rel <= 2.0 m/s  -> CAUTION [1]
      v_rel > 2.0 m/s          -> DANGER [2]
    """
    vr = float(v_rel_ms)
    if vr > 2.0:
        return 2, "DANGER"
    elif vr >= 1.0:
        return 1, "CAUTION"
    else:
        return 0, "SAFE (NOMINAL)"

def eval_relative_humidity(humidity_pct: float) -> Tuple[int, str]:
    """
    DHT22 Capacitive:
      RH < 80%          -> SAFE [0]
      80% <= RH <= 90%  -> CAUTION [1]
      RH > 90%          -> DANGER [2]
    """
    rh = float(humidity_pct)
    if rh > 90.0:
        return 2, "DANGER"
    elif rh >= 80.0:
        return 1, "CAUTION"
    else:
        return 0, "SAFE (NOMINAL)"

def eval_moisture_precipitation(rain_detected: bool, heavy_rain: bool = False) -> Tuple[int, str]:
    """
    YL-83 Rain Sensor:
      Dry (Rain = False)       -> SAFE [0]
      Rain Detected (Active)   -> CAUTION [1]
      Heavy Rain / Flood       -> DANGER [2]
    """
    if heavy_rain:
        return 2, "DANGER"
    elif rain_detected:
        return 1, "CAUTION"
    else:
        return 0, "SAFE (NOMINAL)"

def eval_gas_concentration(gas_ppm: float) -> Tuple[int, str]:
    """
    MQ-2 ADC (Scaled PPM):
      Gas < 300 PPM          -> SAFE [0]
      300 <= Gas <= 500 PPM  -> CAUTION [1]
      Gas > 500 PPM          -> DANGER [2]
    """
    ppm = float(gas_ppm)
    if ppm > 500.0:
        return 2, "DANGER"
    elif ppm >= 300.0:
        return 1, "CAUTION"
    else:
        return 0, "SAFE (NOMINAL)"

def eval_blindspot_motion(motion_detected: bool, distance_m: float) -> Tuple[int, str]:
    """
    HC-SR501 PIR:
      No Motion                 -> SAFE [0]
      Motion detected (d >= 5m) -> CAUTION [1]
      Motion AND d < 5.0m       -> DANGER [2]
    """
    if not motion_detected:
        return 0, "SAFE (NOMINAL)"
    
    d = float(distance_m)
    if d < 5.0:
        return 2, "DANGER"
    else:
        return 1, "CAUTION"

# =============================================================================
# COMBINED VEHICLE TELEMETRY RISK EVALUATION
# =============================================================================

def evaluate_truck_telemetry(t: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies the full recalibration matrix to a truck's raw sensor telemetry.
    Computes per-sensor state scores [0, 1, 2], identifies triggers, and assigns
    the overall vehicle safety state based on the worst-case parameter.
    """
    # 1. Distance
    d_m = t.get("distance_m", 50.0)
    score_d, label_d = eval_obstacle_distance(d_m)

    # 2. Vehicle Speed
    v_kmh = t.get("speed_kmh", 0.0)
    score_v, label_v = eval_vehicle_speed(v_kmh)

    # 3. Relative Closing Speed
    v_rel_ms = t.get("closing_speed_ms")
    if v_rel_ms is None:
        # Fallback to speed in m/s if closing speed not explicitly tracked
        v_rel_ms = t.get("speed_ms", v_kmh / 3.6)
    score_vrel, label_vrel = eval_relative_closing_speed(v_rel_ms)

    # 4. TTC
    ttc_s = t.get("ttc_s", 999.0)
    score_ttc, label_ttc = eval_time_to_collision(ttc_s)

    # 5. Humidity
    rh = t.get("humidity", 50.0)
    score_rh, label_rh = eval_relative_humidity(rh)

    # 6. Moisture / Rain
    rain = bool(t.get("rain", False))
    heavy_rain = bool(t.get("heavy_rain", False) or (rain and rh > 90.0))
    score_rain, label_rain = eval_moisture_precipitation(rain, heavy_rain)

    # 7. Gas PPM
    gas = t.get("gas_ppm", 200.0)
    score_gas, label_gas = eval_gas_concentration(gas)

    # 8. Blindspot Motion
    motion = bool(t.get("motion", False))
    blind_dist = t.get("blindspot_dist_m", d_m)
    score_blind, label_blind = eval_blindspot_motion(motion, blind_dist)

    parameter_scores = {
        "obstacle_distance": {"score": score_d, "state": label_d, "value": f"{d_m:.1f} m", "sensor": "HC-SR04"},
        "time_to_collision": {"score": score_ttc, "state": label_ttc, "value": f"{ttc_s:.1f} s" if ttc_s < 900 else "CLEAR", "sensor": "Kinematic Derivative"},
        "vehicle_speed": {"score": score_v, "state": label_v, "value": f"{v_kmh:.1f} km/h", "sensor": "CAN / GPS"},
        "relative_closing_speed": {"score": score_vrel, "state": label_vrel, "value": f"{v_rel_ms:.2f} m/s", "sensor": "Radar"},
        "relative_humidity": {"score": score_rh, "state": label_rh, "value": f"{rh:.1f}% RH", "sensor": "DHT22"},
        "moisture_precipitation": {"score": score_rain, "state": label_rain, "value": "Heavy/Flood" if heavy_rain else ("Rain Active" if rain else "Dry"), "sensor": "YL-83"},
        "gas_concentration": {"score": score_gas, "state": label_gas, "value": f"{gas:.0f} PPM", "sensor": "MQ-2 ADC"},
        "blindspot_motion": {"score": score_blind, "state": label_blind, "value": f"Motion @ {blind_dist:.1f}m" if motion else "Clear", "sensor": "HC-SR501 PIR"}
    }

    all_scores = [score_d, score_ttc, score_v, score_vrel, score_rh, score_rain, score_gas, score_blind]
    worst_score = max(all_scores)

    # Map to nominal / caution / danger
    overall_state_label = "DANGER" if worst_score == 2 else ("CAUTION" if worst_score == 1 else "NOMINAL")
    overall_color = STATE_COLORS[worst_score]

    # Collect non-zero triggers
    triggers = [k for k, v in parameter_scores.items() if v["score"] > 0]
    danger_triggers = [k for k, v in parameter_scores.items() if v["score"] == 2]

    # Dominant hazard detection
    if danger_triggers:
        dominant_hazard = danger_triggers[0]
    elif triggers:
        dominant_hazard = triggers[0]
    else:
        dominant_hazard = "all_systems_clear"

    return {
        "overall_score": worst_score,
        "overall_state": overall_state_label,
        "overall_color": overall_color,
        "dominant_hazard": dominant_hazard,
        "triggers": triggers,
        "parameter_scores": parameter_scores
    }
