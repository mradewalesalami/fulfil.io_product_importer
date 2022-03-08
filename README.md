# fulfil.io_product_importer
Designing an API system that allows import of a large CSV file of over 500K rows into an SQL database considering robustness of the API system and scalability

# Getting started
- Clone the repository into your local system
- Install python 3.10
- Open the cloned repository in any editor of choice
- Create a virtual environment
- Install requirements.txt file in the virtual environment
- Download and install RabbitMQ and Redis
- Download and install postgresql database
- Configure RabbitMQ as message broker
- Configure Redis as result backend
```
```
- RabbitMQ config for localhost
```
$ rabbitmqctl add_user celery celery
$ rabbitmqctl add_vhost celery
$ rabbitmqctl set_permissions -p celery celery ".*" ".*" ".*"
$ rabbitmqctl set_user_tags celery management
```
- Postgres config for localhost
```
username: fulfil
password: password
db name: fulfil_db
```
- To test the webhook, visit www.webhook.site and get a unique URL. Paste the URL as value for WEBHOOK_TEST_URL. Create a new product or update a product and see the webhook gets triggered.

# Usage
To use the postman collections, check the documentation on the postman collection for sample request and responses.
- When uploading a CSV file at the upload CSV endpoint, key name must be 'file'

# Tech stack
- Flask
- SQLAlchemy
- Celery
- RabbitMQ/Redis
- Postgressql
- Heroku

# Test
![img.png](img.png)