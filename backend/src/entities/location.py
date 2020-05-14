# coding=utf-8

from sqlalchemy import Column, String, Date, ARRAY, Integer
from geoalchemy2 import Geometry
from marshmallow import Schema, fields
from sqlalchemy.orm import relationship

from .entity import Entity, Base


class Location(Entity, Base):
    __tablename__ = 'locations'

    geo_coordinate = Column(Geometry('POINT'))
    name = Column(String)
    region = Column(String)
    country = Column(String)