from configure import detect_configuration_mode
from core import create_app

# Get the config mode from the environment
configuration_mode = detect_configuration_mode()

# Instantiate the flask app
app, celery = create_app(configuration_mode)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
