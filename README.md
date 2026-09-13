# MineBoard — Autonomous Mining-Truck Fleet Collision Avoidance System (CAS)

A Flask-based dashboard for monitoring and preventing collisions in autonomous mining fleets. This project was built for the Smart India Hackathon (SIH).

## Features
- **Fleet Control Center**: Live 2D position map, KPI cards, risk distribution donut chart, and full telemetry table.
- **Driver In-Cab HUD**: Simulated AI camera view, hazard state banner, circular TTC gauge, and hover-reveal sensor tiles.
- **Simulation Engine**: 50-step precomputed dataset with 4 distinct truck scenarios (speeding, wet incline, gas leak, blind-spot pedestrian).
- **Asynchronous API**: Step, reset, and telemetry endpoints to update the UI without page reloads.

## Tech Stack
- **Backend**: Python, Flask, Jinja2
- **Frontend**: HTML, Tailwind CSS (via CDN), Vanilla JavaScript
- **Libraries**: Chart.js (charts), Lucide (icons)
- **Data**: 50-step x 4-truck JSON dataset

## How to Run Locally
1. Clone the repository: `git clone https://github.com/YourUsername/YourRepo.git`
2. Navigate into the folder: `cd final`
3. Install Flask: `pip install flask`
4. Run the app: `python run.py`
5. Open your browser to `http://localhost:5000`

## Project Structure
- `app.py`: Flask routes and API endpoints
- `calibration.py`: Safety thresholds and risk evaluation logic
- `generate_data.py`: Script to regenerate the simulation dataset
- `templates/`: Jinja2 HTML templates
- `static/`: CSS and JavaScript files
- `data/`: Precomputed `sample_data.json` telemetry file

- Made by https://github.com/ajaykumar25bev7072-hub [AJAY] and https://github.com/_______________________[HARINI].
