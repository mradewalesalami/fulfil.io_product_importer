import os

from dask import dataframe as dd
from flask import current_app as app

from app import celery
from core import db
from core.models import Product
from helpers import get_project_root


@celery.task
def delete_all_products_from_db():
    Product.query.delete()
    db.session.commit()


@celery.task
def upload_product_from_csv_to_db(filename):
    file_root = get_project_root()
    file = os.path.join(file_root, filename)
    
    # Using the dask library to read the uploaded csv file, loop through the file and keep the last occurrence of
    # duplicate sku.
    # This is more efficient that iterating through the database everytime for duplicate skus which still get
    # overwritten anyway.
    df = dd.read_csv(file, converters={'sku': lambda v: v.lower()})
    dedupe_df = df.drop_duplicates(subset=['sku'], keep='last')
    
    # Loading all products in the database once into a dask dataframe object.
    # This avoids expensive database operations. We don't need to loop through all the items in the database to find a
    # duplicate in the database.
    existing_products = dd.read_sql_table('products', app.config['SQLALCHEMY_DATABASE_URI'], 'id',
                                          columns=['sku']).compute()
    
    # Loop through the csv file, check if any duplicates are there in the dataframe above.
    # If yes, we query the database for the duplicate product and overwrites it.
    # if no, a new product is created and saved to the database.
    for row in dedupe_df.itertuples(name='Product'):
        if (row.sku == existing_products['sku']).any():
            product = Product.query.filter(Product.sku == row.sku).first()
            product.name = row.name
            product.sku = row.sku
            product.description = row.description
            product.is_active = True if row.Index % 2 == 0 else False
            db.session.add(product)
        else:
            product = Product(
                name=row.name,
                sku=row.sku,
                description=row.description,
                is_active=True if row.Index % 2 == 0 else False
            )
            db.session.add(product)
    
    db.session.commit()
    
    # remove the csv file from file system after use to save disk space.
    os.remove(file)
