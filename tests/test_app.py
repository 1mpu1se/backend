def test_index(client):
    response = client.get('/')

    assert response.status_code == 200
    assert 'version' in response.json()


def test_register_success(client):
    response = client.post(
        '/register',
        json={
            'username': 'test',
            'password': '1234'
        }
    )

    assert response.status_code == 200
    assert 'token' in response.json()


def test_login_success(client):
    # сначала регистрируем
    client.post(
        '/register',
        json={
            'username': 'test',
            'password': '1234'
        }
    )

    response = client.post(
        '/login',
        json={
            'username': 'test',
            'password': '1234'
        }
    )

    assert response.status_code == 200
    assert 'token' in response.json()
    # assert response.json()['token'] == 'test-token'


def test_login_wrong_password(client):
    client.post(
        '/register',
        json={
            'username': 'test',
            'password': '1234'
        }
    )

    response = client.post(
        '/login',
        json={
            'username': 'test',
            'password': 'wrong'
        }
    )

    assert response.status_code == 401
