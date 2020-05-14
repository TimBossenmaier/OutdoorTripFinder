# coding=utf-8

from sqlalchemy import Column, String
from marshmallow import Schema, fields
from sqlalchemy.orm import relationship

from .entity import Entity, Base


class Region(Entity, Base):
    __tablename__ = 'regions'

    name = Column(String)
    country = relationship('country_id', foreign_keys='countries.id')

    def __init__(self, name, country, created_by):
        Entity.__init__(self, created_by)
        self.name = name
        self.country = country


class RegionSchema(Schema):
    id = fields.Number()
    name = fields.String()
    country = fields.Number()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_updated_by = fields.String()