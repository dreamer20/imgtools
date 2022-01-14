import os
from flask import Flask
from config import Config


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_object(Config)

    if test_config:
        app.config.from_mapping(test_config)

    from . import main
    app.register_blueprint(main.bp)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
