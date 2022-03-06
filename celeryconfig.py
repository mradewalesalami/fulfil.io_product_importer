broker_url = 'amqp://celery:celery@localhost:5672/celery'
imports = ('tasks',)
accept_content = ['pickle']
task_serializer = 'pickle'