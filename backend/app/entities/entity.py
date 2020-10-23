# coding=utf-8

from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from marshmallow import Schema, fields
from dotenv import load_dotenv
from enum import Enum
import os

load_dotenv('../.env')

engine = None
if os.environ.get('FLASK_CONFIG') == 'prod':
    engine = create_engine('postgresql://{}:{}@{}/{}'.format(os.environ.get('PROD_DATABASE_USER'),
                                                             os.environ.get('PROD_DATABASE_PASSWORD'),
                                                             os.environ.get('PROD_DATABASE_HOST'),
                                                             os.environ.get('PROD_DATABASE_NAME')))
elif os.environ.get('FLASK_CONFIG') == 'test':
    engine = create_engine('postgresql://{}:{}@{}/{}'.format(os.environ.get('TEST_DATABASE_USER'),
                                                             os.environ.get('TEST_DATABASE_PASSWORD'),
                                                             os.environ.get('TEST_DATABASE_HOST'),
                                                             os.environ.get('TEST_DATABASE_NAME')))
else:
    engine = create_engine('postgresql://{}:{}@{}/{}'.format(os.environ.get('DEV_DATABASE_USER'),
                                                             os.environ.get('DEV_DATABASE_PASSWORD'),
                                                             os.environ.get('DEV_DATABASE_HOST'),
                                                             os.environ.get('DEV_DATABASE_NAME')))

Session = sessionmaker(bind=engine)

Base = declarative_base()


class Entity:

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False, onupdate=datetime.now())
    last_updated_by = Column(String, nullable=False)

    def __init__(self, created_by):
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.last_updated_by = created_by


class EntitySchema(Schema):
    id = fields.Integer()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_updated_by = fields.String()


class EntityAttributes(Enum):
    ID = 'id'
    CREATED_AT = 'created_at'
    UPDATED_AT = 'updated_at'
    UPDATED_BY = 'last_updated_by'
