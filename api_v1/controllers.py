from flask import jsonify, request
from sqlalchemy.exc import IntegrityError
from . import v1_api_product_importer
from core.models import Product
from core import db
from helpers import make_failure_response, make_success_response, make_delete_response, allowed_file_upload, \
    make_pending_response, get_project_root
from werkzeug.utils import secure_filename
import os


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
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return make_failure_response(message='Duplicate SKU Detected. SKU Must Be Unique.')
    except:
        db.session.rollback()
        return make_failure_response(message='Product not added to Database')
    
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
    
    return make_pending_response(message='All Products Queued for Deletion. Deletion in progress.')


@v1_api_product_importer.route('/products/csv_upload', methods=['POST'])
def add_product_from_csv():
    if 'file' not in request.files:
        return make_failure_response(message='Invalid Request Data.')
    
    csv_file = request.files['file']
    
    if csv_file.filename == '':
        return make_failure_response(message='No file uploaded.')
    
    if csv_file and not allowed_file_upload(csv_file.filename):
        return make_failure_response(message='Invalid file format uploaded.')
    
    filename = secure_filename(csv_file.filename)
    upload_folder = get_project_root()
    csv_file.save(os.path.join(upload_folder, filename))
    
    from tasks import upload_product_from_csv_to_db
    upload_product_from_csv_to_db.delay(filename)
    
    return make_pending_response(message='Data Upload in Progress.')


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