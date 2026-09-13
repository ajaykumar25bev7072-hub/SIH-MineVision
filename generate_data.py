"""
MineBoard CAS — Autonomous Mining-Truck Fleet Collision Avoidance System
Scenario & Telemetry Data Generator with Exact Firmware Calibration Engine Integration
"""

import json
import math
import os
import sys

# Ensure local directory is on import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calibration

def generate_sample_data():
    TRUCK_CONFIGS = {
        "Truck A": {
            "name": "Truck A (Interceptor)",
            "role": "Speeding & Trajectory Closure",
            "start_x": 45.0, "start_y": 80.0,
            "dx": 0.0, "dy": -0.8,
            "hx": 0.0, "hy": -1.0,
            "target": "CAT 793D (Hauler 12)",
            "target_type": "HEAVY-DUMP-TRUCK",
            "det_source": "AI CAMERA + V2V RADAR"
        },
        "Truck B": {
            "name": "Truck B (Slope Hauler)",
            "role": "Adverse Wet Incline Slip",
            "start_x": 75.0, "start_y": 70.0,
            "dx": -0.65, "dy": -0.45,
            "hx": -0.82, "hy": -0.57,
            "target": "Slope Retaining Berm",
            "target_type": "STATIC-BERM",
            "det_source": "YL-83 + DHT22 + RADAR"
        },
        "Truck C": {
            "name": "Truck C (Pit Shovel Loader)",
            "role": "Toxic Exhaust Inversion",
            "start_x": 20.0, "start_y": 35.0,
            "dx": 0.25, "dy": -0.15,
            "hx": 0.86, "hy": -0.51,
            "target": "Excavator EX-04 Staging",
            "target_type": "HYDRAULIC-SHOVEL",
            "det_source": "MQ-2 ADC GAS SENSOR"
        },
        "Truck D": {
            "name": "Truck D (Loading Maneuver)",
            "role": "Ground Worker Blind-Spot",
            "start_x": 60.0, "start_y": 25.0,
            "dx": -0.1, "dy": 0.2,
            "hx": -0.45, "hy": 0.89,
            "target": "Hopper Support Worker",
            "target_type": "GROUND-PERSONNEL",
            "det_source": "HC-SR501 PIR + RADAR"
        }
    }

    steps_data = []

    for step in range(50):
        t = step / 49.0
        step_trucks = {}

        # ---------------------------------------------------------------------
        # 1. TRUCK A: "The High-Speed Closure"
        # Progresses through SAFE [0] -> CAUTION [1] -> DANGER [2]
        # Step 0-9:   v=8.8 km/h (<10), d=26m (>10), TTC>10s, v_rel=0.8 m/s (<1.0) -> SAFE
        # Step 10-17: v=13.2 km/h (10-15), d=14m, TTC=8.2s (5-10), v_rel=1.4 m/s (1-2) -> CAUTION
        # Step 18-49: v=26.5 km/h (>15), d=4.5m (<5.0), TTC=1.6s (<5.0), v_rel=2.4 m/s (>2.0) -> DANGER
        # ---------------------------------------------------------------------
        cfg_a = TRUCK_CONFIGS["Truck A"]
        if step < 10:
            speed_a = round(8.2 + 0.15 * step, 1) # < 10.0 km/h (SAFE)
            dist_a = round(28.0 - 1.2 * step, 1)  # > 10.0 m (SAFE)
            rel_closing_speed_a = 0.75            # < 1.0 m/s (SAFE)
        elif step < 18:
            speed_a = round(11.0 + 0.4 * (step - 10), 1) # 10.0 - 15.0 km/h (CAUTION)
            dist_a = round(16.0 - 0.7 * (step - 10), 1)  # 5.0 - 10.0 m or > 10m
            rel_closing_speed_a = 1.45                   # 1.0 - 2.0 m/s (CAUTION)
        else:
            speed_a = round(min(27.8, 16.5 + 0.38 * (step - 18)), 1) # > 15.0 km/h (DANGER)
            dist_a = round(max(4.2, 10.2 - 0.22 * (step - 18)), 1)   # < 5.0 m (DANGER)
            rel_closing_speed_a = 2.45                                # > 2.0 m/s (DANGER)

        speed_a_ms = round(speed_a / 3.6, 2)
        # Kinematic derivative TTC = distance / closing_speed
        ttc_a = round(dist_a / max(0.1, rel_closing_speed_a), 1)
        if ttc_a < 0 or ttc_a > 30:
            ttc_a = 999.0

        gas_a = int(195 + 15 * math.sin(step * 0.2)) # Safe < 300
        hum_a = int(55 + 4 * math.sin(step * 0.1))   # Safe < 80%
        temp_a = round(28.0 + 1.2 * math.cos(step * 0.15), 1)
        rain_a = False
        motion_a = False
        blind_dist_a = round(22.0 + 2.0 * math.sin(step * 0.3), 1)

        t_data_a = {
            "truck_id": "Truck A",
            "truck_name": cfg_a["name"],
            "role": cfg_a["role"],
            "step": step,
            "x": round(cfg_a["start_x"] + cfg_a["dx"] * step * 0.5, 1),
            "y": round(cfg_a["start_y"] + cfg_a["dy"] * step * 0.7, 1),
            "hx": cfg_a["hx"], "hy": cfg_a["hy"],
            "speed_kmh": speed_a,
            "speed_ms": speed_a_ms,
            "closing_speed_ms": rel_closing_speed_a,
            "distance_m": dist_a,
            "blindspot_dist_m": blind_dist_a,
            "ttc_s": ttc_a,
            "gas_ppm": gas_a,
            "humidity": hum_a,
            "temp_c": temp_a,
            "rain": rain_a,
            "motion": motion_a,
            "obstacle_target": cfg_a["target"],
            "obstacle_type": cfg_a["target_type"],
            "detection_source": cfg_a["det_source"],
            "diagnostics": {"GPS": "Online", "HC-SR04": "Online", "MQ-2": "Online", "DHT22": "Online", "YL-83": "Online", "PIR": "Online"}
        }
        eval_a = calibration.evaluate_truck_telemetry(t_data_a)
        t_data_a["risk"] = eval_a["overall_state"]
        t_data_a["calibration_eval"] = eval_a
        t_data_a["risk_headline"] = (
            "CRITICAL COLLISION TRAJECTORY — SPEEDING & PROXIMITY" if eval_a["overall_state"] == "DANGER"
            else ("CLOSING DISTANCE TO LEAD HAULER (BUFFER COMPROMISED)" if eval_a["overall_state"] == "CAUTION"
            else "HAUL CORRIDOR CLEAR — NOMINAL OPERATIONS")
        )
        t_data_a["risk_action"] = (
            "AEB Full Override Active (-3.5 m/s²) • Cab Siren Activated" if eval_a["overall_state"] == "DANGER"
            else ("Governed Speed 15 km/h • Maintain 25m Buffer" if eval_a["overall_state"] == "CAUTION"
            else "Cruising Speed Permitted")
        )
        step_trucks["Truck A"] = t_data_a

        # ---------------------------------------------------------------------
        # 2. TRUCK B: "Adverse Wet Curved Descent"
        # Progresses through SAFE [0] -> CAUTION [1]
        # Step 0-11:  Dry (rain=False), RH=62% (<80), v=8.5 km/h (<10), d=18m -> SAFE
        # Step 12-49: Rain active (YL-83=True), RH=84% (80-90%), v=12.5 km/h (10-15), d=8.5m (5-10) -> CAUTION
        # ---------------------------------------------------------------------
        cfg_b = TRUCK_CONFIGS["Truck B"]
        rain_b = (step >= 12)
        hum_b = int(min(88, 62 + (24.0 * (1.0 - math.exp(-0.18 * max(0, step - 10)))))) if rain_b else int(60 + 2 * math.sin(step))
        speed_b = round(8.5 if step < 12 else 12.0 + 1.2 * math.sin(step * 0.2), 1) # 10-15 km/h
        speed_b_ms = round(speed_b / 3.6, 2)
        dist_b = round(18.0 - (9.5 * (step / 49.0)), 1) if rain_b else 19.5 # Lands at ~8.5m (CAUTION: 5-10m)
        v_rel_b = round(min(1.6, speed_b_ms), 2) # 1.0 - 2.0 m/s (CAUTION)
        ttc_b = round(dist_b / max(0.1, v_rel_b), 1)
        gas_b = int(220 + 12 * math.cos(step * 0.1))
        temp_b = round(24.5 - (2.2 if rain_b else 0.0) + 0.3 * math.sin(step * 0.2), 1)
        motion_b = False
        blind_dist_b = 18.0

        t_data_b = {
            "truck_id": "Truck B",
            "truck_name": cfg_b["name"],
            "role": cfg_b["role"],
            "step": step,
            "x": round(cfg_b["start_x"] + cfg_b["dx"] * step * 0.5, 1),
            "y": round(cfg_b["start_y"] + cfg_b["dy"] * step * 0.5, 1),
            "hx": cfg_b["hx"], "hy": cfg_b["hy"],
            "speed_kmh": speed_b,
            "speed_ms": speed_b_ms,
            "closing_speed_ms": v_rel_b,
            "distance_m": dist_b,
            "blindspot_dist_m": blind_dist_b,
            "ttc_s": ttc_b,
            "gas_ppm": gas_b,
            "humidity": hum_b,
            "temp_c": temp_b,
            "rain": rain_b,
            "motion": motion_b,
            "obstacle_target": cfg_b["target"],
            "obstacle_type": cfg_b["target_type"],
            "detection_source": cfg_b["det_source"],
            "diagnostics": {"GPS": "Online", "HC-SR04": "Online", "MQ-2": "Online", "DHT22": "Online", "YL-83": "Online", "PIR": "Online"}
        }
        eval_b = calibration.evaluate_truck_telemetry(t_data_b)
        t_data_b["risk"] = eval_b["overall_state"]
        t_data_b["calibration_eval"] = eval_b
        t_data_b["risk_headline"] = (
            "SLIPPERY INCLINE HAZARD — PRECIPITATION & ELEVATED HUMIDITY" if eval_b["overall_state"] == "CAUTION"
            else "DESCENT INCLINE CLEAR — DRY SURFACE"
        )
        t_data_b["risk_action"] = (
            "Hydraulic Retarder Engaged • Anti-Slip Traction Mode Active" if eval_b["overall_state"] == "CAUTION"
            else "Standard Downhill Descent Profile"
        )
        step_trucks["Truck B"] = t_data_b

        # ---------------------------------------------------------------------
        # 3. TRUCK C: "Exhaust Gas Accumulation"
        # Progresses through SAFE [0] -> CAUTION [1] -> DANGER [2]
        # Step 0-14:  Gas < 300 PPM, v=7.2 km/h (<10), d=24m (>10) -> SAFE
        # Step 15-28: Gas = 320 to 480 PPM (300-500 PPM) -> CAUTION
        # Step 29-49: Gas spikes to 530 - 660 PPM (> 500 PPM) -> DANGER
        # ---------------------------------------------------------------------
        cfg_c = TRUCK_CONFIGS["Truck C"]
        speed_c = round(max(3.5, 7.5 - 0.08 * step), 1) # < 10.0 km/h (SAFE)
        speed_c_ms = round(speed_c / 3.6, 2)
        dist_c = round(22.0 + 1.2 * math.sin(step * 0.15), 1) # > 10.0 m (SAFE)
        v_rel_c = round(speed_c_ms * 0.5, 2) # < 1.0 m/s (SAFE)
        ttc_c = 999.0

        if step < 15:
            gas_c = int(185 + step * 6.5) # 185 -> 276 PPM (SAFE < 300)
        elif step < 29:
            gas_c = int(310 + (step - 15) * 13) # 310 -> 479 PPM (CAUTION 300-500)
        else:
            gas_c = int(min(665, 515 + (step - 29) * 7.5 + 8 * math.sin(step))) # > 500 PPM (DANGER)

        hum_c = 48
        temp_c = round(31.0 + 0.1 * step, 1)
        rain_c = False
        motion_c = False
        blind_dist_c = 15.0

        t_data_c = {
            "truck_id": "Truck C",
            "truck_name": cfg_c["name"],
            "role": cfg_c["role"],
            "step": step,
            "x": round(cfg_c["start_x"] + cfg_c["dx"] * step * 0.4, 1),
            "y": round(cfg_c["start_y"] + cfg_c["dy"] * step * 0.4, 1),
            "hx": cfg_c["hx"], "hy": cfg_c["hy"],
            "speed_kmh": speed_c,
            "speed_ms": speed_c_ms,
            "closing_speed_ms": v_rel_c,
            "distance_m": dist_c,
            "blindspot_dist_m": blind_dist_c,
            "ttc_s": ttc_c,
            "gas_ppm": gas_c,
            "humidity": hum_c,
            "temp_c": temp_c,
            "rain": rain_c,
            "motion": motion_c,
            "obstacle_target": cfg_c["target"],
            "obstacle_type": cfg_c["target_type"],
            "detection_source": cfg_c["det_source"],
            "diagnostics": {"GPS": "Online", "HC-SR04": "Online", "MQ-2": "Online", "DHT22": "Online", "YL-83": "Online", "PIR": "Online"}
        }
        eval_c = calibration.evaluate_truck_telemetry(t_data_c)
        t_data_c["risk"] = eval_c["overall_state"]
        t_data_c["calibration_eval"] = eval_c
        t_data_c["risk_headline"] = (
            f"TOXIC DIESEL EXHAUST CONCENTRATION SPIKE ({gas_c} PPM > 500)" if eval_c["overall_state"] == "DANGER"
            else (f"ELEVATED HYDROCARBON GAS READINGS ({gas_c} PPM)" if eval_c["overall_state"] == "CAUTION"
            else "ATMOSPHERIC QUALITY NOMINAL (< 300 PPM)")
        )
        t_data_c["risk_action"] = (
            "Cabin HVAC Sealed • Recirculation Active • Evacuate Pocket" if eval_c["overall_state"] == "DANGER"
            else ("Activate Auxiliary Ventilation • Monitor Sensor Plume" if eval_c["overall_state"] == "CAUTION"
            else "Staging Operations Safe")
        )
        step_trucks["Truck C"] = t_data_c

        # ---------------------------------------------------------------------
        # 4. TRUCK D: "Loading Zone Blind-Spot Hazard"
        # Progresses through SAFE [0] -> CAUTION [1] -> DANGER [2] -> SAFE [0]
        # Step 0-19:  motion=False, v=4.2 km/h (<10), d=24m (>10) -> SAFE
        # Step 20-25: motion=True, worker entering perimeter at d=6.8m (d >= 5.0m) -> CAUTION
        # Step 26-45: motion=True, worker breaches blind-spot at d=3.4m (d < 5.0m) -> DANGER
        # Step 46-49: motion=False, worker cleared -> SAFE
        # ---------------------------------------------------------------------
        cfg_d = TRUCK_CONFIGS["Truck D"]
        speed_d = round(max(0.5, 4.2 - 0.07 * step if step < 30 else 1.2), 1) # < 10.0 km/h (SAFE)
        speed_d_ms = round(speed_d / 3.6, 2)
        dist_d = round(24.0 + 1.2 * math.cos(step * 0.1), 1)                  # > 10.0 m (SAFE)
        v_rel_d = round(speed_d_ms * 0.3, 2)                                 # < 1.0 m/s (SAFE)
        ttc_d = 999.0

        if 20 <= step <= 25:
            motion_d = True
            blind_dist_d = round(6.8 - 0.2 * (step - 20), 1) # 6.8 -> 5.8 m (>= 5.0m -> CAUTION)
            obs_target_d = "Ground Worker Approaching Blind-Spot"
        elif 26 <= step <= 45:
            motion_d = True
            blind_dist_d = round(3.4 + 0.2 * math.sin(step * 0.5), 1) # 3.2 - 3.6 m (< 5.0m -> DANGER)
            obs_target_d = "Ground Personnel Inside Blind-Spot Cone"
        else:
            motion_d = False
            blind_dist_d = 14.5
            obs_target_d = "Loading Hopper Perimeter Clear"

        gas_d = int(210 + 10 * math.sin(step * 0.2)) # Safe < 300
        hum_d = 52
        temp_c_d = round(27.5 + 0.3 * math.cos(step * 0.2), 1)
        rain_d = False

        t_data_d = {
            "truck_id": "Truck D",
            "truck_name": cfg_d["name"],
            "role": cfg_d["role"],
            "step": step,
            "x": round(cfg_d["start_x"] + cfg_d["dx"] * step * 0.3, 1),
            "y": round(cfg_d["start_y"] + cfg_d["dy"] * step * 0.3, 1),
            "hx": cfg_d["hx"], "hy": cfg_d["hy"],
            "speed_kmh": speed_d,
            "speed_ms": speed_d_ms,
            "closing_speed_ms": v_rel_d,
            "distance_m": dist_d,
            "blindspot_dist_m": blind_dist_d,
            "ttc_s": ttc_d,
            "gas_ppm": gas_d,
            "humidity": hum_d,
            "temp_c": temp_c_d,
            "rain": rain_d,
            "motion": motion_d,
            "obstacle_target": obs_target_d,
            "obstacle_type": "GROUND-PERSONNEL" if motion_d else "CLEAR",
            "detection_source": "HC-SR501 PIR + LATERAL RADAR" if motion_d else "HC-SR04 ULTRASONIC",
            "diagnostics": {"GPS": "Online", "HC-SR04": "Online", "MQ-2": "Online", "DHT22": "Online", "YL-83": "Online", "PIR": "Online"}
        }
        eval_d = calibration.evaluate_truck_telemetry(t_data_d)
        t_data_d["risk"] = eval_d["overall_state"]
        t_data_d["calibration_eval"] = eval_d
        t_data_d["risk_headline"] = (
            f"PEDESTRIAN IN LATERAL BLIND-SPOT ({blind_dist_d}m < 5.0m)" if eval_d["overall_state"] == "DANGER"
            else (f"LATERAL MOTION DETECTED AT PERIMETER ({blind_dist_d}m >= 5.0m)" if eval_d["overall_state"] == "CAUTION"
            else "LOADING ZONE CORRIDOR SECURE")
        )
        t_data_d["risk_action"] = (
            "Immediate Hydraulic Brake Lock • Blind-Spot Camera Active" if eval_d["overall_state"] == "DANGER"
            else ("Audible Horn Chime • Reduce Creep Speed" if eval_d["overall_state"] == "CAUTION"
            else "Maneuvering Clearance Verified")
        )
        step_trucks["Truck D"] = t_data_d

        # Fleet Aggregates for step
        danger_count = sum(1 for t_data in step_trucks.values() if t_data["risk"] == "DANGER")
        caution_count = sum(1 for t_data in step_trucks.values() if t_data["risk"] == "CAUTION")
        nominal_count = sum(1 for t_data in step_trucks.values() if t_data["risk"] == "NOMINAL")
        avg_speed = round(sum(t_data["speed_kmh"] for t_data in step_trucks.values()) / 4.0, 1)

        steps_data.append({
            "step": step,
            "total_steps": 50,
            "timestamp": f"T+{step * 2:03d}s",
            "kpis": {
                "active_units": 4,
                "fleet_avg_speed": avg_speed,
                "collision_alerts": danger_count,
                "caution_alerts": caution_count,
                "sensor_health_index": 100.0
            },
            "risk_summary": {
                "DANGER": danger_count,
                "CAUTION": caution_count,
                "NOMINAL": nominal_count
            },
            "trucks": step_trucks
        })

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "sample_data.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(steps_data, f, indent=2)

    print(f"Generated {len(steps_data)} calibrated steps with 4 trucks each in {out_file}")
    return steps_data

if __name__ == "__main__":
    generate_sample_data()
