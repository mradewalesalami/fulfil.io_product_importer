import os

# WEBHOOK_URL = 'http://127.0.0.1:2673/api/v1.0/webhook'
WEBHOOK_URL = 'https://product-importer-rest-api.herokuapp.com/api/v1.0/webhook'
REQUEST_HEADER = {'Content-Type': 'application/json'}
WEBHOOK_TEST_URL = 'https://webhook.site/092c1398-3e5a-4a66-aee2-0dc8738f8aeb'
BROKER_URL = os.environ['QUEUE_BROKER_URL']
CELERY_IMPORTS = ('tasks',)
CELERY_ACCEPT_CONTENT = ['msgpack', 'json', 'pickle']
CELERY_RESULT_BACKEND = os.environ['REDIS_URL']
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_RESULT_EXPIRES = None
CELERY_TASK_SERIALIZER = 'pickle'
