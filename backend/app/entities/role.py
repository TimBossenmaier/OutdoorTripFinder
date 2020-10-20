from .entity import Entity, EntitySchema, Base
from marshmallow import fields
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

class Role(Entity, Base):

    __tablename__ = 'roles'
    name = Column(String, unique=True)
    users = relationship('User', backref='role')

    def __init__(self, name, created_by):
        Entity.__init__(self, created_by)
        self.name = name

    def __repr__(self):
        return '<Role %r' % self.name


class RoleSchema(EntitySchema):
    name = fields.String()
