import pytest

from core import create_app, db
from core.models import *


@pytest.fixture()
def app():
    app, celery = create_app('test')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
