import secrets

import bcrypt


def hashpw(password: str) -> bytes:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def checkpw(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


def generate_token() -> str:
    return secrets.token_hex(16)
