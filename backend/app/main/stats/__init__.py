from flask import Blueprint

stats = Blueprint('stats', __name__)


@stats.route('/test')
def test():
    return "Hallo"