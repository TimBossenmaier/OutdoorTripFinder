# coding=utf-8

from sqlalchemy import Column, String,Text
from marshmallow import Schema, fields
from sqlalchemy.orm import relationship
from backend.src.entities.location_activity import LocationActivity

from .entity import Entity, Base


class Activity(Entity, Base):
    __tablename__ = 'activities'

    name = Column(String, nullable=False)
    locations = relationship('LocationActivity', uselist=True, backref='activities')
    description = Column(Text)
    activity_type = Column(String, nullable=False)
    source = Column(String, nullable=False)
    save_path = Column(String, nullable=False)

    def __init__(self, name, description, activity_type, source, save_path, created_by):
        Entity.__int__(self, created_by)
        self.name = name
        self.description = description
        self.activity_type = activity_type
        self.source = source
        self.save_path = save_path


class ActivitySchema(Schema):
    id = fields.Number()
    name = fields.String()
    description = fields.String()
    activity_type = fields.String()
    source = fields.String()
    save_path = fields.String()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_updated_by = fields.String()
