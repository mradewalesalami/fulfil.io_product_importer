import os
from flask import jsonify

ALLOWED_FILE_EXTENSIONS = {'csv'}


def get_project_root():
    """
    Helper function to get the project root
    :return: project root dir name
    """
    return os.path.dirname(__file__)


def allowed_file_upload(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_FILE_EXTENSIONS


def make_failure_response(message):
    response = {
        'status': 'FAILURE',
        'error': {
            'message': message
        }
    }
    return jsonify(response)


def make_success_response(response_data):
    response = {
        'status': 'SUCCESS',
        'data': [response_data]
    }
    return jsonify(response)


def make_delete_response(message):
    response = {
        'status': 'SUCCESS',
        'info': {
            'message': message
        }
    }
    return jsonify(response)


def make_pending_response(message):
    response = {
        'status': 'PENDING',
        'info': {
            'message': message
        }
    }
    return jsonify(response)