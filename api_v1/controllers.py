from flask import jsonify, request
from . import v1_api_product_importer
from core.models import Product
from core import db
from helpers import make_failure_response, make_success_response, make_delete_response


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


@v1_api_product_importer.route('/products/<product_id>', methods=['PATCH'])
def update_product(product_id):
    product = Product.query.get(product_id)
    
    if product is None:
        return make_failure_response(message='Product with ID ({}) Not Found.'.format(product_id))

    payload = request.json

    if 'name' in payload and payload['name'] != '' or None:
        product.name = payload['name']
    if 'sku' in payload and payload['sku'] != '' or None:
        product.sku = payload['sku']
    if 'description' in payload and payload['description'] != '' or None:
        product.description = payload['description']
    if 'is_active' in payload and payload['is_active'] is True:
        product.is_active = True
    elif 'is_active' in payload and payload['is_active'] is False:
        product.is_active = False
    
    db.session.add(product)
    db.session.commit()

    data = {
        'name': product.name,
        'sku': product.sku,
        'description': product.description,
        'is_active': product.is_active
    }
    
    return make_success_response(data)
    

@v1_api_product_importer.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    
    if product is None:
        return make_failure_response(message='Product with ID ({}) Not Found.'.format(product_id))
    
    db.session.delete(product)
    db.session.commit()
    
    return make_delete_response(message='SKU ({}) with ID ({}) Successfully Deleted.'.format(product.sku, product.id))


@v1_api_product_importer.route('/products', methods=['DELETE'])
def delete_all_products():
    from tasks import delete_all_products_from_db
    delete_all_products_from_db.delay()
    
    return make_delete_response(message='All Products Queued for Deletion. Deletion in progress.')


# @v1_api_product_importer.route('/', methods=['POST'])
# def add_product_from_csv():
#     payload = request.fil


# @v1_api_product_importer.route('/products', methods=['GET'])
# def get_all_products():
#     args = request.args
#     sku = args.get('sku') or ''
#     name = args.get('name') or ''
#     is_active = args.get('is_active') or ''
#     description = args.get('description') or ''
#
#     query = Product.query.filter().all()

#
# @v1_api_product_importer.route('/products', methods=['GET'])
# def get_product():
#     args = request.args
#     sku = args.get('sku') or None
#     name = args.get('name') or None
#     active = args.get('active') or None
#     description = args.get('description') or None
#
#     query = Product.query.filter_by(sku=sku, name=name, is_active=active, description=description).all()