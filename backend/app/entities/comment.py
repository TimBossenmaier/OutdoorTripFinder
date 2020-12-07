# coding=utf-8
from datetime import datetime
from enum import Enum
from marshmallow import fields, Schema
from sqlalchemy import Column, Integer, ForeignKey, Text, Boolean

from app.entities.entity import Entity, Base, EntitySchema


class Comment(Entity, Base):
    __tablename__ = 'comments'

    body = Column(Text, nullable=False)
    disabled = Column(Boolean, default=False)
    author_id = Column(Integer, ForeignKey('users.id'))
    activity_id = Column(Integer, ForeignKey('activities.id'))
    last_updated_by = Column(Integer, ForeignKey('users.id'), nullable=False)

    def __init__(self, body, author_id, activity_id, created_by):
        Entity.__init__(self)
        self.body = body
        self.author_id = author_id
        self.activity_id = activity_id
        self.last_updated_by = created_by

    def create(self, session):

        session.add(self)
        session.commit()

        return self

    def delete(self, session):
        session.delete(self)
        session.commit()

    def update(self, session, updated_by, **kwargs):
        self.updated_at = datetime.now()
        self.last_updated_by = updated_by

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        session.add(self)
        session.commit()

    def convert_to_insert_schema(self):
        schema = CommentInsertSchema()
        return schema.dump(self)

    def serialize(self):
        com = CommentSchema().dump(self)

        return com

    @staticmethod
    def get_insert_schema():
        return CommentInsertSchema()

    @staticmethod
    def get_schema(many, only):
        return CommentSchema(many=many, only=only)

    @staticmethod
    def get_attributes():
        return CommentAttributes


class CommentSchema(EntitySchema):
    body = fields.String()
    disabled = fields.Boolean()
    author_id = fields.Integer()
    activity_id = fields.Integer()
    last_updated_by = fields.Integer()


class CommentInsertSchema(Schema):
    body = fields.String()
    disabled = fields.Boolean()
    author_id = fields.Integer()
    activity_id = fields.Integer()
    created_by = fields.Integer()


class CommentAttributes(Enum):
    BODY = "body"
    DISABLED = "disabled"
    AUTHOR_ID = "author_id"
    ACTIVITY_ID = "activity_id"
    LAST_UPDATED_BY = 'last_updated_by'
    ID = 'id'
    CREATED_AT = 'created_at'
    UPDATED_AT = 'updated_at'

    def __str__(self):
        return str(self.value)
