def test_update_product(client):
    """
        GIVEN a Product model
        WHEN a Product is deleted
        THEN return the deletion update
    """

    client.post('/api/v1.0/products', json={
        "name": "name",
        "sku": "sku",
        "description": "description",
        "is_active": True
    })
    
    response = client.delete('/api/v1.0/products/1')
    assert 'Successfully Deleted' in response.json['info']['message']
