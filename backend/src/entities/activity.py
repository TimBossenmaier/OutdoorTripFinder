# coding=utf-8

from sqlalchemy import Column, String, Date, ARRAY, Integer
from marshmallow import Schema, fields
from sqlalchemy.orm import relationship

from .entity import Entity, Base


class Activity(Entity, Base):
    __tablename__ = 'activities'

    locations = relationship(uselist=True, backref='activities')
    activity_type = Column(String)
    origin = Column(String)
    save_path = Column(String)

    def __init__(self, locations, activity_type, origin, save_path, created_by):
        Entity.__init__(self, created_by)
        self.locations = locations
        self.activity_type = activity_type
        self.origin = origin
        self.save_path = save_path


class ActivitySchema(Schema):
    id = fields.Number()
    locations = fields.Integer()
    activity_type = fields.String()
    origin = fields.String()
    save_path = fields.String()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_updated_by = fields.String()
