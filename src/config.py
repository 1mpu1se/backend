import logging
from os import environ as env

"""
BASE
"""


def log_level() -> int:
    """
    Logging level (defaults to logging.DEBUG)
    """
    return int(
        env.get('LOG_LEVEL', logging.DEBUG)
    )


"""
REDIS
"""


def redis_host() -> str:
    """
    Redis host (defaults to '127.0.0.1')
    """
    return (
        env.get('REDIS_HOST', '127.0.0.1')
    )


def redis_port() -> int:
    """
    Redis port (defaults to 6379)
    """
    return (
        int(env.get('REDIS_PORT', 6379))
    )


"""
POSTGRES
"""


def postgres_host() -> str:
    """
    Postgres host (defaults to '127.0.0.1')
    """
    return (
        env.get('POSTGRES_HOST', '127.0.0.1')
    )


def postgres_port() -> int:
    """
    Postgres port (defaults to 5432)
    """
    return int(
        env.get('POSTGRES_PORT', 5432)
    )


def postgres_username() -> str:
    """
    Postgres username (defaults to 'postgres')
    """
    return (
        env.get('POSTGRES_USERNAME', 'postgres')
    )


def postgres_password() -> str:
    """
    Postgres password (defaults to 'postgres')
    """
    return (
        env.get('POSTGRES_PASSWORD', 'postgres')
    )


def postgres_database() -> str:
    """
    Postgres database (defaults to 'postgres')
    """
    return (
        env.get('POSTGRES_DATABASE', 'postgres')
    )


"""
S3
"""


def s3_host() -> str:
    """
    S3 host (defaults to '127.0.0.1')
    """
    return (
        env.get('S3_HOST', '127.0.0.1')
    )


def s3_port() -> int:
    """
    S3 port (defaults to 9000)
    """
    return int(
        env.get('S3_PORT', 9000)
    )


def s3_access_key() -> str:
    """
    S3 access key (defaults to 'minioadmin')
    """
    return (
        env.get('S3_ACCESS_KEY', 'minioadmin')
    )


def s3_secret_key() -> str:
    """
    S3 secret key (defaults to 'minioadmin')
    """
    return (
        env.get('S3_SECRET_KEY', 'minioadmin')
    )


"""
ELASTICSEARCH
"""


def elasticsearch_host() -> str:
    """
    Elasticsearch host (defaults to '127.0.0.1')
    """
    return (
        env.get('ELASTICSEARCH_HOST', '127.0.0.1')
    )


def elasticsearch_port() -> int:
    """
    Elasticsearch port (defaults to 9200)
    """
    return (
        env.get('ELASTICSEARCH_PORT', 9200)
    )


def elasticsearch_username() -> str:
    """
    Elasticsearch username (defaults to 'elastic')
    """
    return (
        env.get('ELASTICSEARCH_USERNAME', 'elastic')
    )


def elasticsearch_password() -> str:
    """
    Elasticsearch password (defaults to 'elastic')
    """
    return (
        env.get('ELASTICSEARCH_PASSWORD', 'elastic')
    )
