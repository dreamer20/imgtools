import pytest
import os
from imgtools import create_app


@pytest.fixture
def app():
    app = create_app({'TESTING': True})

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def image_sample():
    return open(os.path.join(os.path.dirname(__file__), 'image.jpg'), 'rb')
