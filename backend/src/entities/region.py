# coding=utf-8

from sqlalchemy import Column, String, Integer, ForeignKey
from marshmallow import Schema, fields
from sqlalchemy.orm import relationship
from backend.src.entities.country import Country

from .entity import Entity, Base


class Region(Entity, Base):
    __tablename__ = 'regions'

    name = Column(String, nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    country = relationship(Country, foreign_keys=country_id)

    def __init__(self, name, country_id, created_by):
        Entity.__init__(self, created_by)
        self.name = name
        self.country_id = country_id


class RegionSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    country_id = fields.Integer()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_updated_by = fields.String()
