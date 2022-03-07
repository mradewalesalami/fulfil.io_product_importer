from . import v1_api_webhook
from flask import request, jsonify, abort, current_app as app
import requests
import json


@v1_api_webhook.route('/webhook', methods=['POST'])
def product_post_webhook():
    """
    Webhook for the create product endpoint.
    """
    # print('Received data: ', request.json)

    headers = app.config['REQUEST_HEADER']
    
    # When a new product is posted, this webhook is triggered.
    # What it does is to send the payload from the post endpoint to an external webhook site.
    requests.post(
        url='https://webhook.site/1f9bc4d0-5974-44ed-90b7-dfc93dacf56d',
        data=json.dumps(request.json),
        headers=headers
    )
    
    return 'success', 200


@v1_api_webhook.route('/webhook', methods=['PATCH'])
def product_patch_webhook():
    """
        Webhook for the update product endpoint.
    """
    # print('Received data: ', request.json)

    headers = app.config['REQUEST_HEADER']

    # When a new product is posted, this webhook is triggered.
    # What it does is to send the payload from the post endpoint to an external webhook site.
    requests.post(
        url='https://webhook.site/1f9bc4d0-5974-44ed-90b7-dfc93dacf56d',
        data=json.dumps(request.json),
        headers=headers
    )
    
    return 'success', 200