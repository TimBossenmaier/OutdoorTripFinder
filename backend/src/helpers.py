import math

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
    https://en.wikipedia.org/wiki/Haversine_formula
    :param lat1:
    :param long1:
    :param lat2:
    :param long2:
    :return:
    """

    diff_lat = deg_to_radian(lat2 - lat1)
    diff_long = deg_to_radian(long2 - long1)

    left_form = math.sin(diff_lat / 2) ** 2
    right_form = math.cos(deg_to_radian(lat1)) * math.cos(deg_to_radian(lat2)) * math.sin(diff_long / 2) ** 2

    return math.ceil(2 * EARTH_RADIUS * math.asin(math.sqrt(left_form + right_form)))
