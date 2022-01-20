import os
from flask import Flask
from config import Config


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_object(Config)

    if test_config:
        app.config.from_mapping(test_config)

    from . import api
    app.register_blueprint(api.bp)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return 'index.html'

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
