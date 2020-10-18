from ..utils.responses import BAD_REQUEST_400, SERVER_ERROR_404, SERVER_ERROR_500
from . import main
from ..utils.responses import response_with


@main.app_errorhandler(404)
def page_not_found(e):
    return response_with(SERVER_ERROR_404)


@main.app_errorhandler(500)
def internal_server_error(e):
    return response_with(SERVER_ERROR_500)


@main.app_errorhandler(400)
def bad_request(e):
    return response_with(BAD_REQUEST_400)