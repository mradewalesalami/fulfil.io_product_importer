import os

broker_url = 'amqp://celery:celery@localhost:5672/celery'
# broker_url = os.environ['BROKER_URL']
imports = ('tasks',)
accept_content = ['pickle']
task_serializer = 'pickle'
result_backend = 'redis://'
# result_backend = os.environ['REDIS_URL']
result_serializer = 'pickle'
result_expires = None
