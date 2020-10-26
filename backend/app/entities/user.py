from marshmallow import fields, Schema
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from itsdangerous import TimedJSONWebSignatureSerializer
from flask import current_app
from datetime import datetime
from enum import Enum,auto
from .entity import Entity, Base, EntitySchema
from .role import Permission


# TODO: check what can be part of entity (e.g. update())
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

    def update(self, session, updated_by, **kwargs):
        self.updated_at = datetime.now()
        self.last_updated_by = updated_by

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        session.add(self)
        session.commit()

    def update_password(self, password, session, updated_by):
        self.password_hash = generate_password_hash(password)

        self.update(session, updated_by=updated_by)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def confirm(self, session):

        self.confirmed = True
        self.last_updated_by = 'Account Validator'
        self.updated_at = datetime.now()
        session.add(self)
        session.commit()

        return True

    def generate_confirmation_token(self, expiration=86400):
        """
        expiration: 24 h
        """

        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def generate_reset_token(self, expiration=86400):
        """
        expiration: 24 h
        """

        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    def generate_email_token(self, new_email, username, expiration=86400):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'email': new_email, 'username': username}).decode('utf-8')

    @staticmethod
    def reset_password(session, token, json):

        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False

        user = session.query(User).get(data.get('reset'))
        if user is None:
            return False
        user.update_password(json["password"], session, json[str(UserAttributes.UPDATED_BY)])
        return True

    @staticmethod
    def resolve_email_token(token):

        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return None, None, None

        new_email = data.get(str(UserAttributes.EMAIL))
        username = data.get(str(UserAttributes.USERNAME))
        user_id = data.get('change_email')

        return new_email, username, user_id

    def change_email(self, session, new_email, user_id, updated_by):

        if user_id != self.id:
            return False

        self.update(session, updated_by, email=new_email)

        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_admin(self):
        return self.can(Permission.ADMIN)


class UserInsertSchema(Schema):
    username = fields.String()
    email = fields.String()
    password = fields.String()
    role_id = fields.Integer()
    created_by = fields.String()


class UserSchema(EntitySchema):
    username = fields.String()
    email = fields.String()
    password_hash = fields.String()
    role_id = fields.Integer()


class UserAttributes(Enum):
    USERNAME = 'username'
    EMAIL = 'email'
    PASSWORD_HASH = 'password_hash'
    ROLE_ID = 'role_id'
    CONFIRMED = 'confirmed'
    ID = 'id'
    CREATED_AT = 'created_at'
    UPDATED_AT = 'updated_at'
    UPDATED_BY = 'last_updated_by'

    def __str__(self):
        return str(self.value)
