from marshmallow import fields
from werkzeug.security import generate_password_hash, check_password_hash
from backend.app import db
from .entity import Entity, EntitySchema


class User(Entity, db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, username, email, password_hash, role_id, created_by):
        Entity.__init__(self, created_by)
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role_id = role_id

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    class UserSchema(EntitySchema):
        username = fields.String()
        email = fields.String()
        password = fields.String()
        role_id = fields.Integer()
