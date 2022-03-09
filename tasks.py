import os

from dask import dataframe as dd
import pandas as pd
from flask import current_app as app

from app import celery
from core import db
from core.models import Product, Progress


@celery.task
def delete_all_products_from_db():
    """
    Query all the products in Database and delete.
    Then return a json response to Celery.
    """
    
    Product.query.delete()
    db.session.commit()


@celery.task(bind=True)
def upload_product_from_csv_to_db(self, data):
    """
    Using the dask library to read the uploaded csv file, loop through the file and keep the last occurrence of
    duplicate sku.
    This is more efficient that iterating through the database everytime for duplicate skus which still get
    overwritten anyway.
    """

    deduplicated_df = data.drop_duplicates(subset=['sku'], keep='last')
    
    """
    Loading all products in the database once into a dask dataframe object.
    This avoids expensive database operations of round trips to the database.
    """
    fetched_db_products = dd.read_sql_table(
        'products',
        app.config['SQLALCHEMY_DATABASE_URI'],
        'id',
        columns=['sku']
    ).compute()
    
    task_id = self.request.id
    total_uploads = len(deduplicated_df)
    task_progress = Progress(task_id=task_id, total=total_uploads)
    db.session.add(task_progress)
    db.session.commit()
    
    upload_done = 0
    
    """
    Loop through the csv file, check if any duplicates are there in the fetched database.
    If yes, we query the database for the duplicate product and overwrites it.
    if no, a new product is created and saved to the database.
    """
    for row in deduplicated_df.itertuples(name='Product'):
        if (row.sku == fetched_db_products['sku']).any():
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
        upload_done += 1
        upload_pending = total_uploads - upload_done
        progress = Progress.query.filter(Progress.task_id == task_id).first()
        progress.done = upload_done
        progress.pending = upload_pending
        db.session.add(progress)
        db.session.commit()
            
    # db.session.commit()
