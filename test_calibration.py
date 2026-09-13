"""
Verification Suite for Flight Control & Safety Recalibration Matrix
Validates exact boundary conditions for all 8 governed parameters.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calibration

def test_boundaries():
    print("--- 1. OBSTACLE DISTANCE (d) ---")
    assert calibration.eval_obstacle_distance(10.1)[0] == 0, "10.1m must be SAFE [0]"
    assert calibration.eval_obstacle_distance(10.0)[0] == 1, "10.0m boundary must be CAUTION [1]"
    assert calibration.eval_obstacle_distance(7.5)[0] == 1, "7.5m must be CAUTION [1]"
    assert calibration.eval_obstacle_distance(5.0)[0] == 1, "5.0m boundary must be CAUTION [1]"
    assert calibration.eval_obstacle_distance(4.9)[0] == 2, "4.9m must be DANGER [2]"
    print("  [PASS] Obstacle Distance boundary checks passed.")

    print("--- 2. TIME-TO-COLLISION (TTC) ---")
    assert calibration.eval_time_to_collision(10.1)[0] == 0, "10.1s must be SAFE [0]"
    assert calibration.eval_time_to_collision(10.0)[0] == 1, "10.0s boundary must be CAUTION [1]"
    assert calibration.eval_time_to_collision(7.5)[0] == 1, "7.5s must be CAUTION [1]"
    assert calibration.eval_time_to_collision(5.0)[0] == 1, "5.0s boundary must be CAUTION [1]"
    assert calibration.eval_time_to_collision(4.9)[0] == 2, "4.9s must be DANGER [2]"
    print("  [PASS] Time-to-Collision boundary checks passed.")

    print("--- 3. VEHICLE SPEED (v) ---")
    assert calibration.eval_vehicle_speed(9.9)[0] == 0, "9.9 km/h must be SAFE [0]"
    assert calibration.eval_vehicle_speed(10.0)[0] == 1, "10.0 km/h boundary must be CAUTION [1]"
    assert calibration.eval_vehicle_speed(12.5)[0] == 1, "12.5 km/h must be CAUTION [1]"
    assert calibration.eval_vehicle_speed(15.0)[0] == 1, "15.0 km/h boundary must be CAUTION [1]"
    assert calibration.eval_vehicle_speed(15.1)[0] == 2, "15.1 km/h must be DANGER [2]"
    print("  [PASS] Vehicle Speed boundary checks passed.")

    print("--- 4. RELATIVE CLOSING SPEED (v_rel) ---")
    assert calibration.eval_relative_closing_speed(0.9)[0] == 0, "0.9 m/s must be SAFE [0]"
    assert calibration.eval_relative_closing_speed(1.0)[0] == 1, "1.0 m/s boundary must be CAUTION [1]"
    assert calibration.eval_relative_closing_speed(1.5)[0] == 1, "1.5 m/s must be CAUTION [1]"
    assert calibration.eval_relative_closing_speed(2.0)[0] == 1, "2.0 m/s boundary must be CAUTION [1]"
    assert calibration.eval_relative_closing_speed(2.1)[0] == 2, "2.1 m/s must be DANGER [2]"
    print("  [PASS] Relative Closing Speed boundary checks passed.")

    print("--- 5. RELATIVE HUMIDITY (RH) ---")
    assert calibration.eval_relative_humidity(79.9)[0] == 0, "79.9% must be SAFE [0]"
    assert calibration.eval_relative_humidity(80.0)[0] == 1, "80.0% boundary must be CAUTION [1]"
    assert calibration.eval_relative_humidity(85.0)[0] == 1, "85.0% must be CAUTION [1]"
    assert calibration.eval_relative_humidity(90.0)[0] == 1, "90.0% boundary must be CAUTION [1]"
    assert calibration.eval_relative_humidity(90.1)[0] == 2, "90.1% must be DANGER [2]"
    print("  [PASS] Relative Humidity boundary checks passed.")

    print("--- 6. MOISTURE / PRECIPITATION (YL-83) ---")
    assert calibration.eval_moisture_precipitation(False)[0] == 0, "Dry must be SAFE [0]"
    assert calibration.eval_moisture_precipitation(True, False)[0] == 1, "Rain detected must be CAUTION [1]"
    assert calibration.eval_moisture_precipitation(True, True)[0] == 2, "Heavy rain must be DANGER [2]"
    print("  [PASS] Moisture / Precipitation boundary checks passed.")

    print("--- 7. GAS CONCENTRATION (MQ-2 ADC) ---")
    assert calibration.eval_gas_concentration(299.0)[0] == 0, "299 PPM must be SAFE [0]"
    assert calibration.eval_gas_concentration(300.0)[0] == 1, "300 PPM boundary must be CAUTION [1]"
    assert calibration.eval_gas_concentration(400.0)[0] == 1, "400 PPM must be CAUTION [1]"
    assert calibration.eval_gas_concentration(500.0)[0] == 1, "500 PPM boundary must be CAUTION [1]"
    assert calibration.eval_gas_concentration(501.0)[0] == 2, "501 PPM must be DANGER [2]"
    print("  [PASS] Gas Concentration (MQ-2) boundary checks passed.")

    print("--- 8. BLINDSPOT MOTION (HC-SR501 PIR) ---")
    assert calibration.eval_blindspot_motion(False, 3.0)[0] == 0, "No motion must be SAFE [0]"
    assert calibration.eval_blindspot_motion(True, 10.0)[0] == 1, "Motion at 10m must be CAUTION [1]"
    assert calibration.eval_blindspot_motion(True, 5.0)[0] == 1, "Motion at 5.0m boundary must be CAUTION [1]"
    assert calibration.eval_blindspot_motion(True, 4.9)[0] == 2, "Motion at 4.9m (<5m) must be DANGER [2]"
    print("  [PASS] Blindspot Motion boundary checks passed.")

    print("\n========================================================")
    print("ALL 8 CALIBRATION MATRIX BOUNDARY CHECKS PASSED (100%)")
    print("========================================================")

if __name__ == "__main__":
    test_boundaries()
