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
    """
    This function checks if the uploaded file is a csv file or return an error.
    """
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_FILE_EXTENSIONS


def make_failure_response(message, meta=None):
    """
    This is a helper function to return a failure response.
    """
    
    response = {
        'status': 'FAILURE',
        'error': {
            'message': message
        }
    }
    
    if meta is not None:
        response.update(meta=meta)
    
    return jsonify(response)


def make_success_response(response_data, meta=None):
    """
        This is a helper function to return a success response.
    """
    
    response = {
        'status': 'SUCCESS',
        'data': response_data
    }
    
    if meta is not None:
        response.update(meta=meta)
        
    return jsonify(response)


def make_delete_response(message):
    """
        This is a helper function to return delete response.
    """
    
    response = {
        'status': 'SUCCESS',
        'info': {
            'message': message
        }
    }
    
    return jsonify(response)


def make_pending_response(message, meta=None):
    """
        This is a helper function to return a pending response.
    """
    
    response = {
        'status': 'PENDING',
        'info': {
            'message': message
        }
    }

    if meta is not None:
        response.update(meta=meta)
    
    return jsonify(response)


def make_processing_response(message=None, meta=None):
    """
        This is a helper function to return progress update response for background tasks still processing.
    """
    
    response = {
        'status': 'PROCESSING'
    }
    
    if meta is not None:
        response.update(meta=meta)
        
    if message is not None:
        response.update(message=message)
    
    return jsonify(response)