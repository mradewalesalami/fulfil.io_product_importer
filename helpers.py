import os
from flask import jsonify


def get_project_root():
    """
    Helper function to get the project root
    :return: project root dir name
    """
    return os.path.dirname(__file__)


def make_failure_response(message):
    response = {
        'status': 'FAILURE',
        'error': {
            'message': message,
            'payload_example': {
                "name": "name",
                "sku": "sku",
                "description": "description",
                "is_active": "true or false"
            }
        }
    }
    return jsonify(response)


def make_success_response(response_data):
    response = {
        'status': 'SUCCESS',
        'data': [response_data]
    }
    return jsonify(response)
