from flask import make_response

from app.utils.responses import BAD_REQUEST_400, SERVER_ERROR_404, SERVER_ERROR_500
from app.main import get_main_app
from app.utils.responses import create_json_response

main_app = get_main_app()


@main_app.app_errorhandler(404)
def page_not_found(e):
    return make_response(create_json_response(SERVER_ERROR_404, "", None))


@main_app.app_errorhandler(500)
def internal_server_error(e):
    return make_response(create_json_response(SERVER_ERROR_500, "", None))


@main_app.app_errorhandler(400)
def bad_request(e):
    return make_response(create_json_response(BAD_REQUEST_400, "", None))
