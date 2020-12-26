# coding=utf-8
from enum import Enum
from sqlalchemy import Column, String, Integer, ForeignKey
from marshmallow import Schema, fields
from datetime import datetime

from app.entities.entity import Entity, EntitySchema, Base, Session


class Country(Entity, Base):
    __tablename__ = 'countries'

    name = Column(String, nullable=False, unique=True)
    abbreviation = Column(String, nullable=False, unique=True)
    last_updated_by = Column(Integer, ForeignKey('users.id'), nullable=False)

    def __init__(self, name, abbreviation, created_by):
        Entity.__init__(self)
        self.name = name
        self.abbreviation = abbreviation
        self.last_updated_by = created_by

    def create(self, session):

        session.add(self)
        session.commit()

        return self

    def update(self, session, updated_by, **kwargs):
        self.updated_at = datetime.now()
        self.last_updated_by = updated_by

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        session.add(self)
        session.commit()

    def convert_to_insert_schema(self):
        schema = CountryInsertSchema()
        return schema.dump(self)

    def convert_to_presentation_schema(self, only=(), **kwargs):
        schema = CountryPresentationSchema(only=only if len(only) > 0 else None)
        dump = schema.dump(self)
        for key, value in kwargs.items():
            dump.update({key: value})

        return dump

    def serialize(self):
        country = CountrySchema().dump(self)

        return country

    @staticmethod
    def get_insert_schema():
        return CountryInsertSchema()

    @staticmethod
    def get_schema(many, only):
        return CountrySchema(many=many, only=only)

    @staticmethod
    def get_attributes():
        return CountryAttributes


class CountrySchema(EntitySchema):
    name = fields.String()
    last_updated_by = fields.Integer()


class CountryInsertSchema(Schema):
    name = fields.String()
    abbreviation = fields.String()
    created_by = fields.Integer()


class CountryPresentationSchema(CountrySchema):
    id = fields.Integer()


class CountryAttributes(Enum):
    NAME = 'name'
    ABBREVIATION = 'abbreviation'
    LAST_UPDATED_BY = 'last_updated_by'
    ID = 'id'
    CREATED_AT = 'created_at'
    UPDATED_AT = 'updated_at'

    def __str__(self):
        return str(self.value)
