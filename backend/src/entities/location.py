# coding=utf-8

from sqlalchemy import Column, String, Date, ARRAY, Integer
from geoalchemy2 import Geometry
from marshmallow import Schema, fields
from sqlalchemy.orm import relationship

from .entity import Entity, Base


class Location(Entity, Base):
    __tablename__ = 'locations'

    geo_coordinate = Column(Geometry('POINT'))
    name = Column(String)
    region = relationship(foreign_keys='regions.id')
    country = relationship(foreign_keys='countries.id')

    def __init__(self, geo_coordinate, name, region, country, created_by):
        Entity.__init__(self, created_by)
        self.geo_coordinate = geo_coordinate
        self.name = name
        self.region = region
        self.country = country


class LocationSchema(Schema):
    id = fields.Number()
    geo_coordinate = fields.String()
    name = fields.String()
    region = fields.Number()
    country = fields.Number()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_updated_by = fields.String()
