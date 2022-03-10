import os
import random
from io import BytesIO

import pandas as pd
from flask import current_app as app
import connectorx as cx
import boto3
from boto3.s3.transfer import TransferConfig
from werkzeug.utils import secure_filename

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
    Product upload task.
    """
    
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


@celery.task
def uploadFileS3(file):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
    )
    # filename = secure_filename(file.filename)
    s3_bucket = 'iamnzapi'
    config = TransferConfig(
        multipart_threshold=1024 * 25,
        max_concurrency=10,
        multipart_chunksize=1024 * 25,
        use_threads=True)
    s3_client.upload_fileobj(
        BytesIO(file),
        s3_bucket,
        'csvfile',
        ExtraArgs={'ACL': 'public-read', 'ContentType': 'file.content_type'},
        Config=config
    )
    return 'csvfile'
