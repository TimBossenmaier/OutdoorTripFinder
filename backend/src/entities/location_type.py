# coding=utf-8

from sqlalchemy import Column, String
from marshmallow import Schema, fields

from .entity import Entity, Base


class LocationType(Entity, Base):
    __tablename__ = 'location_types'

    name = Column(String, nullable=False)

    def __init__(self, name, created_by):
        Entity.__init__(self, created_by)
        self.name = name


class LocationTypeSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_updated_by = fields.String()
