from marshmallow import fields
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, Integer, ForeignKey
from .entity import Entity, EntitySchema, Base


class User(Entity, Base):
    __tablename__ = 'users'
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String(256))
    role_id = Column(Integer, ForeignKey('roles.id'))

    def __init__(self, username, email, password, role_id, created_by):
        Entity.__init__(self, created_by)
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role_id = role_id

    def __repr__(self):
        return '<User %r>' % self.username

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    class UserSchema(EntitySchema):
        username = fields.String()
        email = fields.String()
        password = fields.String()
        role_id = fields.Integer()
