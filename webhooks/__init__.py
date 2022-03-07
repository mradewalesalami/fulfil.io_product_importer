from flask import Blueprint

v1_api_webhook = Blueprint('v1_api_webhook', __name__, url_prefix='/api/v1.0')

from . import webhook