"""
MineBoard CAS Application Runner
Usage: python run.py
"""
import sys
from app import app

if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    print(f"Starting MineBoard CAS on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
