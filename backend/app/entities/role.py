from .entity import Entity, EntitySchema, Base
from marshmallow import fields
from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import relationship


class Role(Entity, Base):
    __tablename__ = 'roles'
    name = Column(String, unique=True)
    default = Column(Boolean, default=False)
    permissions = Column(Integer)
    users = relationship('User', backref='role')

    def __init__(self, name, default, permissions, created_by):
        Entity.__init__(self, created_by)
        self.name = name
        self.default = default
        self.permissions = permissions

    def __repr__(self):
        return '<Role %r' % self.name

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def rem_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles(session):
        roles = {
            'Test User': [Permission.READ],
            'User': [Permission.READ, Permission.LIKE, Permission.FOLLOW, Permission.COMMENT],
            'Advanced User': [Permission.READ, Permission.LIKE, Permission.FOLLOW, Permission.COMMENT,
                              Permission.CREATE],
            'Admin': [Permission.READ, Permission.LIKE, Permission.FOLLOW, Permission.COMMENT, Permission.CREATE,
                      Permission.ADMIN]
        }

        default_role = 'Test User'

        for r in roles:
            role = session.query(Role).filter_by(name=r).first()

            if role is None:
                role = Role(name=r, default=[True if r == default_role else False], permissions=0,
                            created_by=' DB Initializer')
            for perm in roles[r]:
                role.add_permission(perm)
            session.add(role)
        session.commit()


class RoleSchema(EntitySchema):
    name = fields.String()
    default = fields.Boolean()
    permissions = fields.Integer()


class Permission:
    READ = 1
    LIKE = 2
    FOLLOW = 4
    COMMENT = 8
    CREATE = 16
    ADMIN = 32
