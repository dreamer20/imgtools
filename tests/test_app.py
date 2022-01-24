import os
import pytest
from PIL import Image
from io import BytesIO
from imgtools import create_app
from imgtools.api import withFileCheck


def test_app():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_main_page(client):
    response = client.get('/')
    assert b'index.html' in response.data


withFileCheck_errorsTestData = [
    (
        {"image": (BytesIO("file contents".encode("utf8")), "test1.txt")},
        {
            "response": {"error": "Расширение не поддерживается"},
            "statusCode": 400
        }
    ),
    (
        {"image": (BytesIO("file contents".encode("utf8")), "file.bashrc")},
        {
            "response": {"error": "Расширение не поддерживается"},
            "statusCode": 400
        }
    ),
    (
        {"": ""},
        {
            "response": {"error": "Файл отсутствует"},
            "statusCode": 400
        }
    ),
    (
        {"image": (BytesIO("file contents".encode("utf8")), "")},
        {
            "response": {"error": "Изображение не выбрано"},
            "statusCode": 400
        }
    ),
]


@pytest.mark.parametrize('data, expected', withFileCheck_errorsTestData)
def test_withFileCheck_errors(app, client, data, expected):
    @app.route('/', methods=['POST'])
    @withFileCheck
    def f():
        return "None"

    response = client.post('/', data=data)
    json_data = response.get_json()
    assert response.status_code == expected['statusCode']
    assert json_data == expected['response']


@pytest.mark.parametrize('ext', ['jpg', 'jpeg', 'gif', 'png'])
def test_withFileCheck_file_ext(app, client, ext):
    @app.route('/', methods=['POST'])
    @withFileCheck
    def f():
        return "good response"

    response = client.post('/', data={
        "image": (BytesIO("file contents".encode("utf8")), f"test.{ext}")
    })
    assert response.status_code == 200
    assert b'good response' in response.data


@pytest.mark.parametrize('direction', ['horizontally', 'vertically'])
def test_reflect(client, direction, image_sample):
    response = client.post('/api/reflect', data={
        "image": (image_sample, "test.jpeg"),
        "direction": direction
    },)
    bytes_io = BytesIO(response.data)

    assert response.mimetype == 'image/jpeg'

    with Image.open(bytes_io) as img:
        img.save(os.path.join(
            os.path.dirname(__file__), f'output/{direction}.jpg')
        )
