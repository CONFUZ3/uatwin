"""
Run the data pipeline:
1. Fetch 3D buildings from Overture Maps
2. Fetch trees from OpenStreetMap via OSMnx
"""

import subprocess
import sys
from pathlib import Path


def run_script(script_path, description):
    print(f"\n{'='*50}")
    print(f"  {description}")
    print(f"{'='*50}")

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"FAILED: {e.stdout}\n{e.stderr}")
        return False


def main():
    base = Path(__file__).parent

    steps = [
        (base / "data_acquisition" / "fetch_overture_buildings.py",
         "Fetching 3D buildings from Overture Maps"),
        (base / "data_acquisition" / "fetch_osmnx_trees.py",
         "Fetching trees from OpenStreetMap"),
    ]

    ok = 0
    for script, desc in steps:
        if run_script(script, desc):
            ok += 1

    print(f"\nPipeline: {ok}/{len(steps)} steps succeeded.")
    if ok == len(steps):
        print("Data ready! Start the web app:")
        print("  cd web_app && python -m http.server 8000")
    else:
        print("Some steps failed — check output above.")


if __name__ == "__main__":
    main()
