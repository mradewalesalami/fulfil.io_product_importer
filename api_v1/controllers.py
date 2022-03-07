from flask import jsonify, request, current_app as app
from sqlalchemy.exc import IntegrityError
from . import v1_api_product_importer
from core.models import Product
from core import db
from helpers import (
    make_failure_response,
    make_success_response,
    make_delete_response,
    allowed_file_upload,
    make_pending_response,
    get_project_root,
    make_processing_response
)
from werkzeug.utils import secure_filename
import os
from sqlalchemy import and_
import requests
import json
from celery.result import AsyncResult


@v1_api_product_importer.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """
    Endpoint to retrieve a single product from the database.
    """
    
    product = Product.query.get(product_id)
    
    if product is None:
        return make_failure_response(message='Product with ID ({}) Not Found.'.format(product_id))
    
    data = {
        'id': product.id,
        'name': product.name,
        'sku': product.sku,
        'description': product.description,
        'is_active': product.is_active
    }
    
    return make_success_response(data)


@v1_api_product_importer.route('/products', methods=['POST'])
def add_product_from_json():
    """
    Endpoint to add a single product to the database.
    Payload Content-Type must be in format application/json.
    Endpoint overrides existing duplicates with same SKU.
    """
    
    if request.content_type != 'application/json':
        return make_failure_response(message='Invalid Content-Type in request headers. Only application/json is allowed.')
    
    payload = request.json
    
    name = payload['name'] if 'name' in payload and payload['name'] != '' or None else None
    sku = payload['sku'] if 'sku' in payload and payload['sku'] != '' or None else None
    description = payload['description'] if 'description' in payload and payload['description'] != '' or None else None
    is_active = True if 'is_active' in payload and payload['is_active'] is True else False
    
    if not all([name, sku, description]):
        return make_failure_response(message='Invalid or Missing Request Data')
    
    product = Product(
        name=name,
        sku=sku,
        description=description,
        is_active=is_active
    )
    
    db.session.add(product)
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        
        # If there is an existing duplicate, this overwrites the data.
        product = Product.query.filter(Product.sku == sku).first()
        product.name = name
        product.sku = sku
        product.description = description
        product.is_active = is_active
        
        db.session.add(product)
        db.session.commit()
        
        data = {
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'description': product.description,
            'is_active': product.is_active
        }
        
        return make_success_response(data)
    except:
        db.session.rollback()
        
        return make_failure_response(message='Product not added to Database')
    
    data = {
        'id': product.id,
        'name': product.name,
        'sku': product.sku,
        'description': product.description,
        'is_active': product.is_active
    }
    
    webhook_url = app.config['WEBHOOK_URL']
    headers = app.config['REQUEST_HEADER']
    
    requests.post(url=webhook_url, data=json.dumps(data), headers=headers)
    
    return make_success_response(data)


@v1_api_product_importer.route('/products/<product_id>', methods=['PATCH'])
def update_product(product_id):
    """
    Endpoint to update a single product in the database.
    Payload Content-Type must be in format application/json.
    """
    
    if request.content_type != 'application/json':
        return make_failure_response(message='Invalid Content-Type in request headers. Only application/json is allowed.')
    
    product = Product.query.get(product_id)
    
    if product is None:
        return make_failure_response(message='Product with ID ({}) Not Found.'.format(product_id))
    
    payload = request.json
    
    # Checking for payload fields to update and updating them accordingly.
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
        'id': product.id,
        'name': product.name,
        'sku': product.sku,
        'description': product.description,
        'is_active': product.is_active
    }
    
    webhook_url = app.config['WEBHOOK_URL']
    headers = app.config['REQUEST_HEADER']
    
    requests.patch(url=webhook_url, data=json.dumps(data), headers=headers)
    
    return make_success_response(data)


@v1_api_product_importer.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    Endpoint to delete a single product from the database.
    """
    
    product = Product.query.get(product_id)
    
    if product is None:
        return make_failure_response(message='Product with ID ({}) Not Found.'.format(product_id))
    
    db.session.delete(product)
    db.session.commit()
    
    return make_delete_response(message='SKU ({}) with ID ({}) Successfully Deleted.'.format(product.sku, product.id))


@v1_api_product_importer.route('/products', methods=['DELETE'])
def delete_all_products():
    """
    Endpoint to delete all products in the database.
    This endpoint uses a background task to handle deletion to cater for large database records that could take
    longer to delete.
    """
    
    # Triggering the background task to start deletion of all products in the database.
    from tasks import delete_all_products_from_db
    delete_all_products_from_db.delay()
    
    return make_processing_response(message='Processing deletion of all products.')


@v1_api_product_importer.route('/products/csv_upload', methods=['POST'])
def add_product_from_csv():
    """
    Endpoint to add products to the database using a csv file.
    This endpoint uses background task to handle csv product upload as this may contain large datasets that could
    take longer to upload.
    """
    
    # Checking if the form name file is present in the request object.
    if 'file' not in request.files:
        return make_failure_response(message='Invalid Request Data.')
    
    csv_file = request.files['file']
    
    # Checking if a file is uploaded
    if csv_file.filename == '':
        return make_failure_response(message='No file uploaded.')
    
    # Checking if the uploaded file is of an allowed format. Only csv files are allowed.
    if csv_file and not allowed_file_upload(csv_file.filename):
        return make_failure_response(message='Invalid file format uploaded.')
    
    filename = secure_filename(csv_file.filename)
    upload_folder = get_project_root()
    csv_file.save(os.path.join(upload_folder, filename))
    
    # Triggering the background task to start the upload in the background.
    from tasks import upload_product_from_csv_to_db
    result = upload_product_from_csv_to_db.delay(filename)
    
    # Metadata about the upload status to be returned when first uploaded.
    meta = {
        'upload_id': result.task_id,
        'upload_status': result.status,
        'upload_state': result.state
    }
    
    return make_processing_response(
        meta=meta,
        message='Processing data upload. Progress can be tracked using upload ID.'
    )


@v1_api_product_importer.route('/products/csv_upload/<upload_id>', methods=['GET'])
def get_csv_upload_status(upload_id):
    """
        Endpoint to track product upload to the database using a csv file.
        This endpoint takes the background task id created when at upload request and uses it to track progress.
    """
    
    # Calling the task and storing its reference
    result = AsyncResult(upload_id)
    
    # Checking upload status and return appropriate responses.
    if result.status == 'SUCCESS':
        data = []
        meta = {
            'upload_id': result.task_id,
            'upload_status': result.status,
            'upload_state': result.state
        }
        
        return make_success_response(data, meta=meta)
    
    if result.status == 'PENDING':
        meta = {
            'upload_id': result.task_id,
            'upload_status': result.status,
            'upload_state': result.state
        }
        
        return make_processing_response(meta=meta)
    
    if result.status == 'FAILURE':
        meta = {
            'upload_id': result.task_id,
            'upload_status': result.status,
            'upload_state': result.state
        }
        
        return make_failure_response(message='Upload Error.', meta=meta)
    
    return make_failure_response(message='Invalid Upload ID or Upload Status Unknown.')


@v1_api_product_importer.route('/products', methods=['GET'])
def get_all_products():
    """
    Endpoint to fetch all the products in the database and paginate the response and also filter the requested data
    by the product fields.
    """
    
    args = request.args
    
    # Checking if a particular filter criteria from the request data is present and filtering accordingly.
    filter_args = {key: value for key, value in args.items() if
                   value is not None and key != 'page' and key != 'per_page'}
    filtered_args = [getattr(Product, attribute) == value for attribute, value in filter_args.items()]
    
    page = args.get('page', 1, type=int)
    per_page = args.get('per_page', 20, type=int)
    
    # Paginated the response
    products = Product.query.filter(and_(*filtered_args)).paginate(page=page, per_page=per_page, error_out=False)
    
    data = [{
        'id': product.id,
        'name': product.name,
        'sku': product.sku,
        'description': product.description,
        'is_active': product.is_active
    } for product in products.items]
    
    # Meta data about the pagination
    meta = {
        'current_page': products.page,
        'previous_page': products.prev_num if products.has_prev else None,
        'next_page': products.next_num if products.has_next else None,
        'total_items': products.total,
        'total_pages': products.pages,
        'has_next_page': products.has_next,
        'has_previous_page': products.has_prev
    }
    
    return make_success_response(data, meta=meta)
