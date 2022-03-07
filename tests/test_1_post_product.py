def test_post_product(client):
    """
        GIVEN a Product model
        WHEN a new Product is created
        THEN return the new product as json response
    """
    
    response = client.post('/api/v1.0/products', json={
        "name": "name",
        "sku": "sku",
        "description": "description",
        "is_active": True
    })
    
    assert response.json['data']['name'] == 'name'
    assert response.json['data']['sku'] == 'sku'
    assert response.json['data']['description'] == 'description'
    assert response.json['data']['is_active'] is True
