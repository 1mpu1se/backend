import sys
import os
import pytest
from unittest.mock import patch, MagicMock, PropertyMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import src.context as context_module


def test_context_initialization():
    '''Проверка инициализации Context и вызова конструкторов клиентов с параметрами из конфига'''
    with patch('redis.Redis') as mock_redis, \
            patch('sqlalchemy.create_engine') as mock_engine, \
            patch('boto3.client') as mock_s3, \
            patch('elasticsearch.Elasticsearch') as mock_es:
        from src.context import Context
        ctx = Context()

        mock_redis.assert_called_once()
        mock_s3.assert_called_with(
            service_name='s3',
            aws_access_key_id=context_module.config.s3_access_key(),
            aws_secret_access_key=context_module.config.s3_secret_key(),
            endpoint_url=f'http://{context_module.config.s3_host()}:{context_module.config.s3_port()}'
        )
        mock_es.assert_called_once()


def test_get_db_yields_session():
    '''Проверка генератора get_db на корректное открытие и закрытие сессии'''
    mock_session = MagicMock()

    # Мы патчим внутренний атрибут _sm, так как sm — это read-only property
    with patch('src.context.ctx._sm', return_value=mock_session):
        db_gen = context_module.get_db()
        db = next(db_gen)

        assert db == mock_session

        try:
            next(db_gen)
        except StopIteration:
            pass

        mock_session.close.assert_called_once()