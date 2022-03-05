from celery import Celery
import celeryconfig


def make_celery(app):
    celery = Celery(app.import_name)
    # celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    
    celery.config_from_object('celeryconfig')
    
    return celery