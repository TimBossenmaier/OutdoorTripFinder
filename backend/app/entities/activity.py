# coding=utf-8

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean
from marshmallow import Schema, fields
from sqlalchemy.orm import relationship

from .entity import Entity, Base


class Activity(Entity, Base):
    __tablename__ = 'activities'

    name = Column(String, nullable=False)
    locations = relationship('LocationActivity', uselist=True, backref='activities')
    description = Column(Text)
    activity_type_id = Column(Integer, ForeignKey('activity_types.id'), nullable=False)
    source = Column(String, nullable=False)
    save_path = Column(String, nullable=False)
    multi_day = Column(Boolean, nullable=False)
    activity_type = relationship('ActivityType', foreign_keys=activity_type_id)

    def __init__(self, name, description, activity_type_id, source, save_path, multi_day, created_by):
        Entity.__init__(self, created_by)
        self.name = name
        self.description = description
        self.activity_type_id = activity_type_id
        self.source = source
        self.save_path = save_path
        self.multi_day = multi_day


class ActivitySchema(Schema):
    id = fields.Integer()
    name = fields.String()
    description = fields.String()
    activity_type_id = fields.Integer()
    source = fields.String()
    save_path = fields.String()
    multi_day = fields.Boolean()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_updated_by = fields.String()


class ActivityPresentationSchema(ActivitySchema):
    activity_type = fields.String()
    location = fields.String()
    region = fields.String()
    country = fields.String()
    distance = fields.Number()
