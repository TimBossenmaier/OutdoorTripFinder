# coding=utf-8

from sqlalchemy import Column, String, ForeignKey, Integer, Float
from marshmallow import Schema, fields
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from app.entities.entity import Entity, Base, EntitySchema


class Location(Entity, Base):
    __tablename__ = 'locations'

    lat = Column(Float, nullable=False)
    long = Column(Float, nullable=False)
    name = Column(String, nullable=False)
    location_type_id = Column(Integer, ForeignKey('location_types.id'), nullable=False)
    location_type = relationship('LocationType', foreign_keys=location_type_id)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)
    last_updated_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    region = relationship('Region', foreign_keys=region_id)
    linked_activities = relationship('LocationActivity', uselist=True, backref='locations')

    def __init__(self, lat, long, name, location_type_id, region_id, created_by):
        Entity.__init__(self)
        self.lat = lat
        self.long = long
        self.name = name
        self.location_type_id = location_type_id
        self.region_id = region_id
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
        schema = LocationInsertSchema()
        return schema.dump(self)

    def convert_to_presentation_schema(self, only=(), **kwargs):
        schema = LocationPresentationSchema(only=only if len(only) > 0 else None)
        dump = schema.dump(self)
        for key, value in kwargs.items():
            dump.update({key: value})

        return dump

    def serialize(self):
        loc = LocationSchema().dump(self)

        return loc

    @staticmethod
    def get_insert_schema():
        return LocationInsertSchema()

    @staticmethod
    def get_schema(many, only):
        return LocationSchema(many=many, only=only)

    @staticmethod
    def get_attributes():
        return LocationAttributes


class LocationSchema(EntitySchema):
    lat = fields.Float()
    long = fields.Float()
    name = fields.String()
    location_type_id = fields.Integer()
    region_id = fields.Integer()
    last_updated_by = fields.Integer()


class LocationInsertSchema(Schema):
    lat = fields.Float()
    long = fields.Float()
    name = fields.String()
    location_type_id = fields.Integer()
    region_id = fields.Integer()
    created_by = fields.Integer()


class LocationPresentationSchema(LocationSchema):
    id = fields.Integer()


class LocationAttributes(Enum):
    NAME = 'name'
    LATITUDE = 'lat'
    LONGITUDE = 'long'
    LOCATION_TYPE_ID = 'location_type_id'
    REGION_ID = 'region_id'
    LAST_UPDATED_BY = 'last_updated_by'
    ID = 'id'
    CREATED_AT = 'created_at'
    UPDATED_AT = 'updated_at'

    def __str__(self):
        return str(self.value)
