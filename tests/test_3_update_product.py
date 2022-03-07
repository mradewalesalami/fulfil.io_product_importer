def test_update_product(client):
    """
        GIVEN a Product model
        WHEN a Product is updated
        THEN return the updated product as json response
    """

    client.post('/api/v1.0/products', json={
        "name": "name",
        "sku": "sku",
        "description": "description",
        "is_active": True
    })
    
    response = client.patch('/api/v1.0/products/1', json={
        "name": "name",
        "sku": "sku2",
        "description": "description",
        "is_active": True
    })
    
    assert response.json['data']['name'] == 'name'
    assert response.json['data']['sku'] == 'sku2'
    assert response.json['data']['description'] == 'description'
    assert response.json['data']['is_active'] is True
