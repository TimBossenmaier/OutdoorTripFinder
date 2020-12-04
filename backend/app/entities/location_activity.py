# coding=utf-8

from sqlalchemy import Column, ForeignKey, Integer
from marshmallow import Schema, fields
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from .entity import Entity, Base, EntitySchema


class LocationActivity(Entity, Base):
    __tablename__ = 'location-activity'

    activity_id = Column(Integer, ForeignKey('activities.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    last_updated_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    location = relationship('Location', foreign_keys=location_id)
    activity = relationship('Activity', foreign_keys=activity_id)

    def __init__(self, activity_id, location_id, created_by):
        Entity.__init__(self)
        self.activity_id = activity_id
        self.location_id = location_id
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
        schema = LocationActivityInsertSchema()
        return schema.dump(self)

    def serialize(self):
        la = LocationActivitySchema().dump(self)

        return la

    @staticmethod
    def get_insert_schema():
        return LocationActivityInsertSchema()

    @staticmethod
    def get_schema(many, only):
        return LocationActivitySchema(many=many, only=only)

    @staticmethod
    def get_attributes():
        return LocationActivityAttributes


class LocationActivitySchema(EntitySchema):
    activity_id = fields.Integer()
    location_id = fields.Integer()
    last_updated_by = fields.Integer()


class LocationActivityInsertSchema(Schema):
    activity_id = fields.Integer()
    location_id = fields.Integer()
    created_by = fields.Integer()


class LocationActivityAttributes(Enum):
    NAME = "name"
    LAST_UPDATED_BY = 'last_updated_by'
    ACTIVITY_ID = 'activity_id'
    LOCATION_ID = 'location_id'
    ID = 'id'
    CREATED_AT = 'created_at'
    UPDATED_AT = 'updated_at'

    def __str__(self):
        return str(self.value)
