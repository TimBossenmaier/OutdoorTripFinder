import re

from ..entities.user import UserAttributes
from ..entities.country import CountryAttributes


def investigate_integrity_error(ie):

    error_detail = ie.orig.args[0]
    affected_attr = str(re.search(r'DETAIL:  Schlüssel »\([a-zA-Z]+\)', error_detail))
    if str(UserAttributes.USERNAME) in affected_attr:
        msg = {"existing": str(UserAttributes.USERNAME)}
        return msg
    if str(UserAttributes.EMAIL) in affected_attr:
        msg = {"existing": str(UserAttributes.EMAIL)}
        return msg
    if str(CountryAttributes.NAME) in affected_attr:
        msg = {"existing": str(CountryAttributes.NAME)}
        return msg
    else:
        return None
