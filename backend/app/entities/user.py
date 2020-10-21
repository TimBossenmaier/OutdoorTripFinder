from marshmallow import fields, Schema
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from itsdangerous import TimedJSONWebSignatureSerializer
from flask import current_app
from datetime import datetime
from .entity import Entity, Base


class User(Entity, Base):
    __tablename__ = 'users'
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String(256))
    role_id = Column(Integer, ForeignKey('roles.id'))
    confirmed = Column(Boolean, default=False)

    def __init__(self, username, email, password, role_id, created_by):
        Entity.__init__(self, created_by)
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role_id = role_id

    def __repr__(self):
        return '<User %r>' % self.username

    def create(self, session):

        self.last_updated_by = 'Account Generator'
        session.add(self)
        session.commit()

        return self

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=86400):
        """
        expiration: 24 h
        """

        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, session):

        self.confirmed = True
        self.last_updated_by = 'Account Validator'
        self.updated_at = datetime.now()
        session.add(self)
        session.commit()

        return True


class UserInsertSchema(Schema):
    username = fields.String()
    email = fields.String()
    password = fields.String()
    role_id = fields.Integer()
    created_by = fields.String()


class UserSchema(Schema):
    id = fields.String()
    username = fields.String()
    email = fields.String()
    password_hash = fields.String()
    role_id = fields.Integer()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_updated_by = fields.String()
