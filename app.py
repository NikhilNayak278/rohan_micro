import os
import logging
from flask import Flask
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Register Blueprints
    from routes import main_bp
    app.register_blueprint(main_bp)

    logger.info(f"FHIR Harmonization Service initialized in {config_name} mode")
    
    # Print all registered routes
    logger.info("Registered Routes:")
    for rule in app.url_map.iter_rules():
        logger.info(f"{rule} -> {rule.endpoint}")
        
    @app.route('/test', methods=['GET'])
    def test_route():
        return "Test Route OK", 200
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=app.config['PORT'])
