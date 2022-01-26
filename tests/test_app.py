import os
import pytest
from PIL import Image
from io import BytesIO
from imgtools import create_app
from imgtools.api import withFileCheck


def save_as_image(file, func_name, image_name):
    with Image.open(BytesIO(file)) as img:
        img_name = (f'{func_name}_{image_name}.{img.format.lower()}')
        img_path = os.path.join(os.path.dirname(__file__), 'output', img_name)
        img.save(img_path)


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

    assert response.mimetype == 'image/jpeg'

    save_as_image(
        file=response.data,
        func_name=test_reflect.__name__,
        image_name=direction)


resize_testData = [
    (100, 100),
    (500, 500),
    (1, 1),
    (1028, 1024),
    (200, 500)
]


@pytest.mark.parametrize('width, height', resize_testData)
def test_resize(client, image_sample, width, height):
    response = client.post('/api/resize', data={
        "image": (image_sample, "test1.jpg"),
        "width": width,
        "height": height
    })

    assert response.status_code == 200
    assert response.mimetype == 'image/jpeg'

    save_as_image(
        file=response.data,
        func_name=test_resize.__name__,
        image_name=f'{width}x{height}')


@pytest.mark.parametrize('degree', [45, 90, 180, 270, 66])
def test_rotate(client, image_sample, degree):
    response = client.post('/api/rotate', data={
        "image": (image_sample, "test1.jpg"),
        "degree": degree,
    })

    assert response.status_code == 200
    assert response.mimetype == 'image/jpeg'

    save_as_image(
        file=response.data,
        func_name=test_rotate.__name__,
        image_name=degree)


def test_invert(client, image_sample):
    response = client.post('/api/invert', data={
        "image": (image_sample, "test1.jpg"),
    })

    assert response.status_code == 200
    assert response.mimetype == 'image/jpeg'

    save_as_image(
        file=response.data,
        func_name=test_invert.__name__,
        image_name='invert')


@pytest.mark.parametrize('filterName', ['BLUR', 'DETAIL'])
def test_filter(client, image_sample, filterName):
    response = client.post('/api/filter', data={
        "image": (image_sample, "test1.jpg"),
        "filterName": filterName,
    })

    assert response.status_code == 200
    assert response.mimetype == 'image/jpeg'

    save_as_image(
        file=response.data,
        func_name=test_filter.__name__,
        image_name=filterName)


@pytest.mark.parametrize('threshold', [0, 24, 64, 128, 256, -100])
def test_solarize(client, image_sample, threshold):
    response = client.post('/api/solarize', data={
        "image": (image_sample, "test1.jpg"),
        "threshold": threshold,
    })

    assert response.status_code == 200
    assert response.mimetype == 'image/jpeg'

    save_as_image(
        file=response.data,
        func_name=test_solarize.__name__,
        image_name=threshold)


@pytest.mark.parametrize('bits', [1, 2, '3', 4, '5', 6, 7, 8])
def test_posterize(client, image_sample, bits):
    response = client.post('/api/posterize', data={
        "image": (image_sample, "test1.jpg"),
        "bits": bits,
    })

    assert response.status_code == 200
    assert response.mimetype == 'image/jpeg'

    save_as_image(
        file=response.data,
        func_name=test_posterize.__name__,
        image_name=bits)


def test_grayscale(client, image_sample):
    response = client.post('/api/grayscale', data={
        "image": (image_sample, "test1.jpg"),
    })

    assert response.status_code == 200
    assert response.mimetype == 'image/jpeg'

    save_as_image(
        file=response.data,
        func_name=test_grayscale.__name__,
        image_name='')


@pytest.mark.parametrize('bits', ['string', '', -1, 0, 10])
def test_posterize_fails(client, image_sample, bits):
    response = client.post('/api/posterize', data={
        "image": (image_sample, "test1.jpg"),
        "bits": bits,
    })
    json_data = response.get_json()

    assert response.status_code == 400
    assert json_data == {'error': 'Некорректное значение.'}


def test_filter_no_found(client, image_sample):
    response = client.post('/api/filter', data={
        "image": (image_sample, "test1.jpg"),
        "filterName": 'somenofiltername',
    })
    json_data = response.get_json()

    assert response.status_code == 400
    assert json_data == {'error': 'Операция не выполнима.'}


# @pytest.mark.test
# def test_processing(client, image_sample):
#     response = client.post('/api/test', data={
#         "image": (image_sample, "test1.jpg"),
#         # "image2": (image_sample2, "test2.jpg"),
#     })

#     assert response.status_code == 200
#     assert response.mimetype == 'image/jpeg'

#     save_as_image(
#         file=response.data,
#         func_name=test_processing.__name__,
#         image_name='posterize')
