# coding=utf-8

from sqlalchemy import Column, String, Integer, ForeignKey
from marshmallow import Schema, fields
from sqlalchemy.orm import relationship
from backend.src.entities.country import Country

from .entity import Entity, EntitySchema, Base, Session


class Region(Entity, Base):
    __tablename__ = 'regions'

    name = Column(String, nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    country = relationship(Country, foreign_keys=country_id)

    def create(self):
        session = Session()
        session.add(self)
        session.commit()
        return self

    def __init__(self, name, country_id, created_by):
        Entity.__init__(self, created_by)
        self.name = name
        self.country_id = country_id


class RegionSchema(EntitySchema):
    name = fields.String()
    country_id = fields.Integer()
