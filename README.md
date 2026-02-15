# University of Alabama Campus Digital Twin

A web-based digital twin prototype of the University of Alabama campus in Tuscaloosa, featuring 3D visualization, interactive building information, and data visualization capabilities.

## Overview

This project creates a comprehensive digital twin of the UA campus, allowing users to:
- Explore the campus in 3D
- View building information by clicking on structures
- Search and filter buildings
- Visualize data such as occupancy, energy usage, and building types
- Navigate with interactive camera controls

## Features

### 3D Visualization
- Full campus rendered in 3D with buildings and terrain
- Realistic lighting and shadows
- Smooth camera controls with orbit, zoom, and pan

### Interactive Features
- **Building Selection**: Click on any building to view detailed information
- **Search**: Search buildings by name, type, or purpose
- **Fly-to**: Automatically navigate to selected buildings
- **Visualization Modes**: 
  - Normal view with original building colors
  - Occupancy visualization (color-coded by occupancy levels)
  - Energy usage visualization (color-coded by energy consumption)
  - Building type visualization (color-coded by building category)

### Data Visualization
- Color-coded buildings based on selected metrics
- Interactive legend showing color meanings
- Real-time data updates (mock data for prototype)

## Project Structure

```
uatwin/
├── data_acquisition/          # Scripts to load and process manual datasets
│   ├── fetch_osm_data.py      # Load building footprints from manual dataset
│   ├── fetch_elevation_data.py # Load elevation data from manual dataset
│   ├── process_building_data.py # Enrich buildings with metadata
│   └── generate_building_heights.py # Estimate building heights
├── data_processing/            # Data processing and conversion
│   ├── convert_to_geojson.py  # Convert to optimized GeoJSON
│   ├── create_3d_models.py    # Generate 3D building models
│   ├── terrain_processor.py   # Process terrain data
│   └── export_gltf.py         # GLTF export (optional)
├── web_app/                   # Web application
│   ├── index.html             # Main HTML interface
│   ├── js/                    # JavaScript modules
│   │   ├── main.js            # Three.js scene setup
│   │   ├── buildings.js       # Building rendering and interaction
│   │   ├── ui.js              # UI controls and handlers
│   │   └── data_visualization.js # Data visualization features
│   ├── css/                   # Stylesheets
│   │   └── styles.css         # Main styles
│   └── data/                  # Processed data files
│       ├── buildings_3d.json # 3D building models
│       ├── terrain_mesh.json  # Terrain mesh data
│       └── building_metadata.json # Building metadata
├── backend/                   # Optional Flask backend
│   ├── app.py                # Flask application
│   └── api/                   # API endpoints
│       └── building_info.py   # Building information API
├── config.json               # Configuration file
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A modern web browser (Chrome, Firefox, Edge, Safari)

### Setup

1. **Clone or download the project**

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the project**
   - Edit `config.json` to adjust campus boundaries, building defaults, etc.
   - The default configuration is set for University of Alabama campus area

## Usage

### Preparing Your Dataset

Before running the pipeline, you need to prepare your manual dataset files:

1. **Prepare building data** as GeoJSON
   - Place your building footprints file at: `web_app/data/buildings_manual.geojson`
   - See `DATASET_REQUIREMENTS.md` for detailed format specifications

2. **Prepare elevation data** as JSON
   - Place your elevation data file at: `web_app/data/elevation_manual.json`
   - See `DATASET_REQUIREMENTS.md` for detailed format specifications

### Data Processing

Once your dataset files are in place, process the data:

1. **Load building data from manual dataset**
   ```bash
   python data_acquisition/fetch_osm_data.py
   ```

2. **Process and enrich building data**
   ```bash
   python data_acquisition/process_building_data.py
   ```

3. **Generate building heights**
   ```bash
   python data_acquisition/generate_building_heights.py
   ```

4. **Load elevation data from manual dataset**
   ```bash
   python data_acquisition/fetch_elevation_data.py
   ```

### Data Processing

Process the raw data into formats suitable for web visualization:

1. **Convert to optimized GeoJSON**
   ```bash
   python data_processing/convert_to_geojson.py
   ```

2. **Create 3D building models**
   ```bash
   python data_processing/create_3d_models.py
   ```

3. **Process terrain data**
   ```bash
   python data_processing/terrain_processor.py
   ```

### Running the Web Application

#### Quick Start

**Option 1: Upload via Web Interface (Recommended)**

1. **Start the Flask backend server**:
   ```bash
   python backend/app.py
   ```
   The API will be available at `http://127.0.0.1:5000`

2. **Start a local web server** for the frontend:
   ```bash
   cd web_app
   python -m http.server 8000
   ```
   Then open `http://localhost:8000` in your browser

3. **Upload your dataset files**:
   - Use the "Data Upload" section in the sidebar
   - Select your `buildings_manual.geojson` file (automatically uploads)
   - Select your `elevation_manual.json` file (automatically uploads)
   - Processing starts automatically when both files are uploaded
   - The scene will automatically reload after processing completes

**Option 2: Manual File Placement**

1. **Prepare your dataset files** (see `DATASET_REQUIREMENTS.md`)
   - Place `buildings_manual.geojson` in `web_app/data/`
   - Place `elevation_manual.json` in `web_app/data/`

2. **Run the data pipeline**:
   ```bash
   python run_data_pipeline.py
   ```
   This will load and process your manual dataset files.

3. **Start a local web server** (required for loading data files):
   ```bash
   cd web_app
   python -m http.server 8000
   ```
   Then open `http://localhost:8000` in your browser

#### File Upload Feature

The web application includes an automatic file upload and processing interface:
- **Automatic Upload**: Files are uploaded immediately when selected
- **Automatic Processing**: Data processing starts automatically when both files are uploaded
- **Automatic Reload**: The scene reloads automatically after processing completes

**To use the upload feature:**
1. Start the Flask backend: `python backend/app.py`
2. Open the web application in your browser
3. Navigate to the "Data Upload" section in the sidebar
4. Select your building data file (GeoJSON) - uploads automatically
5. Select your elevation data file (JSON) - uploads automatically
6. Processing begins automatically when both files are uploaded
7. The scene reloads with your new data when processing completes

**Note:** The upload feature requires the Flask backend to be running.

## Data Sources

### Manual Dataset
- Building footprints and elevation data are provided as manual datasets
- See `DATASET_REQUIREMENTS.md` for format specifications
- Building data should be provided as GeoJSON with building footprints
- Elevation data should be provided as JSON with elevation grid

### Building Metadata
- Building names, types, and purposes can be included in the GeoJSON properties
- The pipeline will process and enrich building data with metadata
- Default values will be used for missing properties (height, color, etc.)

## Configuration

Edit `config.json` to customize:

- **Campus boundaries**: Adjust the bounding box coordinates
- **Building defaults**: Set default heights, colors, etc.
- **Key buildings**: Specify priority buildings for detailed modeling
- **Data sources**: Enable/disable data sources

## Features in Detail

### Navigation Controls
- **Orbit**: Left-click and drag to rotate around the campus
- **Pan**: Right-click and drag (or middle mouse button) to pan
- **Zoom**: Scroll wheel to zoom in/out
- **Reset View**: Click "Reset View" button to return to default camera position

### Building Interaction
- **Click**: Click on any building to select it and view information
- **Hover**: Hover over buildings to see cursor change
- **Search**: Type in the search box to find buildings by name
- **Fly-to**: Clicking a search result or selecting a building will fly the camera to it

### Visualization Modes
- **Normal**: Original building colors
- **Occupancy**: Green (high), Yellow (medium), Red (low)
- **Energy**: Green (low), Orange (medium), Red (high)
- **Type**: Color-coded by building category

## Development

### Adding New Features

1. **New visualization mode**: Add to `data_visualization.js` and update UI
2. **New data source**: Create script in `data_acquisition/` and update processing pipeline
3. **New building metadata**: Update `process_building_data.py` with new data

### Extending the API

The Flask backend (`backend/app.py`) can be extended with:
- Real-time data endpoints
- Building analytics
- User preferences storage
- Authentication (if needed)

## Troubleshooting

### Data Not Loading
- Ensure your manual dataset files are placed in `web_app/data/`:
  - `buildings_manual.geojson`
  - `elevation_manual.json`
- Ensure all data processing scripts have been run
- Check that processed files exist in `web_app/data/`
- Check browser console for errors
- Use a local web server instead of opening HTML directly
- Verify your dataset format matches `DATASET_REQUIREMENTS.md`

### Buildings Not Visible
- Check that buildings are within the camera view
- Use "Reset View" button
- Verify building data was processed correctly

### Performance Issues
- Reduce number of buildings in your dataset
- Simplify terrain resolution in your elevation data
- Use lower quality settings in Three.js renderer
- Simplify building polygon geometries if they have too many vertices

## Future Enhancements

- Integration with real-time sensor data
- Detailed 3D models for key buildings (GLTF/GLB)
- Weather visualization
- Traffic and pedestrian flow visualization
- Energy consumption real-time data
- Occupancy sensors integration
- Mobile device support
- VR/AR viewing modes

## References

- Publication: [Developing campus digital twin using interactive visual analytics approach](https://link.springer.com/article/10.1007/s44243-024-00033-2)
- Three.js Documentation: https://threejs.org/docs/
- GeoJSON Specification: https://geojson.org/

## License

This project is a prototype for academic/research purposes.

## Contact

For questions or issues, please refer to the project supervisor or development team.

## Acknowledgments

- University of Alabama for campus data and inspiration
- Three.js community for excellent 3D web graphics library

