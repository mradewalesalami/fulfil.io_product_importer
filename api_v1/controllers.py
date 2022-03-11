import json
import os
from http import HTTPStatus as Status
from tempfile import gettempdir

import requests
from celery.result import AsyncResult
from flask import request, current_app as app
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from core import db
from core.models import Product, Progress
from helpers import (
    make_json_response,
    allowed_file_upload
)
from . import v1_api_product_importer

ALLOWED_POST_PAYLOAD_PARAMETERS = ['name', 'sku', 'description', 'is_active']


@v1_api_product_importer.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """
    Endpoint to retrieve a single product from the database.
    
    params: product ID
    
    returns: product as json
    """
    
    product = Product.query.get(product_id)
    
    if product is None:
        return make_json_response(
            http_status_code=Status.NOT_FOUND.value,
            status=Status.NOT_FOUND.phrase,
            message='Product not found'
        )
    
    data = {
        'id': product.id,
        'name': product.name,
        'sku': product.sku,
        'description': product.description,
        'is_active': product.is_active
    }
    
    return make_json_response(
        http_status_code=Status.OK.value,
        status=Status.OK.phrase,
        data=data,
        message='Successful'
    )


@v1_api_product_importer.route('/products', methods=['POST'])
def add_product_from_json():
    """
    Endpoint to add a single product to the database.
    Payload Content-Type must be in format application/json.
    Endpoint overrides existing duplicates with same SKU.
    
    returns: added product as json
    """
    
    """
    Request content type validation. Must be json format.
    """
    if request.content_type != 'application/json':
        return make_json_response(
            message='Invalid Content-Type in request headers. Only application/json is allowed',
            status=Status.FORBIDDEN.phrase,
            http_status_code=Status.FORBIDDEN.value
        )
    
    payload = request.json
    
    """
    Request parameter validation. Parameter must be in list of accepted parameters.
    Request parameter must not have an empty or null value.
    """
    for key in payload.keys():
        if key not in ALLOWED_POST_PAYLOAD_PARAMETERS:
            return make_json_response(
                message='Invalid request body: {}'.format(key),
                status=Status.BAD_REQUEST.phrase,
                http_status_code=Status.BAD_REQUEST.value
            )
        if key != 'is_active' and payload[key] == '' or None:
            return make_json_response(
                message='Missing values. No value for {}'.format(key),
                status=Status.BAD_REQUEST.phrase,
                http_status_code=Status.BAD_REQUEST.value
            )
    
    payload_keys = [key for key in payload.keys()]
    
    """
    Request body validation. name, sku, and description must be present in request keys.
    """
    if 'name' not in payload_keys or 'sku' not in payload_keys or 'description' not in payload_keys:
        return make_json_response(
            message='Missing request body',
            status=Status.BAD_REQUEST.phrase,
            http_status_code=Status.BAD_REQUEST.value
        )
    
    name = payload['name']
    sku = payload['sku']
    description = payload['description']
    is_active = True if 'is_active' in payload.keys() and payload['is_active'] is True else False
    
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
        
        """
        If there is an existing duplicate, overwrites the data.
        """
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
        
        return make_json_response(
            message='Successfully Created',
            status=Status.CREATED.phrase,
            http_status_code=Status.CREATED.value,
            data=data
        )
    
    except:
        """
        Catch every other exceptions.
        """
        db.session.rollback()
        
        return make_json_response(
            message='Product not added to database',
            status=Status.INTERNAL_SERVER_ERROR.phrase,
            http_status_code=Status.INTERNAL_SERVER_ERROR.value
        )
    
    data = {
        'id': product.id,
        'name': product.name,
        'sku': product.sku,
        'description': product.description,
        'is_active': product.is_active
    }
    
    """
    Trigger the webhook to send the created product details to an external URL.
    """
    webhook_url = app.config['WEBHOOK_URL']
    headers = app.config['REQUEST_HEADER']
    
    requests.post(url=webhook_url, data=json.dumps(data), headers=headers)
    
    return make_json_response(
        message='Successfully Created',
        status=Status.CREATED.phrase,
        http_status_code=Status.CREATED.value,
        data=data
    )


@v1_api_product_importer.route('/products/<product_id>', methods=['PATCH'])
def update_product(product_id):
    """
    Endpoint to update a single product in the database.
    Payload Content-Type must be in format application/json.
    
    params: product ID
    
    returns: updated product as json
    """
    
    """
    Request content type validation. Must be json format.
    """
    if request.content_type != 'application/json':
        return make_json_response(
            message='Invalid Content-Type in request headers. Only application/json is allowed',
            status=Status.FORBIDDEN.phrase,
            http_status_code=Status.FORBIDDEN.value
        )
    
    product = Product.query.get(product_id)
    
    if product is None:
        return make_json_response(
            http_status_code=Status.NOT_FOUND.value,
            status=Status.NOT_FOUND.phrase,
            message='Product not found'
        )
    
    payload = request.json
    
    """
    Request parameter validation. Parameter must be in list of accepted parameters.
    Request parameter must not have an empty or null value.
    """
    for key in payload.keys():
        if key not in ALLOWED_POST_PAYLOAD_PARAMETERS:
            return make_json_response(
                message='Invalid request body: {}'.format(key),
                status=Status.BAD_REQUEST.phrase,
                http_status_code=Status.BAD_REQUEST.value
            )
        """
        Validation of null values in request body.
        Fields are not nullable.
        """
        if key != 'is_active' and payload[key] is None:
            return make_json_response(
                message='Values cannot be null for {}'.format(key),
                status=Status.BAD_REQUEST.phrase,
                http_status_code=Status.BAD_REQUEST.value
            )
    
    payload_keys = [key for key in payload.keys()]
    
    """
    Checking for payload fields to update and updating them accordingly.
    """
    if 'name' in payload_keys and payload['name'] != '':
        product.name = payload['name']
    
    if 'sku' in payload_keys and payload['sku'] != '':
        product.sku = payload['sku']
    
    if 'description' in payload_keys and payload['description'] != '':
        product.description = payload['description']
    
    if 'is_active' in payload_keys and payload['is_active'] is True:
        product.is_active = True
    elif 'is_active' in payload_keys and payload['is_active'] is False:
        product.is_active = False
    
    db.session.add(product)
    
    try:
        db.session.commit()
    
    except IntegrityError:
        db.session.rollback()
        
        return make_json_response(
            message='Sku not unique',
            status=Status.BAD_REQUEST.phrase,
            http_status_code=Status.BAD_REQUEST.value
        )
    
    except:
        """
        Catch every other exceptions.
        """
        db.session.rollback()
        
        return make_json_response(
            message='Product not added to database',
            status=Status.INTERNAL_SERVER_ERROR.phrase,
            http_status_code=Status.INTERNAL_SERVER_ERROR.value
        )
    
    data = {
        'id': product.id,
        'name': product.name,
        'sku': product.sku,
        'description': product.description,
        'is_active': product.is_active
    }
    
    """
    Trigger the webhook to send the updated product details to an external URL.
    """
    webhook_url = app.config['WEBHOOK_URL']
    headers = app.config['REQUEST_HEADER']
    
    requests.patch(url=webhook_url, data=json.dumps(data), headers=headers)
    
    return make_json_response(
        message='Successfully Updated',
        status=Status.CREATED.phrase,
        http_status_code=Status.CREATED.value,
        data=data
    )


@v1_api_product_importer.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    Endpoint to delete a single product from the database.
    
    params: product ID
    
    returns: Deletion response
    """
    
    product = Product.query.get(product_id)
    
    if product is None:
        return make_json_response(
            http_status_code=Status.NOT_FOUND.value,
            status=Status.NOT_FOUND.phrase,
            message='Product not found'
        )
    
    db.session.delete(product)
    db.session.commit()
    
    return make_json_response(
        message='Successfully Deleted',
        status=Status.OK.phrase,
        http_status_code=Status.OK.value
    )


@v1_api_product_importer.route('/products', methods=['DELETE'])
def delete_all_products():
    """
    Endpoint to delete all products in the database.
    This endpoint uses a background task to handle deletion to cater for large database records that could take
    longer to delete.
    
    returns: Acknowledgement that deletion is processing
    """
    
    """
    Triggering the background task to start deletion of all products in the database.
    """
    
    from tasks import delete_all_products_from_db
    delete_all_products_from_db.delay()
    
    return make_json_response(
        message='Deletion in progress',
        status=Status.PROCESSING.phrase,
        http_status_code=Status.PROCESSING.value,
    )


@v1_api_product_importer.route('/products/csv_upload', methods=['POST'])
def add_product_from_csv():
    """
    Endpoint to add products to the database using a csv file.
    This endpoint uses background task to handle csv product upload as this may contain large datasets that could
    take longer to upload.
    
    returns: acknowledgement upload in progress
    """
    
    """
    Checking if the incoming upload is a csv file
    """
    if request.content_type != 'text/csv':
        return make_json_response(
            message='Only CSV file allowed',
            status=Status.UNSUPPORTED_MEDIA_TYPE.phrase,
            http_status_code=Status.UNSUPPORTED_MEDIA_TYPE.value
        )
    
    """
    Triggering the background task to start the upload in the background.
    """
    from tasks import upload_product_from_csv_to_db
    result = upload_product_from_csv_to_db.delay(request.data)
    
    """
    Metadata about the upload status to be returned when first uploaded.
    """
    meta = {
        'upload_id': result.task_id,
        'upload_status': result.status
    }
    
    return make_json_response(
        meta=meta,
        message='Upload in progress',
        status=Status.PROCESSING.phrase,
        http_status_code=Status.PROCESSING.value,
    )


@v1_api_product_importer.route('/products/csv_upload/<upload_id>', methods=['GET'])
def get_csv_upload_status(upload_id):
    """
    Endpoint to track product upload to the database using a csv file.
    This endpoint takes the background task id created when at upload request and uses it to track progress.

    params: upload id from the upload endpoint

    returns: progress of the upload
    """
    
    """
    Calling the task and storing its reference
    """
    result = AsyncResult(upload_id)
    
    progress = Progress.query.filter(Progress.task_id == upload_id).first()
    
    done = progress.done
    total = progress.total
    
    data = {
        'uploaded': done,
        'pending': progress.pending,
        'total': total,
        'progress': f'{int(int(done) / int(total) * 100)}% completed'
    }
    
    meta = {
        'status': result.status
    }
    
    return make_json_response(
        meta=meta,
        status=Status.OK.phrase,
        http_status_code=Status.OK.value,
        data=data
    )


@v1_api_product_importer.route('/products', methods=['GET'])
def get_all_products():
    """
    Endpoint to fetch all the products in the database and paginate the response and also filter the requested data
    by the product fields.
    
    returns: a paginated list of the all products
    """
    
    args = request.args
    
    """
    Checking if a particular filter criteria from the request data is present and filtering accordingly.
    """
    filter_args = {key: value for key, value in args.items() if
                   value is not None and key != 'page' and key != 'per_page'}
    
    filtered_args = [getattr(Product, attribute) == value for attribute, value in filter_args.items()]
    
    page = args.get('page', 1, type=int)
    per_page = args.get('per_page', 20, type=int)
    
    """
    Paginate the response
    """
    products = Product.query.filter(and_(*filtered_args)).paginate(page=page, per_page=per_page, error_out=False)
    
    data = [{
        'id': product.id,
        'name': product.name,
        'sku': product.sku,
        'description': product.description,
        'is_active': product.is_active
    } for product in products.items]
    
    """
    Meta data about the pagination
    """
    meta = {
        'current_page': products.page,
        'previous_page': products.prev_num if products.has_prev else None,
        'next_page': products.next_num if products.has_next else None,
        'total_items': products.total,
        'total_pages': products.pages,
        'has_next_page': products.has_next,
        'has_previous_page': products.has_prev
    }
    
    return make_json_response(
        message='Successful',
        data=data,
        meta=meta,
        status=Status.OK.phrase,
        http_status_code=Status.OK.value
    )


@v1_api_product_importer.route('/products/upload', methods=['POST'])
def upload():
    file = request.files['file']
    print('got file')
    filename = secure_filename(file.filename)
    print('secured file name')
    file.save(os.path.join(gettempdir(), filename))
    print('saved to ', gettempdir())
    from tasks import test_upload
    print('sending to task')
    test_upload.delay(filename)
    print('sent to task')
    
    return 'done'