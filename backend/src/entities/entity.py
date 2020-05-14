# coding=utf-8

from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

dict_db_params = None

# read the config JSON and load it as JSON
with open('./entities/db_config.json', encoding='utf-8') as F:
    dict_db_params = json.load(F)

db_url = dict_db_params["host"]
db_name = dict_db_params["db_name"]
db_user = dict_db_params["user"]
db_password = dict_db_params["password"]

engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_url}/{db_name}')
Session = sessionmaker(bind=engine)

Base = declarative_base()


class Entity:

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    last_updated_by = Column(String)

    def __int__(self, created_by):
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.last_updated_by = created_by
