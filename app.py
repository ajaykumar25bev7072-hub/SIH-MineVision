"""
MineBoard — Autonomous Mining-Truck Fleet Collision Avoidance System (CAS)
Flask Backend Application
"""

import json
import os
from flask import Flask, render_template, session, jsonify, request, abort

app = Flask(__name__)
app.secret_key = os.environ.get("MINEBOARD_SECRET_KEY", "mineboard_cas_sih_hackathon_super_secret_key_2024")

# Load precomputed 50-step x 4-truck simulation dataset
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "sample_data.json")

def load_simulation_data():
    if not os.path.exists(DATA_FILE):
        # Auto-generate if missing
        import generate_data
        generate_data.generate_sample_data()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

DATASET = load_simulation_data()
TOTAL_STEPS = len(DATASET)

def get_current_step_index():
    """Retrieve and validate the active step index from Flask session."""
    step = session.get("current_step", 0)
    if not isinstance(step, int) or step < 0 or step >= TOTAL_STEPS:
        step = 0
        session["current_step"] = 0
    return step

def get_telemetry_payload(step_idx):
    """Build telemetry JSON response including step data and trailing history."""
    step_data = DATASET[step_idx]
    # Trailing history up to current step for line charts
    history = [
        {
            "step": s["step"],
            "timestamp": s["timestamp"],
            "trucks": {
                tid: {
                    "distance_m": s["trucks"][tid]["distance_m"],
                    "speed_kmh": s["trucks"][tid]["speed_kmh"],
                    "gas_ppm": s["trucks"][tid]["gas_ppm"],
                    "risk": s["trucks"][tid]["risk"]
                }
                for tid in s["trucks"]
            }
        }
        for s in DATASET[:step_idx + 1]
    ]

    return {
        "step": step_idx,
        "total_steps": TOTAL_STEPS,
        "timestamp": step_data["timestamp"],
        "kpis": step_data["kpis"],
        "risk_summary": step_data["risk_summary"],
        "trucks": step_data["trucks"],
        "history": history
    }

# ==========================================
# PAGE ROUTES
# ==========================================

@app.route("/")
def index():
    """Page 1: Fleet Controller overview (data-rich overview across all 4 trucks)."""
    step_idx = get_current_step_index()
    current_telemetry = DATASET[step_idx]
    return render_template(
        "index.html",
        current_step=step_idx,
        total_steps=TOTAL_STEPS,
        current_telemetry=current_telemetry,
        active_page="fleet"
    )

@app.route("/truck/<truck_id>")
def truck_view(truck_id):
    """Page 2: Driver In-Cab cockpit view (visual-first, minimal text per truck)."""
    step_idx = get_current_step_index()
    current_telemetry = DATASET[step_idx]
    
    # Normalize and validate truck_id
    valid_trucks = current_telemetry.get("trucks", {})
    matched_id = None
    for tid in valid_trucks:
        if tid.lower() == truck_id.lower():
            matched_id = tid
            break

    if not matched_id:
        abort(404, description=f"Vehicle '{truck_id}' not recognized in autonomous fleet.")

    truck_data = valid_trucks[matched_id]
    return render_template(
        "truck.html",
        current_step=step_idx,
        total_steps=TOTAL_STEPS,
        truck_id=matched_id,
        truck=truck_data,
        current_telemetry=current_telemetry,
        active_page=matched_id
    )

# ==========================================
# SIMULATION API ENDPOINTS
# ==========================================

@app.route("/api/step", methods=["POST"])
def step_forward():
    """
    Advances simulation step forward by 1 in Flask session (loops at 50).
    Returns new telemetry slice as JSON without full page refresh.
    """
    current_idx = get_current_step_index()
    next_idx = (current_idx + 1) % TOTAL_STEPS
    session["current_step"] = next_idx
    session.modified = True
    return jsonify(get_telemetry_payload(next_idx))

@app.route("/api/reset", methods=["POST"])
def reset_simulation():
    """
    Resets simulation session back to step 0 for instant demo replay.
    """
    session["current_step"] = 0
    session.modified = True
    return jsonify(get_telemetry_payload(0))

@app.route("/api/telemetry", methods=["GET"])
def get_telemetry():
    """
    Returns the current step's telemetry slice as JSON.
    """
    step_idx = get_current_step_index()
    return jsonify(get_telemetry_payload(step_idx))

@app.route("/api/calibration", methods=["GET"])
def get_calibration():
    """
    Returns the flight control safety & sensor recalibration matrix specification.
    """
    try:
        import calibration
        matrix = calibration.RECALIBRATION_MATRIX
    except ImportError:
        matrix = {}
    return jsonify({
        "status": "CALIBRATED",
        "firmware_version": "v2.4-RECAL",
        "matrix": matrix
    })

if __name__ == "__main__":
    # Launch locally on port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
