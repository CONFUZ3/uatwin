import os
from pathlib import Path

data_dir = Path("e:/cursor/uatwin/web_app/data")
files = ["ua_trees.geojson", "ua_buildings.geojson"]

for f in files:
    p = data_dir / f
    if p.exists():
        size_mb = p.stat().st_size / (1024 * 1024)
        print(f"{f}: Found, {size_mb:.2f} MB")
    else:
        print(f"{f}: Not Found")
