web: gunicorn app:app --preload --timeout 30 --log-level debug
worker: celery -A tasks.celery_app worker -Ofair --pool=gevent --concurrency=1000 --loglevel=INFO --without-gossip --without-mingle --without-heartbeat
