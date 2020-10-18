from .. import db
from .entity import Entity, EntitySchema
from marshmallow import fields


class Role(Entity, db.Model):

    __tablename__ = 'roles'
    name = db.Column(db.String, unique=True)
    users = db.relationship('User', backref='role')

    def __init__(self, name, created_by):
        Entity.__init__(self, created_by)
        self.name = name

    def __repr__(self):
        return '<Role %r' % self.name


class RoleSchema(EntitySchema):
    name = fields.String()
