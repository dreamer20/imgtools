import pytest
import os
import glob
from imgtools import create_app


@pytest.fixture(scope='session', autouse=True)
def remove_output_images():
    output_dir = glob.glob(os.path.join(
        os.path.dirname(__file__),
        'output',
        '*.*')
    )
    for p in output_dir:
        os.remove(p)


@pytest.fixture
def app():
    app = create_app({'TESTING': True})
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def image_sample():
    img_path = os.path.join(
        os.path.dirname(__file__),
        'input',
        'test_image3.jpg'
    )
    return open(img_path, 'rb')


@pytest.fixture
def image_sample2():
    img_path = os.path.join(
        os.path.dirname(__file__),
        'input',
        'test_image4.jpg'
    )
    return open(img_path, 'rb')
