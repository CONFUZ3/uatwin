import json
from pathlib import Path

def validate_geojson(path):
    print(f"Validating {path}...")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "type" not in data or data["type"] != "FeatureCollection":
            print("❌ Invalid GeoJSON: Root type must be FeatureCollection")
            return
            
        if "features" not in data:
            print("❌ Invalid GeoJSON: Missing 'features' key")
            return
            
        count = len(data["features"])
        print(f"✅ Valid GeoJSON with {count} features.")
        if count > 0:
            print("Sample feature properties:", data["features"][0].get("properties", {}))
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

validate_geojson("e:/cursor/uatwin/web_app/data/ua_buildings.geojson")
validate_geojson("e:/cursor/uatwin/web_app/data/ua_trees.geojson")
