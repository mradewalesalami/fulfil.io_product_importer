import os
import random
from io import BytesIO
from tempfile import gettempdir

import pandas as pd
from flask import current_app as app
import connectorx as cx
from celery import Celery

from core import db
from core.models import Product, Progress
import celeryconfig
from app import app as ctx

STATE = [True, False]

celery_app = Celery(__name__)
celery_app.config_from_object(celeryconfig)


@celery_app.task
def delete_all_products_from_db():
    """
    Query all the products in Database and delete.
    Then return a json response to Celery.
    """
    with ctx.app_context():
        Product.query.delete()
        db.session.commit()


@celery_app.task(bind=True)
def upload_product_from_csv_to_db(self, data):
    """
    Product upload task.
    """
    with ctx.app_context():
        csv_file = BytesIO(data)
        csv_df = pd.read_csv(csv_file).drop_duplicates(subset=['sku'], keep='last')
        
        """
        Querying all products in the database and loading it in a pandas dataframe.
        To iterate over it checking if any duplicates from the uploaded csv.
        """
        query_from_sql = cx.read_sql(
            conn=app.config['SQLALCHEMY_DATABASE_URI'],
            query="SELECT sku FROM products",
            return_type="pandas"
        )
        
        query_to_numpy = query_from_sql.to_numpy()
        
        """
        Tracking the task metadata
        """
        task_id = self.request.id
        total_uploads = len(csv_df)
        task_progress = Progress(task_id=task_id, total=total_uploads)
        db.session.add(task_progress)
        db.session.commit()
        
        upload_done = 0
        
        """
        Loop through the csv file, check if any duplicates are there in the fetched database.
        If yes, we query the database for the duplicate product and overwrites it.
        if no, a new product is created and saved to the database.
        """
        for row in csv_df.itertuples(name='Product', index=False):
            if row.sku in query_to_numpy:
                product = Product.query.filter(Product.sku == row.sku).first()
                product.name = row.name
                product.sku = row.sku
                product.description = row.description
                product.is_active = random.choice(STATE)
                db.session.add(product)
            else:
                product = Product(
                    name=row.name,
                    sku=row.sku,
                    description=row.description,
                    is_active=random.choice(STATE)
                )
                db.session.add(product)
            upload_done += 1
            upload_pending = total_uploads - upload_done
            progress = Progress.query.filter(Progress.task_id == task_id).first()
            progress.done = upload_done
            progress.pending = upload_pending
            db.session.add(progress)
            db.session.commit()
