import os
from flask import Flask, jsonify

app = Flask(__name__)

if os.environ.get('WORK_ENV') == 'PROD':
    app_config = ProductionConfig
elif os.environ.get('WORK_ENV') == 'TEST':
    app_config = TestingConfig
else:
    app_config = DevelopmentConfig

app.config.from_object(app_config)

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', use_reloader=False)