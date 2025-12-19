from flask import Blueprint, request, jsonify
from mapping_service import MappingService
from harmonization_service import HarmonizationService
import logging
import json

main_bp = Blueprint('main', __name__, url_prefix='/api/v1')
logger = logging.getLogger(__name__)

@main_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'fhir-harmonization-service'}), 200

@main_bp.route('/map', methods=['POST'])
def map_data():
    """
    Accepts legacy JSON, returns FHIR Bundle.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        fhir_bundle = MappingService.map_legacy_to_fhir(data)
        # Parse back to dict for JSON response
        return jsonify(json.loads(fhir_bundle)), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in /map: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@main_bp.route('/harmonize', methods=['POST'])
def harmonize_data():
    """
    Accepts FHIR Bundle, returns Harmonized FHIR Bundle.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        harmonized_bundle = HarmonizationService.harmonize_bundle(data)
        return jsonify(json.loads(harmonized_bundle)), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in /harmonize: {e}")
        return jsonify({'error': 'Internal server error'}), 500
