import math
from backend.src.entities.location import Location, LocationSchema
from backend.src.entities.activity_type import ActivityType, ActivityTypeSchema
from backend.src.entities.activity import ActivitySchema, Activity
from flask import jsonify
from backend.src.entities.entity import Session, Base, engine

# in km
EARTH_RADIUS = 6371


def deg_to_radian(val, backwards=False):
    """
    converts values in degree to radians and vice versa
    :param backwards: indicates the convertion to be in the other direction
    :param val: value in degrees
    :return: converted value as radian value
    """
    if not backwards:
        return val * math.pi / 180
    else:
        return val * 180 / math.pi


def distance_between_coordinates(lat1, long1, lat2, long2):
    """
    calculates the distance between two geo-coordinates with the Haversine formula
    reference:
        https://en.wikipedia.org/wiki/Haversine_formula
    :param lat1: latitude of position one
    :param long1: longitude of position one
    :param lat2: latituted of position two
    :param long2: longitude of position two
    :return: ceiled distance between both coordinates
    """

    diff_lat = deg_to_radian(lat2 - lat1)
    diff_long = deg_to_radian(long2 - long1)

    # separate calculation into both terms of sum in the square root
    left_form = math.sin(diff_lat / 2) ** 2
    right_form = math.cos(deg_to_radian(lat1)) * math.cos(deg_to_radian(lat2)) * math.sin(diff_long / 2) ** 2

    return math.ceil(2 * EARTH_RADIUS * math.asin(math.sqrt(left_form + right_form)))


def sort_by_dist(dic):
    return dic['dist']
