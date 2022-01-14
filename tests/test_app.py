from imgtools import create_app


def test_app():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_main_page(client):
    response = client.get('/')
    assert b'Index page' in response.data
