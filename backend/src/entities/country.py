# coding=utf-8

from sqlalchemy import Column, String
from marshmallow import Schema, fields

from .entity import Entity, Base


class Country(Entity, Base):
    __tablename__ = 'countries'

    name = Column(String, nullable=False)

    def __init__(self, name, created_by):
        Entity.__int__(self, created_by)
        self.name = name


class CountrySchema(Schema):
    id = fields.Integer()
    name = fields.String()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_updated_by = fields.String()
