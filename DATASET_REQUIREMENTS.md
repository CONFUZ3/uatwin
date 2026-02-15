# Manual Dataset Requirements

This document specifies the format and requirements for the manual dataset files that should be placed in `web_app/data/` directory.

## Required Files

### 1. Building Data: `buildings_manual.geojson`

**Location:** `web_app/data/buildings_manual.geojson`

**Format:** GeoJSON file with building footprints

**Required Properties:**
- **geometry**: Polygon or MultiPolygon in WGS84 (EPSG:4326) coordinate system
  - Coordinates should be in [longitude, latitude] format
  - Example: `[[-87.545, 33.210], [-87.544, 33.210], [-87.544, 33.211], [-87.545, 33.211], [-87.545, 33.210]]`

**Recommended Properties (will be used if present):**
- **name**: Building name (string)
  - Example: `"Gorgas Library"`
- **building_type**: Type of building (string)
  - Examples: `"academic"`, `"residential"`, `"library"`, `"stadium"`, `"student_center"`
- **purpose**: Building purpose/description (string)
  - Example: `"Main Library"`
- **height**: Building height in meters (number)
  - Example: `30.0`
- **color**: RGB color values [0-1] (array of 3 numbers)
  - Example: `[0.7, 0.7, 0.8]` for light gray

**Example GeoJSON Structure:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-87.545, 33.210],
          [-87.544, 33.210],
          [-87.544, 33.211],
          [-87.545, 33.211],
          [-87.545, 33.210]
        ]]
      },
      "properties": {
        "name": "Gorgas Library",
        "building_type": "library",
        "purpose": "Main Library",
        "height": 30.0,
        "color": [0.7, 0.7, 0.8]
      }
    }
  ]
}
```

**Notes:**
- If `height` is not provided, a default height of 15.0 meters will be used
- If `color` is not provided, a default color of `[0.7, 0.7, 0.8]` (light gray) will be used
- If `name` is not provided, buildings will be named "Building {index}"
- The coordinate system must be WGS84 (EPSG:4326). If your data is in a different CRS, convert it first.

---

### 2. Elevation Data: `elevation_manual.json`

**Location:** `web_app/data/elevation_manual.json`

**Format:** JSON file with elevation grid data

**Required Structure:**
```json
{
  "bounds": {
    "north": 33.220,
    "south": 33.200,
    "east": -87.530,
    "west": -87.560
  },
  "resolution": {
    "height": 100,
    "width": 100
  },
  "elevation": [
    [50.0, 51.0, 52.0, ...],
    [49.5, 50.5, 51.5, ...],
    ...
  ],
  "min_elevation": 45.0,
  "max_elevation": 55.0
}
```

**Required Fields:**
- **bounds**: Object with bounding box coordinates
  - `north`: Northern latitude (number)
  - `south`: Southern latitude (number)
  - `east`: Eastern longitude (number)
  - `west`: Western longitude (number)
- **resolution**: Object with grid dimensions
  - `height`: Number of rows in elevation grid (integer)
  - `width`: Number of columns in elevation grid (integer)
- **elevation**: 2D array of elevation values
  - Array of arrays, where each inner array represents a row
  - Values should be elevation in meters (numbers)
  - First row corresponds to southernmost latitude
  - First column corresponds to westernmost longitude
- **min_elevation**: Minimum elevation value in meters (number)
- **max_elevation**: Maximum elevation value in meters (number)

**Notes:**
- Elevation values should be in meters above sea level
- The grid should cover the same area as your building data
- For better performance, keep resolution reasonable (100x100 to 500x500 is recommended)
- Coordinates should match the bounding box in `config.json`

---

## Optional: Pre-processed Data

If you have already processed your data, you can also place these files directly:

- `buildings_raw.geojson` - Raw building data (will be used if `buildings_manual.geojson` is not found)
- `terrain.json` - Processed elevation data (will be used if `elevation_manual.json` is not found)

---

## Coordinate System

**All coordinates must be in WGS84 (EPSG:4326):**
- Latitude: -90 to 90 (degrees)
- Longitude: -180 to 180 (degrees)
- Format: `[longitude, latitude]` (note: longitude comes first)

---

## Data Quality Recommendations

1. **Building Footprints:**
   - Ensure polygons are closed (first and last coordinates should be the same)
   - Remove invalid geometries (self-intersecting polygons, etc.)
   - Simplify complex polygons if they have too many vertices (>1000) for better performance

2. **Elevation Data:**
   - Ensure elevation grid covers the entire campus area
   - Use consistent resolution (square grid recommended)
   - Remove any NaN or invalid values

3. **Metadata:**
   - Provide building names for better user experience
   - Include building types for visualization modes
   - Set appropriate heights for realistic 3D rendering

---

## Validation

After placing your dataset files, run:

```bash
python run_data_pipeline.py
```

This will:
1. Load your manual dataset files
2. Process and validate the data
3. Generate the required output files for the web application

If there are any format issues, error messages will indicate what needs to be fixed.

---

## Example Workflow

1. Prepare your building data as GeoJSON with required geometry
2. Prepare your elevation data as JSON with grid format
3. Place both files in `web_app/data/`:
   - `buildings_manual.geojson`
   - `elevation_manual.json`
4. Run the data pipeline:
   ```bash
   python run_data_pipeline.py
   ```
5. Check `web_app/data/` for generated output files
6. Start the web application

---

## Questions?

If you need help preparing your dataset or have questions about the format, please refer to:
- GeoJSON specification: https://geojson.org/
- WGS84 coordinate system: https://en.wikipedia.org/wiki/World_Geodetic_System

