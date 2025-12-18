from src.util import hashpw, checkpw, generate_token


def test_hashpw_generates_bytes():
    """Проверяем, что функция возвращает байты, а не строку"""
    password = "my_secret_password"
    hashed = hashpw(password)
    assert isinstance(hashed, bytes)
    assert hashed != password.encode('utf-8')


def test_checkpw_positive():
    """Проверяем успешную валидацию пароля"""
    password = "correct_password"
    hashed = hashpw(password)
    assert checkpw(password, hashed) is True


def test_checkpw_negative():
    """Проверяем, что неверный пароль не проходит проверку"""
    password = "correct_password"
    wrong_password = "wrong_password"
    hashed = hashpw(password)
    assert checkpw(wrong_password, hashed) is False


def test_generate_token_length():
    """Проверяем длину и уникальность токена"""
    token1 = generate_token()
    token2 = generate_token()

    # secrets.token_hex(16) возвращает 32 символа (16 байт в hex)
    assert len(token1) == 32
    assert token1 != token2  # Токены должны быть уникальными