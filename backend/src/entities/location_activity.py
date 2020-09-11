# coding=utf-8

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields

from .entity import Entity, Base


class LocationActivity(Entity, Base):
    __tablename__ = 'location-activity'

    activity_id = Column(Integer, ForeignKey('activities.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    location = relationship('Location', foreign_keys=location_id)
    activity = relationship('Activity', foreign_keys=activity_id)

    def __init__(self, activity_id, location_id, created_by):
        Entity.__int__(self, created_by)
        self.activity_id = activity_id
        self.location_id = location_id


class LocationActivitySchema(Schema):
    id = fields.Integer()
    activity_id = fields.Integer()
    location_id = fields.Integer()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_updated_by = fields.String()
