import os
import random

import pandas as pd
from flask import current_app as app

from app import celery
from core import db
from core.models import Product, Progress

STATE = [True, False]


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
    fetched_db_products = pd.read_sql_table(
        'products',
        app.config['SQLALCHEMY_DATABASE_URI'],
        index_col='id',
        columns=['sku']
    ).to_dict()
    
    """
    Tracking the task metadata
    """
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
    for row in deduplicated_df.itertuples(name='Product', index=False):
        data = {
            'name': row.name,
            'sku': row.sku,
            'description': row.description,
            'is_active': random.choice(STATE)
        }
        if row.sku in fetched_db_products['sku'].values():
            overwrite_db.delay(data)
        else:
            add_to_db.delay(data)
        upload_done += 1
        upload_pending = total_uploads - upload_done
        progress = Progress.query.filter(Progress.task_id == task_id).first()
        progress.done = upload_done
        progress.pending = upload_pending
        db.session.add(progress)
        db.session.commit()


@celery.task
def add_to_db(data):
    """
    Helper function to add each row to the database
    """
    
    product = Product(
        name=data['name'],
        sku=data['sku'],
        description=data['description'],
        is_active=data['is_active']
    )
    
    db.session.add(product)
    db.session.commit()


@celery.task
def overwrite_db(data):
    """
    Helper function to overwrite duplicated product and save.
    """
    
    product = Product.query.filter(Product.sku == data['sku']).first()
    product.name = data['name']
    product.sku = data['sku']
    product.description = data['description']
    product.is_active = data['is_active']
    
    db.session.add(product)
    db.session.commit()
