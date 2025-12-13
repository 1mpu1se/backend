import boto3
import elasticsearch
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config


class Context:
    _rs: redis.Redis = None
    _sm = None
    _s3 = None
    _es: elasticsearch.Elasticsearch = None

    def __init__(self):
        # Redis
        self._rs = redis.Redis(
            host=config.redis_host(),
            port=config.redis_port()
        )

        # Database
        self._sm = sessionmaker(
            bind=create_engine('postgresql+psycopg2://{}:{}@{}:{}/{}'.format(
                config.postgres_username(),
                config.postgres_password(),
                config.postgres_host(),
                config.postgres_port(),
                config.postgres_database()
            ), pool_size=20, max_overflow=0),
            autocommit=False,
            autoflush=False,
        )

        # S3
        self._s3 = boto3.client(
            service_name='s3',
            aws_access_key_id=config.s3_access_key(),
            aws_secret_access_key=config.s3_secret_key(),
            endpoint_url=f'http://{config.s3_host()}:{config.s3_port()}'
        )

        # Elasticsearch
        self._es = elasticsearch.Elasticsearch(
            hosts=f'http://{config.elasticsearch_host()}:{config.elasticsearch_port()}',
            basic_auth=(config.elasticsearch_username(), config.elasticsearch_password())
        )

    @property
    def rs(self) -> redis.Redis:
        return self._rs

    @property
    def sm(self):
        return self._sm

    @property
    def s3(self):
        return self._s3

    @property
    def es(self) -> elasticsearch.Elasticsearch:
        return self._es


ctx = Context()


def get_db():
    db = ctx.sm()
    try:
        yield db
    finally:
        db.close()
