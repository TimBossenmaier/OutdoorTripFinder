# coding=utf-8

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean
from marshmallow import Schema, fields
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from app.entities.comment import Comment
from app.entities.entity import Entity, Base, EntitySchema


class Activity(Entity, Base):
    __tablename__ = 'activities'

    name = Column(String, nullable=False)
    description = Column(Text)
    activity_type_id = Column(Integer, ForeignKey('activity_types.id'), nullable=False)
    source = Column(String, nullable=False)
    save_path = Column(String, nullable=False)
    multi_day = Column(Boolean, nullable=False)
    last_updated_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    activity_type = relationship('ActivityType', foreign_keys=activity_type_id)
    locations = relationship('LocationActivity', uselist=True, backref='activities')
    comments = relationship(Comment, foreign_keys=[Comment.activity_id], lazy='dynamic')

    def __init__(self, name, description, activity_type_id, source, save_path, multi_day, created_by):
        Entity.__init__(self)
        self.name = name
        self.description = description
        self.activity_type_id = activity_type_id
        self.source = source
        self.save_path = save_path
        self.multi_day = multi_day
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
        schema = ActivityInsertSchema()
        return schema.dump(self)

    def serialize(self):
        act = ActivitySchema().dump(self)

        return act

    @staticmethod
    def get_insert_schema():
        return ActivityInsertSchema()

    @staticmethod
    def get_presentation_schema(many, only=()):
        if len(only) == 0:
            return ActivityPresentationSchema(many=many)
        else:
            return ActivityPresentationSchema(many=many, only=only)

    @staticmethod
    def get_schema(many, only):
        return ActivitySchema(many=many, only=only)

    @staticmethod
    def get_attributes():
        return ActivityAttributes


class ActivitySchema(EntitySchema):
    name = fields.String()
    description = fields.String()
    activity_type_id = fields.Integer()
    source = fields.String()
    save_path = fields.String()
    multi_day = fields.Boolean()
    last_updated_by = fields.Integer()


class ActivityInsertSchema(Schema):
    name = fields.String()
    description = fields.String()
    activity_type_id = fields.Integer()
    source = fields.String()
    save_path = fields.String()
    multi_day = fields.Boolean()
    created_by = fields.Integer()


class ActivityPresentationSchema(ActivitySchema):
    activity_type = fields.String()
    location = fields.String()
    region = fields.String()
    country = fields.String()
    distance = fields.Number()


class ActivityAttributes(Enum):
    NAME = 'name'
    DESCRIPTION = 'description'
    ACTIVITY_TYPE_ID = 'activity_type_id'
    SOURCE = 'source'
    SAVE_PATH = 'save_path'
    MULTI_DAY = 'multi_day'
    LAST_UPDATED_BY = 'last_updated_by'
    ID = 'id'
    CREATED_AT = 'created_at'
    UPDATED_AT = 'updated_at'

    def __str__(self):
        return str(self.value)
