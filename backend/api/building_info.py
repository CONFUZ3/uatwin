"""
Building information API endpoints
(Can be expanded for more specific building queries)
"""

from flask import Blueprint, jsonify
import json
from pathlib import Path

building_info_bp = Blueprint('building_info', __name__)

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "web_app" / "data"

@building_info_bp.route('/search', methods=['GET'])
def search_buildings():
    """Search buildings by name, type, or purpose"""
    from flask import request
    
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({"error": "Query parameter 'q' required"}), 400
    
    try:
        buildings_path = DATA_DIR / "buildings_3d.json"
        if not buildings_path.exists():
            return jsonify({"error": "Buildings data not found"}), 404
        
        with open(buildings_path, 'r') as f:
            data = json.load(f)
        
        buildings = data.get('buildings', [])
        results = []
        
        for building in buildings:
            name = (building.get('name', '') or '').lower()
            purpose = (building.get('purpose', '') or '').lower()
            building_type = (building.get('type', '') or '').lower()
            
            if query in name or query in purpose or query in building_type:
                results.append({
                    'id': building.get('id'),
                    'name': building.get('name'),
                    'type': building.get('type'),
                    'purpose': building.get('purpose')
                })
        
        return jsonify({"results": results, "count": len(results)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

