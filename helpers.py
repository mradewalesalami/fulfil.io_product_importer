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


def make_json_response(data=None, message=None, http_status_code=None, status=None, meta=None):
    """
     Generally, all responses will be in the following format:
        "status": [string],  // HTTP status phrase for the appropriate status code
        "message": [string], // Entirely informational.
        "data": [object]    // contains actionable result of processing if present
        
    params:
        data - This is the response data if any
        message - Entirely Informational
        http_status_code - HTTP status code to send to the client
        status - HTTP status phrase for the appropriate status code
        meta - metadata sent along with the response if any
        
    returns: json response
    """
    
    response = {
        'status': status,
        'status_code': http_status_code
    }
    
    if data is not None:
        response.update(data=data)

    if message is not None:
        response.update(message=message)

    if meta is not None:
        response.update(meta=meta)
        
    return jsonify(response)