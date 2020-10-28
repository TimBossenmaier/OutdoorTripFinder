# coding=utf-8

from sqlalchemy import Column, String, Integer, ForeignKey
from marshmallow import Schema, fields
from datetime import datetime
from enum import Enum

from .entity import Entity, Base, EntitySchema


class LocationType(Entity, Base):
    __tablename__ = 'location_types'

    name = Column(String, nullable=False)
    last_updated_by = Column(Integer, ForeignKey('users.id'), nullable=False)

    def __init__(self, name, created_by):
        Entity.__init__(self)
        self.name = name
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

    @staticmethod
    def get_insert_schema():
        return LocationTypeInsertSchema()

    @staticmethod
    def get_schema(many, only):
        return LocationTypeSchema(many=many, only=only)

    @staticmethod
    def get_attributes():
        return LocationTypeAttributes

    def convert_to_insert_schema(self):
        schema = LocationTypeInsertSchema()
        return schema.dump(self)


class LocationTypeSchema(EntitySchema):
    name = fields.String()
    last_updated_by = fields.Integer()


class LocationTypeInsertSchema(Schema):
    name = fields.String()
    created_by = fields.Integer()


class LocationTypeAttributes(Enum):
    NAME = 'name'
    LAST_UPDATED_BY = 'last_updated_by'
    ID = 'id'
    CREATED_AT = 'created_at'
    UPDATED_AT = 'updated_at'

    def __str__(self):
        return str(self.value)
