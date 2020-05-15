# coding=utf-8

from sqlalchemy import Column, String, ForeignKey, Integer
from marshmallow import Schema, fields
from sqlalchemy.orm import relationship

from .entity import Entity, Base


class Location(Entity, Base):
    __tablename__ = 'locations'

    geo_coordinate = Column(String, nullable=False)
    name = Column(String, nullable=False)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    region = relationship('Region', foreign_keys=region_id)
    country = relationship('Country', foreign_keys=country_id)

    def __init__(self, geo_coordinate, name, region_id, country_id, created_by):
        Entity.__int__(self, created_by)
        self.geo_coordinate = geo_coordinate
        self.name = name
        self.region_id = region_id
        self.country_id = country_id


class LocationSchema(Schema):
    id = fields.Number()
    geo_coordinate = fields.String()
    name = fields.String()
    region_id = fields.Number()
    country_id = fields.Number()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_updated_by = fields.String()
