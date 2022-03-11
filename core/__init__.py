from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()


def bind_home_url(app):
    """
    A home URL endpoint to test API endpoint is working.
    
    returns: A welcome message
    """
    
    @app.route('/')
    @app.route('/api/v1.0')
    def index():
        return 'Welcome to Product Importer API v1.0'
    

def setup_blueprints(app):
    """
    Helper function to set up blueprint.
    ALl blueprints will be registered here.
    """
    
    from api_v1 import v1_api_product_importer
    from webhooks import v1_api_webhook
    
    app.register_blueprint(v1_api_product_importer)
    app.register_blueprint(v1_api_webhook)


def create_app(configuration_mode):
    """
    The flask app application factory.
    All integrations and extensions are initialized in this factory.
    
    params: configuration mode
    
    returns: the flask app instance
    """
    
    from configure import load_configuration
    
    app = Flask(__name__, instance_relative_config=True)
    
    # Setting up all extensions.
    load_configuration(app, configuration_mode)
    setup_blueprints(app)
    bind_home_url(app)
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        import api_v1
        import webhooks
        # db.create_all()
        
    return app
