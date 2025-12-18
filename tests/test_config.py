import os
import logging
from unittest.mock import patch
import src.config as config

def test_log_level_default():
    '''Проверка уровня логирования по умолчанию'''
    with patch.dict(os.environ, {}, clear=True):
        assert config.log_level() == logging.DEBUG

def test_log_level_custom():
    '''Проверка ручной установки уровня логирования через окружение'''
    with patch.dict(os.environ, {'LOG_LEVEL': str(logging.INFO)}):
        assert config.log_level() == logging.INFO

def test_allowed_origins_default():
    '''Проверка разрешенных адресов по умолчанию'''
    with patch.dict(os.environ, {}, clear=True):
        assert config.allowed_origins() == ['http://localhost:3000']

def test_allowed_origins_multiple():
    '''Проверка парсинга нескольких адресов через точку с запятой'''
    origins = 'http://test.com;http://app.io'
    with patch.dict(os.environ, {'ALLOWED_ORIGINS': origins}):
        assert config.allowed_origins() == ['http://test.com', 'http://app.io']

def test_redis_config():
    '''Проверка настроек Redis'''
    with patch.dict(os.environ, {'REDIS_HOST': '10.0.0.1', 'REDIS_PORT': '7000'}):
        assert config.redis_host() == '10.0.0.1'
        assert config.redis_port() == 7000

def test_postgres_config():
    '''Проверка настроек Postgres'''
    test_data = {
        'POSTGRES_HOST': 'db.host',
        'POSTGRES_PORT': '5433',
        'POSTGRES_USERNAME': 'admin',
        'POSTGRES_PASSWORD': 'password123',
        'POSTGRES_DATABASE': 'prod_db'
    }
    with patch.dict(os.environ, test_data):
        assert config.postgres_host() == 'db.host'
        assert config.postgres_port() == 5433
        assert config.postgres_username() == 'admin'
        assert config.postgres_password() == 'password123'
        assert config.postgres_database() == 'prod_db'

def test_s3_config_defaults():
    '''Проверка настроек S3 по умолчанию'''
    with patch.dict(os.environ, {}, clear=True):
        assert config.s3_host() == '127.0.0.1'
        assert config.s3_access_key() == 'minioadmin'

def test_elasticsearch_config():
    '''Проверка настроек Elasticsearch'''
    with patch.dict(os.environ, {'ELASTICSEARCH_PORT': '9500'}):
        # В коде config.py elasticsearch_port не обернут в int(), проверим это
        assert config.elasticsearch_port() == '9500'