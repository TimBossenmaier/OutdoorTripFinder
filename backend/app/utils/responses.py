"""
Standard class of HTTP responses
"""

from enum import Enum
from flask import jsonify

INVALID_FIELD_NAME_SENT_422 = {
    "http_code": 422,
    "code": "invalidField"
}

INVALID_INPUT_422 = {
    "http_code": 422,
    "code": "invalidInput"
}

MISSING_PARAMETER_422 = {
    "http_code": 422,
    "code": "missingParameter"
}

BAD_REQUEST_400 = {
    "http_code": 400,
    "code": "badRequest"
}

SERVER_ERROR_500 = {
    "http_code": 500,
    "code": "serverError"
}

SERVER_ERROR_404 = {
    "http_code": 404,
    "code": "notFound"
}

UNAUTHORIZED_403 = {
    "http_code": 403,
    "code": "notAuthorized"
}

SUCCESS_200 = {
    "http_code": 200,
    "code": "success"
}

SUCCESS_201 = {
    "http_code": 201,
    "code": "success"
}

SUCCESS_204 = {
    "http_code": 204,
    "code": "success"
}


def create_json_response(http_resp, message, data, classname=""):

    http_resp.update({'message': str(message).format(classname)})
    http_resp.update({'data': data})

    return jsonify(http_resp)


class ResponseMessages(Enum):
    AUTH_USERNAME_NOT_PROVIDED = "[auth] no username provided"
    AUTH_LOGIN_SUCCESSFUL = "[auth] login successful"
    AUTH_LOGIN_FAILED = "[auth] login failed"
    AUTH_USER_CREATED = "[auth] user successful created"
    AUTH_DUPLICATE_PARAMS = "[auth] user params already exist"
    AUTH_TOKEN_INVALID = "[auth] token invalid"
    AUTH_USER_CONFIRMED = "[auth] user successfully confirmed"
    AUTH_ALREADY_CONFIRMED = "[auth] user already confirmed"
    AUTH_CONFIRMATION_RESEND = "[auth] user confirmation resend"
    AUTH_INVALID_PARAMS = "[auth] invalid params"
    AUTH_PASSWORD_CHANGED = "[auth] password changed"
    AUTH_WRONG_PASSWORD = "[auth] old password is incorrect"
    AUTH_PW_REQUESTED = "[auth] password reset requested"
    AUTH_PASSWORD_NOT_PROVIDED = "[auth] no new password provided"
    AUTH_RESET_SUCCESSFUL = "[auth] password reset successful"
    AUTH_RESET_FAILED = "[auth] password reset failed"
    AUTH_EMAIL_EXISTS = "[auth] new email equals old email"
    AUTH_EMAIL_REQUESTED = "[auth] change email requested"
    AUTH_EMAIL_CHANGED = "[auth] email change successful"
    AUTH_EMAIL_FAILED = "[auth] email change failed"
    MAIN_NO_USER_INFORMATION = "[main] no information about user provided"
    MAIN_NO_DATA = "[main] data could not be retrieved from request"
    CREATE_SUCCESS = "[create] {} successful"
    CREATE_MISSING_PARAM = "[create] {}, missing parameter"
    CREATE_NOT_AUTHORIZED = "[create] no permission"
    CREATE_DUPLICATE_PARAMS = "[create] {}, params already exist"
    UPDATE_SUCCESS = "[update] {} successful"
    UPDATE_FAILED = "[update] {} failed"
    UPDATE_MISSING_PARAM = "[update] {}, missing parameter"
    UPDATE_NOT_AUTHORIZED = "[update] no permission"
    LIST_SUCCESS = "[list] {} successful"
    LIST_EMPTY = "[list] {} empty"
    LIST_INVALID_INPUT = "[list] {}, invalid parameters provided"
    FIND_MISSING_PARAMETER = "[find] {}, missing parameter"
    FIND_NO_RESULTS = "[find] {}, no results"
    FIND_SUCCESS = "[find] {}, successful"
    FIND_NOT_AUTHORIZED = "[find] no permission"

    def __str__(self):
        return self.value
