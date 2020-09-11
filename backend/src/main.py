import os
from flask import Flask, jsonify
from .utils.database import db
from .utils.responses import response_with
from .config.config import ProductionConfig, TestingConfig, DevelopmentConfig
from .utils.responses import BAD_REQUEST_400, SERVER_ERROR_404, SERVER_ERROR_500


app = Flask(__name__)

if os.environ.get('WORK_ENV') == 'PROD':
    app_config = ProductionConfig
elif os.environ.get('WORK_ENV') == 'TEST':
    app_config = TestingConfig
else:
    app_config = DevelopmentConfig

app.config.from_object(app_config)

db.init_app(app)
with app.app_context():
    db.create_all()


# START GLOBAL HTTP CONFIGURATIONS
@app.after_request
def add_header(response):
    return response

@app.errorhandler(400)
def bad_request(e):
    logging.error(e)
    return response_with(BAD_REQUEST_400)


@app.errorhandler(500)
def server_error(e):
    logging.error(e)
    return response_with(SERVER_ERROR_500)


@app.errorhandler(404)
def not_found(e):
    logging.error(e)
    return response_with(SERVER_ERROR_404)


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', use_reloader=False)