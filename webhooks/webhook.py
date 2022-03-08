import json

import requests
from flask import request, current_app as app

from . import v1_api_webhook


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
        url='https://webhook.site/092c1398-3e5a-4a66-aee2-0dc8738f8aeb',
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
        url='https://webhook.site/092c1398-3e5a-4a66-aee2-0dc8738f8aeb',
        data=json.dumps(request.json),
        headers=headers
    )
    
    return 'success', 200
