# coding=utf-8
from enum import Enum

from marshmallow import fields
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.entities.entity import Entity, Base, EntitySchema


class HikeRelation(Entity, Base):
    __tablename__ = 'hike-relations'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    activity_id = Column(Integer, ForeignKey('activities.id'), nullable=False)
    user = relationship('User', foreign_keys=user_id)
    activity = relationship('Activity', foreign_keys=activity_id)

    def __init__(self, user_id, activity_id):
        Entity.__init__(self)
        self.user_id = user_id
        self.activity_id = activity_id

    def create(self, session):

        session.add(self)
        session.commit()

        return self

    def delete(self, session):
        session.delete(self)
        session.commit()

    def convert_to_insert_schema(self):
        schema = HikeRelationSchema()
        return schema.dump(self)

    def convert_to_presentation_schema(self, only=(), **kwargs):
        schema = HikeRelationPresentationSchema(only=only if len(only) > 0 else None)
        dump = schema.dump(self)
        for key, value in kwargs.items():
            dump.update({key: value})

        return dump

    def serialize(self):

        hr = HikeRelationSchema().dump(self)

        return hr

    @staticmethod
    def get_insert_schema():
        return HikeRelationSchema()

    @staticmethod
    def get_schema(many, only):
        return HikeRelationSchema(many=many, only=only)

    @staticmethod
    def get_attributes():
        return HikeRelationAttributes


class HikeRelationSchema(EntitySchema):
    user_id = fields.Integer()
    activity_id = fields.Integer()


class HikeRelationPresentationSchema(HikeRelationSchema):
    id = fields.Integer()


class HikeRelationAttributes(Enum):
    USER_ID = 'user_id'
    ACTIVITY_ID = 'activity_id'
    ID = 'id'
    CREATED_AT = 'created_at'
    UPDATED_AT = 'updated_at'

    def __str__(self):
        return str(self.value)
