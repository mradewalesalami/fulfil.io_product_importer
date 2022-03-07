def test_get_product(client):
    """
        GIVEN a Product model
        WHEN a Product is fetched
        THEN return the product as json response
    """

    client.post('/api/v1.0/products', json={
        "name": "name",
        "sku": "sku",
        "description": "description",
        "is_active": True
    })
    
    response = client.get('/api/v1.0/products/1')
    assert response.json['data']['name'] == 'name'
    assert response.json['data']['sku'] == 'sku'
    assert response.json['data']['description'] == 'description'
    assert response.json['data']['is_active'] is True
