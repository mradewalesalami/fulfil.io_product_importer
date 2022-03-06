from flask import jsonify, request
from . import v1_api_product_importer
from core.models import Product
from core import db
from helpers import make_failure_response, make_success_response


@v1_api_product_importer.route('/products', methods=['POST'])
def add_product_from_json():
    payload = request.json
    
    name = payload['name'] if 'name' in payload and payload['name'] != '' or None else None
    sku = payload['sku'] if 'sku' in payload and payload['sku'] != '' or None else None
    description = payload['description'] if 'description' in payload and payload['description'] != '' or None else None
    is_active = True if 'is_active' in payload and payload['is_active'] is True else False
    
    if not all([name, sku, description]):
        return make_failure_response(message='Invalid or Missing Request Data')
        
    product = Product(name=name, sku=sku, description=description, is_active=is_active)
    db.session.add(product)
    db.session.commit()
    data = {
        'name': product.name,
        'sku': product.sku,
        'description': product.description,
        'is_active': product.is_active
    }
    return make_success_response(data)
    
    
# @v1_api_product_importer.route('/products', methods=['GET'])
# def get_all_products():
#     args = request.args
#     sku = args.get('sku') or None
#     name = args.get('name') or None
#     is_active = args.get('is_active') or None
#     description = args.get('description') or None
#
#     query = Product.query.filter().all()
#
#
#
# #
# @v1_api_product_importer.route('/products', methods=['GET'])
# def get_product():
#     args = request.args
#     sku = args.get('sku') or None
#     name = args.get('name') or None
#     active = args.get('active') or None
#     description = args.get('description') or None
#
#     query = Product.query.filter_by(sku=sku, name=name, is_active=active, description=description).all()