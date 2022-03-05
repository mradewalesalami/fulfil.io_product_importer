"""
Blueprint to organize related views.
URL prefix will be used for all view implementing this blueprint.

E.g, in a view, the route will be in the below format
@v1_api_product_importer.route('/my_view')

The absolute url will become /api/v1.0/my_view
"""

from flask import Blueprint


v1_api_product_importer = Blueprint('v1_api_product_importer', __name__, url_prefix='/api/v1.0')


from . import controllers