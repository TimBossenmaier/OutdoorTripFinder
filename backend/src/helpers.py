import math


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
