# coding=utf-8
from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey
from marshmallow import Schema, fields
from sqlalchemy.orm import relationship
from enum import Enum

from ..entities.country import Country
from .entity import Entity, EntitySchema, Base


class Region(Entity, Base):
    __tablename__ = 'regions'

    name = Column(String, nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    country = relationship(Country, foreign_keys=country_id)
    last_updated_by = Column(Integer, ForeignKey('users.id'), nullable=False)

    def __init__(self, name, country_id, created_by):
        Entity.__init__(self)
        self.name = name
        self.country_id = country_id
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
        schema = RegionInsertSchema()
        return schema.dump(self)

    def serialize(self):
        reg = RegionSchema().dump(self)

        return reg

    @staticmethod
    def get_insert_schema():
        return RegionInsertSchema()

    @staticmethod
    def get_schema(many, only):
        return RegionSchema(many=many, only=only)

    @staticmethod
    def get_attributes():
        return RegionAttributes


class RegionSchema(EntitySchema):
    name = fields.String()
    country_id = fields.Integer()
    last_updated_by = fields.String()


class RegionInsertSchema(Schema):
    name = fields.String()
    country_id = fields.Integer()
    created_by = fields.Integer()


class RegionAttributes(Enum):
    NAME = "name"
    COUNTRY_ID = "country_id"
    LAST_UPDATED_BY = 'last_updated_by'
    ID = 'id'
    CREATED_AT = 'created_at'
    UPDATED_AT = 'updated_at'

    def __str__(self):
        return str(self.value)