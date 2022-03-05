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
    from api_v1 import v1_api_product_importer
    
    app.register_blueprint(v1_api_product_importer)


def create_app(configuration_mode):
    from configure import load_configuration
    from celery import make_celery
    
    app = Flask(__name__, instance_relative_config=True)
    
    load_configuration(app, configuration_mode)
    setup_blueprints(app)
    bind_home_url(app)
    db.init_app(app)
    migrate.init_app(app)
    
    celery = make_celery(app)
    
    with app.app_context():
        import api_v1
        
    return app, celery