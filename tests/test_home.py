def test_home(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested with (GET)
    THEN return a welcome response
    """
    
    response = client.get('/')
    assert b'Welcome to Product Importer API v1.0' in response.data
    assert b'Welcome' in response.data
    assert b'Product Importer API v1.0' in response.data
    assert b'Product Importer' in response.data
    assert response.status_code == 200