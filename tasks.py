from app import celery
from core import db
from core.models import Product
from dask import dataframe as dd
import os
from helpers import get_project_root
from flask import current_app as app


@celery.task
def delete_all_products_from_db():
    Product.query.delete()
    db.session.commit()


@celery.task
def upload_product_from_csv_to_db(filename):
    file_root = get_project_root()
    file = os.path.join(file_root, filename)
    df = dd.read_csv(file, converters={'sku': lambda v: v.lower()})
    dedupe_df = df.drop_duplicates(subset=['sku'], keep='last')
    
    existing_products = dd.read_sql_table('products', app.config['SQLALCHEMY_DATABASE_URI'], 'id',
                                          columns=['sku']).compute()
    
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
    os.remove(file)
