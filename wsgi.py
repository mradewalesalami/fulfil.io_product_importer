from configure import detect_configuration_mode
from core import create_app


configuration_mode = detect_configuration_mode()

application = create_app(configuration_mode)


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=2673)