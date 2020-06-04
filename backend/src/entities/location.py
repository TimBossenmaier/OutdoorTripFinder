# coding=utf-8

from sqlalchemy import Column, String, ForeignKey, Integer, Float
from marshmallow import Schema, fields
from sqlalchemy.orm import relationship
from backend.src.entities.region import Region
from .entity import Entity, Base


class Location(Entity, Base):
    __tablename__ = 'locations'

    lat = Column(Float, nullable=False)
    long = Column(Float, nullable=False)
    name = Column(String, nullable=False)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)
    region = relationship(Region, foreign_keys=region_id)

    def __init__(self, lat, long, name, region_id, created_by):
        Entity.__init__(self, created_by)
        self.lat = lat
        self.long = long
        self.name = name
        self.region_id = region_id


class LocationSchema(Schema):
    id = fields.Integer()
    lat = fields.Float()
    long = fields.Float()
    name = fields.String()
    region_id = fields.Integer()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_updated_by = fields.String()
