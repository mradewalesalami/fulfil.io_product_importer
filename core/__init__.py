from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()


def setup_blueprints(app):
    from api_v1 import v1_api_product_importer
    app.register_blueprint(v1_api_product_importer)


def create_app(configuration_mode):
    from configure import load_configuration
    app = Flask(__name__, instance_relative_config=True)
    load_configuration(app, configuration_mode)
    setup_blueprints(app)
    db.init_app(app)
    migrate.init_app(app)
    
    with app.app_context():
        import api_v1
        from . import models
        return app