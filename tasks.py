from app import celery
from core import db
from core.models import Product


@celery.task
def delete_all_products_from_db():
    Product.query.delete()
    db.session.commit()
    