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
    img_path = os.path.join(os.path.dirname(__file__), 'test_image3.jpg')
    return open(img_path, 'rb')


@pytest.fixture
def image_sample2():
    img_path = os.path.join(os.path.dirname(__file__), 'test_image4.jpg')
    return open(img_path, 'rb')
