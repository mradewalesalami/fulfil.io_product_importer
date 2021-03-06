import os

# broker_url = 'amqp://celery:celery@localhost:5672/celery'
broker_url = os.environ['QUEUE_BROKER_URL']
imports = ('tasks',)
accept_content = ['msgpack', 'json', 'pickle']
result_accept_content = ['msgpack', 'json', 'pickle']
task_serializer = 'pickle'
# result_backend = 'redis://'
result_backend = os.environ['REDIS_URL']
result_serializer = 'pickle'
result_expires = None
# task_time_limit = 60
# task_soft_time_limit = 60
task_acks_late = True
worker_prefetch_multiplier = 10
worker_send_task_event = False
