"""
Flask backend API for UA Campus Digital Twin
Serves building data and handles API requests
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import sys
import subprocess
from pathlib import Path
from werkzeug.utils import secure_filename

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Try to register blueprints if available
try:
    from backend.api.building_info import building_info_bp
    app.register_blueprint(building_info_bp, url_prefix='/api/buildings')
except ImportError:
    pass  # Blueprint not available, continue without it

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "web_app" / "data"

@app.route('/')
def index():
    """Redirect to web app"""
    return jsonify({"message": "UA Campus Digital Twin API", "version": "1.0"})

@app.route('/api/buildings', methods=['GET'])
def get_buildings():
    """Get all buildings data"""
    try:
        buildings_path = DATA_DIR / "buildings_3d.json"
        if buildings_path.exists():
            with open(buildings_path, 'r') as f:
                data = json.load(f)
            return jsonify(data)
        else:
            return jsonify({"error": "Buildings data not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/buildings/<building_id>', methods=['GET'])
def get_building(building_id):
    """Get specific building data"""
    try:
        buildings_path = DATA_DIR / "buildings_3d.json"
        if buildings_path.exists():
            with open(buildings_path, 'r') as f:
                data = json.load(f)
            
            building = next((b for b in data.get('buildings', []) if b.get('id') == building_id), None)
            if building:
                return jsonify(building)
            else:
                return jsonify({"error": "Building not found"}), 404
        else:
            return jsonify({"error": "Buildings data not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    """Get building metadata"""
    try:
        metadata_path = DATA_DIR / "building_metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                data = json.load(f)
            return jsonify(data)
        else:
            return jsonify({"error": "Metadata not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/terrain', methods=['GET'])
def get_terrain():
    """Get terrain data"""
    try:
        terrain_path = DATA_DIR / "terrain_mesh.json"
        if terrain_path.exists():
            with open(terrain_path, 'r') as f:
                data = json.load(f)
            return jsonify(data)
        else:
            return jsonify({"error": "Terrain data not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get campus statistics"""
    try:
        buildings_path = DATA_DIR / "buildings_3d.json"
        stats = {
            "total_buildings": 0,
            "total_area": 0,
            "average_height": 0
        }
        
        if buildings_path.exists():
            with open(buildings_path, 'r') as f:
                data = json.load(f)
            
            buildings = data.get('buildings', [])
            stats["total_buildings"] = len(buildings)
            
            if buildings:
                heights = [b.get('height', 0) for b in buildings if b.get('height')]
                if heights:
                    stats["average_height"] = sum(heights) / len(heights)
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads for building or elevation data"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        file_type = request.form.get('type', '')
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file_type not in ['buildings', 'elevation']:
            return jsonify({"error": "Invalid file type. Must be 'buildings' or 'elevation'"}), 400
        
        # Validate file extension
        filename = secure_filename(file.filename)
        if file_type == 'buildings':
            if not (filename.endswith('.geojson') or filename.endswith('.json')):
                return jsonify({"error": "Building file must be .geojson or .json"}), 400
            save_path = DATA_DIR / "buildings_manual.geojson"
        else:  # elevation
            if not filename.endswith('.json'):
                return jsonify({"error": "Elevation file must be .json"}), 400
            save_path = DATA_DIR / "elevation_manual.json"
        
        # Ensure data directory exists
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file.save(str(save_path))
        
        return jsonify({
            "success": True,
            "message": f"{file_type} file uploaded successfully",
            "filename": filename
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_data():
    """Process uploaded data files using the data pipeline"""
    try:
        # Check if required files exist
        buildings_file = DATA_DIR / "buildings_manual.geojson"
        elevation_file = DATA_DIR / "elevation_manual.json"
        
        if not buildings_file.exists():
            return jsonify({"error": "Building data file not found. Please upload buildings_manual.geojson"}), 400
        
        if not elevation_file.exists():
            return jsonify({"error": "Elevation data file not found. Please upload elevation_manual.json"}), 400
        
        # Run the data pipeline
        pipeline_script = BASE_DIR / "run_data_pipeline.py"
        
        if not pipeline_script.exists():
            return jsonify({"error": "Data pipeline script not found"}), 500
        
        # Run pipeline as subprocess
        result = subprocess.run(
            [sys.executable, str(pipeline_script)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Unknown error"
            return jsonify({
                "success": False,
                "error": f"Pipeline failed: {error_msg}"
            }), 500
        
        return jsonify({
            "success": True,
            "message": "Data processed successfully",
            "output": result.stdout
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Data processing timed out"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting UA Campus Digital Twin API server...")
    print(f"Data directory: {DATA_DIR}")
    app.run(debug=True, port=5000, host='127.0.0.1')

